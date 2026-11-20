# CORNERSTONE — Build Record (2026-10-21)

Owner design drop 2026-10-21 (~01:54 CDT), verbatim core: *"I told u how ryuji character will be mixed with the rock from WWE and do the uranage/rock bottom, he will also get the rock bottom from king and from WWE all stars, and some animations of the rock from the WWE teardown games, and kings jumping diving elbow attack, mixed with ryuji yamazakis stance and taunts and moveset and antics mixed with the rock persona from early attitude era WWE. And his name will be CornerStone, log that into the repo push and merge it clean without clobbering work from any side and I'll get his model to u, u get 3d ryuji moves and stance and data to wire into him and everything else I asked for: [Tripo link] and u can give him ryuji tongue stick out taunts and attacks also younger toguro is another inspiration for him if u can pull from the yuyuhakusho game his fingernail blast and etc"*

Prior foundation (owner 2026-10-19, MEMORY.md): *"Ryuji Yamazaki version… black shirt, blonde top hair… obnoxious like Ryuji, sticks his tongue out, personality mixed with The Rock"* — moveset = Ryuji base + Rock's moves, Rock Bottom from King in Tekken + Urban Reign/Tekken/other teardowns. Canon: `CANON.md` §"CORNERSTONE — The Obnoxious One (Bonus)" (PR #426) + `RENAME-MAP.md`. Internal id stays `ryuji-rock`; display name is CORNERSTONE everywhere.

## Phase 2 — Model

