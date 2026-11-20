# Akira Yuki — VF5 model archives

- **Code:** `aki` · **Style:** Bajiquan
- **Source:** Virtua Fighter 5 PS3 (BLES00029), Ver.C
- **Release:** `vf5-ps3-v1` — https://github.com/mhvnsnt/western-heart/releases/download/vf5-ps3-v1/

## Archives

| File | Size | Inner files | Contents |
|------|------|-------------|----------|
| `aki.farc` | 759B | 2 | base body: `, a, k, i, _, o, b, j, ., b, i, n, `,  , (, m, o, d, e, l, ),  , +,  , `, a, k, i, _, t, e, x, ., b, i, n, `,  , (, t, e, x, t, u, r, e, s, ) |
| `akiitm.farc` | 34.7MB | 176 | customization items: `, *, _, o, b, j, ., b, i, n, `,  , (, m, o, d, e, l,  , d, a, t, a, ),  , +,  , `, *, _, t, e, x, ., b, i, n, `,  , (, t, e, x, t, u, r, e,  , d, a, t, a, ) |

## Extraction

`../tools/farc_extract.py` — FArC magic + BE u32 entries + gzip payloads.
Decompressed `*_obj.bin` → chrrox 3ds Max script; `*_tex.bin` → TXP.bms (QuickBMS).
