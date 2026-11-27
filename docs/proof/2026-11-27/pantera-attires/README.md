# Pantera: all six attires wired and checked in the game's own loader (2026-11-27)

Owner, 2026-11-27: "Those are all correct outfits, so make sure you're getting everything into the repo and wired up a
hundred percent. And don't hold any work hostage, get it all to the repo."

Ladder (game/js/attires.js, unchanged): A1 `pantera-leoman`, A2 `pantera-leopard-king`, A3 `pantera`, A4
`pantera-snow-leopard`, A5 `pantera-crimson-rage`, A6 `pantera-p2`. Each key now points at a file that is rigged,
skinned and under Cloudflare Pages' 25 MiB file cap (A2 and A4-A6 also under jsDelivr's 20 MB limit).

## What was wrong (seen in renders, `before/`)
* **A5 / A6**: static meshes (no skin), lying on their side. They are re-textures of the A3 parts.
* **A4 Snow Leopard**: arms stretched into long blades, gloves and armbands floating (`before/a4_snow_leopard_idle_y0_BEFORE.png`).
  Its parts match A3 exactly (18 parts, 11,376 verts, similarity residual 3e-15), but its skin is a copy from
  2026-10-17, before A3's 2026-10-20/22 weight repairs.
* **A3 Classic** (and so everything built on it): those repairs were judged on the file's own Idle clip, which the game
  never plays. Under the T7 King bank the fight does play, boot straps came off the standing shin as shards and the
  trousers tore in the kick (`before/a3_classic_kick_y90_BEFORE.png`, stretch heat `before/a3_classic_kick_y90_stretchheat_BEFORE.png`;
  poselab stretch p99.9 up to 51.8).
* **A2 Leopard King**: `model-refit.glb` is 32.6 MB, over Cloudflare's 25 MiB per-file cap and jsDelivr's 20 MB, so the
  live build only reached a different, stale copy on the Worker (32,679,076 B vs the repo's 32,615,156 B).

## What changed (all rule-based tools, no hand-painted weights, no mesh cuts, skeletons untouched, originals kept)
1. **A3**: `game/assets/models/pantera-weights-v2.glb` = `pantera.glb` with only JOINTS_0/WEIGHTS_0 changed by the new
   `tools/auto_rig/game_pose_seam_smooth.py`:
   it captures the game's own posed skeleton (poselab `showFighter`, 20 action slots x 5 times, `harness/capture_poses.mjs`,
   data `harness/poses_pantera_t7king.json.gz`), embeds those poses as clips in a temp copy, and runs
   `backends/seam_safe_smooth.py`'s method with layer coupling: separate islands closer than 2 cm at bind (straps over
   boots, trousers over thighs) on the same limb chain are smoothing neighbours, and a pair that separates by more than
   1 cm in any game pose counts as a defect. Report `reports/classic_game_pose_seam_smooth.json` (p99.9 15.4 -> 7.4;
   separating layer pairs 1,155 -> 117, max 0.371 m -> 0.034 m). `assets.js` `pantera` repointed.
2. **A4**: `pantera-snow-leopard-reweighted.glb`: `tools/auto_rig/rig_multipart_from_donor.py` with donor
   `pantera-weights-v2.glb` (all 18 parts: donor weights copied, same vertex order). Key repointed.
3. **A5 / A6**: `-rigged.glb` the same way: orientation fixed by one similarity transform fitted on the 15 name+count
   matched parts (scale 0.7836, residual ~1e-7), 15 parts copy donor weights, belt2/boots1/boots3 by per-part k-NN
   (mean NN distance 0), tail rigid to Hips (its own fit_tail seed was too small; reported). Keys repointed, facing +Z
   added to `model-facing.json`. A variant with an extra game-pose smoothing pass (`reports/*_smooth.json`) was
   evaluated and NOT shipped (its max layer separation rose to 0.119 m).
