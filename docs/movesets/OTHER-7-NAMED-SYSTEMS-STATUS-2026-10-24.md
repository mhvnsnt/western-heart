# Other 7 T7 fighters — named-system entries status (Pantera first, then these)

**Date:** 2026-10-24. **Base:** main moveset files at read time.
**The 7 are:** burger, demonio, diablo, kinpo, phantom, scimitar, skull.
Together with Pantera they are the 8 MOD fighters of the 9-lane report
(hard-mismatch baseline after merged PR #1043: pantera 236/762, burger
151/471, demonio 161/665, diablo 134/559, kinpo 108/429, phantom 553/937,
scimitar 54/268, skull 122/605 — total 1,519/4,696). Torch is the 9th
reconciliation fighter but is NOT one of the 7: it still carries
playable `t8:` refs (165, not purged) and belongs to a separate lane.
**Buttons:** LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2,
LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

## Status shared by all 7 (same as Pantera, verified per file)

- **System flags: 0.** No move in any of the 7 files carries
  `rageArt` / `rageDrive` / `powerCrush` / `screw` / `tornado`. The
  engine flags exist (`fighter.js` reads them); the data does not.
  Adding the flags is part of each fighter's named-system change, once
  its Rage Art / Rage Drive keys are confirmed below.
- **Correct anims: UNMAPPED for every renamed system** (same rule as
  Pantera: original system's Tekken-file clip only; T3 = temporary
  fallback at most, never the mapping). No T7 clip bytes exist in the
  repo for any fighter; the unblock for Ikari Jishin / Rinne Kōgeki /
  Kongō / Spin Juggle Floor Form is the same T7 live extraction
  (per-fighter move ids below); Air Form needs a T8 clip route;
  Ōgi needs a V-System route (open item, not packaged).
- **Kongō / Ōgi / Spin Juggle moves: UNIDENTIFIED in all 7 files.**
  No Power Crush flag, no Screw flag, no Tornado flag, no V-System
  entries exist in-file for any of the 7 (same `t7` block census shape
  as Pantera: no `powerCrush`/`screw`/`tornado` fields). Identification
  is the work, not an assumption — and the `t7` crush field is evasion
  crush, not Power Crush, for every fighter.
- **Rinne gating: engine-side, shared.** HP ≤ 25%, once per round,
  `R.` prefix only while gating holds (see the Pantera doc). Rinne
  presentation (aura caller, HUD tag + gauge) is unverified for all
  fighters, same as Pantera.
- **Rinne damage boost: OPEN user question for all fighters** — not
  wired anywhere, not assumed anywhere.

## Per-fighter Rage Art / Rage Drive candidates (from the files)

"Rage Art" / "Rage Drive" names below are the files' own T7 move names
(technical record, not in-game text). Slot hijack = `slots['R.d/f+1+2']`
pointing at the T8 `R.df+1+2` move instead of the T7 Rage Art key.

