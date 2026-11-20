# Urban Reign Redux — extraction follow-on (Lane 2 leftovers)

**Date:** 2026-11-08 ~04:30 CST
**Prior work:** [URMOD-EXTRACTION.md](sandbox://workspace/urban-reign-redux/URMOD-EXTRACTION.md) (Lane 2, 2026-11-08 ~02:00–02:50). This lane builds on it — nothing in Lane 2 was redone.
**Method:** the author's own tools only (Mod Manager zip, `SHA256SUMS.json`, roster-lib `toolnative/`); no hand-written parser; no gap-filling, no guessing. Canon laws applied (REVISED Law 1, Jay 2026-11-07 ~22:32): the word "Devil" MAY appear — but ONLY written in OUR own way and language, NEVER in the Devil Within way (never Tekken's Devil Jin / Devil Gene sense); "Jin" only ever means the soul JIN (刃).

## 1. Re-verification of Lane 2 (done first)

All 8 extracted fighter files re-hashed on disk — **8/8 match Lane 2's reported SHA-256 exactly** (Asuka, CJ, Hwoarang, King, Paul, Vergence packages; Kiryu model + package). `extracted/core/fighter_entries.json` re-read: 8 files extracted, **50 still missing**, total gap bytes **5,666,960 B (5.40 MiB)** — computed from the file, not hand-added. Largest gaps: Leon package 925,696 B, Leon model 903,168 B, Renamon model 485,376 B, Bob model/package 460,800 B each.

## 2. New extraction this lane — 34 fighter portraits (all SHA-verified)

The 34 portraits live inside the Mod Manager zip (`Urban Reign Redux Mod Manager 0.5/config/portraits/`, 34 PNGs). Extracted to `extracted/portraits/` + `MANIFEST.json`. Verified against the author's own `SHA256SUMS.json` (70 entries, `{file, bytes, sha256}`): **34 OK, 0 bad, 0 missing-sum. Total 5,651,867 B.**

- Asuka, Baek, Bob, Bruce, Bryan, CJ, Cammy, Christie, Dragunov, Eddy, Feng, Heihachi, Hwoarang, Jack, Jeff, Kazuya, King, Kiryu, Kunimitsu, Leon, Marduk, Nina, Paul, Reina, Renamon, Ricardo, Snake, Steve, Vergence, Violet, Yoshimitsu, Armor Queen — 32 portraits, donor art, no canon conflict.
- **FLAGGED, not wired:** `Devil Jin.png` and `Jin.png`. The first is Tekken's Devil Jin — the Devil Within way, so it cannot be used under that name (revised Law 1: "Devil" only in our own way/language, never the Devil Within way); a canon-safe name for it would be a proposal for Jay. The second is Jin Kazama, not the soul JIN. Both sit on disk as extracted donor art only — neither was wired into the game under its source name, and no canon name was invented for them. Jay's call owed if either is ever used as template art.

## 3. The remaining 50 fighter files — still blocked, exact cause

**Not extractable without the source ISO.** The .urmod is a diff: the 50 files are 81.3%–99.9% covered (Leon 34.5%/42.3%), and the missing **5,666,960 B** exist only in Jay's own Urban Reign (USA) source ISO, which is not on this VM. No gap was filled, zero-padded, or guessed — a file with invented bytes is not the file. Per-file gaps are in `extracted/core/fighter_entries.json` (exact byte ranges per file).

## 4. Movesets / banks — still 0% extractable from parts

Unchanged from Lane 2: shared GYU banks + pmot/tmot packages are 0% covered (unchanged vanilla); moveset tables in the ELF are 0.2%–50% covered in their first 64 KB. Decodable only from a built disc with the Editor's `moveset.py`. No moveset data exists on this VM to wire into the template library — Redux stays a pending-ingest row there.

## 5. Launcher build — the 3 blockers, re-verified with exact current state

**The disc was NOT built. No build was claimed.**

