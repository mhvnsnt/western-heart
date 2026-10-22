# DOA4 Phase 9 — Job 1: head/hair geometry hunt

## Question
Phase-6 GLBs (chrone) contain NO heads — phase-8 front renders end at collar/neck. Where does head/hair geometry live?

## Evidence so far

### (a) Phase-6 assembly re-audit — no dropped decl class in chrone
- chrone pkg00 report (`phase6/reports/chrone-pkg00_report.txt`): 68 GeoDecls → 67 exported meshes; the single loss is decl39 "NO SEGMENT" (a segment-location failure, 1 decl, not a class). All segment classes (s0/s1/s3) are exported. The batch export did NOT skip a geometry class.
- GLB audit of all 30 chrone GLBs (`phase9/tools/glb_head_audit.py`): every package's geometry Ymax is 0.30–0.33 (group C ninja 0.59–0.60 = back-katana tips above the shoulder line), Ymin ≈ −0.46 (group C −0.52). No chrone package contains geometry above the collar line except group C's weapon tips. Chrone packages are body-only as exported — and the assembly accounting says nothing was dropped from them.
- Chrone skeleton tops: pkg00 top joints are a symmetric pair at Y=0.589 (children of one node — shoulder/weapon class, not a single central head joint); pkg06 same pattern at 0.646.

### (b) Container census — chrtwo holds 42 head-sized packages
- `phase6/inventory-chrtwo.csv`: chrtwo packages split into two populations — full-size packages (00–03, 46–67; 58–100 meshes) and **42 small packages (04–45; only 5–17 meshes each)**. Chrone has no small population except pkg29 (2,913 verts, non-character, phase-8 strong). Chrthree's 50 full packages are all 61–108 meshes — no small population; its 25 texture-only sub-packages hold no geometry at all (phase 6, proven).
- **Phase-6's own viewed sample render `phase6/samples/chrtwo-pkg20-front.png` IS one of the small packages: a braided-hair HEAD with face, braids and a large collar — and nothing else.** Re-viewed by this lane 2026-10-21: head + collar only, no body. Phase 6 described it as "coherent (braided head + collar)" without drawing the structural conclusion.

## Interim verdict (to be proven by render)
Heads live as **separate small packages inside chrtwo.afs (pkg04–45)**, each carrying its own Hie skeleton. The game's character assembly = body package (chrone/chrthree/full chrtwo) + head package (chrtwo small). Remaining proof steps:
1. Audit all chrtwo GLBs (bounds/joints per package) — classify small = head.
2. Render a small package front, VIEW it (head confirmed by eyes, not stats).
3. Map head-package ↔ body-package with evidence (skeleton/Hie compatibility: head package's root/neck joint chain vs body package's neck joint; roster ordering).
4. PROOF render: one body package rendered WITH its mapped head attached per the game's own skeleton.

## UPDATE 2026-10-21 (later) — heads CONFIRMED by viewed renders
- All 68 chrtwo GLBs extracted from release `doa4-phase6-models-20261021` (extract_span: 68 ok / 0 fail). Small packages audit: 11–32 nodes, 6–17 meshes, compact bounds (Y span ≈ 0.43–0.55, some with hair drops to −0.75/−0.79), own small Hie skeletons (8–15 joints), head-local (skeleton base at origin; e.g. pkg04 joints at Y 0 / 0.111 / 0.468).
- VIEWED renders (`phase9/renders/p9-head-chrtwo-pkg04/20/24.png`): pkg04 = face + slotted cap + very long straight hair panels; pkg20 = face + braided pigtails + smooth cap + wide collar; pkg24 = face + spiky hair ornaments + long dropped ponytail strand. **The small chrtwo packages ARE head+hair packages — certain.**
- Exporter defect found en route: small-package GLBs carry out-of-range JOINTS_0 sentinel entries (pkg04: 162 entries, pkg20: 144; ALL with weight 0.000000) that crash Blender's glTF importer (IndexError 65535 vs joint count). `phase9/tools/glb_sanitize.py` clamps them in a render copy only (source GLBs untouched; clamped weight sum = 0 proves no skinning change).
- Body-side anchor: chrone pkg00 skeleton has a central top joint (joint17 @ (0, 0.486, −0.021)) = neck/head-base candidate; head packages are head-local with base at origin, so attachment = head origin → body head joint, per Hie.
- Mapping test in flight: XPR2 package-wide **f3 tag** for all 148 packages (range-fetched headers; phase 3: f3 is package-wide, e.g. 3364 for chrone pkg0) — if f3 encodes character identity, heads and bodies of one character share/relate by f3.
- Still owed: the f3 verdict, the head↔body map, and the combined proof render (body + its mapped head, front, viewed).
