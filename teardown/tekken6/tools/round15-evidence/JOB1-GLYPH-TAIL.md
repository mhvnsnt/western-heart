# JOB 1 — GLYPH TAIL: **COMPLETE — all 13 remaining codepoints PROVEN**

Round 14 fixed 16 codepoints + the contextual E00C and left 12
unproven (E006, E008, E009, E00A, E00B, E00E, E00F, E01A, E01D,
E01F, E021, E022, E023 — 13 counting E006), gating 605 moves.
This round fixes **every one** under the unchanged proof standard
(>=1 carrier move decoding EXACTLY to its cited T6 notation +
charmap position consistent), and revises E00C to its glyph
identity. Result: **6,814 / 6,814 notation-carrying moves decode
completely; 0 partial** (was 6,209 complete / 605 partial).

Two structural findings organize the proofs:

**The button block is a complete subset enumeration.** E015–E023
is exactly the 15 non-empty subsets of {1,2,3,4}, ordered by
highest button, then combination order: max-1 [1]; max-2 [2,
1+2]; max-3 [3, 1+3, **2+3**, 1+2+3]; max-4 [4, **1+4**, 2+4,
**1+2+4**, 3+4, **1+3+4**, **2+3+4**, **1+2+3+4**]. Round 14's
nine proven points (1, 2, 1+2, 3, 1+3, 1+2+3, 4, 2+4, 3+4) pin
the scheme; the six gaps (bold) are exactly the six unproven
button codepoints, and each is independently proven below by an
exact move decode — the enumeration is corroboration, never the
proof. (The brief's hypothesis (b) is confirmed in outcome but
refined in order: it is highest-button-major, not raw
enumeration order.)

