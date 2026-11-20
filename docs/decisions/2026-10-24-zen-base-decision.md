# Zen = Eleven/Twelve/Dural + own canon, NOT Heihachi, NOT Julia

Owner decision, 2026-10-24. This resolves the Zen conflict flagged in PR #1016
("roster says Heihachi, FIGHTER_BANK says Julia, CANON.md appendix lists
Julia -> NIGHTWOLF / soul ZEN as an unresolved three-way conflict").

## Owner decision (verbatim intent)

> "Zen's base is neither of those. Zen is like 11 and 12 but not just a copycat
> he has his own moves he has all these different things that go with him and
> to his character and his canon so his thing is completely built off of that
> and like a little bit of copy X but like not really copy X"

## Why Dural (addendum, owner 2026-10-24, verbatim)

> "Dural was the closest thing to 10 or 11 in a 3D game, that's what it came
> down to"

Eleven/Twelve are 2D Street Fighter shapeshifters. Dural (Virtua Fighter 5)
is the closest 3D character that does the same thing — a chrome humanoid
that mimics other fighters. Dural is therefore NOT a separate pick: it is
the 3D stand-in for Eleven/Twelve.

## The base chain (read this before touching Zen)

```
Eleven / Twelve (SF, 2D concept: shapeshifting mimicry)
  -> Dural (VF5, 3D implementation: chrome humanoid, closest 3D thing to Eleven/Twelve)
    -> Zen's OWN canon moves on top
```

- **Base concept:** Eleven/Twelve (SF shapeshifters, mimicry).
- **3D base:** Dural (VF5, chrome humanoid, mimics VF fighters).
  Dural's stance is Zen's stance (permanent layer, owner 2026-10-22);
  Twelve's dancing idle stance is added ON TOP once converted 2D->3D.
- **Plus:** Zen's OWN moves, OWN canon attacks, OWN fighting style.
- **Plus:** A little X.COPY (Twelve's copy super) as ONE super, NOT his identity.
- **Plus:** Tentacle Mode, Oversoul, transformation, spirit-form stand (canon).

## Corrected FIGHTER_BANK entry

`game/js/fighter.js`, `bankIdFor()` / `FIGHTER_BANK`:

```js
// zen: null = UNMAPPED (owner decision 2026-10-24). A null value is intentional:
// hasOwnProperty('zen') is true, so bankIdFor returns null before any Heihachi/Julia
// fallback can bind. Do NOT restore 'julia' or 'heihachi' here without a new owner decision.
tou: 'paul', gyou: 'hwoarang', zen: null, rave: 'lei',
```

- **Before:** `MOVESET_MAP zen: 'heihachi'` AND `FIGHTER_BANK zen: 'julia'`
  (two different wrong bases at once — that was the conflict).
- **After:** `FIGHTER_BANK zen: null` (UNMAPPED). `bankIdFor('zen')` returns
  null, so Zen falls back to embedded locomotion + procedural combat —
  never another character's clips (the function's own documented rule).
- **Why null and not 'dural':** NO Dural bank exists in the repo. Checked:
  no `game/assets/anim/vf5/` directory, no `dural` key in
  `game/js/t3anims.js` `SOURCE_TO_BANK`, no Dural bank in
  `game/assets/anim/t3/`. Binding a bank that does not exist would be a
  guess, and the repo's NEVER-guess rule forbids it.
- **Why Heihachi/Julia are both wrong, not just one:** Heihachi is Diablo's
  base (CANON.md: Heihachi→DIABLO); Julia is Nightwolf's base (CANON.md
  appendix: Julia→NIGHTWOLF; roster/zen/CANON.md owner 2026-10-22:
  "Zen can't use Julia's moves ... night wolf uses Julia's moves").
- **MOVESET_MAP note:** the `zen: 'heihachi'` line in `MOVESET_MAP` is
  kept, now labelled in-line as INTERIM frame-data provenance ONLY (the
  639 interim rows in `zen.json` genuinely are Heihachi rows). It is not
  Zen's bank and must not be read as his base. The FIGHTER_BANK null
  short-circuits it in `bankIdFor()`.

## Zen's true moveset (additive, never mixed)

`game/assets/movesets/zen.json`, new top-level key `wh_true_moveset`
(25 entries). The interim 639-move Heihachi `moves` map is untouched;
the two sources are NEVER mixed (rule from
`docs/anim/VF5-DURAL-ANIM-GAP-20261023.md`, kept).

