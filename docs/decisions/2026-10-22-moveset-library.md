# 2026-10-22 — Moveset Library System (worker 47)

## What was built
Central, organized moveset/animation library + per-fighter assembly system, per the owner's standing directive (MOVESET LIBRARY SYSTEM, 2026-10-22).

- **Library: 9,516 moves, 6 live banks** (`game/data/moveset-library/`): Tekken 3 (4,648 damaging rows, 20 banks), WWF No Mercy mat-kings (4,409 named moves, Tekken inputs wired), WMXIX (169 clips), DOA federation (146), VF federation (48), **VF5 federation (96 — vf-elblaze/jeffry/wolf/leifei, live base kits)**. 8 more banks registered as pending (vf5-motion, t7, ttt2, t6, soulcalibur, urban_reign, bloody_roar, sf, def_jam).
- **Organization axes** (`axes.json`): type / position / orientation / hit_level / properties / Tekken input / frames / damage — every entry tagged, every estimate flagged in `provenance.estimated`.
- **Assembler** (`game/js/moveset-library.js`): manifest → v2-contract moveset (same shape `game/js/movesets.js` reads). Enforces the **moveset source law in code** (`claimed-map.json`): refuses pulls from claimed Tekken fighters (tested: `t3:king:row:100` refused — claimed by Pantera; `t3:ogre:row:54` allowed — True Ogre FREE).
- **Per-fighter manifests** (`game/data/movesets/`): reference library IDs, never copy. The four locked Ashlane→VF5 mappings assemble against the LIVE vf5 bank: **bannon** 28 moves (vf5 jeffry 25 + Ogre heavies/Oklahoma Slam), **el-toro** 23 (vf5 wolf 21 + clean Asai Moonsault + Super Powerbomb), **pablo** 36 (vf5 el-blaze 28 + powerhouse + comedy-whiff lucha attempts + Black Reign Ride / Abyss Choke dark thread), **npc-finxsse** 23 (vf5 lei-fei 22 + counter-punch).
- **UI** (`game/moveset-browser.html`): browse 9,420 moves by axis, inspect (input notation preview, frames, provenance, estimated flags), attach/detach to a fighter, rename overrides, live source-law check, save (download + localStorage).

## Pablo canon (locked, applied in `game/data/movesets/pablo.json`)
Big/fat powerhouse who TRIES to be aerial — wants to be athletic, attempts lucha flyer moves anyway; comedy + heart (Goldust does the same thing). Underneath: Goldust theatricality MIXED with dark Black Reign/Abyss/Mankind energy — disturbed masked darkness (matches PABLO_blackreign variant). Assembly: El Blaze base (pending) + powerhouse layer (Oklahoma Slam, Brainbuster, Ogre heavy) + ambitious lucha attempts (Frog Splash, Shooting Star Press, Diving Moonsault — `comedy-whiff-candidate`, whiff frames canon) + dark thread (Black Reign Ride = Last Ride S-tier, Abyss Choke = Chokeslam from Hell — `dark-finisher`, read as the mask slipping, not comedy). El Toro is the straight man: one clean aerial, lands it.

## Decisions
- T3 per-row Tekken inputs are NOT decoded in the library (branch target slots need the slot table) — that's the #615 fidelity engine's lane. Library entries carry `input: null` + raw `state_word`/`attack_word`; **assembly assigns the slot**. This is the editor workflow, not a gap.
- Schema is additive over the v2 moveset-editor contract — no v1/v2 field renamed/removed; the assembler projects entries to v2 moves.
- No duplication of #615 (runtime fidelity) or worker 45 (VF5 extraction): coordination via this log + `docs/handoffs/moveset-library-vf5-format.md` (read-only, their files untouched).
- Browser is a standalone dev page; wiring into the creation suite's moveset tab is a follow-up in that lane's UI (documented, not done here).
- Ingest is reproducible: `node tools/moveset-library/ingest.mjs` (WH_REPO_ROOT override for any checkout).

## Proof
- `node --check` clean on all three JS files.
- Ingest run: 9,516 entries, 0 schema/type violations; all 9,516 carry estimated-field flags.
- Assembler CLI: pablo 36 moves / bannon 28 / el-toro 23 / npc-finxsse 23, all source-law clean, vf5 bases live (no pending banks).
- Source-law unit check: claimed pull refused, free pull allowed (see above).
