# Urban Reign Redux — INVENTORY (got it, via the author's own GitHub release)

**Date:** 2026-11-08 ~01:55 CST
**Folder:** `~/workspace/urban-reign-redux/`

## What this is — read this first

The **all-in-one ZIP (2.67 GB, SHA-256 `9b0c94b6…`) was NOT found anywhere else.** No mirror of it exists on the open web (see "Alternate links tried" below). The author's Drive link is still quota-blocked (re-checked 2026-11-08 ~01:52 — still "Quota exceeded"). The scheduled retry for tomorrow evening (Sun Nov 8 ~7:18 PM CST) stays as the backup for the all-in-one.

What **IS** on disk now, downloaded and hash-verified, is the **same v0.5 release from the author's own GitHub release page** — the Mod Manager + Editor. The Mod Manager builds the **byte-identical 0.5 disc** from Jay's own Urban Reign (USA) ISO (already in the repo as release `urban-reign-iso-v1`), per the author's release notes: "with no extra fighter packs the disc is identical to the tested 0.5 release (game CRC 74E78599)". The only thing missing vs the all-in-one is the ready-made ISO itself — and Jay already owns that disc.

**Caveat:** the Launcher is a Windows .exe. The build step (point it at the ISO + PCSX2 folder, press "Build modded disc") runs on Windows, not on this Linux VM. The files are here now; the build runs where Jay runs PCSX2.

## Files on disk (verified)

### 1. `Urban.Reign.Redux.Mod.Manager.0.5.V97.zip`
- **Source:** https://github.com/Jasonafex/urban-reign-redux/releases/download/v0.5.0/Urban.Reign.Redux.Mod.Manager.0.5.V97.zip (v0.5.0 release, Oct 28 2026, asset from the author)
- **Size:** 1,176,180,939 bytes (~1.10 GiB)
- **SHA-256:** `ad222bad1d0cd1a03672bc88e0132e63ceb15ce0129a406b69b925ceb2f0f6d6` — **MATCHES** the author's published Mod Manager zip hash (release notes) and the GitHub asset digest
- **Contents (71 files, 1,176,284,403 bytes uncompressed):**
  - `Urban Reign Redux Launcher.exe` (411,136 B) — the Mod Manager launcher (Windows)
  - `mods/Urban Reign Redux 0.5 V97.urmod` (388,029,599 B) — the core 0.5 mod payload (fighters, movesets, sounds, stages)
  - `mods/Urban Reign Redux 0.5 V97 HD textures.urmod` (144,430,980 B) — HD texture pack (main set)
  - `mods/Urban Reign Redux 0.5 V97 HD textures, full set.urmod` (624,958,499 B) — HD texture pack (full set)
  - `config/portraits/` — 34 fighter portraits: Armor Queen, Asuka, Baek, Bob, Bruce, Bryan, CJ, Cammy, Christie, Devil Jin, Dragunov, Eddy, Feng, Heihachi, Hwoarang, Jack, Jeff, Jin, Kazuya, King, Kiryu, Kunimitsu, Leon, Marduk, Nina, Paul, Reina, Renamon, Ricardo, Snake, Steve, Vergence, Violet, Yoshimitsu
  - `config/fight/` — 19 files: Brad + Golem fight-scene PNGs (idle/punch/kick/dodge/damage/block/slam/walk/taunt/laugh/axe), `gates.png`, `clips.json`
  - `config/sounds/` — close.mp3, error.mp3, success.mp3; `config/ui/` — 3 files; `config/redux.ico`
  - `guide/` — index.html + 4 step JPGs (1-start, 2-fighter, 3-hd, 4-build)
  - `README.txt`, `SHA256SUMS.json` (per-file checksums inside the zip)
- **Use:** unzip anywhere (needs ~5 GB free next to the ISO), open the Launcher, point it at Jay's own Urban Reign (USA) ISO + PCSX2 folder, tick the packs, press "Build modded disc". Output: `<ISO name>-redux-0.5.iso`, fresh-boot in PCSX2. The ISO is read only, never changed (Clone mode).

