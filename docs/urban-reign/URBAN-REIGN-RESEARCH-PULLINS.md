# Urban Reign — research and pull-in log (2026-10-20)

Owner mandate: heavy research on the PS2 reverse-engineering
ecosystem, pull in and wire up the best tools into the repo, note
each license honestly, document-but-don't-pull what licenses forbid.

## Pulled in and used

### chaoticgd/ghidra-emotionengine-reloaded — Ghidra R5900 processor module
- Source: https://github.com/chaoticgd/ghidra-emotionengine-reloaded
- License: Apache-2.0.
- What: Ghidra language/processor module for the Emotion Engine
  (R5900 + VU0/VU1), language ID `r5900:LE:32:default`.
- Where it landed: installed into the shared Ghidra 12.1.4
  Extensions directory on the workstation (release v2.1.38 build
  for Ghidra 12.1.4). NOT vendored into this repo — it is a binary
  Ghidra extension with its own release channel; the repo records
  the version and source here instead.
- What it unlocked: stock Ghidra's MIPS language truncates R5900
  functions (MMI/VU instructions decode wrong), which made the
  kg_human/kg_objdata code paths unreadable. With this module the
  targeted decompilation passes produced the loader findings in
  URBAN-REIGN-SKINNING.md (human update FUN_001e7ea8, animation
  sampler FUN_00292670, track getter FUN_00299130).

## Studied, NOT pulled in (license)

### thiagordsfx/urban-reign-recomp — static recompilation of SLUS-21209
- Source: https://github.com/thiagordsfx/urban-reign-recomp
- License: GPLv3 — studied for facts only; no code vendored into
  this repo (this repo's tooling is original).
- Facts used (all independently re-verified against our own files
  where load-bearing):
  - `recomp/urban_functions.csv` — 8,966-function map used as
    ground truth to navigate the stripped ELF in Ghidra.
  - `src/urban/anim_decoder.cpp` — animation container layout
    (cross-checks the sampler/track-getter findings above).
  - `docs/PROGRESS.md` — VU1 skinning microprogram at VU1 addr
    0x1D98; "bone matrix addressed by the w of the weight" (matches
    the premultiplied-by-weight vertex storage proven from the
    data); bone matrices computed from per-node Euler+position
    (func_101628), i.e. bind matrices are not stored as matrices
    in the files — the fact that pointed the decoder at recovering
    them from the skinning relations; characters confirmed standing
    upright in-game after their MMI permutation fixes.

## Consulted (documentation / references, nothing vendored)

- ps2sdk (https://github.com/ps2dev/ps2sdk, AFL/PS2SDK license) —
  Emotion Engine / VU / DMA background for reading the packet
  formats.
- PCSX2 (https://github.com/PCSX2/pcsx2, GPLv3) — debugger/symbol
  conventions for PS2 ELFs; reference only.
- Ghidra stock MIPS language — evaluated first and found
  insufficient for R5900 (see above); the search for a proper
  processor module is what surfaced EmotionEngine-reloaded.

## Community format research

No published Noesis plugin or format write-up for Urban Reign's
PPK/.vmd character format was found (searches across GitHub and RE
format wikis, 2026-10-20). Namco PS2-era sibling titles use
different containers. The format documentation in
URBAN-REIGN-SKINNING.md is therefore original work from this
teardown, proven against the data and the game's own code.
