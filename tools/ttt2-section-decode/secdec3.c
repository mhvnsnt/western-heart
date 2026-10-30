/* Section decoder v3:
   - Stored section (BE16 0 + expected == inlen-2): raw copy.
   - LZX section: fresh state; walk chunks by size prefix; chunk-done rule
     (block boundary + <=16B left = padding); chunk-start resync: if a chunk's
     first slice fails, retry its prefix at -1/+1 (prior chunk size overstated
     by 1 -- data028 chunk-2383 precedent); clamp chunk data to section end
     (a chunk cannot cross its section); fallback binary-search on slice fail,
     then CONTINUE (no break) so spanning blocks finish.
   Usage: secdec3 <file> <sec_start> <sec_inlen> <expected_out> <outpath> */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "lzx.h"
#include "lzx_exact.c"
static unsigned char *g; static long fsize;
int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: secdec3 file sec_start sec_inlen expected_out outpath\n"); return 2; }
    const char *path = argv[1];
    long sec_start = atol(argv[2]);
    long sec_inlen = atol(argv[3]);
    long expected = atol(argv[4]);
    const char *outpath = argv[5];
    FILE *f = fopen(path, "rb");
    if (!f) { perror("fopen"); return 2; }
    fseek(f, 0, SEEK_END); fsize = ftell(f); fseek(f, 0, SEEK_SET);
    g = malloc(fsize + 1048576);
    if (fread(g, 1, fsize, f) != (size_t)fsize) return 2;
    fclose(f);
    memset(g + fsize, 0, 1048576);
    FILE *o = fopen(outpath, "wb");
    if (!o) { perror("fopen out"); return 2; }
    long sec_end = sec_start + sec_inlen;
    if (sec_end > fsize) sec_end = fsize;
    int be0 = (g[sec_start]<<8)|g[sec_start+1];
    if (be0 == 0 && expected == sec_inlen - 2) {
        fwrite(g + sec_start + 2, 1, expected, o);
        fclose(o);
        printf("STORED sec_start=%ld out=%ld\n", sec_start, expected);
        return 0;
    }
    struct LZXstate *st = LZXinit(17);
    st->ex_base = g;
    unsigned char *out = malloc(32768);
    long inpos = sec_start;
    long total = 0;
    int nch = 0, failed = 0, nresync = 0, nclamp = 0;
    while (inpos < sec_end && total < expected) {
        if (inpos + 2 > sec_end) { printf("CHUNK TRUNC at %ld\n", inpos); failed = 1; break; }
        int sz = (g[inpos]<<8)|g[inpos+1];
        if (sz < 2 || sz > 65535) { printf("CHUNK BAD SIZE %d at %ld (total=%ld)\n", sz, inpos, total); failed = 1; break; }
        long coff = inpos + 2, cend = coff + sz;
        if (cend > sec_end) { cend = sec_end; nclamp++; printf("CLAMP chunk %d size %d to sec_end (inpos=%ld)\n", nch, sz, inpos); }
        long cpos = coff;
        int first_slice = 1;
        int guard = 0;
        int chunk_ok = 0;
        while (cpos < cend && total < expected) {
            if (!first_slice && st->block_remaining == 0 && (cend - cpos) <= 16) { chunk_ok = 1; break; }
            struct LZXstate bkp; memcpy(&bkp, st, sizeof(bkp));
            unsigned char *wcopy = malloc(131072); memcpy(wcopy, st->window, 131072);
            long spos; int sbit;
            if (first_slice) { spos = coff; sbit = 0; }
            else { spos = bkp.ex_next_byte; sbit = bkp.ex_next_bit; }
            st->ex_entry_bit = sbit;
            int rc = LZXdecompress(st, g + spos, out, (int)(cend - spos), 32768);
            if (rc != 0) {
                /* FALLBACK FIRST: binary-search largest succeeding outlen (final partial block). */
                int lo = 1, hi = 32767, best = -1;
                while (lo <= hi) {
                    int mid = (lo + hi) / 2;
                    struct LZXstate t; memcpy(&t, &bkp, sizeof(t));
                    unsigned char *tw = malloc(131072); memcpy(tw, wcopy, 131072);
                    t.window = tw;
                    t.ex_entry_bit = sbit;
                    int r2 = LZXdecompress(&t, g + spos, out, (int)(cend - spos), mid);
                    free(tw);
                    if (r2 == 0) { best = mid; lo = mid + 1; } else hi = mid - 1;
                }
                if (best >= 0) {
                    unsigned char *rw = st->window;
                    memcpy(st, &bkp, sizeof(*st));
                    st->window = rw;
                    memcpy(rw, wcopy, 131072);
                    free(wcopy);
                    st->ex_entry_bit = sbit;
                    rc = LZXdecompress(st, g + spos, out, (int)(cend - spos), best);
                    if (rc != 0) { printf("CHUNK %d REDO FAIL\n", nch); failed = 1; goto done; }
                    fwrite(out, 1, best, o);
                    total += best;
                    cpos = st->ex_next_byte;
                    st->ex_entry_bit = st->ex_next_bit;
                    first_slice = 0;
                    continue;
                }
                /* Fallback found nothing: if mid-chunk at a block boundary, scan for next block header. */
                if (!first_slice && bkp.block_remaining == 0) {
                    int found = 0; long fbyte = 0; int fbit = 0;
                    long scan_end = spos + 32; if (scan_end > cend - 1) scan_end = cend - 1;
                    for (long by = spos; by <= scan_end && !found; by++) {
                        for (int bit = (by == spos ? sbit : 0); bit < 8 && !found; bit++) {
                            struct LZXstate t; memcpy(&t, &bkp, sizeof(t));
                            unsigned char *tw = malloc(131072); memcpy(tw, wcopy, 131072);
                            t.window = tw; t.ex_entry_bit = bit;
                            int inlen = (int)(cend - by); if (inlen > 4096) inlen = 4096; if (inlen < 64) inlen = 64;
                            int r2 = LZXdecompress(&t, g + by, out, inlen, 1);
                            if (r2 == 0 && (t.block_type == 1 || t.block_type == 2) && t.block_length <= 32768) {
                                found = 1; fbyte = by; fbit = bit;
                                printf("BLOCKSCAN chunk %d: %ld bit %d -> %ld bit %d type %lu len %lu\n", nch, spos, sbit, fbyte, fbit,
                                    (unsigned long)t.block_type, (unsigned long)t.block_length);
                            }
                            free(tw);
                        }
                    }
                    if (found) {
                        unsigned char *rw = st->window;
                        memcpy(st, &bkp, sizeof(*st));
                        st->window = rw;
                        memcpy(rw, wcopy, 131072);
                        free(wcopy);
                        st->ex_entry_bit = fbit;
                        struct LZXstate bkp2; memcpy(&bkp2, st, sizeof(bkp2));
                        unsigned char *wcopy2 = malloc(131072); memcpy(wcopy2, st->window, 131072);
                        rc = LZXdecompress(st, g + fbyte, out, (int)(cend - fbyte), 32768);
                        if (rc != 0) {
                            int lo2 = 1, hi2 = 32767, best2 = -1;
                            while (lo2 <= hi2) {
                                int mid2 = (lo2 + hi2) / 2;
                                struct LZXstate t2; memcpy(&t2, &bkp2, sizeof(t2));
                                unsigned char *tw2 = malloc(131072); memcpy(tw2, wcopy2, 131072);
                                t2.window = tw2; t2.ex_entry_bit = fbit;
                                int r22 = LZXdecompress(&t2, g + fbyte, out, (int)(cend - fbyte), mid2);
                                free(tw2);
                                if (r22 == 0) { best2 = mid2; lo2 = mid2 + 1; } else hi2 = mid2 - 1;
                            }
                            if (best2 < 0) { printf("CHUNK %d BLOCKSCAN REDO FAIL\n", nch); free(wcopy2); failed = 1; goto done; }
                            unsigned char *rw2 = st->window;
                            memcpy(st, &bkp2, sizeof(*st));
                            st->window = rw2;
                            memcpy(rw2, wcopy2, 131072);
                            free(wcopy2);
                            st->ex_entry_bit = fbit;
                            rc = LZXdecompress(st, g + fbyte, out, (int)(cend - fbyte), best2);
                            if (rc != 0) { printf("CHUNK %d BLOCKSCAN REDO2 FAIL\n", nch); failed = 1; goto done; }
                            fwrite(out, 1, best2, o);
                            total += best2;
                            cpos = st->ex_next_byte;
                            st->ex_entry_bit = st->ex_next_bit;
                            first_slice = 0;
                            continue;
                        }
                        free(wcopy2);
                        fwrite(out, 1, 32768, o);
                        total += 32768;
                        cpos = st->ex_next_byte;
                        st->ex_entry_bit = st->ex_next_bit;
                        first_slice = 0;
                        continue;
                    }
                }
                if (!first_slice) { printf("CHUNK %d FAIL at %ld (total=%ld)\n", nch, spos, total); free(wcopy); failed = 1; goto done; }
                int resynced = 0;
                for (int d = -1; d <= 1 && !resynced; d += 2) {
                    long npre = inpos + d;
                    if (npre < sec_start || npre + 2 > sec_end) continue;
                    int nsz = (g[npre]<<8)|g[npre+1];
                    if (nsz < 2 || nsz > 65535) continue;
                    long ncoff = npre + 2, ncend = ncoff + nsz;
                    if (ncend > sec_end) ncend = sec_end;
                    struct LZXstate t; memcpy(&t, &bkp, sizeof(t));
                    unsigned char *tw = malloc(131072); memcpy(tw, wcopy, 131072);
                    t.window = tw; t.ex_entry_bit = 0;
                    int r2 = LZXdecompress(&t, g + ncoff, out, (int)(ncend - ncoff), 32768);
                    free(tw);
                    if (r2 == 0) {
                        printf("RESYNC chunk %d: prefix %ld -> %ld (delta %d)\n", nch, inpos, npre, d);
                        inpos = npre; coff = ncoff; cend = ncend; cpos = coff;
                        unsigned char *rw = st->window;
                        memcpy(st, &bkp, sizeof(*st));
                        st->window = rw;
                        memcpy(rw, wcopy, 131072);
                        st->ex_entry_bit = 0;
                        rc = LZXdecompress(st, g + coff, out, (int)(cend - coff), 32768);
                        if (rc == 0) { resynced = 1; nresync++; }
                        break;
                    }
                }
                if (!resynced) { printf("CHUNK %d FAIL at %ld (total=%ld, no resync)\n", nch, spos, total); free(wcopy); failed = 1; goto done; }
                /* resynced and rc==0: fall through to success handling (which frees wcopy) */
            }
            free(wcopy);
            fwrite(out, 1, 32768, o);
            total += 32768;
            cpos = st->ex_next_byte;
            st->ex_entry_bit = st->ex_next_bit;
            first_slice = 0;
            if (++guard > 10000) { printf("GUARD chunk %d\n", nch); failed = 1; goto done; }
        }
        (void)chunk_ok;
        inpos = cend;
        nch++;
    }
done:
    fclose(o);
    printf("LZX sec_start=%ld chunks=%d out=%ld expected=%ld inpos=%ld sec_end=%ld resync=%d clamp=%d %s\n",
        sec_start, nch, total, expected, inpos, sec_end, nresync, nclamp,
        (!failed && total == expected && inpos == sec_end) ? "EXACT" : "MISMATCH");
    return (!failed && total == expected && inpos == sec_end) ? 0 : 1;
}
