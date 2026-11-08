# Urban Reign Redux 0.5 — .urmod extraction (Lane 2)

**Date:** 2026-11-08 ~02:00–02:50 CST  
**Pack:** Urban Reign Redux 0.5 V97 (`urr-base-1`, id `urr-0.5-v97`), from the author's own GitHub release v0.5.0  
**Method:** the author's own tools only — `Source/vendor/mod-manager/urrpack.py` (.urmod = ZIP + manifest), `urrlayout.py` (AFS layout), `Source/vendor/roster-lib/toolnative/` (`gyu_structure`, `gyu_decode`, `vmd_structure`, `vmd_mesh`, `ppk_index`, `texture`/`gs_texture`), `Source/editor/review.py` (mouth-node check). No hand-written parser; where a roster-lib tool could not parse a piece, that is recorded as a tool limit, not worked around.  
**Rules:** `docs/RULES_NO_GUESSING.md` read before data work. No ISO downloaded or fetched. No piracy/ROM/leak sites. No login/paywall bypass.

## 1. What a .urmod is (measured, not assumed)

- The core mod is a ZIP (`urr-base-1`) with `manifest.json`, `data/NNNNNN.bin` parts, and portraits. Verified: **3639 parts, 670,765,056 bytes**, every part SHA-256-checked against the manifest — **0 bad**.
- Output disc the pack builds: **4,606,052,352 bytes, SHA-256 `cc2312c1909cec438b8971133445eb7e2bfc7eecf03bdd0fed01cbefd7134541`, PCSX2 CRC 74E78599**. Source disc: 4,140,924,928 bytes, SHA-256 `c22209eefcdc4275a75dc3656b4abf5807940155236916271e19455d302a8ec2`.
- Parts + copies are a binary diff of the output disc against the source ISO: a part is a changed byte range of the output disc; a copy is a range copied verbatim from the source ISO at build time. **Parts cover only 14.56% of the output disc** (670,765,056 of 4,606,052,352 bytes). Everything not in parts exists ONLY in the source ISO — which is not on this VM.
- DVD000 AFS table + names: **100% covered by parts** (rebuilt from parts; 2716 entries). DVD001 table + names: **100% covered** (1335 entries). DVD000 data region: 35.8% covered. DVD001 data region: 10.8% covered. ELF (runtime): 38.4% covered (19,810,304 of 51,564,544 bytes, 273 parts).
- The two HD packs are plain PNG ZIPs (`urr-hd-1`): main set 76 files, full set 397 files — all SHA-verified, all extracted (see §5).

## 2. The fighter list — 29 found, not 25

The task named 25 fighters. The pack actually holds **29**: the manifest roster's 23 custom-slotted fighters plus 6 more whose model/package live in stock slots (CID map from the author's `extract_portraits.py`). The 4 not in the task's list are Baek, Jack, Steve, Violet — all four are Tekken guests with custom model/package entries in the roster. Tekken guests total 20 (16 roster + Bryan, King, Hwoarang, Heihachi in stock slots); crossovers total 9 (Cammy, Leon, CJ, Kiryu, Jeff, Snake, Renamon, Vergence, Ricardo).

## 3. Per-fighter extraction table

Model = loose VMD (`converter/design/test/chrNN.vmd`); Package = PPK (`afs/safe/ppk/charNNN.ppk`). Coverage = share of the file's bytes present in the .urmod parts. Gaps = byte ranges that only exist in the source ISO. **EXTRACTED means the exact bytes are on disk under `extracted/fighters/<Name>/`; anything below 100% was NOT written out** (no gap-filled files — a file with invented bytes is not the file). Node counts come from the author's `vmd_structure.parse_vmd` on the extracted file (or its embedded copy inside the package).

