# WORKLOG — Burger Kusaregedo Kit (2026-10-19)

## Task
Wire Youkai Kusaregedo's full kit into Burger per owner 2026-10-19 ~18:41 CDT.
Owner confirmed Samurai Shodown (not Onimusha) is the right source.

## Sources (NO-GUESSING compliance)
- Frame data: https://dreamcancel.com/wiki/Samurai_Shodown_VI/Kusaregedo (Tekitogate)
- Powers/story: https://snk.fandom.com/wiki/Youkai_Kusaregedo
- Research doc: ~/workspace/burger-kusaregedo/KUSAREGEDO-MOVESET.md
- All startup/active frames are real SamSho VI data (60fps -> seconds).
- Damage scaled to WH 100HP. Kusaregedo's fixed grab % preserved.

## Files
- `game/assets/movesets/burger-demon.json` (NEW): 24 moves, 8 specials. Full kit + form-mix + 2 exclusives.
- `game/assets/movesets/burger-speed-demon.json` (NEW): 12 moves, 3 specials. Quick moves.
- `game/assets/movesets/burger-the-mouth.json` (NEW): 12 moves, 3 specials. Head/bite.
- `game/js/movesets.js` (EDIT): registered 3 IDs in MOVESET_IDS.
- `game/js/roster-full.js` (EDIT): Burger `forms` block — chain base -> speed-demon -> the-mouth -> demon.
- `roster/burger/ATTIRE-SLOTS.md` (EDIT): documented per-form movesets + chain.

## Per-form distribution
- **Demon (final)**: FULL kit (7 signatures + 16 normals) + smaller-form abilities
  (demon-dash, rapid-bites, mega-chomp, head-slam, hungry-eyes, feral-rend)
  + exclusives (INFINITE HUNGER ultimate, Gaki's Feast armor stance).
- **Speed Demon**: Flying Head Butt (up/down), Quick Palm, Speed Boot, Backflip + speed kit.
- **The Mouth**: Huge Headbutt, Mega Chomp, Head Slam, Tongue Lick/Sweep, Maw of Hunger.

## Verification
- All 3 JSONs: schema_version 2, valid JSON, fighter IDs match filenames.
- `node --check` passes on both edited JS files.
- `git status`: 3 modified + 3 new, zero deletions (anti-clobber check clean).

## Follow-ups (not in this PR)
- Mini Tank form (model pulled 2026-10-19): needs its own moveset + chain slot.
- New form models (speed-demon, the-mouth) not yet wired to roster/ — Tripo pulls exist in ~/workspace/tripo-recovery/.
- Bob's full Tekken moveset for Burger base (separate lane).
- Kusaregedo animation clips: anim_ref points to samsho:kusaregedo/ — clips to be built from footage.
