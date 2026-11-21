# YOBJ models and YANM animation clips (WWE 2K19)

Format reference for `yobj.py`, `yobj_to_gltf.py`, `yanm.py`,
`yanm_decode.py`, and `yanm_to_gltf.py`.
Verified against real 2K19 data (see README for the verification
summary). All YOBJ/YANM integers are big-endian unless noted.

## YOBJ (character model, magic `JBOY`)

### File header

| Field | Offset | Notes |
|---|---|---|
| SubItemCount | 0x18 | number of sub-objects (meshes) |
| HeaderStartOffset | 0x1C | +8 = first sub-object header |
| BoneCount | 0x20 | 421 in ch10002 |
| TextureCount | 0x24 | 123 in ch10002 |
| BonesStartOffset | 0x28 | +8 = first bone record |
| TextureStartOffset | 0x2C | +8 = texture name table (0x10-byte names) |
| ShaderStartOffset | 0x30 | +8 = shader table (0x20-byte records) |
| ShaderCount | 0x34 | |
| EmoteNameCount | 0x48 | 110 in ch10002 |
| EmoteNameStartOffset | 0x4C | +8 = emote names (0x10 bytes each) |
| BoneStructureCount | 0x50 | 420 in ch10002 |
| BoneStructureStartOffset | 0x54 | +8 = bone order list (u32s) |

### Sub-object headers (0xB8 bytes each)

VertexCount @0, Rendered boolean @7, WeightCount @0x5C,
VertexHeadCount @0x64, VertexOffset @0x68, WeightOffset @0x6C,
TextureCordOffset @0x70, NormalsOffset @0x74, shader name (16
chars) @0x7C, MaterialIndex @0x90, ParameterCount @0x94,
ParameterOffset @0x98, FacesOffset @0x9C, TextureCordCount @0xA0.

### Vertices (28 bytes each, BE floats)

X, Y (up, negative — the model hangs downward from Y=0), Z, RX,
RZ, RY, Weight. Units are centimetres; the model is ~196 cm tall,
arms span +/-86 cm. File bounds X[-86,86] Y[-196.3,0.1]
Z[-24.4,16.4].

### Vertex heads (morph targets)

A table of u32 offsets at VertexOffset+8, one per head; head data
starts at table value +8. Multiple heads = morph targets: 110
emotes + neutral = 111 heads on face sub-objects.

### Skin weights (8-byte records: 4-byte Num + f32 weight)

Vertex-major: `WeightOffset+8 + v*8*WeightCount + j*8`.
Per-vertex weights sum to exactly 1.0 (verified on all 25,026
verts of ch10002).

**Num decode (solved after several wrong theories):** Num is an
index into the bone structure order list with a mixed-endian
quirk — if byte1 == 0 the index is byte0, otherwise it is
(byte0 << 8) | byte1; bone = struct_order[index]. (0xFF, 0xFF) is
the unused sentinel (28,857 slots, total weight 0.0 — float
noise). WrestleMINUS reads Num as a BE u32, which is wrong for
2K19.

### Normals / UVs

Normals: 12 bytes/vertex (X, Y, Z BE floats). UVs: 8
bytes/vertex (U, V BE floats; file V is top-origin like glTF,
use as stored).

### Faces (tri-strips)

FaceListOffset+4 = u32 index count; u16 BE indices at +12
(1-based in the strip parser). The strip-splitting + winding
logic follows WrestleMINUS's port faithfully. Winding verified
against stored normals (head mesh: 7,649 agree, 0 disagree).

### Bones (0x50 bytes each)

Name (16 chars) @0. **Parent-relative offset = 3 BE floats @0x10**
(in the parent's local frame; every bone's long axis is local +X
— knee/foot/toe/shoulder/elbow/wrist offsets are (length, 0, 0),
e.g. knee (43.65, 0, 0), foot (48.48, 0, 0)). **Rest orientation
= 3 BE floats @0x20** (Euler XYZ radians, relative to the
parent; J_Hips (pi, 0, -pi/2), J_Leg_L/R (0, 0, -/+175 deg),
J_Foot (0, -62 deg, 0), J_Wrist_L/R (-/+90 deg, 0, 0),
J_Clavicle (0, 161 deg, +/-80 deg)). **Parent index = u32 BE
@0x30** (0xFFFFFFFF = root). Mesh position (X, N, O) @0x40/0x44/
0x48: N = mesh Y (height), O = mesh Z (depth); P @0x4C is NOT a
mesh coordinate (identical for L/R pairs). 87 parented bones
(J_* + H_*) form one tree rooted at J_Hips; 334 `m###_####`
morph bones are parentless. The bone structure order list (420
entries) covers all bones except bone 0 ('vector'); it is NOT a
topological order (29 parent-after-child violations) — use
explicit parents for hierarchy, the order list only for weight
decoding.

