# TKMovesets2 — the solved Tekken 7 decode, wired into Western Heart

This directory pulls the community's solved Tekken 7 moveset decode into
Western Heart's animation pipeline, so future pulls use the solved decode —
not raw scrambled files, and not the graph bank alone.

## The solved source

**TKMovesets2** — https://github.com/Kiloutre/TKMovesets — v1.1, GPL-3.0.
Pinned commit `8e6bfc1` (pushed 2026-11-18). It extracts whole per-character
movesets for Tekken 7 (and T8 / TTT2 / TRev / T6 / T5) from live game memory
or straight from the game files, into `.tkmvst` files. A `.tkmvst` file is
the known-good decode: the game itself has already run its decryptor and
byteswap before the data is captured, so the file holds little-endian move
records, MOTA archives, and animation blobs with the documented layout.

There is no Tekken 7 decomp or recomp (verified 2026-11-20, see
CONFLICT-RESOLUTION.md). TKMovesets2 is the solved source for T7/T8.

## What is vendored here (and what is not)

Vendored verbatim, with hashes in VENDORED.md:

- `docs/file-formats.md` — the `.tkmvst` container: TKM2 header, compression
  codecs, the T7 8-block payload, CRC coverage.
- `docs/t7-structures.md` — every T7 record: MovesetInfo, the 19 tables,
  Move (0xB0), Cancel (0x28), HitCondition (0x18), Reactions (0x70), MOTA
  archives, terminators, the three representations (memory / file / disk).
- `docs/t7-behaviour.md` — runtime behaviour (what the records do in-game).
- `editor_t7_properties.txt` — Extra Move Property ids → labels.
- `editor_t7_requirements.txt` — requirement condition ids → labels.
- `LICENSE-GPL-3.0.txt` — the upstream licence. All vendored material is
  GPL-3.0; keep the licence file beside it.

NOT vendored: the TKMovesets2 tool itself (Windows, needs Visual Studio +
vcpkg + the Steamworks SDK to build, and the game to run). No binary is
committed. The tool is referenced by pin (commit `8e6bfc1`); fetch it from
https://github.com/Kiloutre/TKMovesets. No decoder was built from scratch.

## The decode path every future pull must follow

1. Extract the character's moveset with TKMovesets2 (memory route, or the
   from-game-files route) → `<character>.tkmvst` (T7: gameId 0).
2. Resolve the throw TRIPLE with `tkmvst_to_wh.py triple` — never pull a
   single clip and call it the throw. A T7 throw is three pieces, all in
   the THROWER's moveset (see CONFLICT-RESOLUTION.md):
   - the thrower's grab — the throw move's own animation;
   - the thrower's throw motion — the throw move's cancel rows on
     throw-hit requirements (3/4/5/6/27) → target move ids;
   - the victim's receiver — the throw move's HitCondition → ReactionList
     → reaction move ids (standing/crouch/left/right/back).
   The throw camera is a fourth, separate piece (Extra Move Property /
   throwCameras table).
3. Map each resolved move to a WH clip with `tkmvst_to_wh.py validate`
   (frames == the move's `anim_len`, 21 bones in skeleton order, unit
   quats). The animation blob itself is decoded by the reference
   implementation — `TAnimUtils::ParseAnimation0x64` /
   `ParseAnimation0xC8`, or WH's game-sampler path
   (`tools/anim/t7_anim64_to_c8.py`, game's own sampler RVA 0x73ea30) —
   never by a hand-rolled re-decode.
4. Record the resolved move ids + clip ids in a `*-throw-triple.json`
   beside the clips (see `king-throw-triple.json`), so the role of every
   clip is traceable to the move/field that produced it.

## Game-gated limit (honest)

Producing a real `.tkmvst` needs Tekken 7 itself (Steam, latest build) —
the extractor reads the running game or its files. This repo does not have
the game, and no public King `.tkmvst` was found anywhere on 2026-11-20
(archive.org live search, TekkenMods, GitHub, web — see
COMPARISON-REPORT.md §5). So the full re-decode of our four T7 throw clips
against a real King `.tkmvst` is NOT done here and is NOT claimed. What IS
done: the format-level verification in COMPARISON-REPORT.md (our clips
parsed against the documented MOTA / `.tkmvst` / skeleton structure, with
numbers), and a `tkmvst_to_wh.py` that is proven against a
spec-conformant synthetic King `.tkmvst` (see `test_tkmvst_to_wh.py`,
29 assertions, all passing). The moment a real King `.tkmvst` exists —
extracted from the game, or supplied publicly — run:

```
python3 tools/anim/tkmovesets2/tkmvst_to_wh.py triple king.tkmvst 1785
python3 tools/anim/tkmovesets2/tkmvst_to_wh.py triple king.tkmvst 1787
python3 tools/anim/tkmovesets2/tkmvst_to_wh.py validate king.tkmvst 1785 \
    game/assets/anim/t7/king/throws/common_709.json
```

and the receiver move id that this report leaves UNKNOWN will be read
straight out of the file (throw move → HitCondition → ReactionList).

## Files

| File | What it is |
|---|---|
| `tkmvst_to_wh.py` | `.tkmvst` parser + throw-triple resolver + WH clip validator + 0x64/0xC8 layout reader |
| `test_tkmvst_to_wh.py` | Synthetic-`.tkmvst` tests (29 assertions, no game, no disk writes) |
| `docs/file-formats.md` | Vendored: `.tkmvst` format spec |
| `docs/t7-structures.md` | Vendored: T7 moveset structures |
| `docs/t7-behaviour.md` | Vendored: T7 runtime behaviour |
| `editor_t7_properties.txt` | Vendored: Extra Move Property labels |
| `editor_t7_requirements.txt` | Vendored: requirement condition labels |
| `LICENSE-GPL-3.0.txt` | Upstream GPL-3.0 licence |
| `VENDORED.md` | Manifest: source, commit, sha256 per vendored file |
| `CONFLICT-RESOLUTION.md` | Thrower-vs-victim conflict, resolved with evidence |
| `COMPARISON-REPORT.md` | Re-decode comparison: our 4 clips vs the solved format |
| `king-throw-triple.json` | King's 1+3 / 2+4 throw triples as resolved data (receiver: unknown) |

## Verification criterion (owner addendum)

A source counts as SOLVED for throws only if it contains BOTH pieces with
correct roles: the thrower's throw motion AND the victim's receiver
animation. TKMovesets2 passes at the moveset level: both pieces live in
the thrower's `.tkmvst` (throw motion via cancel rows, receiver via
Reaction List). This pull-in satisfies the criterion structurally — but the
receiver move id for King's throws is still UNKNOWN in our data (see
`king-throw-triple.json`): our graph extraction dropped the
hit-condition/reaction tables, and no real King `.tkmvst` exists yet to
read it from. That gap is named, not papered over.
