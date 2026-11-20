# DW kit-pack move map log

Mapped 2026-11-08 (branch `dw-followups`) by `tools/anim/dw_map_kit_moves.py` from the measured moveset library — never invented. One `moves` entry per packed clip with a library move, keyed by the library move id minus `dw:`; `input` null (no measured DW input), `active_frames` null (no hit timing in the decode), `verified` false (not yet watched playing).

## Sources (SHA-256)

- moveset library: `game/data/moveset-library/banks/dw.json` sha256 `4c4959dce0cafe3e50a391384cbeb3dfcfa8c95a8c9e98c6e1a226e9f46f5a2d`
- curves (kit cross-check): `teardown/tekken5/dw-motion-curves.json` sha256 `5c5d9f8e0811547b7de1591a3f30bc1e6a2124dddddb1437268ab8e0a21ac054`
- pack before mapping: `moves.pantera.pack.json` sha256 `199633d990b6bd250b778741710232bd11dda5c062af6dbdf1fe210f9c85ef06`
- pack before mapping: `moves.warden.pack.json` sha256 `d947eca414b5a5ad8209d74aaa87d0975dc20e394af105e15852d3850918ef46`
- pack before mapping: `moves.unmasked.pack.json` sha256 `013813aa934f774c1794f7a1a07cfc6948eb27802267af3d454a37ae20c36506`
- pack before mapping: `moves.drowned-ogre.pack.json` sha256 `3f49740ed00bc599c90259bff4bbb4eede688383ebe0e5479a67d168ea5a2606`
- pack before mapping: `moves.wave-echo.pack.json` sha256 `5a5afc8e11a487647a97753ca5b153bcb27646b291f224449bcb29a7838bc922`

## moves.pantera.pack.json — 54 clips, 54 moves, 0 skipped

