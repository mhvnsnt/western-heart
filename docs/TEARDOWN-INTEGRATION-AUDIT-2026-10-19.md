# Teardown Integration Audit — 2026-10-19 (owner order ~21:46 CDT)

**Gap measured:** teardown-"done" vs actually playable in `game/`.
**Base:** `origin/main` @ 1eacf7a9 (PR #350). All wiring verified by node
(imports, JSON validity, fetch-stub loads of every moveset + aggregate).

## Audit table (teardown → extracted → wired before → gap → after this lane)

| Teardown | Extracted (in repo) | Wired before | Gap | After |
|---|---|---|---|---|
| **Tekken 3** | 7 motion banks decoded (365–652 rows, 188–249 attacks each), 15 stage panoramas + atlases, 31 King anim clips | Movesets: per-fighter files of **10–20 moves** (thin subsets); stages: 15 retro ✓; anims: **broken** (clips live at repo-root `assets/anim/`, game fetched `game/assets/anim/` → all 404); aggregates: `demonio_moves.json` missing → `loadRealMovesets()` rejected wholesale | Moveset depth (FULL MOVESET LAW), anim path, demonio aggregate | **Full bank depth wired: 61 per-fighter files at 89–191 entries** (moves+strings+specials; 50/61 ≥100, bryan-family 90–97 — smallest bank, see generator note); 7 aggregates restored (82–117 moves); T3 anim base path fixed |
| **Tekken 6 (PSP/PS3)** | ~40–45%: structure, videos, EBOOT decrypted; DATA401/DATA214 models still encrypted | Nothing playable | Moveset/model extraction blocked on KIRK/DATA401 decrypt lane | Unchanged — blocked upstream, not a wiring gap |
| **TTT2** | ~15–25%: roster (59) + stages (29) docs, archive on release `ttt2-7z-v1` | Nothing | Full extraction not run (13GB archive; disk-gated) | Unchanged — extraction gap, not wiring |
| **Urban Reign** | ~95%: 72 fighter PPK models (ROSTER.json), motion .gyu packs, stage SFX audio | **Nothing** — no GLBs, no movesets, no stages | Models are raw PPK geometry (needs conversion lane); motion semantics not decoded (PPK RE) | Unchanged — conversion/RE gap, not wiring. Kronos moveset canonically mixes Golem (UR) via the king bank |
| **WWF No Mercy** | Models + **17 arena assemblies (OBJ + vertex colors)** | CAW/customization systems only; arenas: **0 wired** | Arenas sat unwired despite being complete geometry | **17 arenas wired as playable stages** (`game/assets/stages/no-mercy/`, vertex colors merged from .vc sidecars, `buildNoMercy` + `WRESTLING` tier; stage count 24 → 41) |
| **WMXIX** | Wrestler OBJs, arena vertex clouds, decoded textures | CAW parts/systems only | Arena OBJs are **vertex-only point clouds** — faces live in undecoded YMG (mesh-decode lane open) | Unchanged — decode gap, not wiring |
| **DOA4** | 50 chrthree meshes decoded, XPR2 carved (219/221); movesets: Bass movelist triangulated | doa-bass/hayabusa/kasumi + vainabel files (12–44 moves, real movelist data) | DOA4 binary motion bank not decoded → converted movelists are the ceiling for now | Unchanged — decode gap |
| **SF 3D (EX/EX2+/EX3)** | ~5–15%: TIM/TMD extraction tooling, partial pulls | blanka/zangief/vega/iori/armor-king Sketchfab models + movesets wired on main, **but no roster entries → unselectable** | Roster entries missing | **5 roster entries added** (working names, WH names pending owner pick) + KRONOS ×2 (model+moveset were wired, roster entry missing) |
| **Eastern Mind** | 100% verified: 5,707 files, stages/bitmaps/soundtrack | 8 canon stages ✓ (Tong-Nou, Five Lands, Marketplace, Shrine) | Audio: soundtrack extracted, game audio is synthesized (audio.js) — no EM music wiring | Unchanged — audio wiring is its own lane |
| **Soulcalibur II** | Extraction complete (OLK out, on releases); character/stage model mapping not done | Nothing | No converted models exist to wire | Unchanged — conversion gap |
| **VF5 / T7 / T8** (federation) | Model libraries on releases; VF5 manifest in teardown | vf-akira/sarah/kage converted movelists (12–19 moves) | Model conversion not run; movelists shallow | Unchanged — conversion gap |

## What this lane wired (all additive; 0 curated entries lost — subset-checked)

1. **Full T3 movesets** — `tools/gen-movesets-t3.py` walks each bank's branch
   graph (Dijkstra over decoded input commands → canonical Tekken notation,
   strings, conditioned variants) and merges full depth over the curated
   files: **+5,879 moves/strings across 61 files + 3 new files**
   (`demonio-human`, `doc-frank-wowomomo`, `doc-frank-hood` — roster ids that
   had no moveset at all) + `kronos-attire2`. Frame data is the banks' real
   data (startup/active/recovery from stream frames; damage scaled
   170HP→100HP, the repo's existing convention). Bryan bank caveat is
   recorded per-file (smallest bank; ~79 attack rows are common-bank/reaction
   rows with no per-character input in the extracted data).
2. **Aggregates restored** — `game/assets/{king,demonio,bryan,heihachi,
   xiaoyu,yoshimitsu,gunjack}_moves.json` (the `demonio` file was missing
   entirely, which silently killed `loadRealMovesets()`).
3. **T3 animation path fix** — `t3anims.js` base now `../assets/anim/...`
   (real clips were 404ing; fighters silently fell back to procedural).
4. **demonio-body repoint** — MODEL_URLS key pointed at a GLB that was never
   pushed; now resolves to `demonio.glb`.
5. **17 No Mercy stages** (above) + `WRESTLING` tier in stage select.
6. **Roster entries** — KRONOS (attires 1+2), Zangief, Blanka, Vega, Iori,
   Armor King selectable; `MOVESET_MAP` fallbacks added for the new ids.

## Verification (proof)

- `node --check` clean on all `game/js/*.js`.
- Node fetch-stub load: **71/71 MOVESET_IDS resolve**; all 7 aggregates parse
  with playable shape (`moves['1']` present).
- Stages smoke test (vendored three): **41 stages, 0 dup ids, 0 bad defs**;
  `parseStageOBJ` on NM arenas yields geometry + vertex colors.
- Curated-data subset check vs HEAD: **0 moves/strings lost**.
- Before/after move counts: per-fighter files went from 10–44 moves to
  89–191 total entries (federated DOA/VF files unchanged at 12–44 — real
  converted data, extraction-gated).

## Remaining gaps (next lanes, in dependency order)

1. DOA4 motion-bank decode → real DOA movesets (replaces 16–20-move files).
2. WMXIX YMG face decode → arena stages (textures already decoded).
3. Urban Reign PPK→GLB conversion + motion semantics → fighters/stages.
4. TTT2 archive extraction (disk-gated) → T7-era movesets/models.
5. T6 DATA401/DATA214 decrypt → T6 movesets/models.
6. SC2/VF5/T7/T8 model conversion → roster GLBs.
7. Eastern Mind soundtrack → audio.js music wiring.
8. Cain Elias moveset file (attires wired, no moveset yet).
