# Decision log — CORNERSTONE moveset (2026-10-22, worker 68)

## Locked by owner (~18:07 CDT)
- Display name is **CORNERSTONE** (capital C, capital S). "Ryuji Rock" was the
  working name. Internal id stays `ryuji-rock`; only the name the player sees
  changes.
- Full spec: Ryuji Yamazaki base (3D KOF) + The Rock + Younger Toguro's
  spammable thumb flick blast, all on Tekken inputs with 1:1 input-to-move
  fidelity. Assembled through the moveset library (worker 47's format).

## Decisions taken in this build
1. **YYH: Dark Tournament teardown = research teardown.** No game files exist in
   the holdings and no crew PS2 pipeline exists for this title. The complete
   kit (moves, inputs, spirit-energy costs, combo damage) was documented from
   the published GameFAQs FAQ + US manual + wiki — sourced, never invented.
   File-level motion extraction is flagged as future work, not faked.
2. **No acquisition duplicated.** Worker 59's KOF3D lane did not cover Yamazaki;
   I decoded his XV list from published sources in w59's exact format.
3. **King T3 proxy removed.** The old `ryuji-rock.json` used T3 King rows as a
   proxy — King is claimed by Pantera per the moveset source law. Replaced by
   the real Yamazaki kit (also fixes the law violation).
4. **Pit Viper input corrected** (`qcb,qcf` → `qcb,hcf`, XV-verified), noted in
   the move entry.
5. **XV vs classic versioning:** XV Todome (hcb,f+K) and classic downed-finisher
   Todome coexist as separate entries; Serpent Slash's qcf→qcb flip recorded;
   Knife Slash kept as legacy (absent from XV, owner explicitly listed it).
6. **Thumb Flick Blast wiring:** `qcf+1`, hold-to-repeat, 12f recovery —
   spammable like the anime; damage scales with Increase Strength (80%), mirroring
   the source game.
7. **Library integration without touching worker 47's files.** New banks
   (`kof3d`, `yyh`, `wwe-rock`) and the manifest added; `index.json`
   registration left for #678/#699's merge (snippet documented in the manifest
   and research doc).
8. **`ryuji` (pure Yamazaki) slot untouched** — only `ryuji-rock` changed.
9. **MERGE FREEZE honored:** branch pushed, PR opened, reported merge-ready —
   not merged (task instruction overrides the repo's merge-it-yourself law).

## Naming question resolved
`docs/owner-directives.md` "Open naming questions" listed
`'ryuji' (RYUJI) vs 'ryuji-rock' (RYUJI ROCK hybrid): two slots, distinct
concepts — needs owner call on whether they merge.` Owner call 2026-10-22:
`ryuji-rock` displays as **CORNERSTONE**; `ryuji` stays pure Yamazaki. Both
slots remain.