| Fighter | CID | Model idx / size / coverage / gaps | Package idx / size / coverage / gaps | Extracted | Nodes | Mouth (AGO/KUCHI_R/KUCHI_L) |
|---|---|---|---|---|---|---|
| ★ Armor Queen | 58 | 1673 / 1,891,792 B / 0.989 / 5 gaps, 20,480 B | 2415 / 1,978,576 B / 0.990 / 5 gaps, 20,480 B | — | — | — |
| ★ Asuka | 56 | 1671 / 974,272 B / 0.987 / 2 gaps, 12,288 B | 2413 / 1,049,496 B / 1.000 / 0 gaps, 0 B | package.ppk | 53 (embedded) | pkg 0/0/0 (embedded) |
| † Baek | 94 | 2585 / 1,403,392 B / 0.920 / 3 gaps, 112,640 B | 2586 / 1,492,416 B / 0.930 / 2 gaps, 104,448 B | — | — | — |
| ★ Bob | 104 | 2694 / 2,510,912 B / 0.817 / 3 gaps, 460,800 B | 2693 / 2,621,312 B / 0.824 / 3 gaps, 460,800 B | — | — | — |
| ★ Bryan | 43 | 1658 / 575,344 B / 0.986 / 1 gaps, 8,192 B | 2400 / 655,360 B / 0.984 / 2 gaps, 10,240 B | — | — | — |
| ★ CJ | 97 | 2591 / 562,016 B / 0.975 / 2 gaps, 14,336 B | 2592 / 647,504 B / 1.000 / 0 gaps, 0 B | package.ppk | 48 (embedded) | pkg 0/0/0 (embedded) |
| ★ Cammy | 31 | 1646 / 2,183,584 B / 0.963 / 4 gaps, 79,872 B | 2388 / 2,265,264 B / 0.966 / 4 gaps, 77,824 B | — | — | — |
| ★ Christie | 57 | 1672 / 1,124,720 B / 0.927 / 4 gaps, 81,920 B | 2414 / 1,197,600 B / 0.932 / 4 gaps, 81,920 B | — | — | — |
| ★ Devil Jin | 93 | 2583 / 1,242,864 B / 0.919 / 4 gaps, 100,352 B | 2584 / 1,390,112 B / 0.950 / 3 gaps, 69,632 B | — | — | — |
| ★ Heihachi | 53 | 1668 / 680,240 B / 0.916 / 4 gaps, 57,344 B | 2410 / 782,752 B / 0.986 / 2 gaps, 10,656 B | — | — | — |
| ★ Hwoarang | 41 | 1656 / 610,784 B / 0.859 / 3 gaps, 86,016 B | 2398 / 696,960 B / 1.000 / 0 gaps, 0 B | package.ppk | 46 (embedded) | pkg 0/0/0 (embedded) |
| † Jack | 45 | 1660 / 1,470,416 B / 0.996 / 1 gaps, 6,144 B | 2402 / 1,548,576 B / 0.999 / 1 gaps, 2,048 B | — | — | — |
| ★ Jeff | 98 | 2593 / 2,487,232 B / 0.996 / 2 gaps, 10,240 B | 2594 / 3,644,556 B / 0.997 / 3 gaps, 12,288 B | — | — | — |
| ★ Jin | 15 | 1630 / 1,459,696 B / 0.996 / 2 gaps, 6,144 B | 2372 / 1,535,840 B / 0.995 / 2 gaps, 8,032 B | — | — | — |
| ★ Kazuya | 16 | 1631 / 636,608 B / 0.813 / 4 gaps, 118,784 B | 2373 / 714,640 B / 0.954 / 2 gaps, 32,656 B | — | — | — |
| ★ King | 19 | 1634 / 611,152 B / 0.993 / 1 gaps, 4,096 B | 2376 / 687,416 B / 1.000 / 0 gaps, 0 B | package.ppk | 46 (embedded) | pkg 0/0/0 (embedded) |
| ★ Kiryu | 46 | 1661 / 637,296 B / 1.000 / 0 gaps, 0 B | 2403 / 736,544 B / 1.000 / 0 gaps, 0 B | model.vmd, package.ppk | 49 | loose {'AGO': 3, 'KUCHI_R': 3, 'KUCHI_L': 3} / pkg {'AGO': 0, 'KUCHI_R': 0, 'KUCHI_L': 0} |
| ★ Kunimitsu | 102 | 2676 / 3,785,904 B / 0.979 / 6 gaps, 77,824 B | 2675 / 3,890,752 B / 0.979 / 8 gaps, 81,920 B | — | — | — |
| ★ Leon | 0 | 1615 / 1,378,640 B / 0.345 / 4 gaps, 903,168 B | 2357 / 1,605,096 B / 0.423 / 11 gaps, 925,696 B | — | — | — |
| ★ Nina | 95 | 2587 / 1,328,528 B / 0.920 / 4 gaps, 106,496 B | 2588 / 1,407,712 B / 0.945 / 1 gaps, 77,824 B | — | — | — |
| ★ Paul | 59 | 1674 / 1,833,488 B / 0.952 / 5 gaps, 88,064 B | 2416 / 1,909,896 B / 1.000 / 0 gaps, 0 B | package.ppk | 46 (embedded) | pkg 0/0/0 (embedded) |
| ★ Reina | 103 | 2684 / 4,077,040 B / 0.988 / 5 gaps, 47,104 B | 2685 / 4,180,160 B / 0.989 / 5 gaps, 47,104 B | — | — | — |
| ★ Renamon | 100 | 2597 / 3,889,360 B / 0.875 / 6 gaps, 485,376 B | 2598 / 3,962,232 B / 0.901 / 4 gaps, 393,216 B | — | — | — |
| ★ Ricardo | 105 | 2714 / 1,545,168 B / 0.983 / 4 gaps, 26,624 B | 2715 / 1,630,960 B / 0.984 / 4 gaps, 26,624 B | — | — | — |
| ★ Snake | 96 | 2589 / 575,568 B / 0.968 / 3 gaps, 18,432 B | 2590 / 655,584 B / 0.981 / 2 gaps, 12,288 B | — | — | — |
| † Steve | 21 | 1636 / 1,107,312 B / 0.995 / 1 gaps, 6,144 B | 2378 / 1,191,840 B / 0.995 / 1 gaps, 6,144 B | — | — | — |
| ★ Vergence | 99 | 2595 / 2,052,128 B / 0.955 / 2 gaps, 92,160 B | 2596 / 2,126,992 B / 1.000 / 0 gaps, 0 B | package.ppk | 50 (embedded) | pkg 0/0/0 (embedded) |
| † Violet | 54 | 1669 / 1,352,576 B / 0.947 / 4 gaps, 71,680 B | 2411 / 1,445,568 B / 0.955 / 2 gaps, 65,536 B | — | — | — |
| ★ Yoshimitsu | 101 | 2615 / 655,360 B / 0.972 / 3 gaps, 18,432 B | 2616 / 733,856 B / 0.975 / 3 gaps, 18,432 B | — | — | — |

