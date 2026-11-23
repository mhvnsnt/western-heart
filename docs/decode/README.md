# docs/decode — fixed vs scrambled

What "scrambled" means here: the fighting-game data Western Heart pulls in
(movesets, animation clips, reaction lists) does not arrive in playable form.
Each game hides it differently — lossy compression, encryption, obfuscation,
bone remaps, swapped clip roles, or a container whose file table lives
somewhere else. A file is **scrambled** until a solved decode turns it into
verified, playable data; a file is **fixed** when a PR lands that decode (or a
correction of a bad bake of it) with before/after proof.

This directory records, per game and per fighter/file, what the scramble was,
how it was solved, and what is still open. It is the record the scramble
sweep works from — not a copy of the sweep's research workdir, and not a
replacement for `docs/movesets/` (moveset method docs), `docs/research/`
(research notes), or `docs/anim/` (animation pipeline docs). Where a fix
depends on one of those, it links to it.

## How to read these docs

- `scramble-overview.md` — the mechanism reference: how each game scrambles,
  in one place, with evidence links.
- `tools.md` — every decoder / bone map / community tool used, with source,
  version, and licence logged honestly.
- `STATUS.md` — the living status table. Every fix PR adds or updates one row
  here, plus its own per-file doc. This is the only file every fix PR touches
  besides its own doc.
- `<game>/scramble.md` — that game's scramble mechanism + how it was solved.
- `<game>/decode-steps.md` — the step-by-step decode for that game
  (tool, command, bone map), so the decode is reproducible.
- `<game>/<fighter-or-file>/fixed-vs-scrambled.md` — one per fighter/file
  fixed, following the 8-section template (what was fixed, how scrambled,
  decoding steps, cracking steps, decomp/recomp steps, before/after proof,
  sources, gaps). Write "none" with a reason rather than deleting a section.

## Status by game

| Game | Scramble | Decode status | First fix / doc |
|---|---|---|---|
| Tekken 3 | Lossy animator-controlled animation compression; BNS container, file table in EXE | **Solved in-repo** (divmot banks + bit-exact AnimDecodePose port) | King on Pantera re-bake — `tekken3/king-pantera/fixed-vs-scrambled.md` |
| Tekken 5 / DR | Retail PS2 obfuscated/encrypted; arcade not | Solved via arcade + emulator-memory routes; retail-PS2 method unknown | — |
| Tekken Tag 2 | No on-disk scramble; moveset only in console/emulator memory | Solved (memory route + static recompilation); motbin motion not decoded | — |
| Tekken 6 | PSP v3 decode family (see `docs/movesets/`) | See `tekken6/` when seeded | — |
| Tekken 7 | UE4 .pak animation cipher not publicly broken; clip roles swapped (thrower/victim) | Solved via the memory route; on-disk cipher unsolved; King throw roles under hunt | — |
| Tekken 8 | UE5 IoStore + `tkdata.bin` | Solved for Steam build 26155785; not solved in general | — |
| Virtua Fighter 5 | Motion not decoded | **Unsolved** (PR #713 open) | — |

Details and evidence: `scramble-overview.md`. Per-game mechanism + solved
steps: `<game>/scramble.md` and `<game>/decode-steps.md`.

## Rules

- **Docs land in the SAME PR as each fix.** A fix PR that changes a
  scrambled file without its `fixed-vs-scrambled.md` (and its `STATUS.md`
  row) is incomplete.
- **No hand-tooled workarounds.** If a fix used a hand-made stand-in because
  no solved decode exists, the doc says so in §8 as a gap, and the file stays
  flagged in `STATUS.md` as unsolved.
- **Licence never gates use** (standing law) — but licence and source are
  still logged honestly next to each item in `tools.md` and in each doc's §7.
- **Archive.org is checked FIRST** for any game acquisition (standing law);
  each doc's §7 records the check (date + result).
- Sequencing note: the coordination proposal (`lane-c-coordination/DOCS-SKELETON.md`)
  said the first docs PR should ride with the first T7 fix (King throws).
  This lane lands the skeleton first instead, with the King T3 re-bake,
  because the T7 throw fix is game-gated (throw hunt still running) while
  the T3 re-bake is runnable today. The T7 `king-throws/` doc still lands
  with the T7 fix when it comes.
