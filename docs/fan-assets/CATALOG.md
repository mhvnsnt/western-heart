# Fan-assets catalog

Every accepted fan-made, reuse-licensed model, stage, and animation.

Machine-readable: [`catalog.json`](catalog.json).

| Name | Category | Author | License | Poly count | Format | URL | SHA-256 | box-storage release | WH move slots |
|---|---|---|---|---|---|---|---|---|---|
| _batch 1 in progress_ | | | | | | | | | |

## Fields

| Field | Required |
|---|---|
| `name` | yes |
| `url` | yes (canonical page, not a CDN hotlink) |
| `author` | yes |
| `license` | yes (exact SPDX or Sketchfab label) |
| `poly_count` | yes (triangles or verts; say which) |
| `format` | yes (glb / fbx / obj / bvh / …) |
| `category` | `fighter` \| `stage` \| `animation` |
| `sha256` | yes once binary is in box-storage |
| `box_storage_release` | yes (tag + asset name) |
| `wh_move_slots` | for animations: list of WH slots |
| `credit_line` | yes (paste-ready for CREDITS.md) |

## WH animation → move slots

`idle`, `walk_fwd`, `walk_back`, `dash_fwd`, `dash_back`, `crouch`, `jump`,
`block_high`, `block_low`, `hit_standing`, `hit_crouching`, `knockdown`, `getup`,
`jab`, `straight`, `hook_l`, `hook_r`, `uppercut`, `low_kick`, `mid_kick`,
`high_kick`, `sweep`, `throw_attempt`, `throw_break`, `special_1`, `special_2`,
`rage_art`, `victory`, `defeat`, `entrance_idle`
