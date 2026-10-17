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

## Input encoding

Branch `command` words decode per n0madic moves.md: bits 0-3 = LP/RP/LK/RK, bit 4 = any, bits 5-13 = numpad directions; 0xC001 = f,f; 0xC002 = b,b; 0xC00D = no input; 0xC00E-0xC04C / 0xC7FF-0xC827 = motion sequences from USA EXE tables 0x800954D0 (63) / 0x800955CC (41).

## Frame data columns (CSV)

`stream_frames` = total frames; `active_first`/`active_last` = hit active window; `damage` = base damage; `hit_freeze` = defender freeze frames; `step_per_frame` = forward movement/frame; `stance_slot` = stance after move; `inputs` = branch commands -> target slots with frame windows.