4. **A2**: `model-refit-cdn.glb` (18.7 MB) by `tools/deploy/fit_cdn_budget.py` (meshopt decoded first; normal PNG ->
   JPEG 4:4:4 q90, mean normal error 0.60 deg / p99 3.84 deg; gltfpack -cc). Same rig. Render comparison
   `a2-pack/a2_original_vs_packed.png` (identical by eye). Key repointed.
5. New helper `tools/auto_rig/transplant_weights_by_position.py` (copies a Blender re-skin back into the original
   layout by bind-space position). It was used to test surface-heat weights on A3. That result was worse (p99.9 up to 97) and was not shipped.

## Verification (game's own loader: game/poselab.html showFighter, T7 King bank, headless Chrome/SwiftShader)
* Attire select: `after/attire_select.json`. setAttire + resolveFighterAttire + showFighter for each of the 6 slots
  resolves the right key, bank `t7_king`.
* Sheets (every image opened and looked at): `after/sheet_y0.png`, `after/sheet_y90.png` (idle, walk, punch, kick,
  hit), `after/sheet_idle_kick_y0.png`; before: `before/sheet_before_y0.png`, `before/sheet_before_y90.png`.
* Close-ups: `after/pantera_kick_y90_AFTER.png`, `after/a3_standing_boot_kick_AFTER.png`,
  `after/a3_classic_kick_y90_stretchheat_AFTER.png`, `after/pantera-snow-leopard_idle_y0_AFTER.png`,
  `after/pantera-crimson-rage_kick_y90_AFTER.png`, `after/pantera-p2_hit_y0_AFTER.png`, `after/pantera-leopard-king_kick_y0_AFTER.png`.
* Measured (`after/results.json`; knee = UpLeg-Leg-Foot angle; minY = lowest skinned vertex sampled; stretch = poselab stretchMap p99.9 max over meshes):

| model | pose | bank | knee L / R deg | minY m | stretch p99.9 |
|---|---|---|---|---|---|
| pantera-leoman | idle | t7_king | 127.9 / 110.6 | 0.019 | 4 |
| pantera-leoman | walk | t7_king | 138.6 / 118.6 | 0.006 | 6.36 |
| pantera-leoman | punch | t7_king | 120.2 / 147.7 | -0.009 | 6.83 |
| pantera-leoman | kick | t7_king | 81.7 / 155.9 | 0.008 | 6.56 |
| pantera-leoman | hit | t7_king | 154.9 / 132.9 | 0.006 | 4.96 |
| pantera-leopard-king | idle | t7_king | 127.9 / 110.6 | 0.022 | 9.15 |
| pantera-leopard-king | walk | t7_king | 138.6 / 118.6 | 0.006 | 9.31 |
| pantera-leopard-king | punch | t7_king | 120.2 / 147.7 | -0.035 | 9.18 |
| pantera-leopard-king | kick | t7_king | 81.7 / 155.9 | 0 | 13.51 |
| pantera-leopard-king | hit | t7_king | 154.9 / 132.9 | 0.01 | 7.82 |
| pantera | idle | t7_king | 110.6 / 127.9 | 0.058 | 9.99 |
| pantera | walk | t7_king | 118.6 / 138.6 | 0.023 | 10.95 |
| pantera | punch | t7_king | 147.7 / 120.2 | -0.036 | 7.57 |
| pantera | kick | t7_king | 155.9 / 81.7 | -0.032 | 19.36 |
| pantera | hit | t7_king | 132.9 / 154.9 | -0.031 | 9.36 |
| pantera-snow-leopard | idle | t7_king | 110.6 / 127.9 | 0.058 | 9.99 |
| pantera-snow-leopard | walk | t7_king | 118.6 / 138.6 | 0.023 | 10.95 |
| pantera-snow-leopard | punch | t7_king | 147.7 / 120.2 | -0.036 | 7.57 |
| pantera-snow-leopard | kick | t7_king | 155.9 / 81.7 | -0.032 | 19.36 |
| pantera-snow-leopard | hit | t7_king | 132.9 / 154.9 | -0.031 | 9.36 |
| pantera-crimson-rage | idle | t7_king | 110.6 / 127.9 | 0.052 | 9.99 |
| pantera-crimson-rage | walk | t7_king | 118.6 / 138.6 | 0.017 | 10.95 |
| pantera-crimson-rage | punch | t7_king | 147.7 / 120.2 | -0.036 | 7.57 |
| pantera-crimson-rage | kick | t7_king | 155.9 / 81.7 | -0.04 | 19.36 |
| pantera-crimson-rage | hit | t7_king | 132.9 / 154.9 | -0.031 | 9.36 |
| pantera-p2 | idle | t7_king | 110.6 / 127.9 | 0.052 | 9.99 |
| pantera-p2 | walk | t7_king | 118.6 / 138.6 | 0.017 | 10.95 |
| pantera-p2 | punch | t7_king | 147.7 / 120.2 | -0.036 | 7.57 |
| pantera-p2 | kick | t7_king | 155.9 / 81.7 | -0.04 | 19.36 |
| pantera-p2 | hit | t7_king | 132.9 / 154.9 | -0.031 | 9.36 |

