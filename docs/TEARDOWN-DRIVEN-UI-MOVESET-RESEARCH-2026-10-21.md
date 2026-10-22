# TEARDOWN-DRIVEN UI + MOVESET EDITOR — RESEARCH (2026-10-21)

**Owner directive (2026-10-21 ~20:35 CDT, verbatim core):** "don't just follow
every exact thing it says. Do actual real research because you might find
something better and a better way to use the actual files we have to set it up
that's not just guessing and hallucinations... do real research to find out how
to use the real Tekken files to set all this up and don't just listen to the way
it explains it — find real ways and do real research to use the actual teardown
files and everything we have to set this up and not hand tooling bullshit...
don't just listen to Gemini's small research and narrow hallucinations."

**What this doc is:** an evidence-first audit of (1) what UI/menu/moveset data
actually exists in the teardown holdings, (2) which of the pasted Gemini
architecture blocks' load-bearing claims survive contact with those files and
with published sources, and (3) the file-driven setup the evidence supports —
engine-agnostic, because the engine verdict is being researched separately.

**The owner's governing design (his own words, locked 2026-10-21 ~20:32 CDT):**
almost-Tekken organization (input matrix 1/2/3/4 × directionals, strings with
follow-ups, WS/WR states, clinch-context grapples) with FULL WWE-depth
per-input moveset customization, tap-to-assign (never drag-and-drop), the
animation library drawn from ALL teardown sources (Tekken, WWE 2K, Def Jam,
Urban Reign, No Mercy, WMXIX), live test on a dummy in the viewport, on mobile.
The pasted blocks' restricted compromise (pick an archetype, swap only four
modifier slots, "you cannot edit every single punch") is **rejected** by that
statement and is not used anywhere below.

**Method + honesty notes:**
- Local evidence was read on `mhvnsnt/western-heart` main @ `3173b0c`
  (2026-10-21 evening) via the GitHub API; the recursive tree listing
  truncated at 60,888 entries, so absence claims below are made only where a
  direct path listing confirmed them.
- **Numbers rule:** every count in this doc is copied from a named repo audit
  or file that was actually read. No count comes from the pasted text. Where
  two repo sources disagree, both are printed and the drift is named.
- Web verdicts cite published sources (URLs in §2). Claims that no source
  could confirm are marked UNVERIFIED, not smoothed over.

---

## 1. File inventory — what the holdings actually contain

### 1A. western-heart (main)

