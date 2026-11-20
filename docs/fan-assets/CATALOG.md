# Fan-assets catalog

Every accepted fan-made, reuse-licensed model, stage, and animation.

Machine-readable: [`catalog.json`](catalog.json).

| Name | Category | Author | License | Poly count | Format | URL | SHA-256 | box-storage release | WH move slots |
|---|---|---|---|---|---|---|---|---|---|
| Mixamo fighting animation set (curated) | animation | Adobe Mixamo | Mixamo free license | n/a (anim-only) | fbx → glb | https://www.mixamo.com | _pending manual download_ | _pending_ | idle, walk_fwd/bk, dash, crouch, jump, blocks, hits, knockdown, getup, jab/straight/hooks/uppercut, kicks, sweep, throws, victory/defeat, entrance |
| CC0 - Free Rigged Character | fighter | reinhpash | CC0 (page: CC-BY, crediting as CC-BY) | 27k tris | glb/fbx | https://sketchfab.com/3d-models/cc0-free-rigged-character-bf75eb2ffcb9444a90b62c3aeee04be2 | _pending_ | _pending_ | — (base mesh) |
| CMU MoCap martial-arts clips | animation | CMU / RancidMilk | Free / CC0 (verify per-pack) | n/a (mocap) | bvh → fbx/glb | itch.io (RancidMilk); mocap.cs.cmu.edu | _pending_ | _pending_ | idle, walk, punches, kicks, sweep, knockdown, getup, blocks |

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

## Binary acquisition note

Binaries require manual download (Mixamo needs Adobe sign-in; Sketchfab needs
click-through). Binaries go to private `mhvnsnt/box-storage` release assets.
SHA-256 recorded on upload. Parent agent to delegate browser download tasks.
