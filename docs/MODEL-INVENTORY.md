# WESTERN HEART — MODEL INVENTORY

**Law (owner 2026-10-18):** the repo tracks ALL models we **HAVE** as a separate state from **WIRED** (actually in the game). Never conflate them again.
**Law (owner 2026-10-18, refined ~20:06 CDT):** nude/base models are NEVER held back — wire the base mesh in AS-IS. Clothing is a CUSTOMIZATION OPTION (Creation Suite), not a gate. The game targets RATED M (high teen minimum), Mortal Kombat-level visceral down the line (bone breaks, fatalities, x-ray attacks) once the base is down. While building: do NOT get caught up on nudity/adult themes — nudity/partial nudity stays in, nothing watered down. Any model missing textures/meshes/UV mapping: "just get it done and put it on the fucking character." Full customization on everything.

Legend: ✅ WIRED (in `game/assets/models/` or a roster attire slot) · 📦 HAVE (on disk, releases, or archives — not in game yet) · 🔧 IN-PROGRESS · ❓ BLOCKED

## Summary (as of 2026-10-18)

- **WIRED:** 55 GLBs in `game/assets/models/` (incl. scimitar) + 5 roster slot GLBs (zui attire1/attire2, pantera classic/snow-leopard, awa-pop attire1)
- **HAVE (not wired):** ~60+ models: Tripo pulls (Vain, Cape Jones sitting), 19 pull-rest GLBs, T7/T3 FBX teardown models, Bass Armstrong, Shaheen, Brad Burns, release archives, wrestling-repo No Mercy GLBs

---

## WIRED — `game/assets/models/` (54 GLBs)

| Model | Proprietary name | Source | Slot / notes |
|---|---|---|---|
| awa-pop.glb | Awa Pop | T7 Nina base + reskin | wired |
| baek.glb | Baek | T7 base | wired |
| bruno.glb | Bruno | fighter hunt R2 | wired (untextured — texture pass follow-up) |
| cape-jones.glb | Cape Jones | Tripo (default attire = Cyborg X Attire 1) | wired |
| cyborg-x.glb | Cyborg X | SFM Alisa fix | wired; Attire 2 = female Cape Jones build (pending) |
| demonio.glb | Demonio | T7 | wired |
| diablo.glb | Diablo | gtainside Heihachi conversion | wired — ladder-back (former default; replaced by Tripo Attire 1 on 2026-10-20) |
| dio.glb | Dio | fighter hunt R2 | wired (untextured — texture pass follow-up) |
| doc-frank.glb | Doc Frank | T7 | wired |
| dxmmii.glb | Dxmmii | limb system | wired |
| jin-body.glb | — | body shell | wired |
| jin.glb | Jin Kazama | T7 base | wired |
| kai-body.glb | — | body shell | wired |
| kiko-tanaka.glb | Kiko Tanaka | Tripo (hooded, default) | wired |
| kiko-tanaka_alt1.glb | Kiko Tanaka | Tripo (unrobed) | wired |
| king-tyrant.glb / _alt1 | King Tyrant | T7 King variant | wired |
| kinpo-t8.glb / kinpo.glb / kinpo_alt1 | Kinpo | T8/T7 base | wired — legacy alternates since 2026-10-20 (kinpo.glb = `kinpo-legacy` key; A1 default is now the Tripo pull, roster slot below) |
| lili.glb | **Silvertongue** | T7 Lili base | wired; Noir Gala = later attire slot (recolor) |
| mariposa.glb | **Mariposa** | T7 base | wired; Golden Pharaoh = later attire slot (recolor) |
| michiko.glb | Michiko | fighter hunt R2 | wired (untextured — texture pass follow-up) |
| n3g4tiv0.glb | n3g4tiv0 | T7 | wired |
| nightwolf.glb | Nightwolf | T7 | wired |
| pantera-body.glb | Pantera | body shell | wired |
| pantera.glb / pantera_alt1 / pantera_fixed | Pantera | T7 King reskin | wired (A1 default) |
| phantom-t8.glb / phantom.glb | Phantom | T8/T7 | wired |
| purple-rain-main.glb | Purple Rain | Tripo (default) | wired |
| purple-rain.glb | Purple Rain | earlier build | wired (later slot) |
| rave.glb | Rave | T7 Lei base | wired |
| retsu-body.glb / rin-body.glb | — | body shells | wired |
| saku-ra-main.glb | Saku Ra | Tripo (default) | wired |
| saku-ra.glb / saku-ra_alt1 | Saku Ra | earlier build | wired (later slot) |
| sam-ur-a1-body.glb / sam-ur-a1.glb | Sam-ur-a1 | T7 | wired |
| sha-body.glb | — | baked body (0 skins) | wired — see clothing plan below |
| skull.glb | Skull | T7 | wired |
| star.glb | Star | fighter hunt R2 | wired (untextured — texture pass follow-up) |
| steve-fox.glb | — | T7 base | wired (canon = Zui) |
| thor.glb / thor_alt1 | Thor | Tripo (default) | wired |
| torch.glb | Torch | Anna base / fighter hunt R2 | wired (untextured — texture pass follow-up) |
| waterfall.glb | Waterfall | Tripo (default) | wired |
| yukihyo.glb | Yukihyō | fighter hunt R2 | wired |
| zafina.glb | **Mariposa** | T7 Zafina base | wired (renamed — use Mariposa everywhere) |
| zen-body.glb | — | body shell | wired |
| zui_alt1.glb / zui_alt2.glb | Zui | T7 Steve base | wired (Zui alternates in ATTIRE_VARIANTS, 2026-10-21) |