1. **32-bit Wine — UNRESOLVABLE in-VM via apt (this lane's finding).** State now: `wine64` is GONE (the runtime restart wiped /usr — system installs are ephemeral). This lane enabled the i386 foreign architecture (`dpkg --add-architecture i386`, now shows `i386`) and ran `apt-get update` clean (62.9 MB of lists). `wine32:i386` candidate exists (9.0~repack-4build3). But the install simulation **FAILS**: `E: Error, pkgProblemResolver::Resolve generated breaks, this may be caused by held packages` (libreoffice chains, `login` PreDepends libpam-runtime/modules, `util-linux` PreDepends libsystemd0, `libzstd1` not installable). `wine64` alone simulates clean (1 package) but is useless — the Launcher is a 32-bit .NET/Mono GUI exe and cannot run under wine64 alone. `wine64` was deliberately NOT installed (spending disk on a quota-edge VM for a component that unblocks nothing). Blocker (a) stands.
2. **No ISO on this VM.** The repo DOES hold Jay's ISO — release **`urban-reign-iso-v1`** ("Urban Reign (USA) ISO", 3.9 GB). Assets: `urban-reign-500m.part_aa` … `part_ah` — 8 parts totaling **exactly 4,140,924,928 B, the source disc size** (7 × 524,288,000 + 470,908,928). Plus a stray `urban-reign-usa.iso.part_ac` (156,336,128 B). **Discrepancy flagged, not resolved by guessing:** the release body's reassembly command names the `urban-reign-usa.iso.part_*` prefix, of which only `part_ac` exists; the 8-part `500m` series is the one that sums to the full disc. Supplying the ISO = downloading the 8 × 500m parts (~3.85 GiB) and concatenating them in order. NOT downloaded — that is the decision owed, and the VM is at its disk-quota edge (Lane 2 hit quota twice; parent probes show small writes work, a 4 GB download is unproven).
3. **No PCSX2 folder on this VM.** The Launcher also needs a PCSX2 folder (game settings + HD texture install). None exists here, and it expects a Windows PCSX2 install folder — a Linux PCSX2 install is not what it asks for (unproven). Not attempted.

## 6. Wiring into the game — 0 wired, with exact reasons

Nothing was wired into the game this lane, and no branch/PR was opened — there is no code change to land, and opening an empty PR would be staging, not work:

- The 8 extracted files are PS2 PPK/VMD. The game loads GLBs. The author's own mesh decoder (`vmd_mesh.read_mesh`) **fails on these guest VMDs** (Lane 2 §4, author's research decoder, Brad VMD only) — no mesh → no GLB → nothing to wire. No hand-written replacement per the industry-standard-only rule.
- No movesets are extractable, so no Redux templates can be built for the moveset template library (Redux stays pending-ingest).
- The 34 portraits are donor art only. The template library has no portrait field in its data model — wiring them would mean inventing a UI surface. The two flagged-name portraits cannot be wired under source names per the revised canon law (Devil Jin is the Devil Within way; Jin is Jin Kazama, not the soul).
- Repo landing of the extracted game-derived bytes remains the coordinator's call (Lane 2's position, unchanged). Nothing pushed, no branch created, main untouched.

## 7. The exact decision owed (stop point for this piece)

**Option A — Jay runs the Launcher build on Windows** (his PCSX2 machine) against his own ISO: point the Mod Manager Launcher at the ISO + PCSX2 folder, tick the packs, press "Build modded disc". Output `<ISO name>-redux-0.5.iso`. This is the route the pack is designed for. The already-extracted parts + tables stay valid; the build fills the gaps from the source disc.

**Option B — Supply the repo ISO copy to this VM** (release `urban-reign-iso-v1`: 8 × `urban-reign-500m.part_*`, 4,140,924,928 B total, concatenate in order). Then this VM can run the extraction to completion (only ~5.4 MiB of ISO bytes finish the 50 fighter files) and decode movesets/banks from the built disc with the Editor's tools. Blockers that would still remain after (B): the 32-bit Wine install (unresolvable via apt — see §5.1; the build step itself would still need Windows or a working Wine32), and the PCSX2 folder.

**Separate route, already scheduled:** the all-in-one Drive retry cron (Sun Nov 8 ~7:18 PM CST). If the ready-made 2.67 GB all-in-one lands, it IS a built disc — movesets/banks decode directly from it with the Editor's tools, and the Launcher build becomes unnecessary for extraction.

## Files delivered this lane

- `extracted/portraits/` (34 PNGs, 5,651,867 B) + `extracted/portraits/MANIFEST.json` (per-file bytes + SHA-256 + author-match flags, 34/34 match)
- `URMOD-EXTRACTION-FOLLOWON.md` (this file)
- No game-code changes. No branch. No PR. Nothing pushed. Main untouched.

## 8. ISO supply attempt (Option B) — STOPPED on disk quota, 2026-11-08 ~05:00 CST

