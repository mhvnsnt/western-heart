# Urban Reign — character skinning format and decoder

Status: character meshes decode to self-contained skinned GLBs with
`teardown/urban-reign/tools/ur_decode.py`. This doc records the format
as proven from the data files and cross-checked against the game's
own code in SLUS_212.09 (Ghidra 12.1.4, r5900 language from the
EmotionEngine-reloaded extension — see URBAN-REIGN-RESEARCH-PULLINS.md).

## File layout

- A character PPK = 0x80-byte `fncc` header + the character's `.vmd`
  model verbatim (char001.ppk[0x80:] is byte-identical to chr01.vmd
  from DVD000.AFS) + a trailing texture-candidate region (uncracked,
  see "Open" below).
- The `.vmd` header (0x0000–0x1FFF) holds an object graph, the DMA
  packet descriptor table, three palette records, and a bone-name
  pool near the end of the file (49 names in chr01/chr02, same set and
  order: MUNE1, MUNE2, KUBI, ATAMA, SAKOTSU_R/L, KATA_R/L, UDE_R/L,
  TE_R/L, KOSHI, MOMO_R/L, HIZA_R/L, ASHI_R/L, TSUMASAKI_R/L, facial
  bones MIKEN/MAYU/EYE/MABUTA/AGO/KUCHI, plus constraint helpers with
  `__rot`/`__prot`/`__slerp`/`__const` suffixes and `j__swing`,
  `yR__swing`, `yL__swing`). GLB joints are emitted as `bone_<id>`
  because the name↔node-id mapping is not yet proven.
- Vertex stream: 0x2000–0x56000 in .vmd coordinates.

## Vertex stream = pre-baked VU1 DMA packets

The descriptor table sits in the header (32-byte entries
`[u32 0x300000XX, u32 packet_off, 0, 0, 0x10000000, 0, 0, 0]`, XX =
packet size in quadwords; u32 `0x60000000` markers separate DMA
groups — 17 groups in chr01). Each packet has a 32-byte header
(vertex count in the `0x8000|count` word) followed by vertex records
tiling exactly to the next packet.

Vertex record = N influence pairs + UV row + GS color row
(r, g, b, a on the 0..128 GS scale):

- influence pair row 1: `(w*px, w*py, w*pz, w)`
- influence pair row 2: `(w*nx, w*ny, w*nz, slotbits)`
- `slotbits = (0x8000 if last influence) | slot*4`;
  `slot = (bits & 0x7fff) // 4` is a palette-local index (0..20),
  NOT a global bone id.

**Positions and normals are stored premultiplied by the weight.**
Proof: `|stored_normal| == w` exactly for every influence. This
matches the game code path: the VU1 skinning microprogram (ELF
`.vutext`, microprogram at VU1 address 0x1D98) sums
`M_bone * stored` with no separate weight multiply — "bone matrix
addressed by the w of the weight" (urban-reign-recomp,
docs/PROGRESS.md). World position of a vertex:

```
world = sum_k  W[bone_k] @ stored_k
```

where `W[bone]` is the bone's world matrix in the authored pose;
its translation term is implicitly weighted because the stored
positions carry `w`.

## Topology: ADC triangle strips (supersedes the PR #305 reading)

Each packet's vertices form a PS2 GS triangle strip. The fourth
float of the UV row is the GS **ADC bit**: a vertex with flag 1
starts a new strip segment (triangles spanning the boundary are
suppressed), and winding alternates along each segment. Faces must
never be built across packet boundaries.

Proof (chr01, local assembly, faces whose longest edge > 0.25 —
authored edges are ~0.02–0.07): with plain consecutive-triples the
clean groups tear (grp15 24/192 bad, grp2 41/202); with ADC strips
grp0/1/5/6/7/14/15/16 have **zero** bad faces locally and the
assembled char001 GLB has 25 bad of 2009 (1.2%). PR #305's
"triangle list" conclusion was the special case you get when the
ADC bit is ignored.

## Where bind matrices come from

They are **not stored as matrices in the character files**, and the
ELF's bone matrices are computed at runtime from per-node
Euler+position data (recomp: func_101628 Euler→matrix, caller chain
0x1018E8 ← 0x20bf84). The decoder recovers them from the skinning
data itself, exactly:

For two slots a, b blended on the same vertex, the unpremultiplied
local points/normals satisfy `q_b = R q_a + t` to float precision,
with `(R, t) = W_b^-1 W_a` the relative bind transform. Fitting
these relations per piece (Kabsch, reflections allowed — mirrored
bone frames exist) recovers every bone's world matrix up to one
frame per connected component of the relation graph. There is no
approximation in this step: residuals on true relations are < 0.002,
and a placed vertex's individual influences imply the *same* world
point (measured spread 0.0000 on multi-influence vertices).

## Palette assignment (slots → bones), self-validating

The header graph stores palette list records
(`01 <tag> 03 <n> <n bone ids>`). chr01's are:

- P27 @.vmd 0x114: [0,1,8,9,43,10,11,44,45,4,5,6,7,46,47,48,2,3,49,50,12,17,51,13,52,53,54]
- P16 @.vmd 0xa8: [35,30,36,31,37,38,33,39,32,34,40,41,42,1,2,3]
  (a second identical copy @0x3b8)
- P6 @.vmd 0x7c: [10,11,44,6,7,46]

Every character's header carries its own records (permutations of
the same bone sets at character-specific offsets; e.g. char015's
largest is an 18-entry record). The decoder's candidate families
are the union of: the three engine-standard tables above, the
character's own parsed header records (exact duplicates of the
base tables dropped), and — only when some piece's slots exceed
every real palette, e.g. char015 grp11 with maxslot 30 — an
identity (node-order) family. Frame-fit validation is the arbiter:
a wrong family never fits, so the union cannot corrupt a decode;
each character's stats record the families available and used.

