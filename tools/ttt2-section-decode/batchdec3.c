/* Batch section decoder v3 (port of secdec3): loads file once, decodes all
   head-table sections in order, concatenates output. Per-section: stored
   path, else LZX with fallback-first, chunk-start resync (+-1), block-scan
   (+32B) for inter-block gaps, blockscan-fallback, clamp to section end,
   chunk-done rule (block boundary + <=16B left = padding).
   Usage: batchdec3 <file> <outpath> <logpath> <ntab> <sec0_stream_start> */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "lzx.h"
#include "lzx_exact.c"
static unsigned char *g; static long fsize;
static long decode_section(struct LZXstate *st, long sec_start, long sec_end, long expected, FILE *o, int *nresync, int *nclamp, int *nscan, char *why, size_t whysize);
int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: batchdec3 file outpath logpath ntab sec0_stream_start\n"); return 2; }
    const char *path = argv[1]; const char *outpath = argv[2]; const char *logpath = argv[3];
    long ntab = atol(argv[4]); long sec0_stream = atol(argv[5]);
    FILE *f = fopen(path, "rb");
    if (!f) { perror("fopen"); return 2; }
    fseek(f, 0, SEEK_END); fsize = ftell(f); fseek(f, 0, SEEK_SET);
    g = malloc(fsize + 1048576);
    if (fread(g, 1, fsize, f) != (size_t)fsize) return 2;
    fclose(f);
    memset(g + fsize, 0, 1048576);
    long *tab = malloc(sizeof(long)*ntab);
    for (long i = 0; i < ntab; i++) tab[i] = (g[12+i*4]<<24)|(g[12+i*4+1]<<16)|(g[12+i*4+2]<<8)|g[12+i*4+3];
    long nsec = ntab - 1;
    FILE *o = fopen(outpath, "wb");
    FILE *lg = fopen(logpath, "w");
    if (!o || !lg) { perror("fopen out/log"); return 2; }
    long grand = 0; int n_exact = 0, n_stored = 0, n_mismatch = 0;
    int tot_resync = 0, tot_clamp = 0, tot_scan = 0;
    for (long k = 0; k < nsec; k++) {
        long sec_start = (k == 0) ? sec0_stream : k * 131072;
        long sec_end = (k == nsec - 1) ? fsize : (k + 1) * 131072;
        long sec_inlen = sec_end - sec_start;
        long expected = tab[k+1];
        int be0 = (g[sec_start]<<8)|g[sec_start+1];
        if (be0 == 0 && expected == sec_inlen - 2) {
            fwrite(g + sec_start + 2, 1, expected, o);
            fprintf(lg, "sec %ld STORED out=%ld\n", k, expected);
            grand += expected; n_stored++;
            continue;
        }
        struct LZXstate *st = LZXinit(17);
        st->ex_base = g;
        char why[256]; why[0] = 0;
        int nr = 0, nc = 0, ns = 0;
        long got = decode_section(st, sec_start, sec_end, expected, o, &nr, &nc, &ns, why, sizeof(why));
        LZXteardown(st);
        tot_resync += nr; tot_clamp += nc; tot_scan += ns;
        if (got == expected) {
            fprintf(lg, "sec %ld LZX EXACT out=%ld resync=%d clamp=%d scan=%d\n", k, got, nr, nc, ns);
            n_exact++;
        } else {
            fprintf(lg, "sec %ld LZX MISMATCH out=%ld expected=%ld resync=%d clamp=%d scan=%d %s\n", k, got, expected, nr, nc, ns, why);
            n_mismatch++;
        }
        grand += got;
        if ((k % 200) == 0) { printf("sec %ld grand=%ld\n", k, grand); fflush(stdout); }
    }
    fclose(o); fclose(lg);
    printf("DONE sections=%ld grand=%ld exact=%d stored=%d mismatch=%d resync=%d clamp=%d scan=%d\n",
        nsec, grand, n_exact, n_stored, n_mismatch, tot_resync, tot_clamp, tot_scan);
    return 0;
}
static long decode_section(struct LZXstate *st, long sec_start, long sec_end, long expected, FILE *o,
    int *nresync, int *nclamp, int *nscan, char *why, size_t whysize) {
    unsigned char *out = malloc(32768);
    long inpos = sec_start;
    long total = 0;
    int nch = 0;
    while (inpos < sec_end && total < expected) {
        if (inpos + 2 > sec_end) { snprintf(why, whysize, "CHUNK TRUNC at %ld", inpos); free(out); return total; }
        int sz = (g[inpos]<<8)|g[inpos+1];
        if (sz < 2 || sz > 65535) { snprintf(why, whysize, "CHUNK BAD SIZE %d at %ld", sz, inpos); free(out); return total; }
        long coff = inpos + 2, cend = coff + sz;
        if (cend > sec_end) { cend = sec_end; (*nclamp)++; }
        long cpos = coff;
        int first_slice = 1;
        int guard = 0;
        while (cpos < cend && total < expected) {
            if (!first_slice && st->block_remaining == 0 && (cend - cpos) <= 16) break;
            struct LZXstate bkp; memcpy(&bkp, st, sizeof(bkp));
            unsigned char *wcopy = malloc(131072); memcpy(wcopy, st->window, 131072);
            long spos; int sbit;
            if (first_slice) { spos = coff; sbit = 0; }
            else { spos = bkp.ex_next_byte; sbit = bkp.ex_next_bit; }
            st->ex_entry_bit = sbit;
            int rc = LZXdecompress(st, g + spos, out, (int)(cend - spos), 32768);
            if (rc != 0) {
                int lo = 1, hi = 32767, best = -1;
                while (lo <= hi) {
                    int mid = (lo + hi) / 2;
                    struct LZXstate t; memcpy(&t, &bkp, sizeof(t));
                    unsigned char *tw = malloc(131072); memcpy(tw, wcopy, 131072);
                    t.window = tw; t.ex_entry_bit = sbit;
                    int r2 = LZXdecompress(&t, g + spos, out, (int)(cend - spos), mid);
                    free(tw);
                    if (r2 == 0) { best = mid; lo = mid + 1; } else hi = mid - 1;
                }
                if (best >= 0) {
                    unsigned char *rw = st->window;
                    memcpy(st, &bkp, sizeof(*st)); st->window = rw; memcpy(rw, wcopy, 131072);
                    free(wcopy);
                    st->ex_entry_bit = sbit;
                    rc = LZXdecompress(st, g + spos, out, (int)(cend - spos), best);
                    if (rc != 0) { snprintf(why, whysize, "CHUNK %d REDO FAIL", nch); free(out); return total; }
                    fwrite(out, 1, best, o); total += best;
                    cpos = st->ex_next_byte; st->ex_entry_bit = st->ex_next_bit; first_slice = 0;
                    continue;
                }
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
                            }
                            free(tw);
                        }
                    }
                    if (found) {
                        (*nscan)++;
                        unsigned char *rw = st->window;
                        memcpy(st, &bkp, sizeof(*st)); st->window = rw; memcpy(rw, wcopy, 131072);
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
                            if (best2 < 0) { snprintf(why, whysize, "CHUNK %d BLOCKSCAN REDO FAIL", nch); free(wcopy2); free(out); return total; }
                            unsigned char *rw2 = st->window;
                            memcpy(st, &bkp2, sizeof(*st)); st->window = rw2; memcpy(rw2, wcopy2, 131072);
                            free(wcopy2);
                            st->ex_entry_bit = fbit;
                            rc = LZXdecompress(st, g + fbyte, out, (int)(cend - fbyte), best2);
                            if (rc != 0) { snprintf(why, whysize, "CHUNK %d BLOCKSCAN REDO2 FAIL", nch); free(out); return total; }
                            fwrite(out, 1, best2, o); total += best2;
                            cpos = st->ex_next_byte; st->ex_entry_bit = st->ex_next_bit; first_slice = 0;
                            continue;
                        }
                        free(wcopy2);
                        fwrite(out, 1, 32768, o); total += 32768;
                        cpos = st->ex_next_byte; st->ex_entry_bit = st->ex_next_bit; first_slice = 0;
                        continue;
                    }
                }
                if (!first_slice) { snprintf(why, whysize, "CHUNK %d FAIL at %ld", nch, spos); free(wcopy); free(out); return total; }
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
                        inpos = npre; coff = ncoff; cend = ncend; cpos = coff;
                        unsigned char *rw = st->window;
                        memcpy(st, &bkp, sizeof(*st)); st->window = rw; memcpy(rw, wcopy, 131072);
                        st->ex_entry_bit = 0;
                        rc = LZXdecompress(st, g + coff, out, (int)(cend - coff), 32768);
                        if (rc == 0) { resynced = 1; (*nresync)++; }
                        break;
                    }
                }
                if (!resynced) { snprintf(why, whysize, "CHUNK %d FAIL at %ld, no resync", nch, spos); free(wcopy); free(out); return total; }
                /* resynced: fall through to success handling (wcopy still owned) */
            }
            free(wcopy);
            fwrite(out, 1, 32768, o);
            total += 32768;
            cpos = st->ex_next_byte;
            st->ex_entry_bit = st->ex_next_bit;
            first_slice = 0;
            if (++guard > 10000) { snprintf(why, whysize, "GUARD chunk %d", nch); free(out); return total; }
        }
        inpos = cend;
        nch++;
    }
    free(out);
    return total;
}
