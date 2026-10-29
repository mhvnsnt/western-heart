# Teardown wiring standard + completion gates for the unfinished games — 2026-10-20

> Owner instruction (verbatim): "do some deep research on what we need to do to get these full tear down files and everything wired up correctly and stop hand tooling and bullshitting."
> Companion research: game-reverse-engineering `docs/research/teardown-completion-2026-10-20/` — one doc per game with the sourced tool/format research and pull-in logs behind every gate below.

## The wiring standard (from the four finished games)

The four complete teardowns — Tekken 3 (western-heart PR #382), WWF No Mercy (#379), WMXIX (#374), Eastern Mind (#375), with the independent audit in PR #385 (`docs/FULL-WIRING-VERIFICATION-2026-10-20.md`) — set the pattern every game below must follow:

1. **Complete file inventory** in `teardown/<game>/WIRING-INVENTORY.md` — every extracted file, no sampling. (WMXIX's inventory ran to 1,708 files; Tekken 3's wiring moved 13 banks + 5,663 moves.)
2. **WIRED with path evidence, or FLAGGED with a named reason** — every inventory line ends in one of those two states. "Wired" names the consuming path (game code, `moveset-library/`, `customization/`, stage registry); "flagged" names why not.
3. **Canon conversion is logged, never silent** — `teardown/<game>/CANON-CONVERSION.md` plus `CANON.md` / `RENAME-MAP.md` entries for every third-party name converted to Western Heart canon; unmapped identities are flagged, never invented.
4. **Moves/animations land as data with Tekken inputs** — moveset-library JSON + animation indexes, renamed and lightly cleaned at industry standard, never degraded.
5. **Independent verification before "complete"** — a separate pass re-walks the inventory (the #385 pattern). A lane's own claim is not verification. The DOA4 audit (PR #381) killing a false "complete" flag is the standing lesson.
6. **Automated gates where the format allows** — import-verify for models (DOA4 PR #386: 165 GLBs import-verified), playback checks for animation, structural validation for decryption. Each game doc below defines its gates explicitly.

## Cross-cutting conclusions (read these first)

1. **For six of the eight games, no public format spec or ready tool exists** (Urban Reign, Tekken 6 PSP, DOA4, SF EX's PAC, Tekken 5's DATA0, TTT2's PS3 containers). This was established by targeted searches across GitHub, QuickBMS/ZenHAX, XeNTaX/ResHax, Noesis plugin indexes, and community wikis — and it is reported as a finding, not an excuse. Anyone claiming a ready-made tool for these must produce a URL. Progress on them is *method*, not downloads.
2. **The proven PS2 method is dynamic-first.** Urban Reign, Tekken 5, and SF EX converge on the same pattern: emulator ground truth (PCSX2 / PCSX-Redux RAM dumps, data breakpoints, GPU capture) *before or alongside* static Ghidra work. Bind matrices that are computed at load time and deobfuscators that hide in overlays are found by watching the game run — not by fitting formulas to ciphertext.
3. **Research corrected five standing premises** (details in the game docs):
   - SCII models are **OLK -> PKG -> VMX**, not loose .mdl/BIN files.
   - TTT2's "NUD/NUDP family" is **unverified** — every NUD source found is Smash Bros (Wii U), a different Namco title.
   - Tekken 5's "NUDP" is **unverified** — no NUDP spec or plugin exists in any discoverable source, for any game.
   - DOA4's AFS does **not** match the public CRI AFS profile (an audio archive format); no public spec covers its encryption.
   - Def Jam compression is **per-file RefPack inside an uncompressed container**; JDLZ has no sourced link to the game.
   - Tekken 6 PSP's distance formula is **published nowhere** — it must be recovered by PPSSPP observation (a proven method), not found.
4. **Two layers are solved today:** Def Jam's containers (unvivtool / pyBIG / QuickBMS script — maintained, open-license) and TTT2's restart (hash-ledger + 7-Zip multi-volume + PS3 identity check). SCII's container chain + importer also exist, as legacy WIP tooling whose repair step is the real work.
5. **Every game gets falsifiable completion gates** (in its doc): oracle tests, structural validation, dual-parser agreement, ground-truth diffs, import-verify counts. Gates exist so "complete" is a test result, not a claim — the DOA4 lesson, generalized.
6. **License honesty:** several load-bearing items have unstated or unverified licenses (legacy forum attachments; the Ghidra Emotion Engine extension; the Allegrex module). They are recorded as UNVERIFIED in the pull-in logs, with the lane's first action being to open the repo and record the license. Nothing non-open was pulled into this repo; openly-licensed Python tooling is pulled via pip at lane runtime (the distribution channel), and that choice is stated per item.


---

## Urban Reign (PS2) — bind matrices + per-vertex bone assignment

**Gap:** Bind matrices + per-vertex bone assignment for skinned models (mesh topology already cracked: non-indexed triangle lists; SLUS_212.09 loader route)
**Serves lane:** Teardown completion sweep — Urban Reign lane (closest to done, ~95%)

## What "wired correctly" means for Urban Reign (WH standard)

Following the four merged games (western-heart PRs #374/#375/#379/#382, verification #385): a `teardown/urban-reign/WIRING-INVENTORY.md` covering **every** extracted file; each model **WIRED** with path evidence (the game/moveset-library path that consumes it) or **FLAGGED** with a named reason; a `CANON-CONVERSION.md` plus `RENAME-MAP.md` entries for every renamed fighter/move; a stage-registry entry; and an independent verification pass before any "complete" claim.

**Completion gates (all must pass):**
- **G1 Palette truth:** palette count derived from the loader == palette count in the PCSX2 RAM capture.
- **G2 Index sanity:** every per-vertex bone index resolves in range through the proven indexing formula (the 27-entry vs max-index-54 question answered by the loader's own arithmetic and recorded — never assumed).
- **G3 Bind check:** inverse(bind) x bind == identity **and** skinned bind-pose vertices reproduce the already-cracked non-indexed triangle positions.
- **G4 Import-verify:** every exported GLB imports clean in Blender with skeleton + weights (bone count > 0, weights normalized).
- **G5 Stance check:** bind-pose render matches the game's stance reference (own-eyes check, per operation standard).

If G1–G3 fail, the captured matrices are pose matrices, not bind matrices — recapture at load time. Do not wire.


---

## Tekken 6 PSP — decrypt6 distance formula + GMO conversion

**Gap:** The dynamic-block distance formula in the data decryption; full COM/GMO -> GLB conversion (40 character meshes in 18 COM files)
**Serves lane:** Teardown completion sweep — Tekken 6 PSP lane (~90%)

## What "wired correctly" means for Tekken 6 PSP (WH standard)

Same template as the four merged games: `WIRING-INVENTORY.md` covering all 40 characters / 18 COM files with per-file status; WIRED-with-path-evidence or FLAGGED-with-reason per file; canon conversion + `RENAME-MAP.md` discipline; independent verification before "complete".

**Completion gates (all must pass):**
- **G1 Decryption proof:** the candidate distance formula + decrypt verifies on **two or more previously unseen files** via known-plaintext anchors (GMO header magic). A fit to ciphertext alone never passes.
- **G2 Trace evidence:** a PPSSPP debugger log of (block index, file offset, size) for one known file is archived with the decoder, and the formula reproduces the observed offsets exactly.
- **G3 Import-verify:** every GMO->GLB imports clean; skeleton present (bones > 0) and weights normalized for skinned characters. A geometry-only GLB is FLAGGED "weights pending" — never reported done.
- **G4 Inventory completeness:** 40/40 characters listed with status before the game is called wired.


---

## Dead or Alive 4 (Xbox 360) — keystream verification, chrthree, animations, skeletons

**Gap:** AFS keystream verification on full payloads; chrthree remaining 25 tables; anm.afs animations; skeletons + skin weights
**Serves lane:** Teardown completion sweep — DOA4 lane (verify-first; a prior 'complete' claim was audit-killed)

## What "wired correctly" means for DOA4 (WH standard)

Same template as the four merged games, with one hard precondition the other games did not need: **no wiring claim of any kind stands until the keystream is proven on full payloads.** The audit (western-heart PR #381) already killed one false "complete" claim on this game; the gates below are how that never happens again.

**Completion gates (all must pass):**
- **G1 Keystream proof:** the five-oracle protocol in this doc (texture / table / animation / cross-container / entropy) passes on **full payloads** for all six containers (anm, chrone, chrtwo, chrthree, mot, stg). Header-only evidence = FAIL.
- **G2 chrthree completeness:** 75/75 tables converted, with the 25-table decrypted-byte diff documented in the teardown doc.
- **G3 Skeleton/weights:** the lane-authored Noesis plugin exports a real skeleton; Blender pose test passes without distortion on sampled models.
- **G4 Animation:** anm.afs clips play (idle loop smooth) on their chr skeletons.
- **G5 Reproducibility:** the proven decryption is published as a QuickBMS `.bms` in this repo's tools, and extraction reproduces from the `.bms` alone.
- **G6 Import-verify count:** GLB import-verified total reaches the full model count (baseline: western-heart PR #386, 165 import-verified) before any completion claim.


---

## Def Jam: Fight for NY (PS2) — ISO completion + EA BIG/VIV extraction

**Gap:** Complete the ISO (~31.5% downloaded); full extraction of every container incl. WRES_ALL.VIV (EA BIG family)
**Serves lane:** Teardown completion sweep — Def Jam lane

## What "wired correctly" means for Def Jam: Fight for NY (WH standard)

Same template as the four merged games, applied in container order: the teardown's `WIRING-INVENTORY.md` is built from the complete ISO manifest; every inner file ends WIRED with path evidence or FLAGGED with a named reason; the 142-fighter / 48-venue documentation already merged (western-heart PR #216) gets its underlying files wired, not just described.

**Completion gates (all must pass):**
- **G1 ISO integrity:** SHA1 `5eda39dfd703804c8734b91bd23039f642317837` **and** MD5 `44ae0340a72c65f94359057ad16c4ba2` match the archive.org metadata exactly; size 4,694,573,056 bytes.
- **G2 Manifest first:** the complete ISO file inventory (every path + size) is committed before any container is opened.
- **G3 Dual-parser rule:** every container's extraction agrees across two independent parsers (unvivtool + QuickBMS script, or pyBIG); disagreements are FLAGGED with the differing file list, never silently resolved.
- **G4 Probe before claims:** WRES_ALL.VIV — and every VIV — has a recorded `get_info()` probe (magic variant, entry count, filenames) before ANY statement about its contents appears in a doc or report.
- **G5 Compression pass logged:** per-file RefPack check results recorded; non-RefPack compressed files identified from comtype-scanner output. No JDLZ claim without header evidence.


---

## Soulcalibur II — fighter models (OLK -> PKG -> VMX)

**Gap:** Fighter models from the Xbox source: the container chain, VMX import, and the proven skeleton/weight repair bottleneck
**Serves lane:** Teardown completion sweep — SCII lane (~60%)

## What "wired correctly" means for Soulcalibur II (WH standard)

Same template as the four merged games: `WIRING-INVENTORY.md` covering every PKG/VMX; per-fighter status; canon conversion for the roster; verification before "complete". For this game the inventory unit is the VMX file, and the repair log is part of the wiring evidence — the community record proves repair is normal, so an undocumented "clean" conversion is treated as unverified.

**Completion gates (all must pass):**
- **G1 Concordance:** Xbox PKG numbering validated against the documented index table (437/445 = Nightmare P1) on the FIRST package before mass conversion; any Xbox delta mapped and recorded.
- **G2 Repair log:** every fighter's skeleton/weight/texture repairs recorded per file. (Repair is the proven bottleneck, not an embarrassment to hide.)
- **G3 Import-verify:** GLB imports clean in Blender; skeleton poses without collapse; textures display on an own-eyes front render. UVs reportedly survive import — broken UVs mean wrong file/variant: stop and re-probe, do not hand-fix silently.
- **G4 Platform truth:** Spawn (Xbox-only guest) validated from the Xbox source only; no GameCube/PS2 substitution for Xbox-only content.
- **G5 Inventory completeness:** every PKG/VMX carries a status (converted / repairing / flagged + reason).


---

## Street Fighter EX trilogy — PAC format + loader decode + Ghidra headless fix

**Gap:** PAC vertex/normal/face format completion and the executable loader decode; the Ghidra headless post-script blocker
**Serves lane:** Teardown completion sweep — SF EX lane

## What "wired correctly" means for the SF EX trilogy (WH standard)

Same template as the four merged games, but this teardown is earlier than the others: its first wiring deliverable is a *proven parser*, and no file is called wired until the parser passes ground truth. Per-game inventories will follow the template once conversion starts.

**Completion gates (all must pass):**
- **G1 Pipeline proof:** the Ghidra headless blocker is closed with an artifact — a postScript/PyGhidra run that produces a real output file (function list / decompilation) committed alongside the teardown doc. (Diagnosis order: Jython-disabled-in-12.x -> `-scriptPath` form -> GUI-open project -> log redirection.)
- **G2 Ground-truth validation:** the PAC parser's output for one character **equals** the GPU-capture reconstruction (GTE/GPU capture OBJ): same vertex set, same face connectivity. No wiring before this passes.
- **G3 Format honesty:** GP0-opcode face records and 1.3.12 normals stay labelled HYPOTHESIS until G2 passes with them; the TMD layout is never forced onto PAC.
- **G4 Series separation:** EX2 Plus / EX3 (PS2) are separate formats; PS1 PAC findings do not transfer without their own loader evidence.


---

## Tekken Tag Tournament 2 — verified restart + USRDIR format discovery

**Gap:** Local reassembly lost: restart from release ttt2-7z-v1 (26 chunks, ~13.3GB); PS3 container/model formats are publicly undocumented
**Serves lane:** Teardown completion sweep — TTT2 lane (disk-gated)

## What "wired correctly" means for Tekken Tag Tournament 2 (WH standard)

Same template as the four merged games, with the inventory rebuilt from the reassembled archive: the USRDIR inventory **is** the `WIRING-INVENTORY.md` foundation. Until it exists, every format statement about this game is premature — including ones in older lane notes.

**Completion gates (all must pass):**
- **G1 Integrity ledger:** all 26 chunks SHA-256-verified against the release manifest **before** joining; the `7z t` log archived with the ledger. If the release has no manifest, that gap is FLAGGED and hashes recorded on first download — never back-filled silently later.
- **G2 Platform identity:** the reassembled tree is confirmed PS3 (`PS3_GAME/USRDIR` + a GameID from the RPCS3 list) before any format claim; Wii U content reroutes to the proven Wii U branches.
- **G3 Magic-first:** the USRDIR inventory records magic bytes for the largest BIN/DAT files; **no format name** (NUD / NUDP / NTX / NUS3) may appear in any doc or claim without a magic citation from this inventory.
- **G4 Container honesty:** a failed generic extraction is recorded as "unidentified container", never "encrypted" — no sourced TTT2 encryption exists.
- **G5 Inventory completeness:** every USRDIR file carries a status before the restart is called complete.


---

## Tekken 5 (PS2) — TK5DATA0.BIN deobfuscation

**Gap:** TK5DATA0.BIN (2,072,586,240 bytes, entropy 8.00) holds character/model/stage data behind an unidentified deobfuscator; model format unidentified until plaintext exists
**Serves lane:** Tekken 5 finisher lane (coordinator phase complete; this is its blocker)

## What "wired correctly" means for Tekken 5 (WH standard)

Same template as the four merged games once DATA0 opens (the TK5DATA5 extraction and the E7 release already follow it). Until then, this game's wiring deliverable is *proven plaintext access*, and the gates below police the difference between access and speculation — the failure mode this teardown cannot afford is a confident format claim built on an unproven decrypt.

**Completion gates (all must pass):**
- **G1 Classification first:** every E0–E9 overlay classified (EE ELF / raw EE overlay / IOP IRX) with header evidence before any further static claim; IRX files are never EE-disassembled.
- **G2 Plaintext ground truth:** a PCSX2 RAM-diff pair (title vs in-match) is archived; post-decryption regions identified by magic scan (TIM2 / VIF-GIF / ASCII). The hunt proceeds from observed plaintext, not cipher speculation.
- **G3 Loader identity:** the deobfuscator is identified by a write-breakpoint PC, recorded with its registers — not by elimination across E5/E6.
- **G4 Structural validation only:** any candidate keystream/decrypt passes on structure (valid ELF or TIM2 header; monotonic index table whose sizes sum to the file size; disassemblable MIPS). Entropy reduction alone NEVER passes.
- **G5 No format assumptions:** the first real plaintext gets a magic-hunt report; a format name ("NUDP" or any other) is used only after its magic is observed in actual plaintext.
- **G6 Crib-drag scope:** E0^E1 results are reported as two-time-pad evidence only; a null result is recorded as "not a shared-offset pad" — nothing more.
