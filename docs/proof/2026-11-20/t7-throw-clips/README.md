# T7 throw clips for Pantera 1+3 / 2+4 (Lane 3, 2026-11-20)

## What this is

The real Tekken 7 motion for Pantera's two plain front throws, extracted from
the baked T7 graph bank into standalone playable clip files, plus the pure
resolver that makes them the DEFAULT pair (T7-first rule) with the T3 pair as
the working fallback.

- **1+3 Winding Nut** — thrower `common_709` (ThrmvLB2_00, `naco_tukami2l(DVD)`,
  40f @ 60fps) + victim `rotsm_574` (Kg_FLnage00_n, 130f, dmg 35)
- **2+4 Suplex** — thrower `rotsm_534` (ThrmvRB2_00, `msco_rtukami(DVD)`,
  40f @ 60fps) + victim `rotsm_578` (Kg_FRnage00_n, 138f, dmg 35)

Files: `game/assets/anim/t7/king/throws/` (10 clips + `index.json` manifest),
`game/js/t7-throw-clips.js` (resolver + loader + validator),
`game/js/t3anims.js` (+`t7ThrowClipRetarget`, additive only),
`test/t7-throw-clips.test.mjs`.

## Provenance — where the motion comes from

The clips were NOT re-extracted from the `.arc` files. They are the output
of the existing kinmot→graph pipeline (`tools/anim/t7_graph_bake.py` +
`tools/anim/t7_move_bake.py` / `t7_anim64_to_c8.py`), already shipped in
`game/assets/anim/t7/king/graph-clips/` (format `wh-t7-graph-clips/1`).
Each standalone file is the bank record sliced out byte-identical (raw-text
brace slice, never re-serialized — the bank stores floats at fixed 6-decimal
precision, so re-serializing would change spellings). `throws/index.json`
records per clip: shard + shard file, frames, bytes, sha256, graph move id,
anim, arc file, and the `t7_source.sha256` of the baked record.

- Source graph: `game/assets/anim/t7/king/graph.json`,
  sha256 `5f58b79388072e57b809514bcfd074612dbbe0d4a200fc996ab53a3179e03c3c`
  (2,787 moves; thrower moves 1785 / 1787; victim nage moves 2125 / 2129 /
  2135 / 2137 / 2139 / 2141 / 2274 / 2276).
- Bank index sha256 `38f8befac4186566e8684e6703ecdd52e87407f517cad8d6a53df527417368b5`
  (772 clips, 10 shards, 57,046,485 B total). Shard 1 (`clips.01.json`,
  5,470,670 B, sha256 `2782a0484540a9c612a45160999a354c71b2e889484bbb9c7b26cb1054f63d71`)
  holds both thrower clips; shard 3 holds the nage victims except the air
  ones (shard 4).
- Each record's own `t7_source`: conversion "the game's own sampler
  (TekkenGame-Win64-Shipping.exe RVA 0x73ea30, CPU-emulated)", tool
  `tools/anim/t7_anim64_to_c8.py`, exe sha256
  `7f2b68727023ce9f4554b47f5442dad9dfb38c8a9b778f2aa758469e2c2d60ed`;
  applier Kiloutre/BlenderTekkenDirect `TekkenAnimHelper.py`
  `applyRotationFromAnimdata` @ `bebb3d8bc5c4c2c58778ac6af4f87f3dc80062b1`.
  Thrower sources: `kinrotsm.arc` (rotsm_534) / `common.arc` (common_709),
  both "(private GRE repo)". Record sha256
  `67c6938dcb16575acc42423c3637cc7dd86b13bd980a2eeaa301566b3ec9c992`
  (rotsm) / `b345560984dd8d87ba7d8896f2ab7a0f7d13d0ff4bcd710d3e164bb9d3c9f623`
  (common_709).

### On `kinmot_move_clip_map.csv` saying UNRESOLVED

`docs/research/t7-move-clip-maps/kinmot_move_clip_map.csv` rows 1787
(ThrmvLB2_00 / clip 709, `BLOCKER_MAIN_MOTA_NOT_IN_TKDATA`) and 1789
(ThrmvRB2_00 / clip 534, `SOURCE_IDENTIFIED_BYTES_UNRESOLVED`) still say
UNRESOLVED — and that is still TRUE for what the CSV tracks: the raw `.arc`
MOTA bytes (the `.arc` files live in a private GRE repo, not in tkdata).
What is resolved here is the PLAYABLE MOTION, via the graph bank the
pipeline already baked. The CSV was deliberately NOT flipped to RESOLVED:
flipping it would misrepresent the `.arc` state. If the coordinator wants
the CSV to track bank resolution too, that is a separate docs change
(a new status value, e.g. `RESOLVED_VIA_GRAPH_BANK`).