| Category | Count | Entries |
|---|---|---|
| Eleven/Twelve (Twelve moves) | 10 | N.D.L., A.X.E., A.X.E. (Air), D.R.A., H.U.G., F.L.G., T.R.W., B.M.K., Kokkuu, Kabe Haritsuki |
| Super (non-copy) | 2 | X.N.D.L., X.F.L.A.T. |
| X.COPY (ONE super, not identity) | 1 | X.C.O.P.Y. — Tekken-style input `d, d/f, f, d, d/f, f+LP1+RP2` (`d, d/f, f, d, d/f, f+1+2`); copies opponent briefly; does NOT grant the opponent's EX/super moves (SuperCombo) |
| Zen canon signatures (from the 188 canon-moves file, quoted verbatim) | 2 | Does Not Compete (`b+LP1+RP2`, armL / 15 / 15f), Refused Seat (`LP1+RP2`, armR / 16 / 17f) |
| Tentacle Mode | 3 | Pastel ink blast, Razor beam, Pastel wave — all NEEDS-INPUT |
| Oversoul | 1 | Oversoul combined-form attack — NEEDS-INPUT (no named Oversoul attack exists in docs; none invented) |
| Transformation (documented triggers) | 4 | TENTACLE MANIFESTATION (up), OVERSOUL (up), WITHDRAW (down), OVERSOUL RELEASE (down) — TRANSFORM touch + full nine-soul meter, multipliers from `roster-full.js` |
| Spirit-form stand | 2 | Spirit-form stand attack, Spirit side-switch — both NEEDS-INPUT |
| **Total** | **25** | |
| Eleven distinct moves | 0 | Eleven (SFV) has NO own moveset — it randomly morphs into another character pre-match (Street Fighter Wiki). Concept/lineage only. Zen does NOT randomly morph. |
| Dural attack rows | 0 | Dural has no published movelist; her style is an amalgam. No VF5 row is wired as a Zen move — that would make Zen a copycat again. Dural's layer is stance + inhuman movement, pending extraction. |
| NEEDS-INPUT | 6 | Tentacle 3 + Oversoul 1 + Spirit-form 2 |
| UNMAPPED animation | 25 / 25 | No Dural motion, no Twelve 2D->3D conversion, no MADE Zen animation exists yet. Every entry has `anim_ref: null` on purpose. |

### Name correction (not silently renamed)

The task brief wrote "X.FLAT". The SF name is **X.F.L.A.T.**
(Super Art II, jumping, `D, DF, F, D, DF, F + K`, 1 stock). The moveset
entry uses X.F.L.A.T. and records the brief's spelling here so the
difference is visible, not hidden.

### What was NOT invented

- No frame data for Twelve moves: the SuperCombo Twelve frame-data
  tables were empty when read, so none is claimed.
- No Eleven normals: Eleven has no moveset to copy.
- No named Tentacle/Oversoul/spirit attacks beyond doc phrases: where
  docs give attack types but no names/inputs, entries carry the doc
  phrase + NEEDS-INPUT.
- No Dural attack rows, no VF5 FAQ rows relabelled as Zen's.
- Provisional single-button bindings are flagged NEEDS-SPEC, not
  presented as canon: SF "P" (any punch) -> LP1 for N.D.L./A.X.E./X.N.D.L.;
  SF "K" (any kick) -> LK3 for D.R.A., RK4 for X.F.L.A.T.; SF "MK"
  (medium kick, no side) -> LK3 for B.M.K.; SF stock/meter mapping for
  supers -> NEEDS-SPEC; EX versions exist in SF but are not wired.

## Move List Creator (Zen only)

`packages/creation-suite/src/movelist-editor.js`, `fromMovesetFile()`:
now also reads `moveset.wh_true_moveset.moves` into display entries
(id namespace `true:<id>`). Zen's 25 true moves show in Zen's editor
list with status `unmapped` (editor's own guard: no `anim_ref` means
nothing to play, so they are shown but NOT offered as swap targets —
never silently "correct"). When a MADE animation or a Dural/Twelve
clip lands, that lane sets `anim_ref` (+ clip properties) on the
entry; only then can it validate correct/approximate and become
eligible. `serializeMoveset()` clones the whole moveset object, so
the section passes through a save untouched. Editor test proof is
in the PR body (simulation only — NOT play verification).