Jay picked Option B ~22:42. Release assets listed first (`gh api`): 8 × `urban-reign-500m.part_aa`…`part_ah` — `aa`…`ag` 524,288,000 B each, `ah` 470,908,928 B, sum exactly 4,140,924,928 B. Stray asset `urban-reign-usa.iso.part_ac` (156,336,128 B) NOT used (see §5.2 — only one part exists under that prefix).

Downloaded one at a time with per-part size verification: `part_aa` 524,288,000 B ✓, `part_ab` 524,288,000 B ✓, `part_ac` **FAILED** — exact error: `write /home/hatch/workspace/urban-reign-redux/iso/./urban-reign-500m.part_ac: disk quota exceeded`. Partial file on disk: 302,284,800 B of 524,288,000. Total in `iso/`: 1,350,860,800 B. `df` still shows 47G "Avail" — the btrfs subvolume quota is the binding limit; the ~4 GB Tekken 5 download was running concurrently.

**STOPPED per orders — no retry loop, nothing of Jay's deleted.** No ISO assembled (needs all 8 parts), no CRC32 computed (nothing to check against 74E78599 yet), extraction NOT run. The 50 fighter files remain blocked on the source ISO, exactly as in §3. The two complete parts are good and need no re-download; resume is from `part_ac` once quota is free. Movesets/banks blockers (§4–§5) unchanged: no built disc, 32-bit Wine still unresolvable via apt, no PCSX2 folder — no hand-written decoder, per the industry-standard-only rule.

**Canon criterion applied in this lane's records (Jay's ~22:43 correction): SOURCE, not spelling.** `Devil Jin.png` stays flagged because it IS Tekken's Devil Jin (the Tekken way — tied to Jin Kazama / the Tekken mode). DIABLO and his title "The Devil Soul" are our way (Jay's own character, Jay's own words) and lawful as written.

## 9. ISO supply RESUME attempt (Option B) — STOPPED on disk quota again, 2026-11-08 ~06:27 CST

Parent re-dispatched the resume (agent `06748eae`) after the quota had apparently freed up — a 1-byte write probe succeeded at ~00:21. This lane's disk check FIRST, per orders: `df -h /home/hatch` showed 47G Avail, and a **100 MB probe write succeeded** (104,857,600 B written at 43.5 MB/s, then deleted). The probe passing did NOT mean ~3 GB was usable.