## Verification (node probe, `test/t7-throw-clips.test.mjs`)

All 10 clips decode clean: 0 NaN quats, 0 zero quats, all quat norms within
0.01 of 1, `root_t` length == frames, `root_motion_fwd_m` length == frames.
Frame counts: throwers 40f each; victims 130 / 138 / 226 / 160 / 203 / 240 /
90 / 155f. FK against `skeleton.json` (21 joints, same math as Lane M's
probe and `t3_bank_facing.py`):

| clip | role | frames | chest-up max | torso-pitch max | rootY range |
|---|---|---|---|---|---|
| `rotsm_534` | 2+4 thrower | 40 | **33.5° @f17** | 37.7° @f18 | 1.000–1.071 |
| `common_709` | 1+3 thrower | 40 | **38.7° @f20** | 40.9° @f20 | 0.988–1.070 |
| `rotsm_574` | 1+3 victim (front) | 130 | 113.4° @f54 | 116.3° @f54 | 0.139–1.576 |
| `rotsm_578` | 2+4 victim (front) | 138 | 105.9° @f76 | 108.6° @f76 | 0.058–1.095 |
| `rotsm_588` | victim (left) | 226 | 49.0° @f33 | 49.2° @f39 | 0.384–1.165 |
| `rotsm_590` | victim (right) | 160 | 96.2° @f54 | 89.0° @f54 | 0.531–1.311 |
| `rotsm_592` | 1+3 victim (back) | 203 | 120.7° @f88 | 126.4° @f88 | 0.393–1.069 |
| `rotsm_594` | 2+4 victim (back) | 240 | 63.2° @f153 | 64.2° @f153 | 0.917–1.164 |
| `rotsm_716` | 2+4 victim (air) | 90 | 103.2° @f50 | 109.8° @f49 | 0.164–1.071 |
| `rotsm_718` | 1+3 victim (air) | 155 | 111.4° @f62 | 107.2° @f62 | 0.074–1.255 |

The thrower numbers reproduce Lane M's independent analysis exactly
(`rotsm534-analysis.txt`: chest 33.5° @f17–18, hips 2.3° max, rootY
1.000–1.071, fwd max 0.545 m; common_709 chest 38.7°, hips 34.1° @f9,
rootY 0.988–1.070). King stays on his feet in both T7 throws — chest bend
~33° / ~39°, never horizontal — unlike the T3 pair, where the thrower goes
prone (torso pitch 88.8°) and the victim fully inverted (172.1°). The T7
victims DO go over (front victims past horizontal, 108–116°), as a thrown
victim should. Root travel: throwers +0.19 m fwd; front victims +2.38 m
(574) / −0.16 m net (578, max +0.26 m) — raw T7 root channels, NOT the pair
drive (see below).

## Victim pairing — how the five reactions were matched

Each throw move's cancel list (graph.json) carries five rows at the connect
window [12, 14], one per throw direction, pointing at the victim's reaction
move. The requirement ids behind them, resolved across ALL 43 throw-class
moves (damage == 0x4000) in the graph:

| req list | condition | points at (43 throws) | situation |
|---|---|---|---|
| 2594 `[[3, 1536]]` | 3 | front reactions (`*F*nage`, throw-specific fronts) | front |
| 1610 `[[5, 1536]]` | 5 | `Kg_Lnage_n` (29×) | left |
| 1612 `[[6, 1536]]` | 6 | `Kg_Rnage_n` (29×) | right |
| 1614 `[[4, 1536]]` | 4 | `Kg_BLnage_n` / `Kg_BRnage_n` / `Kg_BCnage_n` | back |
| 2598 `[[27, 2536]]` | 27 | `Kg_Air*` | air |

