# Move clip coverage, every fighter (`tools/anim/plan_coverage_audit.mjs`)

**Read this first (2026-11-02):**
- **No-clip moves after PR #1491's last-resort tier:** 50 fighters have **zero** moves without a clip; Diablo 1, Kinpo 1, Pantera 10.
- **Pantera's 10** are long chain-throw stages that have neither a matching throw clip nor a matching earlier step. In the browser his real T7 clips cover more than Node sees.
- **Six fighters have no animation bank at all:** Vain Abel, Ryuji, Ryusan, Pond, Zen, Megami. Their bases have no decoded T3 / T7 bank in the repo yet. In a fight they fall back to their model's own locomotion plus procedural combat poses: never a real move clip.
- **Fix for those six:** bake their base characters' real T7 moves, the way Pantera's King moves were baked: `tools/anim/t7_move_resolve.py` + `t7_move_bake.py`.


59 fighters, 16696 moves: **1415 would play no clip** (bind pose = T-pose) by the game's own planner (Node; real T7 clips not loaded, so conservative). Easiest first.

| fighter | bank | moves | with a clip | no clip | examples |
|---|---|---|---|---|---|
| byou | jin | 753 | 100% | 0 |  |
| phantom | yoshimitsu | 563 | 100% | 0 |  |
| rave | lei | 477 | 100% | 0 |  |
| awapop | nina | 429 | 100% | 0 |  |
| star | xiaoyu | 427 | 100% | 0 |  |
| torch | anna | 419 | 100% | 0 |  |
| kai | eddy | 403 | 100% | 0 |  |
| samura1 | gunjack | 395 | 100% | 0 |  |
| kingtyrant | eddy | 390 | 100% | 0 |  |
| rin | jin | 385 | 100% | 0 |  |
| gyou | hwoarang | 383 | 100% | 0 |  |
| koreshi | heihachi | 376 | 100% | 0 |  |
| retsu | bryan | 373 | 100% | 0 |  |
| tobi | hwoarang | 360 | 100% | 0 |  |
| buffalo-bill | law | 351 | 100% | 0 |  |
| sha | xiaoyu | 350 | 100% | 0 |  |
| sakura | xiaoyu | 350 | 100% | 0 |  |
| zui | jin | 343 | 100% | 0 |  |
| thor | bryan | 342 | 100% | 0 |  |
| demonio | jin | 326 | 100% | 0 |  |
| cyborgx | gunjack | 323 | 100% | 0 |  |
| skull | bryan | 313 | 100% | 0 |  |
| tou | paul | 304 | 100% | 0 |  |
| gashadokuro | kuma | 290 | 100% | 0 |  |
| aotsuki | kuma | 290 | 100% | 0 |  |
| purplerain | jin | 286 | 100% | 0 |  |
| yukihyo | armorking | 284 | 100% | 0 |  |
| burger | bryan | 262 | 100% | 0 |  |
| nightwolf | julia | 243 | 100% | 0 |  |
| silvertongue | xiaoyu | 235 | 100% | 0 |  |
| slice | bryan | 230 | 100% | 0 |  |
| chordz | jin | 225 | 100% | 0 |  |
| mariposa-monarch | xiaoyu | 224 | 100% | 0 |  |
| charger | bryan | 218 | 100% | 0 |  |
| chatur | ogre | 214 | 100% | 0 |  |
| menajerii | kuma | 208 | 100% | 0 |  |
| waterfall | jin | 204 | 100% | 0 |  |
| docfrank | bosconovitch | 196 | 100% | 0 |  |
| bruno | bryan | 192 | 100% | 0 |  |
| scimitar | jin | 182 | 100% | 0 |  |
| michiko | jin | 181 | 100% | 0 |  |
| negativo | bryan | 155 | 100% | 0 |  |
| dio | heihachi | 149 | 100% | 0 |  |
| ryuji-rock | king | 144 | 100% | 0 |  |
| deathfang | heihachi | 142 | 100% | 0 |  |
| kronos | king | 113 | 100% | 0 |  |
| dorowani | gon | 108 | 100% | 0 |  |
| dxmmii-patchwork | jin | 72 | 100% | 0 |  |
| cainelias | king | 61 | 100% | 0 |  |
| baek-master-white | bryan | 51 | 100% | 0 |  |
| diablo | heihachi | 319 | 99.7% | 1 | `1,1,1` |
| kinpo | jin | 251 | 99.6% | 1 | `1+2+3+4,1+2` |
| pantera | king | 429 | 97.7% | 10 | `BACKDROP.1+2,3,4,1+3` `BACKDROP.1+2,4,1+2,1+2+3` `BURNING_HAMMER.2+4,3+4,1+3,1+2,1+2+3` `CANNONBALL_BUSTER.3+4,1+2,1+2+4` `CHICKEN_WING_FACE_LOCK.1+3,3+4,2+4,1+2,1+2+3` `CHICKEN_WING_FACE_LOCK.2,1,3,1+2+4,1+2+4` |
| vainabel | — | 75 | 0% | 75 | `1` `2` `3` `4` `d/f+1` `d+1` |
| ryuji | — | 142 | 0% | 142 | `1` `2` `3` `4` `5` `6` |
| ryusan | — | 226 | 0% | 226 | `1` `2` `3` `4` `1,2` `(1),2` |
| pond | — | 312 | 0% | 312 | `1` `2` `3` `4` `1+2` `1+2+3+4` |
| zen | — | 324 | 0% | 324 | `1` `2` `3` `4` `1+2` `1+2+3+4` |
| megami | — | 324 | 0% | 324 | `1` `2` `3` `4` `1+3` `2+4` |
