# Parsed SCVI move tables (Lane 1C, 2026-11-21)

Complete extraction record: every move of all 22 fighters, produced by
running the vendored Scuffle parser offline (see
`../run_parser.py`, `../WH-NOTES.md` under `tools/anim/scvi-scuffle/`).

## How to reproduce

```sh
SCUFFLE_DIR=tools/anim/scvi-scuffle python3 teardown/soulcalibur-6/run_parser.py
```

## Format (per file)

- `fighter`, `source` (`FottenSC/Scuffle movelists/<fighter>.sc6_movelist`),
  `source_sha256`, `source_bytes`, `parser`, `move_count`,
  `attack_count`, `throw_count`, `attack_move_count`, `moves[]`.
- Per move: `move_id`, `animation_id` (the .mot animation id),
  `anim_start_frame`, `anim_max_frame_override`, `motion_multiplier`,
  `speed_multiplier`, `total_frames`, `attack_indexes`, `command_raw`
  (parser's raw command string — may contain `.`/`?` placeholders),
  `attacks[]` (raw 112-byte attack records: hitbox, hit_level, startup,
  active_end, damage, chip, block/hit/counter stun, hit/counter effect,
  launch types, physics vectors), `frame_data[]` (the parser's own
  `Move.get_frame_data()` rows: impact_frame, active_frames,
  recovery_frames, damage, stuns, attack_type, notes such as `TC[5-16]`,
  `TJ[0-112]`, `ARMOR:…`, `[HITBOX n]`, `GRND`).

## Totals

| Fighter | Moves | Attacks | Throws | Attack moves |
|---|---|---|---|---|
| 2B | 3,058 | 434 | 14 | 347 |
| Astaroth | 2,964 | 328 | 61 | 326 |
| Azwel | 2,908 | 296 | 6 | 242 |
| Cervantes | 2,930 | 293 | 18 | 250 |
| Geralt | 2,802 | 212 | 11 | 158 |
| Groh | 2,810 | 191 | 9 | 163 |
| Ivy | 2,961 | 371 | 33 | 299 |
| Kilik | 2,890 | 291 | 17 | 232 |
| Maxi | 2,915 | 307 | 6 | 240 |
| Mitsurugi | 2,869 | 235 | 12 | 191 |
| Nightmare | 3,050 | 349 | 29 | 301 |
| Raphael | 2,853 | 218 | 8 | 193 |
| Seong Mi-na | 2,834 | 255 | 11 | 204 |
| Siegfried | 2,930 | 245 | 12 | 203 |
| Sophitia | 2,857 | 240 | 23 | 213 |
| Taki | 2,971 | 280 | 15 | 245 |
| Talim | 2,914 | 257 | 11 | 234 |
| Tira | 2,930 | 326 | 26 | 288 |
| Voldo | 3,020 | 327 | 14 | 280 |
| Xianghua | 2,969 | 327 | 12 | 270 |
| Yoshimitsu | 3,043 | 339 | 19 | 287 |
| Zasalamel | 2,833 | 227 | 9 | 194 |
| **Total** | **64,311** | **6,348** | — | **5,360** |

## Notes

- Moves with no attacks (stances, transitions, neutral states) are included
  in full — only the attack moves are wired into the WH banks
  (`game/assets/movesets/scvi-*.json`).
- No move names exist in the source data; moves are identified by
  `move_id`. No values here were hand-edited or estimated — this is the
  parser's output verbatim.
- `.mot` animation motion data is NOT in these tables (format uncracked);
  `animation_id` is the pointer that resolves when it is cracked — see
  `../MOT-FORK-20261121.md`.
