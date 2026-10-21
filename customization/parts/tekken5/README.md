# Tekken 5 Parts

Owner order 2026-10-21 (~09:39 CDT): customization parts from the legacy
Tekken games already in teardown — T5 + T6 + TTT2 — become the active parts
program; Tekken 7 acquisition later. This directory is the T5 slice
(gap-closure W7b).

## What's here

- `CATALOG.json` — the Tekken 5 parts catalog in the Creation Suite's
  registry-entry shape (consumer: `packages/creation-suite/src/catalogs.js`,
  same pattern as `customization/parts/tekken7/CATALOG.json`, PR #437).
  It loads and merges today. **`parts` is empty** and `named_gaps` carries
  the extracted-but-unconverted sets and the two hard gaps — see the survey
  for why, with byte-level evidence.
- `T5-CUSTOMIZATION-SURVEY-2026-10-21.md` — the full survey: DATA1
  extraction (1,571-record table, 1,355 files, 0 checksum failures),
  costume-pack anatomy, the complete NUDP census (464), own-eyes render
  verdicts, the skull-mask verdict, the ctype-5 / VIF-0x82 format gap, and
  new TK5DATA0 cipher evidence.
- `catalog.test.mjs` — test against the real runtime module and the real
  registry: catalog loads, merges without disturbing anything, named gaps
  resolve `unresolved` (reported, never silently dropped).
- `proof/` — own-eyes renders of the ACTUAL extracted models (orthographic
  projections of ModelMagic-converted geometry): pack 0240 costume model,
  its low-poly body, a 16-pack contact sheet, and the file-0022 ctype-5
  container's undecoded state is documented in the survey instead (its VIF
  0x82 streams do not convert with held tooling — no frame is faked).

## What's NOT here (named gaps, details in CATALOG.json)

1. **Converted GLB slot parts** — T5's data predates the slot schema: each
   of the 80 costume packs carries ONE whole-costume model + ONE low-poly
   body + textures. No per-slot item meshes exist in the packs (census +
   renders). Parts land at `full_body` granularity when the conversion
   pass (NUDP→OBJ→GLB with TIM2 bound) runs; per-slot claims would be
   invented and are not made.
2. **ctype-5 container models** — 9 containers, 16 small NUDP models in an
   undecoded VIF vertex format (globalFlags 0x82 vs the working 0x91/0x93).
   The last place DATA1 slot-item meshes can hide.
3. **TK5DATA0.BIN** — still encrypted (second cipher layer). DATA1's table
   has 216 empty slots whose content is not in DATA1.
4. **Skull mask** — NOT FOUND in DATA1. The `tekken7:cmn:full_head:skull-mask`
   named gap is untouched; a T5 skull mask is registered here as a survey
   target with verdict `named_gap_not_found_in_surveyed_data`.
