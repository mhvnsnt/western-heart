# License Log — Multi-Arm Research 2026-10-19

Every item studied during this lane, with its license status and the pull/no-pull decision. Per the CONTINUOUS RESEARCH + PULL-IN law: open source first, honest license calls, never crack commercial software.

## Pulled

| Item | License | Evidence |
|---|---|---|
| N30Z3N/Blender-Wiggle-Bones-V3 | GPL-3.0 | GitHub API `license.spdx_id = GPL-3.0`; LICENSE file (35,149 bytes, FSF GPL v3 text) shipped verbatim in `wiggle-bones-v3/LICENSE` |

## Not pulled — license blocks

| Item | Status | Detail |
|---|---|---|
| aditiapratama/tentacle_rigs (Blender tentacle-rig generator) | **No license** | GitHub API `license = null`. 3 files, 0 stars, last updated 2023-08. Cannot verify redistribution rights — not pulled. |
| aresdevo/animaide (animation tools addon) | **No license detected** | 795 stars but no license on record — not pulled. |
| artellblender/springbones (spring/bouncy bones) | **No license** | 809 stars, no license file — not pulled. |
| Pauan/blender-rigid-body-bones | **No license** | 156 stars, no license file — not pulled. |
| mtb-tools/wiggle_bones (Jiggle Bone fork) | **No license** | Not pulled. |
| chambersu1996-wq/springpreview | MIT | License is clean but 0 stars, VRM-focused, unproven — not pulled (MIT would have been fine). |

## Not pulled — commercial / out of scope

| Item | Status | Detail |
|---|---|---|
| Auto-Rig Pro | Commercial (paid) | Its "duplicate or remove limbs to rig spiders, centaurs... or whatever!" is exactly the multi-limb feature wanted — documented as the commercial reference, never cracked. |
| tentacletk (m3trik/tentacle) | LGPL v3 | License is fine, but it's Maya-first: the Blender wrapper (`TclBlender`) is a stub with no slot library. Nothing useful to pull for Blender. |
| Goro MK Onslaught FBX (a9strack3d / DeviantArt) | Fan conversion, gray area | Already documented in `tools/limb-system/dxmmii/RESEARCH.md`; not redistributed. |
| thepiccio/Wiggle-2-Blender-5.2-Compatibility-Fix | GPL-3.0 | Clean license, but it's a patch for Blender 5.2 (we run 4.0.2) — the V3 pull covers our version. |

## Referenced without pulling (already in the environment)

| Item | License | Note |
|---|---|---|
| Rigify (Blender built-in) | GPL | Ships with Blender 4.0.2 at `~/workspace/tools/blender/`; no pull needed. |
| Blender 5.x Manual — Child Of constraint | CC BY-SA (docs) | Quoted with attribution; technique documented, not copied code. |
