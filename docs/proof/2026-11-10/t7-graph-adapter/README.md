# Pantera: King T7 full-graph fighter adapter, DEVELOPMENT integration (2026-11-10)

Status: **opt-in development integration**. It is off by default; the existing Pantera path is unchanged when the flag is off.
Turn it on with `?t7graph=1`, or with `localStorage['wh.t7graph']='1'`, or with `globalThis.WH_T7GRAPH=true`.
A yellow on-screen label shows the current source move and frame, the fire count, and the count of rows skipped for unknown conditions.

This is **not** 100%. It has **no** touchscreen proof and **no** visual, rig or model proof (that proof stays UNKNOWN).
Everything here is Node-tested only.

## What is wired (real input path)

`InputManager` (on-screen limb buttons now track hold/release in `held`; the stick reads 8-way) → `game.js` player branch → `feedT7GraphInput` (`game/js/t7-graph-input.js`).
That step handles:
- direction relative to facing, using the same body as `_tekkenDir` (a test checks for drift);
- press edges and chords;
- held buttons;
- the double-tap dash latch.

→ `Fighter.t7gFeed` → `T7GraphDriver.step` (`game/js/t7-graph-driver.js`) → `stepCancel` (`game/js/t7graph.js`) walks the source cancel list in order.

→ the source move's own clip frame is posed through the T7 retarget (`t7GraphRetarget`), with:
- the source root forward travel per frame;
- the source damage, active frames and hit level as the hitbox;
- WH guard while the source move does 0 damage.

The tick model is one source frame per 60 Hz tick. Frame f plays, then the cancels are evaluated at f. A fire plays the target's frame 1 on the next tick. At the end of the clip with no fire, the move goes to the source `transition`.

## Decoding evidence (from the source, not assumed)

- **Cancel command u64.** The low 32 bits are the direction mask. The high 32 bits are `0xMMNNHHPP`, per the TekkenMods Input Extradata doc:
  - PP = pressed;
  - HH>>1 = held;
  - NN>>2 = not held;
  - MM: 0x40 = at least, 0x20 = any one of, 0x80 = direction only.

  In King's data, MM is set exactly when PP is set. HH appears on 31 rows and NN on 6, only on button-less rows.
  Graph command modes: 0x00: 7,600, 0x20: 627, 0x40: 30,542.
  v1 misread the 0x20 rows as "held" and lost HH/NN. Fixed here (`wh-t7-graph/2`).
- **Cancel frame (`starting_frame`).** Input is accepted inside [start, end] (32767 = the whole move) and applied at `starting_frame`; earlier input is buffered.
  `starting_frame` 0 with an input means at the animation end.
  Rows whose `starting_frame` is beyond the clip are **not** guessed; they count as `timing`.
- **Move length.** motbin `anim_max_len` (+0x68) is 0 for all 2,787 King moves on disk, so the length is the clip frame count.
- **Hit level.** Decoded from `hitlevel & 0xFFF` with the existing attack-word layout. It agrees with the T7 frame data on **48/48** joinable moves.pack moves (last hit for strings).
  Levels used for hitboxes: h, m, l. Throw-class, 'u' and special-mid ('s', 10 reachable damaging moves, not checked against the join) produce **no** hitbox.
- **Root motion.** The raw T7 root channel z per frame (mm/1000), computed with the existing decoder. Lateral is 0 because its sign is unproven.
- **Reuse.** The cached bake clips are byte-identical in rotations and root channel to the shipped moves.pack clips (≥45 checked in a test). Nothing was rebaked.

## Runtime policies that are WH choices (unproven, labelled)

- P1: a button-less state row does not take a press frame.
- P2: a sequence matches as an ordered subsequence of input events within the window.
- P3: the first accepted pending cancel is kept until its frame.
- Dash-latch timing for 0x8001/0x8002.
- Facing re-snaps only during the source stance move.
- Posture during graph moves is always standing (move vulnerability flags are not decoded).
- No blending between moves.