| # | Asset | Location | Format | Decoder / tool status | What it can directly drive |
|---|-------|----------|--------|----------------------|----------------------------|
| 1 | TKM2 moveset decoder | `tools/moveset-decode/tkm2_decode.py` + `README.md`; vendored upstream `tools/open-source/tkmovesets/` (TKMovesets2, Kiloutre, GPL-3.0) | `.tkmvst` (TKMovesets2 extraction container) → JSON | **Works, spec-validated only.** Full inner decode for the T7 layout; container decode for T5/T6/TTT2/TREV/T8 gameIds. Validated by a spec-built fixture round-trip (62/62 field checks, 2026-10-20) — **no real `.tkmvst` sample exists on this machine yet** (README states the search evidence). `.mvl` movelist block and MOTA contents are reported by size, **not parsed**. | Per-move name, animation name, startup (`first_active_frame`), active window, `anim_len`, damage (via `hitCondition`), hit level, hitbox location, cancel index — the raw material of a command list and of editor slot validation. |
| 2 | Tekken 3 motion banks | `teardown/tekken3/movesets/moveset_<char>.json/.csv` + `MOVESET-SUMMARY.md` | Decoded bank rows (JSON/CSV) | **Works.** 20 banks extracted with the verified USA table addresses; King = 652 rows (summary table, all 20 banks listed). Parser: `tools/local/moveset_extract.py` (per summary). | Each row carries `stream_frames`, `damage`, `attack_class`, `active_first/last`, `stance_slot`, and **`branches[]`** — the cancel/string graph as data: `{command, target_slot, first/last frame window, restriction, condition}`. This is the string builder and the follow-up system, already decoded. |
| 3 | Moveset generator | `tools/gen-movesets-t3.py` | Python | **Works** (per `docs/TEARDOWN-INTEGRATION-AUDIT-2026-10-19.md`): walks each bank's branch graph (Dijkstra over decoded input commands → canonical Tekken notation, strings, conditioned variants) and merges full depth over the curated fighter files. | Proof that the editor taxonomy can be *generated* from bank data — the generator already does the graph walk the editor needs. |
| 4 | WH fighter movesets | `game/assets/movesets/*.json` (schema v2) | JSON, **`moves` is a dictionary keyed by the input string itself** (`"1"`, `"d/f+2"`, `"1+3"`, `"2,1"`, …) | **Live game data.** Spot-check (Pantera, read 2026-10-21): 873 input-keyed entries; each carries `name`, `input`, bank provenance (`t3_source`, `t3_row`), `startup/active/recovery`, `damage`, `limb`, `move_class`, `anim_ref` (`t3:king:row:44`), `input_slots`; `strings[]` are explicit follow-up chains (`input` → `hits[]` + bank rows). | **The editor's slot list already exists as data**: the union of input keys across these files *is* the Tekken input matrix, with provenance and frame data attached. An assignment is a repointing of one key to another `(bank, row)` / `anim_ref`. |
| 5 | Moveset coverage audit | `docs/MOVESET-COVERAGE.md`, generated by `tools/moveset-coverage/moveset_coverage.py` | Generated markdown | **Generated, now drifting.** Audit figures: **85 fighter files, 7,294 base moves (+318 strings/specials = 7,612)**; 15 FULL-REAL / 37 FULL-BANKED / 30 REAL-THIN / 3 PROXY. But the `game/assets/movesets/` directory listing read the same evening shows **101 entries** (fighter files + shared bank files such as `moveset_king.json`), and spot-checked files have since been expanded (Pantera 873 input keys vs the audit's 125-move bank row). **The audit needs a regeneration run** — see §4. | The citable roster/move counts until regenerated; also the FULL-REAL vs FULL-BANKED distinction (own bank vs assigned teardown bank) the editor's library browser must show honestly. |
| 6 | WWE-depth slot taxonomy | `moveset-library/movesets/MOVE-SLOTS.json` | JSON | **In repo, documented.** Template is the **WWF No Mercy move-slot layout** (sourced from the No Mercy re-docs), extended with Tekken striking slots: **176 total slots** (per the file's `_meta`). Grappling is context-keyed exactly as the owner's clinch design requires — front weak/strong grapple × `{grapple, dir+grapple, up+grapple, down+grapple, strike, …}`. Assignment chain: `slot → move_id → anim_id` (No Mercy: `anim_id = file_id − 0x3322`) → clip. | The editor's category tree for the wrestling/clinch half — derived from a real game's own slot structure, not invented. Joins to #4's input-keyed Tekken half by slot/input. |
| 7 | Cross-game animation library index | `moveset-library/animations/ANIMATION-INDEX.json` + `WMXIX-CLIP-INDEX.json` | JSON index over decoded clips | **In repo.** No Mercy: **5,762 clips** decoded (`.npy` int16, AKI joint layout; 4,409 move clips, 1,353 system clips; manifest at `teardown/wwf-no-mercy/animations/manifest.json`). WMXIX: **170 clips** (JSON per clip, 70-bone Yukes skeleton). T3: all 20 divmot banks + common bank, SHA-256-verified (2026-10-20). | The editor's animation library browser: searchable, provenance-carrying clip inventory across sources. Depth is uneven (No Mercy deep, WMXIX shallow) — see §4. |
| 8 | Existing moveset editor spec | `docs/MOVESET_EDITOR_SPEC.md` + `moveset-library/MOVESET-EDITOR-RESEARCH.md`, `UI-DESIGN-SPEC.md`, `MOVES-LIBRARY.md` | Markdown specs | **Already file-grounded.** The spec's categories come from `MOVE-SLOTS.json` (#6); its Tekken slot data from the T3 banks (#2); saves are per-attire versioned files (`roster/<id>/movesets/<attire>_vN.json`, never overwrite); the editor is merged with Practice (edit → live in the running fight; command list + input display always on); every move keeps `source` + `third_party` flags; frame data "comes from the bank, not typed by hand." | The build contract this research refines (§3) — it already obeys the owner's design; nothing in the pasted blocks improves on it. |
| 9 | Creation-suite parts registry | `customization/PARTS-REGISTRY.json` (+ `CUSTOMIZATION-JSON-SCHEMA.md`, `PARTS-INDEX.json`) | JSON registry | **In repo.** **1,148 parts** (count read from the file itself). Per part: `id`, `kind`, `library`, `asset`, `part_class`, `editable[]` (e.g. position/size/opacity), `placement`. `suite_slots`: 21. Converted part GLBs on disk include rigged/skinned variants (e.g. `customization/parts/accessories/chains/*_rigged.glb`). **The "4,523 parts" figure is not supported by this file** and should not be cited. | Item grids generated by filtering the registry on `kind`/`library` — no hand-authored item lists. The `editable[]` field is what generates each part's adjust controls. |
| 10 | Tekken 6 customization data | `customization/parts/tekken/tekken6-item-names.json`; `wh/teardown/tekken6/ui/` (per `docs/CREATION-SUITE-UI-V2-2026-10-21.md` survey) | JSON name records; NTXL string tables | **Structure/text real; art locked.** **9,440 item-name records** from the decrypted bulk; **120 NTXL UI string tables** (including the games' own prompt texts — "Select item to equip.", "Purchase item?", the hair-conflict prompt's exact words); customization classes in the decrypted EBOOT (`tcb_customize_mode_t`, `CUSTOMIZEPACK%d_%d`, `sbcustomize_item_t`). **Absent: every panel/frame/cursor/font texture** — UI art sits in containers that still fail to decode (56 of 76 GZIP containers; 0 GIM textures carved, per the v2 survey). | Category names, item names, prompt wording, and pack structure from the real game. **No pixel layout or positions exist for any Tekken game in the holdings** — see claim C1. |
| 11 | Tekken 7 customization schema | Documented in `docs/CREATION-SUITE-UI-V2-2026-10-21.md` §1 (from tekkenmods documentation) | Documented schema | **Documented, sprites incoming via the W6 lane.** 16-slot schema, `SlotGroupID` menu order (−254…−236), 21-field item record, conflict rules. | The category spine and item-record shape for the suite — from the game's documented data model, not from screenshots. |
| 12 | Roster data | `game/js/roster-full.js`; audit `docs/MODEL-KEY-AUDIT-2026-10-21.md`; `game/data/tripo-fighters.json` (generated by `tools/roster/tripo_fighters.py`) | JS/JSON | **Audited.** The model-key audit executed the game's real resolution chain over **58 roster entries**: 33 OWN / 10 BASE-BY-DESIGN / 13 WRONG→FIXED / 2 no-model. The select screen's data source comment states tripo-fighters.json ordering is generated, "no hand-picked order." | The character grid's data source and the only citable roster count. |
| 13 | Character select (current game) | `game/js/select-screen.js` | JS | **Data-driven with hand-tuned grouping.** The grid is generated from `deps.roster()` — but the section split is hard-coded slice ranges (roster[0:9] "THE NINE SOULS", [9:16] "MAIN ROSTER", [16:] "BONUS ROSTER", plus a Tripo-originals filter). | Mostly file-driven already; the grouping should read roster metadata fields instead of positional slices (§3, R5). |
| 14 | Stage data + thumbnails | `game/js/stages.js`; `game/assets/stages/{eastern-mind,no-mercy,t3,sf-ex,sunra,thumbs}/`; `tools/stage-arena-pull/{convert_nomercy,render_gallery,reskin_stage}.py`; `teardown/ARENA-INVENTORY.md` | Hand-written JS registry + decoded stage geometry + PNG thumbnails | **Data exists; no single stage index.** stages.js header (read 2026-10-21): 8 canon Eastern Mind lands + 15 Tekken 3 retro arenas built from real teardown geometry (`teardown/tekken3/stages/<letter>/`), with per-stage texture atlases decoded from the real stage texture ARCs. No Mercy: **17 arena assemblies wired as playable stages** (integration audit 2026-10-19; its stage smoke test: **41 stages, 0 duplicate ids**). `game/assets/stages/thumbs/` holds **41 thumbnail files with 41 distinct blob SHAs** (verified from the git tree 2026-10-21) — per-stage thumbnails exist and are all different images. | **The owner's identical-thumbnail screenshot is a UI wiring failure, not missing assets**: the select screen is not consuming the per-stage thumbs that already exist. Stage select should be generated from a stage index built over these sources (§3, R4). |
| 15 | Def Jam (in western-heart) | `teardown/def-jam-fight-for-ny/` | Findings doc + `ANIMTAGS.DAT` | **Thin in this repo**: an animation-findings doc and the tag data; no decoded move/animation library here. The full Def Jam teardown lives in its own repo — see §1B. | Not yet an editor library source from this repo alone. |
| 16 | Urban Reign | `teardown/urban-reign/` (3,166 blobs incl. `animations/motion-packs/*.ppk`) | Raw PPK motion packs; ROSTER.json (72 fighter models, per integration audit) | **Extracted ~95%, semantics NOT decoded** (integration audit): motion packs are raw; models are raw PPK geometry needing conversion. Kronos' Urban Reign (Golem) mix-in currently rides the King bank (FULL-BANKED rows in #5). | A named gap (§4): UR moves cannot be first-class editor entries until the PPK motion semantics decode lands. |
| 17 | WWE 2K CAW | `customization/wwe2k-caw/` (`CAW-STRUCTURE-2026-10-19.md`, `CAW-SUITE-BREAKDOWN.md`, `PARTS-CATALOG.md`, `MOVESET-LIBRARY-2026-10-19.md`, `COMBINED-CREATION-SUITE.md`, `AUDIT-2026-10-19.md`) + converted parts under `customization/parts/` (incl. No Mercy CAW faces) | Structure docs + converted part assets | **Structure documented; parts converted** (registry #9 is the consumable form). No WWE 2K moveset *binary* decode is claimed by these docs — the moveset side of WWE enters via the No Mercy slot layout (#6) and the WMXIX clip index (#7). | Suite structure reference (layering, parts catalog) rather than a move-data source. |
| 18 | Frame-data fetchers | `tools/fetch_wavu_framedata.py`, `tools/fetch_t7chicken_framedata.py` | Python | **In repo.** Community frame data (Wavu/TekkenDocs lineage) is structured: 15-field records — Command, Hit level, Damage, Start up frame, Block/Hit/Counter-hit frames, Notes, Tags, Transitions, Name, Recovery, Image, Video (TekkenDocs format documentation). | The command list's frame columns for T7/T8-era data, complementing the banks' native fields (#1, #2). |
| 19 | Suite front-end v2 | `docs/CREATION-SUITE-UI-V2-2026-10-21.md`; build in `packages/creation-suite/ui2/` | File-derived UI build | **Built from the file surveys** (Tekken-frontend + WWE/Def Jam-frontend inventories): v2 keeps v1's data layer and rebuilds presentation from the games' front-end files/structure — the standing answer to the owner's 2026-10-21 rejection of the hand-tooled v1. | The suite's current implementation baseline; §3's recommendations extend it rather than replace it. |

### 1B. game-reverse-engineering repo + on-disk teardown trees

### 1B. game-reverse-engineering repo + on-disk teardown trees

Audited read-only on disk 2026-10-21 (checkout `~/workspace/gre-p9r/` of
`mhvnsnt/game-reverse-engineering`, plus `~/workspace/teardowns/`,
`~/workspace/wwe2k-teardown/`, `~/workspace/defjam-repo/`,
`~/workspace/western-heart-movesets/`, `~/workspace/wh-teardown-research/`).

**GRE checkout — thin, with one working pipeline.** The checkout holds 7
markdown docs + `soulcalibur/`; the `tekken/`, `tekken3/`, `tekken6/`,
`tekken7/` directories its docs reference are **not in this checkout**. Its
`TEARDOWN-STATUS.md` (updated 2026-10-19) is the scoreboard: Tekken 3
"7 fighters, 15 stages, 8,556 textures, 3,247 moves" (the 3,247 is exactly
the 7-bank row total in §1A #2's summary: 652+449+594+413+365+383+391);
No Mercy "5,787 anims, 3,570 models, 5,029 textures, 17 arenas" — note the
anim count differs from the WH animation index's 5,762 clips (§1A #7): two
artifacts, two counts, neither reconciled here; WMXIX "~80%, 126 wrestler
OBJs, 170 YANM anims, 2,690 CAW parts"; SCII "24 movesets, 371 textures,
125 models, 577 anims."

| Asset | Location | Format / status | What it can drive |
|-------|----------|-----------------|-------------------|
| SCII animation-bank decoder | `soulcalibur/tools/bankdec.py` (Ghidra-derived, docstring: byte-exact) + `motion-db/`, `motion-tracks/` (decoded per-frame tracks for Mitsurugi + Taki only) | **Works** for the two fighters present; tools hard-code paths outside the checkout, so they don't run from the repo alone | Move preview data; a worked decoder pattern |
| SCII moveset converter | `soulcalibur/tools/movesets_convert.py` | **Partial**: SCII type-7 command files (48-byte records: `name[32]` + 4×u32) → per-fighter moveset JSON with a **mechanical SC2→Tekken input map (A→1, B→2, K→3, G→G)**; its own header states the display-string ↔ cmd-record pairing table (type-8/10 sections) is **not yet decoded**, so move names can't yet be reliably paired to records | A second in-house precedent (besides #3) for mapping a foreign game's command records onto the Tekken matrix mechanically |
| SCII fighter models | `soulcalibur/models/*_fighter_placed.glb` (28) via `tools/build_skinned.py` + VMX pipeline | **Works** (outputs present) | Select/customization preview models |
| Tekken data in GRE | — | **Absent as data**: `tekken-model-catalog.md` / `tekken-missing4-catalog.md` are external free-model link catalogs; `CHIMERA-BUILD.md`'s Tekken claims (T7 ID tables, "34 stages", No Mercy "98 faces, ~150 ring attires, positional move slots front/back × weak/strong × 8") are prose whose underlying files are **not in this checkout** — unverifiable from GRE, superseded by the WH-repo data in §1A | Nothing directly; do not cite GRE prose counts over §1A files |

**On-disk trees:**

| Tree | Contents that matter | Status |
|------|---------------------|--------|
| `teardowns/` | 5 prose design teardowns (Fight Club, Sleeping Dogs, Warriors, Yakuza, SA Turf War) | **Narrative only** — no move/CAW/stage data, no decoders. Drives nothing. |
| `wwe2k-teardown/moveset-library-2k19.txt` | WWE 2K19 move-name library: **5,581 lines** (wc-verified), string-table extraction from `pac/root/createmode*.pac`; categorized counts in `MOVESET-LIBRARY-2026-10-19.md`: Strikes 1,171 / Grapples 795 / Submissions 230 / Diving 203 / Running 77 / Corner 62 / Apron 28 / Uncategorized 2,856; per-wrestler motion pacs: 17 wrestler IDs, 7,449 move entries | **Names/IDs complete; animations NOT decoded** (`.pac` HSPC container + `.YANM` blobs untouched; the 51 GB game pull never landed, so `pac/edit/` CAW part library is absent from disk). Drives a move-library *browser* (names + categories + slot→move-ID mapping), not playback. |
| `wwe2k-teardown/CAW-STRUCTURE-2026-10-19.md` | WWE 2K19 CAW structure: 8 editors; layered attire (part ID + color/pattern + material, up to 8+ attire slots); morph sliders; base templates at slot 256 (male) / 257 (female) | **Structure only** (string tables extracted; part binaries absent). Corroborates §1A #17's suite structure reference. |
| `defjam-repo/` (checkout of `mhvnsnt/def-jam-fight-for-ny`) | `AGENTS.md` + `lane-logs/` only | **Effectively empty** — no teardown data, moves, venues, or tools in this checkout. Combined with §1A #15: **Def Jam move data is not decoded in any audited location**; checkpoint statuses (§C of the audit) report lanes "done" while the sweep checkpoint simultaneously says "blocked" — see the caution below. |
| `western-heart-movesets/` | An **older standalone checkout** with its own copies: 45 moveset JSONs (vs 101 entries on current main), the same 7 T3 banks (3,247 rows, counts verified identical to §1A #2), 20 T8 frame-data JSONs sourced from wavu.wiki (CC0 — reference data, **not a teardown decode**), `teardown/ARENA-INVENTORY.md` (sourcing matrix: T7 34 stages ID-mapped, TTT2 29 documented, Urban Reign 7 stage PPKs, **VF5 18 arenas extracted** — the largest ready stage pool for R4 expansion) | **Stale copy — cite current main (§1A), not this tree.** One exhibit matters: its `game/js/roster-full.js` header still reads **"36 named fighters"** — a stale header in an old copy is a plausible laundering path for the "36 fighters" figure the owner keeps flagging (C9). The current-main audit count is 58 (§1A #12) and governs. Also: this copy references `MOVE-SLOTS.json` without containing it; on current main the file exists (§1A #6) — one more reason §1A is the citation base. |
| `wh-teardown-research/` | One empty directory | Nothing. |

**Caution on checkpoint statuses (from the audit, adopted here):** the
agent-ops checkpoints for these games mostly read `"done"` even where the
underlying docs say the decode is partial or blocked (T6, WMXIX semantics,
Def Jam). A checkpoint `status` is a **lane-completion flag, not a
decode-completion flag** — this doc cites file contents and audit docs for
decode state, never checkpoint statuses.

**Count discrepancies found while auditing (printed, not smoothed):**
(i) No Mercy animations: 5,762 clips (WH `ANIMATION-INDEX.json`) vs 5,787
anims (GRE `TEARDOWN-STATUS.md`). (ii) Tekken 6 item names: 9,440 item-name
records (WH v2 front-end survey, §1A #10) vs the T6 customization research
doc's name-table format "verified across 10,495 records" — plausibly records
vs extracted item names, but the two artifacts don't say, so both stand as
printed. (iii) Moveset files: 85 audited (§1A #5) vs 101 current directory
entries vs 45 in the stale on-disk copy.


---

## 2. Claim check — the pasted blocks vs files and published sources

Verdict key: **VERIFIED** (source confirms), **REFUTED** (source or file
contradicts), **REFINED** (a real mechanism, misstated), **UNVERIFIED** (no
source found — treat as guess).

### C1. "Tekken 8 customization = fixed 25% left column / 75% viewport, 3-column grid, color panel expands footprint to ~40%"
**UNVERIFIED as Tekken 8 fact — and not derivable from our files either.**
No authoritative source publishes those proportions. The Tekken Wiki and
Bandai Namco's official customization page describe *content*, not layout
geometry: slots for full body, head, glasses, upper body, lower body, shoes,
and 2 accessories; per-part color; accessory size/position adjustment;
characters **standing** (not in fighting stance) on the customization screen;
a default white shirt/jeans look when unequipped. No 25/75 split, column
count, or 40% figure appears in any located source. Locally, the v2 front-end
survey (§1A #10) is blunt: **no pixel layout or positions exist for any Tekken
game in the holdings** — T6's UI art is locked in containers that still fail
to decode. So the proportions in the paste are eyeballed from footage. They
may be a reasonable *design target* — and the owner's own suite law (researched
T8 proportions, no panel covering the fighter preview, portrait-first) governs
regardless — but they must be **measured from captures** before being called
Tekken 8's layout, and the slot list in the paste ("Full Body, Upper, Lower,
Head") is incomplete against the documented slot content above.
Sources: [tekken.fandom.com/wiki/Customize](https://tekken.fandom.com/wiki/Customize) ·
[tk8.tekken-official.jp/en/mode/customize.php](https://tk8.tekken-official.jp/en/mode/customize.php)

### C2. "BoneAttachment3D snaps a selected clothing mesh to the skeleton"
**REFUTED for skinned clothing (this was already flagged to the owner).**
Godot's docs define `BoneAttachment3D` as copying/overriding the transform of
**one** bone — the whole child follows rigidly; the canonical examples are a
held weapon or a cloak pin point. It performs no skinning or deformation.
The documented skinned route is a `MeshInstance3D` bound to a `Skeleton3D`
via its `skeleton` NodePath + a `Skin` resource, vertices weighted across
many bones. Notably, **our own pipeline already follows the documented-correct
pattern**: suite parts ship as rigged/skinned GLBs (§1A #9, e.g. the
`*_rigged.glb` chains). The paste's mechanism would produce exactly the rigid,
body-detached clothing the owner keeps rejecting.
Sources: [docs.godotengine.org BoneAttachment3D](https://docs.godotengine.org/en/4.4/classes/class_boneattachment3d.html) ·
[MeshInstance3D](https://docs.godotengine.org/en/4.2/classes/class_meshinstance3d.html)

### C3. "Assign in UI → write JSON → at runtime inject the animation into an AnimationNodeOneShot in the AnimationTree"
**REFINED — the pattern is real, the stated mechanism is wrong in two places.**
Runtime assignment is supported, but animations live in the `AnimationPlayer`:
`add_animation_library()` and `AnimationLibrary.add_animation()` are runtime
APIs. An `AnimationNodeOneShot` **holds no animation** — it fires the
sub-animation connected to its `shot` port via
`parameters/OneShot/request = ONE_SHOT_REQUEST_FIRE`; it is an
`AnimationNodeAnimation` (a `StringName` reference) that points at a library
animation. AnimationTree node resources are **shared between all instances**
unless duplicated/made unique, so naive runtime mutation leaks across
characters. And Godot does not load JSON into a tree by itself — parsing and
applying the file is application code. Correct shape: JSON → load/create
`Animation` resources → add to the character's library → point state/
`AnimationNodeAnimation` nodes at them → drive playback via parameters.
Engine-agnostic note (§3, R7): WH's existing data design already avoids this
whole class of problem — assignments are data (input key → `anim_ref`), not
mutations of a shared animation graph.
Sources: [AnimationTree tutorial](https://docs.godotengine.org/en/latest/tutorials/animation/animation_tree.html) ·
[AnimationPlayer](https://docs.godotengine.org/en/4.1/classes/class_animationplayer.html) ·
[AnimationNodeAnimation](https://docs.godotengine.org/en/4.4/classes/class_animationnodeanimation.html) ·
[AnimationNodeOneShot](https://docs.godotengine.org/en/stable/classes/class_animationnodeoneshot.html) ·
[Godot forum: dynamically changing AnimationTree animations](https://forum.godotengine.org/t/how-to-go-about-dynamically-changing-the-animation-in-an-animation-tree/54557)

### C4. "Morph sliders drive Skeleton3D.set_bone_pose_scale() (No Mercy bone scaling)"
**VERIFIED as an API; REFINED as a design claim.** `set_bone_pose_scale(
bone_idx, scale)` exists in the Godot 4 class reference alongside
`set_bone_pose_position/rotation`. The docs present it as a pose-transform
component, not a morph/blend-shape system — using it for proportion morphs is
a legitimate application, not a documented morph feature. In WH's own data,
morphs already live as data (`customization/body-morphs/`, `face-morphs/`)
under the customization JSON schema — whichever engine renders them, the
*morph definitions* are file data, and No Mercy's actual CAW body-scaling
ranges should be taken from the No Mercy data/docs, not invented slider
ranges.
Source: [Skeleton3D class reference](https://docs.godotengine.org/en/4.4/classes/class_skeleton3d.html#properties)

### C5. "MK11: universal base kit + 3 ability slots, moves cost 1–2 slots"
**VERIFIED with a nuance the paste missed.** Documented: three slots; custom
abilities cost 1 or 2 slots — and, in rare instances, **all 3** (e.g.
Kollector's are listed at costs on SuperCombo; Deep Freeze listed as
"2 Slots"). The structural claim (base kit + slotted customs) is right. It is
also **moot for WH**: the owner's locked design is full per-input
customization, not a point-buy loadout; MK11's system is a *restriction*
mechanism, and importing its slot economy would water the editor down exactly
as he rejected.
Sources: [gamerevolution MK11 tournament-mode guide](https://www.gamerevolution.com/guides/666947-mortal-kombat-11-how-to-use-custom-moves-in-tournament-mode) ·
[SuperCombo MK11/Kollector](https://wiki.supercombo.gg/index.php?title=Mortal_Kombat_11/Kollector) ·
[gamerstemple MK11 Ultimate review](https://www.gamerstemple.com/featured-review/switch/1607/mortal-kombat-11-ultimate-review)

### C6. "WWE 2K24 moveset editor = situation-based tabs (Standing, Ground, Corner, Ropes, Apron, Diving, Signatures, Finishers)"
**VERIFIED in kind, incomplete in count.** Create-A-Moveset's documented
sections are situation-based — Standing actions, Standing, Grounded, Corner,
Ropes, Apron, Diving/Aerial, Running, Tag Team, Finishers (with signatures
inside Finishers). But for WH the better source is already in the repo: the
slot taxonomy was torn down from **No Mercy's own move-slot layout** and
extended with Tekken striking slots (§1A #6, 176 slots) — a real game's data
structure we hold in full, versus a feature list of a game we don't.
Source: [smackdown.fandom.com/wiki/Create_A_Moveset](https://smackdown.fandom.com/wiki/Create_A_Moveset)

### C7. "Tekken has no moveset customization; characters have rigid 80–120-move lists; swapping strikes would break frame data"
Descriptively true of shipped Tekken — and **irrelevant as a design veto**.
The research-relevant fact runs the other way: the Tekken modding community
extracts complete per-character movesets into structured data. Kiloutre's
TekkenMovesetExtractor (the upstream of our own decoder, §1A #1) exports
movesets from the running game; TekkenDocs stores per-character movelists as
structured records (Command, Hit level, Damage, startup, block/hit frames,
Transitions, …). In other words, in Tekken's own data model a move **is** a
record keyed by its input command with frame/property fields and transition
links — which is precisely the shape WH's decoded banks (#2) and fighter
files (#4) already have. Per-input reassignment is a data operation on that
model; "Tekken doesn't ship an editor" is a product fact, not a data
constraint.
Sources: [TekkenMovesetExtractor](https://gitmemories.com/Kiloutre/TekkenMovesetExtractor) ·
[TekkenDocs CSV format](https://deepwiki.com/pbruvoll/tekkendocs/4.1-csv-data-format-and-fields)

### C8. "Clinch via a Master/Slave FSM (as built for AshLane)"
**UNVERIFIED as a claim about our codebase; SUPPORTED as a data shape.**
No source in the paste or the surveyed WH docs documents an existing
"Master/Slave FSM" — that phrase should not be repeated as fact. What the
files do support: grapples are **context states with their own slot tables**
in the real data — No Mercy's slot layout keys grapple follow-ups by context
+ direction (§1A #6), and T3 bank rows carry `condition`/`restriction` fields
on their branches (state-dependent transitions are bank data, §1A #2). The
Def Jam/Urban Reign clinch the owner wants is therefore implementable as:
enter clinch state → the four buttons rebind to the context's slot table →
paired clips play from the library index. Paired-attacker/defender animation
sync is an animation-data property (wrestling move clips were authored as
paired performances), not something a hand-built FSM invents.
Local sources: §1A #2, #6, #7.

### C9. "Your 36 (or 50+) canon fighters"
**REFUTED — the known Gemini hallucination the owner named.** The repo audits
say: **58 roster entries** (model-key audit, §1A #12) and **85 audited
moveset files / 7,294 base moves** (coverage audit, §1A #5; the census lane's
sheet supersedes when it lands). Any architecture sized to "36" — grid
dimensions, archetype lists, slot counts — is sized to a fiction. This is why
§3 derives every enumeration from the data files at build time instead of
constants.

### C10. "Select grids of thumbnails" as the Tekken pattern
**REFINED.** Data-driven select grids have a documented precedent — M.U.G.E.N's
`select.def` literally generates its character/stage select from data lines,
with the motif defining grid geometry — and data-bound grid generation is the
standard tutorial pattern (Noesis). For shipped Tekken specifically, "the grid
is generated from roster files" is **UNVERIFIED** publicly (internals aren't
documented) — cite M.U.G.E.N and our own roster-driven grid (§1A #13), not
Tekken, for the generation claim. What *is* Tekken-documented is the content
model the grid displays (C1).
Sources: [M.U.G.E.N character select via select.def](https://umatechnology.org/how-to-add-mugen-characters-on-mugen/) ·
[M.U.G.E.N stages](https://itstillworks.com/12420809/how-to-add-mugen-stages) ·
[Noesis character selector tutorial](https://www.noesisengine.com/docs/4.0/Gui.Studio.Tutorial_CharacterSelector.html)

### C11. "Floating color panel / decal drag / test-anim footer" (paste's suite mechanics)
**MIXED, mostly already governed by owner law + repo spec.** The mechanics
themselves (palette overlay, decal placement sliders, in-viewport move test)
match the owner's locked shell spec and the repo's editor spec (§1A #8
already merges the editor with Practice for live testing). Two paste details
conflict with standing law and are rejected: (a) decal placement by
**touch-drag across the model** is fine *for decals* (the owner's own TTT2
decal spec specifies it) but the **moveset editor's assignment flow is
tap-to-assign, never drag-and-drop** — the paste blurs that line; (b) any
overlay footprint that covers the fighter preview violates the owner's
three-times-stated preview law regardless of what percentage a paste assigns
it (C1).

---

## 3. Recommended file-driven setup (engine-agnostic)

Each recommendation names the file evidence it stands on. None of these
require hand-authored trees, hard-coded counts, or invented layouts; each is a
*generator over data we already hold*, plus the few decoders §4 names.

**R1 — The moveset editor's slot taxonomy is generated, not authored.**
Build the editor tree from two joins over repo data:
(a) the **Tekken half** = the union of input keys across all files in
`game/assets/movesets/` (§1A #4) — every key is a real slot that real decoded
data uses, grouped by parsing the notation (base button × directional prefix
× state prefixes WS/WR, exactly the owner's matrix); and
(b) the **wrestling/clinch half** = `MOVE-SLOTS.json` contexts (§1A #6).
The generator is a small extension of tools that already exist:
`tools/gen-movesets-t3.py` already walks bank branch graphs into canonical
notation (#3), and `tools/moveset-coverage/` already enumerates the fighter
files (#5). *Better than the paste because:* the paste hand-authors a command
tree and an archetype list from memory; the files produce the true tree,
including slots a human would forget (conditioned variants, motion inputs
like `b,n,f+1+2`, chain throws), and it can never drift from the data as new
banks land.

**R2 — Strings and follow-ups render the bank branch graph.**
A move's follow-ups are its bank row's `branches[]` (T3, §1A #2) / cancel list
(TKM2 `cancel` structures, §1A #1), each with its frame window. The editor
shows follow-up slots *because the data has branches there*, validates
mechanically (target exists; window inside `anim_len`/stream frames), and
never lets a user "create" a string the data can't express. The existing
editor spec's slot schema already mirrors this (#8) — build to it.

**R3 — Assignment = repointing, with provenance kept.**
An editor assignment rewrites one input key's `(bank, row)` / `anim_ref` in
the fighter's moveset JSON — the format the game already consumes (#4) — and
records `source` + `third_party` per the editor spec (#8). Saves stay
per-attire, versioned, never overwrite (`roster/<id>/movesets/<attire>_vN.json`).
Cross-game moves are therefore not a special feature: a Def Jam or Urban
Reign clip becomes assignable the moment it exists in the animation index
(#7) with a bank/row identity, on the same footing as a T3 row. (Today that
means No Mercy and WMXIX clips are first-class; Def Jam/UR become so when
§4's decoders land — honestly labeled in the library browser as
FULL-REAL / FULL-BANKED / REAL-THIN, reusing the coverage audit's vocabulary,
#5.)

**R4 — Stage select is generated from a stage index; the art already exists.**
Generate one `stages index` (JSON) from the three real sources: the stages.js
registry data (canon lands + T3 retro arenas built from teardown geometry),
the No Mercy arena set, and `game/assets/stages/thumbs/` (§1A #14). The index
carries per stage: id, display name, source game, description, thumbnail
path, builder key. The select screen renders *the index* — scrollable grid,
preview tracking the highlight, description inside the layout — so the class
of failure in the owner's 2026-10-21 screenshots (same thumbnail on every
card, banner/preview mismatch, unreachable stages, no confirm path) becomes
impossible by construction: 41 stages, **41 distinct thumbnails already on
disk**, and a generated grid has no hand-maintained subset to clip. The arena
render pipeline (`tools/stage-arena-pull/render_gallery.py`) is the thumbnail
source for any stage missing one.

**R5 — Character select grouping reads roster metadata, not slice positions.**
The grid is already roster-generated (§1A #13); replace the hard-coded
`[0:9]/[9:16]/[16:]` section slices with fields on the roster entries
themselves (soul/vessel class, provenance from the model-key audit #12,
Tripo-original flag from the generated `tripo-fighters.json`). A roster that
grows from 58 entries then needs zero UI edits — the paste's hard-sized
"36 (or 50+)" thinking (C9) is designed out.

**R6 — Suite categories and item grids come from the games' own schemas.**
Category spine = T7's documented `SlotGroupID` menu order + 16-slot schema
(#11) merged with T6's real category/prompt text (#10) — names and conflict
prompts in the games' own words where we hold them. Item grids = filters over
`PARTS-REGISTRY.json` by `kind`/`library` (#9); each part's adjust controls
are generated from its `editable[]` list; morphs render from
`body-morphs/`/`face-morphs` data (C4). Proportions and preview-protection
follow the owner's suite layout law (researched T8 measurements — which, per
C1, still have to be *measured*, since no source publishes them and no file
holds them).

**R7 — Keep assignments as data; never mutate a shared animation graph.**
Whichever engine wins the separate verdict, hold the line the current data
design already draws: movesets/customization are JSON documents consumed at
load; the runtime builds per-character state from them. C3 documents how the
paste's "inject into a shared AnimationTree" fails in Godot specifically
(shared resources across instances); the same failure class exists in any
engine with shared animation assets. Per-character instances built from data
files are the portable pattern.

**R8 — The command list is generated from the same files the editor edits.**
Practice mode's command list, frame meter, and input display (editor spec
#8) render from the fighter's moveset JSON + bank frame fields — startup/
active/recovery are bank data (#1, #2), never typed. When T7/T8-era frame
data is needed, the Wavu/TekkenDocs-shaped fetchers (#18) are the pipeline.
Longer term, the TKM2 `.mvl` block (§4, G2) is the games' *own* displayable
movelist format — parsing it lets even the *presentation* of the command list
come from the extraction, not from our formatting choices.

---

## 4. Gaps — missing data/decoders, and what unblocks each

| # | Gap | Evidence | Unblock |
|---|-----|----------|---------|
| G1 | **TKM2 decoder unproven on real data** — validated by spec fixture only; no real `.tkmvst` exists on this machine | §1A #1 (README's own limits) | One real extraction on a Windows/game machine (T7) → decode → diff against the TKMovesets2 editor output. Then the T7 pipeline is proven, not argued. |
| G2 | **`.mvl` movelist + MOTA contents unparsed** in `tkm2_decode.py` (sizes reported only) | §1A #1 | Extend the decoder next to the T7 layouts (the vendored headers define the blocks); unblocks R8's from-the-game command-list presentation. |
| G3 | **Native inner layouts unimplemented** for T8/TTT2/T6/T5 extractions (container decodes; inner structs stop with an explicit message) | §1A #1 | Add each game's table-entry sizes + `Move` layout beside the T7 one (vendored `Structs_t8/ttt2/t6/t5.h`). TTT2 matters most — it is the owner's named customization source. |
| G4 | **No Tekken UI pixel geometry exists in holdings** — T6 UI art locked (56/76 GZIP containers fail; 0 GIM textures carved); T7 sprites incoming via W6 | §1A #10, #11; C1 | Two tracks: (a) the container/GIM decode work (teardown lane), (b) measure T8 proportions from captures and record them *as measurements* in the shell spec. Until then, no percentage may be cited as "Tekken 8's layout." |
| G5 | **Def Jam move data not decoded in any audited location** — WH repo holds a findings doc + `ANIMTAGS.DAT` (§1A #15); the `def-jam-fight-for-ny` checkout holds only lane logs (§1B); lane checkpoints disagree ("done" vs sweep "blocked") and are lane flags, not decode state | §1A #15; §1B | Locate the actual Def Jam extraction outputs (they are not in either audited repo), land clips + move records in an `ANIMATION-INDEX`-style artifact, then Def Jam entries become first-class in the editor library like No Mercy's. |
| G6 | **Urban Reign motion semantics undecoded** — PPK packs raw; models unconverted | §1A #16 | PPK motion RE + PPK→GLB conversion lane (integration audit's ordering). Until then UR's editor presence stays bank-mediated (Kronos pattern), labeled as such. |
| G7 | **WMXIX shallow + arena faces undecoded** — 170 clips indexed vs No Mercy's 5,762; arena OBJs are vertex-only point clouds (faces in undecoded YMG) | §1A #7; integration audit | YMG face decode (existing lane) + continued clip indexing. |
| G8 | **Coverage audit is stale** — 85 audited fighter files vs 101 current directory entries; expanded files outgrew audited counts | §1A #5 | Regenerate `tools/moveset-coverage/` output; extend the same run to emit R1's editor taxonomy artifact so the editor tree and the audit can never drift apart again. |
| G9 | **No stage index data file** — stage knowledge is split across a hand-written JS registry, arena folders, and a thumbs directory | §1A #14 | The R4 generator (small, deterministic, diffable in PRs like every other generated artifact in this repo). |
| G10 | **T6 movesets/models blocked upstream** on DATA401/DATA214 decryption | Integration audit (§1A, source doc) | The existing decrypt lane; not a UI/editor blocker — T6's *customization text/schema* (#10) is already usable. |

---

## 5. Bottom line for the build lanes

1. The pasted blocks' **information architecture** (Tekken-organized,
   WWE-deep) agrees with the owner's locked design — but their
   **implementation claims** are wrong or unproven at almost every load-bearing
   point (C1, C2, C3, C9), and their restricted editor contradicts the owner
   outright (C5 note, §0).
2. Everything the owner's design needs already exists as data or as a working
   tool in the holdings: input-keyed movesets with provenance (#4), decoded
   string/cancel graphs (#2), a real game's 176-slot taxonomy (#6), a
   5,762-clip cross-game animation index (#7), a 1,148-part registry (#9),
   per-stage thumbnails for all 41 stages (#14), and an editor spec that was
   already written against those files (#8).
3. The work is therefore **generators and two decoder extensions** (R1–R8,
   G2/G3/G8/G9) — not a hand-built UI on a pasted blueprint. Where the files
   genuinely run out (G1, G4, G5, G6), this doc says so and names the lane
   that unblocks it, instead of letting a plausible-sounding paste fill the
   hole.
