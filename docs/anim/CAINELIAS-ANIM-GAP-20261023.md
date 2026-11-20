# Cain Elias motion bank — precise gap (2026-10-23)

**Source priority: WWF No Mercy re-docs DB FIRST
(`game/data/moveset-library/banks/wrestling.json` — 4409 moves, DB labels
from No Mercy re-docs, verified anim clips under
`teardown/wwf-no-mercy/animations/clips/`), T3 king rows LAST (fallback
only).** WMXIX bank (`wmxix.json`) carries only provisional registry
labels — no Undertaker-attributed moves; not a source.

## Moveset status (done this pass — batch10-special-pull)

+5 documented No Mercy Undertaker moves pulled into
`game/assets/movesets/cainelias.json` (41 → 46 moves):
- `2+4` Chokeslam from Hell 01 (`wrestling:mk-0457`, anim_34EB.npy)
- `f+2+4` Two Handed Chokeslam (`wrestling:mk-1155`, anim_37A5.npy)
- `1+3` Swinging Chokeslam (`wrestling:mk-1852`, anim_3A5E.npy)
- `1+2+3+4_u1` Undertaker 01 (`wrestling:mk-4274`, anim_43D4.npy)
- `1+2+3+4_u2` Undertaker 02 (`wrestling:mk-4323`, anim_4405.npy)

Each carries `wwe_bank` / `wwe_source` / `wwe_mk_category` provenance.
Documented: name, input, anim_ref, MK category. Estimated (stated
in-file): damage/frames, by analogy to this file's existing WH SIGNATURE
throws — the bank documents total frames only, and its own provenance
already estimates WH-scale damage. The 5 existing WH SIGNATURE moves
(Tombstone Piledriver, Last Ride, Chokeslam, Hell's Gate, Old School)
were NOT overwritten.

**SHOW-ANIMATION LOCK (owner 2026-10-23):** `anim_set_lock` added;
46/46 moves stamped `"set": "FIGHT"`. No taunts in the file.

## Documented but NOT pulled (precise)
- **Chokeslam 02** (`mk-0761`) / **Huge Chokeslam** (`mk-1163`): same
  inputs as the pulled primaries (`2+4`, `f+2+4`) — filed as verified
  alternates for the WWE lane, not double-added.
- **Undertaker Punch** (`mk-2110`): input `2` collides with the existing
  T3 king row at `2` — filed, not overwritten.
- **Undertaker's Pin** + P1/P2 Win/Break Up/Release/Repeat parts,
  **Chokeslam to Outside** P1/P2 (Win): pin/win-sequence content — SHOW.
  Wire to win slots, never the moveset.
- **Reversal parts** (P1/P2 Reversal 1/3): system pieces for a reversal
  mechanic, not standalone moves — not pulled.

## The missing bank — FIGHT vs SHOW
- **FIGHT** — the 5 pulled moves' No Mercy clips
  (`teardown/wwf-no-mercy/animations/clips/anim_*.npy`) are DOCUMENTED
  and on disk — the WWE lane converts them to wh-anim/1 and registers
  the bank; the moves already carry `anim_ref`s.
- **SHOW** — pin/win parts → win slots and cutscenes ONLY.
