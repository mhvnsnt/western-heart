Toukon Retsuden (TR1) English — FULL English version (v6, 2026-11-20)
=====================================================================
Shin Nihon Pro Wrestling - Toukon Retsuden (PS1, Yuke's, 1995, SLPS-00084).
"First English version of the Japanese NJPW Toukon Retsuden, with the real
NJPW roster" — no EN version of TR1 ever existed (the US release, Power Move
Pro Wrestling, swapped the roster for 12 fictional wrestlers).

FULL ENGLISH (default — everything on screen in English):
- tr1-fullen.chd (372,039,105 B, SHA-1 1b8217e39f1104ff40d9b9546477fbd7c91d0e1e)
  Full disc, 7 tracks, 58:07 — EN Track 1 + REAL CD audio tracks 2-7.
  chdman-verify passed (raw + overall SHA-1). Use this on the console.
- tr1-fullen-track1.bin (209,861,904 B, SHA-1 07f08608fadab90b7998ab740e36d0f49a8390f2)
  EN Track 1 alone (CUE: test-fullen.cue, dummy silent audio tracks).
  Verified in DuckStation: title, main menu, game menu, options (all rows
  clean), char select (12 EN names), VS screen, match HUD, demo HUD,
  attract demo, RESULTS (GAUNTLET / IWGP CHAMPS / TOURNAMENT), IWGP CHAMPS
  screen (#17, MUTOH W HASHIMOTO, 21m13s), SAVE MATCH?, SAVING, DATA SAVED,
  BEST BOUTS. Menus use a rebuilt EN texture atlas (glyphs harvested from
  the US version); names from the EN name sheet + EXE; staff lines + The
  End from the US version. Ring apron + event poster stay Japanese
  (NJPW branding, as in the US release). RING row shows 1/2/3/4 (as in
  the US release — full "NJPW2"/"NJPW3" words split on the options screen).

HYBRID (setting/option — EN names + The End, rest Japanese):
- tr1-en-final-track1.bin (209,861,904 B, SHA-1 17050fec804b94661892ae35cece7ae167d1f952)
  CUE: testFINAL.cue.

ORIGINAL:
- tr1-jp-track1.bin (209,861,904 B, SHA-1 284fd4f27d08556326a163f177923f92202e4cc4)
  Full original zip SHA-1: a63d2bf861cb5b3f60fc54df7e50a116b8ee8260
  (archive.org 2024-sony-playstation-jap-hearto-1g1r-collection, file under
  "2024-sony-playstation-jap-hearto-1g1r-collection/Sony - Playstation - JAP/").

NOTE: Mednafen HANGS on the full-EN build (any PAC_WRES slot 202/203 change
hangs it — same for the genuine US slot 202 blob; mechanism unknown). The
build is verified in DuckStation. PCSX ReARMed (console core) NOT yet tested
— test the CHD there before flipping the console card to playable.

Tools + docs: local ~/workspace/toukon-english/ (WORKLOG.md); western-heart
branch muse/toukon-english (teardown/toukon-retsuden/).
