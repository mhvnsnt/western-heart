# Toukon Retsuden TR1 - game files (VM sweep Lane B, 2026-11-21)

English-patched PS1 disc files, moved off the Oracle VM disk. Tools, WORKLOG
and CUE sheets are already on this branch under `teardown/toukon-retsuden/`.

- `tr1-fullen.chd` (372,039,105 B) - the playable CHD (patched Track 1 +
  dummy silent audio tracks). SHA-256 in MANIFEST.tsv.
- `tr1-en-final-track1.bin` (209,861,904 B) - patched Track 1, final.
  SHA-1 `17050fec804b94661892ae35cece7ae167d1f952`.
- `tr1-fullen-track1.bin` (209,861,904 B) - patched Track 1, full-English build.
- `tr1-jp-track1.bin` (209,861,904 B) - original Japanese Track 1.
  SHA-1 `284fd4f27d08556326a163f177923f92202e4cc4`.
- `dummy-audio/` - silent placeholder audio tracks (track2-7).
- `qa/` - Mednafen/PCSX QA screenshots from the translation lane.
- `test-jp.cue`, `toukon-README.txt` - cue + notes from the lane.

Big files are split into <=100 MB pieces; reassemble with
`cat <file>.part* > <file>` and verify against MANIFEST.tsv (SHA-256).
