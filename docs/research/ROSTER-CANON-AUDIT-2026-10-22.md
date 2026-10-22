# ROSTER-TO-CANON RECONCILIATION AUDIT (2026-10-22)

**Worker 19 — Western Heart round.** Owner quote: *"CANON.md knows who's a character, but the
character select screen and game have a whole bunch of random bullshit. Every slot in the game
must trace back to a real canon identity. A canon character means the END-GAME Western Heart
identity — NOT the teardown base."*

**Canon rule applied:** a canon character = the end-game WH identity (Pantera, Birodo…).
A Tekken/model base (King, Feng Wei, Zafina, Armor King…) is raw material, never a character,
never selectable, never counted.

**Base commit audited:** main @ `eaf3303` (2026-10-22). All game-code facts below were read
from main via the Git Database API (`game/js/roster-full.js`, `select-screen.js`, `attires.js`,
`assets.js`), CANON.md @ `153b23f`, the 55 `roster/` dirs, and all 65 open PRs.

---

## 1. THE REAL TOTAL: 49 CANON CHARACTERS

| # | Character | Group | Where it lives today |
|---|-----------|-------|----------------------|
| 1 | PANTERA | The Seven | roster dir + select slot |
| 2 | DEMONIO | The Seven | roster dir + select slot |
| 3 | PHANTOM | The Seven | roster dir + select slot |
| 4 | DIABLO | The Seven | roster dir + select slot |
| 5 | SKULL | The Seven | roster dir + select slot |
| 6 | SAM-UR-A1 | The Seven | roster dir + select slot |
| 7 | SAKU RA | The Seven | roster dir + select slot (dirs `saku-ra/` + `sakura/` — split, dedup pending) |
| 8 | ZUI | The Four | roster dir + select slot |
| 9 | KINPO | The Four | roster dir + select slot |
| 10 | WATERFALL | The Four | roster dir + select slot |
| 11 | KING TYRANT | The Four | roster dir + select slot |
| 12 | BURGER | The Twelve | roster dir + select slot |
| 13 | AWA POP | The Twelve | roster dir + select slot |
| 14 | SCIMITAR | The Twelve | select slot only — **no roster dir, model unwired** (need-models list) |
| 15 | PURPLE RAIN | The Twelve | roster dir + select slot (dirs `purple-rain/` + `purplerain/` — split, dedup pending) |
| 16 | NIGHTWOLF | The Twelve | roster dir + select slot |
| 17 | MICHIKO | The Twelve | roster dir + select slot |
| 18 | STAR | The Twelve | roster dir + select slot |
| 19 | TORCH | The Twelve | roster dir + select slot |
| 20 | DIO | The Twelve | select slot only — **no roster dir, model unwired** (need-models list) |
| 21 | CYBORG X | The Twelve | roster dir + select slot |
| 22 | BRUNO | The Twelve | select slot only — **no roster dir, model unwired** (need-models list) |
| 23 | N3GΔTIV0 | The Twelve | select slot only — **no roster dir**, model `assets/models/n3g4tiv0.glb` wired (need-models list) |
| 24 | SILVERTONGUE | New Vessels | roster dir + 4 attires — **NO select slot** (missing!) |
| 25 | KEVIN | New Vessels | select slot `baek-master-white`; models via `roster/baek/` (Baek = Kevin's A2) |
| 26 | JIN (Eastern Mind) | New Vessels | **NO model, NO select slot.** `roster/jin/` is a leftover (bloodline-ember staging). CANON.md still says "JIN KAZAMA" — conflicts with owner directive 2026-10-22 (EM-Jin ≠ Jin Kazama). PR #620 tracks the rename. |
| 27 | STEVE FOX | New Vessels | canon entry, **no roster dir, no select slot** (exists today only as a base model) |
| 28 | DXMMII | New Vessels | roster dir + select slot `dxmmii-patchwork` |
| 29 | MARIPOSA (= Mary Posa) | New Vessels | roster dir + select slot `mariposa-monarch`; Zafina ladders under her |
| 30 | DOC FRANK | New Vessels | roster dir + select slot `docfrank` |
| 31 | KIKO TANAKA (= RAVE = Ghost) | New Vessels | roster dir `kiko-tanaka/`; select slot is `rave` (model `kiko-tanaka`); attires.js already ladders `rave` as Kiko's Attire 3 — separate slot is a dedup leftover |
| 32 | THOR | New Vessels (bonus) | roster dir + select slot |
| 33 | SLICE | New Vessels (bonus) | roster dir + select slot |
| 34 | YUKIHYŌ | New Vessels (bonus) | select slot `yukihyo`; models via `roster/armor-king/` (Armor King = his base) |
| 35 | CAIN ELIAS | New Vessels (bonus) | roster dir + 2 attires — **NO select slot** (missing!) |
| 36 | DEATHFANG | New Vessels (bonus) | roster dir + select slot |
| 37 | CORNERSTONE | New Vessels (bonus) | **PR #449 pending**: renames `ryuji-rock` → CORNERSTONE, wires Tripo Attire 1. Currently NO select slot on main. (`roster/ryuji-rock/` holds his models.) |
| 38 | BIRODO | Intake | **no roster dir, no select slot** (pending) |
| 39 | JOTEI | Intake | **no roster dir, no select slot** (pending) |
| 40 | CHATUR | Intake | roster dir `rahkasa/` (old name) — **NO select slot** (missing!) |
| 41 | RYUSAN | Intake | **no roster dir, no select slot** (pending) |
| 42 | POND | Intake | roster dir `tsuyu-asui/` (old name) — **NO select slot** (missing!) |
| 43 | MEGAMI | Intake | **no roster dir, no select slot** (pending) |
| 44 | MENAJERII | Intake | roster dir `vixen/` (old name) — **NO select slot** (missing!) |
| 45 | TOBI | Intake | **no roster dir, no select slot** (pending) |
| 46 | CHARGER | Owner-locked (Blanka replacement, owner verbatim 2026-10-20) | roster dir + select slot. CANON.md entry pending. |
| 47 | VAIN ABEL | Owner-locked (Cain Elias's brother, owner 2026-10-20) | roster dir + 4 Tripo attires — **NO select slot** (missing!). CANON.md entry pending. |
| 48 | DOROWANI | Owner-locked (Gon's WH replacement, owner 2026-10-22) | roster dir + select slot `dorowani`. Referenced in CANON.md canon web; full entry pending. |
| 49 | ZEN | Owner-locked spirit entity (owner canon `roster/zen/CANON.md` 2026-10-21; main CANON.md: the Still Soul, unvesseled — "refused the trial") | roster dir + select slot `zen` (currently a soul-tier placeholder using the wrong model). Playability TBD by owner. |

Not counted: SUN RĀ — CANON.md: *"Not a fighter. A realm."* (boss/arena entity, not a select character).
Not counted: the Nine Souls as such — CANON.md §4: *"The nine are not characters. They are the
condition the characters exist in."* RIN/BYOU/TOU/SHA/KAI/JIN/RETSU/ZEN/GYOU are souls, not fighters.

**Location summary (49):** roster dir + select slot: 31 · select slot only (no dir): 4
(Scimitar, Dio, Bruno, N3g4tiv0) · roster dir, no select slot: 6
(Silvertongue, Cain Elias, Vain Abel, Chatur, Pond, Menajerii) · PR pending: 1 (Cornerstone) ·
intake pending (neither): 6 (Birodo, Jotei, Ryusan, Megami, Tobi, Steve Fox) · special: 1 (EM-Jin).

---

## 2. FULL CLASSIFICATION TABLE

Every `roster/` dir on main (55), every hardcoded select entry without a dir, every
character-adding open PR, and the intake set. Classes: **CANON** · **TEMPLATE** (base with no
WH identity — fold or build canon) · **ATTIRE** (ladder under another character) · **ORPHAN**
(in game but no canon identity — user decision) · **SOUL** (not a character per CANON.md §4) ·
**DOC** (not a character).

### 2a. Roster dirs (55)

| Dir | Class | Canon identity / notes |
|-----|-------|------------------------|
| armor-king | TEMPLATE | Tekken base for YUKIHYŌ (canon). Never a character itself. Fold under Yukihyō's ladder. |
| awa-pop | CANON | AWA POP (Twelve). Select slot `awapop`. |
| baek | ATTIRE | KEVIN's A2 model (canon: "Baek's model is Kevin's A2 attire"). Select slot `baek-master-white`. |
| blanka | TEMPLATE | Raw SF base, superseded. Owner: "Blanka's roster slot is [Charger's] now"; files stay in repo, not selectable. |
| bonus | DOC | Only `BONUS-CHARACTERS.md` (design notes). Not a character. |
| burger | CANON | BURGER (Twelve). Select slot `burger`. |
| cain-elias | CANON | CAIN ELIAS (Vessels bonus). 2 attires wired. **Missing from select.** |
| charger | CANON | CHARGER — owner-named Blanka replacement (verbatim 2026-10-20). Select slot `charger`. CANON.md entry pending. |
| cyborg-x | CANON | CYBORG X (Twelve). Select slot `cyborgx`. |
| deathfang | CANON | DEATHFANG (Vessels bonus). Select slot `deathfang`. |
| demonio | CANON | DEMONIO (Seven). Select slot `demonio`. |
| diablo | CANON | DIABLO (Seven). Select slot `diablo`. |
| doc-frank | CANON | DOC FRANK (Vessels). Select slot `docfrank`. |
| dorowani | CANON | DOROWANI — Gon's WH replacement (owner-locked). Select slot `dorowani`. |
| dxmmii | CANON | DXMMII (Vessels). Select slot `dxmmii-patchwork`. |
| gyou | SOUL | GYOU soul — unvesseled per canon ("a splinter trapped in CYBORG X"). Dir = soul-body assets. Select slot `gyou` is a non-canon placeholder. |
| iori | TEMPLATE | Iori Yagami base for DEATHFANG (canon: "built on Iori Yagami: he keeps Iori's moves"). Select slot `iori` must go — Deathfang is the character. |
| jin | ORPHAN | Leftover staging dir (bloodline-ember images). EM-Jin has NO model per owner (user finding reference). CANON.md "JIN KAZAMA" conflicts with EM-Jin directive — needs owner call. |
| kiko-tanaka | CANON | KIKO TANAKA = RAVE = Ghost (one person, owner identity canon). Models live here; select slot is `rave`. |
| king-tyrant | CANON | KING TYRANT (Four). Select slot `kingtyrant`. |
| kinpo | CANON | KINPO (Four). Select slot `kinpo`. |
| koreshi | ORPHAN | "The Shadow Ninja" (Kakashi+SSJ). Tripo models + select slot, zero canon. **User decision: build canon or cut.** |
| kronos | ORPHAN | "The Titan Cyclone" (Zangief+Golem). 3 attires + select slot, zero canon. **User decision: build canon or cut.** |
| lili | TEMPLATE | Lili's T7 frame = SILVERTONGUE's base model (canon). Fold under Silvertongue. |
| mariposa | CANON | MARIPOSA = Mary Posa (Vessels). Select slot `mariposa-monarch`. |
| michiko | CANON | MICHIKO (Twelve). Select slot `michiko`. |
| mina-ashido | TEMPLATE | SmutBase intake (MHA). No WH identity. Raw material. |
| miruko | TEMPLATE | SmutBase intake (Rumi Usagiyama). No WH identity. Raw material. |
| nightwolf | CANON | NIGHTWOLF (Twelve). Select slot `nightwolf`. |
| pantera | CANON | PANTERA (Seven). Select slot `pantera`. |
| parvati | TEMPLATE | SmutBase intake. No WH identity. Raw material. |
| phantom | CANON | PHANTOM (Seven). Select slot `phantom`. |
| purple-rain | CANON | PURPLE RAIN (Twelve). Metadata dir (ATTIRE-SLOTS.md + kitbash). **Split with `purplerain/` — dedup.** |
| purplerain | CANON | Same character; holds `attires/`. Select slot `purplerain`. **Merge with `purple-rain/`.** |
| rahkasa | CANON | CHATUR (Intake) — dir under old intake name. **Missing from select.** |
| rave | CANON | RAVE = Kiko Tanaka. attires.js already lists `rave` as Kiko's Attire 3 (MUTA) — the separate select slot `rave` is a dedup leftover; fold into Kiko's ladder. |
| ryuji-rock | CANON | CORNERSTONE (Vessels bonus) — PR #449 renames the select entry. Models here. |
| saku-ra | CANON | SAKU RA (Seven). Metadata dir. **Split with `sakura/` — dedup.** |
| sakura | CANON | Same character; holds `attires/`. **Merge with `saku-ra/`.** |
| sam-ur-a1 | CANON | SAM-UR-A1 (Seven). Select slot `samura1`. |
| silvertongue | CANON | SILVERTONGUE (Vessels). 4 attires wired. **Missing from select.** |
| skull | CANON | SKULL (Seven). Select slot `skull`. |
| slice | CANON | SLICE (Vessels bonus). Select slot `slice`. |
| star | CANON | STAR (Twelve). Select slot `star`. |
| thor | CANON | THOR (Vessels bonus). Select slot `thor`. |
| torch | CANON | TORCH (Twelve). Select slot `torch`. |
| tsuyu-asui | CANON | POND (Intake) — dir under old intake name. **Missing from select.** |
| vainabel | CANON | VAIN ABEL — Cain Elias's brother (owner 2026-10-20). 4 Tripo attires. **Missing from select.** CANON.md entry pending. |
| vega | TEMPLATE | Sketchfab intake. Owner: "working names, WH names pending owner pick." Not selectable as Vega. |
| vixen | CANON | MENAJERII (Intake) — dir under old intake name. **Missing from select.** |
| waterfall | CANON | WATERFALL (Four). Select slot `waterfall`. |
| zafina | TEMPLATE | Zafina = MARIPOSA's Tekken base ("Mary Posa goes OVER Safina"). Already ladders under `mariposa-monarch`. Never a character. |
| zangief | TEMPLATE | Sketchfab intake. "Working names, WH names pending owner pick." Not selectable as Zangief. |
| zen | CANON | ZEN spirit entity (owner canon `roster/zen/CANON.md`). Select slot `zen` exists but uses wrong (tinted steve-fox) model — rewire to his Tripo spirit body. Playability TBD. |
| zui | CANON | ZUI (Four). Select slot `zui`. |

Dir counts: CANON 39 (incl. the 4 split-dup partners purple-rain/purplerain, saku-ra/sakura) ·
TEMPLATE 10 (armor-king, blanka, iori, lili, mina-ashido, miruko, parvati, vega, zafina, zangief) ·
ATTIRE 1 (baek) · ORPHAN 3 (jin, koreshi, kronos) · SOUL 1 (gyou) · DOC 1 (bonus) = 55 ✓

### 2b. Hardcoded select entries with NO roster dir (main `game/js/roster-full.js`)

| Entry | Class | Notes |
|-------|-------|-------|
| rin, byou, tou, sha, kai, retsu | SOUL | The Nine Souls are not characters (CANON.md §4). All 6 slots must go. (byou: canon notes "Lei is not Byou — he is Rave/Kiko".) |
| scimitar | CANON | SCIMITAR (Twelve). No dir, model unwired — on the need-models list. |
| dio | CANON | DIO (Twelve). No dir, model unwired — on the need-models list. |
| bruno | CANON | BRUNO (Twelve). No dir, model unwired — on the need-models list. |
| negativo | CANON | N3GΔTIV0 (Twelve). No dir; model `assets/models/n3g4tiv0.glb` wired. |
| ryuji | ORPHAN | "RYUJI — The Wicked Heretic" (base Ryuji Yamazaki, model steve-fox). No roster dir on main (deleted). Canon's Ryuji×Rock hybrid is CORNERSTONE — this bare-Ryuji slot has no identity. **User decision: fold into Cornerstone's ladder or cut.** |

### 2c. Open PRs that add characters (65 open reviewed)

| PR | Effect | Class |
|----|--------|-------|
| #434 "Wire Urban Reign fighters into the playable build" | Adds **72** select entries `ur-char001`…`ur-char072` named `CHAR001`…`CHAR072` ("Street Reign Guest") | **ORPHAN ×72** — the PR's own `CANON-CONVERSION.md` says: "FLAGGED, not mapped… no UR fighter [has a canon mapping]". **Must not merge as selectable.** This is the single biggest source of "random bullshit" if merged. |
| #449 "CornerStone Attire 1: owner's Tripo model wired" | Renames select entry `ryuji-rock` → **CORNERSTONE**, wires Tripo A1 | CANON — merge when green (completes #37) |
| #450 / #463 / #510 | Cornerstone moveset + Toguro mechanics | CANON — supporting lanes |
| #620 "Jin (Eastern Mind) / EM-Jin naming" | Docs: establishes EM-Jin ≠ Jin Kazama | CANON — docs only |
| all others (teardowns, movesets, docs, rigging) | No new selectable characters | — |

### 2d. Intake set (8)

| Character | Dir | Select | Status |
|-----------|-----|--------|--------|
| BIRODO | none | none | pending |
| JOTEI | none | none | pending |
| CHATUR | `rahkasa/` | none | models under old name; needs select entry + rename |
| RYUSAN | none | none | pending |
| POND | `tsuyu-asui/` | none | models under old name; needs select entry + rename |
| MEGAMI | none | none | pending |
| MENAJERII | `vixen/` | none | models under old name; needs select entry + rename |
| TOBI | none | none | pending |

---

## 3. SELECT SLOT → CANON → MODELS (source of truth, main @ eaf3303)

49 slots in `FULL_ROSTER`. **Bold** = non-canon slot (must go or be remapped). Model ladders
from `game/js/attires.js` `ATTIRE_VARIANTS` (29 wired ladders); others use the entry's base model.

| # | Slot id | Display | Canon identity | Models (ladder head → back) |
|---|---------|---------|----------------|------------------------------|
| 1 | **rin** | RIN | **SOUL — not a character** | steve-fox (tint placeholder) |
| 2 | **byou** | BYOU | **SOUL — not a character** (Lei is Rave, not Byou) | steve-fox (tint placeholder) |
| 3 | **tou** | TOU | **SOUL — not a character** | pantera (tint placeholder) |
| 4 | **sha** | SHA | **SOUL — not a character** | steve-fox (tint placeholder) |
| 5 | **kai** | KAI | **SOUL — not a character** | pantera (tint placeholder) |
| 6 | **retsu** | RETSU | **SOUL — not a character** | pantera (tint placeholder) |
| 7 | zen | ZEN | ZEN (spirit entity; slot uses wrong model) | REWIRE: zen-attire1 (Tripo spirit body), zen-body (legacy) |
| 8 | **gyou** | GYOU | **SOUL — not a character** (unvesseled) | pantera (tint placeholder) |
| 9 | pantera | PANTERA | PANTERA (Seven) | pantera-leoman, pantera-leopard-king, pantera, pantera-snow-leopard, pantera-crimson-rage, pantera-p2 |
| 10 | demonio | DEMONIO | DEMONIO (Seven) | demonio, demonio-a1, demonio-winged, demonio-human, demonio-bloodline-ember |
| 11 | phantom | PHANTOM | PHANTOM (Seven) | phantom, phantom-t8, steve-fox, jin-bloodline-ember |
| 12 | diablo | DIABLO | DIABLO (Seven) | diablo, diablo-attire2 |
| 13 | skull | SKULL | SKULL (Seven) | skull (single) |
| 14 | samura1 | SAM-UR-A1 | SAM-UR-A1 (Seven) | sam-ur-a1 (single) |
| 15 | sakura | SAKU RA | SAKU RA (Seven) | saku-ra, saku-ra-main |
| 16 | zui | ZUI | ZUI (Four) | zui-attire1, zui-attire2, steve-fox, zui_alt1, zui_alt2 |
| 17 | kinpo | KINPO | KINPO (Four) | kinpo, kinpo-attire2, kinpo-t8 |
| 18 | waterfall | WATERFALL | WATERFALL (Four) | waterfall (single) |
| 19 | kingtyrant | KING TYRANT | KING TYRANT (Four) | king-tyrant-attire1…4, king-tyrant |
| 20 | burger | BURGER | BURGER (Twelve) | burger, burger-attire2…7 |
| 21 | awapop | AWA POP | AWA POP (Twelve) | awa-pop, awa-pop-attire2 |
| 22 | scimitar | SCIMITAR | SCIMITAR (Twelve) | **UNWIRED — need-models list** |
| 23 | purplerain | PURPLE RAIN | PURPLE RAIN (Twelve) | purple-rain, purple-rain-main |
| 24 | nightwolf | NIGHTWOLF | NIGHTWOLF (Twelve) | nightwolf-attire1, nightwolf |
| 25 | dio | DIO | DIO (Twelve) | **UNWIRED — need-models list** |
| 26 | cyborgx | CYBORG X | CYBORG X (Twelve) | cyborgx (single; model key cape-jones) |
| 27 | michiko | MICHIKO | MICHIKO (Twelve) | michiko-attire1, michiko-attire2, michiko |
| 28 | star | STAR | STAR (Twelve) | star-attire1, star-attire2, star-attire3, star-attire5, star |
| 29 | torch | TORCH | TORCH (Twelve) | torch-tripo-a1, torch-tripo-a2, torch (Tripo-first ✓) |
| 30 | bruno | BRUNO | BRUNO (Twelve) | **UNWIRED — need-models list** |
| 31 | negativo | N3GΔTIV0 | N3GΔTIV0 (Twelve) | n3g4tiv0 (`assets/models/n3g4tiv0.glb`) |
| 32 | thor | THOR | THOR (Vessels bonus) | thor, thor-attire2 |
| 33 | yukihyo | YUKIHYŌ | YUKIHYŌ (Vessels bonus) | yukihyo (via `roster/armor-king/`) |
| 34 | slice | SLICE | SLICE (Vessels bonus) | slice-attire1, slice-attire2 |
| 35 | docfrank | DOC FRANK | DOC FRANK (Vessels) | doc-frank-big, doc-frank-wowomomo(+big), doc-frank-hood(+big), doc-frank-frankenstein(+big), doc-frank-a1, doc-frank, doc-frank-machine-shop (Tripo-first ✓) |
| 36 | baek-master-white | KEVIN | KEVIN (Vessels) | kevin-tripo, baek, baek-master-white (Tripo-first ✓) |
| 37 | mariposa-monarch | MARIPOSA | MARIPOSA = Mary Posa (Vessels) | mariposa-butterfly-default, mariposa, mariposa-monarch, zafina-golden-pharaoh, zafina (Zafina ladders back ✓) |
| 38 | dxmmii-patchwork | DXMMII | DXMMII (Vessels) | dxmmii-tripo, dxmmii-patchwork, dxmmii-a2 |
| 39 | **zangief** | ZANGIEF | **TEMPLATE — no WH identity** (WH name pending owner pick) | zangief |
| 40 | charger | CHARGER | CHARGER (owner-locked) | charger, charger-attire2 |
| 41 | dorowani | DOROWANI | DOROWANI (owner-locked, Gon replacement) | dorowani |
| 42 | **vega** | VEGA | **TEMPLATE — no WH identity** (WH name pending owner pick) | vega |
| 43 | **iori** | IORI | **TEMPLATE — Deathfang's base, not a character** | iori |
| 44 | **armor-king** | ARMOR KING | **TEMPLATE — Yukihyō's base, not a character** | armor-king |
| 45 | **kronos** | KRONOS | **ORPHAN — no canon** | kronos, kronos-attire2, kronos-attire3 |
| 46 | deathfang | DEATHFANG | DEATHFANG (Vessels bonus) | deathfang, deathfang-werewolf |
| 47 | **ryuji** | RYUJI | **ORPHAN — no canon** (no roster dir; Cornerstone is the hybrid) | steve-fox |
| 48 | **koreshi** | KORESHI | **ORPHAN — no canon** | koreshi |
| 49 | rave | RAVE | KIKO TANAKA = Rave = Ghost (Vessels) | kiko-tanaka, kiko-tanaka_alt1, rave (fold slot into Kiko's ladder — dedup) |

**Slot census:** 49 slots = 34 canon + 15 non-canon (7 soul placeholders + iori/armor-king templates
+ zangief/vega templates + kronos/koreshi/ryuji orphans). The zen slot is canon-identity but wrong-model.

---

## 4. FLAGS FOR THE USER (decisions needed before the canon-only select)

### A. Templates: build canon or fold (7)
1. **iori** — fold into DEATHFANG's ladder (canon says Deathfang "keeps Iori's moves"); delete the `iori` select slot.
2. **armor-king** — fold into YUKIHYŌ's ladder (his Tekken base); delete the `armor-king` select slot.
3. **zafina** (dir) — already ladders under Mariposa; confirm dir stays as raw material, never selectable. ✓ (no action)
4. **blanka** (dir) — stays in repo per your order (Charger took the slot); confirm never selectable. ✓ (no action)
5. **lili** (dir) — Silvertongue's base; confirm it stays a template dir only.
6. **zangief** — Sketchfab intake, "WH name pending owner pick." **Pick a WH name/identity or cut the slot.**
7. **vega** — same as Zangief. **Pick a WH name/identity or cut the slot.**
8. **mina-ashido / miruko / parvati** (dirs) — SmutBase intake raw material, no slots. No action unless you want them as characters.

### B. Orphans: build canon or cut (5)
1. **kronos** (dir + 3 attires + select slot) — no canon whatsoever. **Keep as new WH character (needs CANON.md entry) or cut?**
2. **koreshi** (dir + Tripo models + select slot) — no canon whatsoever. **Keep or cut?**
3. **ryuji** (select slot only, no dir) — bare Ryuji Yamazaki; canon's hybrid is CORNERSTONE. **Fold into Cornerstone's attire ladder or cut?**
4. **jin** (dir) — leftover bloodline-ember staging. EM-Jin has no model yet (you're finding the reference). **Delete/park the dir until EM-Jin's model lands?** Also: CANON.md still says "JIN KAZAMA — The Bloodline Soul" — confirm the entry should be rewritten as Jin (Eastern Mind).
5. **PR #434's 72 Urban Reign guests** — explicitly unmapped (their own doc says FLAGGED, not mapped). **Do not merge #434's roster wiring** until each maps to a canon identity — or land it models-only with zero select entries.

### C. Canon characters missing from select (7) — wire up, no user decision needed
- SILVERTONGUE (4 attires), CAIN ELIAS (2 attires), VAIN ABEL (4 Tripo attires),
  CHATUR (`rahkasa/`), POND (`tsuyu-asui/`), MENAJERII (`vixen/`), CORNERSTONE (PR #449).
- Plus intake pending models: BIRODO, JOTEI, RYUSAN, MEGAMI, TOBI. Plus STEVE FOX, EM-JIN, SCIMITAR, DIO, BRUNO (need-models list).

### D. Dedup / housekeeping (no canon impact)
- `rave` select slot → fold into Kiko Tanaka's attire ladder (attires.js already lists it as Attire 3).
- `purple-rain/` + `purplerain/` → merge into one dir. `saku-ra/` + `sakura/` → merge into one dir.
- `zen` select slot → rewire model to his Tripo spirit body (`zen-attire1`); confirm whether Zen is playable or a spirit/boss entity.
- `bonus/` dir → it's only a doc; fine as-is.

### E. Canon conflicts spotted
- CANON.md "JIN KAZAMA — The Bloodline Soul" vs your 2026-10-22 directive (EM-Jin ≠ Jin Kazama; PR #620). CANON.md needs the rewrite.
- `phantom` attire ladder contains `steve-fox` and `jin-bloodline-ember` models — likely mislabeled; worth a look when the select is rebuilt.

---

## 5. METHOD

- `roster/` dirs: `GET /repos/mhvnsnt/western-heart/contents/roster?ref=main` → 55 dirs, each dir listed.
- Select slots: `game/js/roster-full.js` @ main (49 entries, `SOUL_IDS`/`MAIN_IDS`), tiering in `game/js/select-screen.js` @ main.
- Attire ladders: `game/js/attires.js` @ main (`ATTIRE_VARIANTS`, 29 ladders). Model keys: `game/js/assets.js` `MODEL_URLS` @ main.
- Canon: CANON.md @ main (`153b23f`) — all `###` headings + targeted section reads (§4 Nine Souls, intake §, New Vessels).
- PRs: all 65 open PRs listed; character-adding candidates (#434, #449, #450, #463, #510, #406) had file lists + patches inspected.
- Owner directives: `docs/owner-directives.md` where cited; RENAME-MAP.md, TRIPO-REGISTRY.md, per-dir READMEs/ATTIRE-SLOTS.md.
- Sandbox note: this worker's Python could not write files >~8KB, so large repo files were read
  through the API in chunks and only small extracts were materialized. No game code was changed
  in this task (audit only).

**Bottom line for the select rebuild:** keep the 34 canon slots (rewire zen's model), add the 7
missing canon fighters (+ Cornerstone via #449), fold the 4 templates into ladders, cut the 7
soul placeholders, resolve the 5 orphans with the user, and keep #434's 72 guests out of the
select until each has a canon identity. That yields a 41-slot canon select today (34 + 7),
49 when intake + need-list models land.
