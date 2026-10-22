# Moveset Library — Schema & System Design (research)

**Worker 47, 2026-10-22.** Owner directive (verbatim): *"build a central moveset/animation library from ALL teardowns (wrestling, Tekken, VF5, etc.), organized by type (grapples, strikes, etc.), position, and orientation in our Tekken-style framework. Then per fighter: swap, customize, edit, and SAVE movesets assembled from the library. Custom movesets per fighter, editable and saved."*

## Where it lives

| Path | What |
|---|---|
| `game/data/moveset-library/index.json` | Bank registry: 5 live banks, 9 pending, total move count |
| `game/data/moveset-library/banks/*.json` | Per-bank move entries (`t3`, `wrestling`, `wmxix`, `doa`, `vf`) |
| `game/data/moveset-library/schema.json` | JSON Schema (draft-07) for one library entry |
| `game/data/moveset-library/axes.json` | Controlled vocabularies for every organization axis |
| `game/data/moveset-library/claimed-map.json` | Moveset Source Law claimed map (machine-enforced) |
| `game/data/movesets/<fighter>.json` | Per-fighter assembly manifests (reference library IDs, never copy) |
| `game/js/moveset-library.js` | Assembler: manifest → v2-contract moveset; source-law gate; pending-bank handling |
| `game/moveset-browser.html` | Dev UI: browse by axis, inspect, attach/detach, save |
| `tools/moveset-library/ingest.mjs` | Reproducible ingest: teardown sources → banks |

## Entry schema (v1)

A library entry is the unit of reuse. Fields:

