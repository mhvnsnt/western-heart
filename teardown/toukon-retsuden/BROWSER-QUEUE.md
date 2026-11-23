# BROWSER-QUEUE — Toukon Retsuden Full English, PCSX ReARMed live test

## Status: READY — deployed site is staged for the test (2026-11-20 ~14:40 EST)

The live arcade card for Toukon is flipped to PLAYABLE on the deployed site
ONLY (VM `/var/www/arcade/games.json` — provisional, test-only). The repo
branch `muse/wrestling-arcade` still has it as `coming_soon` (blob
`9049f2e8`). The repo change lands ONLY after this browser test passes.

## Test URL

http://132.145.194.139/play.html?game=toukon

Phone-sized viewport if the browser can do it; desktop viewport is acceptable
for the boot test (the site renders a narrow central column).

## What must be confirmed

1. Tap START GAME. First start downloads the 372 MB CHD — allow several
   minutes for the download + core load.
2. Boot: does it reach the Toukon title screen IN ENGLISH? (PCSX ReARMed
   uses HLE BIOS, so it may skip the PlayStation logo.)
3. Main menu in English (GO! / RESULTS / BEST BOUTS / LOAD).
4. Get into a match: VS COMPUTER → character select (12 EN names) → pick
   two wrestlers → match starts. Match HUD in English?
5. Sound present? (CD audio / sound effects.)
6. Controls respond? (Virtual gamepad / keyboard.)
7. Speed: full speed, or slow? Report honestly with FPS if the emulator
   shows it. Context: Tekken 3 runs ~55–60% in this console without
   threads, so sub-full-speed is plausible — report the actual feel.
8. Screenshots at each step: title, main menu, character select, VS screen,
   in-match HUD.

## Pass / fail

- PASS: boots, reaches a playable match, controls + sound work. Speed is
  reported honestly; the flip decision is the parent's/Mars's from the
  result. On PASS, apply the repo change (below).
- FAIL: hang on boot, black screen, error message, crash — report EXACTLY
  what screen/error and at what step. On FAIL, revert the deployed
  games.json (below) and do NOT commit the repo change.

## On PASS — apply the repo change (one GitHub API call)

- File: `arcade/games.json`, repo `mhvnsnt/Bannon`, branch
  `muse/wrestling-arcade`, base blob SHA
  `9049f2e88c0ac0d45db654cd64c075326dc8196a`.
- New content (byte-identical to the deployed file): local
  `~/workspace/toukon-english/work/games.json.new`
  (17,619 B, SHA-256
  `44c295ebd6e89e45d7a42bf88c7e06c4e4b0b8d8555bc32d9a8da8e59cb68602`).
  Only the `toukon` entry changed + `toukon-hybrid` card added.
- Suggested commit message: "Arcade: Toukon Retsuden Full English playable
  (PCSX ReARMed verified)".
- No merges without Mars's visual confirmation (PR #166 stays open).

## On FAIL — revert the deployed flip (one SSH call)

```
ssh -o ProxyCommand="nc -X connect -x 198.19.0.1:3128 %h %p" -o IdentitiesOnly=yes -i ~/.ssh/id_ed25519 ubuntu@132.145.194.139 "cp /var/www/arcade/games.json.bak-toukon-test /var/www/arcade/games.json"
```

The nginx aliases (`/roms/toukon-fullen.chd`, `/roms/toukon-hybrid.cue`,
`/roms/tr1-en-final-track1.bin`, `/roms/dummy-audio/`) can stay for a
retest, or be removed by restoring
`/etc/nginx/sites-available/arcade.bak-toukon` + `nginx -t` + reload.

## Hybrid card (NOT part of this test)

`toukon-hybrid` is staged as `coming_soon` with its files served
(CUE + BIN + dummy audio). It has NOT been tested in PCSX ReARMed either.
Its live test needs its deployed status flipped first (ask the lane for a
follow-up flip) — play.html gates non-playable cards, so the browser cannot
reach it until then.

## Reference hashes

- `tr1-fullen.chd` FILE SHA-1: `6e2b31dc418a2f1134f93ebbc77603c8d6246390`
  (this is what `romSha1` in games.json records — matches the tekken3
  convention, verified by sha1sum).
- CHD internal raw SHA-1 (chdman): `1b8217e39f1104ff40d9b9546477fbd7c91d0e1e`
  — chdman verify passed (raw + overall) on the VM 2026-11-20.
- `tr1-en-final-track1.bin` SHA-1: `17050fec804b94661892ae35cece7ae167d1f952`.