This agrees with `docs/proof/2026-11-10/t7-requirements/README.md`
("Throw-side cases 2..16 compare the id with a computed throw direction")
and with the damages booked on the nage moves: front 35 (= documented
front-throw damage), right 42, back 60 — the known T7 King throw damages.
Correction to Lane C (PR #1749): victim-side T7 clips are NOT absent from
the repo — all eight nage clips are in the graph bank (shards 3–4). What
was missing was the pairing, which is what this lane resolved. Note the
`*i` moves (e.g. ThrmvLB2_00i) share the thrower's clip and carry no
distinct victim clip — Lane M's note stands for those.

UNPROVEN, flagged not guessed: which physical side "left" / "right" is.
The names only say L/R; the engine's computed throw direction is not in
the shipped data, so the left/right orientation cannot be proven from the
repo. The front default needs no left/right call. A playtest must confirm
the victim does not mirror on side throws before side situations are
trusted live.

## What is NOT done by this PR (sequenced by the coordinator)

**The live game does NOT play T7 throws yet.** This PR delivers the clips,
the resolver, and the retarget helper. The selection-path edit belongs to
Lane 1 (owns `fighter.js` `_throwPairFor` / `t3-throw.js` `selectThrow`).
Exact integration (for Lane 1 to sequence; no file in this PR touches it):

1. In `Fighter._throwPairFor` (game/js/fighter.js), AFTER `selectThrow`
   succeeds and `resolveThrowClips` returns banks — only when
   `this.attackName` is `'1+3'` or `'2+4'` — resolve the T7 pair for the
   situation: `resolveT7ThrowPair(this.attackName, situation)` where
   `situation` is `'front'` for quadrant 0, `'back'` for quadrant 2,
   `'left'`/`'right'` for quadrants 1/3 (per the victim's side; see the
   unproven note above), `'air'` when the victim is airborne. Attach the
   result (or null) as `pair.t7`. Do NOT replace the T3 selection: the T3
   pair still supplies the anchors, damage time, break windows, and the
   fallback.
2. In `Fighter._bindThrowPair`, AFTER the T3 bind succeeds — following the
   existing DW Surge Kit precedent in the same function (`_dwThrowAction`,
   "the victim keeps the T3 reaction, the pair root still follows the
   pack anchors, and the pack's damage time / duration still time the
   pair") — if `pair.t7`, load both records with `loadT7ThrowPair` and
   retarget them with `t7ThrowClipRetarget('pantera', key, record, model,
   THREE)` (new, additive, in `t3anims.js`; mirrors `ensureDwMoves`:
   fetches the T7 king skeleton once into `_t3skelCache`, then
   `jsonToClip` + `retargetT3Clips`, which analyzes the rig on first
   use — no captured rest pose needed). On success, swap
   `pair.throwerAction` / `pair.victimAction` for the retargeted actions
   (`Object.assign(this.t3actions, createT3Actions(this.mixer, rc, THREE))`,
   same as `_reactionAction`); on ANY failure, keep the T3 actions.
   That is the T7-default-with-T3-fallback: T7 plays when it loads, T3
   plays when it does not.
3. Known limits, same as the DW swap (do not "fix" by inventing motion):
   the pair clock, anchors, damage time, and break windows stay the T3
   pair's; the T7 thrower clip (40f) ends before the pair does and the
   T7 front victim clips (130/138f) run past it — what the thrower does
   after its clip ends (hold last frame vs blend to idle) is Lane 1's
   call at integration time; the T7 victim's own root travel must NOT
   drive the pair (the shared-frame drive still reads the T3 pack
   anchors). Break windows and damage timing for the T7 pair come from
   the T3 entry until T7 frame data is wired (the nage moves' own
   damages — 35 front / 42 right / 60 back — are recorded in the table
   for that follow-up).
4. The T7 graph path (`?t7graph=1`) still marks throws unsupported
   (`fighter.js`: `'throw: clip only, NO GRAB (unsupported)'`) and the
   driver still cannot step through a throw: at the connect frame the
   victim-selection conditions (3/4/5/6/27) are unknown to
   `makeEvalCond`, so `stepCancel` in strict mode blocks as ambiguous.
   This PR does not change that path; throws keep the T3 pair system
   with T7 clips swapped in, per (1)–(2) above.

## Open items

- Live playtest of the T7 pair (needs the Lane 1 integration above):
  thrower upright through the throw, victim going over, pair in sync,
  break input still working on the T3 window.
- Left/right orientation on side throws (unproven — see above).
- Thrower end-of-clip behavior after f40 (hold vs idle blend).
- T7-native damage timing / break windows (nage damages recorded; T7
  frame data not yet wired for throws).
- `kinmot_move_clip_map.csv` rows 1787/1789: left UNRESOLVED on purpose
  (raw `.arc` bytes); coordinator decides on a `RESOLVED_VIA_GRAPH_BANK`
  status (see Provenance).