## Honest limits
* A3-A6 still show p99.9 stretch 7.6-19.4 (trousers in the kick) vs A1 4-6.8. No tear is visible in the renders above, but the
  number is not at the 2.5 gate.
* A3-A6 Foot/ToeBase, Spine2 and Shoulder joints carry no weight (inherited from the 2026-10-22 k-NN reskin): the boot
  does not flex at the ankle. `validate.py` fails `fingers_symmetric` (Thumb3) on the donor and on all derived files (skeleton, inherited).
* minY: feet dip 3-4 cm under the floor in punch/kick/hit for A3-A6 (same numbers before the change; game grounding,
  not the skin), A2 punch -3.5 cm.
* The A5/A6 tail is rigid to Hips (no tail chain).
* Throws were not checked (unsupported). The Worker CDN does not have the new files (404). The loader falls through to the
  Cloudflare Pages copy, or to jsDelivr on GitHub Pages.
* `roster/pantera/pantera_rigged.glb` and `teardown/tekken7/king/pantera_rigged.glb` (scale bug) were left alone: the only
  references are metadata in `roster/pantera/anatomy/anatomy-layers.json` and a test fixture. game/js never loads them.

## Model SHA-256 (bytes)
```
7085ce665a6e1dcebb40af4783a1f6661669fb98379b1310871e74f82d736ab6 7625912 game/assets/models/pantera.glb
64f1e05f232217112915c7cf00143112d966f02d838de529e196af04527ab132 7625912 game/assets/models/pantera-weights-v2.glb
a1b7f7fadaf18cd187dad0ca30fbb41c6c66aee7a0b839b0d67f03254aa9e6ca 7434348 roster/pantera/attires/snow-leopard/pantera-snow-leopard.glb
5715a3285a4d167b310cc294649fbfa25b0e48d7e86698028d72b514b456a541 7463976 roster/pantera/attires/snow-leopard/pantera-snow-leopard-reweighted.glb
e87931fdc4178a2ff0897d3f7e86990b20cd3289f5e2ab97f2e3e520c27e7bd8 14675572 roster/pantera/attires/crimson-rage/pantera-attire5-crimson.glb
e98d9df0a8fb8888299795b1d56fbac5d045faf70c069b512c45358adf84c34b 15287916 roster/pantera/attires/crimson-rage/pantera-attire5-crimson-rigged.glb
99c34370480194a0e35b765721425bbf5e00746ca6f4a89970a7d853b7825ec7 14548052 roster/pantera/attires/p2-wired/pantera-attire4-p2.glb
a41688a44b5003ecfb36ac10a1237760fd867271842fe25e24262d61b493886b 15160400 roster/pantera/attires/p2-wired/pantera-attire4-p2-rigged.glb
f91deef00c9b5b9466b2971fc227ddcf0531cde6731116fbe91f7ed1b5b05d53 32615156 roster/pantera/attires/leopard-king/model-refit.glb
2ac3da87d560bc14a399eb82970c00472d2ac59f2bac628a7414db0659b8fb79 18729904 roster/pantera/attires/leopard-king/model-refit-cdn.glb
5c4e1669e040e48e8cbc12cc8865328377a0f2fd96873de6839bef304aefcc3c 4414284 roster/pantera/attires/leomon/model.glb
```

