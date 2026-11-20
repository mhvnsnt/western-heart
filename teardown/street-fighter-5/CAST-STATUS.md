# Street Fighter V — Base-Roster Cast Pull Status

**Task:** pull the rest of the SFV on-screen base roster into `teardown/street-fighter-5/models/<name>/`
following the Rashid precedent (`models/rashid/` — DeviantArt PharaohIllusion XPS `.7z` + SFMLab SFM `.rar`,
README per character in Rashid format, original archives preserved).

**Status as of 2026-10-13:** BLOCKED ON DOWNLOADS — see below. This file is the verified source
manifest so a browser-equipped worker can complete the pulls without re-doing research.

## Download blockers (verified this lane)

1. **DeviantArt — free-account quota exhausted.** The 2026-10-13 gallery pull hit DA's 10-downloads/week
   free limit; quota was exhausted pulling 4 non-SFV models. The full-file download endpoint
   (`/download/<id>`) 404s without a logged-in session, and deviation pages expose no tokenized file URL
   to anonymous fetchers. A live browser on the owner's DA session can download, subject to quota reset.
2. **SFMLab — Anubis bot-wall.** `curl` gets a JS proof-of-work challenge; the download-server picker is a
   browser action. `browser.open` can read project pages (checksums included) but cannot fetch files.
3. **This lane has no live browser.** Per subagent constraints, all downloads below are handed off as exact URLs.

