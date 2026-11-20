# Pantera — complete moveset, including named-system entries

**Date:** 2026-10-24. **Base:** main, Pantera file `game/assets/movesets/pantera.json`
(874 moves, git sha `25cb48bee3935bdce92fb7b3326cd37c41e54178` at read time;
re-verify at PR time — if main moved, this change re-applies to the fresh file).
**Buttons:** LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2,
LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.
**Canon law:** Tekken names below are technical-only (moveset/wiring record).
No famous names in-game; no invented canon.

## Correctness rule (user 2026-10-24 22:09 CDT, tightened)

> "Get the animations straight from the Tekken files of the things we switched
> them from, and add them into the things we switched them to correctly."

For every renamed system, an animation is ONLY correct when it is the original
system's anim from the Tekken files. Anything not yet extracted is UNMAPPED
(tracked, extraction is the unblock). A T3 anim may serve as a temporary
in-game fallback, but is NEVER recorded as the correct mapping. No
class-matching, no stand-ins presented as correct. This supersedes any looser
"T3 fallback" wording for these systems. The same rule is written into the
`named_systems` object added to `game/assets/movesets/pantera.json` by this
change, so the file itself carries the status — this doc is the evidence
record, the file is the entry.

## Entries (all live in `named_systems` in `game/assets/movesets/pantera.json`)

### Rinne (state) — Tekken Rage state

- **Gating (verified in engine on main):** low HP at or below 25% of max HP,
  once per round. `game/js/fighter.js` `_inputCtx` rage flag
  (`hp <= maxHp * 0.25`, not `_rageUsed`); `_rageUsed` is set when an
  `R.`/`RD.` move fires (once per round). `game/js/movesets.js` `_pressV2`
  offers the `R.` prefix ONLY while gating holds. `RD.` exists only in the
  legacy resolver; Pantera has no `RD.` keys, his drive is `R.d/b+1+2`.
- **Presentation: PARTIAL, not claimed.** `fighter.js` `setRageAura()` exists
  but has NO caller in `fighter.js` (verified by grep). Small HUD tag +
  gauge + aura per spec are NOT verified wired by this change. No banner,
  per spec. Full-repo HUD grep (game.js, menus) is owed before presentation
  is called done.
- **Gates:** Ikari Jishin + Rinne Kōgeki, usable only in Rinne.
- **Damage boost: OPEN QUESTION FOR THE USER — not wired, not assumed.**
  No Rage/Rinne damage multiplier was found in `game/js/fighter.js` or
  `game/js/combat-core.js` on main at read time (`_rageOn` is initialised
  and never set true elsewhere in `fighter.js`). If current behaviour is
  "gating only", that is existing behaviour to be confirmed by the user,
  not this change's decision.
- **Correct anim:** UNMAPPED (Rage state presentation in WH canon look).

### Ikari Jishin (super) — Tekken Rage Art

- **Move:** key `R.d/f+1+2`, name "Rage Art", input "(During Rage) d/f+1+2",
  T7 id `king_184`, `anim_ref` `t7:king:king_184`.
- **Numbers (from the file, not assumed):** damage 32 (body) / raw
  `55 [57]`, startup 20f (T7), on_block `-22`, on_hit KND, mid, knockdown,
  heavy, limb both, soulGain 13.
- **Correct anim:** UNMAPPED — T7 King Rage Art clip for `king_184`.
  No playable clip exists in the repo today (all `t7:` refs have no clip
  bytes; T7 clips are CLIP-UNRESOLVED until the live-memory extraction:
  running T7 + TKMovesets2, Practice-mode P1 export, ~1,702-entry MOTA,
  join `anim_ref` − 0x8000 — see `~/workspace/gapfill-20261024/extraction-100/01-t7-live.md`,
  do not re-derive it here).
- **Temporary fallback:** NONE wired (no `t3_row`, no `anim_t3` on this
  move). Today it plays donor/pool/generic via `_attackClipPlan`.
- **Fixed by this change:** (1) `slots['R.d/f+1+2']` repointed to itself —
  it previously fired `R.df+1+2` "Anger Of The Beast", a T8 move with
  damage 0, so the super input was effectively dead in Rinne;
  (2) `rageArt: true` added — read by `fighter.js` and `combat-core.js`
  armor logic. Same hijack pattern exists roster-wide (see the other-7
  status doc); only Pantera is changed here.

### Rinne Kōgeki (drive) — Tekken Rage Drive