## Sources actually read (not guessed)

- SF: SuperCombo Wiki, Twelve/Archive
  (https://wiki.supercombo.gg/index.php?title=Street_Fighter_3:_3rd_Strike/Twelve/Archive&oldid=13553)
  — throws, command normals, specials, Super Arts, X.C.O.P.Y. limits.
- SF: Street Fighter Wiki, Eleven (https://streetfighter.fandom.com/wiki/Eleven)
  — Eleven has no own moveset; morphs pre-match.
- VF: Video Game Characters Database, Dural
  (https://vgcdatabase.fandom.com/wiki/Dural) — chrome humanoid,
  amalgam style, no officially published movelists.
- Repo: `roster/zen/CANON.md` (canon, modes, fighting base, Dural mix),
  `roster/zen/RIG-NOTES.md` (spirit behaviour, Tentacle attack design,
  Oversoul features), `game/js/roster-full.js` (Zen forms chain),
  `game/assets/movesets/zen.json` (interim Heihachi kit + lock note),
  `docs/anim/VF5-DURAL-ANIM-GAP-20261023.md` (Dural motion gap),
  `canon-moves-needing-made-animations-2026-10-24.md` ZEN section
  (Does Not Compete, Refused Seat — reused verbatim, not redone).

## What remains (honest gaps)

1. **Dural motion extraction** — VF5 motion format RE + Dural stance/idle/
   strikes converted to `game/assets/anim/vf5/dural/`; then bind
   `FIGHTER_BANK zen: 'dural'` (see the gap doc). Until then: UNMAPPED.
2. **Twelve 2D->3D conversion** — SF3:3S Twelve is 2D sprites; lifting
   N.D.L./A.X.E./D.R.A./X.F.L.A.T./X.C.O.P.Y. to 3D is its own lane.
3. **Eleven from the SFV pull** — still blocked on downloads
   (`teardown/street-fighter-5/CAST-STATUS.md` per Zen canon doc).
4. **MADE animations** for all 25 true moves (or Dural/Twelve clips when
   lanes 1–2 land). Nothing here is playable as Zen's true kit yet.
5. **NEEDS-INPUT (6)** and **NEEDS-SPEC bindings** above — owner/spec
   decisions, not agent guesses.
6. **Roster display fields** (`roster-full.js` Zen `base: 'Heihachi'`,
   `style: 'Mishima'`) still name the interim provenance; left untouched
   here because form keys and display code read that entry — a display
   follow-up should rename them to Dural/Twelve, not this bank fix.
7. **PR #1016's stance audit** (`docs/anim/STANCE-AUDIT-2026-10-24.md`,
   on #1016's branch, not main) still lists Zen as "Heihachi* / julia /
   CONFLICT". That file lives on #1016's branch; this PR comments on
   #1016 with the resolution instead of rewriting another agent's
   branch. If #1016 merges first, its audit row needs a follow-up line
   pointing here.
8. **NOT play-verified.** Editor/simulation proof only. Playing Zen's
   true kit is impossible until gap 1/2/4 land — nobody should claim
   otherwise.

## Files changed in this PR

- `game/js/fighter.js` — FIGHTER_BANK zen -> null (UNMAPPED), conflict
  comments resolved, MOVESET_MAP provenance labelled.
- `game/assets/movesets/zen.json` — `wh_true_moveset` (25 entries) +
  `anim_set_lock.note` decision line. Interim `moves` map untouched.
- `packages/creation-suite/src/movelist-editor.js` — display
  `wh_true_moveset` entries (Zen only on main today).
- `roster/zen/CANON.md` — data-status paragraph resolved (was: bank
  still maps zen->julia).
- `roster/zen/RIG-NOTES.md` — stale "Julia's bank" sentence corrected
  to UNMAPPED.
- `docs/decisions/2026-10-24-zen-base-decision.md` — this file.
- `WORKLOG.md` + `docs/owner-directives.md` — short decision entries.

## PR relationship

- PR #1016 (open, branch `feature/stance-fix-20261024`) flagged the
  conflict; it is NOT rewritten here (another agent's branch). This PR
  is the follow-up resolution, and #1016 gets a comment linking here.
  Do NOT reopen/merge #1016 to resolve Zen — this PR does it.
