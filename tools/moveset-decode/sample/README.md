# sample/ — validation fixture (SPEC-BUILT, not a game extraction)

**Nothing in this folder came out of a game.** The character
("ValidationVera", characterId 999) and the moves (`VAL_jab`,
`VAL_elbow_smash`, `VAL_launcher_upper`) are fictional, invented to
exercise the decoder.

## Why there is no real sample

A genuine hunt was run on 2026-10-20 before building this fixture:

* `find ~/workspace -iname "*.tkmvst" -o -iname "*.tkanim"` → **0 files**
* `find ~/workspace -type d -name "extracted_chars"` (the TKMovesets
  extraction directory, `MOVESET_DIRECTORY` in `Utils/constants.h`) → **0**
* Magic-byte scan for `TKM2` at offset 0 over 4,023 candidate files under
  `~/workspace/game-reverse-engineering/`, `~/workspace/tools/tekken-decrypt/`,
  `~/workspace/wh-lane3-movesets/`, `~/workspace/western-heart-movesets/`
  → **0 hits**
* The vendored TKMovesets tree itself ships no test/example movesets.

This is expected: TKMovesets2 extracts from a *running game's memory* on
Windows — no lane has run it yet, so no `.tkmvst` exists on disk. The raw
Tekken `.bin` files in the teardown folders are on-disc game data in
native layouts, **not** the TKM2 container format, and were not passed
off as samples.

## What the fixture proves instead

`../make_validation_sample.py` builds `spec_validation_sample.tkmvst`
(2,560 bytes) directly from the vendored struct specifications
(`MovesetStructs.h`, `Structs_t7.h`, `Extractor_t7.cpp`), writing fields
at explicit offsets from its own tables — it does not import the decoder.
Decoding it with `../tkm2_decode.py` reproduced **every** checked field
(62/62: header, properties, MovesetInfo strings, all 19 table counts, all
3 moves' names/damage/frame data/hitbox/cancel/transition, hit-condition
damages, requirement signed/float param views). `ground_truth.json` is
the builder's input; `decoded.json` is the decoder's output.

Plausibility of the fixture's decoded values (checked by eye): startup /
first-active frames 10, 13, 27 and active windows 10–12, 13–15, 27–29;
damage 12 / 20 / 35; animation lengths 35 / 41 / 58 frames — all inside
normal Tekken 7 ranges; all names decode as clean ASCII.

Rebuild + re-verify:

```bash
cd tools/moveset-decode
python3 make_validation_sample.py sample/spec_validation_sample.tkmvst sample/ground_truth.json
python3 tkm2_decode.py sample/spec_validation_sample.tkmvst --out sample/decoded.json
```