### Roster slot GLBs (wired as attires)

| Path | Character | Slot | Source |
|---|---|---|---|
| `roster/zui/attires/attire1/model.glb` | Zui | A1 DEFAULT | Tripo Drunken Monk (20.7MB) — WIRED 2026-10-21: MODEL_URLS `zui-attire1`, default on both paths (model-key audit follow-up) |
| `roster/zui/attires/attire2/model.glb` | Zui | A2 | Tripo rework v2 — WIRED 2026-10-21: MODEL_URLS `zui-attire2`, selectable alternate |
| `roster/pantera/attires/classic/pantera-classic.glb` | Pantera | A3 | older build reskin |
| `roster/pantera/attires/snow-leopard/pantera-snow-leopard.glb` | Pantera | A3 alt | snow-leopard reskin (tweaked) |
| `roster/pantera/attires/leomon/model.glb` | Pantera | A2 · Leo man | owner's model via Google Drive (restored 2026-10-20) — WH-Canonical-22 rig, T3 King clips embedded |
| `roster/awa-pop/awa-pop-attire-1.glb` | Awa Pop | A1 DEFAULT | Tripo |
| `roster/kronos/attires/attire1/model.glb` | KRONOS | A1 DEFAULT | Tripo "muscular warrior" (19.1MB) |
| `roster/kronos/attires/attire2/model.glb` | KRONOS | A2 Timberwolf | Tripo (20.4MB) |
| `roster/kronos/attires/attire3/model.glb` | KRONOS | A3 TimberWolf Fully suited | Tripo (21.5MB) — Wolverine claws both hands; middle claw each hand short + rounded |
| `roster/diablo/attires/attire1/model.glb` | DIABLO | A1 DEFAULT | Tripo "fantasy demon" (22.8MB) — oni Heihachi: long silver wing-hair, two short horns, tattooed chest/arms, purple dragon hakama |
| `roster/diablo/attires/attire2/model.glb` | DIABLO | A2 Devil God | Tripo (22.5MB) — Hagoromo drapery + Raijin Taiko Drum Ring |
| `roster/slice/attires/attire1/model.glb` | SLICE | A1 DEFAULT | Tekken 7 Dragunov teardown conversion (52.4MB) — beret default costume, T7 skeleton (198 joints); source `dragunov-t7-rig.blend` (release `tekken-models-batch-2`) |
| `roster/vainabel/attires/attire2/model.glb` | VAIN ABEL | A2 | Tripo "wrestler character" (19.8MB) — purple flame vest, purple-stitched black pants; mismatched eyes |
| `roster/vainabel/attires/attire3/model.glb` | VAIN ABEL | A3 · Masked Demon of the Purple Haze | Tripo "masked fighter" (19.6MB) |
| `roster/kinpo/attires/attire1/model.glb` | Kinpo | A1 DEFAULT | Tripo "stylized female character" (20.3MB meshopt) — mini skirt; jiggle butt/thighs/hips at rig stage (owner 2026-10-20, `roster/kinpo/RIG-NOTES.md`) |
| `roster/kinpo/attires/attire2/model.glb` | Kinpo | A2 "Goth Sport" | Tripo "gothic punk character" (18.4MB meshopt) — owner 2026-10-20; same mini skirt as A1, no jacket, goth makeup, little fangs; enhanced jiggle + M-rated anatomy rig specs in `roster/kinpo/RIG-NOTES.md` |

