# Soulcalibur II (Xbox) — VXT Texture Format (Phase 13, JOB 1)

Verdict: **VXT is decoded.** Textures are Xbox DXT (DXT1/DXT3/DXT5,
stored **linear**) and P8 paletted (stored **Xbox-swizzled**), at
VXT-relative offsets, with up to 2 mip levels stored consecutively.
First textures decoded to PNG and viewed in real colors (see Proof).

## Sources / method

- Starting point: GRE PR #28 (MODEL-HUNT-PHASE2 §2) — VXT section
  relocator `FUN_00025300`, texture records stride 36 B at header+0x0c
  pointer, count u16 at +0x08, D3D texture-creation wrappers
  `FUN_000160c44` / `FUN_00153280`.
- Field semantics below come from that decompile (argument order into
  `FUN_000160c44`, pointer relocation targets) plus byte-exact size
  accounting across all 28 records of idx47 VMX#1's VXT section: every
  record's data span is exactly consumed by the next record's offset
  iff format = DXT block size and the +0x1c field = mip count. No field
  was assigned by guessing at pixels; the pixel decode was the last
  step and it confirmed the accounting.

## VXT section layout

Header (offsets from the `VXT.` magic):

| Off | Type | Meaning |
|---|---|---|
| 0x00 | u32 | magic `VXT.` (0x2e545856) |
| 0x04 | u8 | version (2) |
| 0x05 | u8 | relocation-list displacement (list at +0x08+byte5) |
| 0x06 | u8 | relocation-list count |
| 0x07 | u8 | flags; bit0 = already relocated |
| 0x08 | u16 | texture record count |
| 0x0a | u16 | count of 12-byte shared records at +0x10 pointer (0 in idx47 VMX#1) |
| 0x0c | u32 | → texture records (stride 36 B), VXT-relative |
| 0x10 | u32 | → 12-byte shared-record array (relocated + uploaded by the tail loop of `FUN_00025300`) |

Texture record (36 B):

| Off | Type | Meaning |
|---|---|---|
| +0x00 | u32 | → palette struct `{u32 data ptr, u32 count ≤ 0x100}` or 0 (none in idx47's set) |
| +0x04 | u32 | common dword (0x241b typical, 0x251b once; not needed for decode) |
| +0x08 | u32 | flags — 0xa2 exactly when 2 mip levels present, else 0 (28/28 records) |
| +0x0c | u16 ×2 | width, height |
| +0x10 | u32 | pixel-data offset, VXT-relative (relocated in place by `FUN_00025300`) |
| +0x14 | u32 | Xbox D3DFORMAT: **11 = P8 (paletted), 12 = DXT1, 14 = DXT3, 15 = DXT5** (size accounting: 12 → 8 B/block, 14/15 → 16 B/block, 11 → 1 B/px + palette) |
| +0x18 | u16 ×2 | width, height (descriptor copy; identical to +0x0c in 28/28) |
| +0x1c | u16 | mip levels present (1 or 2) |
| +0x1e | u16 | flags; bit2 set ⇒ relocator skips the data upload (`FUN_00153280`) |

Pixel data: level 0 first, then level 1 (half dims), each
`(w/4)·(h/4)` DXT blocks in plain row-major block order. **DXT records
are NOT swizzled**: a Morton-unswizzled decode of idx47 tex06
scrambles into block noise, while the linear decode is a coherent
texture (proof below). (The runtime presumably swizzles on upload via
`FUN_00153280`; the file storage is linear.)

**P8 records (format 11) differ**: pixel data is 1 byte/pixel palette
indices stored **Xbox-swizzled** (canonical bit-spread unswizzle at
texel level), and the palette comes from the record's +0x00 pointer:
a 12-byte palette struct `{u32 data ptr, u32 count (=256), u32 ?}`
(the header's +0x10 array holds these structs), palette data =
`count` × 4-byte entries in **B,G,R,A** byte order. Proof (viewed):
idx632 tex02 unswizzled = a human ear on skin with hair (Cassandra's
head texture); idx944 tex06 unswizzled = Spawn's chest emblem over the
black suit. The linear (non-unswizzled) reads of the same records are
streak-scrambled, and the DXT records are coherent ONLY linear — the
split is proven per-format, not assumed.

## Fighter ↔ texture mapping (evidence, not adjacency)

Each VMX carries its own VXT section (VMX header +0x18), so a bundle's
VMX#1 textures belong to that bundle's fighter **by construction**.
Inside the VMX, the assignment to mesh parts is pointer-exact:

- Part record (40 B) +0x0c → rec80 material record (GRE PR #30:
  rec80 = materials).
- rec80 +0x08 → primary VXT texture record (VMX-relative pointer,
  e.g. idx47 mat0 → VXT+0x98c14 = texture record 0).
- rec80 +0x0c → secondary VXT texture record or 0 (a second layer;
  materials with w0 low byte 2 / 0x20 flag carry one).

Confidence: **HIGH** for primary-texture assignment (byte-exact
pointers consumed by the game's own relocator). The secondary
pointer's runtime role (detail/alpha/env layer) is **not** asserted;
JOB 2 ships the primary texture as `baseColorTexture` only.

Parts whose material has texture pointer 0 (idx47 mat8) are
color-only in the source; they get no texture (no placeholders).

## Proof

Decoded from the verified local bundle copy
`~/workspace/scii-work/p10/idx47_v982.bin` (Mitsurugi, v982 entry 47;
NOT the banned stale `p2/v982_idx47.bin`), VMX#1 VXT section at
VMX+0x98c00, with `tools/vxt_decode.py` in this folder:

- `phase13-proof/idx47-tex07-mitsurugi-skin-sash.png` — texture 7,
  512×256 DXT1: skin tones, purple sash with stitched trim, chainmail.
  Viewed by the lane: real colors, coherent, recognizable as
  Mitsurugi's body/clothing texture.
- `phase13-proof/idx47-tex06-mitsurugi-tooled-leather.png` — texture
  6, 256×256 DXT5: tooled-leather panels with floral tooling, rivets,
  metal trim and pipes (armor/clothing). Viewed by the lane.

Size-accounting check (all 28 records, idx47 VMX#1): sequential data
offsets 0x480 → 0xa9080+ reconcile exactly with DXT block sizes × mip
counts; shared data offsets occur where two records reference the same
texture (tex13/tex14 → 0x5d880).