★ = one of the 25 named in the task. † = additional fighter found in the pack (Baek, Jack, Steve, Violet).

**Totals: 58 fighter files (29 models + 29 packages); 8 fully covered and extracted; 50 partial (81.3%–99.9% covered, except Leon 34.5%/42.3%).**

## 4. The 8 extracted files (exact bytes, SHA-256)

- `extracted/fighters/Asuka/package.ppk` — 1,049,496 B, SHA-256 `a0fab1a3114f09adbc03fba6f8824799b91489e43f93e278da10e2caddb1f108` (DVD000 entry 2413, `afs/safe/ppk/char057.ppk`)
- `extracted/fighters/CJ/package.ppk` — 647,504 B, SHA-256 `2026e38f52c3c191aef67fa5731f25a8746c26bf01186b185d2224c7afa0b397` (DVD000 entry 2592, `afs/safe/ppk/char098.ppk`)
- `extracted/fighters/Hwoarang/package.ppk` — 696,960 B, SHA-256 `3e07f90fed12d87b72f29654016273c38b20fbf8215fe29aecef85911c8e15a0` (DVD000 entry 2398, `afs/safe/ppk/char042.ppk`)
- `extracted/fighters/King/package.ppk` — 687,416 B, SHA-256 `0fffca42e0d40c390139cad78d17771ab1e254821269e3c95746a397869b50c3` (DVD000 entry 2376, `afs/safe/ppk/char020.ppk`)
- `extracted/fighters/Kiryu/model.vmd` — 637,296 B, SHA-256 `366a1d5724092674cfcc116c45ea9d8df5844c91e7ecf472e1214368dc1f8b8b` (DVD000 entry 1661, `converter/design/test/chr47.vmd`)
- `extracted/fighters/Kiryu/package.ppk` — 736,544 B, SHA-256 `b4cea4f9b2d96c043d6f164abf73411581bc094d2a3270662eb8c5868dbd3f5b` (DVD000 entry 2403, `afs/safe/ppk/char047.ppk`)
- `extracted/fighters/Paul/package.ppk` — 1,909,896 B, SHA-256 `cb7830a2306afa0b566abe719d7dd2bac3ee8c99ffbeaed78e82d551a44fd96f` (DVD000 entry 2416, `afs/safe/ppk/char060.ppk`)
- `extracted/fighters/Vergence/package.ppk` — 2,126,992 B, SHA-256 `1c4fe28ded96e4e3fc33c62b10e57fb39e857b3a77695fbb964cff69fe9441de` (DVD000 entry 2596, `afs/safe/ppk/char100.ppk`)

