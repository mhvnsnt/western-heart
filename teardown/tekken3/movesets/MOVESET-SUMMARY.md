# Tekken 3 Moveset Extraction (USA SLUS_004.02)

Extracted from the 7 motion banks with the verified USA table addresses. Move names are not stored in the banks (they live in the ARC move-list text); moves are identified by move-index slot and row.

| Fighter | Bank type | Move rows | Attacks (active window) |
|---|---|---|---|
| king | 3 | 652 | 218 |
| yoshimitsu | 4 | 449 | 247 |
| xiaoyu | 7 | 594 | 243 |
| jin | 9 | 413 | 242 |
| bryan | 12 | 365 | 188 |
| heihachi | 13 | 383 | 215 |
| gunjack | 16 | 391 | 249 |

## Round 2 — remaining banks (2026-10-20, full-wiring lane)

Extracted with the same parser (`tools/local/moveset_extract.py`, `extract_bank`)
and the same USA EXE tables, from the 13 divmot banks extracted the same day
(see `../CANON-CONVERSION.md`). 5,663 additional move rows. Bank type 15
(Mokujin) has no local bank — BNS record 295 is size 0 in `../bns-table.pkl` —
so no Mokujin moveset exists yet.

| Fighter | Bank type | Move rows | Attacks (active window) |
|---|---|---|---|
| paul | 0 | 372 | 193 |
| law | 1 | 459 | 236 |
| lei | 2 | 604 | 275 |
| nina | 5 | 529 | 212 |
| hwoarang | 6 | 496 | 216 |
| eddy | 8 | 436 | 242 |
| julia | 10 | 360 | 197 |
| kuma | 11 | 303 | 194 |
| ogre | 14 | 330 | 194 |
| anna | 17 | 560 | 221 |
| bosconovitch | 18 | 647 | 268 |
| gon | 19 | 369 | 157 |
| forestlaw | 20 | 198 | 116 |

## Input encoding

Branch `command` words decode per n0madic moves.md: bits 0-3 = LP/RP/LK/RK, bit 4 = any, bits 5-13 = numpad directions; 0xC001 = f,f; 0xC002 = b,b; 0xC00D = no input; 0xC00E-0xC04C / 0xC7FF-0xC827 = motion sequences from USA EXE tables 0x800954D0 (63) / 0x800955CC (41).

## Frame data columns (CSV)

`stream_frames` = total frames; `active_first`/`active_last` = hit active window; `damage` = base damage; `hit_freeze` = defender freeze frames; `step_per_frame` = forward movement/frame; `stance_slot` = stance after move; `inputs` = branch commands -> target slots with frame windows.
