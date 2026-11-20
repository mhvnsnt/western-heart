# Input matrix audit (`tools/input-verify/input_matrix_audit.mjs`)

> "do all the directional inputs work ... forward left punch, forward right punch, back left kick, back right kick,
> down right kick, jump and punch ... all the different combinations of button inputs ... for every character ... so
> I'm not limited or blocked" (owner, 2026-11-01)

**Before (game as shipped on 2026-11-01): 1,987 of the 7,425 inputs did nothing.** A button chord with no move of its
own hit `fighter.js` "chord with no matching move: whiff, no action" (Pantera alone: 36 dead, e.g. 1+2+3, f+1+2+4;
Purple Rain 28, e.g. 1+4, b+1+4; Chordz 35). Direction + single button was never dead (no directional move: the
neutral button's move fires, as in Tekken).

**After:** `TekkenBuffer.pressChordLenient` (game/js/movesets.js): the chord's own move first (unchanged), else its best
two-button sub-chord (strikes before the 1+3 / 2+4 throws), else its first button's move. Extra buttons never block a
move. Guard: `test/input-matrix.test.mjs` (every roster fighter, every direction, every button set; 0 dead).
Next: where a fighter's T7 / T8 source data has a real move for a chord that now falls back, wire that move.

55 fighters x 9 directions x 15 button sets = 7425 inputs through the game's own TekkenBuffer. **DEAD (nothing happens): 0.**

own = the fighter's move for that exact input; neutral = direction + button with no directional move fires the neutral button's move (as Tekken does); fallback = a chord with no move of its own fires its best sub-chord / first button (no dead chords); generic = the base WH punch / kick; DEAD = nothing happens.

| fighter | own | neutral | fallback | generic | DEAD | dead inputs (first 8) |
|---|---|---|---|---|---|---|
| rin | 114 | 3 | 18 | 0 | 0 |  |
| byou | 100 | 2 | 33 | 0 | 0 |  |
| tou | 96 | 4 | 35 | 0 | 0 |  |
| sha | 114 | 3 | 18 | 0 | 0 |  |
| kai | 95 | 4 | 36 | 0 | 0 |  |
| retsu | 94 | 5 | 36 | 0 | 0 |  |
| zen | 103 | 5 | 27 | 0 | 0 |  |
| gyou | 107 | 1 | 27 | 0 | 0 |  |
| pantera | 95 | 4 | 36 | 0 | 0 |  |
| demonio | 114 | 3 | 18 | 0 | 0 |  |
| phantom | 105 | 3 | 27 | 0 | 0 |  |
| diablo | 103 | 5 | 27 | 0 | 0 |  |
| skull | 87 | 5 | 43 | 0 | 0 |  |
| samura1 | 95 | 4 | 36 | 0 | 0 |  |
| sakura | 114 | 3 | 18 | 0 | 0 |  |
| zui | 111 | 6 | 18 | 0 | 0 |  |
| kinpo | 103 | 5 | 27 | 0 | 0 |  |
| waterfall | 89 | 2 | 44 | 0 | 0 |  |
| kingtyrant | 94 | 5 | 36 | 0 | 0 |  |
| burger | 86 | 4 | 45 | 0 | 0 |  |
| awapop | 97 | 2 | 36 | 0 | 0 |  |
| scimitar | 103 | 5 | 27 | 0 | 0 |  |
| purplerain | 103 | 4 | 28 | 0 | 0 |  |
| nightwolf | 104 | 4 | 27 | 0 | 0 |  |
| dio | 81 | 9 | 45 | 0 | 0 |  |
| cyborgx | 104 | 4 | 27 | 0 | 0 |  |
| michiko | 82 | 8 | 45 | 0 | 0 |  |
| star | 105 | 3 | 27 | 0 | 0 |  |
| torch | 106 | 2 | 27 | 0 | 0 |  |
| bruno | 76 | 6 | 53 | 0 | 0 |  |
| negativo | 94 | 5 | 36 | 0 | 0 |  |
| thor | 83 | 6 | 46 | 0 | 0 |  |
| yukihyo | 103 | 5 | 27 | 0 | 0 |  |
| slice | 96 | 3 | 36 | 0 | 0 |  |
| docfrank | 68 | 13 | 54 | 0 | 0 |  |
| baek-master-white | 69 | 12 | 54 | 0 | 0 |  |
| mariposa-monarch | 86 | 5 | 44 | 0 | 0 |  |
| dxmmii-patchwork | 75 | 15 | 45 | 0 | 0 |  |
| charger | 79 | 13 | 43 | 0 | 0 |  |
| dorowani | 64 | 10 | 61 | 0 | 0 |  |
| chatur | 135 | 0 | 0 | 0 | 0 |  |
| pond | 83 | 8 | 44 | 0 | 0 |  |
| ryusan | 80 | 8 | 47 | 0 | 0 |  |
| tobi | 96 | 3 | 36 | 0 | 0 |  |
| megami | 92 | 7 | 36 | 0 | 0 |  |
| menajerii | 67 | 8 | 60 | 0 | 0 |  |
| kronos | 83 | 8 | 44 | 0 | 0 |  |
| deathfang | 77 | 13 | 45 | 0 | 0 |  |
| ryuji | 70 | 15 | 50 | 0 | 0 |  |
| koreshi | 105 | 3 | 27 | 0 | 0 |  |
| rave | 108 | 1 | 26 | 0 | 0 |  |
| buffalo-bill | 97 | 3 | 35 | 0 | 0 |  |
| vainabel | 58 | 23 | 54 | 0 | 0 |  |
| cainelias | 58 | 22 | 55 | 0 | 0 |  |
| chordz | 93 | 7 | 35 | 0 | 0 |  |