## Asset pack (`game/assets/anim/t7/king/graph-clips/`)

- 772 unique clips: 10 deterministic shards (`wh-t7-graph-clips/1`, shard bytes ≤ 6,000,000).
  - Total 57,046,485 B; max shard 5,991,270 B; about 18.3 MB gzip.
  - `index.json` (39,690 B) carries the graph sha256 and the sha256 of each shard.
- Limits checked:
  - Cloudflare Pages: 25 MiB per file, 20,000 files.
  - jsDelivr: 20 MB per file.
  - A single 56 MB file would have been rejected by both.
- Cloudflare: `game/` is a deploy root, so every shard is in the closure.
- GitHub Pages: there is no headroom for 57 MB, so the shards are not added. The loader falls back to jsDelivr after a page 404.
- `graph.json`: 3,140,664 B. `graph.commands.json`: about 6.7 MB.

## Reachable vs playable vs tested

- Source reachability (from the stance): 1,196 moves.
- Command rows on reachable moves: 37,419 (`graph.commands.json`, generated from the graph by `tools/anim/t7_graph_commands.mjs`).

| Status | Rows | Meaning |
|---|---|---|
| evaluable | 7,775 | every condition is known and true in neutral |
| unknown | 28,247 | ≥1 condition unknown; skipped at runtime, never assumed true |
| known-false | 1,039 | |
| timing | 151 | cancel frame beyond the clip |
| special | 134 | 0x8003/0x8004 (sidestep targets), unproven |
| seq-mode | 73 | sequences with mode-0 button inputs (86 sequences), unproven |

- **Tested through the real fighter input path:**
  - all **66** evaluable stance press commands (same-frame stick + press);
  - jab (frame 1 → active frame 10 only → AUTO at 27 → stance);
  - the buffered 1,2 string;
  - n+3+4 fstep held vs released;
  - the dash latch → run at frame 12 (and no run on early release);
  - f+3 never resolving to the run kick;
  - a 400-step mixed replay where every fire had only known-true conditions;
  - held d/f → crouch transition after unknown rows (flagged `precedenceUnknown`).
- Negative tests: unknown conditions 72, 35 and 124 return null; mode-0 sequences return null; the flag is opt-in.

## Blockers (counts from the source)

Top unknown conditions by row count (a row can have several):

| Condition | Rows | Label |
|---|---|---|
| 217 | 10,876 | Player character ID; needs the T7 character-ID table |
| 609 | 10,607 | Has item |
| 225 | 7,775 | Character Controller |
| 72 / 73 | 3,615 / 461 | Backturned / Not Backturned (needs WH backturn state) |
| 554 | 3,456 | unlabelled |
| 81 / 80 | 1,347 / 1,341 | unlabelled |
| 254 | 640 | unlabelled |
| 126 | 536 | Opponent downed |
| 35 / 36 | | distance, needs T7 distance units |

- 185 distinct unknown conditions; 106 of them are unlabelled in the community list.
- Throws: the throw/throw_extras tables are not decoded, so throw moves play their clip without a grab.
- Defender reactions: King's reaction lists are not traversed; the WH engine handles them.
- Not done: lateral root sign, posture, and blending.

## Tests

- `test/t7-graph-adapter-pantera.test.mjs`: 14/14.
- `test/t7-graph-king.test.mjs`: 10/10.
- `test/input-timing.test.mjs`: 13/13.
- The local unit failure set is identical to the base checkout (sparse checkout, missing files). CI is authoritative.

## Provenance

Sources are in the private reverse-engineering repo checkout at `/workspace/pantera-t7-sources` (not in this repo): the King motbin, the anim cache, and the root-channel cache (`graph-bake-cache/root/`, 772 files).
Generators:
- `tools/anim/t7_graph_import.py`
- `tools/anim/t7_graph_pack.py`
- `tools/anim/t7_graph_commands.mjs`
