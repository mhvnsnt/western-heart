# SCVI + DOA6 Acquisition Assessment (2026-10-14 ~20:00 EDT)

**Status:** Mechs docs done and safe (both MERGED to western-heart main: PR #45 SCVI,
PR #44 DOA6). Game binaries NOT acquired. This doc covers the acquisition hunt.

## Archive.org — NEGATIVE (verified via advancedsearch API, not guesswork)

- `soulcalibur VI` → no game dump. Only gameplay videos, trailers, Giant Bomb quick-looks.
- `dead or alive 6` → no game dump. Only gameplay clips/playthroughs.
- Stepdown titles: `soulcalibur V`, `soulcalibur IV`, `dead or alive 5` → NO game
  binaries on Archive.org (trailers + gameplay videos only).
- Conclusion: Archive.org is not a path for either game or any stepdown version.

## SCVI — torrent paths exist (RESEARCH ONLY, nothing downloaded)

- **FitGirl repack** `SoulCalibur VI v02.31.01/Denuvoless + 14 DLCs`: repack 10.3 GB
  (orig 17.3 GB). Listed on fitgirl-repacks.site with 1337x/RuTor magnet mirrors.
  RarBG mirror records show recent seeders (13 on one FitGirl torrent, 10 on KaOs
  repack, 19 on the 17.3 GB CODEX ISO, 22 on DODI Deluxe Edition). Well seeded.
- **PS4 PKG** (CUSA09884, 9.7 GB) also indexed but low seeds.
- Size after install: ~17–20 GB. VM disk: 83% used (17 GB free) — an install-sized
  pull would blow the disk ceiling. Only the 10.3 GB repack itself would fit, and
  extracting + installing needs 2× space. Not viable on this VM.

## DOA6 — torrent paths exist (RESEARCH ONLY, nothing downloaded)

- **ElAmigos** `Dead or Alive 6 Last Round [Update 1.10]+[Update 1.14]`: 29.24 GB
  download / 29.9 GB ISO, torrent mirrors listed (elamigosgames.net, Updated 3 days ago).
- **FitGirl repack**: 27.7 GB. **SteamUnlocked pre-installed**: 58.22 GB archive.
- PS4/PC deltas: install footprint 50–80 GB. VM disk: 83% used — nowhere near enough.
  Not viable on this VM.

## Stepdown strategy

- **DOA5: Last Round PC** — FitGirl repack v1.10C + All DLCs, 4.3 GB (orig 11.2 GB),
  listed on fitgirl-repacks.site with 1337x/KAT/RuTor mirrors + a Google Drive filehoster
  mirror. Small enough to fit. Value: partial — same developer lineage (Team Ninja),
  hold/triangle DNA is close, but DOA5 models/anims ≠ DOA6 and owner wants DOA6 exactly.
- **Soulcalibur IV / V** — PS3/Xbox 360 ONLY, no PC version; nothing on Archive.org.
  Would need PS3 disc dumping (owner hardware) or PS3-PKG hunt with worse seeding.
  Value: partial — weapon-fighter 8-way-run DNA, but SCVI is UE4 with different formats.
  Note: Soulcalibur II teardown (GameCube/PS2/Xbox, ~60%) already covers the series'
  weapon-fighter base — biggest overlap is already in progress.
- Owner's complete game list (2026-10-14) names **SCVI and DOA6 exactly**, not the
  stepdowns — stepdown material would need owner sign-off as useful vs. wasted tokens.

## What's secured

- GitHub (western-heart, main): `teardown/soulcalibur-6/TEARDOWN.md` + `docs/`;
  `teardown/dead-or-alive-6/DOA6-MECHANICS.md` + `TEARDOWN.md`. Both via merged PRs
  (#45, #44). No open PRs.
- TeraBox: NOT done by this lane — owner requires ALL TeraBox uploads via browser
  lane (assistant browser task). Flagged for coordinator: upload the two teardown
  folders to TeraBox.

## BLOCKERS — what the owner would need to provide

1. **Download hardware**: a machine with 60–100 GB free (or direct-to-TeraBox via a
   browser lane) to take the SCVI FitGirl repack (~10.3 GB dl / ~17 GB installed)
   and DOA6 (~29.2 GB dl / ~50–80 GB installed). The VM at 83% usage cannot.
2. **Decision**: pursue exact titles (SCVI/DOA6 torrents listed above) vs. approve
   stepdown (DOA5LR 4.3 GB FitGirl; SCIV/V via PS3 dump) vs. owner-supplied copy.
3. **WH franchise names**: RENAME-MAP.md rows added for both games; WH proprietary
   names are owner-assigned — not renamed until he names them.
4. RESUME RULE (owner 2026-10-14): any pull must be resume-capable
   (aria2c/wget -c/curl -C-) — never restart from zero.

**Honest ceiling:** these two games cannot reach 100% teardown from this VM without
either (a) owner-provided copies, or (b) a larger staging machine the browser lane
can drive. Docs-only at 10% is the real status until then.
