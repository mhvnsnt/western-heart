# DOA4 Sweep Audit — 2026-10-20 (teardown-completion sweep, lane 3)

**Question audited:** the DOA4 teardown checkpoint was closed as COMPLETED on
2026-10-18 ("129 triangulated GLBs live on origin/main; nothing left to do").
Was that true under the TEARDOWN-COMPLETION LAW (extracted + decrypted +
decoded + ASSEMBLED + wired into Western Heart)?

**Verdict: NO.** The completion claim was not true when made, and is still not
true today. The honest state, by the numbers (all counts verified against
`mhvnsnt/western-heart` main, git tree API + fresh checkout, 2026-10-20):

## What is actually on main

| Item | Count | Evidence |
|---|---|---|
| Triangulated GLBs total | **165** | git tree `teardown/dead-or-alive-4/models/triangulated/**/*.glb` |
| chrone | 30/30 tables | tree listing |
| chrtwo | 68/68 tables | tree listing |
| chrthree | **56/75 tables** | tree listing (50 from PR #248 + 6 from the 2026-10-19 continuation) |
| mot | 11/11 tables | tree listing |
| stg (stages) | **0 verified** | continuation doc: auto-discovery output failed the quality gate (NaN positions, 4–39% degenerate), GLBs removed rather than merged |
| Vertex-buffer point-cloud GLBs | 105 | `models/vertex-buffers/` (21 chrone + 39 chrthree + 25 chrtwo + 2 mot + 18 stg) |
| XPR2 textures carved | 219 | GitHub release `doa4-xpr2-carved-v1` (not in git tree) |
| Standard AFS files extracted | 961 | snd/spr/avt/cmn (release mirrors, not in git tree) |
| Movesets wired | 6 fighters, 16–26 moves each | `DOA4-CONTINUATION-2026-10-19.md` (core lists only; FULL MOVESET LAW wants 100+/fighter) |

## Own-eyes findings on the shipped GLBs (new this audit)

1. **Every triangulated GLB fails to import into Blender 4.0.2.**
   `tools/doa4_decode.py:write_glb` declares the TEXCOORD_0 accessor with
   `byteOffset = n*12`, but the binary chunk is written interleaved
   (pos 12B + uv 8B per vertex, stride 20), so the correct offset is 12.
   Blender's importer dies in `decode_accessor` ("buffer is smaller than
   requested size"). The geometry (positions + indices) parses fine with a
   lenient reader; the UV accessor is also what makes strict readers reject
   the files. New GLBs from this lane use a corrected writer
   (`tools/doa4_decode3.py`); the 165 shipped GLBs need a one-line header
   repair pass (documented, not silently rewritten by this lane).
2. **The meshes are unassembled per-part pools.** chrone_00 rendered
   (Blender Cycles, after the byteOffset repair in a scratch copy) is a
   spiked ball of overlapping parts, and point-cloud plots of chrone_00 /
   chrthree_00 show no character silhouette. This matches the 2026-10-19
   continuation's own note: vertex pools are stored in **per-part local
   space** and only assemble into a character via the skeleton transforms in
   the **MdlGeo ObjGeo chunks, which are not parsed yet**. So even the
   "decoded" GLBs are NOT assembled assets.
3. **No skeletons, no weights, no animations in any GLB.** Parsed GLB JSON:
   `skins = None`, `animations = None`, single node, single mesh, attributes
   POSITION + TEXCOORD_0 only. (Per the per-character isolation law: files
   ARE per-character-table and self-contained — no shared-rig artifact exists
   in the DOA4 tree — but they contain no rig at all.)
4. **anm.afs (animations) is not decoded at all** — see the animation
   section below. mot.afs GLBs are model pools, not motion clips.

## chrthree 09–33 — the real blocker (new this audit, byte-level)

The 25 XPR2 offsets 0x6e7c800–0xaf46800 (batch indices 09–33) are NOT
full model tables. Dumping offset 0x6e7c800: the record run is
`XPR2` + 48 `TX2D` records, then the run breaks at record 49 — there are
**no VBUF records, no IBUF records, and no 0x20001/0x30001 descriptors
anywhere in the chunk** (byte-scan of the whole chunk: VBUF×0, IBUF×0).
These are sub-packages (texture/accessory bundles) whose geometry, if any,
is referenced from a parent package — the "relative-offset sub-layout" the
2026-10-19 continuation noted. `tools/doa4_decode3.py` (this lane) adds
region-restricted per-descriptor base discovery and a fixed GLB writer,
but it cannot invent VBUF records that do not exist in these chunks.
19 named indices remain undecoded (10, 13, 14, 15, 17, 20–33 in shipped
naming); finishing them requires reverse-engineering the sub-package
layout (how a parent table references these chunks' data), not another
batch run. This lane also caught and removed its own first decode3
output before commit: the run enumerated only 50 tables (parse rejects
the sub-packages), so its GLBs were re-decodes of already-shipped tables
under wrong indices — deleted from the branch, never committed.

## Animations (anm.afs) — assessed 2026-10-20 on the real bytes

- anm.afs = 2,949,120 bytes (0x2D0000), re-extracted from release
  `doa4-mirror-20261017` this run; first-4-byte XOR key re-verified:
  cipher `c1 ff 28 52` XOR `80 b9 7b 52` = `AFS\0`.
- Unlike chr*/mot/stg (plaintext payloads), anm.afs is obfuscated through
  its body: entropy 6.83–6.84 sustained over the first ~1MB (vs 4.85–5.56
  in later regions), zero format markers anywhere (XPR2/VBUF/IBUF/TX2D/
  USER/MdlGeo/ObjGeo/ANM/MOT counts all 0), and no plaintext BE-float
  keyframe streams (the longest [-1,1] float run is a zero padding area).
- Repeated 8-byte ciphertext blocks (16× in the first 8KB, e.g. tails of
  `6b6b6b6b`, `f4f4f4f4`) indicate structured plaintext under a periodic
  keystream — the same cipher family as the AFS TOCs.
- **Blocker, precisely:** animation decoding needs (a) the keystream
  algorithm (Audit 19 status: derivation unknown, 0/6 reproduced) AND
  (b) the Team Ninja animation format behind it, which cannot even be
  sampled until (a) falls. No animation data is decoded; no workaround
  was substituted.

## Completion-law scorecard

| Law stage | State |
|---|---|
| Extracted (ISO → files) | DONE — 14 files / 3.0GB from XGD; ISO byte-verified on release `doa4-iso-v1` |
| Decrypted | PARTIAL — data payload is plaintext (proven); AFS header/TOC cipher NOT cracked (keystream algorithm unknown after 19 Ghidra audits; 6 per-file 4-byte header keys known from `AFS\0` known-plaintext only) |
| Decoded | PARTIAL — 165/183 XPR2 model tables triangulated (chrthree 56/75, stg 0/18 verified); textures carved (219 XPR2, not converted); animations 0% |
| Assembled | **NOT DONE** — per-part local-space pools; MdlGeo ObjGeo skeleton transforms unparsed; no skinned/posed character exists |
| Wired into Western Heart | PARTIAL — GLBs + 6 core movesets in repo; no fighter is roster-wired from these models (fighter identification of tables is itself blocked on the TOC cipher) |

## Keystream status (Audit 19, this lane)

- Audits 1–18 (2026-10-18): not cracked; static string-xref space exhausted.
- Audit 19 (2026-10-20, `tools/ghidra-audits/findings-audit19.txt`): the
  00dfxxxx "prime lead" is **closed** — it is the XDK CRT register
  save/restore helper block (Capstone disassembly + exactly 1 pattern hit in
  .text + `__savegprlr_*` naming in the doa4-recomp generated code). The
  Audit 12/15 "thunk to the decrypt routine" conclusion is retracted.
- The CRI AFS partition descriptor tables were located in .data (six
  28-byte-stride tables holding pointers to the `cache:\*.afs` strings) —
  the loader is table-indirect. Key reproduction from a derived algorithm:
  **0/6** (keys known individually, derivation unknown).
