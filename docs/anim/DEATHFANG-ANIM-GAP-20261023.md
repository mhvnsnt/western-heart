# Deathfang motion bank — precise gap (2026-10-23)

**Source priority: KOF XV FIRST (directed KOF 3D teardown, XV > XIV),
KOF XIV second, T3 heihachi proxy LAST (fallback only).** Deathfang's canon
base is Iori Yagami (KOF). His MOVESET data is now 127 moves
(`game/assets/movesets/deathfang.json`): 98 `kof_motion`-documented KOF
moves + 29 T3 heihachi proxy rows (fallback — Iori has no T3 bank; the T3
use is logged here, not hidden).

## Moveset status (done this pass — batch10-special-pull)

+5 documented KOF Iori moves pulled from `game/assets/movesets/iori.json`
(diffed by `kof_motion` id; 5 were missing):
`ya_sakazuki_l1` (Ura 108 Shiki: Ya Sakazuki DM), `getup_low`,
`getup_mid`, `facedown_kick`, `bt_strike`. Renamed to the DEATHFANG —
convention, `anim_ref` re-pointed `kofxv:iori:` → `kofxv:deathfang:`.
8 werewolf-form extras already in the file are Deathfang's own transform
content (attire 2), not Iori's — untouched.

**SHOW-ANIMATION LOCK (owner 2026-10-23):** `anim_set_lock` added;
126/127 moves stamped `"set": "FIGHT"`. The 1 taunt (`moves/taunt`,
"DEATHFANG — Taunt") is stamped `"set": "SHOW"` — taunts wire to
intro/win slots and cutscenes ONLY, never the moveset, without the
user's explicit approval.

## The missing bank — FIGHT vs SHOW

- **FIGHT** — moveset moves, combat stances → the moveset
  (`game/assets/movesets/deathfang.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations →
  intro/win slots and cutscenes ONLY.

### FIGHT clips → combat bank + moveset
KOF XV Iori motion is NOT extracted — every `kof_motion` move's
`anim_ref` (`kofxv:deathfang:*`) is aspirational until the KOF teardown
lane decodes motion (directed: XV > XIV). Needed: stance/idle, the 98
KOF normals/specials/DMs, block/hit/ko, locomotion. Until then the file
binds the flagged heihachi proxy bank for generic actions.

### SHOW clips → intro/win slots + cutscenes ONLY (never the moveset)
- `moves/taunt` — tagged SHOW in-file; wires to the taunt slot only.
- Win pose / intro pose: no documented KOF XV clips on disk — gap for
  the KOF teardown lane. Nothing stubbed.

## Unblock sequence
1. KOF teardown lane decodes Iori's XV motion → wh-anim/1.
2. Tag every clip FIGHT or SHOW at intake (SHOW-ANIMATION LOCK).
3. Bake per-move rows; register the bank; Deathfang binds his own bank —
   the 127 moves already carry `anim_ref`s.
