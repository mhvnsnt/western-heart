# Akira Yuki (alt) — VF5 model archives

- **Code:** `akixx` · **Style:** —
- **Source:** Virtua Fighter 5 PS3 (BLES00029), Ver.C
- **Release:** `vf5-ps3-v1` — https://github.com/mhvnsnt/western-heart/releases/download/vf5-ps3-v1/

## Archives

| File | Size | Inner files | Contents |
|------|------|-------------|----------|
| `akixx.farc` | 2.5MB | 2 | base body: `, a, k, i, x, x, _, o, b, j, ., b, i, n, `,  , (, m, o, d, e, l, ),  , +,  , `, a, k, i, x, x, _, t, e, x, ., b, i, n, `,  , (, t, e, x, t, u, r, e, s, ) |

## Extraction

`../tools/farc_extract.py` — FArC magic + BE u32 entries + gzip payloads.
Decompressed `*_obj.bin` → chrrox 3ds Max script; `*_tex.bin` → TXP.bms (QuickBMS).

## Notes

variant body (4.3MB uncompressed)
