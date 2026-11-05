# Pantera = exact King T7 — audit 2026-11-05
Owner: Pantera must be **100% exact King Tekken 7** (no switched/mixed/swapped
anims; no T3 King as T7). Template: `t7-grappler-jaguar-mask` → `pantera`
(see `MOVESET-TEMPLATE-INVENTORY-2026-11-05.md`).

Authorized: t369u / t374u. Claim #866.

## Sources of truth

- Clipmap: `docs/proof/t7-clipmap-king-pantera.json` (**467** mapped moves).
- Wiring diagnosis: `docs/movesets/PANTERA-WIRING-DIAGNOSIS-2026-11-03.md` (RC1–RC5 fixed on main for strike-as-grab; A1/C1 carried).
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

## Carried anomalies (from 2026-11-03 diagnosis — NOT claimed fixed here)

- **A1** — most throws deal 0 damage in probe (Zen / legacy lock path); `1+3` damages ≈24 but `2+4`, `1+4`, `f+1+3`, `f+2+4`, `d/b+1+3` execute with 0 damage.
- **C1** — chain-throw follow-ups (`1+3,1`, `2+4,1`) registered as ordinary strings; correct only inside throw via `_throwChainPress`.
- **RC4** — deliberate throws hard at human two-finger timing (`CHORD_WINDOW_MS = 50`) on touch.
- Unmapped step plans / dead slots still listed in the diagnosis “11 dead slots” table.

## r17-core8 failing inventory (Pantera) — 55 named slots

These are the historical failing notation / system rows. Clear one-by-one with
proven King T7 clipmap rows only — never a donor guess.

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

## Proven fixes in this adoption PR

- Template attachment logged (`t7-grappler-jaguar-mask` → `pantera`).
- No animation row rewrites in this PR (would violate exactness without fresh probe proof).
- Next MoneyManBusch Pantera commits: A1 throw damage path (`completeThrow` / `_throwSlamDamage`), then unmapped step plans against clipmap, then pile-driver / MMD / UT strings from the list above.

## Percent complete (honest)

- Clipmap coverage: 467 mapped (bank extract).
- Input fire coverage (2026-11-01): 227/238 fired.
- Identity-correct wiring: RC1–RC3 fixed; A1/C1/RC4 + r17 list remain → **not 100%**.
- Do not claim 100% until this remaining list is empty with probe proof.