| Fighter (Tekken base / T3 bank / moves) | T7 Rage Art (Ikari Jishin) | T7 Rage Drive (Rinne Kōgeki) | Slot hijack? |
| --- | --- | --- | --- |
| burger (Bob / `moveset_bryan.json` / 552; refs t3 106, t7 281, t8 161, wh 4) | `R.d/f+1+2` "Rage Art" (`t7:bob:bob_261`) | TWO candidates — `R.f+2+3,F` "Rage Drive" (`bob_250`) AND `R.f+2+3` "Rage Drive" (`bob_262`, + variant `bob_263`) — DISAMBIGUATION OWED, do not pick silently | YES — `slots['R.d/f+1+2']` → `R.df+1+2` "Ultimate Full-Course" (T8). Same fix as Pantera once the drive disambiguation lands (the Art key itself is unambiguous). |
| demonio (Jin Kazama / `moveset_jin.json` / 764; t3 326, t7 259, t8 173, wh 6) | `R.b+1+2` "Rage Art" (`t7:jin:jin_173`); slot self-consistent | `R.f,n,d,d/f+1+2,3,1` "Rage Drive" (`jin_177`) AND `R.f,n,d,d/f+4,3+4` "Rage Drive" (`t7:devil_jin:deviljin_190`) — Devil Jin variant needs a ruling (base vs Devil form) | Pattern present (`slots['R.d/f+1+2']` → T8 "Polar Demon Gouge") but demonio's T7 Art is on `R.b+1+2`, NOT `R.d/f+1+2` — no Art hijack; whether `R.d/f+1+2` in Rinne should fire the T8 Art is a design question, not a slot bug to silently "fix". |
| diablo (Heihachi / `moveset_heihachi.json` / 661; t3 308, t7 201, t8 146, wh 6) | `R.d+1+2` "Rage Art" (`t7:heihachi:heihachi_160`); slot self-consistent | TWO drives — `R.1,b+2,1+2` "Rage Drive 1" (`heihachi_157`, + variants 158/159) AND `R.b+2,1+2` "Rage Drive 2" (`heihachi_161`, + variant 162) — DISAMBIGUATION OWED | Pattern present (`slots['R.d/f+1+2']` → T8 "Mishima Style Ultimate Technique - Tempest Dragon God Fist") but diablo's T7 Art is on `R.d+1+2` — same design question as demonio, plus the heihachi classification gap (see below). |
| kinpo (Asuka / `moveset_jin.json` / 525; t3 143, t7 232, t8 146, wh 4) | `R.d/f+1+2` "Rage Art" (`t7:asuka:asuka_208`) | `R.f,F+1+2` "Rage Drive" (`asuka_209`) — single candidate | YES — `slots['R.d/f+1+2']` → `R.df+1+2` "Naniwa Peacemaker Knuckle" (T8). Same fix as Pantera. |
| phantom (Yoshimitsu / `moveset_yoshimitsu.json` / 1019; t3 315, t7 386, t8 312, wh 6) | `R.b+1+2` "Rage Art" (`t7:yoshimitsu:yoshimitsu_328`); slot self-consistent | `R.f,n,d,d/f+1+2` "Rage Drive" (`yoshimitsu_330`) — single candidate (multi-step motion input; verify the motion path plays) | Pattern present (`slots['R.d/f+1+2']` → T8 "Trailokya Pilgrimage") but phantom's T7 Art is on `R.b+1+2` — design question, not a silent fix. Worst hard-mismatch count (553/937) — phantom's batch lane is the longest. |
| scimitar (Shaheen / `moveset_jin.json` / 362; t3 143, t7 125, t8 90, wh 4) | `R.1+2` "Rage Art" (`t7:shaheen:shaheen_107`); slot self-consistent | `R.d/b+2,4,D/F` "Rage Drive" (`shaheen_110`, chain of 107→110 with intermediate keys 108/109) — single drive, multi-step; verify the chain path plays | Pattern present (`slots['R.d/f+1+2']` → T8 "Najm Alshamal") but scimitar's T7 Art is on `R.1+2` — design question, not a silent fix. |
| skull (Bryan Fury / `moveset_bryan.json` / 688; t3 248, t7 266, t8 168, wh 6) | `R.d/f+1+2` "Rage Art" (`t7:bryan:bryan_246`) | `R.b+1+2` "Rage Drive" (`bryan_247`) — single candidate | YES — `slots['R.d/f+1+2']` → `R.df+1+2` "Total Vandalization" (T8). Same fix as Pantera. |

## What each fighter's named-system change contains (same shape as Pantera's)

1. `named_systems` object in the fighter's moveset file (Rinne gating
   spec, Ikari Jishin + Rinne Kōgeki entries with file numbers,
   Kongō / Ōgi / Spin Juggle as UNMAPPED with unblock paths, Amatsu
   Rinne excluded).
2. Slot fix where the T7 Rage Art key IS `R.d/f+1+2` (burger, kinpo,
   skull — same as Pantera) + `rageArt: true` / `rageDrive: true`
   flags on the confirmed keys.
3. NO slot change where the T7 Art lives on another key (demonio,
   diablo, phantom, scimitar) until the `R.d/f+1+2`-in-Rinne design
   question is answered (T7 Art input vs T8 Art input).
4. NO flags for Kongō / Ōgi / Spin Juggle until moves are identified
   from flagged frame data — never from move names.
5. Batch lane order per fighter (after Pantera): Batch 1 (LP1/RP2-only
   strings) first, then Batch 2, then Batch 3+, one by one, each clip
   verified with file evidence before it wires. No fighter's batch is
   fixed on simulation alone.

## Diablo + heihachi classification note

Diablo's T3 bank label is `heihachi`, which has NO classification bank
in PR #1079 (see the row-resolution doc). Diablo's wire-in therefore
stays input-verified until a real heihachi rows pack lands or a
documented `heihachi` → `heihachi_on_jin` alias is owner-approved.
Do not alias silently in any fighter's change.