| move key | clip | library move | type | frames | gloss |
|---|---|---|---|---|---|
| `1+3` | `ikdv_36_nage_f` | `dw:surge:36-nage-f` | throw | 120 | throw, variant 36, _f variant |
| `2+4` | `ikdv_36_nage_y` | `dw:surge:36-nage-y` | throw | 126 | throw, variant 36, _y variant |
| `surge` | `dwhadoh00` | — (pilot move, no library entry) | — | — | pilot-mapped, kept as-is |
| `surge-trigger` | `ozhe_power` | `dw:unmasked:ozhe-power` | strike | 45 | power |
| `surge:all-beam` | `ikdv_all_beam` | `dw:surge:all-beam` | special | 85 | beam hitting all targets |
| `surge:b-nage-f` | `ikdv_b_nage_f` | `dw:surge:b-nage-f` | throw | 170 | throw, variant b, _f variant |
| `surge:b-nage-y` | `ikdv_b_nage_y` | `dw:surge:b-nage-y` | throw | 170 | throw, variant b, _y variant |
| `surge:beam` | `ikdv_beam` | `dw:surge:beam` | special | 85 | beam / laser |
| `surge:chaku` | `ikdv_chaku` | `dw:surge:chaku` | transition | 20 | landing |
| `surge:d-beam` | `ikdv_d_beam` | `dw:surge:d-beam` | special | 65 | devil beam |
| `surge:d-jump-k` | `ikdv_d_jump_k` | `dw:surge:d-jump-k` | aerial | 57 | devil jump kick |
| `surge:d-jump-p` | `ikdv_d_jump_p` | `dw:surge:d-jump-p` | aerial | 62 | devil jump punch |
| `surge:d-nagi-beam` | `ikdv_d_nagi_beam` | `dw:surge:d-nagi-beam` | special | 70 | devil sweeping beam |
| `surge:dsrp` | `ikdv_dsrp` | `dw:surge:dsrp` | strike | 65 | opaque token |
| `surge:dsrp-k` | `ikdv_dsrp_k` | `dw:surge:dsrp-k` | strike | 77 | opaque token, kick variant |
| `surge:dv-jz` | `ikdv_dv_jz` | `dw:surge:dv-jz` | strike | 90 | opaque token |
| `surge:dv2kam2` | `ikdv_dv2kam2` | `dw:surge:dv2kam2` | strike | 101 | opaque token |
| `surge:fstep` | `ikdv_fstep` | `dw:surge:fstep` | transition | 32 | forward step |
| `surge:jump-beam` | `ikdv_jump_beam` | `dw:surge:jump-beam` | special | 130 | jumping beam |
| `surge:jump-k` | `ikdv_jump_k` | `dw:surge:jump-k` | aerial | 77 | jumping kick |
| `surge:jump-p` | `ikdv_jump_p` | `dw:surge:jump-p` | aerial | 63 | jumping punch |
| `surge:jz-dv` | `ikdv_jz_dv` | `dw:surge:jz-dv` | strike | 90 | opaque token |
| `surge:k-1` | `ikdv_k_1` | `dw:surge:k-1` | strike | 55 | kick variant 1 |
| `surge:k-2` | `ikdv_k_2` | `dw:surge:k-2` | strike | 59 | kick variant 2 |
| `surge:k-3` | `ikdv_k_3` | `dw:surge:k-3` | strike | 66 | kick variant 3 |
| `surge:k-4` | `ikdv_k_4` | `dw:surge:k-4` | strike | 70 | kick variant 4 |
| `surge:l2idou` | `ikdv_l2idou` | `dw:surge:l2idou` | transition | 40 | left movement |
| `surge:lturn` | `ikdv_lturn` | `dw:surge:lturn` | transition | 30 | left turn |
| `surge:lturn90` | `ikdv_lturn90` | `dw:surge:lturn90` | transition | 20 | left turn 90 degrees |
| `surge:lukemi` | `ikdv_lukemi` | `dw:surge:lukemi` | transition | 50 | left breakfall |
| `surge:nara` | `ikdv_nara` | `dw:surge:nara` | strike | 66 | opaque token |
| `surge:nige00` | `ikdv_nige00` | `dw:surge:nige00` | transition | 61 | escape / flee |
| `surge:p-1` | `ikdv_p_1` | `dw:surge:p-1` | strike | 39 | punch variant 1 |
| `surge:p-2` | `ikdv_p_2` | `dw:surge:p-2` | strike | 40 | punch variant 2 |
| `surge:p-3` | `ikdv_p_3` | `dw:surge:p-3` | strike | 54 | punch variant 3 |
| `surge:p-4` | `ikdv_p_4` | `dw:surge:p-4` | strike | 51 | punch variant 4 |
| `surge:p-5` | `ikdv_p_5` | `dw:surge:p-5` | strike | 56 | punch variant 5 |
| `surge:p-kaitenk` | `ikdv_p_kaitenk` | `dw:surge:p-kaitenk` | strike | 64 | punch into spinning kick |
| `surge:pk` | `ikdv_pk` | `dw:surge:pk` | strike | 49 | punch-kick combo |
| `surge:ppk` | `ikdv_ppk` | `dw:surge:ppk` | strike | 69 | punch-punch-kick combo |
| `surge:ppp-nage-f` | `ikdv_ppp_nage_f` | `dw:surge:ppp-nage-f` | throw | 92 | 3-punch combo into throw, _f variant |
| `surge:ppp-nage-y` | `ikdv_ppp_nage_y` | `dw:surge:ppp-nage-y` | throw | 92 | 3-punch combo into throw, _y variant |
| `surge:r2idou` | `ikdv_r2idou` | `dw:surge:r2idou` | transition | 40 | right movement |
| `surge:rturn` | `ikdv_rturn` | `dw:surge:rturn` | transition | 30 | right turn |
| `surge:rturn90` | `ikdv_rturn90` | `dw:surge:rturn90` | transition | 20 | right turn 90 degrees |
| `surge:rukemi` | `ikdv_rukemi` | `dw:surge:rukemi` | transition | 50 | right breakfall |
| `surge:run-p` | `ikdv_run_p` | `dw:surge:run-p` | strike | 52 | running punch |
| `surge:shoryu` | `ikdv_shoryu` | `dw:surge:shoryu` | strike | 50 | rising dragon uppercut |
| `surge:sjk` | `ikdv_sjk` | `dw:surge:sjk` | strike | 67 | opaque token |
| `surge:sjk00` | `ikdv_sjk00` | `dw:surge:sjk00` | strike | 66 | opaque token, variant 00 |
| `surge:sjk01` | `ikdv_sjk01` | `dw:surge:sjk01` | strike | 60 | opaque token, variant 01 |
| `surge:sjk02` | `ikdv_sjk02` | `dw:surge:sjk02` | strike | 70 | opaque token, variant 02 |
| `surge:sjk03` | `ikdv_sjk03` | `dw:surge:sjk03` | strike | 70 | opaque token, variant 03 |
| `surge:sway` | `ikdv_sway` | `dw:surge:sway` | transition | 35 | sway |