- **Identity:** `id` (namespaced: `t3:<fighter>:row:<n>`, `wrestling:<mk-id>`, `wmxix:<id>`, `doa:<char>:<slot>`, `vf:<char>:<slot>`, `vf5:<char>:<slug>`, `wh:<slug>`), `name`, `name_status` (honesty flag — auto-labels are marked, never invented canon names), `source`, `source_game_label`, `source_character`, `anim_ref` (v2 preview hook: `t3:king:row:44`, `doa:bass:palm-jab`, …).
- **Axes (see axes.json):** `type` (strike/grapple/throw/hold/aerial/counter/transition/stance/taunt/special), `subtype` (free-form), `position` (standing/crouching/grounded/back-turned/sidestep-L/R/jumping/running/airborne/corner/apron/mounted), `orientation` (forward/backward/left/right/up/down), `hit_level` (high/mid/low/special-mid/throw/unblockable), `properties[]` (launch, knockdown, wall-splat, counter-hit, power-crush, homing, armor, comedy-whiff-candidate, dark-finisher, …).
- **Tekken input mapping:** `input` (Tekken notation `1/2/3/4`, `d/f+2`, `1,2`, `qcf+2`, `1+3`…), `input_slots[]`. **Federation rule:** every non-Tekken move is wired to Tekken inputs on ingest — no wrestling control schemes ever reach the player. T3 bank rows carry `input: null` (branch target slots need the slot table; the #615 fidelity engine owns that decode) — **assembly assigns the slot**, which is exactly the editor workflow.
- **Frames:** `frames.{startup,active,recovery,total}` in **frames @60fps** (integer). The v2 editor contract uses seconds; the assembler converts.
- **Damage:** `damage_raw` (source value) + `damage` (WH 100HP scale). T3: `round(raw/3)` — estimated, flagged. No Mercy: power tier F→2 … S→22 — estimated, flagged.
- **WH tuning:** `wh.{knock, soulGain, heavy}`.
- **Provenance:** `provenance.{note, estimated[]}` — every estimated field is listed. Nothing is invented as canon. Raw T3 `state_word`/`attack_word` are preserved for later decode.

The schema is **additive over the v2 moveset-editor contract** (`docs/movesets/MOVESET-SCHEMA.md`): the assembler projects any entry to a v2 move (`name, input, input_slots, move_class, anim_ref, damage, startup/active/recovery, limb, heavy, knock, soulGain, throw/isGrab/unblockable, note`) — the same shape `game/js/movesets.js` reads.

## Bank inventory (built 2026-10-22)

| Bank | Source | Moves | Notes |
|---|---|---|---|
| `t3` | Tekken 3 PSX SLUS_004.02, 20 divmot banks | 4,648 | damaging rows only; inputs pending fidelity-engine decode |
| `wrestling` | WWF No Mercy mat-kings DB | 4,409 | named moves, Tekken inputs already wired by the wiring lane |
| `wmxix` | WWE WrestleMania XIX YANM clips | 169 | provisional labels — per-clip identity pending hash-set mapping |
| `doa` | DOA federation conversions (6 chars) | 146 | Tekken-notation federation rule applied |
| `vf` | VF federation conversions (akira/sarah/kage) | 48 | same |
| **pending** | vf5, t7, ttt2, t6, soulcalibur, urban_reign, bloody_roar, sf, def_jam | 0 | registered in index.json with status; vf5 format contract in `docs/handoffs/moveset-library-vf5-format.md` |

**Total: 9,420 moves.**

## Assembly model

A per-fighter manifest (`game/data/movesets/<fighter>.json`, `schema_version: 3`):

```json
{
  "fighter": "pablo",
  "base": { "bank": "vf5", "character": "el-blaze", "status": "pending-bank" },
  "moves": [
    { "library_id": "wrestling:mk-3517", "slot": "u/f+3",
      "overrides": { "name": "Pablo — Frog Splash Attempt", "properties": ["aerial","comedy-whiff-candidate"] },
      "note": "why this move is here" }
  ]
}
```

- Manifests **reference** library IDs — never copy move data. Swap = change the ID; edit = `overrides`; save = the JSON file (+ `assembly_version` bump).
- `game/js/moveset-library.js` `assembleFighter()` resolves a manifest to a v2 moveset: base kit (when its bank lands) + overlay moves on their slots + `pending` list + `source_law` verdict. Pending banks degrade honestly (`proxy: true`, base listed) instead of crashing.
- **Source law is code, not convention:** `checkSourceLaw()` maps T3 slugs to display names and refuses any pull from a claimed Tekken fighter (e.g. `t3:king:row:100` → refused, claimed by Pantera) unless an approved exception names the fighter. The browser UI surfaces the same check live.

## Pre-assembled fighters (locked Ashlane→VF5)

| Fighter | Base (pending vf5) | Overlay (real library moves, resolvable now) |
|---|---|---|
| **bannon** | vf5 jeffry | T3 Ogre heavies (r54, r57 — True Ogre FREE), Oklahoma Slam |
| **el-toro** | vf5 wolf | Asai Moonsault (one clean aerial — cleaner than Pablo), Super Powerbomb Pin 02 |
| **pablo** | vf5 el-blaze | Powerhouse (Oklahoma Slam, Brainbuster, Ogre r54) + comedy lucha attempts (Frog Splash, Shooting Star Press, Diving Moonsault — `comedy-whiff-candidate`) + dark thread (Black Reign Ride = Last Ride, Abyss Choke = Chokeslam from Hell — `dark-finisher`) |
| **npc-finxsse** | vf5 lei-fei | Counter-punch defensive answer (Lei-Fei's counter game) |

Pablo flavor (owner-locked, refined 2026-10-22): big/fat powerhouse who TRIES to be aerial — wants to be athletic, attempts lucha flyer moves anyway; comedy + heart (Goldust does the same thing). Underneath: Goldust theatricality mixed with dark Black Reign/Abyss/Mankind energy — disturbed masked darkness (matches his PABLO_blackreign variant). El Toro: powerhouse with slight aerial — lands his, the straight man to Pablo's comedy.

## UI

`game/moveset-browser.html` — standalone dev page (creation-suite hook-in documented for later; no other lane's files touched):
- Browse 9,420 moves by axis (type, position, hit level, property, bank), damage/startup ranges, text search; hide-estimated toggle.
- Move detail: input notation preview, frames, damage, anim_ref, provenance + estimated-field flags.
- Assembly panel: pick fighter (4 pre-assembled + New), attach selected move to a Tekken slot, rename overrides, detach, live source-law check, Save → downloads JSON + localStorage (commit the file to `game/data/movesets/`).

## Open items / not duplicating

- **#615 Tekken fidelity engine (merged):** owns runtime input→move fidelity + PSX controls. The library feeds it data; it does not reimplement the engine. T3 per-row input decode is its lane — library entries carry `input: null` + raw words until then.
- **Worker 45 (VF5 extraction):** format contract in `docs/handoffs/moveset-library-vf5-format.md` — read-only alignment, no edits to their lane.
- **T7/TTT2/T6/Soulcalibur/Urban Reign/Bloody Roar/SF/Def Jam:** banks registered as pending; ingest extends by adding a function + bank entry.
- **Creation suite moveset tab:** browser is standalone; wiring it into the suite is a follow-up that touches another lane's UI — documented, not done here.
