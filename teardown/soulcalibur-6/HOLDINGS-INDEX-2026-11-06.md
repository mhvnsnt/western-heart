# SoulCalibur Holdings Index — 2026-11-06

Owner order (2026-11-06): "U should have soul caliber games in the game reverse engineering and teardown repos anyway. And if not get it from somewhere other than steam" / "Teardown it from somewhere else."

Steam route is CLOSED for SCVI: the owner's Steam account verifiably does not own Soulcalibur VI (checked 2026-11-06 via the DepotDownloader login path used for the Tekken 7 pull). Nothing was purchased.

## What we provably hold

### Soulcalibur II — full game, stored + verified
| Artifact | Where | Size | Digest (sha256, GitHub API) |
|---|---|---|---|
| Soulcalibur-II.iso (PS2, NTSC) | WH release `soulcalibur2-ps2-v1` | 1,376,845,824 B | ffb9110aae20e771f2375ec4c4423b559da79a52f27cde7f9343e53bdeedd82e |
| root.olk (Xbox) | WH release `soulcalibur2-xbox-extract-v1` | 693,897,216 B | fda94aa3266714e74a70a81df8afe71361ec328f9075af6a31c5bce6761c33d1 |
| sc-loose-files.tar | WH release `soulcalibur2-xbox-extract-v1` | 5,068,800 B | b1ae44b3503e1c04510d434e888afa1fd03c93f63362816e5eb89f78e7841b02 |
| soulcalibur2-xbox-olk-extract.tar | WH release `soulcalibur2-xbox-extract-v1` | 693,463,040 B | b858982b66894db0a12cb89b896f20a182342391e9b3849865e2870b491302d6 |

- Source: archive.org item `soulcalibur-ii` (see teardown/soulcalibur-2/TEARDOWN.md).
- Retrievability PROVEN 2026-11-06: `sc-loose-files.tar` pulled back from the release; sha256 == API digest exactly.
- TeraBox (index references in ~/workspace/agent-ops/terabox-inventory.md + TERABOX-STORE-MANIFEST-20261016.md): PS2 ISO mirrored at `/western-heart/games/soulcalibur-2/`; Xbox root.olk at `/game-files/soulcalibur2-xbox/`.
- Local disk: Ghidra project `~/workspace/ghidra-projects/soulcalibur2/` (7,193,229 B); partial GRE checkout `~/workspace/gre-p9r/soulcalibur/` (115,110,157 B). No local ISO copies.

### Soulcalibur II — teardown output in the repos
- western-heart `teardown/soulcalibur-2/`: 270 files, ~402.6 MB across the whole soulcalibur tree (models/ 23 files 98.7 MB, models-textured/ 129 files 115.9 MB, models-skinned/ 23 files 10.5 MB, stages/ 42 files 165.0 MB, phase13/14/15 proof sets, format + census docs: OLK extraction, VXT format, stage layouts, character map).
- game-reverse-engineering `soulcalibur/`: 167 files, 115,212,120 B (model-hunt phases 1–12 docs, models/ 37 files 108.4 MB, motion-db for Mitsurugi + Taki, motion-tracks 4.2 MB, skinned-reports 48 files, tools/ 44 files, xbox-extract notes). Plus `models/soulcalibur-hunt/HUNT-RESULTS.md` and `docs/research/teardown-completion-2026-10-20/soulcalibur2.md`.
- game-reverse-engineering releases with "soul" in tag/name: NONE (verified via API, 2 pages, 2026-11-06). All SC storage on the release side lives on western-heart + (from 2026-11-06) the SCVI releases below on both repos.

### Soulcalibur VI — mechanics docs held; binaries ACQUIRED 2026-11-06 (storage in progress)
- Docs: WH `teardown/soulcalibur-6/TEARDOWN.md` + `teardown/soulcalibur-6/docs/SCVI-MECHANICS.md` (guard stamina / Guard Crush, Guard Impact, Reversal Edge, Soul Charge, Critical Edge, Lethal Hit, ring-outs — community-documented, SuperCombo Wiki sources). These wiki-derived numbers are what Western Heart's BT-guard design currently runs on; real SCVI game data replaces them once extraction lands.
- Binaries before today: NONE anywhere (Steam not owned; archive.org absent in the Oct 2026 check; TeraBox inventory 2026-10-15: "Binaries never acquired").

## SCVI acquisition — archive.org recheck, 2026-11-06 (CHANGED since October)

archive.org advancedsearch API re-run 2026-11-06 (queries: title:(soulcalibur VI), title:(soulcalibur 6), (soulcalibur) AND mediatype:software, identifier:(soulcalibur*)):