- Owner's Tripo: https://studio.tripo3d.ai/3d-model/20c1fd2e-40d0-4500-9be6-50f6494ab5e1 — "tattooed man 3d model" (Tripo account tyneshiahall19), pulled 2026-10-21 via `tools/tripo-pull/` (no sign-in).
- GLB: 18,872,720 B, sha256 `658848674696b6c4e47c55f773d2c55e07359595e51e57ce273704dc4871049d` — 1 mesh, 1 material, 3 embedded textures, KHR_mesh_quantization (meshopt). Original archived on release `cornerstone-tripo-pulls-20261021` (server-side size verified).
- Wired: `roster/ryuji-rock/attires/attire1/model.glb` (the path `game/js/assets.js` already had pre-wired for `ryuji-rock`), display name in `game/js/roster-full.js`, guard `pending: true` removed in `game/tests/model-key-guard.test.mjs` (his file-exists test now runs), `docs/MODEL-INVENTORY.md` roster-slot row, `docs/MODEL-KEY-AUDIT-2026-10-21.md` addendum, `roster/TRIPO-REGISTRY.md` CORNERSTONE row.
- What the model is (structural read of the GLB): a single static Tripo mesh — muscular tattooed man (the pull's own name), 3 textures. Rig status: unrigged static, same class as the other Tripo pulls (🎨/rig pipeline applies per roster practice). Front render: `docs/tpose-refs/ryuji-rock/a1_front.png` (own-eyes verified — see Phase 2 PR).

## Phase 3 — Moves, stance, data (`game/assets/movesets/ryuji-rock.json`: 24 → 129 moves)

### Yamazaki layer — WIRED (data)
Additive union of `game/assets/movesets/ryuji.json` (the full KOF Yamazaki set: 103 moves, KOF XV frame data — sources dreamcancel / SNK wiki / supercombo KOF '98, converted per that file's `frame_convention`) into `ryuji-rock.json`: **+98 moves**, 5 input collisions held (pre-existing entries win; recorded in the file's `cornerstone_build.skipped_input_collisions_main_wins`):

- The Hebi Tsukai (Serpent) family — Hebi Tsukai A/B/C + follow-ups (Yaki'ire, Hebi Korogari, Danko), the extended-arm snake strikes.
- **Sadomazo L/H/EX (hcf+3 / hcf+4 / hcf+3+4)** — Yamazaki's tongue-stick-out taunt that IS an attack (counter-grabs a high/mid hit into a headbutt) — the owner's "tongue stick out taunts and attacks", on top of the file's WH-original `S` TONGUE OUT signature and the KOF `2+3 (taunt)` Taunt entry.
- Bai Gaeshi H/EX projectiles, Suna Kake sand-kick family, Bakudan Pachiki, Todome, Sabaki no Aikuchi, Nejikomi Bunmawashi, Guillotine L/H/EX, Pit Viper, Drill (climax) + Drill levels 1–4, KOF system (MAX Mode, Blow Back, Shatter Strike, hops/jumps) and the full KOF normals set.
- ROCK'S DDT (wh_original), PEOPLE'S ELBOW grounded (`d+1+2`), PEOPLE'S ELBOW (FLYING) (`u/f+2+4`).

**Stance:** Yamazaki's stance is recorded in the file's `cornerstone_build.stance` — the Hakkesshu slouch with tongue flicks; taunt layer = `S` TONGUE OUT + KOF Taunt + the Sadomazo family. In-game stance CLIP today = King T3 bank stance (`game/js/fighter.js` MOVESET_MAP `'ryuji-rock': 'king'`) — a named proxy: **no KOF game teardown exists in the holdings** (searched 2026-10-19 for his model hunt and again for this build), so Yamazaki-sourced entries carry `anim_ref: kofxv:ryuji:*` naming their KOF XV source animations — real data wired now, clips land with a KOF teardown. Nothing was fabricated.

### Rock Bottom / uranage — multi-source, as ordered
| Source | Status | Where |
|---|---|---|
| King (Tekken) | ✅ WIRED (pre-existing) | `b,n,f+1+2` (T3 King row 281) + `d/f+1+2` (row 210) + specials `hcb+1+2` (super) |
| King (Tekken 7) | ✅ WIRED (this union) | `FC d/b,d,d/b+1+2` ROCK BOTTOM — modeled on T7 King's Clothesline Press (from ryuji.json, wavu T7 King movelist) |
| The Rock — No Mercy teardown | ✅ WIRED as data (this build) | `f+2+4` ROCK BOTTOM (NO MERCY) → `mk:MK-1240` (anim_37FA.npy, 49f; P2 MK-1241/anim_37FB.npy) |
| The Rock — WMXIX teardown | ❌ NOT IDENTIFIABLE | All 169 WMXIX library moves are provisional unnamed grapples; per-clip identity undecoded (only slot 000 = Triple H confirmed). No WMXIX Rock data invented. |
| WWE All Stars | ⏳ PENDING SOURCE | Queued on the teardown-idle queue (owner 2026-10-20), NOT acquired, NOT torn down. Wires in when the teardown exists. |

### The Rock — No Mercy clips wired as data (`mk:` entries)
From `moveset-library/movesets/mat-kings-move-database.json` (WWF No Mercy teardown, 100% wired as library data): ROCK BOTTOM `mk:MK-1240` · PEOPLE'S ELBOW `mk:MK-2843` (+P2 MK-2844) · PEOPLE'S ELBOW (RUNNING) `mk:MK-3473` · ROCK TAUNT `mk:MK-4353` — one entry citing all five Rock-named taunts (MK-4353 Rock 01 62f, MK-4347 Rock 02, MK-4354 Rock 03, MK-4233 Entry Way, MK-4269 In The Ring; DB input `1+2+3+4`) · ROCK SPINEBUSTER `mk:MK-1885` · ROCK STOMP `mk:MK-3120` · ROCK SPINNING DDT `mk:MK-3659`. Skipped, recorded in-file: Rock Punch MK-2102 (DB input `2` — owned by RYUJI 2) and Rock Clothesline MK-2216 (DB input `f,f+2` — owned by BRAHMA BULL LARIAT, his clothesline spot).

Damage/timing on `mk:` entries are labeled WH data-layer values — the mat-kings DB carries no power join for Rock entries (survey finding); the clips are the source of truth.

**Playback status, stated plainly:** the `mk:` (and `kofxv:`) entries are DATA-wired with named source clips. The runtime animation bank/loader today is Tekken-3-only (`game/js/t3anims.js`); the AKI→Tekken retarget (`teardown/wwf-no-mercy/aki_to_tekken3.py`) is proven on one clip (0x339A on T3 King) and the Rock clips have **not** been baked yet. That bake is the anim lanes' named next step — it is not faked here. What plays in-game today for CornerStone: his King bank (stance, Rock Bottom row 281, the T3-sourced set) + every data entry resolving through the fighter's move system.

### King's jumping diving elbow — WIRED
`u/f+2` PEOPLE'S ELBOW is identified in-file with its Tekken 7 source: King **High Elbow Drop** (u/f+2, damage 35 [42], speed i47, on block −17, KND, crushes low/mid/high — `docs/t7t8-reference/frame-data-t7/king.json`, id king_31) — King's jumping diving elbow attack, as ordered. The flying variant `u/f+2+4` (from ryuji.json) is likewise modeled on the air version.

### Younger Toguro — INTENT ONLY, source absent
Owner: *"younger toguro is another inspiration for him if u can pull from the yuyuhakusho game his fingernail blast and etc"*. Surveyed 2026-10-21: **no Yu Yu Hakusho game, teardown, or Toguro source exists in any holding** (western-heart full tree, game-reverse-engineering, local disk — zero hits). The design intent (incl. the fingernail blast) is recorded in CANON.md and in the moveset's `cornerstone_build.toguro_fingernail_blast`. No move data was invented; it wires in when a YYH source is acquired and torn down.

## No-loss proof
Union rule = the PR #407 pattern (identity = canonical input; whitespace/case-folded). Verified programmatically against `origin/main`: every pre-existing move deep-equal (the `u/f+2` elbow entry gained additive fields only), specials untouched, 24 → 129 moves. The 3 changed lines in the diff are `display`, `proxy_note` (appended), and the elbow entry's field separator — all declared in the PR.

## Harness proof
_Pending the render/RAM window on the build box — frames + console log land in `docs/cornerstone-proof-2026-10-21/` with the Phase 3 PR update._
