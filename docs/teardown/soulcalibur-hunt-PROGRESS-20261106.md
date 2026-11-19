# SoulCalibur Hunt — 2026-11-06
Owner order: inventory all SoulCalibur holdings in GRE + WH, hunt SCVI from non-Steam sources (archive.org first).
Started: 2026-11-06 ~18:08 CST

## Steps
- [ ] Inventory: WH releases (soulcalibur filter)
- [ ] Inventory: GRE releases (soulcalibur filter)
- [ ] Inventory: teardown folders both repos
- [ ] Inventory: local disk + TeraBox refs
- [ ] Retrievability proof: pull-back hash 1 small file
- [ ] Land inventory docs: PR GRE + mirror WH
- [ ] Hunt: archive.org thorough recheck
- [ ] Hunt: other project-used public archives/mirrors
- [ ] If found + fits: download/hash/store both repos/teardown guard data
- [ ] If not found: logged gap report

## Log

## Findings (2026-11-06 ~18:13-18:20 CST)
- WH releases w/ SoulCalibur: exactly 2, both SC2 (ps2 ISO sha256 ffb9110a..., xbox extract 3 assets). GRE releases: ZERO soul releases (2 API pages checked).
- WH teardown/soulcalibur-2/: 270 files, teardown/soulcalibur-6/: 4 files; WH soul total 274 files / 402,603,372 B.
- GRE soulcalibur/: 167 files / 115,212,120 B (model hunt docs phases 1-12, SC2 models, motion-db, skinned-reports) + models/soulcalibur-hunt/HUNT-RESULTS.md + docs/research/teardown-completion-2026-10-20/soulcalibur2.md.
- RETRIEVABILITY PROVEN: sc-loose-files.tar (5,068,800 B) pulled back from WH release soulcalibur2-xbox-extract-v1, sha256 == API digest b1ae44b3...
- IA RECHECK 2026-11-06 (advancedsearch API): SCVI NOW PRESENT (absent Oct 2026): identifier dixen-18-soulcalibur-vi, title "Soulcalibur VI (PC)", uploader gustavo.ghr89@gmail.com, 1 game file: [dixen18] Soulcalibur VI.zip = 11,441,266,068 B, md5 55259ff04257400d1d0e23df4d8e05a1... (full in manifest), sha1 feac0ac177d9dbcdeb2be1c49d0c147eb00f51e3.
- Zip central directory read via Range requests: 5 entries - Setup.exe (4,217,618 B) + Data01.dxn (11,131,847,685 B) + Data02.dxn (281,302,906 B) + Data03.dxn (21,008,297 B). Data01.dxn header bytes contain FreeArc signature ("ArC\x01", block type "storing") => .dxn = FreeArc archives. Game .paks are inside; extraction needs FreeArc tooling (PeaZip-bundled arc / unarc under Wine) + ~12-25 GB workspace - deferred until space staged.
- SCV on IA: soulcalibur-v-bljs-10115, 7,557,336,316 B RAR (PS3 JP full disc) - complete copy, NOT downloaded (disk).
- SCIV on IA: soul-calibur-iv-RPCS3 4,916,231,864 B zip "DLC + ONLINE" (contents unverified - may be DLC-only); soul-calibur-iv-usa-all-dlc-pack-fix-blus-30160 = DLC pkgs only (99,452,669 B), NOT the base game.
- Other IA SC software surfaced: SCII HD Online (360), SCIII Definitive Edition v1.20, SC Broken Destiny PSP, Soul Edge arcade, SC1 (DC/Android/iOS), SC Legends Wii.
- Disk at start: 104G used / 45G free (df); quota wall ~119G. Whole-zip on disk + extract does NOT fit safely => streaming store: curl | tee(md5,sha1) | 1.9GB chunker, parts uploaded to GRE+WH releases and deleted as verified. Peak ~2 parts (~3.8G).

## Storage pipeline
- [ ] SCVI parts -> GRE release soulcalibur6-archiveorg-20261106
- [ ] SCVI parts -> WH release soulcalibur6-archiveorg-20261106
- [ ] whole-file md5/sha1 verified vs IA metadata
- [ ] pull-back verify 1 part per repo
- [ ] manifest + docs PRs

## Landings (2026-11-06 ~18:39-18:45 CST)
- GRE PR #83 MERGED 2026-11-07T00:43:32Z (7d20d701): soulcalibur/HOLDINGS-INDEX-2026-11-06.md
- WH PR #1616 MERGED 2026-11-07T00:39:14Z (73e082ca): teardown/soulcalibur-6/HOLDINGS-INDEX-2026-11-06.md + TEARDOWN.md status correction (NOT YET ACQUIRED -> ACQUIRED 2026-11-06)
- S6 READ-BACK: both index docs on main blob 383c09a219ac5d1983cdbd9423da57dd17c17ae7 == local doc. TEARDOWN.md edit verified on main. Known cosmetic flaw: TEARDOWN.md line "...see the holdings index.." has a doubled period (fix on next doc touch).
- Instruction-gate needed 2 body fixes (deviation #ref as #<PR number>; Proof paths backticked + repo-resident only). Final: all WH checks green.

## Storage pipeline state (2026-11-06 ~18:47 CST)
- store2.sh RUNNING detached (setsid, PID 6615 at relaunch). First launch was killed at 00:27:56Z when its launching exec session was reaped (318 MB frozen); relaunched via setsid; all 4 workers RESUMED from exact byte offsets. Aggregate ~1.9 MB/s at last check; ETA ~1.7-2 h for the remaining ~11 GB.
- Design: 7 parts x 1.9 GB (part-06 = 41,266,068 B), 4 parallel range downloads w/ resume loop + disk guard (pause >124 GB used), per-part sha256 -> upload BOTH releases -> API digest verify -> local delete. On completion: MANIFEST-scvi-parts.json + full pull-back md5/sha1 verification (verify_pullback.py, streamed, zero disk) -> VERIFY-PULLBACK.json on both releases + STORE2_DONE marker in this folder.
- Chain pre-proven by a 20 MB smoke asset: sha256 == API digest on BOTH repos (then deleted).
- RESUME COMMAND if the pipeline dies: cd ~/workspace/_soulcalibur-hunt-20261106/scvi && setsid nohup bash store2.sh > store2-run.log 2>&1 < /dev/null &
- Extraction NOT started: .dxn = FreeArc; needs FreeArc tooling (PeaZip-bundled arc / unarc) + ~12-25 GB staged workspace. First target when it runs: guard/stamina system data for the WH BT-guard design.
