# Input resolver V2 — deterministic Tekken input (owner t116u, 2026-10-23 CT)

Owner: "presses give random moves, a neutral button fires a crouching kick instead of only d+3/d+4."

## Root causes found
1. **Touch stick latched 'down'** (game/js/input.js). After *holding* the stick down past 200 ms, moving it back to centre without lifting the finger never cleared `down` (only taps were released). Every following neutral 3/4 resolved as d+3/d+4/FC.x = the crouching kick. Also d→u without lifting was ignored. Fix: `_udStick()` — leaving the vertical zone always releases; switching u↔d releases then presses.
2. **Repeated-step motions matched one long hold** (`_seqMatch`): holding d/f and pressing 1 fired `d/f,d/f+1`; `f,F` vs `f,f,F` indistinguishable. V2 `_motionHeldV2` needs the stick to leave the direction between identical steps; inner `n` steps are real.
3. **Chord specials ignored stance** (`pressChord` step 1 was context-blind) → `REV.b+1+3` fired `b+1+3`. V2 resolves chords through the stance-aware table first.
4. **Specials without an `input` field crashed every chord press** (TypeError in parseSpecialInput) → guarded.
5. **Tap vs held spellings** (`d/f+2` vs `D/F+2`, `f,f,f+3` vs `f,f,F+3`) picked by fixed order. V2: held ≥ 8 frames (direction) / ≥ 4 frames (final motion step) = capital spelling.
6. **Neutral-ending motions** (`f,n,2`) vs held ones (`f,F+2`): V2 requires the stick state the notation says (released vs still held).
7. **Strings whose middle steps aren't standalone moves** (stance chain throws, long strings) were unreachable. V2 keeps a string cursor (800 ms) through intermediate steps.

No random/fallback selection exists in the resolver; the slots table maps one notation → one key. Moves with no command never bind to a button (merge keys containing `~` are never typed).

## Priority (V2)
string continuation → per state prefix most specific first (stance, R., BT., SS., FC. only while crouching, WS. only in the rising window): motion > held direction+button → then plain button. A neutral stick never reaches a directional / FC move.

## Flag
V2 ON by default. Old resolver: `localStorage.wh_input_resolver = 'legacy'` (or `window.WH_INPUT_RESOLVER='legacy'`). Legacy code is untouched in `_pressLegacy`.

## Test (CI: rig-guard → game-unit-tests)
`node test/input-determinism.test.mjs [--resolver legacy] [--report out.json]` — 125 fighters, every slot notation injected with the stance + stick it needs.

| | legacy | v2 |
|---|---|---|
| fighters fully passing | 36 | 93 |
| commands pass | 14552 | 15419 |
| non-string failures | 208 | **0** |
| string failures (reported, not gating) | 608 | 107 |
| neutral 1/2/3/4 wrong move | 0 in data path | 0 |
| touch stick re-centre releases down | **FAIL** | PASS |
| same input bound to 2 moves (data conflicts) | 192 | 34 |
| hold-button `*` commands (need release-timed input, not wired) | 142 | 142 |

DOA fighters (6) have no 2/4 slots in their decoded data → those buttons are dead (fire nothing), never a different move. Fill from the DOA4 decode when that batch lands.

## Remaining / port notes
- 107 long strings with chord or held-direction steps mid-string, 34 duplicate-spelling conflicts, 142 hold-button commands — lists in `docs/input/input-determinism-v2.json`.
- Port to AshLane / Brutal Fist: copy `_pressV2`, `_motionHeldV2`, `_heldFrames`, `_strPrefixes`, `_udStick` and the test harness; point the harness at that game's moveset dir.