**Joint bind positions:** the rest orientations + offsets
reproduce the bind pose exactly by forward kinematics
(`YOBJ.rest_fk()`, verified 2026-11-19: mean error 3.6 cm vs the
mesh, all of it centroid-vs-joint offset — the FK joints sit on
the true pivots: hips (0,-108.7,0), knee height 58.2 cm, wrist
within 2 cm of its centroid). The weighted vertex centroids are
NOT the pivots for long bones: leg/shoulder/knee centroids sit
mid-segment (thigh centroid height 66 cm vs the 101.6 cm hip
joint; shoulder centroid X +/-42.8 vs the +/-20 joint), so the
v1 claim that centroids are anatomical is corrected here — use
the FK for pivots, centroids only for the parentless morph
bones (whose offsets are not mesh positions).

**Morph bones** (`m###_####`, 332 in ch10002) carry heavy skin
weights all over the body, not just the face (435 vertices are
100% morph-weighted; sub01 has 2583/4698 morph-weighted slots).
They are parentless leaves in the file, so the converter parents
each to its nearest skeleton bone (by bind-pose distance) with a
local transform reproducing its exact world bind pose (centroid
position, identity rotation) — otherwise the mesh rips apart the
moment the skeleton animates. Their true runtime parenting is
still unknown; the proximity attachment is a v1 approximation
that keeps the bind pose exact and the animation coherent.

### YOBJ array files (separate format, ModelArrayView)

Header `EA A1 59 00 01 00 00 00 01 00 00 00`, total count @0xC,
container count @0x10, object count @0x14; per-item 8-byte
entries at 0x20 (enabled byte, number u32); per-item 0x30-byte
records at 0x20 + count*8 (name 16 chars, X/Y/Z floats, RX/RY/RZ
floats, item count, start index). Scene-graph/object list, not
geometry.

### glTF conversion (`yobj_to_gltf.py`)

Mapping (x, y, z) -> (x, -y, -z) x 0.01 (cm -> m, right-handed,
no mirror — the map is diag(1,-1,-1), a 180-degree rotation
about X, so rotations conjugate cleanly: R_gltf = C @ R @ C).
One mesh per sub-object; skin over all 421 joints (hierarchy
from the parent field, all roots parented under bone 0 'vector'
except morph bones, which attach to their nearest skeleton bone
— see above); inverse bind matrices are the full inverse of
each joint's world transform; weights top-4 -> JOINTS_0/
WEIGHTS_0, next up to 4 -> JOINTS_1/WEIGHTS_1; morph targets
as POSITION deltas with emote names in
`mesh.extras.targetNames`; materials named `{shader}_mat{material}`
with shader/material in extras, no textures embedded (the
name->DDS mapping lives in the ch PACs, not yet unpacked).

**v2 skeleton (2026-11-19):** joints use the decoded bind pose
(local offsets + rest orientations) instead of the v1 centroid
positions + identity rotations. Node translation = parent-frame
offset, node rotation = rest orientation (quaternion); IBMs are
the full rigid inverse. The bind pose renders identically to v1
(verified in Blender); the skeleton is now animation-ready (see
`yanm_to_gltf.py`).

**v2 limits:** no textures; morph-target normals not emitted.
Boundary edges exist on every mesh (229 on the head) — a mix of
natural part seams and strip-parser splits; the render shows a
solid model. 5 of the 47 entrance-prop YOBJs fail conversion
(truncated files / out-of-range indices — see the W4 lane notes).

## YANM (animation clip, magic `YANM`)

### Header

`YANM` @0; u32 BE total length @4 (the clip's real length — the
file may carry YANMPack padding past it, rounded up to 0x20
blocks); u16 BE bone-entry count @0xA; entries start @0x10,
chained by each entry's own length field (u16 BE at +2).
**Entry count = count_field - 1** (loop 0..count-2).

### Bone entry