Parsed with the author's roster-lib tools (full detail in each `extracted/fighters/<Name>/parse.json`):

- **Asuka package** (4 members, 4 lookup groups): key 0149 (2,928 B); key a340 (71,424 B); key b59f (974,272 B) = embedded model VMD, 53 nodes; key ff7e (744 B).
  - Mouth nodes in the package's embedded model copy: AGO/KUCHI_R/KUCHI_L all type 0 (static).
- **CJ package** (4 members, 4 lookup groups): key 6bc6 (81,680 B); key 7d19 (562,016 B) = embedded model VMD, 48 nodes; key 853e (744 B); key c9cf (2,928 B).
  - Mouth nodes in the package's embedded model copy: AGO/KUCHI_R/KUCHI_L all type 0 (static).
- **Hwoarang package** (4 members, 4 lookup groups): key 05fb (744 B); key 60d4 (82,368 B); key 760b (610,784 B) = embedded model VMD, 46 nodes; key c2dd (2,928 B).
  - Mouth nodes in the package's embedded model copy: AGO/KUCHI_R/KUCHI_L all type 0 (static).
- **King package** (4 members, 4 lookup groups): key 3f24 (2,928 B); key 8bf2 (611,152 B) = embedded model VMD, 46 nodes; key 9d2d (72,464 B); key a370 (744 B).
  - Mouth nodes in the package's embedded model copy: AGO/KUCHI_R/KUCHI_L all type 0 (static).
