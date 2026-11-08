# L/R-swapped weights fix — 7 files — REPORT

Owner order 2026-11-07 23:41 CST: "Fix it all." Method: industry-standard deterministic correction only, no hand tooling. No PR opened, nothing pushed — staged for lead verification.

## The defect (from the Nightwolf audit lane)
7 GLBs ship with correctly-placed joints but skin weights assigned to the mirror-named bones (full limbs — arms, legs, hands). In bind they render fine; under named-bone animation each side drives the opposite side's geometry. Full record: `~/workspace/_nightwolf-rerig-20261107/REPORT.md` Task 1.

## The fix (one mechanical operation, identical for every file)
Pipeline per file, all steps scripted (`run_file.sh`, `permute_joints.mjs`, scripts in this folder):
1. Pull from mhvnsnt/western-heart main, **git blob-verified** (hash-object == ls-tree HEAD sha) before touching.
2. Decode with the repo's own codec (`tools/anim/gltf_codec.mjs decode` — dequantize + unpartition).
3. Derive the pair map **mechanically from the skeleton's own joint names** (Left↔Right token swap across the whole skeleton). All 7 files share the pipeline's 49-joint template skeleton: **21 L/R pairs** (Shoulder, Arm, ForeArm, Hand, Thumb1–2, Index1–3, Middle1–3, Ring1–3, Pinky1–2, UpLeg, Leg, Foot, ToeBase) + 7 center joints. Involution and target-uniqueness verified by the script; any unpaired-but-referenced or ambiguous joint is a hard stop (exit 3, no write).
4. Permute JOINTS_0 index values through that map (single index permutation, same for every vertex). Geometry, skeleton, nodes, and inverse bind matrices are not touched.
5. Re-encode with the repo codec (`gltf_codec.mjs encode` — prune keepSolidTextures + meshopt medium), the same form the game's shipped files use.
6. Verify on the **final encoded deliverable itself** (decode it back and re-probe), plus header, Blender, and harness-render checks below.

