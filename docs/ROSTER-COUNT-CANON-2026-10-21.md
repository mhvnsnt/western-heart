Counts derived from the repo + releases on 2026-10-21, method stated per count, supersedes all chat/spec figures — including the "36-fighter" figure in pasted AI specs (a hallucination) and every count quoted in chat summaries.

# ROSTER COUNT CANON — 2026-10-21

**Census point:** `main` @ `eeb59a8860176add39dcbdb12ec44e2e31689680` (merge of PR #460, 2026-10-21 19:19 CDT). Anything merged after that SHA (e.g. the Vain Abel Attire 4 lane ordered 2026-10-21 ~19:52 CDT) is NOT in these numbers and moves them when it lands.

**Post-census merges already on main when this doc was filed** (main had advanced past the census SHA and kept moving during filing): PR #473 (moveset gaps), PR #477 (ryuji/slice fix), PRs #476/#478/#480 (rig batches adding `model-rigged.glb` builds across the roster). Those merges move specific findings below — §1's moveset-file gaps and the Ryuji Rock model absence, and §3's rig-state notes (e.g. Sam-ur-a1's rig). The numbers in this doc describe `eeb59a88` exactly; re-deriving the moved counts is the next census trigger, not a silent edit of this one.

**Method, globally:** every count below was re-derived this session from primary sources — the git trees of `roster/`, `game/`, `docs/` on main (GitHub git-trees API, untruncated per-subtree), the raw text of `game/js/roster-full.js`, `game/js/movesets.js`, `game/js/attires.js`, `game/js/assets.js`, the executed audits committed on main (`docs/MODEL-KEY-AUDIT-2026-10-21.md`, `docs/FIGHTER-COMPLETENESS-AUDIT-2026-10-21.md`), `roster/TRIPO-REGISTRY.md`, `game/data/tripo-fighters.json`, the owner's attire-provenance marking sheet of 2026-10-20 (101 rows, parsed and re-tallied by script), and the GitHub release list for this repo. Chat summaries — including the brief that commissioned this census — were used only as reconciliation targets, never as sources.

---

## 1. Roster entries

**Headline: 59 roster entries in `FULL_ROSTER` (`game/js/roster-full.js`), covering 50 distinct fighters.**

| Cut | Count | Method |
|---|---|---|
| `FULL_ROSTER` entries | **59** | Counted `{ id: ... }` objects in `game/js/roster-full.js` on main; 59 unique ids. |
| Distinct fighters | **50** | 59 entries grouped by display `name`: 50 unique names. The 9 extra entries are attire/form entries of the same fighter: DEMONIO ×4 entries (base, Bloodline Ember, Winged, Human), DOC FRANK ×5 (base + Wowomomo, Hood, Frankenstein, Machine Shop), CHARGER ×2, KRONOS ×2. |
| `roster/` directories | **46** | Top-level dirs in the `roster/` tree (+ 2 loose files: `ROSTER-GAPS-2026-10-19.md`, `TRIPO-REGISTRY.md`). NOT the roster count: some fighters have no dir (the souled entries ride shared bases), some dirs are file homes for one fighter under two names (`purplerain`/`purple-rain`, `sakura`/`saku-ra`), and some are staged/unassigned (`vainabel`, `cain-elias`, `lili`, `blanka` — files retained, no `FULL_ROSTER` entry). |
| Entries resolving to an existing GLB on main | **58 / 59** | The model-key audit's executed resolution chain (both player and enemy paths) + existence check of every resolved path against the `roster/` and `game/` trees. The one miss is below. |
| Entries with a per-id moveset file | **58 / 59** | `game/assets/movesets/<id>.json` presence for each `FULL_ROSTER` id. The one miss is below. |
| Entries with BOTH (existing GLB + moveset file) | **57** | Intersection of the two rows above. |
| Model-file only | **1** | `doc-frank-frankenstein` — model exists, **no moveset file at all** (also absent from `MOVESET_IDS` and from `game/assets/movesets/index.json`). |
| Moveset-file only | **1** | `ryuji-rock` (CORNERSTONE) — moveset file exists (`ryuji-rock.json`), but his wired model path `roster/ryuji-rock/attires/attire1/model.glb` does **not** exist on main; the dir holds only a README. Model pending (owner Tripo, per the comment in `game/js/assets.js`). |
| Neither | **0** | — |

**Model-ownership cut** (the PR #418 taxonomy, brought current):

| Class | Count | Notes |
|---|---|---|
| OWN model shipped | **49** | The entry's resolved model is that fighter's own wired model and the file exists on main. |
| BASE-BY-DESIGN | **8** | The eight souled entries still riding their declared vessel bases (`steve-fox` / `pantera` files): RIN, BYOU, TOU, SHA, KAI, JIN, RETSU, GYOU. |
| No own model — fallback rider | **1** | `ryuji` — no Yamazaki model exists anywhere in the repo; rides the `steve-fox` fallback (report-only in #418; still true). |
| Own key wired, file absent | **1** | `ryuji-rock` — see above. |

**Moveset-loader cut:** of the 58 per-id moveset files for roster entries, **55** ids are listed in `MOVESET_IDS` (`game/js/movesets.js`). Three files exist but their ids are NOT in the loader list: `doc-frank-wowomomo`, `doc-frank-hood`, `ryuji` (the completeness audit's PR #444 fixed this for `demonio-human`, `kronos-attire2`, `charger-attire2` — verified in the current file; it did not cover these three). Repo-wide moveset data: **100** JSON files in `game/assets/movesets/` (98 fighter/form files + `index.json` + `t3_input_tables.json`); `index.json` carries **96** fighter entries; `MOVESET_IDS` lists **83** ids, of which **28** are staged sets not in `FULL_ROSTER` (federation, intake, forms — §4). Found inconsistency: `charger-attire2` is in `MOVESET_IDS` but missing from `index.json`'s fighter table, which the lazy loader consults first — flagged, not fixed (not this census's job).

### Reconciliation vs PR #418 (58 entries: OWN 33 / BASE-BY-DESIGN 10 / WRONG→FIXED 13 / no-model 2)

The audit's numbers were an executed **pre-fix** snapshot of a roster that has since changed; they are not wrong for their moment, but they no longer describe main:

- **58 → 59 entries:** RAVE was added to `FULL_ROSTER` after the audit executed (his entry, with the Kiko Tanaka Tripo models, is on current main; the audit table has no Rave row). The sibling-session recount of "59 entries, 50 distinct fighters" — previously unadopted — is **independently confirmed** by this census (same two numbers, derived from the file, not from the session).
- **WRONG→FIXED 13 → 0 as a live class:** all 13 (Phantom, Skull, Saku Ra, Kinpo, Waterfall, King Tyrant, Burger, Awa Pop, Purple Rain, Nightwolf, Cyborg X, Negativo, Thor) now carry their own model in the current `roster-full.js` — verified field-by-field this session.
- **No-model 2 → 1:** SLICE was resolved the same day (the audit's own addendum): his model is a Tekken 7 Dragunov teardown conversion at `roster/slice/attires/attire1/model.glb`, wired. Only `ryuji` remains a fallback rider.
- **BASE-BY-DESIGN 10 → 8:** ZEN and ZUI left the class via the audit's own follow-ups (Zen's own spirit-body Tripo, PR #460; Zui's Tripo A1 wired as `zui-attire1`). The remaining 8 are the souled entries above.
- **The often-quoted "57 fighters have movesets"** matches no current cut: the derivable numbers are 58 files / 55 loader-listed / 57 with both model+moveset. Use those, with their definitions.

---

## 2. Attires by provenance

**Universe:** attire rows for `FULL_ROSTER` fighters (+ Kevin), one row per distinct attire/form model slot, as established by the owner's 2026-10-20 provenance marking sheet. That sheet was re-parsed and re-tallied by script this session (its stated totals reproduce exactly: 101 rows — Tripo-original 53 / Tripo reskin-of-source 4 / source-game models 13 / source retextures 12 / community rips 10 / unclassified 9; wired 79 / not wired 19 / broken 3). The table below is that census **brought current to the census SHA** with only evidence-backed deltas (each delta names its evidence).

**Current totals: 108 attire rows — Tripo-original 60 · Tripo reskin-of-source 4 · source-game models 13 · source retextures 12 · community rips 10 · unclassified 9. Wire status: wired 94 · not wired 13 · broken 1.**

Deltas applied to the Oct 20 sheet (Oct 20 → census SHA):

| Delta | Effect | Evidence |
|---|---|---|
| PANTERA A2 Leo man: broken → wired | broken −1, wired +1 | File restored (`roster/pantera/attires/leomon/model.glb` exists); PR #448 slot order. |
| PANTERA A4 Leopard King: not wired → wired | not −1, wired +1 | `pantera-leopard-king` key → `roster/pantera/attires/leopard-king/model-rigged.glb` in `game/js/assets.js`; PR #448. |
| DEATHFANG A2 Werewolf: broken → wired | broken −1, wired +1 | `deathfang-werewolf` key → `roster/deathfang/attires/attire2/model.glb`; PR #443. |
| CHARGER A1 + A2: not wired → wired | not −2, wired +2 | `charger` / `charger-attire2` keys in `assets.js` (lines 232–233) → files exist in `roster/charger/attires/`; PR #392. |
| ZUI Tripo (sheet row "A2 · Drunken Monk"): not wired → wired | not −1, wired +1 | `zui-attire1` → `roster/zui/attires/attire1/model-rigged.glb`, `zui-attire2` → `attire2/model.glb`; model-key audit follow-up. |
| AWA POP A3 (attires/attire2, Tripo d71f4210): not wired → wired | not −1, wired +1 | `awa-pop-attire2` key; PR #444 variant listing. (Her A2-row Tripo file `awa-pop-attire-1.glb` remains unwired — the wired `awa-pop` key still points at the unclassified `game/assets/models/awa-pop.glb`.) |
| KRONOS A3 TimberWolf Suited: not wired → wired | not −1, wired +1 | File is on main (`roster/kronos/attires/attire3/model.glb`); `kronos-attire3` key;PR #444 variant listing. The Oct 20 sheet had it "not on main (PR #378 open)" — that is no longer true. |
| DIABLO A2 "Devil God": NEW ROW | rows +1, Tripo-original +1, wired +1 | Tripo 9b096022 (`roster/diablo/ATTIRE-SLOTS.md`, `roster/TRIPO-REGISTRY.md`); `diablo-attire2` key; PR #419. The Oct 20 sheet predates it — and it corrects the sheet's DIABLO A1 "unknown" row's implication: Diablo A1 is likewise a Tripo original (aee46f6a) per the registry, though its sheet class is left as-is here because the A1 game file's provenance audit is the registry's word alone. |
| ZEN A1: source-game model → Tripo-original | source-model −1, Tripo-original +1 | His own spirit-body Tripo (8c46e379) is Attire 1 on main; the steve-fox base row is retired. PR #460. |
| ZEN forms: +3 NEW ROWS (spirit entity, tentacle mode, oversoul) | rows +3, Tripo-original +3, wired +3 | Tripos 803f4cf1 / 9460095d / 2bbc8e88 at `roster/zen/spirit|tentacle|oversoul/model.glb`; `zen-spirit` / `zen-tentacle` / `zen-oversoul` keys; wired as in-attire transformation modes. PR #460. |
| RAVE: +3 NEW ROWS (A1 Hooded Tripo, A2 Ghost Tanaka Tripo, A3 Muta = Lei base) | rows +3, Tripo-original +2, source-model +1, wired +3 | Rave entered `FULL_ROSTER` after the sheet (the sheet carried these only in its back-catalog table). `ATTIRE_VARIANTS['kiko-tanaka']` in `game/js/attires.js`; `roster/TRIPO-REGISTRY.md` RAVE row. |
| SLICE A1: class unchanged (source-game model), basis changed | no count change | Was the shared steve-fox base on Oct 20; now his own dedicated T7 Dragunov teardown conversion (see §1, §4). |

**Still broken (1):** RYUJI ROCK A1 — wired key, model file absent (see §1).
**Still not wired (13):** Pantera A3/A5/A6 (exempt reskins), King Tyrant A1–A4 Tripos (picker has no variant list — completeness audit), Awa Pop A2 Tripo file, Nightwolf A2 Tripo, Star A1/A2/A3 (her Tripo statics are deliberately unwired; the shipped default is the A4 "Classic" community rip), Kevin A1 Tripo (file present at `roster/baek/attires/attire1/model.glb`, no game key — rig/wiring in flight). Kevin A3 Master White remains PARKED by owner verdict and is counted in the retexture class, as in the sheet.

**Not in this universe (by the sheet's own definition):** staged fighters' attires (Vain Abel A2/A3, Cain Elias A1/A2, Silvertongue) — counted in §3, not here. Extra unladdered file flagged: `roster/deathfang/attires/attire3/model.glb` exists on main but appears in no `ATTIRE_VARIANTS` ladder — uncounted.

**Known sheet misses (flagged, not folded into the arithmetic above):** the registry records Tripo pulls the Oct 20 sheet never rowed — Kinpo's two pulls (`roster/kinpo/attires/attire1|attire2/model.glb`; the sheet's two Kinpo rows describe the legacy `game/assets/models/kinpo*.glb` files instead) and Zui's rework-v2 pull (`roster/zui/attires/attire2/model.glb`) — and it misclasses Diablo A1 (the wired A1 is his Tripo aee46f6a at `roster/diablo/attires/attire1/model.glb` per the model-key audit's executed resolution, not the unclassified `game/assets/models/diablo.glb` the sheet row points at). §3's pull-level count is enumerated independently of the sheet and includes all of these; a future provenance-sheet pass should row them in §2's universe.

---

## 3. Tripo models — distinct count

**Headline: 66 distinct Tripo models** are identified across the registry, the marking sheet, the release archives, and the roster attires — deduplicated at pull level (byte-identical copies of one pull, e.g. Mariposa's A1/slot2 and Thor's two identical files, count once; Star's A2/A3 are colorways of her single pull and count once). **42** of the 66 carry a full Tripo UUID in the records (`roster/TRIPO-REGISTRY.md` + slot docs); the rest are identified by short-prefix, account-pull, or owner-provided-file evidence in the same records. Vain Abel's Attire 4 pull (owner link, 2026-10-21 ~19:52 CDT) is NOT counted — it was not on main at the census SHA.

Per-fighter distinct pulls: Pantera 2 (Leo man — owner-provided via Drive, no UUID; Leopard King 094c2f37) · Zui 2 · Zen 4 (8c46e379, 803f4cf1, 9460095d, 2bbc8e88) · Thor 2 · Awa Pop 2 · Waterfall 1 · Saku Ra 1 · Purple Rain 1 · Rave 2 · Cape Jones/Cyborg X 1 · Skull 1 · Mariposa 1 · Kevin 1 · King Tyrant 4 · Star 1 · Silvertongue 1 · DXMMII 2 (ca068026 + Blockhead) · Phantom 1 · Nightwolf 1 · Sam-ur-a1 1 · Doc Frank 7 (four attires' transformed/base Tripo forms; his A1 base is the Bosconovitch source model, not a Tripo) · Cain Elias 2 · Vain Abel 2 · Burger 7 · Gyou 1 (spirit form) · Kronos 3 · Diablo 2 · Koreshi 1 · Kinpo 2 · Demonio 3 · Charger 2 · Deathfang 2. Named exclusion: Star's in-flight Attire 5 models (`roster/star/attires/attire5/` — a separate rated-M lane, per `roster/star/attires/_VARIANT-PIPELINE.md`) carry no pull identity in the registry records and are NOT in the 66.

**Status split (pull level):**

| Bucket | Count | Contents |
|---|---|---|
| Wired into the playable roster | **53** | The pull (or its rigged derivative) is what a `FULL_ROSTER` entry resolves to, or is reachable via its attire ladder / transformation forms. Derived from the per-fighter enumeration above, not from §2's rows — the two counts differ because the registry records wired pulls the Oct 20 sheet never rowed (Kinpo ×2, Zui's rework v2) or misrowed (Diablo A1), and because three sheet rows are duplicate files of one pull (Mariposa slot 2, Saku Ra MAIN, Purple Rain MAIN). |
| Staged — wired in suite/movesets, fighter not in `FULL_ROSTER` | **5** | Vain Abel 2 (`ATTIRE_VARIANTS['vainabel']` + moveset listed), Cain Elias 2 (`ATTIRE_VARIANTS['cain-elias']` + moveset listed), Silvertongue 1 (registry only). |
| Pulled, in repo/releases, not wired | **8** | King Tyrant ×4 (no picker ladder), Kevin A1 (rig in flight), Star's pull (statics deliberately unwired), Nightwolf A2, Awa Pop's e3d3b06f file. |

Note on rig state: pulls land as unrigged statics; the wired bucket carries rigged builds from the auto-rig waves (e.g. `model-rigged.glb` derivatives for Zui, Leopard King, Mariposa Monarch, Master White class). The one wired model the audits flag as still unrigged is SAM-UR-A1 (single-node static; rigging owned by the pose lane). A per-file skin recount was not performed for this census — rig claims above rest on `docs/FIGHTER-COMPLETENESS-AUDIT-2026-10-21.md` and `game/assets/models/MODEL-STATUS.md`.

**Release archives holding Tripo pulls** (GitHub releases on this repo, asset counts from the API): `tripo-wire-20261019` (12) · `tripo-landing-20261019` (4) · `tripo-recovery-originals-20261021` (13) · `zen-tripo-pulls-20261021` (4) · `kinpo-tripo-pulls-20261020` (4) · `diablo-tripo-pulls-20261020` (4) · `charger-tripo-pulls-20261020` (4) · `vain-abel-tripo-pulls-20261020` (4) · `deathfang-tripo-pulls-20261020` (3) · `cornerstone-tripo-pulls-20261021` (1) · `slice-tripo-pulls-20261021` (2) · `leoman-restore-20261020` (2) · `pose-rigged-masters-20261020` (2) · `pantera-leopard-king-rigged-20261020` (1). Release assets are split archives/parts, not model counts — the 66 above is a model-level count from the registry/slot records, not an asset sum. The local `~/workspace/tripo-recovery/` folder named in older records was not present on this machine at census time (its contents are mirrored in `tripo-recovery-originals-20261021`); no count here depends on it.

---

## 4. Teardown-conversion characters

**Documented: 4 named conversions + staged conversion sets below.** A conversion is counted only where a canon/roster record in the repo documents it. Docs searched: `roster/*/ATTIRE-SLOTS.md`, `roster/*/CANON.md`, `roster/TRIPO-REGISTRY.md`, `roster/ROSTER-GAPS-2026-10-19.md`, `docs/MODEL-KEY-AUDIT-2026-10-21.md`, `docs/FIGHTER-COMPLETENESS-AUDIT-2026-10-21.md`, `docs/TEARDOWN-INTEGRATION-AUDIT-2026-10-19.md`, and the header/attire comments in `game/js/roster-full.js` and `game/js/movesets.js`. Anything not in those records is not invented here.

**Named conversions (documented per fighter):**

| Fighter | Conversion | Status on main |
|---|---|---|
| SLICE | Built from Tekken 7 Dragunov teardown assets only (owner canon in `roster-full.js` + `roster/slice/ATTIRE-SLOTS.md`; source blend sha recorded in the model-key audit addendum). Skull-mask part is a named gap (not in teardown holdings). | Done — own model wired. |
| CHARGER | Proprietary Blanka replacement: Blanka's converted 199-move set (ice/electric signature renames), owner Tripo models. Blanka's own files stay in the repo. | Done — both attires wired. |
| DEATHFANG | Iori Yagami base converted: keeps Iori's stance, moves, animations in both forms; models are owner Tripo. | Done — A1/A2 wired. |
| CORNERSTONE (`ryuji-rock`) | Ryuji Yamazaki base + The Rock: Rock animations sourced from the No Mercy / WMXIX teardowns (canon comments in `roster-full.js` / `movesets.js`). | Moveset on main (24-move interim file); model file absent — see §1. |

**Staged conversion sets** (movesets converted from teardown games into Tekken notation; fighters not yet in `FULL_ROSTER`, per the completeness audit's "staged fighters" section and `movesets.js`): DOA federation ×6 (`doa-kasumi, doa-bass, doa-hayabusa, doa-ayane, doa-tina, doa-jannlee`), VF federation ×3 (`vf-akira, vf-sarah, vf-kage`), intake/custom staged ids in `MOVESET_IDS` (`hugo, raiden, marduk, bob, realizzt, kutz, chordz, sunra, cainelias, vainabel` — several await owner WH name picks), plus 12 Street Fighter moveset files present but not in `MOVESET_IDS` (`sf-akuma, sf-blanka, sf-cammy, sf-chunli, sf-dhalsim, sf-guile, sf-ken, sf-mbison, sf-ryu, sf-sagat, sf-vega, sf-zangief`). Base-game fighters whose shipped models are community rips of their base (Zangief, Vega, Iori, Armor King, Dio, Bruno, Michiko, Torch) are counted as community rips in §2, not as conversions — no canon doc calls them conversions.

---

## Corrections this census makes to numbers in circulation

1. **"36 fighters"** (pasted Gemini directives) — false. 59 entries / 50 distinct fighters (§1).
2. **PR #418's 58 / 33 / 10 / 13 / 2** — a pre-fix snapshot; superseded as itemized in §1 (59 entries; own-model-shipped 49 / base-by-design 8 / fallback 1 / wired-but-absent 1).
3. **"57 fighters have movesets"** — no current cut derives 57 movesets; the numbers are 58 files / 55 loader-listed (§1). (57 is the count of entries holding both a model file and a moveset file.)
4. **Oct 20 marking sheet (101 rows; 79/19/3)** — internally exact for its date; superseded by the §2 deltas: **108 rows; wired 94 / not wired 13 / broken 1**; Tripo-original 53 → **60**.
5. **Sibling recount "59 entries, 50 distinct fighters"** — confirmed independently; adopted.
6. **Kronos A3 "not on main"** (Oct 20 sheet) — it is on main and wired (§2).

*Next census trigger: any merge that adds/removes a `FULL_ROSTER` entry, a Tripo pull, or an attire ladder (the Vain Abel A4 lane is already queued to move §2/§3).*