## moves.warden.pack.json — 39 clips, 39 moves, 0 skipped

| move key | clip | library move | type | frames | gloss |
|---|---|---|---|---|---|
| `warden:bakutyu` | `kmb1_bakutyu` | `dw:warden:bakutyu` | strike | 65 | explosion-type attack |
| `warden:bakutyushot` | `kmb1_bakutyushot` | `dw:warden:bakutyushot` | special | 205 | explosion shot |
| `warden:charge-shot-02` | `kmb1_charge_shot_02` | `dw:warden:charge-shot-02` | special | 137 | charged shot, variant 2 |
| `warden:guard-mm` | `kmb1_guard_mm` | `dw:warden:guard-mm` | hold | 30 | guard |
| `warden:hijump-shot` | `kmb1_hijump_shot` | `dw:warden:hijump-shot` | special | 200 | high-jump shot |
| `warden:histep-l` | `kmb1_histep_l` | `dw:warden:histep-l` | transition | 55 | high step, left |
| `warden:histep-r` | `kmb1_histep_r` | `dw:warden:histep-r` | transition | 55 | high step, right |
| `warden:jumpmachinegun` | `kmb1_jumpmachinegun` | `dw:warden:jumpmachinegun` | aerial | 211 | jumping machine gun |
| `warden:kamae` | `kmb1_kamae` | `dw:warden:kamae` | stance | 150 | stance |
| `warden:lk` | `kmb1_lk` | `dw:warden:lk` | strike | 64 | left kick |
| `warden:lk-histep-r` | `kmb1_lk_histep_r` | `dw:warden:lk-histep-r` | strike | 60 | left kick into right high step |
| `warden:lturn180` | `kmb1_lturn180` | `dw:warden:lturn180` | transition | 30 | left turn 180 degrees |
| `warden:lturn90` | `kmb1_lturn90` | `dw:warden:lturn90` | transition | 20 | left turn 90 degrees |
| `warden:machinegun` | `kmb1_machinegun` | `dw:warden:machinegun` | strike | 225 | machine gun |
| `warden:machinegun-f` | `kmb1_machinegun_f` | `dw:warden:machinegun-f` | strike | 60 | machine gun, _f variant |
| `warden:rk` | `kmb1_rk` | `dw:warden:rk` | strike | 70 | right kick |
| `warden:rk-histep-l` | `kmb1_rk_histep_l` | `dw:warden:rk-histep-l` | strike | 70 | right kick into left high step |
| `warden:rturn180` | `kmb1_rturn180` | `dw:warden:rturn180` | transition | 30 | right turn 180 degrees |
| `warden:rturn90` | `kmb1_rturn90` | `dw:warden:rturn90` | transition | 20 | right turn 90 degrees |
| `warden:run01-start` | `kmb1_run01_start` | `dw:warden:run01-start` | strike | 32 | run cycle, start |
| `warden:run02-loop` | `kmb1_run02_loop` | `dw:warden:run02-loop` | strike | 32 | run cycle, loop |
| `warden:run03-walk` | `kmb1_run03_walk` | `dw:warden:run03-walk` | transition | 32 | run cycle, walk |
| `warden:shortshot-shot` | `kmb1_shortshot_shot` | `dw:warden:shortshot-shot` | special | 65 | short shot, shot |
| `warden:shortshot-soten` | `kmb1_shortshot_soten` | `dw:warden:shortshot-soten` | special | 102 | short shot, soten variant |
| `warden:shotgun-cyop` | `kmb1_shotgun_cyop` | `dw:warden:shotgun-cyop` | special | 59 | shotgun, cyop variant |
| `warden:shotgun-shot` | `kmb1_shotgun_shot` | `dw:warden:shotgun-shot` | special | 65 | shotgun shot |
| `warden:shotgun-soten` | `kmb1_shotgun_soten` | `dw:warden:shotgun-soten` | special | 102 | shotgun, soten variant |
| `warden:step-in` | `kmb1_step_in` | `dw:warden:step-in` | transition | 45 | step in |
| `warden:step-l` | `kmb1_step_l` | `dw:warden:step-l` | transition | 40 | step left |
| `warden:step-r` | `kmb1_step_r` | `dw:warden:step-r` | transition | 40 | step right |
| `warden:tojo` | `kmb1_tojo` | `dw:warden:tojo` | taunt | 180 | entrance / appearance |
| `warden:walk-f01-start` | `kmb1_walk_f01_start` | `dw:warden:walk-f01-start` | transition | 30 | walk forward, start |
| `warden:walk-f02-loop` | `kmb1_walk_f02_loop` | `dw:warden:walk-f02-loop` | transition | 45 | walk forward, loop |
| `warden:walk-l` | `kmb1_walk_l` | `dw:warden:walk-l` | transition | 75 | walk left |
| `warden:walk-r` | `kmb1_walk_r` | `dw:warden:walk-r` | transition | 75 | walk right |
| `warden:wdown` | `kmb1_wdown` | `dw:warden:wdown` | strike | 91 | knocked down |
| `warden:wshot` | `kmb1_wshot` | `dw:warden:wshot` | special | 69 | weapon shot |
| `warden:yoko-l` | `kmb1_yoko_l` | `dw:warden:yoko-l` | transition | 125 | side step left |
| `warden:yoko-r` | `kmb1_yoko_r` | `dw:warden:yoko-r` | transition | 125 | side step right |