### 2. `Urban.Reign.Redux.Editor.0.5.zip`
- **Source:** https://github.com/Jasonafex/urban-reign-redux/releases/download/v0.5.0/Urban.Reign.Redux.Editor.0.5.zip (same v0.5.0 release)
- **Size:** 54,476,021 bytes (~52 MB)
- **SHA-256:** `883387a9d3b78e7c38270697dfe46ddc72dc4958b062bbdb7e1c86f32cc3f7ef` — **MATCHES** the GitHub asset digest
- **Contents (1,081 files, 150,974,503 bytes uncompressed):**
  - `Urban Reign Redux Editor.exe` + full Python 3.10 runtime (`Runtime/`)
  - `Source/editor/` (36 files) — the editor itself
  - `Source/vendor/roster-lib/` (87 files) — the mod-making tooling: `gyu_decode.py`, `gyu_structure.py`, `vmd_mesh.py`, `vmd_structure.py`, `ppk_index.py`, `texture.py`, `gs_texture.py`, `retime.py`, `bind.py`, `render_stream.py`, `stage_preview.py`, `gyu_byte_tables.json`, `gyu_codec12_tables.bin`, and more
  - `Source/web/` (15 files: app.js, iso.js, porting.js, viewport.js, tutorial.js, index.html, app.css), `Source/data/` (4 files)
  - `README.txt`, `VERSIONS.json`, `Runtime/LICENSE.txt`

## All-in-one status (still owed)

- **All-in-one ZIP:** NOT downloaded. Expected ~2.67 GB, SHA-256 `9b0c94b67b2ddd2415a6dddfe1f4385db64461541770d52525a81b984036ba2f`, disc SHA-256 `cc2312c1909cec438b8971133445eb7e2bfc7eecf03bdd0fed01cbefd7134541`.
- **Author's Drive link:** https://drive.google.com/file/d/1anZDvW-zTK52fi4HEZLxqO-3OlE2e1Wl/view — re-checked 2026-11-08 ~01:52, still "Google Drive - Quota exceeded". Retry scheduled Sun Nov 8 ~7:18 PM CST (job `urban-reign-redux-retry`).

## Alternate links tried (every one)

1. **Author's site** https://jasonafex.github.io/urban-reign-redux/ — only the same Drive link for the all-in-one; Mod Manager/Editor point to the GitHub release (gotten, above).
2. **GitHub releases** https://github.com/Jasonafex/urban-reign-redux/releases — v0.5.0: all-in-one = Drive link only; Mod Manager + Editor are GitHub-hosted assets (gotten, above). v0.4.0: different package (1.75 GB, ZIP SHA `b475e759…`) — **wrong version, not downloaded**.
3. **GitHub forks (3):** EduardtAlbergII/urban-reign-redux — no releases at all. EduardtAlbergI/urban-reign-redux — same person's fork, no releases checked (forks don't carry release assets). skyhelldragon-oss/urban-reign-redux — releases page 404s (fork gone/renamed).
4. **Web search, 5 queries** ("Urban Reign Redux" + download / ModDB / GameBanana / mega / mediafire / mirror / reddit / discord / hash `9b0c94b6…`): **no mirror found anywhere.** Results were only the author's site, the GitHub releases page, YouTube/Facebook/Instagram promo posts (all linking back to the author's site), the unrelated thiagordsfx/urban-reign-recomp PC port (different project, needs your own ISO), and one unrelated MediaFire file ("UnderthesameroofREDUX-Redux0.3-pc.zip", 435 MB — a different game mod, not touched).
5. **Discord:** the Urban Reign Modding Discord is mentioned on the author's site, but joining/asking there needs a sign-in and a human in the server — not doable unattended. Not attempted.
6. **Piracy/ROM/leak sites:** not searched, not used. No commercial ISO downloaded from anywhere — Jay's own USA ISO is already in the repo.

## Follow-on (2026-11-08 ~04:30) — see [URMOD-EXTRACTION-FOLLOWON.md](sandbox://workspace/urban-reign-redux/URMOD-EXTRACTION-FOLLOWON.md)

