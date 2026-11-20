# Koreshi motion bank — precise gap (2026-10-23)

**CUSTOM-SOURCE fighter (no canonical game source).** Koreshi is the
owner's custom composite ("Kakashi (Naruto) + Super Saiyan 4/5 + ninja",
owner 2026-10-19). There is NO Kakashi/Naruto/SSJ/ninja game source in
the repo — no bank, no movelist, no teardown. Nothing was invented to
fill that concept: per the no-guessing law this doc records what is
ACTUALLY in the file vs. what is missing.

## What is actually in the file (documented, verified 2026-10-23)

`game/assets/movesets/koreshi.json` — 953 moves:
- **Vega (SF) kit, complete**: all 31 `sf-vega.json` documented moves
  and all 91 `vega.json` `sf_motion` moves present (id-diffed, 0 missing).
  Provenance on-file: `guide:canon-6-button-layout`, `guide:capcom`,
  `guide:capcom-era canon`, `guide:scwiki-era canon` (sfex+alpha /
  sfex2plus).
- **T8 Yoshimitsu kit**: 312 moves with `t8_source: yoshimitsu`.
- **T3 heihachi rows**: 497 `t3_source` entries (logged fallback).
- **Custom-named moves**: exactly 2 carry the Kakashi/Naruto concept —
  "KORESHI 14 — SHARINGAN COUNTER" and "CHIDORI BURST"
  (`wh_signature`/`wh_note` style, creator-named, no game source).

## Moveset status (done this pass — batch10-special-pull)

+0 moves — the documented sides are complete; the custom-concept side
has no source to pull from, and nothing was invented.

**SHOW-ANIMATION LOCK (owner 2026-10-23):** `anim_set_lock` added;
949/953 moves stamped `"set": "FIGHT"`. 4 taunt entries
(`1+2+3+4~donor.vega` variants) stamped `"set": "SHOW"` — taunts wire
to intro/win slots and cutscenes ONLY, never the moveset, without the
user's explicit approval.

## The missing bank — FIGHT vs SHOW

- **FIGHT** — moveset moves, combat stances → the moveset
  (`game/assets/movesets/koreshi.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations →
  intro/win slots and cutscenes ONLY.

### FIGHT clips → combat bank + moveset
SF Vega motion: real frame data pending OVL decode (TEARDOWN.md 2c).
T8 Yoshimitsu motion: extraction lane. No Kakashi/SSJ/ninja motion
exists or is claimed — if the owner ever names a real source game for
the concept, that lane files a new gap doc; until then this stays as-is.

### SHOW clips → intro/win slots + cutscenes ONLY (never the moveset)
- 4 taunt entries — tagged SHOW in-file; wire to taunt slots only.
- Win pose / intro pose: no documented clips on disk — gap.