## Per-fighter results
| fighter | legacy pass/tested | v2 pass/tested | v2 neutral 1/2/3/4 | v2 data conflicts | hold-button (not wired) |
|---|---|---|---|---|---|
| armor-king | 200/225 | 220/225 | ok ok ok ok | 0 | 6 |
| awapop | 319/355 | 349/355 | ok ok ok ok | 1 | 1 |
| baek | 31/31 | 31/31 | ok ok ok ok | 0 | 0 |
| baek-master-white | 34/34 | 34/34 | ok ok ok ok | 0 | 0 |
| blanka | 40/42 | 42/42 | ok ok ok ok | 0 | 0 |
| bob | 198/207 | 205/207 | ok ok ok ok | 0 | 2 |
| bruno | 133/135 | 135/135 | ok ok ok ok | 0 | 3 |
| buffalo-bill | 66/78 | 78/78 | ok ok ok ok | 0 | 0 |
| burger | 202/210 | 208/210 | ok ok ok ok | 0 | 3 |
| burger-demon | 200/208 | 206/208 | ok ok ok ok | 0 | 2 |
| burger-speed-demon | 195/204 | 202/204 | ok ok ok ok | 0 | 2 |
| burger-the-mouth | 193/202 | 200/202 | ok ok ok ok | 0 | 2 |
| byou | 60/60 | 60/60 | ok ok ok ok | 0 | 0 |
| cainelias | 41/41 | 41/41 | ok ok ok ok | 0 | 0 |
| charger | 40/42 | 42/42 | ok ok ok ok | 0 | 0 |
| charger-attire2 | 40/42 | 42/42 | ok ok ok ok | 0 | 0 |
| chatur | 125/126 | 126/126 | ok ok ok ok | 0 | 0 |
| chordz | 173/180 | 179/180 | ok ok ok ok | 0 | 2 |
| cyborgx | 251/270 | 269/270 | ok ok ok ok | 0 | 7 |
| deathfang | 4/4 | 4/4 | ok ok ok ok | 0 | 0 |
| deathfang-werewolf | 8/8 | 8/8 | ok ok ok ok | 0 | 0 |
| demonio | 239/250 | 249/250 | ok ok ok ok | 1 | 0 |
| demonio-bloodline-ember | 242/250 | 249/250 | ok ok ok ok | 1 | 0 |
| demonio-human | 242/250 | 249/250 | ok ok ok ok | 1 | 0 |
| demonio-winged | 283/308 | 305/308 | ok ok ok ok | 2 | 3 |
| diablo | 222/236 | 235/236 | ok ok ok ok | 1 | 9 |
| dio | 119/119 | 119/119 | ok ok ok ok | 0 | 1 |
| doa-ayane | 23/23 | 23/23 | ok dead ok dead | 0 | 0 |
| doa-bass | 20/20 | 20/20 | ok dead ok dead | 0 | 0 |
| doa-hayabusa | 16/16 | 16/16 | ok dead ok dead | 0 | 0 |
| doa-jannlee | 18/21 | 21/21 | ok dead ok dead | 0 | 0 |
| doa-kasumi | 16/18 | 18/18 | ok dead ok dead | 0 | 0 |
| doa-tina | 24/25 | 25/25 | ok dead ok dead | 0 | 0 |
| doc-frank-frankenstein | 133/143 | 142/143 | ok ok ok ok | 0 | 0 |
| doc-frank-hood | 133/143 | 142/143 | ok ok ok ok | 0 | 0 |
| doc-frank-machine-shop | 157/163 | 162/163 | ok ok ok ok | 0 | 0 |
| doc-frank-wowomomo | 133/143 | 142/143 | ok ok ok ok | 0 | 0 |
| docfrank | 132/143 | 143/143 | ok ok ok ok | 0 | 0 |
| dorowani | 21/23 | 23/23 | ok ok ok ok | 0 | 0 |
| dxmmii | 53/53 | 53/53 | ok ok ok ok | 0 | 0 |
| dxmmii-patchwork | 54/54 | 54/54 | ok ok ok ok | 0 | 0 |
| gyou | 303/314 | 313/314 | ok ok ok ok | 1 | 0 |
| gyou-spirit-body | 72/84 | 84/84 | ok ok ok ok | 0 | 0 |
| hugo | 9/9 | 9/9 | ok ok ok ok | 0 | 0 |
| iori | 7/7 | 7/7 | ok ok ok ok | 0 | 0 |
| jin_soul | 393/439 | 416/439 | ok ok ok ok | 5 | 5 |
| kai | 280/287 | 287/287 | ok ok ok ok | 0 | 0 |
| kingtyrant | 260/273 | 273/273 | ok ok ok ok | 0 | 0 |
| kinpo | 186/197 | 195/197 | ok ok ok ok | 1 | 7 |
| koreshi | 250/273 | 273/273 | ok ok ok ok | 0 | 4 |
| kronos | 65/68 | 67/68 | ok ok ok ok | 0 | 0 |
| kronos-attire2 | 65/68 | 67/68 | ok ok ok ok | 0 | 0 |
| kutz | 48/48 | 48/48 | ok ok ok ok | 0 | 0 |
| lili | 173/178 | 177/178 | ok ok ok ok | 0 | 4 |
| marduk | 140/145 | 145/145 | ok ok ok ok | 0 | 1 |
| mariposa | 171/180 | 180/180 | ok ok ok ok | 0 | 0 |
| mariposa-monarch | 182/191 | 191/191 | ok ok ok ok | 0 | 0 |
| megami | 93/101 | 101/101 | ok ok ok ok | 0 | 0 |
| menajerii | 88/94 | 94/94 | ok ok ok ok | 0 | 0 |
| michiko | 141/143 | 143/143 | ok ok ok ok | 0 | 0 |
| negativo | 115/116 | 116/116 | ok ok ok ok | 0 | 9 |
| nightwolf | 191/200 | 200/200 | ok ok ok ok | 0 | 0 |
| pantera | 282/364 | 346/364 | ok ok ok ok | 1 | 8 |
| phantom | 379/441 | 418/441 | ok ok ok ok | 5 | 5 |
| pond | 72/79 | 79/79 | ok ok ok ok | 0 | 0 |
| purplerain | 211/225 | 225/225 | ok ok ok ok | 0 | 1 |
| raiden | 13/13 | 13/13 | ok ok ok ok | 0 | 0 |
| rave | 340/342 | 341/342 | ok ok ok ok | 0 | 0 |
| realizzt | 59/59 | 59/59 | ok ok ok ok | 0 | 0 |
| retsu | 243/255 | 255/255 | ok ok ok ok | 0 | 4 |
| rin | 250/258 | 257/258 | ok ok ok ok | 1 | 0 |
| ryuji | 0/0 | 0/0 | dead dead dead dead | 0 | 0 |
| ryuji-rock | 16/16 | 16/16 | ok ok ok ok | 0 | 0 |
| ryusan | 61/65 | 62/65 | ok ok ok ok | 0 | 0 |
| sakura | 242/273 | 270/273 | ok ok ok ok | 2 | 2 |
| samura1 | 302/320 | 312/320 | ok ok ok ok | 5 | 14 |
| scimitar | 138/142 | 141/142 | ok ok ok ok | 0 | 0 |
| sf-akuma | 96/102 | 102/102 | ok ok ok ok | 0 | 1 |
| sf-blanka | 30/31 | 31/31 | ok ok ok ok | 0 | 0 |
| sf-cammy | 7/7 | 7/7 | ok ok ok ok | 0 | 0 |
| sf-chunli | 7/8 | 8/8 | ok ok ok ok | 0 | 0 |
| sf-dhalsim | 7/7 | 7/7 | ok ok ok ok | 0 | 0 |
| sf-guile | 7/7 | 7/7 | ok ok ok ok | 0 | 0 |
| sf-ken | 25/25 | 25/25 | ok ok ok ok | 0 | 0 |
| sf-mbison | 5/5 | 5/5 | ok ok ok ok | 0 | 0 |
| sf-ryu | 27/27 | 27/27 | ok ok ok ok | 0 | 0 |
| sf-sagat | 7/7 | 7/7 | ok ok ok ok | 0 | 0 |
| sf-vega | 28/28 | 28/28 | ok ok ok ok | 0 | 0 |
| sf-zangief | 27/28 | 27/28 | ok ok ok ok | 0 | 0 |
| sha | 242/273 | 270/273 | ok ok ok ok | 2 | 2 |
| skull | 242/254 | 254/254 | ok ok ok ok | 0 | 4 |
| slice | 172/178 | 178/178 | ok ok ok ok | 0 | 0 |
| star | 320/341 | 339/341 | ok ok ok ok | 1 | 1 |
| sunra | 44/44 | 44/44 | ok ok ok ok | 0 | 0 |
| t3-anna | 70/78 | 78/78 | ok ok dead ok | 0 | 0 |
| t3-bosconovitch | 86/91 | 91/91 | ok ok ok ok | 0 | 0 |
| t3-eddy | 78/90 | 90/90 | ok ok ok ok | 0 | 0 |
| t3-forestlaw | 32/44 | 44/44 | ok ok ok ok | 0 | 0 |
| t3-gon | 61/61 | 61/61 | ok dead ok ok | 0 | 0 |
| t3-hwoarang | 66/78 | 78/78 | ok ok ok ok | 0 | 0 |
| t3-julia | 62/74 | 74/74 | ok ok dead ok | 0 | 0 |
| t3-kuma | 58/70 | 70/70 | ok ok ok ok | 0 | 0 |
| t3-law | 66/78 | 78/78 | ok ok ok ok | 0 | 0 |
| t3-lei | 93/101 | 101/101 | ok ok ok ok | 0 | 0 |
| t3-nina | 63/71 | 71/71 | ok ok dead ok | 0 | 0 |
| t3-ogre | 57/65 | 65/65 | ok ok ok ok | 0 | 0 |
| t3-paul | 44/56 | 56/56 | ok ok ok ok | 0 | 0 |
| thor | 97/97 | 97/97 | ok ok ok ok | 0 | 0 |
| tobi | 70/82 | 82/82 | ok ok ok ok | 0 | 0 |
| torch | 304/335 | 329/335 | ok ok ok ok | 1 | 1 |
| tou | 218/230 | 228/230 | ok ok ok ok | 1 | 12 |
| vainabel | 45/50 | 50/50 | ok ok ok ok | 0 | 0 |
| vega | 32/32 | 32/32 | ok ok ok ok | 0 | 0 |
| vf-akira | 17/18 | 18/18 | ok dead ok dead | 0 | 0 |
| vf-elblaze | 25/25 | 25/25 | ok dead ok dead | 0 | 0 |
| vf-jeffry | 24/24 | 24/24 | ok dead ok dead | 0 | 0 |
| vf-kage | 11/12 | 12/12 | ok dead ok dead | 0 | 0 |
| vf-leifei | 20/20 | 20/20 | ok dead ok dead | 0 | 0 |
| vf-sarah | 11/12 | 12/12 | ok dead ok dead | 0 | 0 |
| vf-wolf | 19/19 | 19/19 | ok dead ok dead | 0 | 0 |
| waterfall | 144/146 | 146/146 | ok ok ok ok | 0 | 0 |
| yukihyo | 219/241 | 236/241 | ok ok ok ok | 0 | 7 |
| zangief | 27/27 | 27/27 | ok ok ok ok | 0 | 0 |
| zen | 222/235 | 234/235 | ok ok ok ok | 1 | 7 |
| zui | 245/254 | 254/254 | ok ok ok ok | 0 | 0 |
