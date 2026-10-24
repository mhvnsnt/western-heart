# RE Battle Plan: Fire Pro Formulas + Destiny 2 Pipeline (2026-10-23)

**Owner directive (verbatim):** *"Find her way around that whole license code issue like bro it's a game that I own and we can reverse engineer the code and everything"*

**Authorization:** The user owns both games on Steam and explicitly authorizes full reverse engineering. This plan covers WHAT to reverse, HOW, and WHERE results go — with the legal firewall from `RE-MASTER-PLAN-2026-10-23.md` in force (techniques/formulas public; binaries/structs/assets stay in PRIVATE `mhvnsnt/game-reverse-engineering`).

---

## A. Fire Pro Wrestling World match-engine formulas (Steam app 564230)

### A.1 What we want
- **Hidden HP/SP resources** — the internal "stamina/spirit/breath" pools behind the visible health bar (body-part damage: neck/arm/back/leg feeds into these).
- **SP damage formula** — how move Damage-Stamina/Spirit/Breath numbers (already visible per move in Move Craft / Workshop listings) convert into SP depletion, and what SP depletion does to KO/pin probabilities.
- **Critical probability** — the per-hit "critical" roll function (critical flags exist per move: Finisher/Signature/Critical; the actual probability formula is engine-side).
- **Counter-window frames** — grapple/reversal timing windows in frames; strike-exchange window.
- **Referee AI** — count speed, when counts start/stop, count-failure conditions, ref positioning logic.
- **AI logic tables** — the 16-situations x damage-bands probability tables (front/back grapple, corner, running, ground positions, etc. x Sml/Med/Lrg/Critical) that drive CPU move selection.

### A.2 Where the formulas live in a 2D engine (head start, not guesswork)
Fire Pro World is a 2D-sprite engine with frame-based state machines. Unlike 3D engines where damage lives in physics code, here:
1. **A large part of the "formula" is designer data, already visible.** Move Craft exposes per-move damage vectors (Damage-Stamina, Damage-Spirit, Damage-Breath, body-part damage, Critical flag) — Workshop listings quote them verbatim (e.g. Tenha Seikou Zan: Stamina 28 / Spirit 08 / Breath 08). The hidden part is the *aggregation function* (how per-part damage becomes HP/SP) and the *probability functions* (crit roll, kickout roll, counter roll), which are engine code.
2. **Save-data side is partially known.** The `firepro.ajworld.net` Save Tool family documents edit/costume formats for Fire Pro Returns (PS2, not World) — useful as a Rosetta Stone for the data layout philosophy (packed bitfields per wrestler/move), but World's own formats need fresh RE. CarlZilla's **FPWW Mod Suite** (used across the Workshop for edit/CPU-logic work) already hooks the game at runtime — its module sources are the single best existing map of where wrestler/move state lives in memory.
3. **The binary is native x64** (not Unity/DotNet — strings analysis is the entry point, not IL decompilation). Float arithmetic for damage aggregation is likely inlined; probability tables may live as data (`.rdata` float arrays) or be computed.

### A.3 RE steps (ordered, cheapest first)

**Phase 1 — Harvest what's already public (no game files needed, ~days)**
- Scrape Steam guides on AI logic (e.g. the community AI & Moveset guide, app 564230 filedetails 973746385) for the 16-situation x damage-band structure and known thresholds (Sml/Med/Lrg/Critical transitions, ukemi sell mechanics, spirit-boost-on-ukemi rules).
- Read CarlZilla's Mod Suite sources for runtime struct layouts (wrestler state, move data) — this is the Rosetta Stone for Phase 2.
- Collect 50+ Workshop move listings with quoted damage vectors as a ground-truth dataset.

**Phase 2 — Binary triage on the real executable (needs game files, ~1–2 weeks)**
- `strings` sweep for situation names, critical-type labels, ref/AI debug strings — anchors into the code regions.
- Cross-reference strings → find the AI logic table loader; map the 16-situation x 4-band tables (look for arrays of probability weights, 16x4 or transposed).
- Hunt SP thresholds: float constants near known damage-band boundaries in `.rdata`; HP/SP aggregation functions near per-move damage reads.
- Counter windows: find grapple-state machine; count frames between "grapple contact" and "lock-in" (frame constants like 20/30/60).
- Deliverable (PRIVATE): address/offset map, table layouts, annotated pseudocode of each formula — never committed to public.