---

## HAVE (not wired yet)

### Tripo pulls — have, not wired

| Model | Tripo ID / source | Local | Notes |
|---|---|---|---|
| Vain (default attire) | f7e90de8-5292-41ab-a7f0-93cd230a7b60 (19MB GLB) | `~/workspace/tripo-downloads/wrestler_character_3d_model.glb` | 4 Bass Armstrong variants become alternates |
| Cape Jones sitting (pose reference) | 22cdbc99 "superhero throne pose" (18MB) | `~/workspace/tripo-sitting-pull/superhero_throne_pose_3d_model.glb` | replicate pose with canon model per owner 2026-10-18 |
| Cape Jones sitting (plain) | — | `~/workspace/tripo-sitting-pull/sitting_plain.glb` | pose reference |

### Special finds — have, not wired

| Model | Source | Local | Status | Clothing / wiring plan |
|---|---|---|---|---|
| **Bass Armstrong** | DOA5 (GTA SA port) | `~/workspace/bass-hunt/DOA5_Bass_Armstrong_Costume_1.zip` (20MB) | 📦 DFF+TXD — needs conversion | convert DFF→GLB (DOA5 tool / Blender), textures ship in zip |
| **Shaheen** | T7 SFMLab | `~/workspace/tmp-transient/shaheen/shaheen-t7-sfmlab.zip` | 📦 **NUDE BASE** (SFM mdl + VTF) | dress from its OWN costume textures (cos1/2/3, cape, shmagh, shoes) + Creation Suite parts — see clothing plans below |
| **Brad Burns** | VF5 PS3 (braitm.farc, 47MB) | release `vf5-local-models-v1` / local | 🔧 cracked (156 files) — model format needs RE | finish RE, then VF5 outfit |
| **Scimitar (Shaheen alt)** | T7 Shaheen | nude MDL base | ✅ WIRED (`game/assets/models/scimitar.glb`, in MODEL_URLS) | static base mesh, rip pose — auto-rig + clothing via Creation Suite as OPTIONS, never gates (NO-GATE LAW 2026-10-18) |

### pull-rest GLBs — have, not wired (19)

`~/workspace/pull-rest/glb/` (verified, renders in `verified/`):
alisa, asuka-t8, baek, bryan, doc-frank, ganryu(-anim), heihachi, josie, julia, lee, lei, lili, mokujin, negan, nina, xiaoyu-t7, yoshimitsu(-t8), zafina

### T7/T3 teardown FBX models — have, not wired

`~/workspace/tpose-staging/`: asuka-kazama, baek, bryan, eddy-gordo, ganryu, gun-jack (3 variants), josie, julia, lee, lei, lili, mokujin, negan, nina, rashid, steve-fox, t3, xiaoyu (3 variants), yoshimitsu, zafina — plus the verified 6 working T7 FBX models (King, Asuka, Eddy, Steve Fox, Xiaoyu pink dress, Armor King, King T8 S2). Full detail: `~/workspace/teardown-model-inventory/INVENTORY.md`.

