# Phase 5 — Repo-player browser verification spec

## What to test
The arcade PS2 player reworked to stream ISOs from the repo instead of the
VM file. Deployed (side-by-side, live player untouched):

- http://132.145.194.139/play-ps2-repo.html?game=koc2&autotest=1  (English)
- http://132.145.194.139/play-ps2-repo.html?game=koc2hybrid&autotest=1  (Hybrid)

`autotest=1` boots automatically (no Play tap needed) and enables the
on-page debug log. The page exposes `window.__ps2test`:
`{state, fps[], errors[], discReads, discBytes, startedAt}`.

## SAB gate (important)
The player needs SharedArrayBuffer + crossOriginIsolated (HTTPS). The live
arcade is HTTP, so the browser task must use the SAME route the original
KoC2 player test used to get SAB working (browser flags, the VM's local
8443 TLS vhost, or whatever that lane did). If `__ps2test.state` is
`no-sab`, that is a TEST-SETUP issue, not a player bug — fix the setup,
do not change the player.

## Success criteria (English first, then Hybrid)
1. `window.__ps2test.state === 'running'`
2. Title screen visible in a screenshot (KoC2 title, English HUD)
3. `__ps2test.fps` has readings (expect ~15-19 fps in a match on desktop,
   same as the VM-file player — speed is a Play! property, not a serving
   property; the point of this test is that repo-serving WORKS)
4. `__ps2test.discReads > 0` and `__ps2test.discBytes > 0` (proves the
   emulator actually read the ISO from the repo pieces)
5. `__ps2test.errors` empty (or only benign entries)

## Failure modes
- `state === 'error'`: read `__ps2test.errors` + the on-page debug log.
  Disc-read errors name the piece + HTTP status.
- Network tab should show Range (206) fetches to
  raw.githubusercontent.com/.../english/King-of-Colosseum-II-English.iso.partNNN
  and one manifest fetch (.manifest.json). No full-piece 200 downloads.

## After a verified boot (do in order)
1. On the VM, back up the old player and swap in the repo player:
   `cp /var/www/arcade/play-ps2.html /var/www/arcade/play-ps2-vmfile.html`
   `cp /var/www/arcade/play-ps2-repo.html /var/www/arcade/play-ps2.html`
   (Verify http://132.145.194.139/play-ps2.html loads + contains PieceDiscDevice.)
2. Delete the VM ISOs + BIOS + memcards (ONLY after the swap is verified):
   `rm -rf /home/ubuntu/koc2-english`  (9,205,133,538 bytes)
   This also removes Mars's old download links — see the new links below.
3. The koc2 card flip in games.json is a SEPARATE decision (standing rule:
   flip only after HTTPS + Mars's phone speed test). Do not flip it here
   unless the parent says so.

## New download links for Mars (repo-based)
- English ISO (47 pieces + manifest, browse):
  https://github.com/mhvnsnt/western-heart/tree/muse/koc2-raw/raw/king-of-colosseum-2/english
- Hybrid ISO (47 pieces + manifest, browse):
  https://github.com/mhvnsnt/western-heart/tree/muse/koc2-raw/raw/king-of-colosseum-2/hybrid
- BIOS (direct download, 13,380,830 bytes):
  https://raw.githubusercontent.com/mhvnsnt/western-heart/muse/koc2-raw/raw/king-of-colosseum-2/ps2/ps2-bios-official.zip
- Reassembly (PCSX2 users): download all 47 .partNNN files + the
  .manifest.json, then:
  `cat King-of-Colosseum-II-English.iso.part* > "King of Colosseum II (English).iso"`
  Verify: `sha256sum` must equal
  e3febfb18878c1c0256e90e4e1bcadee66bfd6b0650739e924a4f5f4c2c398fc (English)
  4519330547d1974a7f5a40cb4731885a86522129dad6d063e6803c836a082d5c (Hybrid)
- Note: for PLAYING, no download is needed — the arcade player streams the
  ISO from the repo. Downloads are only for PCSX2-on-PC use.