## Proof file SHA-256
| path | sha256 |
|---|---|
| `docs/proof/2026-11-27/pantera-attires/reports/a2_fit_cdn_budget.json` | d9ece86b7dcbc1dfc80d69022ec5ef73fbd0d1621eaf78056e09a3225840a404 |
| `docs/proof/2026-11-27/pantera-attires/reports/a4_rig.json` | d0adee1b9237c71dc4cb9bbe39601e90d7d95876b1ff9c74e7105bea616a88e9 |
| `docs/proof/2026-11-27/pantera-attires/reports/a5_first_rig_from_pantera_glb.json` | 80c48f2c28199ecd4b7deda565bfc7ad5fe9d521c4b480f990510c2ed527ee55 |
| `docs/proof/2026-11-27/pantera-attires/reports/classic_game_pose_seam_smooth.json` | 69fde5340e934a085448319e920949eb56375288618f34ba02547dbb9e1c2070 |
| `docs/proof/2026-11-27/pantera-attires/reports/pantera-attire4-p2_rig.json` | b05bc5965482c844b5fa3a941575a50267428da7a7d07b3e3a18fc2ac357cab3 |
| `docs/proof/2026-11-27/pantera-attires/reports/pantera-attire4-p2_smooth.json` | ab5e74d24bf6b43a7accd970f5a1d80d46e04e998fdf7ccb1de55cef4174ac94 |
| `docs/proof/2026-11-27/pantera-attires/reports/pantera-attire5-crimson_rig.json` | 187893ba05192d37e1827f94e1f98ebbc9c5ced85aec6818148de5dccdd8231c |
| `docs/proof/2026-11-27/pantera-attires/reports/pantera-attire5-crimson_smooth.json` | cb19fa9d939bad13107926d99f0118f106e306b466e9463e9df34dc97341ec2c |
| `docs/proof/2026-11-27/pantera-attires/a2-pack/a2_original_vs_packed.png` | b22881178c9194419255ebb3694e46dc6c656ac6ab81e9a80d21d3362c4760b7 |
| `docs/proof/2026-11-27/pantera-attires/harness/attire_select_check.mjs` | 0dc5922b57c0093216406fd4d714d1b4c17769d8ffc5dbdac54abed13893b5a7 |
| `docs/proof/2026-11-27/pantera-attires/harness/capture_poses.mjs` | c3a183f0f4b6bc74200d03349a2a7a2e337eb108cc526fb1e1d990fb8971b18b |
| `docs/proof/2026-11-27/pantera-attires/harness/make_sheet.py` | 30ccb28ff6361a0d6058ee43029b976d0bc87ee40acf488800092caa3edbfa85 |
| `docs/proof/2026-11-27/pantera-attires/harness/poses_pantera_t7king.json.gz` | c90ba30f7cc4c13af72a03ffff03f82057cd308913321351fc558f976a3440ba |
| `docs/proof/2026-11-27/pantera-attires/harness/render_six_attires.mjs` | 1a61c064986124a93787ea2fed5ad53c3c34ddaebc521721f559c92d71db3401 |
| `docs/proof/2026-11-27/pantera-attires/after/a3_classic_kick_y90_stretchheat_AFTER.png` | 2e09240cd057249154720facfdabc80b8e56a778d7771b9cf94cf2c42e06e8e3 |
| `docs/proof/2026-11-27/pantera-attires/after/a3_standing_boot_kick_AFTER.png` | 739c6e3d6c5b8ae63ee5140d604a7e041386df216c067f4e34af24ddb94925c7 |
| `docs/proof/2026-11-27/pantera-attires/after/attire_select.json` | f720044a164433b165d8d781afde0c3201921618a8d15bf0c3695b631cc11706 |
| `docs/proof/2026-11-27/pantera-attires/after/pantera-crimson-rage_kick_y90_AFTER.png` | fce95151db81868f0d31718be8d991947c9257d74d975f1ae6f90a63276c08bb |
| `docs/proof/2026-11-27/pantera-attires/after/pantera-leopard-king_kick_y0_AFTER.png` | 0cd016de071842c8ea996af91c6c0386e60722eaac895a95a86187b7537acbc1 |
| `docs/proof/2026-11-27/pantera-attires/after/pantera-p2_hit_y0_AFTER.png` | 40a2e17a8d40bb008e971616e55e1cf86ecc90465d0e521526cbc5e8a48f19f2 |
| `docs/proof/2026-11-27/pantera-attires/after/pantera-snow-leopard_idle_y0_AFTER.png` | 6ab4a3e299fb4295534acd79783b354341b8c773641c77d50e45cffb9632b54a |
| `docs/proof/2026-11-27/pantera-attires/after/pantera_kick_y90_AFTER.png` | e8d3ab65a92b09f7c1d4a292bdf70242ab4c79c00aeaf2a666b3b7dcf43e3154 |
| `docs/proof/2026-11-27/pantera-attires/after/results.json` | e4785a923a27e15cba40d794576dfab44581064a9072acdefe030ef7b5b8a813 |
| `docs/proof/2026-11-27/pantera-attires/after/sheet_idle_kick_y0.png` | f845896ed8de1aaf62e4c0e79d81a62c6f7b369ab5f72a4d21e9ce29efac0d03 |
| `docs/proof/2026-11-27/pantera-attires/after/sheet_y0.png` | 2b6cc1a995dc06f6f31d0110eda848231e8589d40989abc27346a23af5b6aae4 |
| `docs/proof/2026-11-27/pantera-attires/after/sheet_y90.png` | 6b40da677aa876a43ab3578c04eb8b4a12b66550477cff036a98a074e93819a9 |
| `docs/proof/2026-11-27/pantera-attires/before/a3_classic_kick_y90_BEFORE.png` | 9613140463eb19773abd480583d768caf872da72d7a98b248c34f4366ef78ed8 |
| `docs/proof/2026-11-27/pantera-attires/before/a3_classic_kick_y90_stretchheat_BEFORE.png` | e8ba2bb123293e3e5632c63125651370785031479c04d8d5f9da53b6bafdd042 |
| `docs/proof/2026-11-27/pantera-attires/before/a3_standing_boot_kick_partial_fix_only.png` | 6632d8528a3825d85d3ef4fd297f416a4447b728a58230a07f3c4ffe350aa41c |
| `docs/proof/2026-11-27/pantera-attires/before/a4_snow_leopard_idle_y0_BEFORE.png` | 8ef064c35a6101e3e7ae62d766805e87abb802d4708150f96cdc30b6ce73de00 |
| `docs/proof/2026-11-27/pantera-attires/before/results_before.json` | 2424114d9cb49bcf3c4d8d70555dceec1ef149745c717f88d93a7197a800051c |
| `docs/proof/2026-11-27/pantera-attires/before/sheet_before_y0.png` | 2e7cd5732992d7041b8458fc38eeaa9e9b39d5e81c826db3d7fc7becb34bb4d9 |
| `docs/proof/2026-11-27/pantera-attires/before/sheet_before_y90.png` | 1d1f301d2427004bbe12220296e9c22d74e549f5352cf68771622409bf4259bc |
