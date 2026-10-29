# MODEL-KEY AUDIT — 2026-10-21

**Owner order (2026-10-21 ~00:11 CDT):** "Fix all characters who model key is incorrectly painted at the wrong character" ("painted" = pointed).

**Trigger:** PR #412 found DIABLO's roster `model:` pointed at `steve-fox` — his own Tripo would never have loaded as his default. This audit swept the whole roster for the same defect class, executed the game's real resolution chain in Node against main, and fixed every wrong fighter on their own line only.

## The resolution chain (verified in code)

1. **Player / character-select path** — `game/js/attires.js` `selectedAttireModel(fighter)`: `ATTIRE_VARIANTS[fighter.model] || ATTIRE_VARIANTS[fighter.id]`, first entry by default (nothing saved); fighters with no variants entry fall back to `[{ model: fighter.model }]`. Used by `game/js/select-screen.js` (previews) and `game/js/main.js` (`resolveFighterAttire` for the player).
2. **Enemy / prefetch / transform path** — the RAW roster `model:` field: `main.js` loads `enemy.model` as-is, `select-screen.js` prefetches `c.model`, and `game/js/fighter.js` sets `this.formKey = charData.model` (transform forms are keyed by model key). A stale roster field is therefore a live bug even when the attire chain rescues the player path (PHANTOM, KINPO below).
3. **Key → file** — `MODEL_URLS[key]` in `game/js/assets.js`, after the `ATTIRE_CUSTOMIZATIONS` override layer is applied (that generated registry is currently an empty map — a no-op today; the guard applies it too, so a future override is covered).

**Ground truth for "their own model":** `docs/MODEL-INVENTORY.md` (HAVE vs WIRED), `game/assets/models/MODEL-STATUS.md` (declared bases: pantera.glb = PANTERA + TOU/KAI/RETSU/GYOU souls; steve-fox.glb = ZUI + RIN/BYOU/SHA/JIN/ZEN souls + fallbacks), `roster/TRIPO-REGISTRY.md` (e.g. CYBORG X Attire 1 default = cape-jones.glb).

## Results — 58 FULL_ROSTER entries executed

| Class | Count | Meaning |
|---|---|---|
| (a) OWN | 33 | Resolves to their own wired model on both paths |
| (b) BASE-BY-DESIGN | 10 | The nine souls on their declared vessel bases + ZUI (steve-fox.glb is designated "canon = Zui") — NOT fixed |
| (c) WRONG → FIXED | 13 | Had their own wired model but the chain loaded another character's — fixed below |
| NO OWN MODEL | 2 | SLICE, RYUJI — no model of their own exists in the repo; they ride the steve-fox fallback and there is nothing correct to point at (report only) |
| (d) COLLISION | 0 unintentional | The only shared resolved files are the two declared bases. Before the fix, every non-declared sharer of steve-fox.glb / pantera.glb was a (c) fighter; after the fix, sharing is declared-only. docfrank + doc-frank-machine-shop resolve to the same file — both are Doc Frank's own entries (main + reskin-wave selectable), same character, intentional |

## The 13 fixes (game/js/roster-full.js — one word on each fighter's own line)

| Fighter | Before | After | Their own file that now loads |
|---|---|---|---|
| PHANTOM | `steve-fox` | `phantom` | roster/phantom/attires/attire1/model.glb |
| SKULL | `pantera` | `skull` | roster/skull/attires/attire1/model.glb |
| SAKU RA | `steve-fox` | `saku-ra` | roster/sakura/attires/attire1/model.glb |
| KINPO | `steve-fox` | `kinpo` | game/assets/models/kinpo.glb |
| WATERFALL | `steve-fox` | `waterfall` | roster/waterfall/attires/attire1/model.glb |
| KING TYRANT | `pantera` | `king-tyrant` | game/assets/models/king-tyrant.glb |
| BURGER | `pantera` | `burger` | roster/burger/attires/attire1/model.glb |
| AWA POP | `steve-fox` | `awa-pop` | game/assets/models/awa-pop.glb |
| PURPLE RAIN | `steve-fox` | `purple-rain` | roster/purplerain/attires/attire1/model.glb |
| NIGHTWOLF | `steve-fox` | `nightwolf` | game/assets/models/nightwolf.glb |
| CYBORG X | `steve-fox` | `cape-jones` | game/assets/models/cape-jones.glb (his Attire 1 default per TRIPO-REGISTRY) |
| N3GΔTIV0 | `pantera` | `n3g4tiv0` | game/assets/models/n3g4tiv0.glb |
| THOR | `pantera` | `thor` | roster/thor/attires/attire1/model.glb |

