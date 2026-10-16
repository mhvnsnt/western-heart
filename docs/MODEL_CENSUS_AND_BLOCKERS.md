# Western Heart — Model Census & Blockers (Updated)

**Status as of 2026-10-16.**  
Goal: every fighter that exists on disk or in the repo gets a front-facing T-pose render.  
Standard: [docs/TPOSE_RENDER_STANDARD.md](TPOSE_RENDER_STANDARD.md).

## Confirmed Sets (were under-documented)

### Rashid (Street Fighter V)
- **Location:** `teardown/street-fighter-5/models/rashid/`
- **Variants:** Default (XPS, 48k verts), Air Man (XPS, 34k verts), SFM (Source .mdl)
- **Status:** Models present. XPS needs conversion to GLB/FBX before Blender render. SFM is Source engine (needs Crowbar/Blender Source tools).
- **Note:** Middle Eastern wind fighter. Owner request 2026-10-13.

### Brad Hawk / Urban Reign
- **Brad Hawk** is the protagonist of Urban Reign (brawler-for-hire, Green Harbor). Not a separate model — he is one of the 72 `char*.ppk` fighters.
- **Location:** `teardown/urban-reign/`
- **Extracted:** 72 fighter PPKs (`ppks/chars/char001–char072`), 7 stage PPKs, motion pools, AFS map.
- **Blocker:** Inner Namco PPK geometry not decoded. All 72 characters are on disk as PPK but not yet renderable as GLB/FBX.
- **ISO:** Safe on release `urban-reign-iso-v1` (8×500MB parts).
- **Roster:** 60+ playable fighters (boxing, wrestling, karate, brawling, capoeira, kung fu). Tekken guests: Paul Phoenix, Marshall Law.

### Virtua Fighter 5
- **Status:** 19 fighters + 38 stages extracted.
- **Models:** On release `vf5-model-library-v1` (two tar archives: `vf5-models-a.tar`, `vf5-models-b.tar`).
- **Blocker:** `.farc` extraction tool is Windows-based. Models exist but need conversion to GLB on a Windows box or Linux path.
- **Docs:** `teardown/virtua-fighter-5/VF5-MODELS-MANIFEST.md`, `TEARDOWN.md`.

### Dead or Alive
- **DOA6:** Mechanics documented (`teardown/dead-or-alive-6/`). Models blocked — game is ~50GB+, not acquired. Formats: `.g1m` models, `.g1t` textures (community converters exist).
- **DOA4:** 30/30 chunks on release `doa4-iso-v1` (7.8GB). Needs reassembly + extraction. Sequenced after TTT2 due to disk.

## Ready to Render (GLB on disk)

### PR #170 roster (roster-integrate-phase1)
awa-pop, baek, dxmmii, king-tyrant, king-tyrant_alt1, kinpo, kinpo_alt1, lili, n3g4tiv0, nightwolf, pantera_alt1, phantom, purple-rain, rave, saku-ra, saku-ra_alt1, sam-ur-a1, skull, thor, waterfall, zafina (Mariposa), zui_alt1, zui_alt2

**Notes:**
- Most face correctly with camera on −X, no model rotation.
- **Zafina (Mariposa)** requires −90° Z + slight downward shift to center.
- DXMMII, Kinpo, Nightwolf, Rave may still need orientation checks if blank/side-facing.

### Tekken 3 donors (local)
t3_bryan, t3_gunjack, t3_xiaoyu, t3_yoshimitsu, t3_jin

**Notes:** Several render as exploded/fragmented geometry. Armature or scale issues. Need re-export or armature-applied versions.

## Extracted but Not Renderable Yet

| Set | Format | Next step |
|-----|--------|-----------|
| Shaheen, Jin T7, Miguel, Nina Revolution, Beast King, Ganryu (from model-pull zips) | Source .mdl / .vvd / .vtx | Source → FBX/GLB |
| Rashid (XPS + SFM) | XPS + Source .mdl | XPS → GLB; Source → FBX/GLB |
| Urban Reign (72 chars) | Namco PPK | Decode inner geometry |
| VF5 (19 fighters) | .farc (Windows tool) | Convert on Windows or find Linux path |

## Still Packed (need extraction)

25 archives in `/tmp/model-pull/` (and mirrored in `mhvnsnt/game-reverse-engineering`):
- T7 FBX zips (some failed unzip)
- Individual: alisa.rar, anna-williams.7z, christie.7z, lee-chaolan.rar, julia-classic.rar, xiaoyu-t8.rar, yoshimitsu-t7.7z, zafina-t7.zip, etc.

**Blocker:** no `unrar` / `7z` on this machine (apt permission denied).

## Fully Blocked

| Set | Count | Blocker | Location |
|-----|-------|---------|----------|
| **Urban Reign** | 72 | PPK inner geometry not decoded | `teardown/urban-reign/ppks/chars/` |
| **VF5** | 19 | .farc needs Windows tool | Release `vf5-model-library-v1` |
| **DOA6** | — | Game not acquired (~50GB) | Mechanics only |
| **DOA4** | — | Chunks on release, not reassembled | Release `doa4-iso-v1` |
| **Soulcalibur 2** | — | Only movesets; PS2 FS not RE'd | Teardown |
| **TTT2** | 26 parts | Release exists, not extracted (disk) | Release `ttt2-7z-v1` |
| **Tekken 6** | — | DATA401 encrypted | Teardown |
| **Rashid (SF5)** | 3 variants | XPS + Source; needs conversion | `teardown/street-fighter-5/models/rashid/` |

## Missing Entirely (need hunting)

Bass, Zangief, Hugo, Kuma, Lars, Samir, Bryden.

## Next Actions

1. Install `unrar` / `p7zip` (or extract elsewhere) and finish the 25 archives.
2. Convert Source `.mdl` sets (Shaheen, Rashid SFM, etc.) to FBX/GLB.
3. Decode Urban Reign PPK geometry (72 characters, including Brad Hawk).
4. Convert VF5 `.farc` on a Windows box or find Linux path.
5. Fix or re-export exploding T3 models.
6. Continue batch-rendering every new GLB with the camera-on-−X standard.
7. Update this doc as blockers clear.

## Handoff Notes

- **Do not guess or procedurally generate** models when teardown data exists.
- **Do not push WIP to main.** Feature branch + PR only.
- **Binary renders** cannot be pushed via the text-only push tool.
- **Zafina (Mariposa)** is the exception: −90° Z + vertical center shift.
- All new T-pose work must follow `docs/TPOSE_RENDER_STANDARD.md`.
- Full teardown status: `teardown/TEARDOWN-STATUS.md`.

---
*Updated to include Rashid, Brad Hawk / Urban Reign, VF5, and DOA. Previous version under-documented these sets.*
