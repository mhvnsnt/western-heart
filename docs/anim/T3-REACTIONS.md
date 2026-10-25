# T3 hit reactions and throws: data and runtime contract

Lane E, 2026-10-24. Owner: "got the fighting and combos and targeting and hit reactions and grapple receiver
animation or hit connections or any of that done it's all bullshit".

Before this, every bank played one generic `t3_hit.json` (slot `0x9a2`) for every hitstun and for being thrown, and
`t3_grab.json` was a copy of `t3_heavy.json`. Tekken 3 picks a different reaction move for every attack, guard,
side, counter hit, juggle and knock-down, and a throw is a pair of moves: the thrower's and the victim's. This lane
decodes that system from the owner's disc and bakes every clip it can start. The lead agent wires it into
`fighter.js`; this lane edits no runtime code.

**Source (owner law, T3 is the fallback):** no reaction or throw data from T5, T6, T7, T8 or TTT2 is decoded in the
repo. T7 fighter animation coverage is 0 of 51 (`teardown/tekken7/TEKKEN7-ROSTER-COVERAGE.md`). T6 `DATA401` is
still encrypted. T5 `TK5DATA2` motions are named but not extracted. TTT2 is not extracted, and T8 has models and UI
only. The T3 use is logged in `docs/anim/PROCEDURAL_AUDIT.md`. Nothing is authored or guessed: every value comes
from `SLUS_004.02` and the divmot banks, with SHA-256 recorded in the files.

## Files

| File | Made by | What |
|---|---|---|
| `game/assets/anim/t3/reactions.json` | `tools/anim/t3_reaction_tables.py` | EXE tables, per-bank row reactions, throws, breaks, the slot plan and coverage. |
| `game/assets/anim/t3/<bank>/reactions.pack.json` (22 banks) | `tools/anim/t3_reaction_bake.py` | Baked clips, keyed by move slot. |
| `test/t3-reactions.test.mjs` | lane E | `node --test test/t3-reactions.test.mjs` |

Rebuild:

```sh
export T3REMAKE_RESEARCH=<n0madic/Tekken3Remake>/tools/research
python3 tools/anim/t3_reaction_bake.py --all            # or --bank paul; --merge bakes only new slots
python3 tools/anim/t3_reaction_tables.py                # writes reactions.json and its coverage
node --test test/t3-reactions.test.mjs
```

### What the game does

These rules come from n0madic/Tekken3Remake `docs/research/code/combat.md`, `moves.md` and
`formats/divmot-banks.md`. The code ports are `tools/research/fight_sim.py` and the remake's
`core/fighter/move_system.gd` (`_hit_select_reaction`, `_air_reaction_kind`, `throw_victim_start`).

- **Reaction value.** An attacking move row's `+0x32` names the defender's reaction.
  - A value below `0x1000` is a record of `g_reactionRecords` (EXE `0x80010CE8`: 633 records of 21 `s16`).
  - A value `0x1nnn` is entry `nnn` of `g_throwVictimSlots` (`0x800174C4`), which gives the victim move of a throw.
  - `+0x34` is a close-range entry of `g_closeReactions` (`0x800177DC`): `[reaction, distance]`.
- **Slot lookup (`DivmotMergeSharedSlots`).** A slot is looked up in the defender's own bank first. If the
  defender's bank does not define it, the slot comes from the opponent's bank. This is how a throw's victim move,
  which only the thrower's bank defines, reaches the victim. Attacker-specific staggers reach the defender the same
  way.
  - Verification shows every slot named by a bank's own records is defined by that bank, so the lookup always lands.
- **Address check.** The research uses Japan Rev.1 addresses. The USA EXE is identical in place for
  `0x80010000–0x8002172C`, which holds every table used here. This is verified below.

## `reactions.json` schema (`wh-t3-reactions/1`)

