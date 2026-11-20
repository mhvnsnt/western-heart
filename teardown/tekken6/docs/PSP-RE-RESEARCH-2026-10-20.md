# PSP reverse-engineering ecosystem research — Tekken 6 PSP (2026-10-20)

Scope: what the industry-standard PSP RE ecosystem offers for finishing
the Tekken 6 PSP teardown (custom DEFLATE in DATA401, GMO models), what
was used, and what is documented-but-not-pulled. Companion to
`teardown/tekken6/tools/ROUND2-DECRYPT-GMO-STATUS.md`.

## Findings

1. **No published format work exists for this data.** Searches across
   GitHub, format wikis and RE community sources found no DATA401, no
   "GZIP"-container, and no Namco PSP pack documentation, and no
   quickBMS script for Tekken 6 PSP (quickBMS by Luigi Auriemma is
   GPL-2.0; its Namco scripts cover other titles/formats). The lane's
   own rounds 1–11 + round 2 are the state of the art for this format.

2. **PPSSPP is the live-observation route.** The team already runs
   PPSSPP (`tools/ppsspp/PPSSPP.AppImage`, hrydgard/ppsspp). Its
   debugger + GE debugger can breakpoint the game's inflate at EBOOT
   0x8b55bf0 while a container loads and log (symbol, length, distance)
   triples — the ground truth needed for the one remaining formula
   (ROUND2 doc §4). Static-only work hit its limit because the game's
   length composition lives behind an Allegrex BITREV the decompiler
   cannot lift. PPSSPP's own license is GPL (per its COPYING file;
   the GitHub API reports NOASSERTION, so cite the file, not the API).

3. **Ghidra's PSP/Allegrex gap is real.** Stock Ghidra 12.1.4 ships
   MIPS variants (default/micro/R6/16e) but no Allegrex Sleigh; the
   bundled `ghidra_psx_ldr` extension targets PS1 (R3000), and the
   EmotionEngine extension targets PS2. Practical consequences, all
   hit this round: the ELF loader rejects the PSP EBOOT's e_flags arch
   bits (workaround: patched copy with the arch nibble zeroed, or raw
   imports); the decompiler truncates control flow at BITREV/CLZ-class
   Allegrex instructions; targeted region imports + seeded
   disassembly are the reliable pattern on a small VM.

4. **PSP tooling staples**: prxtool and pspsdk document PRX structure
   and the firmware library model. Relevant conclusion for this game:
   the two PRX modules on the Tekken 6 disc are Sony's PSMF player
   (libpsmfplayer.prx, psmf.prx) — there is no Namco pack PRX on disc,
   and firmware `sceDeflt` is stock zlib, which does NOT match this
   data (custom code-length order + renumbered repeat symbols), so the
   decoder is the game's own EBOOT code (proven by decompilation).

5. **GMO ecosystem**: PiosGmoLibrary (Pionome) is the authoritative
   GMO chunk parser (Model/Bone/Part/Arrays/Mesh/Material/Motion);
   PSP-GMO-Loader is the reference render-path implementation
   (bind-pose math: game bind pose = raw verts). Neither repo carries
   a license file → both are **documented, not re-pulled**; the copies
   already in release `tekken6-recon-20261016` (`work/tooling/`) are
   the working set. ShrineFox's P4GModelConverter covers GMO↔MDS for
   Persona titles; also no license file → documented, not pulled.
   puyotools (GIM texture decode) is already in the same tooling tree.

6. **Ecosystem neighbor**: tkdr-recomp (Tekken Dark Resurrection PSP
   recompilation) shows the community's PSP-Tekken RE direction
   (static recomp of the earlier PSP title). No shared format data
   with Tekken 6's DATA401; reference only.

## What this changed in practice

- Killed the "find the decoder PRX" line of investigation (disc
  inventory is complete: 2 PSMF modules only).
- Killed the preset-dictionary theories (the EBOOT wrapper rejects
  FDICT — decompiled).
- The remaining formula work is routed to PPSSPP live tracing, the
  only route that observes the length composition directly.