- **Move:** key `R.d/b+1+2`, name "Rage Drive", input "(During Rage)
  d/b+1+2", T7 id `king_185`, `anim_ref` `t7:king:king_185`.
  NOT "Rinne Waza" (rejected by the user) and NOT "Rinne Jutsu" (picked
  then voided/reversed by the user). Do not wire either name anywhere.
- **Numbers (from the file):** damage 14 (body) / raw `24 [28]`, startup
  20f (T7), on_block `+9`, on_hit LAUNCH, mid, launch, heavy, limb both,
  soulGain 10. Slot `R.d/b+1+2` already points at itself (no hijack).
- **Correct anim:** UNMAPPED — T7 King Rage Drive clip for `king_185`
  (same live-extraction unblock as above).
- **Temporary fallback:** NONE wired. Today donor/pool/generic.
- **Fixed by this change:** `rageDrive: true` added (read by
  `fighter.js`).

### Kongō (armored strike) — Tekken Power Crush

- **Move:** NONE identified. 0 Pantera moves carried any of
  `powerCrush`/`power_crush`/`screw`/`tornado`/`rageArt`/`rageDrive` before
  this change (this change adds only the two Rage flags above).
- **Identification is itself UNMAPPED:** the file's `t7` blocks carry no
  Power Crush flag. The `t7` crush field (70 moves) is high/low evasion
  crush, NOT Power Crush — do not conflate them (Stage 0 trap, confirmed).
- **Armor spec (from engine, not invented):** `combat-core.js`
  `POWER_CRUSH_ARMOR_FRAMES` 8; absorbs mid/high; damage lands; swing is
  not interrupted. `isPowerCrushMove` reads `move.powerCrush` /
  `power_crush` / `powercrush` or `t7`/`t8.powerCrush`.
- **Correct anim:** UNMAPPED. **Unblock:** a T7 frame-data source carrying
  the Power Crush flag for King, joined by move id, plus T7 clip
  extraction for the identified move(s).

### Ōgi (toolkit) — V-System

- **Components, BY FUNCTION ONLY** (component WH names still open, future
  work): skill, trigger, reversal, shift. No move identified for any
  component.
- **Correct anim:** UNMAPPED, all four components. V-System is not a
  Tekken system, and no V-System extraction package exists in the
  extraction-100 set (T7, VF5, TTT2, 2K22 only) — the extraction route
  for V-System clips is itself an open item, not assumed.
- **Temporary fallback:** none.

### Spin Juggle — Air Form + Floor Form

- **Mechanic is ON MAIN** via merged PR #1060 (`game/js/combat-core.js`,
  `game/js/fighter.js`): Screw spins the airborne opponent into a slump
  (`SCREW_SLUMP_STUN` 0.9s), Tornado flips into a ground bound
  (`TORNADO_BOUND_STUN` 0.8s), one extender slot per combo. The mechanic
  exists; Pantera has no flagged extender moves feeding it yet.
- **Air Form (Air Spin) ← Tornado (T8):** UNMAPPED. Pantera's file carries
  0 `t8` blocks and 0 tornado flags. T8 clips are not extractable from
  this VM (disk not accessible) and no T8 extraction package is landed.
- **Floor Form (Floor Spin) ← Screw (T7):** UNMAPPED. No Pantera move
  carries a screw/tailspin flag (engine reads `move.screw` /
  `tailspin` / `screwAttack` or `t7.screw`; 0 present), and the file's
  `t7` blocks carry no Screw flag, so identification is UNMAPPED too.
  Tailspin is T8's word for Screw and collapses into this form — NO
  third form.
- **Name trap:** moves named "Leg Screw" / "Screwdriver" are throws, NOT
  the Screw mechanic. Never flag them from their names.

### Amatsu Rinne — EXCLUDED

Future powered/transformed form of Rinne. Mechanic NOT designed. NO
moveset or animation work in this change, by instruction. Recorded in
`named_systems` as excluded only.

## What this change does NOT fix (fix-order report, Pantera)

Per the coordinator's Stage 1 order, with honest status per item. Nothing
below is claimed fixed unless it says FIXED.

1. **LP1+RP2 (Battle Itself) jumping animation — NOT FIXED.** Move `1+2`
   (WH signature, damage 19, no clip) falls back through `byInput['1+2']`
   to row 35 first (`1+2__main`, dict index 17, before `1+2~t3.king`
   row 220 at index 772) — row 35 is CONFIRMED AIRBORNE (rise +0.382).
   No exact standing 1+2 clip exists in the bank; no class-matched
   substitute is wired. Real fix path: T7 clip for `king_148` (the T7
   1+2 move data exists in-file on `1+2~t7.king`: damage 24, 18f,
   `-11~-10` block, mid) via live extraction — or an authored standing
   clip. PR #1043's chord fix covered demonio/diablo only, not Pantera.
   This is Batch-adjacent, not a string batch: the signature is a single
   chord, and its fix is a clip, not a sequence.