| Key | Content |
|---|---|
| `exe`, `exe_sha256`, `common_bank*`, `addresses` | Inputs and EXE addresses. |
| `verification[]` | `{check, pass, detail}`. All must pass, or the tool writes nothing. |
| `record_fields[21]` | Names of the 21 record words. Words 0–13 are slots: `front`, `front_crouch`, `counter`, `counter_crouch`, `side1`, `side1_crouch`, `side3`, `side3_crouch`, `back`, `back_crouch`, `guard`, `guard_crouch`, `down`, `down_other`. Words 14–20 are push-back data: `push_angle`, `push_hit`, `unused_angle`, `push_counter`, `push_angle_down`, `push_down`, `push_guard`. |
| `records[633][21]` | `g_reactionRecords`, as `s16`. |
| `forced_record[21]` | The record used when a thrown body hits a fighter (Tekken Force). |
| `throw_victim_slots[418]` | `g_throwVictimSlots`: 397 entries, then the words a 21-word read reaches. |
| `close_reactions[58]` | `[reaction value, distance]`. |
| `air_kinds[6]` | `[ground offset, air move slot]` for kinds 0–5: `0xD56`, `0xD61`, `0xD62`, `0xD63`, `0xD64`, `0xD57`. |
| `push_tables`, `launch_push` | `g_pushTables` (`s16`, 710 entries; an entry is `frames, speed, off[8]`) and the 8-step launch push. |
| `transitions`, `stance_slots`, `collapse_slot` | Transition codes `0x21`–`0x2B`; stance slots 3 and 40; KO collapse `0xD66`. |
| `common_rows{row: [reaction, close, attack_class]}` | The divmot99 move rows that carry a reaction. |
| `banks{<dir>}` | One entry per runtime folder; 22 folders. See the next table. |
| `coverage{<dir>}` | Planned, baked and missing slots, by role, plus throw counts, read from the packs. |

Each `banks{<dir>}` entry holds:

| Key | Content |
|---|---|
| `divmot`, `divmot_sha256`, `bank_type` | The motion bank (`armorking` and `king_on_pantera_leoman` share `divmot03`; `heihachi` and `heihachi_on_jin` share `divmot13`). |
| `rows{<row>: [reaction, close, attack_class]}` | Every own row with a reaction. `<row>` is the bank row that `t3_row` and `rows.pack.json` use. |
| `throws[]` | Every move a transition-`0x21` branch of this bank starts. See [Throws](#throws). |
| `throw_attempts{<row>}` | A move with situation-conditioned `0x21` rows: `{slot, attack, attack_class, branches[]}` in BranchFind order. |
| `throw_inputs[]` | Stance commands (slot 3 standing, slot 40 crouching) that start a throw attempt. `LP+LK` is 1+3; `RP+RK` is 2+4. `cond 36` is the turned-away version. |
| `slots{<hex slot>}` | The slot plan for this bank's pack: `{row ("common:N" for divmot99), src, frames (60 fps), state, next (default continuation slot), air?, hold?, launch_entry?, roles[]}`. Roles are `hit`, `guard`, `air`, `collapse`, `victim`, `throw`, `escape` and `chain` (continuation). |

## `reactions.pack.json` schema (`wh-anim-pack/1`, the `rows.pack.json` layout)

| Key | Content |
|---|---|
| `bank`, `body_kmd`, `stance`, `target_rig`, `skeleton`, `sha256` | The same body, rig and bank as the folder's `rows.pack.json`. The tool checks them by SHA-256 and refuses to bake on a mismatch. |
| `bones` | WH-Canonical-22. Joints the 18-part T3 rig lacks (Spine, Neck, toes) are identity. Rotations are local to the parents in `skeleton.json`, as in the shipped `t3_*.json` clips; `decodePackRow` in `t3anims.js` reads them unchanged. |
| `fps` | 30 (the 60 fps stream sampled every 2 frames). |
| `anchor_mm_to_rig_m` | Converts T3 millimetres to this rig's metres (rig hip height / T3 hip height / 1000). |
| `rows{"0x8b8": rec}` | **Keyed by move slot (hex)**, because records, victim entries and air kinds name slots. |
| `rec` | `slot`; `move_row` (bank row, or `0x40000000` + divmot99 row); `src` (`own` or `common`); `stream_frames`; `n`; `roles`. |
| `rec.q` | `int16 [n][22][4]`: xyzw × 32767. |
| `rec.rx`, `rec.ry`, `rec.rz` | `int16 [n]`, as in `rows.pack.json`: hip delta from frame 0 in the yaw-normalised frame, in mm on the rig. |
| `rec.ax`, `rec.ay`, `rec.az` | `int16 [n]`: decoded root channels 0–2 in mm, in the move's heading frame. +Z is forward, +Y is up, and +X is the T3 `+x` side, which the bake names Left. This is the root's offset from the move anchor. |
| `rec.yaw0` | Radians: frame 0's Hips yaw in the heading frame. `retarget()` normalises this away by turning every clip's frame 0 to +Z. |
| `missing{"0x…": reason}` | Slots that could not be baked. |

Lookup used by every rule below. V is the defender's (or victim's) folder, A is the attacker's (or thrower's).
Folders are the `game/assets/anim/t3/<dir>` names that `t3anims.js` `T3_BANKS` points at.

