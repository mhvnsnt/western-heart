# Scramble overview — how each game hides its data

Summary of the scramble-research findings (sweep research workdir,
`lane-b-mechanisms/MECHANISMS.md`, fetched live 2026-11-20), plus the
corrections this sweep's fix lanes have verified since. This is the mechanism
reference; per-game detail lives in `<game>/scramble.md`.

## The one-sentence truth

No game in the sweep encrypts everything. Each game hides its data in a
different way, and each way has a different solved (or unsolved) route in.
There is no single "unscramble" step — the work is per game, per file.

## Tekken 3 (PS1, 1997 / System 12 arcade)

- **Lossy animation compression, built for the PS1 port.** The arcade
  animation data was so large two fighters' data could not load at once
  (King alone would not fit); Namco built an animation loss-compression tool
  letting animators control the compression rate per animation. T3 animations
  on disc are **compressed with per-animation quality chosen by the animator**
  — data is thrown away by design, not encrypted. Any decode is an
  approximation of the arcade original by construction.
- **Container: `TEKKEN3.BNS` (BinStream).** The file table is not in the
  container — it is read from the **LBA table in the game executable**.
- No evidence of encryption or bone-index permutation in T3.
- **Solved in-repo:** divmot motion banks + a bit-exact port of the game's
  `AnimDecodePose` (`teardown/tekken3/tools/local/usa_motion.py`, literal
  port of n0madic's `motion.py` spline machinery) + KMD part assembly
  (`pose_assemble.py`) + the WH bake tools (`lab/tools/t3_motion_bake.py`
  and `tools/anim/t3_*_bake.py`). See `tekken3/decode-steps.md`.
- Correction to the research note: `MECHANISMS.md` (2026-11-20) recorded
  "a documented T3 moveset/animation-clip decode was not found". That was
  true of *published* docs; the repo's own teardown + bake pipeline is the
  solved decode, verified end to end by the King re-bake lane (SHA-verified
  sources, direct-tool references, slot-path audit of all 856 motion units).
  The moveset-level record (move rows, reaction lists) comes from the repo's
  own teardown (`teardown/tekken3/movesets/`), not from a published T3
  moveset doc.

## Tekken 5 / Tekken 5: Dark Resurrection

- **Retail PS2 build is obfuscated/encrypted; arcade is not.** The
  TekkenMods tutorial "Extracting Vanilla Tekken 5 Assets for modding"
  (citing Phantom D.Z): the retail PS2 version has stages and characters
  obfuscated; only "The Devil Within" data is extractable. The tutorial uses
  Tekken 5.1 arcade for that reason. The obfuscation *method* (cipher, key,
  transform) is not documented in the sources fetched — only its effect.
- Status: solved via arcade + emulator-memory routes; retail-PS2 method
  unknown.

## Tekken Tag Tournament 2

- **No on-disk scramble to break — the barrier is that it is a console
  game.** No PC .pak files; the moveset only exists decoded in
  console/emulator memory. The moveset lineage is the same as T7's
  (same table order; MovesetInfo 0x20C bytes, table at 0x140, MOTA list at
  0x1D8; move stride 0x70, Cancel 0x20, Reactions 0x50).
- Status: solved (memory route + static recompilation). MOTA offsets are
  present but motion is not decoded — recorded as unsolved until a community
  solution is found; the sweep does not build a decoder from scratch
  silently.

## Tekken 6

- PSP v3 decode family — see `docs/movesets/` for the conversion method.
  Per-game `tekken6/scramble.md` is seeded by the first T6 fix lane.

## Tekken 7 (PC, UE4.14)

- **On-disk animation cipher not publicly broken.** The moveset is solved
  via the memory route (live-game memory reads); the on-disk cipher is a
  separate, unsolved problem.
- **Clip roles are swapped.** The thrower/victim assignment of paired clips
  is the live scramble for King: the hunt lane is deciding which of the 10
  King throw clips is the thrower's throw and which is the victim's receiver
  (common_709, rotsm_534, rotsm_574, rotsm_578 and others). See
  `MECHANISMS.md` §7 (thrower vs victim) and the T7 `king-throws/` doc when
  it lands. Do not touch the 10 King throw clips until the hunt decides.
- Status: solved via the memory route; on-disk cipher unsolved.

## Tekken 8 (PC, UE5)

- **UE5 IoStore + `tkdata.bin`.** Movesets (plus character and customisation
  lists) live in `TEKKEN 8\Polaris\Content\Binary\pak\tkdata.bin` — a single
  archive that "cannot be modified through regular Unreal Engine modding".
  Extracting/repackaging the whole file is "very heavy and unstable"; the
  loader injects only modified files at runtime (Ultimate ASI Loader).
- Status: solved for Steam build 26155785; not solved in general.

## Virtua Fighter 5

- Motion not decoded. Status: **unsolved** (PR #713 open). Its
  `virtua-fighter-5/scramble.md` will record the gap honestly until a solved
  decode exists.

## What remains unknown (do not fill in by guessing)

- T5 retail-PS2 obfuscation method (cipher, key, transform).
- T7 on-disk animation cipher.
- T8 beyond Steam build 26155785.
- VF5 motion decode (PR #713).
- TTT2 motbin motion (MOTA offsets present, motion not decoded).
- T3: the exact per-clip animation encoding inside BNS at the *arcade*
  level is lossy by design (animator-controlled compression) — the PS1
  decode is solved; the arcade original is not recoverable from the disc.