2. **`2,1` exact-clip — NOT REPOINTED (damage ruling owed).** Slot
   `2,1` still fires `2,1~t8.king` (body damage 16) while the canonical
   `2,1` (exact T3 row 220) sits unused. All three `2,1` variants share
   the same T7 block (`king_23`, `mod_damage` "13,16") but carry
   different body damages: canonical 9 (T3 value), T8 twin 16, T7 twin
   15. Repointing the slot silently changes damage 16 → 9 with no ruling
   on which body damage is correct. **Question for the coordinator:**
   which body damage should the fired `2,1` carry — 9, 15, or 16 — and
   does MOD per-hit ("13,16") change that answer? No slot change until
   answered.
3. **11 twin-key wrong-key cases — NOT CANONICALIZED (ruling owed).**
   Spelling twins (`d/f`↔`df`, `WS`↔`ws`, `u/f`↔`uf`, `d/b`↔`db`) fire
   the T8 twin instead of the canonical T7 key (Stage 0 §4b table stands).
   Flipping the aliases is a T7-version switch with damage/frame changes
   per pair, not a pure alias cleanup — and it collides with the
   reconciliation lane's T8 purge (PR #1073, open). Per-pair table +
   ruling owed; no bulk alias flip in this change.
4. **68 strike-class keys on throw rows + 27 special-class keys on throw
   rows — DOCUMENTED, NOT bulk-edited.** Reproduced exactly on main
   from `game/assets/anim/t3/king_on_pantera_leoman/hit_frames.json`
   (190 throw rows): the engine's `fits()` guard already rejects these
   rows at play time, so they pool-pick — they are mislabeled data, NOT
   live grapple bugs. Per-key identity (true strike with a wrong row vs
   throw-chain step with a wrong class) is not established by the row
   flag alone, so no bulk reclassification. Full 95-key list in the
   appendix. Generated row-keys (`1_r153`, `1_c26_r235`, …) are preserved,
   not deleted. Pressable keys in the list (`3+4` on row 435, `1,1`,
   `1+3,1`, `2+4,1`, …) need individual rulings; excluding generated
   keys from `byInput`/donor consideration is an engine change that must
   be play-verified, not slipped in here.
5. **Jab remap row 44 → row 110 — FIXED by this change.** Moves
   `1~t8.king` (damage 9, the actually-fired LP1) and `1~t7.king`
   carried `anim_t3` row 44, match "class-verified remap (anim-fix
   2026-10-23)". Row 44 is the jumping string `u+1,1~t3.king.2`'s row:
   CONFIRMED AIRBORNE DESCENT (starts 1.457, lands 0.901, no rise).
   Both remaps now point at row 110 (the standing jab row of move `1`,
   hip-Y verified standing 0.904 → 0.966 → 0.904). Runtime normally plays
   the notation tier (row 110) before the anim tier, so this fixes the
   notation-failure path; the first-hit path was already row 110.
6. **FC.1 / WS.1 / TACKLE.1 nearest row 39 — NOT REPOINTED (replacement
   UNMAPPED).** Row 39 is a jumping clip (see the row 38/39 resolution
   doc); it is wrong for crouch/rising/tackle LP1 contexts, but no
   verified standing/rising replacement row has been identified. The
   remaps stay recorded as wrong + approximate; no substitute row is
   invented. Pool picks for these moves are audited in the batch lane,
   not trusted from the recorded row.
7. **Chain-throw final chords (6 DANGLING) — PLAY-TEST ITEM, unchanged.**
   Whether the throw-chain system (`grab-hold.js` / `chrono-grapple.js`)
   rescues the `1+2+3` / `1+2+4` final chords is unverified; comma-typing
   cannot fire them. One chain throw end-to-end on the live build is
   owed, with the exact button the user pressed twice still unknown
   (resolver sim: 0 strike→throw double-press reproductions on main —
   hypotheses remain: fixed by merged PR #1024, fighter-layer cause, or
   chain-throw collapse; do not guess the button).
8. **Twin throw key `1~t3.king` (row 290, throw attempt, input LP1) —
   UNCHANGED, play-verify item.** `fits()` rejects row 290 for strikes
   in clip planning; the hazard is resolution paths outside `_pressV2`
   (movelist preview, donor logic, editor). Play-verify LP1 from fight,
   movelist, and trials; re-key or gate only if a path fires it.

