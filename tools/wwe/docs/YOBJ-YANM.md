# YOBJ models and YANM animation clips (WWE 2K19)

Format reference for `yobj.py`, `yobj_to_gltf.py`, and `yanm.py`.
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

Name (16 chars) @0. **Parent index = u32 BE @0x30**
(0xFFFFFFFF = root). N/O/P floats @0x44/0x48/0x4C: N = mesh Y
(height), O = mesh Z (depth); P is NOT a mesh coordinate
(identical for L/R pairs). 87 parented bones (J_* + H_*) form one
tree rooted at J_Hips; 334 `m###_####` morph bones are
parentless. The bone structure order list (420 entries) covers
all bones except bone 0 ('vector'); it is NOT a topological order
(29 parent-after-child violations) — use explicit parents for
hierarchy, the order list only for weight decoding.

**Joint bind positions:** measured as weighted vertex centroids
— validated anatomical for all 23 checked skeleton bones (J_Hips
centroid (0,-106,2) vs N=-103.9; J_Head (0,-180.7,-12.1) vs
N=-180.5; J_Eye_L (3.3,-184.7,-13.9); perfect L/R mirroring).

### YOBJ array files (separate format, ModelArrayView)

Header `EA A1 59 00 01 00 00 00 01 00 00 00`, total count @0xC,
container count @0x10, object count @0x14; per-item 8-byte
entries at 0x20 (enabled byte, number u32); per-item 0x30-byte
records at 0x20 + count*8 (name 16 chars, X/Y/Z floats, RX/RY/RZ
floats, item count, start index). Scene-graph/object list, not
geometry.

### glTF conversion (`yobj_to_gltf.py`)

Mapping (x, y, z) -> (x, -y, -z) x 0.01 (cm -> m, right-handed,
no mirror). One mesh per sub-object; skin over all 421 joints
(hierarchy from the parent field, all roots parented under bone
0 'vector'); inverse bind matrices are pure translations
(rotations identity in v1 — bind pose renders correctly); weights
top-4 -> JOINTS_0/WEIGHTS_0, next up to 4 -> JOINTS_1/WEIGHTS_1;
morph targets as POSITION deltas with emote names in
`mesh.extras.targetNames`; materials named `{shader}_mat{material}`
with shader/material in extras, no textures embedded (the
name->DDS mapping lives in the ch PACs, not yet unpacked).

**v1 limits:** joint rotations unknown (the A–L bone fields are
undecoded — J_Hips has values pi and -pi/2 among them, suggesting
rotation data); no textures; morph-target normals not emitted.
Boundary edges exist on every mesh (229 on the head) — a mix of
natural part seams and strip-parser splits; the render shows a
solid model.

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

Two per standard clip (positions 16 and 20 in the sample clip).
Their +8 fields are NOT (index, length) pairs (they read as
absurd offsets like 63,504,439). They may be event/marker
records interleaved in the table. The parser flags them
(`special`) and does not validate their parts. Their data occupies
~404-408 bytes each in the data section (measured from the index
gaps around them).

### 61-bone variant clips

188 of 18,862 moves clips carry 61 bones with StartingIDs
0x0101/0x0104/0x0900 and part fields that do not fit the standard
layout (e.g. a 0x80000000 length sentinel, lengths like 0x900004).
Probably a 2K20-format clip. The parser flags their out-of-range
parts (`part_a_ok`/`part_b_ok`) instead of failing the clip.

### Known bone hashes (14, from WrestleMINUS's enum)

vector 0x0C5879E5, J_Hips 0xF91A7A26, Ch_rotation 0x0DAECC2E,
J_Spine1 0x3D185308, J_Head 0xF9D973BE, J_Neck 0xF91972B1,
J_Clavicle_L 0xD153E363, J_Shoulder_L 0xA46A2F43, J_Elbow_L
0x6742F8AA, J_Wrist_L 0xD4C2705A, J_MiddleF0–F3_L 0xB10CEB4C /
0xB10CAB4C / 0xB10C6B4C / 0xB10C2B4C. The rest of that enum is
sequential ordinals, not hashes. 159 distinct hashes seen across
the moves pack; 70 in a 200-clip sample.

**The hash function is unknown** — CRC32, Adler32, FNV-1,
FNV-1a, DJB2, SDBM, and Jenkins one-at-a-time were all tested
against the 14 known name/hash pairs: 0 matches. But the hash is
"smooth": right-side bones sit a few units from their left-side
counterparts (J_Clavicle_R is D153E37D vs J_Clavicle_L D153E363;
J_Shoulder_R A46A2F5D vs _L A46A2F43; J_Elbow_R 6742F8B4 vs _L
6742F8AA; J_Wrist_R D4C27044 vs _L D4C2705A), so L/R pairs can
still be identified by proximity + position in the chain. A
standard hash of the name is ruled out; a custom polynomial or
seeded hash is the remaining lead.

### Frame counts (do NOT trust)

WrestleMINUS reads channel flags (u16 LE 1/0xFF00) and a frame
count (u16 BE @+14) from Part A (StartingID < 1000) or Part B
(>= 1000). On 2K19 clips that read yields garbage (frame counts
like 61954, 52994). The parser returns `frames = 0` and exposes
the raw part bytes instead.

### Keyframe value decode — build plan (the remaining deep job)

Part A/B data look like a bitstream (J_Hips Part A:
`c9 cc f6 00 b6 cb 00 05 b4 c9 01 04...`) with possible
(float, u16, u16) 8-byte records in Part B (the last u16
increments 1,1,2 — frame numbers?). Turning these into
per-frame rotations/translations (→ glTF animation) needs:

1. **A known-pose clip pair**: two clips of the same move where
   one is a single static pose — the delta isolates the value
   encoding. The 0/1/2/3-bone clips in the catalog (109 of them)
   are candidates for near-static data.
2. **A second tool's output as ground truth**: run a reference
   YANM reader (WrestleMINUS's AnimationView) on the same clip
   and compare its channel values against the raw bytes.
3. **Bit-level differential analysis**: flip one input byte at a
   time in a short clip and watch which output values move.
4. Once values decode, emit glTF animation (rotation quaternions
   per joint per frame) and validate by rendering the first and
   last frames against a known move.

Estimate: a multi-hour reverse-engineering job, not a stub fix.
The parser + catalog are the foundation; do not claim keyframe
values work until a clip renders as a recognizable move.