- Lane 2 re-verified: 8/8 extracted files match their SHA-256 on disk. Total remaining gap across the 50 files: **5,666,960 B (5.40 MiB)**, computed from `extracted/core/fighter_entries.json` — still lives only in the source ISO.
- **New extraction: 34 fighter portraits** (`extracted/portraits/`, 5,651,867 B), **34/34 SHA-verified** against the author's `SHA256SUMS.json`. Flagged, not wired: `Devil Jin.png` (Tekken's Devil Jin — the Devil Within way, not ours, per revised Law 1) and `Jin.png` (Jin Kazama, not the soul) — donor art on disk only.
- **Launcher blockers re-verified:** (a) 32-bit Wine UNRESOLVABLE in-VM via apt — i386 enabled, wine32 candidate exists, install simulation fails on held packages (`pkgProblemResolver` breaks); wine64 alone simulates clean but can't run a 32-bit .NET exe, so it was not installed. (b) No ISO on this VM — repo release `urban-reign-iso-v1` holds it (8 × `urban-reign-500m.part_*`, exactly 4,140,924,928 B; the body's reassembly command names a different prefix — discrepancy flagged). (c) No PCSX2 folder.
- **Wiring: 0 wired** — PS2 PPK/VMD can't load in the game (author's mesh decoder fails on guest VMDs), no movesets extractable, portraits are donor art only. No branch/PR; nothing pushed.
- **Decision owed:** (A) Jay runs the Launcher build on Windows against his own ISO, or (B) supply the repo ISO copy to this VM. The all-in-one Drive retry (Sun Nov 8 ~7:18 PM CST) is a separate route.

## Bottom line

