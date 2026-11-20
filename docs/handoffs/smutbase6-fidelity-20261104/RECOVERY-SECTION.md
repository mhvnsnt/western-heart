
---

## MEGAMI + MENAJERII SOURCE RECOVERY — FOUND (2026-11-05, this PR)

The two commission packages are recovered. The TeraBox check came back
negative; a browser lane then identified the original SmutBase listings
(MilkGuy_3D: "Parvati Holcomb" project 9ca4fe0b…, "Vixen" project
c7db985f…) and re-downloaded both archives from the free mirror. The
recovered files were extracted, inventoried in Blender 5.2.3, rendered
for identity, and stored on the intake release (below) — they no longer
exist in only one place.

**The archives are byte-identical to the lost originals.** The full
original sha256 values were preserved in the lane checkpoint
(`~/workspace/agent-ops/checkpoints/smutbase6-fidelity-20261104.json`)
all along, and both re-downloaded rars match them exactly:

| File | Bytes | sha256 | vs original record |
|---|---|---|---|
| `ParvatiCommission.rar` | 326,033,257 | `2601d9356f5e530cd0abb0956db99fc47e2b70bba4bec58908ce64fc8dc68ff7` | **EXACT match** |
| `Vixen_Commission.rar` | 412,236,235 | `e6d2754b09f6de050e8a586d6fca3c4ed49f57fcdc4c1f36abfdc41c2be5e5a7` | **EXACT match** |

Hash note (the open question this lane had to settle): the SmutBase
mirror page states a "source" SHA-256 for the Parvati archive of
`2601d935e1f8a09e1da0d67ad3b47eae4d2f4e9f38bc3a0d6dd0b0b5fbb6da8` —
same 8-char prefix, different thereafter. That page value is the
artifact: the downloaded archive's own hash matches the ORIGINAL
intake record digit for digit, and the contents independently match
the intake description (below). The Vixen mirror page value matches
in full.

**Extracted blends (inventory: Blender 5.2.3, measured)**

| | Parvati(Commission).blend | Vixen (Commission).blend |
|---|---|---|
| Bytes | 595,860,144 | 984,617,116 |
| sha256 | `cfc9864a15b03989b9dcb559e5fffc02bde8075f26472eeb4308500f01a8612a` | `085d914c6539e0bef89f881ba6887336a1d93115ee6bef792161ec737c375670` |
| File version | Blender 4.2 (reads 4.2.66) | Blender 4.2 (reads 4.2.66) |
| Scene objects | 66 (55 MESH, 1 ARMATURE, 5 LIGHT, 1 CAMERA, 4 EMPTY) | 67 (56 MESH, 1 ARMATURE, 5 LIGHT, 1 CAMERA, 4 EMPTY) |
| Armature | `Parvati` — 469 bones | `Vixen` — 450 bones |
| Rig | GZM — `GZM_*` controller objects present (GZM_Arrows / GZM_CircleChest / GZM_FaceHead / …) | GZM — same controller set |
| Shape keys | 474 non-Basis, all on `Parvati Mesh` | 2,509 non-Basis across 24 meshes (515 on `Vixen Mesh`, 365 Body Suit, 355 Suit, …) |
| Images | 124 total, 123 packed | 125 total, 124 packed |

Intake-record deltas, stated plainly: the old record said "Blender
4.02, 90 / 88 objects." The files read as Blender 4.2 and hold 66 / 67
scene objects (the old counts evidently enumerated more than scene
objects). Every hard identifier — archive hashes, byte sizes, GZM rig,
character identity — matches; these are counting/label deltas in the
old record, not a different package.

**Identity proof (eye-checked, this PR)**
- `docs/proof/2026-11-04/smutbase6-fidelity/parvati-src-front-20261104.png`
  + `parvati-src-q34-20261104.png` + `parvati-src-face-20261104.png`:
  the recovered Parvati, fully textured in her blend — same character,
  face, and steampunk outfit (goggles, chest plate, belt + hanging
  cloth, thigh pouch, arm guards) as `parvati-full.glb`, piece for
  piece. (In the GLB she reads silver-haired because the 8 hair-strand
  materials carry no texture — the source trait recorded above; the
  blend's hair is dark and textured.)
- `docs/proof/2026-11-04/smutbase6-fidelity/vixen-src-front-20261104.png`
  + `vixen-src-face-20261104.png`: the recovered Vixen — same suit
  (high collar, spiked neck emblem, long sleeves, pelvis emblem, knee
  guards, boots), face, and proportions as the intact sibling
  `model.glb`, piece for piece.
- Full inventories: `inventory-parvati-recovered.json`,
  `inventory-vixen-recovered.json` in the same proof folder.

**Store (mirror law — never one copy again)**
Release `megami-menajerii-smutbase-20261023` (mhvnsnt/western-heart)
now holds, alongside the original two GLBs:
- `ParvatiCommission.rar` (326,033,257 B) — whole, digest verified
- `Vixen_Commission.rar` (412,236,235 B) — whole, digest verified
- Both blends as 300 MB parts (`ParvatiCommission.blend.part-00/01`,
  `VixenCommission.blend.part-00…03`) with `MANIFEST-recovered-blends.md`
  (whole-file + per-part hashes, reassembly commands).

Why parts: uploads above ~412 MB from the work VM never finalized on
GitHub's side in this session — assets stayed in "starter" state with
no retrievable content (range GET → 404) even though both the gh CLI
and a direct curl POST reported success and sent the full byte count.
A 419,430,400-byte part failed repeatedly; everything ≤ 412,236,235 B
succeeded. The blends therefore went up as ≤ 314,572,800-byte parts,
one at a time via direct API POST. (GitHub also sanitizes asset names,
so the blends' parts use the undressed names; the manifest maps them
back to the original filenames.) Every stored asset's size + sha256
digest was verified against the local file via the Releases API, and
the store was pull-back proven: all six parts re-downloaded,
reassembled, and both whole-file sha256 values reproduced exactly;
`ParvatiCommission.rar` likewise re-downloaded and hash-matched.
Local copies:
`~/workspace/_smutbase6-fidelity-20261104/recovered-sources/` (blends +
renamed rars); the browser-download originals remain untouched in
`~/workspace/browser_downloads/sess-316653875/`. The only deletions in
this lane were the lane's own empty "starter" upload shells, removed
to retry the same files until they landed. Nothing else was deleted.

**Status change:** Track 1 recovery is DONE. Rebuild steps 5 (Megami)
and 6 (Menajerii) in the plan above are UNBLOCKED — the "BLOCKED on
source recovery" wording is superseded by this section. The rebuilds
themselves are NOT started here; they keep their place in the owner's
order (Chatur → Ryusan → Megami → Menajerii). The full rigs, morphs,
and textures the fidelity order demands for these two now exist in
hand: Parvati 469-bone GZM rig + 474 shape keys + 123 packed images;
Vixen 450-bone GZM rig + 2,509 shape keys + 124 packed images.