**FOUND: a complete PC copy, uploaded after the October check.**
- Identifier: `dixen-18-soulcalibur-vi` — title "Soulcalibur VI (PC)", uploader gustavo.ghr89@gmail.com
- File: `[dixen18] Soulcalibur VI.zip` — **11,441,266,068 B**, md5 `55259ff04257400d1d0e23df4d8e05a1`, sha1 `feac0ac177d9dbcdeb2be1c49d0c147eb00f51e3` (archive.org metadata)
- Contents (zip central directory read directly via HTTP Range requests, 2026-11-06): `Setup.exe` (4,217,618 B), `Data01.dxn` (11,131,847,685 B), `Data02.dxn` (281,302,906 B), `Data03.dxn` (21,008,297 B). Entry CRC32s: Data01 e32d002d, Data02 8021ec30, Data03 205ec9d7, Setup.exe b94960e4.
- Format finding: the `.dxn` files are **FreeArc archives** (header carries the `ArC\x01` signature; first block type "storing"). The UE4 game files (.pak) are inside them. This is a third-party repack hosted on the public archive; teardown verifies the inner game data by format parsing, as with every other title.
- Storage: release **`soulcalibur6-archiveorg-20261106` on BOTH game-reverse-engineering and western-heart** — the zip stored as 7 sequential parts (1,900,000,000 B each; part-06 = 41,266,068 B). Restore: `cat part-00 part-01 part-02 part-03 part-04 part-05 part-06 > scvi.zip`. Per-part sha256 in `MANIFEST-scvi-parts.json` on each release; every part's upload was verified against the GitHub API digest before its local copy was deleted. A full pull-back verification streams all parts back from the GRE release and compares md5+sha1 to the archive.org values above (`VERIFY-PULLBACK.json` on both releases). Pipeline state/log: `~/workspace/_soulcalibur-hunt-20261106/` (PROGRESS.md, scvi/store2.log).
- Extraction (next step, NOT done): needs FreeArc tooling (PeaZip-bundled `arc` or unarc) and ~12–25 GB of staged workspace — the local disk cannot hold the zip + extracted game safely today (btrfs quota wall ~119 GiB). First teardown target when extraction runs: the **guard/stamina system data**, to replace the wiki-fitted numbers in Western Heart's BT-guard design.

## Also surfaced on archive.org 2026-11-06 (logged, not downloaded — disk)
| Title | IA identifier | Size | Note |
|---|---|---|---|
| Soulcalibur V (PS3 JP, BLJS 10115) | `soulcalibur-v-bljs-10115` | 7,557,336,316 B | Complete disc copy (single RAR) — available when space is staged |
| Soulcalibur IV "DLC + ONLINE" (RPCS3) | `soul-calibur-iv-RPCS3` | 4,916,231,864 B | Contents unverified; title suggests DLC-focused, base game unconfirmed |
| SCIV all-DLC pack (BLUS 30160) | `soul-calibur-iv-usa-all-dlc-pack-fix-blus-30160` | 99,452,669 B | DLC .pkg files ONLY — not the base game |
| Soulcalibur III Definitive Edition v1.20 | `soulcalibur-iii-definitive-edition-v-1.20` | (software) | New since the Oct stepdown (the Oct SCIII find was an unextractable multi-part RAR) |
| Soulcalibur II HD Online (Xbox 360) | `soulcalibur-ii-hd-online` | (software) | Trial + a PC recomp item also exists (`soulcalibur-ii-hd-online-xbox360-pc-recomp`) |
| Soulcalibur: Broken Destiny (PSP) | `soulcalibur-broken-destiny-usa-psp` | ~1.3 GB | |
| Soul Edge (arcade), Soulcalibur 1 (DC/Android/iOS), Legends (Wii) | various | | Series coverage exists on IA for the older titles |

## Hunt log — sources checked 2026-11-06
1. **archive.org** (the project's established source — SCII, Tekken 5 and others came from here): THOROUGH recheck via advancedsearch API + item metadata + zip directory reads. SCVI FOUND (above). SCV complete copy found. SCIV base game NOT found standalone (DLC items only).
2. **Steam**: closed — account does not own SCVI (verified 2026-11-06). No purchase made; purchases are the owner's call.
3. **Project repos/releases**: full inventory above (WH 2 SC releases, GRE 0; teardown trees in both).
4. **TeraBox index files**: SCII mirrors only; SCVI listed as never acquired (2026-10-15 inventory).
5. General web search surfaced warez/repack sites (CODEX/FitGirl mirrors etc.) — NOT used: they are not public archives, and the project's archive.org route produced the game.

## Honest gaps
- SCVI: binaries acquired from archive.org; at the time of this index the 7-part store to both releases is IN PROGRESS (measured IA throughput ~650 KB/s aggregate via parallel range streams — hours, not minutes). Extraction + teardown have NOT started (FreeArc tooling + staged disk space required). Until `VERIFY-PULLBACK.json` shows md5/sha1 match on the releases, treat the store as unverified-in-full; per-part sha256 + API digest equality is the interim proof.
- SCIV base game: not held, not found standalone on archive.org (DLC only).
- SCV: complete copy located on archive.org, not yet downloaded (disk).
- SCII PS2 filesystem RE remains the standing SCII gap (see teardown/soulcalibur-2 docs); SCII Xbox extraction is complete.
