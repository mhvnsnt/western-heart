# TTT2-PC Static-Recompilation Port — Teardown Assessment (2026-10-22)

**Project:** https://github.com/shihabal3amri/tekken-tag-tournament-2-pc
(NEW — created 2026-10-12, 122 stars, 6 releases, MIT-built on XenonRecomp)
**Why it matters:** a *static recompilation* of the TTT2 Xbox 360 executable.
The authors reverse-engineered the X360 binary deeply enough to translate it to
native Windows code — and their **installer builds the game's art/sound/stages/
movies from the user's disc image + Title Update 3**. That installer pipeline is,
in effect, a documented, tested **TTT2 X360 asset extractor**.

## What it gives the teardown (no RE from scratch)

| Port component | Teardown use |
|---|---|
| `tools/` — installer asset pipeline (disc → PC game files) | **Direct model:** how TTT2's PAC/PACH archives, texture archives (BPE-compressed `0A`-style blobs), XMA audio, and stage files unpack. Ports the "STFS extraction" blocker into a solved problem — read their code instead of reversing the formats blind. |
| `re/recomp/` — recompiled function set | Symbol/function names the authors recovered (loaders, decompressors). Cross-reference with our Ghidra targets. |
| TU3 handling (`TU_174Q22P_0000008000000.00000000000O2`) | Title-update container format (STFS) parsing, already working. |
| FFmpeg (LGPL) XMA audio path | Audio decode solved — matches our vgmstream gap (`tools/re/cli/README.md`). |
| libmspack (LGPL) LZX | Decompression primitive TTT2 archives use. |
| tiny-AES-c | If any TTT2 blob is AES, the port shows where. |

## Unblock-path change for TTT2 (was: "download 13.3GB + STFS extract", ~15%)

1. **Study the installer's asset build** (`How the installer works` doc in their repo):
   map each step to a TTT2 format → write our extractor stage to match
   (grounded in their code, not byte-guessing — satisfies NO-HAND-TOOLING).
2. **Cross-check their `re/recomp` function list** against `tools/re/QUEUE.md` TTT2
   targets before spending Ghidra time — skip anything they already reversed.
3. **XMA audio:** adopt their FFmpeg-based decode path for the TTT2 audio lane
   (and note it for the vgmstream build decision).
4. Their installer *validates* the disc image (checksum per version) — reuse those
   hashes to verify our 26 release chunks reassemble to a good dump.

## Caveats (honest)

- Windows-only port; the useful parts for us are the **format knowledge** in
  `tools/` + `re/recomp/`, not the binaries.
- Ships no game data — we still need our own disc image (the 26 chunks on release).
- License: built with XenonRecomp (MIT); the port repo itself is a fan project —
  read code, don't copy blobs; reimplement extractors in our pipeline.
- Not yet pulled into `tools/open-source/` — that pull-in (source-only, submodules
  excluded per the 2026-10-19 convention) is the next step for the TTT2 lane.

## Recommendation

Promote TTT2 from "QUEUED — extract first" to **active RE lane**: the format work
is now a reading task, not a reversing task. Estimated effect: TTT2 15% → 60%+
(models/stages/audio flowing) once the installer-pipeline mapping lands.