**Precedent for what lands where:** original archives → GitHub Release (like `rashid-models-20261013`) or
TeraBox `/western-heart/street-fighter-5/`; repo dir keeps `README.md` + `SHA256SUMS.txt` only
(Rashid's dir is README + SHA256SUMS, 8 KB — the 57 MB archives live on the release).

## Per-character manifest

Status codes: `HAVE-URL` = exact download target verified, awaiting browser pull.
`NOT-FOUND` = no PharaohIllusion/SFMLab match surfaced via public search — browser worker should check
PharaohIllusion's "Street Fighter V" gallery folder (168 deviations) directly before declaring it missing.

| Character | DA XPS (PharaohIllusion unless noted) | SFMLab SFM | Status |
|---|---|---|---|
| Ryu | Fallback: DaemonCollection "Hot Ryu" `https://www.deviantart.com/daemoncollection/art/XPS---Street-Fighter-V---Hot-Ryu-614498602` (no PharaohIllusion Ryu found) | `https://sfmlab.com/project/9826d2b7-c2b2-429b-a600-4e3760fbe6e4/` — `ryu.rar` 12.46 MB, SHA-256 `e47e912701642825a1a247f5db4a9340949d2e39c5eacad683553e62c95715f4` | HAVE-URL |
| Chun-Li | June `.../pharaohillusion/art/SFV-Chun-Li-June-XNALara-XPS-767971466` · Nostalgia `.../SFV-Chun-Li-Nostalgia-XNALara-XPS-828383790` · Track Suit `.../SFV-Chun-Li-Track-Suit-XNALara-XPS-828383932` · School Uniform `.../SFV-Chun-Li-School-Uniform-XNALara-XPS-861532253` · Special Forces `.../SFV-Chun-Li-Special-Forces-XNALara-XPS-821622882` · (fallback: Chrissy-Tee Training `https://www.deviantart.com/chrissy-tee/art/SFV-Chun-Li-Training-XPS-UPDATED-721285362`) | "Street Fighter - Chun Li" by SFMLab-Import and "Chun Li Superpack" exist on the SF street-fighter list (project URLs not captured — resolve via list) | HAVE-URL |
| Ken | No PharaohIllusion Ken found. Fallbacks: Chrissy-Tee C1 `https://www.deviantart.com/chrissy-tee/art/SFV-Ken-C1-XPS-712468200` · DragonLord720 1p `https://www.deviantart.com/dragonlord720/art/SFV-Ken-1p-612389686` · JSRRemix `https://www.deviantart.com/jsrremix/art/Sfv-Ken-569964374` | NOT-FOUND (no clean SFV Ken SFM port surfaced) | HAVE-URL (fallbacks) |
| Cammy | Nostalgia `https://www.deviantart.com/pharaohillusion/art/SFV-Cammy-Nostalgia-XNALara-XPS-861538216` · Killer Bee (= default costume) `https://www.deviantart.com/pharaohillusion/art/SFV-Cammy-Killer-Bee-XNALara-XPS-876667337` · (fallback: Chrissy-Tee C1 `https://www.deviantart.com/chrissy-tee/art/SFV-Cammy-C1-XPS-Model-757480702`) | "Cammy White - Street Fighter V" and "Cammy White" by SFMLab-Import exist on list (resolve URLs via list) | HAVE-URL |
| M. Bison | NOT-FOUND | NOT-FOUND | NOT-FOUND — check PharaohIllusion SFV gallery folder |
| Nash | NOT-FOUND | NOT-FOUND | NOT-FOUND — check PharaohIllusion SFV gallery folder |
| Vega | Fallback: Teh69thSpartan Default `https://www.deviantart.com/teh69thspartan/art/Vega-Default-1209333558` (no PharaohIllusion Vega found) | NOT-FOUND | HAVE-URL (fallback) |
| Zangief | NOT-FOUND | "Street Fighter (IV + V) - Zangief" by SFMLab-Import exists on list (resolve URL via list) | HAVE-URL (SFMLab) |
| Dhalsim | NOT-FOUND | NOT-FOUND | NOT-FOUND — check PharaohIllusion SFV gallery folder |
| Birdie | NOT-FOUND | NOT-FOUND | NOT-FOUND — check PharaohIllusion SFV gallery folder |
| Karin | NOT-FOUND | NOT-FOUND | NOT-FOUND — check PharaohIllusion SFV gallery folder |
| R. Mika | Fallback: Chrissy-Tee Swimsuit `https://www.deviantart.com/chrissy-tee/art/SFV-R.Mika-Swimsuit-XPS-Model-808348446` (no PharaohIllusion Mika found) | "Rainbow Mika - Street Fighter V" by SFMLab-Import + "Rainbow Mika (Street Fighter V) *2017*" by Stealth2111 exist on list (resolve URLs via list) | HAVE-URL |
| Laura | Story `https://www.deviantart.com/pharaohillusion/art/SFV-Laura-Story-XNALara-XPS-876667542` | `https://sfmlab.com/project/626527b9-5b19-4c05-b16a-3caf02eb5b98/` — "Laura Matsuda [Alt Costume]" (+ "Laura Matsuda - Street Fighter V" by SFMLab-Import on list) | HAVE-URL |
| F.A.N.G | NOT-FOUND | NOT-FOUND | NOT-FOUND — check PharaohIllusion SFV gallery folder |
| Necalli | NOT-FOUND | NOT-FOUND | NOT-FOUND — check PharaohIllusion SFV gallery folder |
| Rashid | DONE (precedent: `models/rashid/`) | DONE | DONE — skipped per brief |

## Browser handoff spec

For each `HAVE-URL` character, the browser worker should:
1. Open the deviation/project page on the owner's logged-in session.
2. Download the original archive (`.7z` for XPS, `.rar` for SFM). Prefer PharaohIllusion default-costume
   variants where a choice exists (Rashid precedent: default + one alt).
3. Extract with py7zr/unrar; record from `.mesh.ascii`: verts, faces, bones, mesh count; list texture names.
4. Create `teardown/street-fighter-5/models/<name>/` with `README.md` (Rashid format), `SHA256SUMS.txt`,
   `archives/` holding the originals (or note the GitHub Release/TeraBox location if too large for git).
5. Note DA's weekly quota: 10 free downloads/week — spread across resets or use Core.

## Western Heart notes (SF federation law)

These are research/reference models for the chimera — SF characters keep SF movesets/animations but play
like Tekken (owner 2026-10-13: Tekken + Urban Reign input style). Brief per-character WH value:
- **Ryu:** the archetype shoto — Hadouken/Shoryuken/Tatsumaki as the baseline projectile/DP/spinning-kick
  templates; renamed/reskinned per federation law.
- **Chun-Li:** fastest legs in the cast — Hyakuretsukyaku (lightning kicks) and Spinning Bird Kick give WH a
  rushdown/pressure template; charge-motion specials are the interesting mechanic to study.
- **Ken:** aggressive shoto variant — multi-hit Shoryuken and run-based pressure; contrasts Ryu's zoning.
- **Cammy:** dive-kick + hooligan mixup rushdown; small fast body type reference for WH roster builds.
- **M. Bison:** charge-motion psycho-power villain; Psycho Crusher as a full-screen armored-advance template.
- **Nash:** teleport + sonic-boom zoning with the "resurrected soldier" visual hook.
- **Vega:** claw + wall-dive mobility; mask/claw as removable-gear reference (bodygroup-style toggles).
- **Zangief:** the grappler — SPD/360s are the command-grab template; huge-body rig reference.
- **Dhalsim:** stretchy-limb zoner; limb-scale rigging study for non-standard proportions.
- **Birdie:** brawler bruiser; chain/grapple normals as weapon-integrated moveset study.
- **Karin:** rekka (multi-input chain) pressure — the rekka system is a prime Tekken-federation candidate.
- **R. Mika:** tag/wrestling hybrid moveset (with partner Nadeshiko) — directly relevant to the WMXIX/No Mercy
  wrestling federation; mic-stand prop as held-weapon reference.
- **Laura:** grappler/striker hybrid with projectile; Brazilian visual design reference.
- **F.A.N.G:** poison/DoT mechanic + long-range normals; the status-effect template for WH.
- **Necalli:** grappler with transformation (V-Trigger form change) — form-change rig reference.
- **Rashid:** (done) wind-fighter movement + Middle Eastern visual design.