Downloaded one at a time with per-part size verification:
- `part_ac` — **524,288,000 B ✓ complete** (downloaded this lane, 06:24). On-disk state now: aa + ab + ac complete = **1,572,864,000 B**.
- `part_ad` — **FAILED** — exact error: `write /home/hatch/workspace/urban-reign-redux/iso/./urban-reign-500m.part_ad: disk quota exceeded`. Partial file reached **470,290,432 B** of 524,288,000 before the write failed. The partial was deleted by this lane (its own failed download, not Jay's data — 470,290,432 B freed); nothing of Jay's deleted.

**STOPPED per orders — no retry loop.** No ISO assembled (needs all 8 parts; have 3), no CRC32 computed (nothing to check against 74E78599 yet), extraction NOT run — the 50 fighter files remain blocked on the source ISO, exactly as in §3. Movesets/banks blockers (§4–§5) unchanged: no built disc, 32-bit Wine still unresolvable via apt, no PCSX2 folder — no hand-written decoder, per the industry-standard-only rule.

**What this proves about the quota:** the btrfs subvolume quota is the binding limit, not device free space (`df` still shows 47G Avail after the failure). A 100 MB probe passing does not predict a 500 MB part landing — this lane wrote 524,288,000 B (ac) + 470,290,432 B (ad partial) = ~995 MB after the probe before hitting the wall. The quota edge moves as other work on the VM writes/deletes; two ~4 GB downloads (Tekken 5 + this ISO) were competing. Resume is from `part_ad` once quota is genuinely free — the three complete parts (aa, ab, ac) are good and need no re-download. Fallbacks unchanged: Option A (Windows Launcher build) or the all-in-one Drive retry Sun Nov 8 ~7:18 PM CST.

Canon law applied: there is NO Jin Kazama in our game at all — the ONLY Jin is the soul JIN (the Blade Soul); the Devil Jin kit is moveset donor data only, never a character. "Devil" only in our own way/language, never the Devil Within way.

## 10. ISO supply COMPLETE + 50 fighter files extracted — 2026-11-08 ~12:00 CST

Quota freed (~11:27 CST, WRITE_OK verified); this lane resumed from `part_ad` and finished the set. Downloads via `gh release download` (release `urban-reign-iso-v1`), one part at a time, size-verified immediately: `part_ad` 524,288,000 B ✓ (17:30), `part_ae` 524,288,000 B ✓ (17:35), `part_af` 524,288,000 B ✓ (17:43), `part_ag` 524,288,000 B ✓ (17:50), `part_ah` 470,908,928 B ✓ (17:56). Assembled `iso/urban-reign-usa.iso`: **4,140,924,928 B** exactly.

**CRC32 CORRECTION (measured this lane — supersedes §3/§8–§9's "nothing to check against 74E78599 yet" framing):** `74E78599` is the PCSX2 *game* CRC (`pcsx2_crc` in the core manifest), NOT the whole-ISO CRC32. Measured: whole-ISO CRC32 = `87803691`; `SLUS_212.09` CRC32 = `58F4F090`. The authoritative check is SHA-256: assembled ISO = `c22209eefcdc4275a75dc3656b4abf5807940155236916271e19455d302a8ec2` — **MATCHES the author's `source_sha256` exactly**. ISO9660 structure verified with the DW lane's stdlib extractor (`iso9660_extract.py`): SYSTEM.CNF, `SLUS_212.09` (6,366,044 B), IRX dir, `DVD001.AFS` (1,258,674,176 B), `DVD000.AFS` (1,077,082,112 B).

**50 fighter files — 50/50 COMPLETE** (`assemble_fighters.py`, 84,536,860 B; per-file SHA-256s in `extracted/fighters/REDUX-0.5-COMPLETION-MANIFEST.json`):

- The `mods/` dir was empty (Lane 2's quota cleanup had deleted the three duplicate .urmod copies); the core .urmod was re-extracted from the Mod Manager zip (source of truth), and the 3,639 parts re-extracted via `extract_a.py` — **0 bad**.
- Each file assembled from SHA-verified parts + gap bytes read from the verified source ISO via the manifest's copy records. **0 uncovered gap ranges.** No gap filled, zero-padded, or guessed.
- **Copies-field CORRECTION (measured this lane):** the manifest stores copies as `[output_offset, source_offset, length]` — NOT `[src, dst, length]` as `extract_a.py`'s docstring says. Proof: with `[dst, src, len]`, parts+copies tile the output disc exactly (merged coverage 4,606,052,352 B, 0 holes, 0 overlap, 1 interval; max copy src+len 4,140,806,144 stays inside the source ISO). With the docstring's order, 5,841 copies read past the end of the source ISO and 409,282,560 B of holes appear. Two earlier bugs this lane came from this: the first assembly run used raw AFS table offsets instead of `DVD000 layout offset + table offset` (caught by the gap assertion before anything was written), and the copy order (caught by the coverage pre-pass + a short ISO read in the streaming hash test `test_hole_semantics.py`).
- Validation: 8/8 Lane 2 files re-hashed, still match. All 50 new files parsed with the author's own roster-lib tools (`extract_d.py` re-run): **29 models + 29 packages, 0 errors**.
- Honest limit: the author's `SHA256SUMS.json` contains **no fighter VMD/PPK hashes**, so there is no per-file author hash to compare against. Proof chain: per-part SHA-256 + whole-ISO SHA-256 + copy-map tiling. The full output-disc SHA check (`output_sha256` cc2312c1…) is still owed — it needs a 4.6 GB write.
- **Full output-disc build attempted, died on quota:** `build_output_disc.py` wrote all 3,639 parts, then hit `OSError: [Errno 122] Disk quota exceeded` during the copies phase. The partial disc (this lane's own file) was deleted at once; nothing of Jay's touched. The per-file assembly (~70 MB of writes) was used instead. Retryable when quota is genuinely free.

**Still blocked, unchanged (§4–§5):** movesets/banks need a built disc (full output-disc build from the verified parts + ISO, or the Windows Launcher on Jay's machine) or the all-in-one (Drive retry cron Sun Nov 8 ~7:18 PM CST). The 50 fighter files are extracted but NOT wired — `vmd_mesh.read_mesh` fails on these guest VMDs, so no mesh → no GLB → nothing to wire; no hand-written replacement per the industry-standard-only rule. Nothing pushed, no branch created, main untouched.

Scripts this lane: `build_output_disc.py` (full-disc build; quota-killed, kept for retry), `assemble_fighters.py` (the per-file completion that worked), `test_hole_semantics.py` (read-only streaming hash test; superseded — the hole question is resolved: with the corrected copy order there are 0 holes).
