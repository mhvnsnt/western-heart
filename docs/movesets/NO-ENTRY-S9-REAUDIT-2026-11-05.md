# NO-ENTRY re-audit + hygiene — roster-100 S9 (2026-11-05)

Owner order (2026-11-04 ~18:04 CST): "All of the models need to be fixed 100% and the character select images need to be fixed 100% and um yeah everything pretty much need to be fixed 100% the animations the inputs the models everything and then we can move forward from there."

**Result: NO ENTRY 593 → 561.** Phantom 17 → 2, Cyborg X 58 → 51, Megami 14 → 4. No other fighter's count moved; totals, engine contexts and chain-throw stages are unchanged (55 fighters, 15,737 move inputs, 5,577 prefixed: engine 2,859, stance-entered 2,034, chain-throw 123).

## Method

The repo's own audit, run before and after on the same tree. The lane opened on main `2aebf11d` (#1589); S6 (#1591) and S8 (#1587, which edited the four demonio moveset files) landed while it ran, so the baseline was re-measured against the merge base `ebe30a5b` — the count is identical (593, every fighter unchanged), and the before/after files in the proof dir are the `ebe30a5b` runs:

```
node tools/input-verify/stance_reachability_audit.mjs --json <out> --md <out>
```

Before/after JSON + MD are in `docs/proof/2026-11-05/roster-100-s9/` (`audit-before.json`, `audit-before.md`, `audit-after.json`, `audit-after.md`), with the engine probe `probe_s9.mjs` + `probe_s9.out.txt` (21/21 through the game's own `TekkenBuffer` / `resolveMoveKey` — the same calls `fighter.js` makes in a fight).

**The 593 was reproduced exactly before any change** — it is not stale as an input count. The Pond/Megami banks landed as animation clips, not as moveset inputs (S1 re-keyed one row in place; S5 stamped anim files), so the input universe is the same one the 2026-11-02 closeout measured. What the banks changed is which NO-ENTRY rows now have clips behind them; that is accounted per class below.

## The 47 "duplicate / artifact spellings" — what they actually are

On the evidence, the 47 split into two different things:

### 22 are duplicate spellings of an entered stance — cleared by a data-declared alias

A fighter's merged layers keyed ONE stance under two spellings. `stance_after` names only one spelling (the layer the entry move came from), and `fighter.js` holds the current stance as a single string, so every row under the other spelling could never fire.

| Fighter | Duplicate spelling (rows) | Entered spelling | Evidence in the fighter's own file |
|---|---|---|---|
| phantom | `INS` (14) | `IND` | The same move names sit under both: `INS.1` "Indian Stance Storm" / `IND.1` "Indian Stance Storm". Wired entries name IND only (`d+3+4` → IND, `POI.d+3+4` → IND). |
| phantom | `POISON_WIND` (1) | `POI` | `POISON_WIND.1+2` is a real clip-backed row; no `POI.1+2` exists, so the input itself was missing. Entries name POI (`uf+3+4` → POI). |
| cyborgx | `BKP` (5) | `BACKUP` | Same move names under both: `BKP.1` "Recovery Hook" / `BACKUP.1` "Recovery Hook". Wired entry names BACKUP (`db+1` → BACKUP). |
| cyborgx | `CLOCKWORK` (2) | `CLK` | `CLOCKWORK.3` and `CLK.3` are the same move ("Clockwork Spring Middle"). Wired entry names CLK (`ws3` → CLK). |

Fix: each moveset file now declares the pairs itself — `"stance_alias": {"INS": "IND", "POISON_WIND": "POI"}` (phantom), `{"BKP": "BACKUP", "CLOCKWORK": "CLK"}` (cyborgx) — and `_prepare` in `game/js/movesets.js` slots every duplicate-spelling key on the canonical spelling **only where nothing else owns that slot** (the same never-overwrite rule as the existing notation pass; no row is renamed or removed). The audit tool classifies a declared alias of an entered stance as `stance`, mirroring the engine.

Per-row outcome of the 22:

- **7 inputs are newly reachable:** phantom's INS-only string chain `2,D/B+2` / `2,D/B+2,2` / `2,D/B+2,2,2` / `2,D/B+2,2,2,2` and `3+4*` (fire as `IND.…`), `POISON_WIND.1+2` (fires as `POI.1+2`), and cyborgx's `BKP.1+2` "Rocket Punch" (fires as `BACKUP.1+2`). The probe drives the full phantom chain through the buffer, step by step.
- **15 rows are shadowed duplicates:** the canonical row already owns the input (9 INS, 4 BKP, 2 CLOCKWORK) and keeps it — probe-verified (`IND.1` → the `IND.1` row, `BACKUP.1` → the `BACKUP.1` row, `CLK.3` → the `CLK.3` row). For these the fix is the truthful classification: their prefix is a spelling of an entered stance, not a stance nothing enters.

### 25 are not spellings at all — dataset row-id keys, documented, not re-keyed

Byou's 25 `t7.*` keys (`t7.lei_158` and siblings) are rows of his merged dataset sitting in the input map under their dataset row ids (each row's `anim_ref` is the same id, `t7:lei:lei_158` provenance). They are not a stance, not duplicates of any other row (no other key in his file carries the same `anim_ref`), and **no input notation for any of the 25 exists anywhere** — not in byou's file, not in any other file under `game/` or `tools/`. Re-keying them would mean inventing commands, which is fabrication; deleting them would delete bank rows. They stay in the data, stay NO ENTRY, and are regrouped below as **artifact row-id keys**. Megami's 4 `t8.*` keys are the same family (dataset-id keys; the plain notations they sit next to, e.g. `b+1+3`, already exist as keys) and are regrouped with them: **artifact row-id keys = 29**.

