Toukon Retsuden (TR1) English — Partial Patch
=============================================
Shin Nihon Pro Wrestling - Toukon Retsuden (PS1, Yuke's, 1995, SLPS-00084).

PATCHED (Track 1 only, no audio tracks):
- tr1-en-final-track1.bin (209,861,904 B, SHA-1 17050fec804b94661892ae35cece7ae167d1f952)
  English wrestler names (16) + "The End" screen. QA-passed: boots to main
  menu, demo match plays, EN names in RAM. Menus + banners still Japanese
  (documented blockers — see western-heart muse/toukon-english WORKLOG.md).

ORIGINAL (Track 1 only, no audio tracks):
- tr1-jp-track1.bin (209,861,904 B) — original JP Track 1.
  Full original zip SHA-1: a63d2bf861cb5b3f60fc54df7e50a116b8ee8260
  (archive.org 2024-sony-playstation-jap-hearto-1g1r-collection).

AUDIO TRACKS: NOT included (deleted locally for quota). Re-download the
TR1 zip from archive.org to get Tracks 2-7 (CD audio), then build the full
disc + CHD with chdman (installed on this VM).

CUE: testFINAL.cue references tr1-en-final-track1.bin + dummy silent audio.
Replace dummy audio with real tracks for a proper CHD.

Tools + docs: western-heart branch muse/toukon-english
(teardown/toukon-retsuden/), commit 68ed4654.