## moves.unmasked.pack.json — 29 clips, 29 moves, 0 skipped

| move key | clip | library move | type | frames | gloss |
|---|---|---|---|---|---|
| `unmasked:360` | `ozb3_360` | `dw:unmasked:360` | strike | 100 | 360-degree spin |
| `unmasked:burn` | `ozb3_burn` | `dw:unmasked:burn` | special | 210 | burning |
| `unmasked:burn2` | `ozb3_burn2` | `dw:unmasked:burn2` | special | 147 | burning, variant 2 |
| `unmasked:bwalk00` | `ozb3_bwalk00` | `dw:unmasked:bwalk00` | transition | 35 | back walk, variant 00 |
| `unmasked:bwalk01` | `ozb3_bwalk01` | `dw:unmasked:bwalk01` | transition | 90 | back walk, variant 01 |
| `unmasked:dead` | `ozb3_dead` | `dw:unmasked:dead` | strike | 500 | death animation |
| `unmasked:firehado2` | `ozb3_firehado2` | `dw:unmasked:firehado2` | special | 153 | fire wave, variant 2 |
| `unmasked:fumi` | `ozb3_fumi` | `dw:unmasked:fumi` | strike | 125 | stomp |
| `unmasked:greaction2` | `ozb3_greaction2` | `dw:unmasked:greaction2` | hold | 30 | guard reaction, variant 2 |
| `unmasked:guardkama2` | `ozb3_guardkama2` | `dw:unmasked:guardkama2` | stance | 10 | guard stance, variant 2 |
| `unmasked:guardpose` | `ozb3_guardpose` | `dw:unmasked:guardpose` | hold | 2 | guard pose |
| `unmasked:guardroop2` | `ozb3_guardroop2` | `dw:unmasked:guardroop2` | hold | 72 | guard loop, variant 2 |
| `unmasked:houmingf` | `ozb3_houmingf` | `dw:unmasked:houmingf` | special | 175 | homing fire |
| `unmasked:issoku` | `ozb3_issoku` | `dw:unmasked:issoku` | transition | 60 | one-foot step |
| `unmasked:kamae` | `ozb3_kamae` | `dw:unmasked:kamae` | stance | 72 | stance |
| `unmasked:kamaguard2` | `ozb3_kamaguard2` | `dw:unmasked:kamaguard2` | stance | 5 | stance-guard, variant 2 |
| `unmasked:lwalk` | `ozb3_lwalk` | `dw:unmasked:lwalk` | transition | 90 | left walk |
| `unmasked:run00` | `ozb3_run00` | `dw:unmasked:run00` | strike | 54 | run, variant 00 |
| `unmasked:run01` | `ozb3_run01` | `dw:unmasked:run01` | strike | 54 | run, variant 01 |
| `unmasked:rwalk` | `ozb3_rwalk` | `dw:unmasked:rwalk` | transition | 90 | right walk |
| `unmasked:shippo` | `ozb3_shippo` | `dw:unmasked:shippo` | strike | 100 | tail |
| `unmasked:tatumaki` | `ozb3_tatumaki` | `dw:unmasked:tatumaki` | strike | 110 | tornado / whirlwind |
| `unmasked:tobinoki` | `ozb3_tobinoki` | `dw:unmasked:tobinoki` | strike | 60 | opaque token |
| `unmasked:toujyou` | `ozb3_toujyou` | `dw:unmasked:toujyou` | taunt | 460 | entrance / appearance |
| `unmasked:tunoupper2` | `ozb3_tunoupper2` | `dw:unmasked:tunoupper2` | strike | 120 | horn upper, variant 2 |
| `unmasked:walk00` | `ozb3_walk00` | `dw:unmasked:walk00` | transition | 64 | walk, variant 00 |
| `unmasked:walk01` | `ozb3_walk01` | `dw:unmasked:walk01` | transition | 90 | walk, variant 01 |
| `unmasked:warp1` | `ozb3_warp1` | `dw:unmasked:warp1` | strike | 100 | teleport 1 |
| `unmasked:warp2` | `ozb3_warp2` | `dw:unmasked:warp2` | strike | 105 | teleport 2 |

