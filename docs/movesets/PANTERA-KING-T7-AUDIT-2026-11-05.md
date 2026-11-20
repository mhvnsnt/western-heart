# Pantera = exact King T7 — audit 2026-11-05 (updated same day)

Owner: Pantera must be **100% exact King Tekken 7** (no switched/mixed/swapped
anims; no T3 King as T7). Template: `t7-grappler-jaguar-mask` → `pantera`
(see `MOVESET-TEMPLATE-INVENTORY-2026-11-05.md`).

Authorized: t369u / t374u / t376u. Claim #866 (MoneyManBusch).

## Sources of truth

- Clipmap: `docs/proof/t7-clipmap-king-pantera.json` (**467** mapped moves; internal `Kg_*` names — no notation bridge in-repo for the 55 r17 slots).
- Wiring diagnosis: `docs/movesets/PANTERA-WIRING-DIAGNOSIS-2026-11-03.md` (RC1–RC5 fixed on main for strike-as-grab; A1/C1 carried until this update).
- Input coverage: `docs/movesets/PANTERA-INPUT-COVERAGE-2026-11-01.md`.
- Historical r17 core-8 failing list: `docs/proof/moveset-sweep-20261028/r17-core8-failing.json`.

## Exactness checklist

| Gate | Verdict |
|---|---|
| Motbin / bank is King 0x64 (not donor) | required — clipmap authority |
| No T3 King clip presented as T7 King | required |
| No swapped/mixed anims across moves | required |
| Template id is generic (`t7-grappler-jaguar-mask`) | logged |
| Roster name stays `pantera` | logged |

## Anomalies — status after this MoneyManBusch pass

| ID | Status | What landed / why still open |
|---|---|---|
| **A1** | **FIXED (engine)** | Root cause: `_enterThrownExec` never cleared `_throwHitDone`. After the first legacy slam the victim kept `true`, so later throws (`2+4`, `1+4`, `f+1+3`, `f+2+4`, `d/b+1+3`) skipped `_throwSlamDamage` while still playing `thrownExec`. Probe pattern (1+3≈23.5 then every later throw dmg 0) matches. Fix: clear `_throwHitDone` in `_enterThrownExec` and in `startThrowLock`. Damage values already present on the King/`~t8.king` records — no donor / clip swap. |
| **C1** | **FIXED (data class only)** | `1+3,1` / `2+4,1` were `move_class: strike` despite diagnosis rows 415/417 being throw rows and the correct path being `_throwChainPress` mid-throw. Set `move_class: throw`, `isGrab`/`throw` true + `throw_chain_follow` hint. **Did not** rewire anims (still `anim_ref` t3:king rows already on file — no new T3-as-T7 presentation). Fresh-input strike presentation of the chain follow-ups is the bug closed. |
| **RC4** | **FIXED (already on main; audit closed)** | Deliberate two-thumb throws: `CHORD_WINDOW_MS` stays **50** (raising it back to 140 regresses strings — see `input.js` comment). Touch rescue already on main in `fighter.js` `tryAttack`: a second single limb within **0.14 s** of startup upgrades to the chord when that chord exists (`PANTERA-WIRING-VIDEO-2026-11-03.md`, proven on camera). No window widen this pass. |
| r17 ×55 | **named-open** | Clipmap uses internal `Kg_*` move names; no in-repo notation↔clipmap bridge proves a replacement row for any of the 55 slots without GRE pac work (forbidden this pass). Including `~t3.king` twins — leave named. |

## r17-core8 failing inventory (Pantera) — 55 named slots (still open)

These stay named until a proven King T7 clipmap row (notation bridge) lands. No donor guess.

1. `P+K`
2. `1_c26_r235`
3. `1_c26_r240`
4. `1_c6_r478`
5. `3,2,2*`
6. `(back to wall).b,b,UB`
7. `H.2+3`
8. `MMD2.1,1+3/ MMD2.2,2+4`
9. `MMD5.1+2,3,1+3/ MMD5.1+2,4,2+4`
10. `MMD5.1+2,4,2,1+2`
11. `PD.1+2,3,4,1+2`
12. `ss2+4,b/db`
13. `UT,1+2,1+2`
14. `UT,3+4,&amp;#58;1+2`
15. `f,n,d,D/F+1`
16. `f,n,d,D/F+4`
17. `t7.king_110`
18. `t7.king_150`
19. `t7.king_158`
20. `PILE_DRIVER.1+2,1+2`
21. `PILE_DRIVER.1+2,3,4,1+2`
22. `t7.king_229`
23. `t7.king_230`
24. `t7.king_231`
25. `t7.king_232`
26. `t7.king_233`
27. `t7.king_234`
28. `t7.king_235`
29. `t7.king_247`
30. `INDIAN_DEATH_LOCK.1,3,4,1+2,3+4`
31. `STANDING_HEEL_HOLD.1+2,3,1,1+3`
32. `HEAD_JAMMER.4,3,4,3+4,1+2`
33. `CHICKEN_WING_FACE_LOCK.1+3,3+4,2+4,1+2,1+2+3`
34. `REVERSE_ARM_SLAM.2,1,1+2`
35. `POWER_BOMB.3,1,2,3+4,1+2+3+4`
36. `BLIND_KICK_HIT.BT.1+2`
37. `t7.king_268`
38. `REVERSE_SPECIAL_STRETCH_BOMB.2,2,1+2`
39. `CANNONBALL_BUSTER.3+4,1+2,1+2+4`
40. `MANHATTAN_DROP.1,2,3+4,1+2`
41. `VICTORY_BOMB.3,1,2,3+4,1+2+3+4`
42. `SLEEPER.3,4,1+2,3+4`
43. `REVERSE_SPECIAL_STRETCH_BOMB.3+4,1+2`
44. `BACKDROP.1+2,4,1+2,1+2+3`
45. `BURNING_HAMMER.2+4,3+4,1+3,1+2,1+2+3`
46. `t7.king_295`
47. `t7.king_296`
48. `t7.king_297`
49. `u/b+1,1~t3.king.3`
50. `u/b+1,4~t3.king.3`
51. `1+4,1~t3.king`
52. `1+4,1~t3.king.2`
53. `d,d/b,d,d/b+1+2~t3.king`
54. `d,d/b,d,d/b+1+2,1`
55. `n,d/f,n,d/f+2+4,1`

## Proven fixes this pass

- A1 engine clear of `_throwHitDone` (`game/js/fighter.js`).
- C1 data classification for `1+3,1` / `2+4,1` (`game/assets/movesets/pantera.json`).
- RC4 audit closed against existing 0.14 s chord rescue (no CHORD_WINDOW widen).
- r17: **0 of 55** cleared (no notation↔clipmap proof without GRE).

## Percent complete (honest)

- Clipmap coverage: 467 mapped (bank extract).
- Input fire coverage (2026-11-01): 227/238 fired.
- A1/C1/RC4 closed; **r17 list still open** → still **not 100%**.
- Do not claim 100% until the r17 list is empty with probe proof.
