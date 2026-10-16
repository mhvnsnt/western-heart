# Western Heart — Model Census & Blockers

**Status as of 2026-10-16.**  
Goal: every fighter that exists on disk or in the repo gets a front-facing T-pose render.  
Standard: [docs/TPOSE_RENDER_STANDARD.md](TPOSE_RENDER_STANDARD.md) (camera on −X, scale ×100, centered, gray bg).

## Ready to Render (GLB on disk)

These are already `.glb` and can be rendered with the current Blender pipeline:

### PR #170 roster (roster-integrate-phase1)
awa-pop, baek, dxmmii, king-tyrant, king-tyrant_alt1, kinpo, kinpo_alt1, lili, n3g4tiv0, nightwolf, pantera_alt1, phantom, purple-rain, rave, saku-ra, saku-ra_alt1, sam-ur-a1, skull, thor, waterfall, zafina (Mariposa), zui_alt1, zui_alt2

**Notes:**
- Most face correctly with camera on −X, no model rotation.
- **Zafina (Mariposa)** requires −90° Z + slight downward shift to center.
- DXMMII, Kinpo, Nightwolf, Rave may still need orientation checks if blank/side-facing.

### Tekken 3 donors (local)
t3_bryan, t3_gunjack, t3_xiaoyu, t3_yoshimitsu, t3_jin (soul-models)

**Notes:**
- Several render as exploded/fragmented geometry. Likely armature or scale issues. Need re-export or armature-applied versions before they are usable.
- Flagged previously as BLOCKED-rig in checklist.

### Other local
rin.glb, zen.glb, skull.glb (soul-tposes)

## Extracted but Not Renderable Yet

These were unpacked from zip/rar but are **Source engine** (`.mdl` / `.vvd` / `.vtx`) or other non-GLB formats. Need conversion (Crowbar, Blender Source tools, or similar) before Blender can import them.

| Archive | Extracted contents | Next step |
|---------|--------------------|-----------|
| shaheen.zip | .mdl / .vvd / .vtx + materials | Source → FBX/GLB |
| jin-t7.zip | (check nested) | Source or FBX conversion |
| miguel.zip | (check nested) | Source or FBX conversion |
| nina-revolution.zip | (check nested) | Source or FBX conversion |
| beast-king.zip | (check nested) | Source or FBX conversion |
| ganryu-t7-default.zip | (check nested) | Source or FBX conversion |

## Still Packed (need extraction)

25 archives remain in `/tmp/model-pull/` (and mirrored in `mhvnsnt/game-reverse-engineering`):

- **T7 FBX zips:** asuka-t7-fbx.zip, eddy-t7-fbx.zip, xiaoyu-t7-fbx.zip, steve-fox-t7-fbx.zip (some failed unzip — may be nested or corrupt)
- **Individual:** alisa.rar, anna-williams.7z, christie.7z, lee-chaolan.rar, julia-classic.rar, xiaoyu-t8.rar, yoshimitsu-t7.7z, zafina-t7.zip, nina-tekken1.rar, josie-diva.zip, heihachi-mishima.rar, etc.

**Blocker:** no `unrar` / `7z` on this machine. Need to install or extract elsewhere.

## Fully Blocked (not on this machine / not decoded)

| Set | Count | Blocker | Location |
|-----|-------|---------|----------|
| **Virtua Fighter 5** | 19 | `.farc` files need Windows extraction tool | Local teardown dir (not in working repo) |
| **Urban Reign** | 72 | Geometry not decoded; full ISO on GitHub | Release `urban-reign-iso-v1` on western-heart |
| **Soulcalibur 2** | — | Only movesets extracted; no 3D models | `mhvnsnt/western-heart` teardown |
| **TTT2** | 26 parts | Release exists, not extracted (disk space) | Release `ttt2-7z-v1` on western-heart |
| **Tekken 6** | — | File map cracked (PR #162); models still locked | `~/workspace/wh-repo/teardown/tekken6/` |
| **Rashid (SF5)** | — | Release exists | Release `rashid-models-20261013` |

## Missing Entirely (need hunting)

Bass, Zangief, Hugo, Kuma, Lars, Samir, Bryden.

## Render Status

| Category | Count | Status |
|----------|-------|--------|
| Confirmed front-facing | Mariposa (Zafina), + several PR #170 with camera-on-−X | Done / acceptable |
| Rendered but exploded | T3 Bryan, T3 Yoshimitsu, others | Need armature/scale fix |
| Not yet rendered | Remaining PR #170 + soul models | Queued |
| Cannot render yet | Source .mdl, packed archives, VF5, Urban Reign, SC2, T6, TTT2 | Blocked |

## Next Actions (priority)

1. Install `unrar` / `p7zip` and finish extracting the 25 archives.
2. Convert Source `.mdl` sets (Shaheen, etc.) to FBX/GLB.
3. Re-export or fix T3 models that explode (apply armature, correct scale).
4. Pull VF5 extraction onto a Windows box or find a Linux path for `.farc`.
5. Decode Urban Reign geometry or document the blocker permanently.
6. Continue batch-rendering every new GLB that becomes available using the camera-on-−X standard.
7. Update this doc and `docs/TPOSE_RENDER_STANDARD.md` as blockers clear.

## Handoff Notes for Agents

- **Do not guess or procedurally generate** models when teardown data exists (see AGENTS.md / RULES_NO_GUESSING).
- **Do not push WIP to main.** Feature branch + PR only.
- **Binary renders** cannot be pushed via the text-only `github___push_files` tool. Local PNGs stay local until a binary-capable path is used.
- **Zafina (Mariposa)** is the exception to the no-rotation rule: −90° Z + vertical center shift.
- All new T-pose work must follow `docs/TPOSE_RENDER_STANDARD.md`.

---
*Generated for handoff. Update as extraction and rendering progress.*