## moves.drowned-ogre.pack.json — 25 clips, 25 moves, 0 skipped

| move key | clip | library move | type | frames | gloss |
|---|---|---|---|---|---|
| `drowned_ogre:180` | `kob2_180` | `dw:drowned_ogre:180` | transition | 75 | 180-degree turn |
| `drowned_ogre:ap` | `kob2_ap` | `dw:drowned_ogre:ap` | strike | 180 | opaque token |
| `drowned_ogre:back2fire` | `kob2_back2fire` | `dw:drowned_ogre:back2fire` | special | 145 | back to fire |
| `drowned_ogre:bwalk` | `kob2_bwalk` | `dw:drowned_ogre:bwalk` | transition | 90 | back walk |
| `drowned_ogre:escape` | `kob2_escape` | `dw:drowned_ogre:escape` | transition | 321 | escape |
| `drowned_ogre:fire` | `kob2_fire` | `dw:drowned_ogre:fire` | special | 120 | fire |
| `drowned_ogre:fly2center` | `kob2_fly2center` | `dw:drowned_ogre:fly2center` | aerial | 140 | fly to center |
| `drowned_ogre:fly2fire` | `kob2_fly2fire` | `dw:drowned_ogre:fly2fire` | special | 110 | fly to fire |
| `drowned_ogre:fly2landing` | `kob2_fly2landing` | `dw:drowned_ogre:fly2landing` | aerial | 67 | fly to landing |
| `drowned_ogre:flykamae` | `kob2_flykamae` | `dw:drowned_ogre:flykamae` | stance | 91 | flying stance |
| `drowned_ogre:fwalk` | `kob2_fwalk` | `dw:drowned_ogre:fwalk` | transition | 90 | forward walk |
| `drowned_ogre:hornatk` | `kob2_hornatk` | `dw:drowned_ogre:hornatk` | strike | 96 | horn attack |
| `drowned_ogre:kamae` | `kob2_kamae` | `dw:drowned_ogre:kamae` | stance | 121 | stance |
| `drowned_ogre:lstep` | `kob2_lstep` | `dw:drowned_ogre:lstep` | transition | 60 | left step |
| `drowned_ogre:lwalk` | `kob2_lwalk` | `dw:drowned_ogre:lwalk` | transition | 90 | left walk |
| `drowned_ogre:rstep` | `kob2_rstep` | `dw:drowned_ogre:rstep` | transition | 60 | right step |
| `drowned_ogre:run` | `kob2_run` | `dw:drowned_ogre:run` | strike | 54 | run |
| `drowned_ogre:rwalk` | `kob2_rwalk` | `dw:drowned_ogre:rwalk` | transition | 90 | right walk |
| `drowned_ogre:snakeatk` | `kob2_snakeatk` | `dw:drowned_ogre:snakeatk` | strike | 120 | snake attack |
| `drowned_ogre:stbwalk` | `kob2_stbwalk` | `dw:drowned_ogre:stbwalk` | stance | 35 | stance back walk |
| `drowned_ogre:stfwalk` | `kob2_stfwalk` | `dw:drowned_ogre:stfwalk` | stance | 64 | stance forward walk |
| `drowned_ogre:strun` | `kob2_strun` | `dw:drowned_ogre:strun` | stance | 54 | stance run |
| `drowned_ogre:stwarp` | `kob2_stwarp` | `dw:drowned_ogre:stwarp` | stance | 40 | stance teleport |
| `drowned_ogre:tailatk` | `kob2_tailatk` | `dw:drowned_ogre:tailatk` | strike | 111 | tail attack |
| `drowned_ogre:warp2fire` | `kob2_warp2fire` | `dw:drowned_ogre:warp2fire` | special | 179 | teleport to fire |