Failure shapes found: (i) plain stale field (SKULL, KING TYRANT, N3GΔTIV0, WATERFALL, NIGHTWOLF, AWA POP); (ii) ATTIRE_VARIANTS keyed by a name that matches neither the fighter's id nor their roster model, so the variants were unreachable and the fallback fired (SAKU RA — variants keyed `saku-ra` vs id `sakura`; PURPLE RAIN — `purple-rain` vs id `purplerain`); (iii) variants keyed by id but SHADOWED, because the roster model `pantera` hits Pantera's own ATTIRE_VARIANTS entry first (BURGER, THOR — their picker showed Pantera's attires); (iv) player path rescued by id-keyed variants but the enemy/raw path still loaded the wrong model (PHANTOM, KINPO).

**BURGER extra (inside his own entry only):** his transform `forms` map was keyed by his old base model (`'pantera': { up: … }`). `fighter.js` sets `formKey = charData.model`, so the forms key had to follow the model fix or his transform entry point would dangle. The key is renamed `'pantera'` → `'burger'` in his entry; no other fighter's forms were touched. (His form TARGETS — burger-speed-demon / burger-the-mouth / burger-demon — have no MODEL_URLS keys; that gap predates this audit and is unchanged by it.)

## Flagged, deliberately NOT fixed (not the wrong-character class)

- **KEVIN (`baek-master-white`):** player path resolves `baek` (his A2, the authored default per the ladder comment in attires.js); the raw-field (enemy) path loads `baek-master-white` — his PARKED A3 — as the body. It is his OWN model, not another character's, and his A1 Tripo wiring is in flight in other lanes; flagged for the roster lane rather than changed here.
- **DOC FRANK (`docfrank`):** resolves to his own Machine Shop model on both paths. Note: `ATTIRE_VARIANTS['doc-frank']` (7 attires) is unreachable for him (his id is `docfrank`, his model is `doc-frank-machine-shop`), so his picker shows a single attire. Own-model family, not wrong-character.
- **DEMONIO:** player default is `demonio` (base, list head) while his roster field is `demonio-a1`; both are his own models. Note: his `forms` are keyed from `demonio-a1`, so the player-side form entry point (`formKey = 'demonio'`) dangles — pre-existing, own-family, transform-lane territory.
- **ZUI:** his Tripo A1/A2 GLBs exist at `roster/zui/attires/` but have NO MODEL_URLS keys (`zui_alt1`/`zui_alt2` point at T7-Steve reskins), so there is no key to point his roster field at. He stays on steve-fox.glb, which the status docs designate as his canon model. Wiring his Tripos in is a roster-lane job.
- **RYUJI ROCK:** resolves to his own key `ryuji-rock`, but `roster/ryuji-rock/attires/attire1/model.glb` does not exist on main yet — assets.js documents it as a pending drop-in ("model.glb lands the moment the owner sends a Tripo link"). Broken target, not a wrong character; nothing correct exists to point at.
- **GYOU:** `gyou-spirit` (his Tripo spirit form) exists as a key; his declared vessel base is pantera, so he stays (b).

## Regression guard

`game/tests/model-key-guard.test.mjs` (node:test, same sandbox pattern as `customization/tools/test_game_hook.mjs`) executes the real chain — real `roster-full.js` + `attires.js` modules, `MODEL_URLS` parsed from the real `assets.js` with the real customization overrides applied — and fails when:
1. a fighter with a wired own model resolves to a non-own key on either path,
2. a declared-base rider drifts off their declared base,
3. a resolved URL (other than the documented pending ryuji-rock) has no file in the repo.

Demonstrated: **green** on the fixed tree (3/3 pass); **red** on the pre-fix tree (test 1 names all 13); **red** on a scratch reproduction of the original Diablo bug (diablo → steve-fox), naming diablo on both paths. Run it with `node --test game/tests/model-key-guard.test.mjs` from the repo root. The ownership table inside the guard mirrors this doc — update both together when a fighter's own model is wired or a declared base changes.

## Full audit table (executed against pre-fix main)

| Fighter | Roster `model:` | Player/select resolves | Enemy/raw resolves | Resolved file (player path) | Class | Fix / note |
|---|---|---|---|---|---|---|
| RIN (`rin`) | `steve-fox` | `steve-fox` | `steve-fox` | `assets/models/steve-fox.glb` | (b) BASE-BY-DESIGN | Nine Souls vessel (declared, MODEL-STATUS) |
| BYOU (`byou`) | `steve-fox` | `steve-fox` | `steve-fox` | `assets/models/steve-fox.glb` | (b) BASE-BY-DESIGN | Nine Souls vessel; BYOU canon vessel = Steve Fox |
| TOU (`tou`) | `pantera` | `pantera` | `pantera` | `assets/models/pantera.glb` | (b) BASE-BY-DESIGN | Nine Souls vessel of Pantera (declared) |
| SHA (`sha`) | `steve-fox` | `steve-fox` | `steve-fox` | `assets/models/steve-fox.glb` | (b) BASE-BY-DESIGN | Nine Souls vessel (declared) |
| KAI (`kai`) | `pantera` | `pantera` | `pantera` | `assets/models/pantera.glb` | (b) BASE-BY-DESIGN | Nine Souls vessel (declared) |
| JIN (`jin_soul`) | `steve-fox` | `steve-fox` | `steve-fox` | `assets/models/steve-fox.glb` | (b) BASE-BY-DESIGN | Nine Souls vessel (declared) |
| RETSU (`retsu`) | `pantera` | `pantera` | `pantera` | `assets/models/pantera.glb` | (b) BASE-BY-DESIGN | Nine Souls vessel (declared) |
| ZEN (`zen`) | `steve-fox` | `steve-fox` | `steve-fox` | `assets/models/steve-fox.glb` | (b) BASE-BY-DESIGN | Nine Souls vessel (declared; PR #412 left this anchor untouched on purpose) |
| GYOU (`gyou`) | `pantera` | `pantera` | `pantera` | `assets/models/pantera.glb` | (b) BASE-BY-DESIGN | Nine Souls vessel (declared); gyou-spirit is a form/attire key |
| PANTERA (`pantera`) | `pantera` | `pantera` | `pantera` | `assets/models/pantera.glb` | (a) OWN | — |
| DEMONIO (`demonio`) | `demonio-a1` | `demonio` | `demonio-a1` | `assets/models/demonio.glb` | (a) OWN | — |
| PHANTOM (`phantom`) | `steve-fox` | `phantom` | `steve-fox` | `../roster/phantom/attires/attire1/model.glb` | (c) WRONG → FIXED | model: 'steve-fox' → 'phantom' |
| DIABLO (`diablo`) | `diablo` | `diablo` | `diablo` | `../roster/diablo/attires/attire1/model.glb` | (a) OWN | — |
| SKULL (`skull`) | `pantera` | `pantera` | `pantera` | `assets/models/pantera.glb` | (c) WRONG → FIXED | model: 'pantera' → 'skull' |
| SAM-UR-A1 (`samura1`) | `sam-ur-a1` | `sam-ur-a1` | `sam-ur-a1` | `../roster/sam-ur-a1/attires/attire1/model.glb` | (a) OWN | — |
| SAKU RA (`sakura`) | `steve-fox` | `steve-fox` | `steve-fox` | `assets/models/steve-fox.glb` | (c) WRONG → FIXED | model: 'steve-fox' → 'saku-ra' |
| ZUI (`zui`) | `steve-fox` | `steve-fox` | `steve-fox` | `assets/models/steve-fox.glb` | (b) BASE-BY-DESIGN | MODEL-STATUS/inventory: steve-fox.glb canon = Zui (declared). His Tripo A1/A2 GLBs sit in roster/zui/attires/ but have NO MODEL_URLS keys (zui_alt1/zui_alt2 are T7-Steve reskins) - not pointable today. |
| KINPO (`kinpo`) | `steve-fox` | `kinpo` | `steve-fox` | `assets/models/kinpo.glb` | (c) WRONG → FIXED | model: 'steve-fox' → 'kinpo' |
| WATERFALL (`waterfall`) | `steve-fox` | `steve-fox` | `steve-fox` | `assets/models/steve-fox.glb` | (c) WRONG → FIXED | model: 'steve-fox' → 'waterfall' |
| KING TYRANT (`kingtyrant`) | `pantera` | `pantera` | `pantera` | `assets/models/pantera.glb` | (c) WRONG → FIXED | model: 'pantera' → 'king-tyrant' |
| BURGER (`burger`) | `pantera` | `pantera` | `pantera` | `assets/models/pantera.glb` | (c) WRONG → FIXED | model: 'pantera' → 'burger' |
| AWA POP (`awapop`) | `steve-fox` | `steve-fox` | `steve-fox` | `assets/models/steve-fox.glb` | (c) WRONG → FIXED | model: 'steve-fox' → 'awa-pop' |
| SCIMITAR (`scimitar`) | `scimitar` | `scimitar` | `scimitar` | `assets/models/scimitar.glb` | (a) OWN | — |
| PURPLE RAIN (`purplerain`) | `steve-fox` | `steve-fox` | `steve-fox` | `assets/models/steve-fox.glb` | (c) WRONG → FIXED | model: 'steve-fox' → 'purple-rain' |
| NIGHTWOLF (`nightwolf`) | `steve-fox` | `steve-fox` | `steve-fox` | `assets/models/steve-fox.glb` | (c) WRONG → FIXED | model: 'steve-fox' → 'nightwolf' |
| DIO (`dio`) | `dio` | `dio` | `dio` | `assets/models/dio.glb` | (a) OWN | — |
| CYBORG X (`cyborgx`) | `steve-fox` | `steve-fox` | `steve-fox` | `assets/models/steve-fox.glb` | (c) WRONG → FIXED | model: 'steve-fox' → 'cape-jones' |
| MICHIKO (`michiko`) | `michiko` | `michiko` | `michiko` | `assets/models/michiko.glb` | (a) OWN | — |
| STAR (`star`) | `star` | `star` | `star` | `assets/models/star.glb` | (a) OWN | — |
| TORCH (`torch`) | `torch` | `torch` | `torch` | `assets/models/torch.glb` | (a) OWN | — |
| BRUNO (`bruno`) | `bruno` | `bruno` | `bruno` | `assets/models/bruno.glb` | (a) OWN | — |
| N3GΔTIV0 (`negativo`) | `pantera` | `pantera` | `pantera` | `assets/models/pantera.glb` | (c) WRONG → FIXED | model: 'pantera' → 'n3g4tiv0' |
| THOR (`thor`) | `pantera` | `pantera` | `pantera` | `assets/models/pantera.glb` | (c) WRONG → FIXED | model: 'pantera' → 'thor' |
| YUKIHYŌ (`yukihyo`) | `yukihyo` | `yukihyo` | `yukihyo` | `assets/models/yukihyo.glb` | (a) OWN | — |
| SLICE (`slice`) | `steve-fox` | `steve-fox` | `steve-fox` | `assets/models/steve-fox.glb` | NO OWN MODEL — fallback rider (report only) | NO own model in repo (MODEL-STATUS: SLICE no source; dedicated Dragunov lane pending). Rides steve-fox fallback - nothing to point at. |
| DOC FRANK (`docfrank`) | `doc-frank-machine-shop` | `doc-frank-machine-shop` | `doc-frank-machine-shop` | `../roster/doc-frank/attires/machine-shop/doc-frank-machine-shop-rigged.glb` | (a) OWN | — |
| DEMONIO (`demonio-bloodline-ember`) | `demonio-bloodline-ember` | `demonio-bloodline-ember` | `demonio-bloodline-ember` | `../roster/demonio/attires/bloodline-ember/demonio-bloodline-ember.glb` | (a) OWN | — |
| DEMONIO (`demonio-winged`) | `demonio-winged` | `demonio-winged` | `demonio-winged` | `../roster/demonio/attires/winged-devil/model.glb` | (a) OWN | — |
| DEMONIO (`demonio-human`) | `demonio-human` | `demonio-human` | `demonio-human` | `../roster/demonio/attires/human/model.glb` | (a) OWN | — |
| DOC FRANK (`doc-frank-wowomomo`) | `doc-frank-wowomomo` | `doc-frank-wowomomo` | `doc-frank-wowomomo` | `../roster/doc-frank/attires/attire2/base/model.glb` | (a) OWN | — |
| DOC FRANK (`doc-frank-hood`) | `doc-frank-hood` | `doc-frank-hood` | `doc-frank-hood` | `../roster/doc-frank/attires/attire3/base/model.glb` | (a) OWN | — |
| DOC FRANK (`doc-frank-frankenstein`) | `doc-frank-frankenstein` | `doc-frank-frankenstein` | `doc-frank-frankenstein` | `../roster/doc-frank/attires/attire4/base/model.glb` | (a) OWN | — |
| DOC FRANK (`doc-frank-machine-shop`) | `doc-frank-machine-shop` | `doc-frank-machine-shop` | `doc-frank-machine-shop` | `../roster/doc-frank/attires/machine-shop/doc-frank-machine-shop-rigged.glb` | (a) OWN | — |
| KEVIN (`baek-master-white`) | `baek-master-white` | `baek` | `baek-master-white` | `assets/models/baek.glb` | (a) OWN | KEVIN ladder (attires.js owner comment): default = baek (A2); baek-master-white = A3 PARKED. Player path resolves baek; raw-field (enemy) path loads the PARKED attire - own model, not wrong-character; flagged, not fixed. |
| MARIPOSA (`mariposa-monarch`) | `mariposa-monarch` | `mariposa-monarch` | `mariposa-monarch` | `../roster/mariposa/attires/monarch/mariposa-monarch-rigged.glb` | (a) OWN | — |
| DXMMII (`dxmmii-patchwork`) | `dxmmii-patchwork` | `dxmmii-patchwork` | `dxmmii-patchwork` | `../roster/dxmmii/attires/patchwork-dj/dxmmii-patchwork-rigged.glb` | (a) OWN | — |
| ZANGIEF (`zangief`) | `zangief` | `zangief` | `zangief` | `../roster/zangief/attires/attire1/model.glb` | (a) OWN | — |
| CHARGER (`charger`) | `charger` | `charger` | `charger` | `../roster/charger/attires/attire1/model.glb` | (a) OWN | — |
| CHARGER (`charger-attire2`) | `charger-attire2` | `charger-attire2` | `charger-attire2` | `../roster/charger/attires/attire2/model.glb` | (a) OWN | — |
| VEGA (`vega`) | `vega` | `vega` | `vega` | `../roster/vega/attires/attire1/model.glb` | (a) OWN | — |
| IORI (`iori`) | `iori` | `iori` | `iori` | `../roster/iori/attires/attire1/model.glb` | (a) OWN | — |
| ARMOR KING (`armor-king`) | `armor-king` | `armor-king` | `armor-king` | `../roster/armor-king/attires/attire1/model.glb` | (a) OWN | — |
| KRONOS (`kronos`) | `kronos` | `kronos` | `kronos` | `../roster/kronos/attires/attire1/model.glb` | (a) OWN | — |
| KRONOS (`kronos-attire2`) | `kronos-attire2` | `kronos-attire2` | `kronos-attire2` | `../roster/kronos/attires/attire2/model.glb` | (a) OWN | — |
| DEATHFANG (`deathfang`) | `deathfang` | `deathfang` | `deathfang` | `../roster/deathfang/attires/attire1/model.glb` | (a) OWN | — |
| RYUJI (`ryuji`) | `steve-fox` | `steve-fox` | `steve-fox` | `assets/models/steve-fox.glb` | NO OWN MODEL — fallback rider (report only) | NO own model in repo (no Yamazaki model anywhere, per assets.js comment). Rides steve-fox fallback. |
| RYUJI ROCK (`ryuji-rock`) | `ryuji-rock` | `ryuji-rock` | `ryuji-rock` | `../roster/ryuji-rock/attires/attire1/model.glb` | (a) OWN | MODEL_URLS wired but assets.js comment says model.glb PENDING drop-in - check existence. |
| KORESHI (`koreshi`) | `koreshi` | `koreshi` | `koreshi` | `../roster/koreshi/attires/attire1/model.glb` | (a) OWN | — |

## Follow-up (2026-10-21) — ZUI Tripos wired

The ZUI note in this audit ("Wiring his Tripos in is a roster-lane job") is done. Zui's Tripo A1 (Drunken Monk) and A2 (Rework v2) GLBs now have MODEL_URLS keys (`zui-attire1`, `zui-attire2`), an `ATTIRE_VARIANTS['zui']` ladder with the Tripo A1 as default, and his roster `model:` field points at `zui-attire1` — so BOTH resolution paths load his own Tripo (reclassify ZUI: (b) → (a) OWN). The guard's OWNERSHIP table was updated in step (zui: own = [zui-attire1, zui-attire2], base = steve-fox retained as his declared canon base). steve-fox.glb stays wired and selectable as Zui's base alternate; the five souls' declared base is untouched. Proof: node resolution on the wired tree (player key `zui-attire1`, enemy key `zui-attire1`) + `node --test game/tests/model-key-guard.test.mjs` 3/3 pass; roster-wide resolved-path diff vs the pre-fix tree = exactly one added path (`roster/zui/attires/attire1/model.glb`). A1 render: `docs/tpose-refs/zui/a1_front.png`.


---

## Addendum 2026-10-21 — SLICE resolved

The audit listed SLICE as one of two fighters with no model in the repo (he rode the `steve-fox` fallback on both paths). Resolved the same day, per the owner's order to build Slice from the Tekken teardown files:

| Fighter | Player/select path | Enemy/raw path | Resolved key | Resolved URL | Class |
|---|---|---|---|---|---|
| SLICE (`slice`) | `slice` (no ATTIRE_VARIANTS entry -> roster `model:` fallback) | `slice` | `slice` | `../roster/slice/attires/attire1/model.glb` | (a) OWN |

Source: Tekken 7 Dragunov teardown model — `dragunov-t7-rig.blend` from release `tekken-models-batch-2` (sha256 `214dc98fcc364245cd75dc52b3538d463c21ed28e45b907c78803feb714e5efd`), the T7 default costume (beret configuration), converted to GLB on the T7 game skeleton (198 joints). `roster-full.js` `model:` changed `steve-fox` -> `slice`; `MODEL_URLS` gained `slice` + `slice-attire1`; the guard's OWNERSHIP table now lists `slice: own [slice, slice-attire1]`. Canon gap (not a defect): Slice's skull mask is a Tekken 7 customization part that is **not present in our teardown holdings** — see `roster/slice/ATTIRE-SLOTS.md`.

## Follow-up (2026-10-21) — SLICE Attire 1 is now the owner's Tripo; Dragunov build laddered to Attire 2

The owner dropped his own Tripo for Slice (2026-10-21 ~08:42 CDT) and named it his **main default Attire 1**: "undead warrior 3d model" by tzflo312 (cf9cf660-1673-4585-ac1b-ce4fc92f1550), pulled via `tools/tripo-pull` and archived on release `slice-tripo-pulls-20261021` (18,884,292 B, sha256 `6cddd2c9697aead7abb4a7c61dd36e9f003bafad14fd9fd6d0e49ff851074337`, digest-verified; glTF 2.0 meshopt, 1 mesh / 1 material / 3 textures, **static — no skin**; rig at the rig stage, see `roster/slice/RIG-NOTES.md`). Canon per the owner: jagged chrome arm blades (Baraka/Wolverine prototype mix), skull mask blending into the back of the head, scars all over, blades on the belt buckle and the side of the shoe.

The PR #433 Dragunov build **laddered back to Attire 2 byte-identical** (sha256 `af51f6473e7764ac6f832d19a3e6a38ef89f924e3a1511f43c3b7531a01d94b0` verified before and after the move; its T-pose refs moved to `docs/tpose-refs/slice/a2_front.png` / `a2_back.png`). It stays wired and selectable — the owner: "you can keep making your version of slice."

| Fighter | Player/select path | Enemy/raw path | Resolved key | Resolved URL | Class |
|---|---|---|---|---|---|
| SLICE (`slice`) | `slice` → `slice-attire1` (ATTIRE_VARIANTS default) | `slice` | `slice` / `slice-attire1` | `../roster/slice/attires/attire1/model.glb` | (a) OWN |
| SLICE Attire 2 (`slice-attire2`) | `slice-attire2` (ATTIRE_VARIANTS) | `slice-attire2` | `slice-attire2` | `../roster/slice/attires/attire2/model.glb` | (a) OWN |

`MODEL_URLS` gained `slice-attire2`; `slice` + `slice-attire1` still point at `attire1/model.glb` (now the Tripo file); `ATTIRE_VARIANTS['slice']` added (A1 Tripo default, A2 Dragunov build); the guard's OWNERSHIP table now lists `slice: own [slice, slice-attire1, slice-attire2]`. Proof: `node --test game/tests/model-key-guard.test.mjs` — resolution tests pass (Slice → his Tripo on both paths, Dragunov build on its own slot); renders `docs/tpose-refs/slice/a1_front.png` + `a1_back.png` own-eyes verified against the owner's description. The skull-mask note in the earlier SLICE addendum is superseded for his default look: the owner's Tripo models the mask on. The T7 generic customization skull-mask part remains a Creation Suite piece goal (see `roster/slice/ATTIRE-SLOTS.md`).

---

## Addendum 2026-10-21 — ZEN resolved

The audit's table recorded ZEN riding the `steve-fox` fallback (guard OWNERSHIP: `zen: base steve-fox`). Resolved the same day with the owner's own models — Zen is unvesseled (canon ruling 2026-10-21), so his main model is his own SPIRIT BODY (owner Tripo), and his legacy body ladders back unmodified:

| Fighter | Player/select path | Enemy/raw path | Resolved key | Resolved URL | Class |
|---|---|---|---|---|---|
| ZEN (`zen`) | `zen` (ATTIRE_VARIANTS['zen'] first entry `zen-attire1`) | `zen` | `zen` / `zen-attire1` | `../roster/zen/attires/attire1/model.glb` | (a) OWN |

Sources: spirit body = owner Tripo 8c46e379-a51c-4741-b4a3-2132ca89078f (raw meshopt 19,574,656 B, sha256 `9eee938f05857b63dbefc6fc6d793ad1c1c449865e926dd979f122e0ea537b74`, archived in release `zen-tripo-pulls-20261021`; wired copy decompressed, 57,367,520 B). `roster-full.js` `model:` changed `steve-fox` -> `zen`; `MODEL_URLS` gained `zen` + `zen-attire1`; `ATTIRE_VARIANTS['zen']` created (Attire 1 Spirit Body default, Attire 2 legacy `zen-body`); the guard's OWNERSHIP table now lists `zen: own [zen, zen-attire1]`. The legacy `game/assets/models/zen-body.glb` file was not moved or modified. Zen's animation bank (`zen → julia`) is untouched.

Also wired, outside the attire system: ZEN'S SPIRIT FORM — Zen himself as a spirit (his stand form), owner Tripo 803f4cf1-35a5-4126-8971-a3a89aee114b (raw 17,279,708 B, sha256 `4814781faa239ad604b5c54543209970b9eed143c30f1ff9c46bc2d1c5d55cfe`, same release), at `roster/zen/spirit/model.glb` under MODEL_URLS key `zen-spirit`. It is a separate model entity tied to Zen's fighter record — not an attire, not a roster fighter — and does not affect the resolution rows above. Behavior spec: `roster/zen/RIG-NOTES.md`.

## ADDENDUM (2026-10-21, CornerStone build) — RYUJI ROCK pending drop-in RESOLVED

The documented pending drop-in flagged in this audit ("RYUJI ROCK: resolves to his own key `ryuji-rock`, but `roster/ryuji-rock/attires/attire1/model.glb` does not exist on main yet") landed on 2026-10-21: the owner delivered his Tripo (https://studio.tripo3d.ai/3d-model/20c1fd2e-40d0-4500-9be6-50f6494ab5e1, "tattooed man 3d model", 18,872,720 B, sha256 `658848674696b6c4e47c55f773d2c55e07359595e51e57ce273704dc4871049d`), pulled via `tools/tripo-pull`, archived on release `cornerstone-tripo-pulls-20261021`, and dropped at `roster/ryuji-rock/attires/attire1/model.glb`. The fighter's canon name is now **CORNERSTONE** (owner 2026-10-21; internal id stays `ryuji-rock`, display name updated in roster-full.js). The guard's OWNERSHIP entry for `ryuji-rock` no longer carries `pending: true`, so test 3 (file-exists) now covers him. The separate `ryuji` entry remains a NO OWN MODEL fallback rider — unchanged by this build.

UPDATE (2026-10-24, rebase of this PR): the `ryuji` entry is no longer a rider. Restoring the `ryuji-rock` roster entry made `ryuji`'s `model: 'ryuji-rock'` a wrong-body violation under the no-wrong-body gate (owner order 2026-10-23, issue #866: no fighter may load another fighter's model key), so `ryuji` is now `model: null, modelPending: true` — the gate's prescribed state for a fighter with no own model yet; he keeps his full KOF moveset (`ryuji-rock` moveset key) and stays in the repo. The "fallback rider" sentence above is superseded by this update.
