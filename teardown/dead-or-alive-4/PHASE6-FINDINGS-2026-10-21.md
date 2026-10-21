# DOA4 Phase 6 — Batch Completion, Skinned Exports, TX2D Textures (2026-10-21)

Follow-on to PR #430 (phase 5, blend indices + G3). Branch:
`feat/doa4-phase6-batch-skinned-tx2d-20261021` (stacked on
`feat/doa4-phase5-blendidx-batch-20261021`). PR #435. State file:
`~/workspace/_doa4p2-scratch/PHASE6-STATE.md`.

## 1. Batch completion (job 1)

Every XPR2 package in chrone.afs (30), chrtwo.afs (68) and chrthree.afs
(50 full packages) was range-pulled from the doa4-mirror release,
assembled per-package in isolation, and exported as a skinned GLB.
Package census = XPR2 directory scan of each AFS
(`tools/phase6/scan_pkgs.py`, `scan_seq.py`).

| AFS | packages | meshes | clean | moderate | poor |
|---|---|---|---|---|---|
| chrone | 30/30 | 2003 | 1078 | 665 | 354 |
| chrtwo | 68/68 | 2497 | 1189 | 670 | 705 |
| chrthree | 50/50 | PENDING | | | |

Quality is per-GeoDecl (phase-4 style): clean = full-coverage strip with
mean edge/scale score < 0.10; moderate < 0.25; poor = worse, NO STRIP, or
NO SEGMENT (flagged per-decl in `phase6/reports/<tag>_report.txt`).
Full per-package table: `phase6/inventory-chrone.csv`,
`phase6/inventory-chrtwo.csv`, `phase6/inventory-chrthree.csv`.

Assembly notes:
- Segment location uses the phase-4 set-walk (segments in decl order) with
  a full-scan fallback. The fallback validator now also checks the
  BLENDWEIGHT invariant — column count per stride hypothesis must equal
  the object's ObjInfo palette count and rows must be in [0,1] summing
  to 1 (this caught a real stride mis-read: chrone pkg00 decl23 walks at
  stride 68/2-col, not 72/3-col).
- Degenerate BLENDWEIGHT rows (sum <= 0.5, e.g. pkg00 decl39) fall back
  to rigid own-node skinning and are flagged in the report.
- chrone pkg06–09 (large images, XPR2 f2 up to 0x1313800) were first
  truncated by a fixed window cap and rebuilt with image-sized windows
  (`xp + f2 + 0x300000`, capped at the next package's directory +
  0x360000); the inventory rows in git are the rebuilt ones.
- chrthree additionally contains 25 TX2D-only sub-packages in the audit
  range 0x6e7c800–0xaf46800 (XPR2 + TX2D records only — no USER/VBUF/IBUF,
  so no geometry exists to assemble). Together with the 50 full packages
  they account for all 75 chrthree tables (see Gates, G2).

Viewed front renders (sample of 6 per AFS, assembly QC):
`phase6/samples/` in this PR.

## 2. Skinned exports (job 2)

Every batch GLB is skinned, in the format phase 5 proved for G3:

- Skeleton: Hie nodes with TRS decomposed from the local matrices.
  (Phase 6 check: all Hie local/world matrix determinants are +1.0 —
  no reflection; the phase-3/5 "X-mirror" is a side-naming difference,
  so TRS decomposition is safe.)
- `JOINTS_0`: the per-object ObjInfo bone palette (u16 array at
  ObjInfo+0x90, count at +0x3c) for blend decls; rigid own-node
  (weight 1.0) for non-blend decls.
- `WEIGHTS_0`: the BLENDWEIGHT columns, normalized.
- `inverseBindMatrices`: inverses of the Hie world matrices.

Spot-verification (chrone pkg00): `tools/phase6/verify_skin.py`
recomputes the bind pose from the exported GLB's own data — max vertex
error 0.000000. A +40° Z bend of joint 14 was then applied through the
exported skin, rendered, and viewed against the bind render: the
gown/leg region swings as one coherent piece, mirroring the phase-5
pose test. Renders: `phase6-spotcheck-bind.png`,
`phase6-spotcheck-bent14.png`.

## 3. TX2D textures (job 3) — SOLVED

