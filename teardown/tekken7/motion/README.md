# Tekken 7 motion path — tkdata → mothead → banks (2026-11-09)

The motion chain for the 9 extracted bases, end to end:

1. **Source binary:** `TekkenGame/Content/Binary/tkdata.bin` (304,756,784 B,
   sha256 `f1523deaa8a17ad4fbd599d23ab9c4bd1e9bed7904277e15244bd5bc183daf3c`)
   from the owner's Steam depot 389731 pull. Held on Release
   `tekken7-gamefiles-v1` (this repo) and on GRE Release
   `t7-depot389731-wave3-20261031`. The local pulled copy was verified against
   the wave3 manifest hash before use (an earlier corrupt pull — different
   hash, stock unpacker died on a truncated zlib stream after 269 files — was
   discarded and re-pulled).
2. **Unpack:** `tools/extract/t7/tkdata_unpack_tolerant.py` (per-entry tolerant
   variant of the GRE-proven `t7_tkdata.py`). Result on the verified copy:
   **1,087 / 1,087 entries recovered, 0 failed** — including
   `mothead/bin/` (57 `<code>mot.bin` movesets) and `mothead/mask/`
   (58 `<code>rotsm.arc` + `common.arc`). The stock unpacker cannot get past
   the one bad stream; the tolerant driver logs and skips instead.
3. **Parsed movesets (committed here):** `tools/extract/t7/t7_motbin_to_json.py`
   run over each target base's `mothead/bin/<code>mot.bin` →
   `<code>mot.json` in this directory (reactions / requirements / cancels /
   moves / throw cameras, frame-data-shaped summaries + full raw lists).
4. **Bank bake:** `tools/anim/t7_generic_bank_bake.py --mothead <mothead dir>`
   consumes the unpacked mothead tree (bin + mask) and bakes each base's own
   generic-action clips (stance / walk / block / hit / KO …) through
   `tools/anim/t7_c8_stance_bake.py`, the same path the in-game T7 stance and
   attack packs were baked from.

## Committed parses (this directory)

| File | Base | Bytes | sha256 (first 12) |
|---|---|---|---|
| `askmot.json` | Asuka Kazama | 6,346,123 | `98fa86559218` |
| `eddmot.json` | Eddy Gordo | 6,877,478 | `6f309ce7ec66` |
| `julmot.json` | Julia Chang | 6,575,595 | `0a479eadbd88` |
| `kinmot.json` | King | 9,690,358 | `fdc439f24311` |
| `lilmot.json` | Lili Rochefort | 6,471,141 | `76701f3190da` |
| `mutmot.json` | Josie Rizal | 6,219,557 | `8cf15819ab8d` |
| `nsamot.json` | Negan | 6,534,075 | `47c7d465bd9a` |
| `stemot.json` | Steve Fox | 7,040,334 | `006bda4bdc84` |
| `xiamot.json` | Ling Xiaoyu | 6,888,706 | `2ff31953ce83` |

Full per-base extraction results: `../T7-BASES-REPORT-2026-11-09.md`.
Background: `docs/handoffs/T7-RIG-MOTION-SOURCES-2026-11-09.md`.