## String batches (summary — full tables in the strings doc)

Under the user batch order 2026-10-24 22:23 CDT, Pantera's 81 strings-list
entries split: Batch 1 (LP1/RP2-only) 19, Batch 2 (LK3/RK4-only) 11,
Batch 3+ (mixed) 13, chain-throw chains 38 (separate grapple system, not
a punch/kick batch). Batch 1 wires FIRST in the batch lane. No batch is
fixed by this change: a batch is fixed only when merged + deployed +
played with the right clip (see the strings doc for the sequence-clip
constraint — a single-row rewire is never a string fix).

## Appendix: 95 keys on throw rows (move_class strike 68 + special 27)

Row = `t3_row`; throw flag from `hit_frames.json` (190 throw rows).
`fits()` rejects these at play time → pool pick. Disposition per key is
owed; none changed here.

Strike-class (68): `1_r153` (153), `1+2_r4_r163` (163), `1_r179` (179),
`3+4_r4` (217), `1_c26_r235` (235), `1_c26_r240` (240), `1_c2_r247` (247),
`1_r4_r271` (271), `1_c2_r415` (415), `1_c2_r417` (417), `1_c5_r421` (421),
`1_c3_r423` (423), `1_c3_r425` (425), `1+2_r433` (433), `3+4` (435),
`1_c2_r439` (439), `1_c2_r443` (443), `1_c2_r445` (445), `3+4_r451` (451),
`1_c3_r455` (455), `1_c2_r457` (457), `1_c58_r465` (465), `1_c59_r469` (469),
`3+4_r471` (471), `3+4_r474` (474), `1_c6_r478` (478), `1_c11_r482` (482),
`1_c10_r486` (486), `d/b+1_c10` (488), `1_c15_r503` (503), `1_c14_r505` (505),
`1_c17_r507` (507), `1_c16_r509` (509), `1_c75_r519` (519), `1_c75_r521` (521),
`1_r578` (578), `1_r620` (620), `1_r630` (630), `1_c60_r650` (650),
`1+4,1,1~t3.king` (235), `1+4,1~t3.king.2` (240), `1+2~t3.king.3` (249),
`f+2,1,1,3,3,4,3,2,1+2,1` (271), `1~t3.king.6` (339), `1~t3.king.8` (343),
`1~t3.king.9` (347), `1~t3.king.10` (351), `1~t3.king.11` (355),
`1~t3.king.13` (359), `1~t3.king.14` (363), `1~t3.king.15` (367),
`1~t3.king.16` (371), `1~t3.king.17` (375), `1~t3.king.18` (379),
`1+3,1` (415), `2+4,1` (417), `2+4,1~t3.king.2` (425),
`b,n,f+1+2,1` (455), `b+1+2,1,1+3` (463), `b+1+2,1,2+4` (467),
`b+1+2,1,3+4` (471), `d+1+3,1` (478), `1,1` (584),
`1+4,1~t3.king.4` (564), `1,1~t3.king` (604), `1,1~t3.king.2` (606),
`1,1~t3.king.3` (608), `2+3,1` (632).

Special-class (27): `1_c73` (519), `1_c74` (519), `1_c58` (650),
`1_c59` (650), `1+4,1~t3.king.3` (240), `d/f+3+4,1` (247),
`1~t3.king.7` (339), `1~t3.king.12` (355), `1+3,1~t3.king` (415),
`2+4,1~t3.king` (417), `f,n,b,d/b,d,f+1,1` (421),
`f,n,b,d/b,d,f+1,1~t3.king` (423), `n,d,d/f,f+1,1` (431),
`n,d,d/f,f+1,1,1+2` (433), `d,d/f,d,d/f+1+2,1` (439),
`d/b,n,f+2,1` (443), `d,d/b,d,d/b+1+2,1` (445),
`b,n,f+1+2,1~t3.king` (455), `d/f+2+3,1` (457), `d/b+1+3,1` (482),
`d/b+2+4,1` (486), `d/b+2+4,d/b+1` (488), `d/b+1+3,1~t3.king` (503),
`d/b+1+3,1~t3.king.2` (505), `d/b+1+3,1~t3.king.3` (507),
`d/b+1+3,1~t3.king.4` (509), `n,d/f,n,d/f+2+4,1` (586).

The appendix is a work list, not a set of edits; verify each key against
the file before acting on it.