The 40-byte TX2D descriptor is an Xbox 360 texture fetch constant
(Xenia `xe_gpu_texture_fetch_t`), read at descriptor words 7/8/9:

- word7 (dword_0): tiled bit (31) = 1; pitch in pixels at [30:22] << 5.
- word8 (dword_1): format [5:0] — 18 = DXT1, 20 = DXT4_5 (DXT5),
  6 = 8_8_8_8; endianness [7:6] (1 = 8in16 swap for DXT, 2 = 8in32 for
  fmt 6); base_address [31:12], in 4K pages, image space.
- word9 (dword_2): size_2d — width [12:0] + 1 and height [25:13] + 1,
  in PIXELS.

(The phase-5 leads are superseded: word0 is not the format and word2 is
not the pool offset.)

Pool location: texture data lives in the package's image region, at
file offset `xp + align_up(xpr2_header_f1, 0x1000) + base_address`.
Pinned by boundary-coherence scans and proven by decode (below).

Unswizzle: X360 Tiled2D, ported from Xenia `texture_address.h`
(Xenia project, BSD-3-Clause, Copyright Ben Vanik / Xenia project;
itself derived from crunch's crn_decomp.h and AMD AddrLib). Port:
`tools/phase6/tx2d_try.py` (attribution header included); decoder:
`tools/phase6/tx2d_decode.py`.

Proof — all 42 chrone pkg00 textures decoded to PNG
(`textures/chrone-pkg00/` in this PR) and the decisive ones viewed:
tex20 = shoe/buckle atlas, tex30 = vest front (buttons, plaid), tex32 =
vest back, tex19 (fmt 6) = the shoe normal map, tex09/tex40 (DXT5) =
crest emblems with alpha. The fmt-6 textures are the normal maps paired
with the DXT1 diffuse maps.

Textured GLB: `models/chrone-pkg00-textured.glb`, rendered and viewed
(`chrone-pkg00-textured-front.png`): the plaid torso is in real colors.
Only three assignments are carried, each with its evidence:
obj0_decl1 -> tex30 (candidate renders for tex30/32/11/18 on this decl
were viewed: tex30's plaid weave follows the surface coherently, the
skin texture lands mottled, i.e. wrong); obj9_decl12 and obj23_decl30 ->
tex40 (tiny patch meshes; UV alpha-hit 0.95 on tex40 vs 0.71 next best).
No other mesh carries a texture: no file-internal material->texture
index exists in the ObjGeo/ObjInfo records (censused — item +0x030
takes only {2,7,32,52}, a shader class), and statistical assignment
metrics (UV painted/structure, border-connected containment) did not
separate candidates decisively. The remaining binding is future work,
most likely in the material data the game keeps outside these packages.

## Pull-in log (research -> repo)
- Xenia texture_address.h / texture_util / xenos.h (BSD-3-Clause) —
  Tiled2D/TiledCombine swizzle + fetch-constant layout + TextureFormat
  enum. Ported to `tools/phase6/tx2d_try.py`; used by
  `tools/phase6/tx2d_decode.py`.

## Gates (PR #397 G1–G6)
- G1 Keystream proof: NOT this phase — open (cipher covers AFS TOCs +
  anm.afs body; chr/mot/stg payloads are plaintext).
- G2 chrthree completeness: 75/75 tables accounted — 50 full packages
  assembled + skinned; 25 sub-packages proven texture-only (directory
  census: XPR2 + TX2D records, no USER/VBUF/IBUF).
- G3 Skeleton/weights: PASSED (phase 5); this PR is its batch evidence —
  148 skinned GLBs + the pkg00 spot-verification above.
- G4 Animation: NOT started — depends on G1.
- G5 Reproducibility (.bms): NOT applicable yet — no decryption proven.
- G6 Import-verify / wiring into game/: NOT this phase — follows
  skinned exports + textures (this PR supplies both).

## Storage
Batch GLBs (148) live in release `doa4-phase6-models-20261021`
(split stored zips, <100MB parts); `models/phase6-manifest.json` in git
carries per-GLB sha256 + size. Graphs, reports, inventories, tools,
texture PNGs, the textured GLB and all proof renders are in git on this
branch. Local copies were cleared after GitHub verification and logged
in `~/workspace/agent-ops/disk-cleanup-log.md`.