| Offset | Field |
|---|---|
| +0x00 | u16 BE StartingID (0x4000/0x4100/0x5000/0x5100 in standard clips; 0x0001 = special record, see below) |
| +0x02 | u16 BE header length (0x10 = Part A only, 0x18 = A+B, 0x28/0x30 = A+B+extra) |
| +0x04 | i32 BE bone hash (only 14 known by name — see below) |
| +0x08 | u32 BE Part A index (data starts at index+8) |
| +0x0C | u32 BE Part A length in **4-byte units** |
| +0x10 | u32 BE Part B index (absent on 0x10-long entries) |
| +0x14 | u32 BE Part B length in **4-byte units** |

Entry lengths vary: 0x10, 0x18, 0x28, 0x30 all occur. Longer
entries have trailing bytes after the pairs (0x28 entries: 16
bytes; 0x30 entries: a possible third pair + 16 bytes of floats
— e.g. J_Hips trailing floats ~= (0.0002, -160.6, 91.2, -6.9),
meaning unknown).

**Part lengths are x4 bytes, NOT x8 as WrestleMINUS assumes:**
the gaps between consecutive part indices equal length*4 for
every part checked (e.g. a Part B of length 39 fills exactly the
156 bytes before the next part). One exception seen: J_Hips'
Part B in one clip spans 352 bytes for length 44 (x8) — open
question, possibly an 8-byte record type on that bone.

### Special entries (StartingID 0x0001)

Two per standard clip (positions 16 and 20 in the sample clip):
the two knee bones. Their data index lives at **+0xC** (not +8);
data starts at index+8 (confirmed by both neighbours: knee L
index 2140 -> data at 2148, knee R 2864 -> 2872). The +8 field
reads (0x03C9 = 969, keyframe count 55/56?). The ~404-408-byte
knee block is NOT 4-byte records (no window sums to the frame
count under any dt byte position) — its format is still open.
The parser flags them (`special`); `yanm_decode.py` exposes the
raw block via `knee_gap()`.

### 61-bone variant clips

188 of 18,862 moves clips carry 61 bones with StartingIDs
0x0101/0x0104/0x0900 and part fields that do not fit the standard
layout (e.g. a 0x80000000 length sentinel, lengths like 0x900004).
Probably a 2K20-format clip. The parser flags their out-of-range
parts (`part_a_ok`/`part_b_ok`) instead of failing the clip.

### Known bone hashes (position-mapped, standard 23-bone order)

Standard 23-bone order: vector, J_Hips, Ch_rotation, 0DAECC2D,
J_Spine1, J_Head, J_Neck, Clavicle_L, Shoulder_L, Elbow_L,
Wrist_L, Clavicle_R, Shoulder_R, Elbow_R, Wrist_R, J_Leg_L,
J_Knee_L (special), J_Foot_L, J_Toe_L, J_Leg_R, J_Knee_R
(special), J_Foot_R, J_Toe_R. Known by name (WrestleMINUS enum
+ position mapping): vector 0x0C5879E5, J_Hips 0xF91A7A26,
Ch_rotation 0x0DAECC2E, J_Spine1 0x3D185308, J_Head 0xF9D973BE,
J_Neck 0xF91972B1, J_Clavicle_L 0xD153E363, J_Shoulder_L
0xA46A2F43, J_Elbow_L 0x6742F8AA, J_Wrist_L 0xD4C2705A,
J_Clavicle_R 0xD153E37D, J_Shoulder_R 0xA46A2F5D, J_Elbow_R
0x6742F8B4, J_Wrist_R 0xD4C27044, J_Leg_L 0xCCB8C530,
J_Leg_R 0xCCB8C52E, J_Knee_L 0xEC2C1192, J_Knee_R 0xEC2C118C,
J_Foot_L 0xFD6851FA, J_Foot_R 0xFD6851E4, J_Toe_L 0x4DF84531,
J_Toe_R 0x4DF8452F, J_MiddleF0–F3_L 0xB10CEB4C / 0xB10CAB4C /
0xB10C6B4C / 0xB10C2B4C. 0DAECC2D (twin of Ch_rotation
0x0DAECC2E, adjacent entry, same clips) is still unnamed —
likely the character-position twin of the character-rotation
track. 159 distinct hashes seen across the moves pack; 70 in a
200-clip sample.

