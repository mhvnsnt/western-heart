/* Probe driver: try raw LZX (MS-PATCH/WIM framing) at a given offset/window.
   Usage: lzx_try <file> <offset> <window_bits> <outlen> */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "lzx.h"
int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: %s file offset window outlen\n", argv[0]); return 2; }
    const char *path = argv[1];
    long offset = atol(argv[2]);
    int window = atoi(argv[3]);
    int outlen = atoi(argv[4]);
    FILE *f = fopen(path, "rb");
    if (!f) { perror("fopen"); return 2; }
    fseek(f, 0, SEEK_END);
    long fsize = ftell(f);
    fseek(f, offset, SEEK_SET);
    long avail = fsize - offset;
    unsigned char *in = malloc(avail > 0 ? avail : 1);
    if (fread(in, 1, avail, f) != (size_t)avail) { fprintf(stderr, "short read\n"); return 2; }
    fclose(f);
    unsigned char *out = malloc(outlen);
    memset(out, 0, outlen);
    struct LZXstate *st = LZXinit(window);
    if (!st) { printf("INIT_FAIL window=%d\n", window); return 3; }
    int rc = LZXdecompress(st, in, out, (int)avail, outlen);
    printf("rc=%d", rc);
    if (rc == 0) {
        printf(" outlen=%d first64=", outlen);
        for (int i = 0; i < 64 && i < outlen; i++) printf("%02x", out[i]);
        printf("\n");
    } else printf("\n");
    LZXteardown(st);
    free(in); free(out);
    return 0;
}
