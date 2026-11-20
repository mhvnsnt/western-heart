# Render Sweep Worklog — 2026-10-19

Owner order: keep showing the models we haven't worked on yet (DOA models, Urban Reign models).

## Renders landed
All locked-standard front renders (front camera -X, ortho, white bg, per docs/RENDER-ORIENTATION.md):

| Model | File | State |
|---|---|---|
| bruno | docs/tpose-refs/bruno/p1_front.png | full color 2048² |
| dio | docs/tpose-refs/dio/p1_front.png | full color 2048² |
| cape-jones | docs/tpose-refs/cape-jones/p1_front.png | full color 2048² (proper locked-standard — replaces the old Babylon viewport screenshot) |
| michiko | docs/tpose-refs/michiko/p1_front.png | gray clay 1024² — 0 embedded textures, texture pass is follow-up (no-gate law) |
| star | docs/tpose-refs/star/p1_front.png | gray clay 1024² — 0 embedded textures, texture pass is follow-up (no-gate law) |
| torch | docs/tpose-refs/torch/p1_front.png | gray clay 1024² — 0 embedded textures, texture pass is follow-up (no-gate law) |
| yukihyo | docs/tpose-refs/yukihyo/p1_front.png | gray clay 1024² — 0 embedded textures, texture pass is follow-up (no-gate law) |

All 7 viewed with own eyes before delivery. The 4 gray-clay models are honest untextured states — they ship as-is per the NO-GATE law, texture pass is follow-up, not a gate.

## Honest notes
- Urban Reign: ZERO character model files on disk — nothing to render. Models need to be pulled/converted before a render pass is possible.
- DOA Bass Armstrong: is a GTA:SA mod package, not a renderable GLB — needs conversion before rendering.
- 5 dense ~1M-vert models (kiko pair, mariposa, purple-rain-main, saku-ra-main) need a stable render window (OOM under memory contention) — not rendered in this sweep.
- Work files: ~/workspace/_rendersweep/