- **Kiryu package** (4 members, 4 lookup groups): key 4fe1 (2,928 B); key d169 (744 B); key ede8 (95,440 B); key fb37 (637,296 B) = embedded model VMD, 49 nodes.
  - Mouth nodes (author's `review.py` `mouth_nodes`, 3 = moving, 0 = static): loose model {'AGO': 3, 'KUCHI_R': 3, 'KUCHI_L': 3}, package copy {'AGO': 0, 'KUCHI_R': 0, 'KUCHI_L': 0} — the release's static-mouth policy holds: the package copy is static.
- **Kiryu loose model** (637,296 B): `parse_vmd` OK, 49 active named nodes, node table at offset 324704.
  - Mesh decode: **FAILED in the author's own tool** — `vmd_mesh.read_mesh` raises `AssertionError` on the first draw (VIF header check). That decoder is documented as a research decoder for the observed Brad VMD; it does not handle this model's stream. No replacement was hand-written. Vertex counts therefore NOT measured for this model.
- **Paul package** (4 members, 4 lookup groups): key 0d95 (3,032 B); key af9c (72,496 B); key b943 (1,833,488 B) = embedded model VMD, 46 nodes; key ff9d (744 B).
  - Mouth nodes in the package's embedded model copy: AGO/KUCHI_R/KUCHI_L all type 0 (static).
- **Vergence package** (4 members, 4 lookup groups): key 1285 (744 B); key 16a2 (2,052,128 B) = embedded model VMD, 50 nodes; key 718c (2,928 B); key d385 (71,056 B).
  - Mouth nodes in the package's embedded model copy: AGO/KUCHI_R/KUCHI_L all type 0 (static).

Skeleton shape (measured on the extracted models): every extracted model shares the same 40-node core — body chain MUNE1/MUNE2/KUBI/ATAMA, arms SAKOTSU/KATA/UDE/TE (R/L), legs KOSHI/MOMO/HIZA/ASHI/TSUMASAKI (R/L), face MIKEN/MAYU/EYE/MABUTA_UP/MABUTA_UN (R/L) + AGO/KUCHI_R/KUCHI_L — plus per-fighter helper nodes (`__rot`, `__prot`, `__swing`, `__slerp`, `__const`, `__phit`): Asuka +13, CJ +8, Hwoarang +6, King +6, Kiryu +9, Paul +6, Vergence +10. Full name lists are in each `parse.json`.

## 5. HD texture packs — extracted, not mapped per fighter

- Main set: `urr-hd-1`, folder `Urban Reign Redux 0.5` — **76 PNGs, 143,669,151 bytes total on disk**, all SHA-verified against its manifest, extracted to `extracted/hd-main/` (76 PNGs + manifest). Covers Fighter Files, character select, menus, every stage (per the pack notes).
- Full set: folder `Urban Reign Redux 0.5 full set` — **397 PNGs, 623,788,311 bytes total on disk**, all SHA-verified, extracted to `extracted/hd-full/` (397 PNGs + manifest). Covers everything else the game might show.
- **Per-fighter mapping: NOT done.** The PNG filenames carry only PCSX2 texture/CLUT hashes plus a texture id (e.g. `09b66dcb48bc8376-285dc0abb0457fb0-00001d93.png`); no fighter name. The author's own mapping route (`editor/hd.py` + `vendor/exporter/derive_aliases.py`) derives aliases from a model's GS texture uploads, which needs the mesh/sampler decode — and `vmd_mesh.read_mesh` fails on these guest VMDs (see §4). Mapping is therefore owed after the disc is built (PCSX2 replacement-folder layout) or after the mesh decoder is extended by the author's tooling. The PNGs themselves are on disk with manifest SHAs.

## 6. What could NOT be extracted, and the exact blocker

**Blocker (single cause for everything below): the gap bytes live only in Jay's own Urban Reign (USA) source ISO, which is not on this VM — and this lane's hard limit forbids fetching an ISO.** The .urmod is a diff, not a full archive: it stores only bytes that differ from the source disc. A fighter file that is 98% covered is still missing its 2% — and without the source bytes there is no exact file. No gap was filled, guessed, or zero-padded in any delivered file.

| Item | State | Exact gap |
|---|---|---|
| 50 of 58 fighter files (all models except Kiryu; all packages except Asuka, CJ, Hwoarang, King, Kiryu, Paul, Vergence) | Partial, 81.3%–99.9% (Leon model 34.5%, Leon package 42.3%) | 2,048–925,696 missing bytes per file (see §3 gap counts); only in the source ISO |
| Movesets / action tables (per-fighter inputs, strings, hits) | NOT extractable from parts | Tables live in the runtime ELF (ACTION 0x25016f0, BRANCH 0x2bd38d8, REACT 0x2adb768, HIT 0x25fe5a0, registry 0x4706000 per `editor/moveset.py`). ELF is 38.4% covered, but the tables' own ranges are 0.2%–50% covered in their first 64 KB (ACTION 0.4%, BRANCH 2.8%, REACT 0.2%, HIT 35.3%, registry 50.0%) — the tables are near-entirely unchanged-vanilla bytes, i.e. source-ISO bytes. Decodable only from a built disc with the editor's `moveset.py` (runs the game's own chains). |
| Motion banks (shared `tec/motion/*/general.gyu`, `pmotNNN`/`tmotNNN.ppk` style packages) | NOT in the pack at all (0% covered) | Unchanged from vanilla — the new fighters reuse the shared banks. No GYU bank exists inside any extracted char PPK (each char PPK holds only the embedded model + 3 small data members). Motion extraction needs the built disc. |
| Grounded idles / T8 stances / revised movesets (release-note claims) | NOT verified from bytes | These are runtime-table + bank properties; the tables/banks are in the not-extractable set above. The claim is neither confirmed nor denied by this extraction. |
| HD textures per fighter | PNGs extracted, mapping owed | See §5. |
| Mesh vertex/texture data for extracted models | NOT measured | `vmd_mesh.read_mesh` (author's research decoder, Brad VMD only) fails on the guest VMDs. No hand-written replacement per the lane's industry-standard-only rule. |
| Disc build (`-redux-0.5.iso`) | NOT built | See §7. |

**What unblocks the rest:** running the Launcher build on Windows against Jay's own ISO (the route the pack is designed for), or a coordinator decision to supply the repo's own ISO copy to this VM. Either way the already-extracted parts + tables above stay valid — the build just fills the gaps from the source disc.

## 7. Launcher build route — status

**The disc was NOT built. Exact blockers, in order:**

1. **Wine 9.0 installs and runs on this VM** (`sudo apt-get install -y --no-install-recommends wine64` → exit 0; `/usr/lib/wine/wine64 --version` → `wine-9.0`; sudo works without a password prompt here). But the installed loader is 64-bit-only, and **the Launcher is a 32-bit .NET/Mono GUI exe** (`PE32 executable (GUI) Intel 80386 Mono/.Net assembly`). It cannot run under wine64 alone. The 32-bit stack was NOT installed: no i386 foreign architecture is enabled (`dpkg --print-foreign-architectures` prints nothing) and `apt-cache policy wine32:i386` returns nothing — enabling it needs `dpkg --add-architecture i386` + a full 32-bit Wine + Mono/.NET install, which was not attempted because blocker 2 below makes a build impossible regardless, and the VM is at its disk quota (see §8).
2. **No ISO on this VM.** The Launcher needs Jay's own Urban Reign (USA) `.iso` (about 4.1 GB) as its input; it only reads it, never changes it. No ISO is on this VM and this lane's hard limit forbids fetching one. The repo holds Jay's ISO as release `urban-reign-iso-v1`, but fetching it was not done per that limit.
3. **No PCSX2 folder on this VM.** The Launcher also needs a PCSX2 folder (for game settings + HD texture install). None exists here.

So the build runs where Jay runs PCSX2 (Windows), exactly as the pack is designed. Nothing was faked: no ISO was produced, no build was claimed.

## 8. Disk quota incidents (flagged for the coordinator)

The VM hit its disk quota **twice** during this lane (`OSError: [Errno 122] Disk quota exceeded`). The filesystem shows 47 GB free, so this is a user/project quota shared VM-wide — it filled while other lanes were writing (video-mocap alone is 57 GB). At the worst point even a 1-byte write failed everywhere under home for several minutes. Recovery, using **my own lane's files only**: deleted the three duplicate `.urmod` copies inside `work/mm/…/mods/` plus the `work/editor/` unzip (~1.3 GB; the lane-root ZIPs remain the source of truth), then deleted `extracted/core/parts/` (645 MB — the 3,639 part files, all SHA-verified; reproducible from the Mod Manager zip with `extract_a.py`). Writes were restored after each deletion. The quota can fill again without warning; the coordinator should know the VM is at its quota edge before scheduling more heavy lanes.

## 9. Files delivered

- `URMOD-EXTRACTION.md` (this file)
- `extracted/core/manifest.json` — the base pack manifest (3,639 parts, 7,644 copies, layout, roster)
- `extracted/core/coverage.json` — merged part intervals over the output disc
- `extracted/core/dvd000_table.json`, `dvd001_table.json` — rebuilt AFS tables (index, name, offset, size, parts-coverage)
- `extracted/core/fighter_entries.json` — per-fighter entry resolution + gap maps
- `extracted/fighters/<Name>/{model.vmd,package.ppk}` + `.sha256` + `parse.json` — the 8 exact-byte files (Kiryu model+package; Asuka, CJ, Hwoarang, King, Paul, Vergence packages)
- `extracted/hd-main/` (76 PNGs + manifest), `extracted/hd-full/` (397 PNGs + manifest)
- Scripts: `extract_a.py` (verify+extract parts/HD), `extract_b.py` (AFS tables), `extract_c.py` (per-fighter gaps + extraction), `extract_d.py` (roster-lib parsing), `gen_report.py` (this report)
- Tool sources used (read from the Editor zip, restored under `work/tools/`): roster-lib `toolnative/` + `research/` tables, `vendor/mod-manager/urrlayout.py`, `extract_portraits.py`
- Note: `extracted/core/parts/` was removed after use for the disk quota (see §8); re-run `extract_a.py` to restore it from the Mod Manager zip.

**Repo landing: NOT done in this lane.** The extracted files are game-derived bytes (mod author + original game data); landing them into a repo is the coordinator's call. Nothing was pushed, no branch was created, main was not touched.
