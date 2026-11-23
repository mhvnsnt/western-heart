# Phase 5 — Repo-player verification report (2026-11-21 ~06:45–07:05 EST)

Route: Puppeteer 25.18.1 + Chrome 157 ON the Oracle VM against
http://localhost/play-ps2-repo.html (secure context, SAB works).
Scripts: `phase5-verify.js` (boot + metrics), `phase5-title.js` /
`phase5-title2.js` (memcard-prompt dismiss + title capture).
All VM-side work ran out of /dev/shm/phase5 — the root disk was 100% FULL
(0 bytes free) at test time, so nothing could be written to /home or /tmp.

## VERDICT: BOTH GAMES VERIFIED — all 5 spec criteria pass for each

### koc2 (English)
- state: `running` (booted in 5s, stayed running through 90s + 2min title runs)
- fps: 95 readings, avg 31.7, min 0 (boot), max 48, last [31,33,33,35,32]
  (title run: 149 readings)
- discReads: 19, discBytes: 39,845,888 (title run: 43 reads / 90,177,536 B)
- errors: []
- Network: manifest 200, 19 x HTTP 206 Range fetches to
  raw.githubusercontent.com piece URLs, 0 non-206 piece fetches
- Title screen: `koc2-title-plus40s.png` — "KING OF COLOSSEUM II" glowing
  blue logo. Also: memcard prompt, NOW LOADING, attract FMV (Colosseum
  exterior).

### koc2hybrid (Hybrid JP/EN)
- state: `running` (booted in 5s)
- fps: 94 readings, avg 31.4, min 0 (boot), max 42, last [39,39,36,33,40]
  (title run: 153 readings)
- discReads: 18, discBytes: 37,748,736 (title run: 42 reads / 88,080,384 B)
- errors: []
- Network: manifest 200, 20 x HTTP 206 Range fetches, 0 non-206
- Title screen: `koc2hybrid-title-plus40s.png` — crisp "KING OF COLOSSEUM II"
  logo. Also: memcard prompt (ENGLISH), attract FMV (4 wrestlers + flames).

## Notable observations
- The memcard prompt on the English ISO is in JAPANESE (known: one of the 3
  untranslated strings); the hybrid shows the same prompt in ENGLISH.
- Title/attract runs at ~19-40 fps (32-65%) on the SwiftShader VM rig —
  same class as the VM-file player; speed is a Play! property, not serving.
- Input works: __ps2press Up + Circle dismissed the memcard prompt.
- No `no-sab` on localhost, as expected.

## Swap + deletion (done in spec order, 2026-11-21 ~07:00 EST)
1. `cp play-ps2.html play-ps2-vmfile.html` (21,825 B backup of old player)
2. `cp play-ps2-repo.html play-ps2.html` (25,751 B, byte-identical to repo file)
3. Verified: http://132.145.194.139/play-ps2.html → HTTP 200, contains
   PieceDiscDevice (9 matches)
4. Deleted `/home/ubuntu/koc2-english` — exactly 9,205,133,538 bytes:
   - King of Colosseum II (English).iso (4,593,778,688)
   - King of Colosseum II (Hybrid JP-EN).iso (4,593,778,688)
   - ps2_bios_official.zip (13,380,830)
   - scph39001.MEC (4), scph39001.NVM (1,024), scph39001.bin (4,194,304)
5. games.json koc2 card NOT touched (still status "desktop", core null).

## Disk
- Before: 193G used, 0 avail, 100%
- After: 184G used, 9.3G avail, 96%

## Consequences (expected, per spec)
- Old download links now 404: /koc2/King-of-Colosseum-II-English.iso,
  /koc2/ps2-bios.zip. Repo-based links in PHASE5-VERIFY.md replace them.
- Live player now streams from western-heart muse/koc2-raw pieces.

## Evidence in this dir
- phase5-results.json, run.log, title-results.json, title2-results.json
- koc2-t10/t30/t60/t90.png, koc2hybrid-t10/t30/t60/t90.png (boot + prompt)
- koc2-prompt.png, koc2-title1/2.png, koc2hybrid-title1/2.png
- koc2-title-plus{20,40,60,80,100,120}s.png,
  koc2hybrid-title-plus{20,40,60,80,100,120}s.png (title + attract)
