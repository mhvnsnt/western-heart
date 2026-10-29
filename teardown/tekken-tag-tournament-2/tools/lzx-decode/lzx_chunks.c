/* Decode an xbdecompress-style file: [12B header][head][2B BE chunk-size][chunk]...
   Each chunk holds ONE LZX block (MS-PATCH framing, 128KB window).
   Chunk 0 starts with the 1-bit E8 flag; later chunks start directly with the block header.
   Block length is read from the 3-bit type + 24-bit length header before decoding.
   Usage: lzx_chunks <file> <start_offset> <window_bits> <outdir> */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "lzx.h"
#include "reactos-lzx.c"

/* Peek the LZX block length at the start of a chunk's data.
   skip_e8 = 1 only for the very first chunk of the stream.
   Returns block length (1..32768) or -1 on invalid header. */
static int peek_block_len(unsigned char *d, int dlen, int skip_e8) {
    long bitpos = 0;
    /* bit reader: 16-bit LE words, MSB-first */
    int read_bits(int n) {
        int v = 0;
        for (int k = 0; k < n; k++) {
            long w = bitpos / 16;
            int bit = 15 - (int)(bitpos % 16);
            long bi = w * 2;
            if (bi + 1 >= dlen) return -1;
            int word = d[bi] | (d[bi+1] << 8);
            v = (v << 1) | ((word >> bit) & 1);
            bitpos++;
        }
        return v;
    }
    if (skip_e8) { if (read_bits(1) < 0) return -1; }
    int type = read_bits(3);
    if (type < 1 || type > 3) return -1;
    int len = read_bits(24);
    if (len < 1 || len > 32768) return -1;
    return len;
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: %s file start window outdir\n", argv[0]); return 2; }
    const char *path = argv[1];
    long start = atol(argv[2]);
    int window = atoi(argv[3]);
    const char *outdir = argv[4];
    FILE *f = fopen(path, "rb");
    if (!f) { perror("fopen"); return 2; }
    fseek(f, 0, SEEK_END); long fsize = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *b = malloc(fsize);
    if (fread(b, 1, fsize, f) != (size_t)fsize) return 2;
    fclose(f);
    long off = start; int nch = 0;
    long *coff = malloc(sizeof(long)*10000); int *clen = malloc(sizeof(int)*10000);
    long chain_break = -1;
    while (off < fsize) {
        if (off + 2 > fsize) { chain_break = off; break; }
        int sz = (b[off]<<8) | b[off+1];
        if (sz < 2 || sz > 65535) {
            /* SECTION PADDING: a few zero bytes may pad the stream to the next 128KB
               section boundary; jump there and resume the chain. */
            long next_sec = ((off / 131072) + 1) * 131072;
            if (next_sec - off <= 16 && next_sec < fsize) {
                printf("CHAIN PAD %ld -> %ld (%ld bytes)\n", off, next_sec, next_sec - off);
                off = next_sec;
                continue;
            }
            chain_break = off; break;
        }
        coff[nch] = off+2; clen[nch] = sz; nch++;
        off += 2 + sz;
        if (nch >= 10000) break;
    }
    if (chain_break >= 0) printf("CHAIN BREAK at off=%ld (filelen %ld, %d chunks before break)\n", chain_break, fsize, nch);
    else printf("CHAIN tiles to EOF: %d chunks\n", nch);
    printf("chunks=%d\n", nch);
    struct LZXstate *st = LZXinit(window);
    if (!st) { printf("INIT_FAIL\n"); return 3; }
    unsigned char *out = malloc(32768);
    long total = 0;
    for (int i = 0; i < nch; i++) {
        /* SECTION BOUNDARY: chunk prefix at a 128KB file offset starts a fresh LZX stream */
        int is_section = (i > 0) && ((coff[i] - 2) % 131072 == 0);
        if (is_section) {
            LZXteardown(st);
            st = LZXinit(window);
            printf("chunk %d: SECTION RESET at file offset %ld\n", i, coff[i] - 2);
        }
        /* A chunk may hold MULTIPLE LZX blocks (e.g. 18453+14315=32768): always try 32768
           first; fall back to the first block's peeked length only if that fails. */
        struct LZXstate backup; memcpy(&backup, st, sizeof(backup));
        int rc = LZXdecompress(st, b + coff[i], out, clen[i], 32768);
        int want = 32768;
        if (rc != 0) {
            memcpy(st, &backup, sizeof(backup));
            want = peek_block_len(b + coff[i], clen[i], i == 0 || is_section);
            if (want < 0) { printf("chunk %d: BAD BLOCK HEADER (clen=%d)\n", i, clen[i]); break; }
            rc = LZXdecompress(st, b + coff[i], out, clen[i], want);
        }
        if (rc != 0) { printf("chunk %d: FAIL rc=%d (clen=%d want=%d)\n", i, rc, clen[i], want); break; }
        char op[512]; snprintf(op, sizeof op, "%s/chunk%03d.bin", outdir, i);
        FILE *o = fopen(op, "wb"); fwrite(out, 1, want, o); fclose(o);
        printf("chunk %d: OK %d bytes -> %s first32=", i, want, op);
        for (int k = 0; k < 32 && k < want; k++) printf("%02x", out[k]);
        printf("\n");
        total += want;
    }
    printf("TOTAL decoded=%ld\n", total);
    return 0;
}
