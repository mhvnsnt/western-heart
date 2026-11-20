# 2026-10-22 — Bannon universe canon package + teardown fighter inventory (worker 49)

## What was done
Built the two reference documents the Bannon-universe round needs, from primary sources
(no invention — every claim traces to a repo file):

1. **`docs/research/bannon-universe-canon-package-2026-10-22.md`** — the consolidated raw-material
   canon package for all 28 Bannon/Ashlane fighters (identity / character / moves / bones /
   hitboxes per fighter). Sources: `mhvnsnt/Bannon` ("Off The Top Rope cast and characters"
   Book 3 master roster, 41 characters); `mhvnsnt/brutalfistgrokversion`
   `native/media/characters/chara_bannon/` (identity/character/moves/bones/hitboxes TXT template,
   pulled verbatim); `mhvnsnt/brutalfistgrokversiontenpointfive` `src/data/bannonRoster.ts`
   (27 full profiles: bio, personality, style, stats, 19-slot defaultMoveSet),
   `src/data/canonPronouns.ts`, `public/models/` (model-variant inventory);
   `mhvnsnt/AshLane-prototype` (SOMBRA_NEGRA, 28th fighter).
2. **`docs/research/teardown-fighter-inventory-2026-10-22.md`** — master per-game → per-fighter
   asset inventory: movesets (format + location), animations (format + location), voice, audio,
   models, textures for T3, T7, T6, TTT2, T8, VF5, DOA4, DOA6, SC2, SC6, SF EX2+, SF EX+α,
   Urban Reign, WWF No Mercy, WMXIX, WWE 2K (catalog), Def Jam FFNY, Bloody Roar (not landed),
   Eastern Mind (not a fighter source), plus the wrestling CAW part libraries.
3. **`docs/owner-directives.md`** — appended the Bannon sub-universe law (owner directive from
   this round).

## Decisions / judgments made
- Canon package covers the 28 MODEL fighters (27 in bannonRoster.ts + Sombra Negra), NOT the
  41 Book 3 story characters — the other 13 are story-only (no models) and are cross-referenced
  by alias only. The doc states this boundary explicitly so worker 48 doesn't bridge ghosts.
- Canon bridges are worker 48's lane — this package is raw material only. Noted in-doc.
- Bones/hitboxes are documented once as the shared template (23-bone Mixamo map, procedural
  hitboxes) rather than repeated 28×, since the sources confirm they don't vary per fighter.
- T3 divmot bank list (20 fighters) and the "7 fighters mapped" geometry note are both kept —
  they measure different things (anim banks vs extracted geometry).
- Def Jam FFNY counted at 142 FIGHTER.XML entries → 78 base models (not "40 fighters") per the
  teardown doc; the exact name list lives in FIGHTER.XML, not yet dumped to docs — flagged as
  a gap, not filled by guessing.
- WMXIX identities stay PENDING owner visual ID (only Triple H confirmed) — no invented names.
- GitHub API went rate-limited mid-task (403, shared PAT quota exhausted by concurrent crew
  workers). Research continued via HTTPS git (sparse checkout) + unauthenticated raw CDN —
  different mechanism, not a retry. PR creation/merge deferred: see WORKLOG entry.

## Open gaps (for follow-up lanes)
- Bannon fighters' kits beyond `defaultMoveSet` are unauthored in the sources (moves.txt has
  only Jab/Heavy) — the teardown banks in the inventory doc are the fill path (worker 47).
- Buffalo Bill / Ashes + the wizard gang: not located in any repo (owner to say where they live).
- SOMBRA_NEGRA has no bannonRoster.ts profile (bio/stats/moveset unauthored) — Book 3 alias
  data captured in the package.
- Bloody Roar teardown hasn't landed. WWE 2K is catalog-only. DOA4 fighter identities unmapped.
  SF EX2+ OVL slots unnamed. Urban Reign char001–072 unnamed.