```js
function reactionClip(V, A, slot) {                 // MoveLookup after DivmotMergeSharedSlots
  const k = '0x' + slot.toString(16);
  for (const d of [V, A]) if (R.banks[d].slots[k])   // the first bank that defines the slot
    return packs[d].rows[k] || null;                 // null only if listed in packs[d].missing
  return null;                                       // never happens for a decoded record (verified)
}
```

## Picking a hit reaction (HitSelectReaction, `0x8002EDF8`)

**Inputs**

| Input | T3 meaning | How to compute it in `fighter.js` |
|---|---|---|
| `A`, `row` | The attacker's bank folder and the T3 row of its current move | `move.t3_row` on WH moves; divmot99 rows use `R.common_rows`. |
| `V` | The defender's bank folder | — |
| `guarded` | HitClassify | `receiveHit`'s `guarded`. |
| `crouch` | Defender `state & 2 == 0` (not standing) | Crouching or crouch-guarding. |
| `counter` | Counter hit | `receiveHit`'s `counter`. |
| `airborne` | `inAir` or state bit 10 | `!onGround`, juggled. |
| `down` | Defender lying (state `4`) | `knockdown` on the ground. |
| `downOther` | Lying the other way (state `0x200`) | — |
| `quadrant` | The defender's `facingQuadrant`: where the attacker is, relative to the defender's heading | 0 = in front; 1 = on the defender's +X side (the bake's Left); 2 = behind; 3 = on the defender's −X side (Right). Each covers 90°, centred on its axis. |
| `close` | Fighters closer than `close_reactions[close][1]` | T3 units. Multiply by the pack's `anchor_mm_to_rig_m` to get metres. |

**Rules**

```js
const [react, closeIdx, cls] = R.banks[A].rows[row] ?? [0, 0, 0];
// MoveStep gate (remake move_system.gd step()). Class 0 always reacts. Class 2 reacts only on a grounded,
// standing defender. Class 1 and class 3 never react.
// The class-1 rows (206 of them) are zero-damage catch strikes whose reaction is a 0x1nnn throw entry: their
// 0x21 branches start the throw instead. combat.md's prose says "0 and 1 react"; the data and the port say otherwise.
if (cls === 1 || cls === 3 || (cls === 2 && (airborne || down))) return null;
let v = (close && closeIdx) ? R.close_reactions[closeIdx][0] & 0xffff : react;
if (!v || (v & 0xf000)) return null;                 // 0x1nnn only acts through a throw
const r = R.records[v], c = crouch ? 1 : 0;
let slot, code, push, angle;
if (guarded)        { slot = r[10 + c]; code = 0x23; push = r[20]; angle = r[14]; }
else if (airborne)  { slot = R.air_kinds[airKind()][1]; code = 0x24; }   // then LaunchTrajectory
else if (downOther) { slot = r[13]; code = 0x25; push = r[19]; angle = r[18]; }
else if (down)      { slot = r[12]; code = 0x25; push = r[19]; angle = r[18]; }
else if (counter)   { slot = r[2 + c]; code = 0x26; push = r[17]; angle = r[14]; }
else { const q = quadrant;                           // 0 front, 1 side1, 2 back, 3 side3
       slot = r[[0, 4, 8, 6][q] + c]; code = [0x2a, 0x27, 0x2b, 0x28][q]; push = r[15]; angle = r[14]; }
const clip = reactionClip(V, A, slot & 0xffff);
```

