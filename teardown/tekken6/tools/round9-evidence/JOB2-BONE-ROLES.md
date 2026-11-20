# Tekken 6 PSP — ROUND 9 JOB 2 (B6′): BONE array roles PROVEN + skeletons

Date: 2026-10-21, round 9. Inputs: idx00 slot-1 BONE (8,032 B,
N=110), idx00 slot-12 BONE (1,664 B, N=22), idx04 slot-1 BONE
(10,768 B, N=146).

## BONE chunk layout (complete, byte-proven)

| Offset | Content |
|---|---|
| 0 | magic `BONE`, u32 ver 1, u32 100, u16 1, u16 0x600, u32 bone count N, f32 1.04 |
| 24 | offset table, 8×u32: `[64, 64+4N, 64+16N, 64+28N, X, names_off, scales_off, 0]` |
| 64 | **parents**: u32 × N (`0xFFFFFFFF` = root) |
| 64+4N | **local translations**: float3 × N |
| 64+16N | **local rotations**: float3 × N (Euler radians) |
| 64+28N | small section (u32 0 + float table; 32 B on idx00, larger on idx04 — contents not fully named, not needed for assembly) |
| names_off (table[5]) | **bone names**: 32 B × N, ASCII (Japanese anatomy: ATAMA=head, KUBI=neck, MUNE=chest, KOSHI=hips, KATA=shoulder, UDE=arm, TE=hand, MOMO=thigh, HIZA=knee, ASHI=foot, OYA/HITO/NAKA/KUSU/KO=fingers, KUCHI/MAYU/ME=face) |
| scales_off (table[6]) | **local scales**: float3 × N (uniform 1.04 on idx00 = the header f32) + 12 B zero trailer |

## Role proofs (from the data, not guesses)

- Parents: bone 0 = −1 (root `HARA_ROT1`); chains are
  anatomical: ATAMA(5)←KUBI(4)←MUNE2(2)←MUNE1(1)←root;
  TE_R(9)←UDE_R(8)←KATA_R(7)←SAKOTSU_R(6)←MUNE2(2).
- Rotations: values are 0 / ±1.571 (π/2 joint orients) —
  e.g. (1.571, 0, 1.571), (−1.571, 0, −1.571).
- Translations + rotations compose (parent world × (T·R),
  R = Rz·Ry·Rx from the stored Euler triple) into a clean
  T-pose bind skeleton — see bind check. The alternate Euler
  orderings score catastrophically worse (27.1 vs 1.66 on the
  anatomical target set), so the convention is pinned by data.

## Bind check (idx00, vs the Job-1 meshes) — PASS

World joint positions: HARA root (0, 1196, 0); KUBI
(0, 1570.5, 0); ATAMA (0, 1653.8, 0) — head-section mesh
spans y 1657–1906, the head joint sits at its base;
TE_R/TE_L (∓800.8, 1560, 0) — inside the slot-10 T-pose
mesh arm span (x ±981 incl. fingers); ASHI_R (−104, 135.2, 0)
near the floor. Overlay proof (VIEWED):
`renders/r9_idx00_skeleton_overlay.png` — every chain inside
the mesh point volume, arms horizontal, legs straight down.

## Shipped skeletons

- `models/idx00_skeleton_r9.glb` — 110 nodes, hierarchy +
  name + local TRS per node (glTF node tree, no mesh).
- `models/idx04_skeleton_r9.glb` — 146 nodes (the brief's
  146-body-bone package), same convention; spot checks:
  ATAMA (0, 1571.3, 0), TE_R (−781.8, 1480.3, 0),
  ASHI_R (−98, 127.4, 0).

## Skinning state (honest)

The NDPP vertex streams DO carry weights (u8 per weight slot,
sum = 128; slot count from VTYPE bits 14–16) — but the
per-unit **bone palette** (which skeleton bones a unit's
weight slots 0..k map to) is not yet proven. The unit header
words 3–4 are the standing candidate (identical across units
sharing strip sets, varying across units); until their
semantics are read, skinned GLBs are NOT shipped — the mesh
GLBs are static and the skeleton GLBs are node hierarchies.
That is the one remaining B6′ sub-item.
