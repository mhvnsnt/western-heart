# TEKKEN-BASE MOVES MAPPING — Canon Fighter ↔ Tekken Base (Scaffold)

**Lane C scaffold — 2026-10-21 (teardown completion coordinator relaunch #4, attempt 2).**
**Status: SCAFFOLD ONLY.** No move data invented here. Data fill follows lanes A/B
(teardown decryption / extraction / decoding). Every section below is marked
`pending data from lane A/B` until decoded rows land.

**Owner order 2026-10-21 ~13:02 CDT, verbatim:** "Get the tear down done within the
repo off of local disk get to tear down decryption extraction decoding and all of
that other show so we can start pulling moves from it for some other characters
where it'll fit to some of our characters in the Canon."

**Owner rule:** Tekken = the content and the fighting. Tekken base names in this
document are **approved transitional scaffolding** — they are not claims about
what is "correct," and they are never "corrected" by any lane.

**TEMPLATE DIRECTIVE (owner 2026-10-21 ~15:04–15:08 CDT, verbatim core):** "put the
TEMPLATE SKELETON back on from the Tekken files, from the MOST RECENT Tekken game
we can get a hold of, FOR EVERYBODY." Lane A/B decodes must come from the most
recent available build per Tekken base (T8 > T7 > T6 > T3), and per-move rows must
state which build they were decoded from.

---

## 1. Moveset JSON schema for decoded Tekken moves

Follows the repo's existing conventions — **no renames, no removals, additive
only.** The base contract is schema v2, defined in
`docs/movesets/MOVESET-SCHEMA.md` (Lane F ↔ Lane H editor contract) and extended
by the T8/T7 source merges (`docs/movesets/SOURCE-MERGE-2026-10-21.md`).

### 1.1 Top-level fields (existing, unchanged)

| Field | Type | Notes |
|---|---|---|
| `fighter` | string | fighter id, matches filename (`game/assets/movesets/{id}.json`) |
| `display` | string | display name |
| `tekken_base` | string | Tekken base character (transitional scaffolding, never corrected) |
| `proxy` | bool | honest flag — true while riding another bank's data |
| `proxy_note` | string\|null | why it's a proxy, in plain words |
| `schema_version` | int | 2 = editor-contract fields present |
| `moves` | object | notation → move entry (§1.2) |
| `strings` | array | `{input, hits[], {game}_rows[]}` multi-hit strings |
| `specials` | array | motion-input specials the input buffer resolves |
| `frame_convention` | string | honest provenance, e.g. `T3 60fps -> seconds; damage scaled T3 170HP -> WH 100HP` |
| `{game}_source` | string | per-game provenance: `t3_source`, `t7_source`, `t8_source`, … |
| `union_merge` | object? | union-merge record where present (`era_note`) |

### 1.2 Per-move fields (existing, unchanged)

`name`, `input` (Tekken notation), `input_slots[]` (first = canonical),
`move_class` (`strike`/`throw`/`string`/`special`), `anim_ref`, `damage` (WH 100HP
scale), `startup`/`active`/`recovery` (seconds at 60fps), `limb`
(`armL`/`armR`/`legL`/`legR`), `heavy`, `knock`, `soulGain`,
`throw`/`isGrab`/`unblockable`, `{game}_source`/`{game}_row`/`{game}_command`/
`{game}_damage`, `t8_source`/`t8_id`, `merge_source`, `note`.

### 1.3 anim_ref registry (existing + teardown-decode addition)

Existing: `t3:{bank}:row:{n}` · `t7:{char}:row:{n}` / `t8:{char}:{id}` ·
`ttt2:{char}:row:{n}` · `t6:{char}:row:{n}` · `doa:{char}:{slug}` · `ur:{char}:{slug}` ·
`nomercy:{wrestler}:{slug}` · `wh:{fighter}:{slug}`.

**ADDITIVE (for lane A/B fill):** `decode:{game}:{base}:row:{n}` — a clip whose
bytes were decoded from the actual teardown files (decrypt → extract → decode),
NOT from a movelist dataset or wiki. `t3:`/`t7:`/`t8:` refs stay as-is for
movelist-derived rows; a row re-decoded from teardown bytes gets a `decode:` ref
alongside, never replacing the movelist ref.

### 1.4 Additive teardown-decode fields (PROPOSED — for lane A/B fill, scaffold only)

These fields do not exist in schema v2 yet. They are **proposed, additive**;
lanes A/B fill them, no existing field is renamed or removed.

Per-move additions:

| Field | Type | Notes |
|---|---|---|
| `decode_provenance` | object | `{teardown, source_file, offset_or_row, decoder, decoder_version, decoded_utc}` — byte truth, not wiki |
| `decode_build` | string | source build, e.g. `t8-retail`, `t7-retail`, `t6-psp-DATA401`, `t3-bank` (TEMPLATE DIRECTIVE: newest build available wins) |
| `raw_frames_total` | int | source-game frame count of the decoded clip |
| `raw_hit_start` / `raw_hit_end` | int | hit-active window in source-game frames (before WH scaling) |
| `fps_source` | number | source game fps (60) |
| `motion_ref` | string | decoded clip location, e.g. `banks/t7/king/row044.bin` (per-character namespaced, §4) |
| `raw_damage` | number | source-game damage, unscaled (parallel to the existing `t3_damage`/`t8_damage` pattern) |
| `note` | string | existing field — decode estimates and gaps go here, honestly |

Top-level additions:

| Field | Type | Notes |
|---|---|---|
| `decode_status` | object | `{lane, decoded_utc, rows_decoded, rows_pending, build}` — per-fighter decode ledger |
| `bank_binding` | string | anim bank the fighter's ACTION clips bind (informational). **Law: never edit `{game}_source` to change binding — `bankIdFor`/`FIGHTER_BANK` owns binding; `{game}_source` stays the data-provenance label.** |

**Gap note (honest):** schema v2 has no field for raw per-frame joint data or
decrypt/extraction provenance. §1.4 is the proposed shape; if lane A/B needs
more, it proposes additions in the data PR — never by renaming v2 fields.

### 1.5 Loader contract (unchanged)

`game/js/movesets.js`: `MOVESET_IDS` → `fetch assets/movesets/{id}.json`;
`getMove(fighterId, notation)` → `ms.moves[notation]`. Case carries meaning in
notation; the normalizer is whitespace-only by default. New fields must not
break the loader or the moveset editor (creation-suite reads these files
directly).

---

## 2. Canon mappings (all pending data from lane A/B)

Each entry: Tekken base (transitional, never corrected) → canon character
(fighter id + display), current file state on main (2026-10-21), status, notes.

### 2.1 Pantera ← King
- **Fighter id:** `pantera` · **Display:** PANTERA
- **Tekken base (transitional):** King
- **Current state:** `tekken_base: King`, `t3_source: king`, 873 moves (T8 +7,
  T7 +297, T3 +199 via SOURCE-MERGE-2026-10-21), 394 inputs, `proxy: false`
- **Status:** pending data from lane A/B
- **Notes:** needs raw King decode rows from the most recent available build
  (TEMPLATE DIRECTIVE). Per-move `decode:` refs + `decode_provenance` per §1.4.

### 2.2 Zui ← Steve Fox
- **Fighter id:** `zui` · **Display:** ZUI
- **Tekken base (transitional):** Steve Fox
- **Current state:** `tekken_base: Steve Fox`, **`t3_source: jin` (proxy)**,
  614 moves (T8 +171, T7 +287 via SOURCE-MERGE-2026-10-21), `proxy: false`
- **Status:** pending data from lane A/B
- **Notes:** T3 rows currently ride the Jin bank — the Steve Fox teardown decode
  must REPLACE those proxy rows with real Steve rows (newest build available),
  keeping every existing move key (no-loss rule). Mark replaced rows with
  `decode_provenance`; keep `proxy_note` honest until the last Jin row is gone.

### 2.3 Skull ← Bryan Fury
- **Fighter id:** `skull` · **Display:** SKULL
- **Tekken base (transitional):** Bryan Fury
- **Current state:** `tekken_base: Bryan Fury`, `t3_source: bryan`, 688 moves
  (T8 +6, T7 +266, T3 +141), `proxy: false`
- **Status:** pending data from lane A/B
- **Notes:** movelist-derived rows exist across T8/T7/T3; needs raw Bryan decode
  rows (`decode:` refs) from the newest available build.

### 2.4 Sam-ur-a1 ← Jack
- **Fighter id:** `samura1` · **Display:** SAM-UR-A1
- **Tekken base (transitional):** Jack
- **Current state:** `tekken_base: Gun Jack`, `t3_source: gunjack`, 860 moves
  (T8 +7 jack-8, T7 +298 jack-7, T3 +213 gunjack), `proxy: false`
- **Status:** pending data from lane A/B
- **Notes:** the transitional mapping base is **Jack** (never corrected). File
  currently records Gun Jack provenance — recorded here as fact, not as a
  correction. Needs raw Jack decode rows from the newest available build; Jack
  vs Gun Jack row identity is lane A/B's call, stated per-row in
  `decode_provenance`.

### 2.5 Doc Frank ← Bosconovitch
- **Fighter id:** `docfrank` · **Display:** DOC FRANK
- **Tekken base (transitional):** Bosconovitch
- **Current state:** `tekken_base: Bosconovitch`, `t3_source: bosconovitch`,
  380 moves (T3 +266 real Bosco rows via SOURCE-MERGE-2026-10-21, `union_merge`
  era census: T3=107, T8/WH-newest=7), `proxy: false`
- **Status:** pending data from lane A/B
- **Notes:** has the REAL T3 Bosconovitch command list; no newer-era full set
  exists yet — T7 Bosco decode is the priority fill. (Doc Frank's FORM files
  `doc-frank-hood/machine-shop/wowomomo` still carry `t3_source: gunjack`; bank
  binding is FIGHTER_BANK's lane, not this doc's.)

### 2.6 Cape Jones ← Alisa
- **Fighter id:** `cyborgx` · **Display:** CYBORG X (canon: Cyborg X IS Cape Jones)
- **Tekken base (transitional):** Alisa
- **Current state:** `tekken_base: Alisa`, `t3_source: gunjack`, 624 moves
  (T8 +6, T7 +284 alisa), `proxy: false`
- **Status:** pending data from lane A/B
- **Notes:** T7/T8 Alisa movelist data merged; needs raw Alisa decode rows from
  the newest available build. T3 rows currently ride Gun Jack — replace with
  real Alisa rows as decode lands (no-loss: keys kept, rows re-sourced).

### 2.7 Yukihyo ← Armor King
- **Fighter id:** `yukihyo` · **Display:** YUKIHYŌ
- **Tekken base (transitional):** Armor King
- **Current state:** `tekken_base: Armor King`, **`t3_source: king` (proxy)**,
  534 moves (T8 +173 armor_king, T7 +19 armorking), `proxy: false`
- **Status:** pending data from lane A/B
- **Notes:** T3 rows ride the King bank; T8/T7 Armor King movelist rows landed.
  Needs raw Armor King decode rows from the newest available build; replace King
  proxy rows with real Armor King rows, no-loss, per-row `decode_provenance`.

### 2.8 Burger ← Bob
- **Fighter id:** `burger` · **Display:** BURGER
- **Tekken base (transitional):** Bob
- **Current state:** `tekken_base: Bob`, **`t3_source: bryan` (proxy)**,
  552 moves (T8 +7 bob, T7 +281 bob), `proxy: false`
- **Status:** pending data from lane A/B
- **Notes:** T8/T7 Bob movelist rows landed; T3 rows ride the Bryan bank ("Bob
  has no T3 bank — Bryan proxy (power)" was the honest historical note). Needs
  raw Bob decode rows — T6 PSP DATA401 Bob / T7 Bob bank per the teardown lanes
  — to replace Bryan proxy rows, no-loss.

---

## 3. What lanes A/B must deliver (per character)

For each of the 8 fighters above, the decode lane delivers:

1. **Build identification** — which teardown build holds the canonical data for
   the Tekken base (newest available: T8 > T7 > T6 > T3), with file/offset
   references. Stated in `decode_provenance.teardown` + `decode_build`.
2. **Decoded move list** — per move: raw command, bank row/index, total frames,
   startup/active/recovery in source-game frames, raw damage, hit properties
   (mid/high/low, throw, unblockable), limb. → §1.4 fields.
3. **Animation clip references** — bank + row per move in
   `decode:{game}:{base}:row:{n}` format; clip bytes land per-character
   namespaced (§4), never in a shared pool.
4. **Strings/combos** — component hit sequences for the `strings[]` array.
5. **Throws/specials** — flags + inputs for `specials[]` and per-move throw flags.
6. **Frame/damage convention** — source HP scale and fps → WH mapping, written
   into `frame_convention` honestly (e.g. `T7 60fps -> seconds; damage scaled
   T7 170HP -> WH 100HP (x0.59)`). No guessed numbers — estimated fields get a
   `note`.
7. **No-loss guarantee** — every existing move key keeps a byte-identical
   payload; decode rows are ADDED or re-source existing keys with both refs
   kept (movelist ref + `decode:` ref). Union-first, like PR #407 and the
   2026-10-21 source merge.

---

## 4. Per-character isolation (owner standing law 2026-10-20)

**Owner law:** every character's skeleton, animations, and add-ons are separate
and stay separate. Per-character features live only on their own character's
data — never in shared state that can alter other characters. Repo layouts are
namespaced per character.

Rules for this mapping and all decode-fill work:

1. **One file per fighter.** Decoded rows land ONLY in
   `game/assets/movesets/{fighter_id}.json` of the owning canon character.
   There is no shared "teardown moves pool" file; this mapping doc references
   move data, it never holds move data.
2. **Decoded clips are per-character namespaced.** Bank clip paths follow
   `banks/{game}/{base}/…` (e.g. `banks/t7/king/row044.bin`); one character's
   decode never mutates another character's bank directory.
3. **No cross-character shared state.** `proxy`, `proxy_note`,
   `decode_status`, `bank_binding` are per-file. A fill for Pantera touches
   `pantera.json` and `banks/*/king/…` only — never `yukihyo.json`, even though
   both ride King-family data.
4. **Binding is per-fighter.** Animation binding is owned by
   `bankIdFor`/`FIGHTER_BANK` per fighter id; `{game}_source` stays a
   data-provenance label and is never edited to change binding.
5. **Additive only.** Schema v2 fields are never renamed or removed for decode
   fill; §1.4 additions are optional per move and ignored by readers that don't
   know them (loader + editor keep working).

---

## 5. Fill checklist (for the coordinator)

- [ ] Lane A/B delivers §3 items for **Pantera ← King** (`pantera.json`)
- [ ] Lane A/B delivers §3 items for **Zui ← Steve Fox** (`zui.json`) — incl. Jin-proxy replacement
- [ ] Lane A/B delivers §3 items for **Skull ← Bryan Fury** (`skull.json`)
- [ ] Lane A/B delivers §3 items for **Sam-ur-a1 ← Jack** (`samura1.json`)
- [ ] Lane A/B delivers §3 items for **Doc Frank ← Bosconovitch** (`docfrank.json`) — T7 Bosco priority
- [ ] Lane A/B delivers §3 items for **Cape Jones ← Alisa** (`cyborgx.json`) — incl. Gun Jack-proxy replacement
- [ ] Lane A/B delivers §3 items for **Yukihyo ← Armor King** (`yukihyo.json`) — incl. King-proxy replacement
- [ ] Lane A/B delivers §3 items for **Burger ← Bob** (`burger.json`) — incl. Bryan-proxy replacement
- [ ] Data PR opened by coordinator (six-section instruction-gate format, owner quote verbatim); NO PR from this scaffold lane
- [ ] Full-bank regression + engine check (`tools/moveset-merge/engine_check.mjs` pattern) before any fill merges
- [ ] Playtest proof: merged movesets must LOAD AND PLAY (proof-harness fight on merged data)

*Scaffold written 2026-10-21 by Lane C, attempt 2. No move data invented; all
current-state figures read from `main` 2026-10-21 (96-file moveset tree).*
