# Soulcalibur II — Canon Conversion, 2026-10-20

Standard (PR #397 §3): canon conversion is logged, never silent; unmapped
identities are flagged, never invented.

## State

- Source identities for the 24 character slots were established from the
  game's own data: FUN_00047440 file-number table (XBE) → slot/tag →
  `CHARACTER-MAP.md` identifications (from the v33 moveset files' signature
  moves, cross-checked against published FAQs; Nightmare additionally
  anchored by the community concordance numbering, PR #29 gate G1).
- **Western Heart canon names: NONE assigned yet.** Per `CHARACTER-MAP.md`'s
  own standing note, WH rename status for the SCII roster is "all PENDING
  owner assignment". This lane does not invent canon names, bios, or
  rename mappings.
- Until the owner assigns canon, the decoded fighters are registered in
  `WIRING-INVENTORY.md` and stored under **source names** as teardown
  reference data (`teardown/soulcalibur-2/models/idxNNN_fighter_placed.glb`,
  NNN = v982 entry). They are **not** presented as Western Heart roster
  fighters and are not registered in `game/js/roster-full.js`.

## Conversion table (to be filled on owner assignment)

| Tag | Source fighter | WH canon | RENAME-MAP entry |
|---|---|---|---|
| 01 | Mitsurugi | PENDING owner assignment | — |
| 02 | Seong Mi-na | PENDING owner assignment | — |
| 03 | Taki | PENDING owner assignment | — |
| 04 | Maxi | PENDING owner assignment | — |
| 05 | Voldo | PENDING owner assignment | — |
| 06 | Sophitia | PENDING owner assignment | — |
| 0b | Ivy | PENDING owner assignment | — |
| 0c | Kilik | PENDING owner assignment | — |
| 0d | Xianghua | PENDING owner assignment | — |
| 0f | Yoshimitsu | PENDING owner assignment | — |
| 11 | Nightmare | PENDING owner assignment | — |
| 12 | Astaroth | PENDING owner assignment | — |
| 13 | (not identified in source map) | — | — |
| 14 | Cervantes | PENDING owner assignment | — |
| 15 | Raphael | PENDING owner assignment | — |
| 16 | Talim | PENDING owner assignment | — |
| 17 | Cassandra | PENDING owner assignment | — |
| 18 | (not identified in source map) | — | — |
| 19 | Necrid | PENDING owner assignment | — |
| 1a | Yun-seong | PENDING owner assignment | — |
| 1d | Spawn (Xbox guest) | PENDING owner assignment | — |
| 1e | UNIDENTIFIED in source data | — | — |
| 1f | UNIDENTIFIED in source data | — | — |
| 20 | UNIDENTIFIED in source data | — | — |

Moves retain their source names in the extracted v33 command lists; move
renames, if any, will be logged here and in `RENAME-MAP.md` when the
moveset-library conversion runs.