### Dissidia test GLBs — have, not wired (test data, not roster)

19 working humanoids from the GMO→GLB pipeline proof (cloud, aeris, cecil, firion, garland, goddess, golbez, jecht, kefka, lightning, mithragirl, onionknight, sephiroth, squall, terra, tidus, warrioroflight, yuna, zidane) in `tekken6/work/tooling/out/` (local, not in repo).

### Release archives — have (model libraries, not wired individually)

| Release | Contents |
|---|---|
| `fighter-hunt-r2` | michiko/torch/dio/star/bruno/yukihyo GLBs — **now wired** |
| `tekken7-full-v1` (8 assets), `tekken8-full-v1` | T7/T8 game-file mirrors |
| `tekken6-recon-20261016` | T6 PSP recon |
| `vf5-model-library-v1` (3 tars) | VF5 models A/B + stages (Brad Burns source) |
| `vf5-local-models-v1` | 334 local VF5 files |
| `soulcalibur2-xbox-extract-v1`, `sf-ex3-v1`, `sf-ex2-plus-v1`, `sf-ex-plus-alpha-v1` | other fighter models |
| `doa4-*` releases | DOA4 workdir (Bass Armstrong lane) |
| `wmxix-teardown-full-v1`, `urban-reign-iso-v1`, `defjam-ps2-iso-v1` | teardown sources |

### Wrestling repos — have (NOT in Western Heart per owner law)

13 No Mercy GLBs (kevin_nash_1, kurt_angle_1, rhyno_1, rob_van_dam_1, scott_hall_1, shawn_michaels_1/2, stephanie_mcmahon_1, steve_austin_1, the_rock_1/2/bald, triple_h_1) live in Bannon (PR #87), wrestling-game (PR #9), wrestlemania-xix-mod, wwe-wrestler-models. Removal from Western Heart: PR #234 (open).

### Customization part libraries — wired via PARTS-REGISTRY.json

- `customization/eye-library/` (yellow tiger universal, blue snow-leopard, classic)
- `customization/parts/pantera-eyes/`, `customization/parts/lili-eyes/`, `customization/parts/zafina-eyes/`
- `customization/decal-library/pantera/` (logos, tights, pants options)
- `customization/parts/superhero/` (4 original mesh pieces: spider-girl eyes, batgirl mask/gauntlets, space-ghost cowl)
- 3372+ indexed teardown parts (PARTS-INDEX.json) + CC0 hair libraries

---

## NUDE / BASE MODELS — CLOTHING AS CUSTOMIZATION OPTION (owner law: clothing is an option, never a gate)

Nudity/partial nudity does NOT block wiring — models go in as-is. These are the customization options, not blockers:

| Model | State | Clothing/customization option |
|---|---|---|
| **Shaheen** (T7 SFMLab nude MDL) | nude base, clothes textures SHIP in the zip | assemble base outfit from its OWN VTF costumes (T_cos1/2/3 + cape + shmagh + shoes), composite via Creation Suite; full mesh swap path on top |
| **Scimitar** (Shaheen alt) | nude base, now WIRED as static | auto-rig + Creation Suite clothing pass as options, never gates |
| **sha-body** | baked body, 0 skins/armatures | base outfit from parts library as an option |
| **Bass Armstrong** (after DFF→GLB) | ships WITH DOA5 costume textures | convert with textures → costume intact |
| **Brad Burns** (after RE) | VF5 outfit files expected in farc | extract outfit with model |

---

## Update protocol

- A model is **HAVE** the moment it lands on disk, in a release, or in an archive — record it here immediately.
- A model becomes **WIRED** only when its GLB is in `game/assets/models/` or a roster attire slot on main.
- Every Tripo pull gets recorded in `roster/TRIPO-REGISTRY.md` AND here.
- Proprietary renames: use the new name everywhere (Zafina→Mariposa, Lili→Silvertongue); old names retired.