**The direction block is two rings.** E000–E007 = tap directions
in ring order (d/b, d, d/f, b, f, u/b, u, u/f — round 14).
E008–E00F = the same ring in **hold form** (capitals in Tekken
notation): D/B, D, D/F, B, F, U/B, U, U/F. This explains round
14's E00C: it is the hold-F glyph — the second stroke of the
f,F dash (Demon's Paw f,f+2, Stonehead f,f+1+2) and the ~F
transition elsewhere. E00D (U/B) never occurs in the corpus
(0 occurrences in the full v2 census of 7,341 moves); it is
assigned by ring position only and flagged as such — no move
decode depends on it.

## Evidence table (codepoint → proof move → decode → cited notation → source)

| glyph | value | proof move (char) | record decode | cited notation | source |
|---|---|---|---|---|---|
| E006 | u | Rolling Bear (Kuma) | b+1+2,f,d/f,d,d/b,b,u/b,**u**,u/f | f,d/f,d,d/b,b,u/b,u,U/F after b+1+2 | Catlord T6 FAQ [1] |
| E006 | u | Bear Skip (Kuma) | **u**+1+2 | u+1+2 | Catlord T6 FAQ [1] |
| E008 | D/B | Figure Four Leg Lock (King) | **D/B**+2+4, caption "(Enemy on back) by the feet" | D/B+2+4, Ground Throws / Face Up–Feet Towards | Catlord T6 FAQ [1] |
| E009 | D | Infinite Kick Chain 1 (Lee) | 3,3,**D**+3 (caption "While rising") | WS+3,3 + (D+3) low infinite starter | Catlord T6 FAQ [1] |
| E009 | D | Low Variation (Lee) | **D**+3,3 | d+3,3,3 low variation; branches are "Hold U or D" | Tekken Wiki, Infinite Kick Chain [5]; TTT movelist note [6] |
| E00A | D/F | Infinite Kick Chain 2 (Lee) | 3,3,**D/F**+3 (caption "While rising") | WS+3,3 + (d/f+3) mid infinite starter | Catlord T6 FAQ [1] |
| E00A | D/F | Spinning Demon / Jumping Low Kick (Heihachi) | d,**D/F**+4,4,4 / d,**D/F**+3 | f,N,d,D/F (hold) CD terminus | Tekken Advance movelist [7]; cf. Catlord T6 "f,N,d,D/F+1+2" [1] |
| E00B | B | Spinning Backfist (Baek) | b,**B**+2 | b,b+2 (dash 2nd stroke; cf. FAQ's own f,f,F / f,F# dash capitals) | Catlord T6 FAQ [1] |
| E00B | B | Fatal Wind (Kuma) | b,**B**+2+3 | b, b+2+3 | Tekken Wiki, Kuma TTT2 movelist [8] |
| E00E | U | High Variation (Lee) | **U**+3,3 | u+3,3,3 high variation | Tekken Wiki, Infinite Kick Chain [5] |
| E00F | U/F | Somersault (Law) | **U/F**+3 | U/F (or U or U/B)+3 | Tekken Wiki, Law T6 movelist [3] |
| E00F | U/F | Catapult Kick (Law) | FC **U/F**+4 (caption "While crouching") | FC+U/F+4 | Tekken Wiki, Law T6 movelist [3] |
| E01A | 2+3 | Salmon Hunter (Kuma) | b,f+**2+3** | b,f+2+3 | Catlord T6 FAQ [1] |
| E01A | 2+3 | Shun Ren Dan (Jin) | d/f+**2+3** | d/f+2+3 | Catlord T6 FAQ [1] |
| E01D | 1+4 | White Heron Dance (Asuka) | **1+4**,2,4 | 1+4,2,4 (White Heron Combo) | Catlord T6 FAQ [1] |
| E01D | 1+4 | Moonsault Body Press (King) | **1+4** | 1+4 Twisting Moonsault Press | Catlord T6 FAQ [1] |
| E01F | 1+2+4 | Manhattan Drop (King) | 3+4,1+2,**1+2+4** | 3+4,1+2,1+2+4 (multithrow N) | Catlord T6 FAQ [1] |
| E01F | 1+2+4 | Dragon Sleeper Finish (King) | 2,1,3,**1+2+4**,**1+2+4** | 2,1,3,1+2+4,1+2+4 (Reverse Guillotine branch, same chain) | Catlord T6 FAQ [1]; name-exact in King's Multi-Throws Guide [9] |
| E021 | 1+3+4 | False Salute (Xiaoyu) | **1+3+4** | 1+3+4 | Tekken Wiki, Xiaoyu T6 movelist [2] |
| E022 | 2+3+4 | Greetings (Xiaoyu) | **2+3+4** | 2+3+4 | Tekken Wiki, Xiaoyu T6 movelist [2] |
| E022 | 2+3+4 | Auger (Heihachi) | **2+3+4** | 2+3+4 (Ki Charge entry) | Wavu Wiki, Heihachi movelist [10] |
| E023 | 1+2+3+4 | Muscle Buster (King) | 3,1,2,3+4,**1+2+3+4** (caption "During Power Bomb") | 3,1,2,3+4,1+2+3+4 (multithrow L, the unique 3,1,2,3+4 continuation, off K. Powerbomb) | Catlord T6 FAQ [1] |
| E023 | 1+2+3+4 | Muscle Buster (King) | same record | (3,1,2,3+4,ALL), ALL = all four buttons | King's Multi-Throws Guide [9] |

Weakest proof, stated honestly: E00B. Its carriers are the
b,B+X dash family (Baek above; Lee Cutter b,b+4; Eddy
hold-back-to-Handstand transitions trailing the glyph). No
carrier contradicts the hold-b identity, its charmap position
mirrors E003=b in the hold ring whose other seven members are
each proven, and its in-string role is the exact analogue of
E00C/F (the dash second stroke, which the T6 FAQ itself writes
with capitals: "f,f,F+2+4", "f,F#"). It is graded PROVEN on
that combined evidence; if a future font-atlas capture (the
Job-1 wall of round 14) ever contradicts a hold-ring member,
E00B is the first to re-examine.

## Deliverables

- `tools/r15_glyph_v3.py` — v3 generator (map + rendering rules
  in its docstring).
- 18 additive v3 moveset JSONs (`movesets/t6psp-*-moveset-v3.json`):
  7,341 moves; 6,814 carry notation and **all 6,814 decode
  completely** (605 partial → 0). Verified field-by-field against
  v2 and the round-7 originals: 0 diffs outside the notation
  layer (all original fields incl. `record_hex` byte-identical;
  v2 files untouched).
- Spot decodes (own-eyes, from the generated v3 files): Rolling
  Bear `b+1+2,f,d/f,d,d/b,b,u/b,u,u/f`; Figure Four Leg Lock
  `D/B+2+4`; Salmon Hunter `b,f+2+3`; Shun Ren Dan `d/f+2+3`;
  White Heron Dance `1+4,2,4`; Dragon Sleeper Finish
  `2,1,3,1+2+4,1+2+4`; Muscle Buster `3,1,2,3+4,1+2+3+4`;
  Somersault `U/F+3`; False Salute `1+3+4`; Greetings `2+3+4`.

## Sources (accessed 2026-10-22)

[1] Catlord, "Tekken 6 FAQ/Move List" v1.06, GameRevolution —
https://www.gamerevolution.com/guides/44917-tekken-6-faqmove-list
[2] Tekken Wiki, "Ling Xiaoyu/Tekken 6 Movelist" —
https://tekken.fandom.com/wiki/Ling_Xiaoyu/Tekken_6_Movelist
[3] Tekken Wiki, "Marshall Law/Tekken 6 Movelist" —
https://tekken.fandom.com/wiki/Marshall_Law/Tekken_6_Movelist
[5] Tekken Wiki, "Infinite Kick Chain" —
https://tekken.fandom.com/wiki/Infinite_Kick_Chain
[6] Tekken Wiki, "Lee Chaolan/Tekken Tag Tournament Movelist"
(+ dlh.net TTT movelist, "Hold U or D to Alternate") —
https://tekken.fandom.com/wiki/Lee_Chaolan/Tekken_Tag_Tournament_Movelist
[7] Tekken Wiki, "Heihachi Mishima/Tekken Advance Movelist" —
https://tekken.fandom.com/wiki/Heihachi_Mishima/Tekken_Advance_Movelist
[8] Tekken Wiki, "Kuma II/Tekken Tag Tournament 2 Movelist" —
https://tekken.fandom.com/wiki/Kuma_II/Tekken_Tag_Tournament_2_Movelist
[9] Naked_King / King's Multi-Throws Guide (GameFAQs /
CheatCodes) — https://gamefaqs.gamespot.com/ps2/952957-namco-classic-fighter-collection/faqs/10602
[10] Wavu Wiki, "Heihachi movelist" (Auger 2+3+4) —
https://wavu.wiki/t/Heihachi_movelist