**`airKind()` (AirReactionKind, `0x8002F0E8`)**

- If the defender is already in kind 2 (`0xD62`), or in `0xD63`/`0xD64` past frame 18: use kind 2, or kind 0 when
  the root is more than `0x3FF` (1023 mm) above the ground.
- Kind 1 (slam): the hit points down (`hitDirY > 0x6D`), or the attacker is Jin (bank 9) running slot `0x241`, or
  Gun Jack running `0x14A`.
- Kind 4: quadrant 1. Kind 3: quadrant 3. Both are skipped while the defender is in `0xD58`.
- Otherwise kind 0.
- Kind 5 (`0xD57`) only comes from a launch branch (transition `0x1E`): Gon has 4 and divmot99 has 2.
  `slots[...].launch_entry` marks them. Only Gon defines `0xD57`.

**After the clip**

- Play at 30 fps. When the clip ends, continue with `R.banks[owner].slots[k].next` until slot 3 (standing:
  `t3_neutral`) or slot 40 (crouching). Resolve each step with `reactionClip(V, A, next)`.
- Knock-down chains (air, then lying, then get-up) are in the plan as role `chain`.
- **Push-back.** The push goes from the attacker's direction + `angle` + 180°.
  - `push_tables[push]` frames, at `push_tables[push+1]` speed per 60 fps frame.
  - Then 8 offsets, `push_tables[push+2..9]`.
  - All in T3 units. Multiply by `anchor_mm_to_rig_m` to get metres.
- **KO.** A KO'd fighter standing without an air window plays the collapse slot `0xD66`.
- **Mapping to main's states.** `hitstun`, `knockdown` and `block` currently play the generic `hit`, `launch` and
  `block` clips. Play the picked clip instead.

## Throws

### Data per throw

Each entry of `R.banks[A].throws[]` holds:

| Key | Content |
|---|---|
| `slot`, `row`, `src`, `frames` (60 fps) | The thrower's move. Its clip is `packs[A].rows[hex(slot)]`. |
| `damage`, `damage_frames[]` | Base damage plus the `0x0Bxx` event arguments (MoveTotalDamage), and the event frames (60 fps) where it lands. |
| `victim_slot`, `victim_in_thrower_bank`, `victim_frames`, `victim_events` | The victim's move. `0x02xx` is a camera shake and `0x04xx` is the ground impact. |
| `breaks[]` | `{input: '1' \| '2' \| '1+2', window: [f0, f1] (victim-move frames, 60 fps), escape_slot}`. These are the T3 throw escapes (conditions `0x3A`/`0x3B`/`0x3C`, tap LP / RP / both). |
| `via[]` | How the throw is reached: `from_row`, `from_slot`, `command`, `cond` (+ `cond_kind`: `situation`, `break`, `reversal`, `always`, `condition`), `param` (max distance), `window`, `entry`, `restriction`. |
| `next` | The thrower's continuation. |

### Choosing the throw (main's `startThrowing` / `startThrowLock`)

1. Map the WH input to an attempt slot through `R.banks[A].throw_inputs`: 1+3 is `LP+LK`, 2+4 is `RP+RK`.
   - With `cond 0` the attempt is `0xae8` / `0xaec` in every bank that has them.
   - `cond 36` (`0xb03` / `0xb04`) is the version done with the thrower's own back turned.
2. Walk `R.banks[A].throw_attempts[<attempt row>].branches` in order. Take the first branch whose situation
   matches and whose distance is `≤ param` (T3 units).
3. Work out the situation code (SituationClassify, `moves.md`). It depends on the victim's posture and on which
   side of the victim faces the thrower (`oppQuadrant`):
   - Standing: front 2, back 3, the victim's +X side 4, −X side 5.
   - Crouching: 6, 7, 8, 9.
   - Lying: 10–13, or 14–17 when lying the other way.
   - 18/19: the thrower's own back is turned (`relAngle > 120°`).
   - `0x14`–`0x17` accept the standing or the crouching code: {2,6}, {3,7}, {4,8}, {5,9}.