## moves.wave-echo.pack.json — 5 clips, 5 moves, 0 skipped

| move key | clip | library move | type | frames | gloss |
|---|---|---|---|---|---|
| `unmasked:ozhe-power` | `ozhe_power` | `dw:unmasked:ozhe-power` | strike | 45 | power |
| `unmasked:oznj-meteorite` | `oznj_meteorite` | `dw:unmasked:oznj-meteorite` | aerial | 110 | meteorite |
| `unmasked:ozt4-aidoring` | `ozt4_aidoring` | `dw:unmasked:ozt4-aidoring` | strike | 60 | opaque token |
| `unmasked:ozt4-goron` | `ozt4_goron` | `dw:unmasked:ozt4-goron` | strike | 57 | rumble |
| `unmasked:ozt4-kamae` | `ozt4_kamae` | `dw:unmasked:ozt4-kamae` | stance | 80 | stance |

## Library moves with no baked clip (unmapped — nothing to bind)

| library move | clip | type | reason not baked |
|---|---|---|---|
| `dw:surge_bloom:newhane01` | `djin_newhane01` | strike | 12-bone wings/feathers appendage motion, not fighter motion |
| `dw:surge_bloom:newhane02` | `djin_newhane02` | strike | 12-bone wings/feathers appendage motion, not fighter motion |
| `dw:surge_bloom:newhane03` | `djin_newhane03` | strike | 12-bone wings/feathers appendage motion, not fighter motion |
| `dw:surge_trigger:dwup00` | `dwup00` | strike | 27-bone single dropped from the pantera pack by the trigger swap (ozhe_power replaces dwup00) |
| `dw:drowned_ogre:tail1` | `kob2_tail1` | strike | 4-bone appendage part-clip (tail/teil1), not a full-body skeleton |
| `dw:drowned_ogre:tail2` | `kob2_tail2` | strike | 4-bone appendage part-clip (tail/teil1), not a full-body skeleton |
| `dw:drowned_ogre:tail3` | `kob2_tail3` | strike | 4-bone appendage part-clip (tail/teil1), not a full-body skeleton |
| `dw:drowned_ogre:tail4` | `kob2_tail4` | strike | 4-bone appendage part-clip (tail/teil1), not a full-body skeleton |
| `dw:unmasked:all-teil1` | `ozb3_all_teil1` | strike | 4-bone appendage part-clip (tail/teil1), not a full-body skeleton |
| `dw:unmasked:demo-teil1` | `ozb3_demo_teil1` | strike | 4-bone appendage part-clip (tail/teil1), not a full-body skeleton |
| `dw:unmasked:hado-teil1` | `ozb3_hado_teil1` | special | 4-bone appendage part-clip (tail/teil1), not a full-body skeleton |
| `dw:unmasked:horming-teil1` | `ozb3_horming_teil1` | strike | 4-bone appendage part-clip (tail/teil1), not a full-body skeleton |
| `dw:unmasked:shipo1` | `ozb3_shipo1` | strike | 4-bone appendage part-clip (tail/teil1), not a full-body skeleton |
| `dw:unmasked:tatumakiup-teil1` | `ozb3_tatumakiup_teil1` | strike | 4-bone appendage part-clip (tail/teil1), not a full-body skeleton |
| `dw:unmasked:tunoup-teil1` | `ozb3_tunoup_teil1` | strike | 4-bone appendage part-clip (tail/teil1), not a full-body skeleton |

## What is NOT mapped

- Inputs, damage, hitboxes: the library carries none of these for DW moves (all null) — the game times DW moves on the moveset's own S/A/R. Mapping a clip to a move does NOT claim an input for it.
- The 24 ikt5 35-bone clips: decoded, but no library entry, so the bank-keyed bake path never baked them. They need library entries first, not a new FK model.
- The 33 non-35/27 clips: not bakeable with the current FK model (11× 4-bone, 15× 78-bone 1-frame init poses, 1× 96-bone devil init object, 2× 111-bone boss init objects, 4× 12-bone wings) — counted from `dw_measurements.json`.