- Redux v0.5 **got now** in the form the author ships on GitHub: Mod Manager (builds the byte-identical disc from Jay's own ISO) + Editor (full mod-making source tooling, including the roster-lib decoders). Both hash-verified.
- The ready-made all-in-one ZIP itself: **no alternate link exists.** Only the author's Drive link, still quota-blocked, retry tomorrow evening.

## Extraction (Lane 2, 2026-11-08 ~02:00–02:50 CST)

Full report: [URMOD-EXTRACTION.md](sandbox://workspace/urban-reign-redux/URMOD-EXTRACTION.md). Method: the author's own tools only (urrpack.py, urrlayout.py, roster-lib `toolnative/`); no hand-written parser; `docs/RULES_NO_GUESSING.md` read first.

- **The .urmod is a diff, not an archive:** 3,639 parts (670,765,056 B, all SHA-verified, 0 bad) cover only **14.56%** of the 4,606,052,352-byte output disc. The rest exists only in Jay's own source ISO (not on this VM, never fetched per lane limits).
- **Fighters found: 29, not 25** — the manifest roster's 23 custom-slotted fighters + 6 in stock slots (Leon, King, Hwoarang, Bryan, Heihachi, CJ). Extra vs the task's list: Baek, Jack, Steve, Violet.
- **Extracted exact bytes (58 of 58 files — COMPLETE 2026-11-08 ~12:00 CST, see the new section at the end of this file):** all 29 fighters' model + package — the 8 from Lane 2 plus the remaining 50 completed from the now-verified source ISO (84,536,860 B). All under `extracted/fighters/<Name>/` with SHA-256 sidecars + `parse.json` (roster-lib parse: PPK members, embedded VMD node counts 46–53, mouth nodes). Per-file SHA-256s in `extracted/fighters/REDUX-0.5-COMPLETION-MANIFEST.json`.
- **Movesets / motion banks: NOT extractable from parts.** Shared GYU banks + pmot/tmot packages are 0% covered (unchanged vanilla); moveset tables in the ELF are 0.2%–50% covered. Decodable only from a built disc.
- **HD textures:** main set 76 PNGs + full set 397 PNGs, all SHA-verified, extracted to `extracted/hd-main/` + `extracted/hd-full/`. Per-fighter mapping owed (needs the mesh/sampler decode; `vmd_mesh.read_mesh` fails on the guest VMDs).
- **Mouth pilot:** all 7 extracted package copies are static (AGO/KUCHI_R/KUCHI_L type 0); Kiryu's loose model is type 3 (moving) → package copy 0, matching the author's static-mouth policy.
- **Launcher build: NOT built.** Wine 9.0 installs and runs, but the Launcher is a 32-bit .NET GUI exe — it needs the 32-bit Wine stack (not installed; no i386 arch enabled) — and there is no ISO and no PCSX2 folder on this VM. The build runs where Jay runs PCSX2 (Windows).
- **Disk quota hit twice** (shared VM quota; filesystem shows 47 GB free). Recovered by deleting this lane's own duplicate unzips + the reproducible `extracted/core/parts/` (re-runnable via `extract_a.py`). The VM is at its quota edge.
- **Repo landing: NOT done** — coordinator's call; nothing pushed, no branch created, main untouched.

## ISO supply attempt (Option B) — STOPPED on disk quota, 2026-11-08 ~05:00 CST

Jay picked Option B ~22:42 ("Send the repo ISO copy to the VM"). Agent `afb8cfd8`.

- **Release assets listed first** (`gh api`): 8 × `urban-reign-500m.part_aa`…`part_ah` — `aa`…`ag` 524,288,000 B each, `ah` 470,908,928 B; sum exactly **4,140,924,928 B** (the source disc size). The stray asset `urban-reign-usa.iso.part_ac` (156,336,128 B) was NOT used — the release body's reassembly command names that prefix but only one part exists under it; the 8-part `500m` series is the one that sums to the full disc.
- **Downloaded one at a time, per-part size verified:** `part_aa` 524,288,000 B ✓, `part_ab` 524,288,000 B ✓, `part_ac` **FAILED** — exact error: `write /home/hatch/workspace/urban-reign-redux/iso/./urban-reign-500m.part_ac: disk quota exceeded`. Partial file left on disk: **302,284,800 B** of 524,288,000.
- **On disk in `iso/`:** 1,350,860,800 B total (aa + ab complete, ac partial). `df` still shows 47G "Avail" — the btrfs subvolume quota is the binding limit, not device free space. The ~4 GB Tekken 5 download was running concurrently.
- **STOPPED per orders:** no retry loop, nothing of Jay's deleted. **No ISO assembled** (needs all 8 parts), **no CRC32 computed**, extraction NOT run — the 50 fighter files remain blocked on the source ISO.
- **Next step is a parent/Jay call:** free quota space (or wait for the concurrent Tekken 5 download to finish) and resume from `part_ac` — the two complete parts are good and need no re-download — or fall back to Option A (Windows Launcher build) / the all-in-one Drive retry Sun Nov 8 ~7:18 PM CST.

## ISO supply RESUME attempt (Option B) — STOPPED on disk quota again, 2026-11-08 ~06:27 CST

Parent re-dispatched the resume (agent `06748eae`) after the quota had apparently freed up — a 1-byte write probe succeeded at ~00:21. Disk check FIRST, per orders: `df -h` showed 47G Avail, and a **100 MB probe write succeeded** (104,857,600 B, then deleted). The probe passing did NOT mean ~3 GB was usable.

- `part_ac` — **524,288,000 B ✓ complete** (downloaded this lane, 06:24). On disk now: aa + ab + ac = **1,572,864,000 B**.
- `part_ad` — **FAILED** — exact error: `write /home/hatch/workspace/urban-reign-redux/iso/./urban-reign-500m.part_ad: disk quota exceeded`. Partial reached **470,290,432 B** of 524,288,000 before failing. The partial was deleted by this lane (its own failed download, not Jay's data — 470,290,432 B freed); nothing of Jay's deleted.
- **STOPPED per orders:** no retry loop. **No ISO assembled** (have 3 of 8 parts), **no CRC32 computed**, extraction NOT run — the 50 fighter files remain blocked on the source ISO.
- **What this proves about the quota:** the btrfs subvolume quota is the binding limit, not device free space (`df` still shows 47G Avail after the failure). A 100 MB probe passing does not predict a 500 MB part landing — this lane wrote ~995 MB after the probe before hitting the wall. The quota edge moves as other work on the VM writes/deletes.
- **Resume is from `part_ad`** once quota is genuinely free — the three complete parts are good and need no re-download. Fallbacks unchanged: Option A (Windows Launcher build) or the all-in-one Drive retry Sun Nov 8 ~7:18 PM CST.

## ISO supply COMPLETE + 50 fighter files extracted — 2026-11-08 ~12:00 CST

Quota freed (~11:27 CST, WRITE_OK verified); this lane resumed from `part_ad` and finished the set. Downloads via `gh release download` (release `urban-reign-iso-v1`), one part at a time, size-verified immediately:

- `part_ad` — 524,288,000 B ✓ (17:30), `part_ae` — 524,288,000 B ✓ (17:35), `part_af` — 524,288,000 B ✓ (17:43), `part_ag` — 524,288,000 B ✓ (17:50), `part_ah` — 470,908,928 B ✓ (17:56). All 8 parts on disk in `iso/`.
- Assembled `iso/urban-reign-usa.iso`: **4,140,924,928 B** exactly.
- **CRC32 CORRECTION (measured this lane):** `74E78599` is the PCSX2 *game* CRC (`pcsx2_crc` in the core manifest), NOT the whole-ISO CRC32 — the earlier record's "Target CRC32 74E78599" framing was wrong. Measured: whole-ISO CRC32 = `87803691`; `SLUS_212.09` CRC32 = `58F4F090`. The authoritative check is SHA-256: assembled ISO = `c22209eefcdc4275a75dc3656b4abf5807940155236916271e19455d302a8ec2` — **MATCHES the author's `source_sha256` exactly**. The ISO is byte-identical to the author's source disc.
- ISO9660 structure verified with the DW lane's stdlib extractor: SYSTEM.CNF, `SLUS_212.09` (6,366,044 B), IRX dir, `DVD001.AFS` (1,258,674,176 B), `DVD000.AFS` (1,077,082,112 B).

**50 fighter files — 50/50 COMPLETE** (`assemble_fighters.py`; per-file SHA-256s in `extracted/fighters/REDUX-0.5-COMPLETION-MANIFEST.json`, 84,536,860 B total):

- Method: each file assembled from the SHA-verified .urmod parts (re-extracted this lane via `extract_a.py` — the `mods/` dir was empty after Lane 2's quota cleanup; the core .urmod was re-extracted from the Mod Manager zip, parts **0 bad**) plus gap bytes read from the verified source ISO via the manifest's copy records. **0 uncovered gap ranges** — every gap byte has a copy record. No gap was filled, zero-padded, or guessed.
- **Copies-field CORRECTION (measured this lane):** the manifest stores copies as `[output_offset, source_offset, length]` — NOT `[src, dst, length]` as `extract_a.py`'s docstring says. Proof: with `[dst, src, len]`, parts+copies tile the output disc exactly (merged coverage 4,606,052,352 B, 0 holes, 0 overlap, 1 interval; max copy src+len 4,140,806,144 stays inside the source ISO). With the docstring's order, 5,841 copies read past the end of the source ISO and 409,282,560 B of holes appear. `build_output_disc.py` and `assemble_fighters.py` both use the corrected order.
- Validation: the 8 Lane 2 files re-hashed — **8/8 still match** their recorded SHAs. All 50 new files parsed with the author's own roster-lib tools (`extract_d.py` re-run): **29 models + 29 packages, 0 errors** (VMD node counts 46–53, embedded VMDs in packages, mouth nodes as Lane 2 found).
- Honest limit on verification: the author's `SHA256SUMS.json` (70 entries) contains **no fighter VMD/PPK hashes** (Launcher.exe + config PNGs only), so there is no per-file author hash to compare against. The proof chain is: per-part SHA-256 (author manifest) + whole-ISO SHA-256 (author `source_sha256`) + copy-map tiling (0 holes, 0 overlap). The full output-disc SHA check (`output_sha256` cc2312c1…) is still owed — it needs a 4.6 GB write.
- **Full output-disc build attempted, died on quota:** `build_output_disc.py` wrote all 3,639 parts, then hit `OSError: [Errno 122] Disk quota exceeded` during the copies phase. The partial disc (this lane's own file) was deleted at once; nothing of Jay's touched. The per-file assembly (~70 MB of writes) was used instead. The quota edge moves — the 4.6 GB build is retryable when quota is genuinely free, and the parts + ISO on disk stay valid.

**Still blocked, unchanged:** movesets/banks need a built disc (full output-disc build — retryable from the verified parts + ISO when quota allows — or the Windows Launcher on Jay's machine) or the all-in-one (Drive retry cron Sun Nov 8 ~7:18 PM CST). The 50 fighter files are extracted but NOT wired into the game — the author's `vmd_mesh.read_mesh` fails on these guest VMDs (Lane 2 §4), so no mesh → no GLB → nothing to wire; no hand-written replacement per the industry-standard-only rule. Nothing pushed, no branch created, main untouched.