### Flag for the lead — RightHandThumb3 (measured no-op, not a guessed pair)
The template skeleton is asymmetric: it has `RightHandThumb3` but no `LeftHandThumb3` (same asymmetry in the healthy pantera template). The name map therefore leaves it unpaired. A per-joint weight census (script `census.py`, run on every file's decode) proves **every finger joint carries zero weight in all 7 files** — hands are weighted to the Hand bones only (game banks carry no finger tracks). RightHandThumb3 is referenced by 0 vertices, so holding it as a fixed point changes no weight value; no pair was invented for it. It is recorded per-file in `work/<name>.pairmap.json` (`unpairedUnreferenced: ["RightHandThumb3"]`) for your veto. All joints that carry any weight are paired.

## Per-file results
Probe = `probe_mirror.py` (dominant-vertex median distance to own vs mirror bone segment, metres). Healthy controls from the audit: own 0.055–0.147. Defect signature: own 0.45–1.09 / mirror 0.12–0.17. "After" values below are measured on the **final encoded file**, decoded back.

### 1. game/assets/models/kiko-tanaka.glb (Rave attire 1, bank: lei)
- Blob before `3df666afd625ba825b716a2f6998331cf9a03949` (20,220,984 B) → after `ece763a5e19f46d23a931bbf72d6a1b78277e9a8` (23,670,744 B)
- Pairs swapped: 21 · joint values changed: 867,516 / 1,022,970 verts
- Probe before: LA own .463 / RA .473 / LF 1.077 / RF .945 (mirror .119–.173)
- Probe after: **LA .126 / RA .119 / LF .142 / RF .173** (mirror .463–1.077) — exact mirror flip
- Renders: `renders/kiko-tanaka_stance_BEFORE.png` (original explodes under lei stance) vs `renders/kiko-tanaka_stance_AFTER.png` (clean crouched guard, hands up on correct sides); bind pair in `renders/`

### 2. game/assets/models/kiko-tanaka_alt1.glb (Rave attire 2, bank: lei)
- Blob before `77db8e2781a1b05cba6345f1bc50c68ae7b6e159` (90,963,360 B) → after `eea3b21003e8dc56c174d4c61791fa794e5266a8` (26,889,304 B)
- Pairs swapped: 21 · joint values changed: 2,863,106 / 971,136 verts
- Probe before: LA .474 / RA .512 / LF 1.086 / RF .892 → after: **LA .163 / RA .147 / LF .142 / RF .168**
- Renders: `renders/kiko-tanaka_alt1.stance-after.png` (dynamic Lei stance, arms/legs correct), bind pair in `renders/`

### 3. game/assets/models/mariposa.glb (Mariposa slot 2 Tripo, bank: zafina)
- Blob before `cc8241b06605eb8250c3c68f90944c22c06566c8` (90,428,948 B) → after `45a1696d60e198ff672cd438d8d0a08bf402a3e1` (25,177,360 B)
- Pairs swapped: 21 · joint values changed: 3,166,342 / 1,013,363 verts
- Probe before: LA .494 / RA .519 / LF 1.070 / RF .901 → after: **LA .153 / RA .142 / LF .170 / RF .174**
- Renders: `renders/mariposa.stance-after.png` (Zafina low crouch, coherent), bind pair in `renders/`

### 4. roster/mariposa/attires/monarch/mariposa-monarch-rigged.glb (Mariposa slot 3, bank: zafina)
- Blob before `0cc15e297a4500f896dcbc9b7296e19992893706` (90,429,536 B) → after `6e65d2136a3d048593693d1b6f2ac0c55bd6f960` (25,177,360 B)
- Pairs swapped: 21 · joint values changed: 3,166,342 / 1,013,363 verts (same rig/mesh family as mariposa.glb — identical probe numbers, expected)
- Probe before: LA .494 / RA .519 / LF 1.070 / RF .901 → after: **LA .153 / RA .142 / LF .170 / RF .174**
- Renders: `renders/mariposa-monarch-rigged.stance-after.png`, bind pair in `renders/`

### 5. game/assets/models/purple-rain-main.glb (Purple Rain main, bank: lee)
- Blob before `2dbccd6dc94d65691d959031421fd26fdd738e2c` (89,476,476 B) → after `76c33bee9d8fb771095f4f2c7684d746e6e0a256` (22,726,660 B)
- Pairs swapped: 21 · joint values changed: 2,616,508 / 1,024,038 verts
- Probe before: LA .454 / RA .477 / LF 1.093 / RF .887 → after: **LA .141 / RA .133 / LF .121 / RF .127**
- Renders: `renders/purple-rain-main.stance-after.png` (Lee stance, limbs correct), bind pair in `renders/`

### 6. game/assets/models/saku-ra-main.glb (Saku-ra main, bank: xiaoyu)
- Blob before `8ce100ac4b5b8e07ad4ce9f79e3f937a0c362412` (88,713,344 B) → after `980aa25b9d2df5dfdafc089cc165acaa9137555f` (22,959,544 B)
- Pairs swapped: 21 · joint values changed: 3,038,835 / 1,007,864 verts
- Probe before: LA .475 / RA .489 / LF 1.056 / RF 1.060 → after: **LA .138 / RA .126 / LF .117 / RF .121**
- Renders: `renders/saku-ra-main.stance-after.png` (Xiaoyu stance — raised hand, guard arm, planted legs, all correct sides), bind pair in `renders/`

### 7. game/assets/models/cape-jones.glb (Cape Jones attire 1, bank: gunjack)
- Blob before `03833f26ec2db1a2c1cce6ba03d4cedb5a50c074` (86,192,132 B) → after `f350d7258da2aeb8539fe3aebb2956fc4732e713` (20,596,200 B)
- Pairs swapped: 21 · joint values changed: 3,324,638 / 991,082 verts
- Probe before: LA .488 / RA .504 / LF 1.044 / RF .931 → after: **LA .156 / RA .144 / LF .137 / RF .150**
- Renders: `renders/cape-jones.stance-after.png` (guard up, cape draped, hands on correct sides), bind pair in `renders/`
- Bank note: roster_map gives this fighter wh_moveset gunjack (tekken_slot Alisa); rendered under the T3 gunjack bank. Alisa's bank exists as a Fill-3 overlay if the lead prefers that check too.

## Verification applied to every file (all 7 pass)
- **probe_mirror on the final encoded deliverable**: own-segment medians 0.117–0.173 (healthy band), mirror-segment 0.449–1.093 — the defect signature exactly inverted. Full JSONs: `work/<name>.probe-{before,after,final}.json`.
- **Bind identity**: harness bind renders of original vs fixed are bone-for-bone identical (world positions of all 49 joints equal to the dumped 3-decimal precision on every file) — proof the skeleton/geometry did not move. PNG pairs in `renders/`, raw dumps in `harness/out/`.
- **Stance render** through the game's own `t3anims.js` retarget harness (same harness as the Nightwolf proofs), t=0.35 on each character's own bank: coherent pose, no crossed/swapped limb motion on all 7. The kiko before/after pair shows the contrast directly: the original tears apart under the lei stance; the fixed file holds a clean guard.
- **Header**: GLB header total-length == actual file size on all 7 outputs. (Note: three originals — cape-jones, kiko-tanaka_alt1, mariposa — carry a pre-existing header length off by 1–2 bytes on main; the codec-encoded outputs are exact.)
- **Blender strict import**: Blender 4.0.2 has no EXT_meshopt_compression support (that is why the repo codec exists), so the strict-import check runs on the codec decode of each deliverable: all 7 import cleanly, `Character` armature, 49 bones each.

## Deliverables (this folder)
- `fixed/<name>.glb` — the 7 fixed files, ready to land at the repo paths above.
- `renders/` — bind before/after + stance-after PNGs per file, plus the kiko stance before/after pair.
- `work/` — pairmaps, censuses, probe JSONs. `harness/` — the render harness (game code + vendored bank clips). `orig/` — blob-verified pulls of main's current files.
- Scripts: `permute_joints.mjs` (the permutation), `run_file.sh` (per-file pipeline), `census.py`, `inspect_glb.mjs`, `codec/gltf_codec.mjs` (repo tool copy).

## Process note
The first backgrounded pull loop produced unreliable early output and interleaved writes into `orig/`; it was killed and **every file was re-pulled individually and hash-verified** before use (the sizes/blobs in this report are from the verified pulls). Disk quota wall (EDQUOT) closed once mid-run; freed ~2 GB of this lane's own scratch (the wh clone) and completed.

## Pin audit (landing lane, 2026-11-08 ~01:20 CST, main a89b10b0)
Question: does anything in the repo pin the 7 PRE-fix blob SHAs, or reference these paths in a way that needs updating alongside the GLBs?
- GitHub code search (`search/code`, repo mhvnsnt/western-heart) for each pre-fix short SHA — **0 hits for all 7**: 3df666af, 77db8e27, cc8241b0, 0cc15e29, 2dbccd6d, 8ce100ac, 03833f26.
- Root-level files (checked-out clone at main): grep for all 7 SHAs — **0 hits**. Filename mentions only in AGENTS.md, WORKLOG.md, portraits-manifest.json (path/name references; paths unchanged).
- All 12 text files >384 KB under game/js, game/data, docs (above the code-search index limit — coverage.json 7.2 MB, banks/wrestling.json 5.7 MB, banks/t3.json 5.7 MB, t7-unified-index 655 KB, weight-bleed-fix/fix-records.json, r13/r14-failing.json, combot-join.json, wmxix.json, sweep-jin_soul*.json) downloaded raw from main and grepped — **0 SHA hits**. Filename mentions in fix-records.json / r13/r14-failing.json are historical moveset-sweep records keyed by fighter name, not blob pins.
- The game loads models by repo path, not by blob SHA; all 7 paths are unchanged by this fix.
- **Verdict: no pins exist. No pin updates needed. Payload = 7 GLBs + this report only.**
- Audit note: a `git grep` over game/js + game/data in the local clone was abandoned after ~9 min with no output (on-demand blob fetch over the egress proxy stalled); code search + the 12-file raw download above cover the same surface — every text file is either indexed by code search or was downloaded and grepped directly.