**Phase 3 — Differential empirical RE (no RE tools needed, runs in parallel, ~2–4 weeks)**
This is the reliable path where binary RE gets hard — and Fire Pro is ideal for it because the game is deterministic given identical inputs.
- Build pairs of test wrestlers identical except ONE stat (e.g. Critical 0 vs 100; Spirit 0 vs 10; a single move's Damage-Stamina swept 0/10/20/30).
- Run CPU-vs-CPU matches, 30–100 samples per condition, log: match length, number of crits, kickout points, move counts per situation.
- Fit: crit probability as function of (move crit flag, wrestler Critical param, damage band); SP threshold where "Critical" band logic kicks in; ukemi sell→HP-return amounts.
- Referee AI: measure count speed in frames across conditions (who's legal man, ref distance, interruptions) — this is pure behavior observation.
- Validate binary-derived formulas against empirical fits; where they disagree, trust the empirical data.

**Phase 4 — Runtime confirmation (optional, Mod Suite hooks)**
- Use Mod Suite's DLL-injection framework (or x64dbg breakpoints on the Phase-2 addresses) to read live HP/SP values mid-match and confirm the aggregation function directly. This collapses the hardest uncertainty (hidden resource values).

### A.4 Honest difficulty assessment
- **EASY (high confidence):** AI logic table structure and band thresholds — mostly designer data, partially documented by the community; Mod Suite sources likely already map most of it.
- **MEDIUM (achievable with effort):** Crit probability function, counter-window frames, referee AI timing — behavior is observable; formulas fittable from data. Expect 2–4 weeks of match-logging.
- **HARD (possible, not guaranteed):** Exact HP/SP aggregation internals (per-part damage → pool → KO check). The state machine is frame-ticked and the pools may be quantized in non-obvious ways (e.g. body-part damage as separate meters that sum). Differential RE gives the *effective* formula, which is all WH needs — but byte-exact engine replication is not guaranteed.
- **NOT NEEDED:** Sprite/animation formats, rendering. WH is 3D; we only want the *math and pacing*, which we re-implement originally in Tekken-style code.

### A.5 Private vs public (Fire Pro)
- **PRIVATE** `mhvnsnt/game-reverse-engineering`: offset maps, table dumps, binary pseudocode, empirical datasets, fitted constants.
- **PUBLIC** `mhvnsnt/western-heart` `docs/research/FIRE-PRO-FORMULAS-TECHNIQUE.md`: technique descriptions only — e.g. "crit probability scales with X and Y", "counter window is N frames", "SP thresholds at S/M/L/Crit bands" — expressed as WH's own re-implementation. No proprietary bytes, no decompiled functions.

---

## B. Destiny 2 data pipeline

### B.1 Phase 1 — Bungie API (PUBLIC, documented, NO RE needed)
Bungie ships a full public API with official docs: base URL `https://www.bungie.net/Platform/`, docs at `https://bungie-net.github.io/multi/index.html`. Requires a free API key (register an app at bungie.net — takes minutes, key goes through the secure connector flow, never in repo).

**Pipeline:**
1. `GET /Platform/Destiny2/Manifest/` → returns manifest with version + paths to JSON definition blobs (download, cache locally).
2. Key definitions for the creation suite:
   - `DestinyInventoryItemDefinition` — **armor pieces and shaders both live here** (shaders are inventory items; filter by `itemTypeAndName` / class type / armor slot). Fields: display properties, screenshots, stats, sockets.
   - `DestinyPlugSetDefinition` + socket/plug data — shader application slots, armor mod slots (the customization-system backbone).
   - `DestinySandboxPerkDefinition` / `DestinyTalentGridDefinition` — **subclass abilities** (supers, grenades, melees, aspects/fragments in later seasons via subclass plug sets).
   - `DestinyStatGroupDefinition` — armor stat display (Mobility/Resilience/Recovery/Discipline/Intellect/Strength).
   - `DestinyClassDefinition` — Titan/Hunter/Warlock.
3. This covers item *definitions, names, icons, stat values, plug relationships* — everything a customization/creation UI needs to present armor, shaders, and subclass choices. **All of Phase 1 is legitimate public API use; nothing to reverse.**

### B.2 Phase 2 — Tiger package extraction (what the community already knows)
**Status: the community already solved this — do not hand-roll a parser.**
- `v4nguard/tiger-pkg` (Rust, open source) implements the full Tiger package format across eras, including the **Destiny 2 Beyond Light format (header version 53)**: revised header, double-indirection 64-bit hash table, bit-packed `EntryHeader`/`BlockHeader` (type info, starting block, block offset, file size), block-based storage in 256KB blocks, AES-GCM block decryption, Oodle decompression. It also covers D1 and Marathon. DeepWiki docs walk the structs file-by-file (`d2_beyondlight/structs.rs`, `d2_shared.rs`).
- **Plan: vendor `tiger-pkg` as a library/dependency, don't reimplement.** Build a small extraction CLI on top of it targeting the asset classes we need (armor meshes, textures, shader parameter blocks).
- **What remains genuinely unknown:** which package/tag IDs correspond to which armor/shader assets (the API gives definitions + icon hashes, but mapping definition hash → package tag requires the manifest's content paths and experimentation), and the per-asset formats (mesh vertex layouts, material/shader parameter blocks) — these need struct-level RE against known assets. Standard approach: extract a known simple asset, correlate with its API icon/definition, then map neighboring tags.
- **Keys:** tiger-pkg's `Version` trait ships the standard AES keys/nonces used across modern Bungie titles — no key RE needed on our side.

### B.3 Private vs public (Destiny 2)
- **PRIVATE:** anything extracted from `.pkg` files (meshes, textures, shader blobs, tag maps), API-downloaded definition JSON used as raw data.
- **PUBLIC:** the *technique* writeup — how the API manifest pipeline works, how plug sets model customization, how WH's original implementation consumes definition-style data. No extracted assets, no definition JSON committed verbatim (transform/attribute as needed).

---

## C. File flow (shared with master plan)
1. **Credentialed machine** (Steam-logged): DepotDownloader pulls Fire Pro (app 564230) + Destiny 2 depots → pushes to PRIVATE `mhvnsnt/game-reverse-engineering` (git-lfs for binaries).
2. **This VM:** clones private repo → runs RE → writes technique docs → original re-implementations → pushes technique docs + code to PUBLIC `western-heart`.
3. **Never:** game files, decompiled code, or extracted assets on the public repo.

## D. What needs game files (blocked until pull)
- Fire Pro x64 executable + data (Phase 2 binary work, Phase 4 hooks).
- Destiny 2 `.pkg` files (Phase 2 extraction experiments only — Phase 1 API work needs NO game files and can start immediately).

## E. Sequencing recommendation
1. **Start now, no files needed:** Destiny 2 Phase 1 (API key + manifest + armor/shader/subclass definition pipeline) and Fire Pro Phase 1 (community docs + Mod Suite source reading) + Fire Pro Phase 3 test-wrestler construction (the user can build these in-game; the differential protocol is ready to run the moment matches can be logged).
2. **After depot pull:** Fire Pro Phase 2 (binary), Destiny 2 Phase 2 (tiger-pkg extraction experiments).

## F. Deliverables checklist
- [ ] `docs/research/FIRE-PRO-FORMULAS-TECHNIQUE.md` (public) — crit/SP/counter/referee/AI-logic techniques, WH re-implementation notes.
- [ ] `docs/research/DESTINY2-API-PIPELINE-TECHNIQUE.md` (public) — API manifest pipeline, plug-set customization model, WH consumption design.
- [ ] PRIVATE: offset/table maps, empirical datasets + fitted formulas, tiger-pkg tag→asset maps, extraction scripts.
- [ ] WH-side: original implementations (Fire Pro-inspired match pacing module; Destiny-inspired armor/shader/subclass customization data model).
