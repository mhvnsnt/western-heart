# Tekken 3 USA Pose Solving — Verified Table Addresses (2026-10-13)

The pose pipeline (`PoseBuildMatrices`: pose vector → 18 joint matrices →
part assembly) was blocked on locating the animation tables in the USA
executable (`SLUS_004.02`). All tables are now located and **verified by
content** against the USA EXE.

## Verified USA addresses

| Table | USA address | Japan Rev.1 | Shift | Verification |
|---|---|---|---|---|
| `EULER_SLOTS` | `0x8001A330` | `0x8001A330` | none | byte pattern `[0,1,11,2,3,7,6,10,14,17]` present (matches animation.md) |
| `SIN_TABLE` | `0x8001E8C4` | `0x8001E8C4` | none | all 4096 s16 == `round(sin(i·2π/4096)·4096)`, 0 mismatches |
| `SQRT_TABLE` | `0x80098D08` | `0x800990AC` | −0x3A4 | 192-entry PsyQ mantissa table, exact analytic shape; dup at `0x8004AF40` |
| `LIMB_BASIS` | `0x80096EAC` | `0x800972D0` | −0x424 | 3×3 s16 exactly orthonormal |
| `SKELETON_OFFSETS` | `0x80096ECC` | `0x800972F0` | −0x424 | `[[0,0,0],[350,0,-100],[350,0,100],[0,0,0]]` — matches doc exactly |
| `LIMB_OFFSETS` | `0x80096EFC` | `0x800972F0+0x30` | −0x424 | `[[-140,0,0],[-140,0,0],[-160,0,100],[-160,0,-100]]` — matches doc exactly |
| `SPLINE_TABLE_BASE` | `0x8009671C` | `0x80096B40` | −0x424 | weight curves = B-spline basis; `A[0]=65536/6` exact; byte-index table monotonic |
| `CHANNEL_SHIFT` | `0x80096C24` | `0x80097048` | −0x424 | 49 bytes == `[1]*15 + [5]*34` |
| Motion seq. tables | `0x800954D0` (63), `0x800955CC` (41) | `0x800958F4`, `0x800959F0` | −0x424 | all 104 pointers dereference to valid sequences |

**Shift rule:** the `0x80096xxx` data region shifted −0x424 (USA = JP − 0x424);
the `0x8001xxxx` code region did **not** shift. (A prior handoff listed
`0x80096EAC/0x80096ECC/0x80096EFC/0x8009671C` as "Japan" addresses — they are
the USA addresses; the −0x424 shift had already been applied.)

## Tools

- `tools/local/usa_tables.py` — `ExeTables` bound to USA addresses; sanity
  assertions on load. `pose_to_slot_rotations()` runs `PoseBuildMatrices`
  (n0madic's verified port) with USA tables.
- `tools/local/usa_motion.py` — bit-exact `AnimDecodePose`/`AnimSplineSample`
  port on the USA spline tables. **Prefer over `pose_sample_analytic.py`**:
  the analytic version mis-models the game's first-segment weights (up to
  ~40 units / 0.2° error on first-segment interiors) and skips the game's
  even-quantization of `local`.
- `tools/local/pose_assemble.py` — full pipeline: motion bank → pose vector
  → 18 slot rotations → local matrices (anim rotation + KMD joint offset
  `(x, y, −z)`) → world matrices via part hierarchy → posed OBJ.
  Usage: `pose_assemble.py <kmd> <bank> <slot> <frame> --out model.obj`
- `tools/local/moveset_extract.py` — moveset extraction (see
  `movesets/MOVESET-SUMMARY.md`).
- `tools/local/validate_usa_spline.py` — USA spline table validation harness.

## Verification

King's stance (slot 0, frame 75) assembles into a coherent fighting stance:
skeleton segment lengths all match KMD offsets; head 437 from chest; feet
near ground; arms in guard. Renders in `renders/pose-check/`.

**Coordinate note:** +Y is DOWN in pose space (floor at y≈0, character at
negative y). The stance stream's frames 0–45 are a crouch-into-stance
transition; the held stance is frames ~45+.

## Moveset data

`movesets/` — all 7 fighters (King, Yoshimitsu, Xiaoyu, Jin, Bryan,
Heihachi, Gun Jack): 3,247 move rows, 1,602 attacks. Per-fighter JSON
(full move rows, branch lists with decoded inputs, event lists) + CSV
(frame-data sheets: frames, damage, active windows, hit freeze, step,
stance). `divmot99_common.bin` (BNS ID 279, 332 moves) extracted to resolve
common-bank animations (248 of King's 652 moves use it).
