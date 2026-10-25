# Ryuji motion bank — precise gap (2026-10-23)

**Source priority: KOF XV FIRST (directed KOF 3D teardown, XV > XIV;
KOF XV via dreamcancel / SNK wiki / supercombo KOF '98 — the file's
`kof_source`) for the Yamazaki side; documented WWE/No Mercy sources for
the Rock side; T3 king rows LAST (fallback only).** Ryuji is the owner's
Yamazaki / Rock hybrid (owner 2026-10-19).

## Moveset status (done this pass — batch10-special-pull)

The Rock side is now merged into the hybrid file. `ryuji.json` is the
file the roster plays (`roster-full.js`: `moveset: 'ryuji'`); its
canon_note claims "FULL KOF Yamazaki set + The Rock's wrestling", but it
held only the 103-move KOF side — the Rock side lived in the separate
`game/assets/movesets/ryuji-rock.json`. Merged 24 moves + 2 specials
(103 → 127 moves), verbatim, zero key collisions; KOF set untouched:
- 10 T3 king rows (`1`–`10`), throws `1+3`/`2+4`, and Rock moves:
  SERPENT SLASH, SAND KICK, KNIFE SLASH, THE GUILLOTINE, SHARPSHOOTER,
  BRAHMA BULL LARIAT, ROCK BOTTOM (`d/f+1+2`), TONGUE-OUT RUSH,
  People's Elbow entries, DDT-family entries.
- specials: ROCK BOTTOM (super), PEOPLE'S ELBOW DROP.
- `merge_sources.rock_side_merge_20261023` records the merge.
  `ryuji-rock.json` remains the Rock-side source document.

**Wiring note (not this lane):** `ryuji` is absent from MOVESET_IDS —
the fighter-completeness test lists it as a KNOWN_GAP owned by the
CornerStone lane ("stale pre-rename entry"). This pull does not change
that; the test must stay green.

**SHOW-ANIMATION LOCK (owner 2026-10-23):** `anim_set_lock` added;
126/127 moves stamped `"set": "FIGHT"` (incl. the 2 new specials).
The 1 taunt (`moves/taunt`) is stamped `"set": "SHOW"` — taunts wire to
intro/win slots and cutscenes ONLY, never the moveset, without the
user's explicit approval.

## The missing bank — FIGHT vs SHOW
- **FIGHT** — KOF XV Yamazaki motion not extracted (directed teardown,
  XV > XIV): the 103 `kof_motion` moves' `anim_ref`s are aspirational
  until the KOF lane decodes motion. Rock-side moves bind T3 king rows
  (`t3:king:row:*`) as the logged fallback.
- **SHOW** — 1 taunt tagged SHOW in-file (wire to taunt slot only);
  win pose / intro pose: no documented clips on disk — gap.