## Megami's Izumo entry — wired (10 rows)

Megami's file had no `stance_after` at all. Her `f+1+2` is named "Izumo (stance)", classed `stance`, and its own note says "Enters Izumo stance."; her file's stance list names "IZU (Izumo, f+1+2)". The 2026-11-02 closeout teed up exactly this one-line wiring "ready to land with the TTT2 bank, not before" — the Jun bank has since landed (#1558, #1561) and her rig was rebuilt (#1576). Added: `"stance_after": {"f+1+2": "IZU"}`. All 10 `IZU.` rows now fire (probe + guard test). Her remaining 4 NO ENTRY are the `t8.*` artifact keys above.

## Pond — banked, entry moves identified, wiring NOT landed here (documented gap)

Pond's bank landed (#1550), which is what the re-audit was waiting on — but her stance wiring is a completion pass of its own, not hygiene: her `stance_after` is empty and her NO ENTRY set is 80 rows across 8 prefixes (LAB 39, SZN 14, HAZ 7, DEEP 5, MIST 5, STRIDE 5, REV 3, RAGE 2). Entry moves identified in her own data, ready for that pass: `b+3+4` "Labyrinth" (LAB), `3+4~t7.masterraven` "Haze" (HAZ), `3+4` "MIST", `qcf` "WATER STRIDE" (STRIDE), `SZN.B` "Blind Labyrinth". Still owed before wiring: per-row clip verification for the stance rows (the bank work covered the basics), and an entry move for DEEP / REV / RAGE, which her data does not name. Wiring 80 rows on move names alone, without that verification, is the guess the no-guessing law bans; the next lane starts from the identified entries above instead of re-deriving them.

## Zen — unchanged, on the owner's word

Zen's 20 NO ENTRY rows (RAI / WAR / TACKLE / REV) stay exactly as they are: the no-bank call for Zen is the owner's standing decision (2026-10-24). Not a lane call, not touched.

## Anatomy id-vs-directory 404s — the two named, plus eleven more of the same class

`game/js/xray.js` `prefetch()` built the anatomy path from the fighter id alone: `roster/<id>/anatomy/anatomy-layers.json`. The anatomy JSON lives under the fighter's roster **directory**, which is not the id for these fighters, so the fetch 404'd on both the page copy and the jsDelivr fallback (fail-silent by design: no X-ray layer reveal, no error). The roster pass (#1562–#1564) only observed cyborgx and mariposa-monarch because it only fought four fighters. The S9 cross-check — every one of the 59 roster ids against every anatomy directory on main — found the full class: **13 fighters**. Each directory below is the one holding that fighter's own attires, and its `anatomy-layers.json` says so itself (its `fighter` field names the WH fighter; its skin `mesh_ref` points at that directory's own model file):

| Fighter id | Anatomy directory | The file's own mesh_ref |
|---|---|---|
| cyborgx | cyborg-x | roster/cyborg-x/attires/attire1/model-rigged.glb |
| mariposa-monarch | mariposa | roster/mariposa/attires/monarch/mariposa-monarch-rigged.glb |
| samura1 | sam-ur-a1 | roster/sam-ur-a1/attires/attire1/model-rigged.glb |
| baek-master-white | baek | roster/baek/attires/attire1/model-rigged.glb |
| docfrank | doc-frank | roster/doc-frank/attires/attire1/model-rigged.glb |
| awapop | awa-pop | roster/awa-pop/attires/attire2/model-rigged.glb |
| dxmmii-patchwork | dxmmii | roster/dxmmii/attires/attire1/model-rigged.glb |
| pond | tsuyu-asui | roster/tsuyu-asui/attires/attire1/model-rigged-textured.glb |
| ryusan | mina-ashido | roster/mina-ashido/attires/attire1/model-rerig.glb |
| tobi | miruko | roster/miruko/attires/attire1/model-rerig-textured.glb |
| chatur | rahkasa | roster/rahkasa/attires/attire1/model-rigged-textured.glb |
| megami | parvati | roster/parvati/attires/attire1/model-rigged.glb |
| menajerii | vixen | roster/vixen/attires/attire1/model-rigged-noplane.glb |

Fix: a documented `ANATOMY_DIR` map in `xray.js` (exported as `anatomyDir()`), used by `prefetch()`; guard assertions in `test/xray.test.mjs` pin the cyborgx and mariposa-monarch fetch URLs. Of the 59 roster ids, 24 already matched their directory and now 13 more resolve through the map; the remaining 22 have no anatomy file under any directory (charger, gashadokuro, aotsuki, the seven un-modelled fighters among them) and keep the designed fail-silent path — that is not a defect and nothing was fabricated for them. The only anatomy directories no roster id uses are six base-character dirs (jin, panda, vega, zafina, zangief, armor-king), which belong to no WH fighter's id.

## What remains of the 561

| Class | Rows | Status |
|---|---|---|
| Tackle family (TACKLE 118, MD1 6, MD2 6, UT 2) | 132 | Owner gameplay decision (tackle-mount re-classing). Count only — nothing re-classed. |
| Bank-linked stance rows (pond 80, zen 20) | 100 | Pond: entries identified above, wiring pass owed. Zen: owner's no-bank decision. |
| Artifact row-id keys (byou `t7.*` 25, megami `t8.*` 4) | 29 | No input notation exists for them anywhere in the repo. Documented; data untouched. |
| Engine contexts + moves with no entry move in the fighter's own data | 300 | The 2026-11-02 remainder classes, unchanged by this pass. |
| **Total** | **561** | |

Count note: the 2026-11-02 closeout hand-grouped the tackle family as 128 (TACKLE 114). Both the 2026-11-01 audit output and this re-run read TACKLE = 118; the closeout's subtotal reads 4 low, and its remainder grouping (304) carries the same 4. The roll-up above uses the tool's numbers throughout so the classes sum to the measured 561.

## Changes in this PR

- `game/assets/movesets/phantom.json` — `stance_alias` line added (data only; no row touched).
- `game/assets/movesets/cyborgx.json` — `stance_alias` line added (data only; no row touched).
- `game/assets/movesets/megami.json` — `stance_after: {"f+1+2": "IZU"}` line added.
- `game/js/movesets.js` — `_prepare` slots declared stance-alias keys on the canonical spelling (never overwrites an owned slot).
- `tools/input-verify/stance_reachability_audit.mjs` — an alias of an entered stance classifies as `stance`.
- `game/js/xray.js` — `ANATOMY_DIR` map + `anatomyDir()`; `prefetch()` uses it.
- `test/stance-reachability.test.mjs`, `test/xray.test.mjs` — guard coverage for all of the above.
- `docs/movesets/STANCE-REACHABILITY-AUDIT-2026-11-01.md` — regenerated from the tool on current main (its table had not been regenerated since 2026-11-01 and still showed 1,363), preamble extended with the 2026-11-02 and S9 lines.
- `docs/proof/2026-11-05/roster-100-s9/` — audit before/after (JSON + MD), `probe_s9.mjs`, `probe_s9.out.txt` (21/21).
- `docs/handoffs/ROSTER-100-FIX-2026-11-04.md` — S9 execution record.

## Deviations

1. **Anatomy scope 2 → 13.** The item named cyborgx and mariposa-monarch; the proven class is 13 fighters with the identical mechanism. All 13 are fixed, each on its own file's evidence (table above). The two named fighters are confirmed members of the class.
2. **The 47 split on evidence.** 22 are duplicate stance spellings (alias fix); 25 are dataset row-id keys, not spellings — documented and regrouped, not re-keyed, because no input notation for them exists anywhere in the repo and inventing commands would be fabrication.
3. **Megami wired, Pond not.** Megami's one-line wiring was teed up by the 2026-11-02 closeout for post-bank landing and is proven by her own data. Pond's wiring is an 80-row completion pass needing per-row clip verification first; it is documented with its identified entry moves instead of being half-done inside a hygiene item.
