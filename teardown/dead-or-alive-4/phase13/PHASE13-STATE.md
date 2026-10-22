# DOA4 Phase 13 — STATE — OPEN 2026-10-22 (FINAL LANE: anime_cm.bin ISO pull → ANM definition layer; 8 unpaired heads via texture/slot evidence; DOA4 closeout)

Branch: `teardown/doa4-phase13-animecm-closeout` (stacked on `teardown/doa4-phase12-anm-handlers`, PR #559 head `86df3aa5`).
Clone: ~/workspace/_doa4p8-clone (sparse, teardown/dead-or-alive-4 only; retargeted from phase 12).
Scratch: ~/workspace/_doa4p2-scratch/p13/.
Repo path note: the task brief says `teardown/doa4/`; the repo's actual path is `teardown/dead-or-alive-4/` (phases 6–12 all live there). Phase 13 follows the repo layout: `teardown/dead-or-alive-4/phase13/`. Wiring inventory lives at `teardown/dead-or-alive-4/phase7/WIRING-INVENTORY.md` (updated in place, Job 4).

## ENVIRONMENT (proven — do not re-derive)
- JAVA_HOME=/home/hatch/workspace/tools/ghidra/jdk-21.0.12.1+1 (NOT on PATH); Ghidra headless needs `-process default_pe.bin`.
- TRUE XEX VA BASE = 0x82000000. Phase-11/12 .text VAs carry +0xE800 PE-frame labels (READER5 frame proof). RAW CAPSTONE is the primary disassembler for XEX code.
- Blender: `xvfb-run -a env -u PYTHONPATH ~/workspace/tools/blender/blender-4.0.2-linux-x64/blender`, Cycles CPU; `glb_sanitize.py` on raw GLBs.
- Disk: ~87% / ~14G free at lane start. ISO plan sized for it (see Job 1). Log every clear here. NEVER delete anything that exists only locally — the ISO + parts are safe in release `doa4-iso-v1`; clearing the local assembled/downloaded copies after verification is the one-store rule and is REQUIRED here.

## INHERITED TRUTH (phases 6–12, verified — do not re-derive)
- Assembly+skinning solved (148 packages / 8,241 meshes; bind reproduction 0.000000). TX2D solved. Texture BINDING declared DYNAMIC-ONLY (terminal, phase 12 — do not re-hunt).
- Heads: attach by node identity; composites 23/31; the 8 UNPAIRED heads are 05, 06, 23, 24, 26, 27, 28, 32 — tested against ALL 148 bodies by the skin-bind Δ method with NO proof (pkg26 min Δ 0.0646, pkg28 min Δ 0.0962 vs the Δ=0.000 bar; six are origin-bound heads untestable by that method).
- ID viewing COMPLETE (chrone/chrtwo/chrthree all viewed; 0 certain names; canon Q1–Q6 OWNER-pending).
- ANM: every XEX-side route exhausted with proven negatives (xref hunt = base artifact; constant scan found the family; the ring/translator is a (tag,key,value) command layer, NOT the record consumer; records don't flow through the ring). anm.afs itself: 27,392 16B records, no container, ch4/ch5 quantized pair, 135 distinct u32. THE ONLY NAMED ROUTE LEFT (ANM-READER5 §4): the per-fighter `.bin` / `anime_cm.bin` DEFINITION LAYER inside the ISO.
- RELEASE FACTS (coordinator-verified 2026-10-22): release `doa4-iso-v1` = 30 assets totaling EXACTLY 7,834,892,288B (parts `doa4-250m.part_NN`, 262,144,000B each ×29 + remainder) = the known assembled ISO size from the original XDVDFS crack (ISO assembled 7,834,892,288B, XDVDFS cracked, 961 AFS files out). Original extraction tooling: `teardown/dead-or-alive-4/tools/extract_iso.py` (XDVDFS partition at file offset 0x390000, magic at 0x3A0000; 14 root files extracted incl. anm.afs 2.9MB) + `tools/afs_extract.py` (standard CRI AFS; 961 files from cmn/spr/snd/avt).

## JOBS
1. THE ISO PULL → DEFINITION FILES: download the 30 parts of release doa4-iso-v1 one at a time into scratch; stream-assemble the ISO (append, verify size, DELETE the part — peak ≈ ISO 7.9GB + one part). Verify assembled ISO: size == 7,834,892,288B exactly + sha256. Extract via the documented XDVDFS tooling (`tools/extract_iso.py`): locate + extract `anime_cm.bin` and the per-fighter `.bin` animation-definition files (and anm.afs if needed). Push extracted definition files to a NEW GitHub release (`doa4-anime-definition-20261022`) + sha256 manifest committed in git — then CLEAR the local ISO (byte-safe in doa4-iso-v1) and log it. If XDVDFS tooling is missing, rebuild it from the documented format (it is not missing — see tools/extract_iso.py).
2. DEFINITION-LAYER ANALYSIS → CLIPS (G4): census anime_cm.bin + per-fighter .bin structure (headers, strides, cross-refs into anm.afs); derive record→stream mapping + 16B field layout FROM THE DEFINITION DATA; implement parser; gate 1 = structural round-trip on anm.afs spans; gate 2 = decode first clips onto a phase-6 skinned GLB skeleton (joint-distance invariant + VIEWED posed render vs bind). Ship parser + clips + ANM-DEFINITION.md. If the definition layer ALSO doesn't yield the mapping: land the complete census + analysis + declare ANM STATICALLY EXHAUSTED with the full evidence chain — that declaration, if earned, is this lane's terminal ANM deliverable.
3. THE 8 UNPAIRED HEADS — NEW EVIDENCE CLASSES: (a) SHARED TEXTURE-RECORD IDENTITY — byte-identical TX2D/XPR2 record hashes shared between a head package and a body package (census the 8 heads × candidate bodies, anchor families first, then full census if cheap). (b) SLOT-GRID ADJACENCY — head slot position within its family block + phase-9 anchor-family assignment. PROOF BAR UNCHANGED: a pairing ships only when combined evidence is unique + quantitative; build composite + VIEWED seated render for any proven pairing. Unproven stays unpaired with matrices landed as evidence.
4. DOA4 CLOSEOUT: `phase13/DOA4-FINAL-STATE.md` — the game's honest final accounting (100% items; terminal-dynamic-only items; owner-pending Q1–Q6). WIRING-INVENTORY final section updated to match. Standalone-readable.

## GATES
- G1 = Job 1 ISO verified (size + sha256) + definition files extracted + pushed to release with manifest.
- G2 = Job 2 census landed (definition-file structure from the data itself).
- G3 = Job 2 parser verdict: mapping + layout proven with round-trip + gated clips, OR the STATICALLY EXHAUSTED declaration with its full evidence chain (no guessed layout either way).
- G4 = Job 3: texture-record overlap matrix + slot-grid test landed; any pairing proven unique+quantitative ships composite + viewed render; unproven stays unpaired.
- G5 = Job 4 closeout doc + WIRING-INVENTORY final section landed.
- G6 = Jobs 0–4 complete + owner canon Q1–Q6 still OWNER-pending (unchanged).

## DISCIPLINE
Additions-only; commit SPECIFIC paths (NEVER git add -A — sparse clone); own-eyes on every render; unique filenames; sanitize before Blender; never delete game files or release assets; the local ISO is a CACHE of release doa4-iso-v1 — verify before clearing, log the clear; never clear extracted definition files until their release push is verified; push every turn; land after every sub-result. Per-character isolation throughout. Collision avoidance: check `git log` on this branch before each job; if the branch moves under me, STOP and reconcile.

## LOG
- 2026-10-22 lane start: PR #559 verified OPEN (base teardown/doa4-phase11-anm-ppcscan, head teardown/doa4-phase12-anm-handlers @86df3aa5); branch `teardown/doa4-phase13-animecm-closeout` created off 86df3aa5; collision check — `git log` on the new branch shows only the inherited #559 history, no foreign commits; this state file landed first, before job work. PR #569 opened (stacked on #559) before job work.
- XEX string census (local `workdir/default_pe.bin`, no download): the definition layer is exactly 25 files — `D:\bin\anime_cm.bin` + 24 fighter `.bin` (sambo, rtm, koryu, gokei, suiken, spartan, tengu, alpha, lisa, boy, ayane, leifang, ninja, hakyo, bass, bayman, hika, genfu, kasumi, ryu, karate, janlee, tina, zack) + `D:\dat\version\anm_version.bin` beside them (file offsets 0x278480–0x278670). The same table carries ~200 `D:\bin\*.mot` names.
- JOB 1 — release verified from the API before any download: `doa4-iso-v1` = 30 assets, sizes sum EXACTLY 7,834,892,288B, per-asset sha256 digests recorded (scratch `p13/`, `/tmp/iso_assets.json` at pull time).
- JOB 1 — part_01 downloaded, VERIFIED: 262,144,000B, sha256 `d51386e4b1e3482c5355ca249033d3445f03ad5c491146dcff4534b5b78c4114` == release digest. It is now `p13/doa4.iso` bytes [0, 262144000).
- JOB 1 — EARLY-DOC OFFSET DISPROVEN: the EXTRACTION-REPORT's "partition at 0x390000, magic at 0x3A0000" does NOT hold for the verified ISO bytes — [0, 262MB) contains NO XDVDFS magic (0x390000 carries DVD-video MPEG data). From part_02's prefix: MAGIC `MICROSOFT*XBOX*MEDIA` sits at the STANDARD XGD2 offset 0x0FDA0000 → partition base 0x0FD90000; root dir = sector 152365, size 2048 → ISO offset ~0x22726800 (inside part_03). The phase-1 extraction's file RESULTS stand (they are mirrored + hash-verified elsewhere); only its offset note was wrong (its tool's brute-force scan is what actually found the partition).
- JOB 3 stage 1 (L1 census) DONE: all 148 packages' XPR2 directories parsed via mirror range-fetches (`phase13/texrecord_census_l1.json`, ~6,000 TX2D records). Controls PERFECT (identical head copies pkg11–16 / 35–40 / 44=45 share 100% of L1 keys). Premise at L1: WEAK — proven heads share layout keys with own-family bodies at the same rate as with other bodies (layout identity ≠ character identity); L2 payload-hash census is the deciding pass (running; chrone-pkg00: 42/42 TX2D hashed, matching phase 7's count).
- JOB 1 — XDVDFS tree COMPLETE (62 entries, `phase13/xdvdfs_tree_full.json`): root (11 files + dic/SOUND/movie dirs) parsed from landed parts; dic/ = 3 IME dictionaries; SOUND/ = 26 audio entries; movie/ = 19 .sfd FMVs (both parsed via verified range fetches of part_15). **There is NO bin/ or dat/ directory and no .bin file in the tree.**
- JOB 1 — parts 02, 03, 04 VERIFIED + landed (sha256 == release digests: 02 def4930d…, 03 1e22b3b5…, 04 294d0259…), part files deleted by the assembler after each write. Landed 4/30 at this log line; assembly continues (part_05 in flight). ISO extraction PROVEN from the assembled bytes: cmn.afs extracted whole (sha256 c7d233337e66290f24d75a05ed9e657d683e37232a63278062538998012a29b9); avt.afs extracted whole (sha256 54c40943ca0304020617fd6a8e0873cb1624f546c8db7a0a01e8317a8e2f1592) and byte-verified against the independent mirror on 3 spans (head / filename block / mid-body).
- JOB 2 — TERMINAL (committed b6273e8): **ANM STATICALLY EXHAUSTED.** The definition files do not exist in the shipped ISO (complete storage census: XDVDFS 62 entries; standard-AFS filename blocks — cmn 7 / snd 201 / avt 700 named, spr 53 by size — contain NO anime/fighter .bin or .mot names; anm/mot are pure data with no name table and, per this phase's whole-file scan, no monotonic offset table at any alignment; the XEX holds only a name registry at 0x82C6B388 with no static volume/offset/size fields and no code materialization). anm.afs's last un-censused regions (sparse-mid 1.25MB, chunk 0x2A1000) are payload, not definitions. Doc: `phase13/ANM-DEFINITION.md` (full chain phases 8–13). G2+G3 landed as the earned declaration; no parser, no clips, no guessed layout.
- JOB 3 — descriptor-level preview (from the L1 census's desc_sha): proven pairs share ~0 full descriptors with their own families (head31's apparent 21/21 was a SELF-match — chrtwo-pkg31 is head31's own package, phase-11's body list mis-included it; analyzer fixed). Unpaired heads share 0–3 descriptors with any family = the proven pairs' noise band. L2 payload matrix is the deciding evidence (census running through chrthree).
- Clears (this lane, own rebuildable intermediates only, logged per discipline):
  - doa4-250m.part_01..04 — deleted by the assembler AFTER sha256 verification + ISO write (bytes live in `p13/doa4.iso` at their offsets AND in release doa4-iso-v1; one-store rule).
  - NOT cleared: p13/doa4.iso (assembly in progress), p13/extracted/{cmn,avt}.afs (pending the release/manifest step), all census JSONs/logs.

- FINAL LANE-CLOSE UPDATE (supersedes the two bullets above
  where they conflict): **Job 2's exhaustion declaration is
  WITHDRAWN** — the definition files were FOUND (26 named
  entries inside the ISO's actual anm.afs, a standard AFS
  container at ISO sector 416009); the phase 7–12 "anm.afs"
  was a different pressing's file (head c1ff2852…) mislabeled
  in phase 1. Definition files released as
  `doa4-anime-definition-20261022` + `phase13/definition-manifest.json`;
  corrected account in `phase13/ANM-DEFINITION-2.md`; semantic
  decode = named next lane. **Job 3 CLOSED**: L2 census
  completed via the incremental resume tool (first process
  died at 131/148 in a session-abort event, results in memory
  only); controls 28/28, 20/20, 23/23; proven signal band 7–15
  unique (fam477: 13, famC: 15, head21: 7); all 8 unpaired
  heads 0–2 vs every family → **no new pairings, composites
  23/31 FINAL** (`phase13/HEAD-EVIDENCE.md`,
  `phase13/texrecord_census.json`). **Job 1: 9/30 parts
  landed + sha256-verified** (01–09), parts 10+11 in flight
  at close; release re-verified 30 assets = 7,834,892,288B;
  ISO not cleared (assembly incomplete, never-kill rule).
  Additional clears: assembler part files 05–09 post-verify;
  two stalled unverified partial downloads (08/09 first
  attempts) deleted to restart cleanly.