The assignment unit is a **piece**: a contiguous packet range of one
DMA group. A group can batch two sub-objects with different palettes
(proven on chr01 grp14/grp15), so pieces split at packet boundaries
where the slot set changes; if splits deadlock, pieces atomise to
single packets. Within a piece, slots form **islands** (connected
components of the blend-relation graph) whose local frames are
exact internally but mutually unconstrained — all fitting is per
island.

A piece's candidate = (palette, window offset, forward/reversed);
slot s maps to `palette[w0 + s]`. Assignment runs in stages:

1. **Trusted-skeleton growth.** The largest piece seeds a skeleton
   under each of its candidates. A piece joins as *proven* only if
   a candidate anchors every island (≥1 shared bone) and every
   island with ≥2 shared bones fits the trusted skeleton's frames
   with worst residual < 0.02 (single-bone "fits" are exact for any
   candidate and prove nothing; wrong full fits are off by tenths).
   Joining pieces extend the skeleton island by island. Pieces
   whose bone sets are disjoint from the main skeleton grow as
   separate components and merge (bone ids are global; on collision
   the earlier component's frame wins).
2. **Final placement.** Pieces never proven (e.g. single-bone
   accessories) are placed per packet by best frame-fit against the
   merged skeleton. Their stats residual is reported as −1.0,
   meaning "placed by a single-bone anchor, not independently
   validated" — the inventory flags these pieces explicitly.
3. **Surface polish (`polish_by_faces`).** Bone frames are
   near-axis-aligned, so a wrong palette can fit frames yet tear
   the surface. Each piece is re-scored under every candidate by
   its ADC-strip long-edge face count, leave-one-out (its
   exclusively-owned bones removed from the skeleton first); a
   strictly better candidate replaces the assignment and re-frames
   only that piece's own bones, so a flip cannot move any other
   piece. On chr01 this step fixes grp0/1/2 (e.g. grp2 → P16
   window 0 reversed) and cuts long-edge faces from 157 (list
   topology, pre-polish) to 25 of 2009.

Assembly then places every vertex by the global formula above —
no per-piece frame is ever applied to vertices, so the exported
skin is consistent with the exported skeleton by construction
(verified in Blender: evaluated skinned positions equal the stored
positions exactly; and by an independent glTF skinning check,
max deviation 3.7e-08).

## The authored pose is an action stance, not a T-pose

The meshes are authored in dynamic fighting stances in native model
space; the engine poses them at runtime from the animation data.
chr01, for example, is a crouched stance: one leg planted, the
other extended, arms guarding — per-bone vertex centroids sit
beside their joints (median offset ≈ 0.1) across all 37 bones, and
the same body plan appears in every decoded character. The GLBs
deliberately keep the authored pose and orientation exactly as
decoded; no cosmetic re-posing is applied.

## What the ELF decompilation established

Ghidra project: SLUS_212.09 (6,366,044 bytes, MD5
0fa29bd55638f9ebe49feb494d4decd5), vaddr = fileoff + 0xFF000, no
symtab. Debug strings name `prog/game/kg_human.cpp` (0x6b4c28) and
`prog/game/kg_objdata.cpp` (0x6b3a98).

- FUN_001e7ea8 (human update): `human_obj+0x5c = *(chara+0x98) + 0x80`
  — chara+0x98 points at the PPK buffer; +0x80 is exactly the fncc
  header size, i.e. the .vmd body. The code that WRITES chara+0x98
  (the byte-stream loader itself) was not located in four targeted
  decompilation passes; the framework region 0x28e000–0x292000 is the
  AFS/file layer (FUN_0028e3f0 streaming state machine,
  FUN_00290270/FUN_00290568 file lookup) and FUN_00123f10 is a
  scene-graph node factory. The decoder therefore recovers bind data
  from the file data (above), which the format makes exact.
- FUN_00292670 = animation sampler (dequant tables at 0x663ac0 /
  0x663cc0 / 0x663ec8); FUN_00299130 = animation track getter
  (track = `*(anim+0x10) + *(*(anim+0x0C) + bone*4)`).
- kg_objdata registers the host path `HST:/team/f090/program/data` +
  `obj_data.bin` — a development leftover; the shipped `.vmd` files
  are that serialization family.

## Per-character isolation

Every GLB is fully self-contained: its own skeleton copy, its own
skin, no shared rig object, no shared animation state. The batch
pipeline runs one fresh Python process per character
(`batch_decode.sh`, `xargs` over PPKs) and the decoder resets all
state per run, so no mutable state can carry across characters; a
defect or fix for one character cannot shift another's pose. Repo
layout stays per-character under
`teardown/urban-reign/models/charNNN/`.

## Open (honest gaps)

- Textures: the PPK tail / .vmd 0x5A000+ region is the texture
  candidate; no TIM2 headers exist and the format is uncracked
  (PR #306 state stands). GLBs ship untextured.
- Some DMA groups use an s16-packed vertex format (chr01 groups
  9–13, small accessory objects) — not decoded; those vertices are
  absent from the GLBs and counted in the inventory.
- `.gyu` motion files: layout known (motion headers carry a bone
  count of 21 and per-motion offsets; 024_BONES.gyu is a 744-byte
  facial set of 14 × 44-byte records) and the runtime sampler is
  identified, but full motion decode is not done. Animations are
  not embedded in the GLBs.
- Mission binaries (256 in the repo) are not decoded.
- The `.vmd` header object-graph grammar is only partially decoded
  (palette records and the DMA table are proven; the per-object
  property-bag blocks are not); the decoder bypasses the rest
  empirically via the DMA table.
- Bone-name ↔ node-id mapping unproven (joints named `bone_<id>`).