4. The throw is `t = R.banks[A].throws.find(x => x.slot === branch.throw_slot)`.
   - The thrower clip is `packs[A].rows[hex(t.slot)]`.
   - The victim clip is `reactionClip(V, A, t.victim_slot)`. The victim uses its own bank's row when it defines the
     slot (clones such as Nina and Anna, or Law and Forest Law); otherwise it uses the thrower's row, decoded on the
     thrower's body and played on the victim's skeleton (canonical bone names).
   - **`t.defined === false`** (Forest Law's six standard throws): the thrower's bank lacks the throw row, so the
     game takes the opponent's row for that slot. Use `tv = R.banks[V].throws.find(x => x.slot === t.slot)`. The
     thrower clip is `reactionClip(A, V, t.slot)` and the victim clip is `reactionClip(V, V, tv.victim_slot)`.
   - **`t.victim_note`** (Bosconovitch's 11 reversal moves): `+0x32` is 0, so the victim plays slot 0, the
     round-start stance (`t3_stance`).
   - The keys of `throw_attempts` are the bank row (or `common:N`) that `throw_inputs[].attempt_row` names.

### Shared root frame (transitions `0x21` / `0x22`)

The anchor is the victim's root, so both clips play in one frame.

**At throw start**

- `P` = the victim's root position (x, z) on the ground.
- `H` = the victim's heading turned 180° (transition `0x22` turns the victim, and the thrower aligns to it). In
  `fighter.js`, facing is ±1 along x and `lean.rotation.y = facing·π/2`, so `H_yaw = −victim.facing·π/2`.

**Every frame `f` of the two clips (30 fps, both start on the same frame)**

```js
const k = packs[A].anchor_mm_to_rig_m;              // the thrower's scale, used for both, keeps contact geometry
for (const [fighter, clip] of [[thrower, thrClip], [victim, vicClip]]) {
  const ax = i16(clip.ax)[f], az = i16(clip.az)[f];
  fighter.root.position.x = P.x + ( Math.cos(H_yaw) * ax + Math.sin(H_yaw) * az) * k;  // R_y(H_yaw)·(ax,0,az)
  fighter.root.position.z = P.z + (-Math.sin(H_yaw) * ax + Math.cos(H_yaw) * az) * k;
  fighter.lean.rotation.y = H_yaw + clip.yaw0;                 // the clip's Hips carries the rest of the turn
  // vertical: keep the clip's own hip motion (ry, or ay·k against the rig's rest hip height)
}
```

- In T3 the thrower's heading starts at the quadrant-snapped direction and turns to `H` over 16 frames. With
  main's 2D facing these are the same.
- **Proof from the data** (Paul, `tools/anim/t3_reaction_bake.py` output; anchors are (x, up, forward) in mm):

| Throw | Thrower clip | Victim clip | Result |
|---|---|---|---|
| Front, 1+3 (`0xaeb` / `0xbc5`) | anchor (86, 1044, −912), `yaw0` +2° | anchor (0, 1026, 0), `yaw0` −176° | Face to face, 0.91 m apart. |
| Back (`0xaf0` / `0xcb2`) | +666 mm forward, `yaw0` 144° | `yaw0` 145° | The victim's back is to the thrower. |
| Side, situation 4 (`0xaee` / `0xc0d`) | x −762 mm, `yaw0` 94° | `yaw0` −176° | The thrower stands on the victim's +X side. |

### Timing, damage, break, after

- **Damage.** Apply `t.damage` at `t.damage_frames` (60 fps frame numbers; halve them for the 30 fps clip). For
  example, Paul's front throw lands 30 damage at frame 75 of 102. This replaces `_throwSlamDamage` at the
  procedural 0.55 s.
- **Break.** `t.breaks` gives the break input and window. Paul's front throw breaks with `1`, frames 1–15
  (0.25 s).
  - This replaces main's `lockMove.throw_break` / `lockT` for T3-bound banks.
  - In T3 there is no separate lock: the window is the first frames of the same two clips. Map
    `throwing`/`thrown` to those frames and `throwExec`/`thrownExec` to the rest of the clips, instead of the
    0.9 s procedural lift and slam and the `grab`/`hit`/`launch` clip picks.
- **When the victim breaks.** The victim starts `escape_slot` as a new throw pair: the victim becomes the thrower.
  - Escape clip on the victim: `reactionClip(V, A, escape_slot)`.
  - The original thrower plays that escape's victim move:
    `reactionClip(A, V, R.banks[A].throws.find(x => x.slot === escape_slot).victim_slot)`.
  - Use the same shared-frame rule, anchored at the original thrower's root.
- **After the throw.**
  - The thrower continues with `t.next` (usually slot 3).
  - The victim continues with `R.banks[...].slots[hex(victim_slot)].next`: a lying state, then the get-up chain.
  - T3 lets the victim mash out of the down state after `recoverFrames` = the longer of the two moves, with
    `recoverMash = clamp(damage·32/45 + 34, 34, 66)` (combat.md "Knock-down recovery").

## Coverage

Read from the packs by `t3_reaction_tables.py` (`reactions.json` `coverage`). A slot is **planned** for a bank
when the bank defines it (an own row or a divmot99 row) and some attack, throw, air kind, KO, escape or
continuation can start it on a fighter using that bank. Slots a bank does not define are baked in the bank that
does: the opponent's, the way the game reads them. Roles overlap, so a slot can count in several columns.

| Bank | Baked / planned | hit | guard | air + KO | victim | thrower | escape | chain | Throws (thrower clip) | Victim row in the thrower bank | Missing |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| anna | 427 / 427 | 172 | 38 | 6 | 83 | 86 | 16 | 57 | 86 (86) | 86 | 0 |
| armorking | 568 / 568 | 152 | 32 | 6 | 169 | 176 | 33 | 44 | 176 (176) | 176 | 0 |
| bosconovitch | 374 / 374 | 196 | 43 | 6 | 52 | 67 | 10 | 26 | 67 (67) | 56 | 0 |
| bryan | 317 / 317 | 158 | 32 | 6 | 45 | 47 | 10 | 40 | 47 (47) | 47 | 0 |
| eddy | 276 / 276 | 164 | 30 | 6 | 33 | 35 | 10 | 19 | 35 (35) | 35 | 0 |
| forestlaw_on_law | 156 / 156 | 119 | 25 | 6 | 5 | 0 | 0 | 11 | 0 (0) | 0 | 0 |
| gon | 241 / 241 | 158 | 32 | 7 | 23 | 24 | 7 | 11 | 24 (24) | 24 | 0 |
| gunjack | 275 / 275 | 141 | 30 | 6 | 43 | 45 | 10 | 20 | 45 (45) | 45 | 0 |
| heihachi | 288 / 288 | 163 | 32 | 6 | 39 | 40 | 10 | 20 | 40 (40) | 40 | 0 |
| heihachi_on_jin | 288 / 288 | 163 | 32 | 6 | 39 | 40 | 10 | 20 | 40 (40) | 40 | 0 |
| hwoarang | 363 / 363 | 194 | 41 | 6 | 47 | 48 | 10 | 39 | 48 (48) | 48 | 0 |
| jin | 312 / 312 | 155 | 34 | 6 | 52 | 58 | 10 | 20 | 58 (58) | 58 | 0 |
| julia | 298 / 298 | 138 | 24 | 6 | 49 | 52 | 10 | 38 | 52 (52) | 52 | 0 |
| king_on_pantera_leoman | 568 / 568 | 152 | 32 | 6 | 169 | 176 | 33 | 44 | 176 (176) | 176 | 0 |
| kuma | 246 / 246 | 131 | 28 | 6 | 35 | 37 | 10 | 19 | 37 (37) | 37 | 0 |
| law | 346 / 346 | 153 | 23 | 6 | 57 | 59 | 10 | 58 | 59 (59) | 59 | 0 |
| lei | 381 / 381 | 179 | 36 | 6 | 56 | 59 | 10 | 55 | 59 (59) | 59 | 0 |
| nina | 418 / 418 | 158 | 28 | 6 | 97 | 101 | 17 | 40 | 101 (101) | 101 | 0 |
| ogre | 268 / 268 | 152 | 33 | 6 | 34 | 36 | 9 | 18 | 36 (36) | 36 | 0 |
| paul | 308 / 308 | 160 | 24 | 6 | 53 | 58 | 10 | 17 | 58 (58) | 58 | 0 |
| xiaoyu | 386 / 386 | 193 | 37 | 6 | 55 | 56 | 10 | 55 | 56 (56) | 56 | 0 |
| yoshimitsu | 264 / 264 | 141 | 25 | 6 | 34 | 31 | 4 | 37 | 31 (31) | 31 | 0 |

**Total: 7368 / 7368 clips baked, 0 missing, 1331 throws with their thrower clip; packs 56.9 MB.**

Notes:

- **Forest Law.** His six standard-throw rows (`0xaeb`–`0xaf1`, from attempt rows 108 and 109) are empty in
  divmot20. The game fills them from the opponent's bank, so he throws with the opponent's throw. These are
  listed with `defined: false` and a note.
- **Bosconovitch.** Eleven reversal moves (`0x3ad`–`0x3d7`) have `+0x32 = 0`. ThrowVictimStart then reads record
  0, whose first word is slot 0, the round-start stance. These carry a `victim_note`; there is no victim move to
  bake.
- **Rows the WH movesets use.** 4,221 of the 4,685 rows in the `rows.pack.json` files carry a reaction value.
  The rest are not attacks.

## Verification

These checks run in `tools/anim/t3_reaction_tables.py`, which writes nothing if any of them fails. The results are
stored in `reactions.json` `verification`.

- PASS: g_airKinds 0x8001A630 equals combat.md's air-kind table ([[440, 3414], [550, 3425], [204, 3426], [436, 3427], [436, 3428], [1357, 3415]])
- PASS: 168 of 633 records have a non-zero +0x20 angle (combat.md) (168)
- PASS: highest push-table index the records use is 700 (remake_import PUSH_ENTRIES = 700 + 10) (700)
- PASS: record 0 is all zero
- PASS: throw-victim indexes stay inside the 397 entries (remake_import THROW_VICTIM_COUNT) (max 396)
- PASS: close-reaction indexes stay inside the 58 entries (max 57)
- PASS: fight_sim._reaction_from (research port) reads the same record / victim entry for every bank row (5143 rows, 0 mismatches)
- PASS: +0x32 / +0x34 / attack class equal teardown/tekken3/movesets/moveset_*.json (moveset_extract.py) (8910 rows, 0 mismatches)
- PASS: every reaction slot named by the records of a bank's moves (own + divmot99 rows) is defined by that bank (0 undefined)

Further checks:

- **Throw geometry.** The throw pairs in the [shared-frame proof](#shared-root-frame-transitions-0x21--0x22)
  land face to face, back to front and side on. These positions come from the decoded root channels alone.
- **Node test.** `node --test test/t3-reactions.test.mjs` runs 9 tests and all 9 pass. It checks that:
  - every pack has 22 bones, and every quaternion is finite with norm 1 ± 0.01;
  - every planned slot is baked or listed missing;
  - every record slot of every attacker resolves on all 22 defenders;
  - the air kinds and the KO collapse resolve in every bank;
  - every throw has its thrower clip and a victim clip against every opponent bank, including the throws
    borrowed from the opponent;
  - every break has its escape clip and the escape's victim move;
  - divmot99 attack rows are covered, and every default continuation is resolvable.

## Known limits

- **Lent clips.** A victim or stagger clip taken from the opponent's bank is decoded on the opponent's body and
  played on the defender's skeleton. Rotations transfer by bone name (identity-rest canonical rigs), and
  proportions are the opponent's. The game does the same with its own data: the motion is shared and the skeleton
  differs.
- **Xiaoyu's skeleton.** `game/assets/anim/t3/xiaoyu/skeleton.json` rest positions differ by up to 0.60 m from
  both Xiaoyu GLBs, the one `rows.pack.json` was baked on and the one `skeleton.json` names. This is a
  pre-existing mismatch. Reactions use the `rows.pack.json` recipe, like her rows.
- **Bosconovitch.** His `rows.pack.json` predates the BODY-EXTRACTION body (`models/bosconovitch/bosconovitch.kmd`
  and `t3_bosconovitch.glb`). His reactions use that same recipe, so the two packs match.
- **Not wired.** Wiring into `fighter.js` is the lead's job. Push-back, LaunchTrajectory physics and knock-down
  mashing are data here (tables plus formulas), not code.