**The hash function is unknown** — CRC32, Adler32, FNV-1,
FNV-1a, DJB2, SDBM, and Jenkins one-at-a-time were all tested
against the known name/hash pairs: 0 matches. But the hash is
"smooth": right-side bones sit a few units from their left-side
counterparts (see the L/R pairs above), so L/R pairs can still
be identified by proximity + position in the chain. A standard
hash of the name is ruled out; a custom polynomial or seeded
hash is the remaining lead.

### Frame counts (decoded 2026-11-19)

Every Part A and Part B (except J_Hips Part B) is a sequence of
4-byte records `(v0, v1, v2, dt)` where dt = frames until the
next keyframe; **the dts of any part sum to the clip's total
frame count**. Validated on 200 random clips: 197/200 have ALL
parts agreeing on one frame total. `yanm_decode.py` takes the
majority vote of the part dt-sums (293/300 random clips have
trusted counts, >=80% agreement). Frame counts range 1-926.
(WrestleMINUS's channel-flag/frame-count read yields garbage on
2K19 clips — do not use it.)

### Keyframe value decode — Part A (decoded 2026-11-19)

Part A values are 3 signed bytes: **Euler rotation angles, 1
unit = 360/256 degrees, wrapping at +/-180 degrees** (values
near +/-127/-128 are near the wrap point — the clavicle X flips
between +127 and -128 as it passes 180 degrees). Zero = rest
pose (all-zero clips reproduce the T-pose exactly). Quaternion
encoding is ruled out (12.8% of records have |v|/127 > 1).

**Rotation formula** (validated by forward-kinematics stick
figures against the decoded skeleton, then by Blender mesh
renders — the identity mapping gives crumpled impossible poses,
this mapping gives coherent standing/kicking/walking poses):

```
R_anim = Rx(v2) @ Ry(v0) @ Rz(v1)   # byte0 = Y, byte1 = Z, byte2 = X
R_local = R_rest @ R_anim           # R_rest = YOBJ rest orientation
```

Euler order for R_rest is XYZ; R_anim is composed as
Rx(v2)·Ry(v0)·Rz(v1) (matrix product). `yanm_to_gltf.py`
emits R_local per joint per frame as glTF rotation keyframes
(times at 60 fps, quaternions kept on one hemisphere so the
wrap slerps correctly; keyframe values are unwrapped before
interpolation so a wrap jump does not swing through 0 degrees).

**Elbow quirk:** elbow bytes 0 and 2 are binary flags (-128 or
0, flipping in blocks), not rotations — treat -128 as 0, leaving
a clean 1-DOF hinge on byte1. (Confirmed across clips: elbow
X/Z are never any other value.)

**Leg twist quirk:** the leg bones' byte2 (local-X twist)
carries a 180-degree offset — stored values cluster near
+/-180 degrees, which points the feet backward; adding 180
degrees (mod 360) makes the feet point forward (toe-vs-hips
facing metric over 3 clips: mean dot -0.27 raw, +0.25 with the
offset). V1 approximation: the exact mechanism is not yet
understood, but the twist does not affect joint positions.

**Validation:** stick-figure FK on 5+ clips (moves + entrance)
under 96 composition/order/permutation/sign combinations — the
winning formula is the only one giving coherent human poses;
Blender mesh renders of an animated GLB (ch10002 + clip
00100000, 110 frames) show a coherent kicking figure with
limbs attached and no shredding (the morph-bone proximity
parenting in the v2 converter is what makes the mesh hold
together — without it the static morph bones rip the mesh).

### Still open

- **Part B values:** same 4-byte dt structure (sums to the frame
  count), but values jump up to ~45 units/frame — not a direct
  spatial signal in the Part A unit. Cumsums wander (not
  delta-encoded). Ch_rotation B Z shows a low-frequency trend
  (+/-100) plus high-frequency noise (+/-30). Meaning unknown.
- **J_Hips Part B (root motion):** 8-byte records (3x i16 BE +
  u16 BE; byte 6 always 0, byte 7 in {0,1,2,4}). The u16 does NOT
  sum to the frame count (ratio 0-0.83, mean 0.40 over 107
  clips). Pure quaternions ruled out (BE |v|^2 > 1 in 47/1218
  records, max 1.82). Values jump wildly (not smooth
  translations). Until this decodes, `yanm_to_gltf.py` animates
  in place (no root motion).
- **Knee-gap format:** see Special entries above. Knees stay
  straight in v1 animation (no bend data applied).
- **0DAECC2D:** unnamed bone hash (see above).
- **Hash function:** unknown (see above).
