# TTT2 Join Table - Buffalo Bill (Marshall Law) - 2026-10-30

WH-100 lane B1 join artifact. This document is analysis only: it makes NO change to game/assets/movesets/buffalo-bill.json. Buffalo Bill is TTT2-primary per the 2026-10-23 canon decision, but the provenance lane's Phase 1 Law-group correction PR has not landed yet, so this table is the join that PR (or a later B1 follow-up) will consume.

## Sources joined

- TTT2 side: game/assets/ttt2/movesets/law.json - Marshall Law, 134 records (127 moves, 7 sample combos), decoded TTT2 MVLT layer (PR #1235). Sample combos are not joined (they are not moves).
- Buffalo Bill side: game/assets/movesets/buffalo-bill.json - 796 move entries, 490 distinct input values. Matching is done on the input field of each entry, so the several source-variant entries that share one input (the base entry and its t3.forestlaw, t7.law, and t8.law twins) count as one matched input.

## Method

Each TTT2 move record was matched by its notation_std (whitespace removed) against Buffalo Bill input values, with the record's condition_text mapped to the input prefixes Buffalo Bill itself uses: During Dragon Charge to DSS. / DSS space form, During Fake Step and After Fake Step succeeds to FS., While rising to WS., While crouching to FC., Back towards enemy and Approach from behind to BT., During side step to SS. Classification:

- Unique: exactly one distinct Buffalo Bill input matches, and when the TTT2 record carries a stance or state condition, the matched input is the condition-prefixed form (the prefixed match wins over the neutral entry, which is the neutral move's own counterpart).
- Ambiguous: the record matches more than one distinct input (the side and back throws, whose TTT2 notation is literally 1+3 or 2+4, and Parry, whose notation is the either-input pair b+1+3, b+2+4), or the record carries a stance or state condition but only the neutral input exists in Buffalo Bill, so the neutral entry cannot be proven to be the conditioned move.
- Unmatched: no candidate input (neutral, condition-prefixed, or listed alternative) exists in Buffalo Bill.

## Counts

- TTT2 Law move records joined: 127
- Unique matches: 76
- Ambiguous: 29
- Unmatched: 22

## Unique matches

| TTT2 row | TTT2 name | notation_std | condition | Buffalo Bill input | Buffalo Bill entry keys |
| --- | --- | --- | --- | --- | --- |
| 0 | Machine Gun Arrow | 1, 1, 1, 1, 1 |  | 1,1,1,1,1 | 1,1,1,1,1, 1,1,1,1,1~t7.law, 1,1,1,1,1~t7.law.2, 1,1,1,1,1~t7.law.3, 1,1,1,1,1~t7.law.4 |
| 1 | Left Right Combo | 1, 2 |  | 1,2 | 1,2, 1,2~t7.law, 1,2~t7.law.2 |
| 2 | Left Right Dragon Fist | 1, 2, 2 |  | 1,2,2 | 1,2,2, 1,2,2~t7.law, 1,2,2~t7.law.2, 1,2,2~t7.law.3 |
| 5 | Left Right to Knee | 1, 2, 3 |  | 1,2,3 | 1,2,3, 1,2,3~t7.law, 1,2,3~t7.law.2, 1,2,3~t7.law.3 |
| 6 | Left Right Combo to Somersault Feint | 1, 2, u/f+3, 4 |  | 1,2,u/f+3,4 | 1,2,u/f+3,4, 1,2,u/f+3,4~t7.law, 1,2,u/f+3,4~t7.law.2, 1,2,u/f+3,4~t7.law.3 |
| 8 | Feint to Middle Kick | 3, 3 |  | 3,3 | 3,3, 3,3~t7.law, 3,3~t7.law.2 |
| 9 | High Kick to Bloody Cleaver | 3, 4 |  | 3,4 | 3,4, 3,4~t7.law, 3,4~t7.law.2 |
| 10 | Shaolin Spin Kicks | 4, 3, 4 |  | 4,3,4 | 4,3,4, 4,3,4~t7.law, 4,3,4~t7.law.2, 4,3,4~t7.law.3 |
| 11 | Crescent Kick Combo | 4, u+3 |  | 4,u+3 | 4,u+3, 4,u+3~t7.law, 4,u+3~t7.law.2 |
| 12 | Ab Cruncher | 3+4 |  | 3+4 | 3+4, 3+4~t8.law, 3+4~t7.law, 3+4~t7.law.2, 3+4~t3.forestlaw |
| 13 | Poison Arrow | f+2, 1 | 【】 | f+2,1 | f+2,1 |
| 16 | Dragon Hammer | f+1+2 |  | f+1+2 | f+1+2, f+1+2~t8.law, f+1+2~t7.law, f+1+2~t3.forestlaw |
| 17 | Dragon Killer | f+3+4 |  | f+3+4 | f+3+4, f+3+4~t7.law, f+3+4~t3.forestlaw.2 |
| 18 | Step in Combo | d/f+3, 3, 3 |  | d/f+3,3,3 | d/f+3,3,3, d/f+3,3,3~t7.law, d/f+3,3,3~t7.law.2 |
| 19 | Mid Kick Combo to Somersault Kick | d/f+3, 3, 4 |  | d/f+3,3,4 | d/f+3,3,4, d/f+3,3,4~t7.law, d/f+3,3,4~t7.law.2 |
| 20 | Right Middle Kick to Somersault Kick | d/f+4, 3 |  | d/f+4,3 | d/f+4,3, d/f+4,3~t8.law, d/f+4,3~t7.law, d/f+4,3~t7.law.2 |
| 21 | Banana Peel | d/f+3+4 |  | d/f+3+4 | d/f+3+4, d/f+3+4~t8.law, d/f+3+4~t7.law, d/f+3+4~t3.forestlaw |
| 22 | Low Backhand to High Kick | d+1, 3 |  | d+1,3 | d+1,3, d+1,3~t7.law, d+1,3~t7.law.2 |
| 23 | Body Blow to Dragon Lift | d+2, 3 |  | d+2,3 | d+2,3, d+2,3~t8.law |
| 24 | Dragon Low Kick | d+3 |  | d+3 | d+3, d+3~t7.law, d+3~t3.forestlaw |
| 25 | Dragon Low to Hook Kick | d+3, 3 |  | d+3,3 | d+3,3, d+3,3~t7.law, d+3,3~t7.law.2 |
| 26 | Construct Kick | d+4, 3 |  | d+4,3 | d+4,3, d+4,3~t8.law, d+4,3~t7.law, d+4,3~t7.law.2 |
| 27 | Dragon Charge | d+1+2 |  | d+1+2 | d+1+2, d+1+2~t7.law |
| 28 | Dragon Knuckle | 1 | During Dragon Charge | DSS.1 | DSS.1, DSS.1~t7.law |
| 29 | Dragon Knuckle Combo | 1, f+1 | During Dragon Charge | DSS.1,f+1 | DSS.1,f+1, DSS.1,f+1~t7.law |
| 30 | Dragon Knuckle Flight | 1, 4 | During Dragon Charge | DSS.1,4 | DSS.1,4, DSS.1,4~t7.law |
| 31 | Cloud Gates | 2 | During Dragon Charge | DSS.2 | DSS.2, DSS.2~t7.law |
| 32 | Dragon Knuckle Spin Kick | 3 | During Dragon Charge | DSS.3 | DSS.3, DSS.3~t7.law |
| 36 | Dragon's Fire | 1+3 | During Dragon Charge | DSS.1+3 | DSS.1+3 |
| 37 | Facelift | 2+4 | During Dragon Charge | DSS.2+4 | DSS.2+4 |
| 38 | Dragon Roar | f+1 | During Dragon Charge | DSS.f+1 | DSS.f+1, DSS.f+1~t7.law |
| 41 | Dragon Cannon | f+3 | During Dragon Charge | DSS.f+3 | DSS.f+3 |
| 42 | Dragon's Flight | f+4 | During Dragon Charge | DSS.f+4 | DSS.f+4, DSS.f+4~t7.law |
| 46 | Low Kick to Somersault | d+3+4, 3 |  | d+3+4,3 | d+3+4,3, d+3+4,3~t7.law, d+3+4,3~t7.law.2 |
| 47 | Elbow Spring Kick | d/b+2, 4 |  | d/b+2,4 | d/b+2,4, d/b+2,4~t8.law, d/b+2,4~t7.law, d/b+2,4~t7.law.2 |
| 48 | Shin Crusher | d/b+3 |  | d/b+3 | d/b+3, d/b+3~t7.law, d/b+3~t3.forestlaw |
| 49 | Dragon's Tail | d/b+4 |  | d/b+4 | d/b+4, d/b+4~t8.law, d/b+4~t7.law, d/b+4~t3.forestlaw |
| 50 | Dragon's Tail to Somersault Kick | d/b+4, 4 |  | d/b+4,4 | d/b+4,4, d/b+4,4~t7.law, d/b+4,4~t7.law.2 |
| 51 | Charge Power Punch | d/b+1+2 |  | d/b+1+2 | d/b+1+2, d/b+1+2~t8.law, d/b+1+2~t7.law, d/b+1+2~t3.forestlaw |
| 52 | Frogman | d/b+3+4 |  | d/b+3+4 | d/b+3+4, d/b+3+4~t7.law, d/b+3+4~t3.forestlaw |
| 53 | Dragon Storm | b+1, 2, 2 |  | b+1,2,2 | b+1,2,2, b+1,2,2~t7.law, b+1,2,2~t7.law.2, b+1,2,2~t7.law.3 |
| 54 | Knuckle Rush | b+2, 2 |  | b+2,2 | b+2,2, b+2,2~t7.law, b+2,2~t7.law.2 |
| 55 | Junkyard Kick | b+2, 3, 4 |  | b+2,3,4 | b+2,3,4, b+2,3,4~t8.law, b+2,3,4~t7.law, b+2,3,4~t7.law.2, b+2,3,4~t7.law.3 |
| 56 | Dragon Rush Combo | b+2, 3, d+4 |  | b+2,3,d+4 | b+2,3,d+4, b+2,3,d+4~t7.law, b+2,3,d+4~t7.law.2, b+2,3,d+4~t7.law.3 |
| 57 | Dragon Spin Kick | b+3 |  | b+3 | b+3, b+3~t8.law, b+3~t7.law |
| 58 | Tiger Fang | b+4, 3 |  | b+4,3 | b+4,3, b+4,3~t7.law, b+4,3~t7.law.2 |
| 59 | Fake Step | b+1+2 |  | b+1+2 | b+1+2, b+1+2~t7.law |
| 78 | Dragon Arrow | b+3+4 |  | b+3+4 | b+3+4, b+3+4~t8.law, b+3+4~t7.law |
| 79 | Blackout | u/f+1, 1 | (or during Charge Power Punch ) | u/f+1,1 | u/f+1,1, u/f+1,1~t3.forestlaw |
| 81 | Somersault | u/f+3 |  | u/f+3 | u/f+3, u/f+3~t7.law |
| 82 | Somersault Fake | u/f+3, 4 |  | u/f+3,4 | u/f+3,4, u/f+3,4~t7.law |
| 83 | Jumping Kick to Somersault | u/f+3, 4 |  | u/f+3,4 | u/f+3,4, u/f+3,4~t7.law |
| 84 | Somersault Kick | u/f+4 |  | u/f+4 | u/f+4, u/f+4~t8.law, u/f+4~t7.law, u/f+4~t3.forestlaw |
| 86 | Dragon's Descent | u/f+3+4 |  | u/f+3+4 | u/f+3+4, u/f+3+4~t8.law, u/f+3+4~t7.law, u/f+3+4~t3.forestlaw |
| 92 | Running Side Kick | f, f, f+3 |  | f,f,f+3 | f,f,f+3 |
| 93 | Flash Fist | 1, 2 | While rising | WS.1,2 | WS.1,2, WS.1,2~t7.law, WS.1,2~t7.law.2 |
| 94 | Dragon Uppercut | 2 | While rising | WS.2 | WS.2, WS.2~t7.law |
| 95 | Side Kick | 3 | While rising | WS.3 | WS.3, WS.3~t7.law |
| 96 | Front Kick Somersault Variation | 4, 3 | While rising | WS.4,3 | WS.4,3, WS.4,3~t7.law, WS.4,3~t7.law.2 |
| 97 | Double Impact | 3, 4 | While crouching | FC.3,4 | FC.3,4, FC.3,4~t7.law |
| 98 | Low Kick to Somersault | 4, 3 | While crouching | FC.4,3 | FC.4,3, FC.4,3~t7.law |
| 101 | Slide Kick | d/f, d, d/f+3 | While crouching | FC.d/f,d,d/f+3 | FC.d/f,d,d/f+3 |
| 102 | Dragon Judgement | 2, 1, 2, 1 | During side step | SS.2,1,2,1 | SS.2,1,2,1 |
| 103 | Double Dragon | 3+4 | During side step | SS.3+4 | SS.3+4, SS.3+4~t7.law, SS.3+4~t7.law.2 |
| 104 | Blind Elbow Combo | 2, 2 | Back towards enemy | BT.2,2 | BT.2,2, BT.2,2~t7.law, BT.2,2~t7.law.2 |
| 105 | Wolf Fang | 4, 3 | Back towards enemy | BT.4,3 | BT.4,3, BT.4,3~t7.law, BT.4,3~t7.law.2 |
| 106 | Dragon Back Blow | 1+2 | Back towards enemy | BT.1+2 | BT.1+2, BT.1+2~t7.law |
| 107 | Reverse Low | d+4 | Back towards enemy | BT.d+4 | BT.d+4, BT.d+4~t7.law |
| 109 | 10 Hit Combo 1 | d/f+1, 2, 2, 1, 3, 3, 3, 4, 3, 4 |  | d/f+1,2,2,1,3,3,3,4,3,4 | d/f+1,2,2,1,3,3,3,4,3,4 |
| 115 | Dragon's Fire | 1+3 | Approach enemy | 1+3 | 1+3, 1+3~t8.law, 1+3~t7.law, 1+3~t3.forestlaw |
| 116 | Dragon's Fire | f+1+3 | Approach enemy | f+1+3 | f+1+3 |
| 117 | Hopping Frog | 2+4 | Approach enemy | 2+4 | 2+4, 2+4~t8.law, 2+4~t7.law, 2+4~t3.forestlaw |
| 118 | Hopping Frog | f+2+4 | Approach enemy | f+2+4 | f+2+4 |
| 122 | Run Up to Drop | f+2+3 | Approach enemy | f+2+3 | f+2+3, f+2+3~t7.law |
| 123 | Headlock Punch | d/f+1+2 | Approach enemy | d/f+1+2 | d/f+1+2, d/f+1+2~t7.law, d/f+1+2~t3.forestlaw |
| 124 | Headlock Drop | d/f+1+2, 1, 2, 1+2 | Approach enemy | d/f+1+2,1,2,1+2 | d/f+1+2,1,2,1+2 |

## Ambiguous

| TTT2 row | TTT2 name | notation_std | condition | Candidate Buffalo Bill inputs |
| --- | --- | --- | --- | --- |
| 33 | Dragon Junkyard Kick | 4, 3 | During Dragon Charge | 4,3 |
| 34 | Quick Hook | 1+2 | During Dragon Charge | 1+2 |
| 35 | Ab Cruncher | 3+4 | During Dragon Charge | 3+4 |
| 40 | Dragon Claw | f+2, 1 | During Dragon Charge 【】 | f+2,1 |
| 43 | Dragon Killer | f+3+4 | During Dragon Charge | f+3+4 |
| 44 | Dragon Arrow | b+3+4 | During Dragon Charge | b+3+4 |
| 45 | Dragon's Descent | u/f+3+4 | During Dragon Charge | u/f+3+4 |
| 60 | Tricky Trap | 1 | After Fake Step succeeds | 1 |
| 61 | Tricky Fist | 2 | After Fake Step succeeds | 2 |
| 62 | Tricky Mid Kick | 3 | After Fake Step succeeds | 3 |
| 63 | Tricky Low Kick | 4 | After Fake Step succeeds | 4 |
| 64 | Dragon Knuckle | 1 | During Fake Step | 1 |
| 67 | Fake Step Uppercut | 2 | During Fake Step | 2 |
| 68 | Dragon Knuckle Spin Kick | 3 | During Fake Step | 3 |
| 69 | Dragon Junkyard Kick | 4, 3 | During Fake Step | 4,3 |
| 70 | Quick Hook | 1+2 | During Fake Step | 1+2 |
| 71 | Ab Cruncher | 3+4 | During Fake Step | 3+4 |
| 73 | Dragon Cannon | f+3 | During Fake Step | f+3 |
| 74 | Dragon's Flight | f+4 | During Fake Step | f+4 |
| 75 | Dragon Killer | f+3+4 | During Fake Step | f+3+4 |
| 76 | Dragon Arrow | b+3+4 | During Fake Step | b+3+4 |
| 77 | Dragon's Descent | u/f+3+4 | During Fake Step | u/f+3+4 |
| 99 | Catapult Kick | u/f+4 | While crouching | u/f+4 |
| 100 | Rainbow Kick | u/f+3+4 | While crouching | u/f+3+4 |
| 108 | Jumping Kick to Somersault | u/f+3, 4 | Back towards enemy | u/f+3,4 |
| 119 | Headlock Kick | 1+3 or 2+4 | Approach from left side (or ) | 1+3, 2+4 |
| 120 | Ball Breaker | 1+3 or 2+4 | Approach from right side (or ) | 1+3, 2+4 |
| 121 | Dragon Bites | 1+3 or 2+4 | Approach from behind (or ) | 1+3, 2+4 |
| 126 | Parry | b+1+3, b+2+4 | Time with enemy attack (or ) | b+2+4, b+1+3 |

## Unmatched (UNMAPPED by name)

These TTT2 Law moves have no Buffalo Bill entry at any candidate input. They stay UNMAPPED by name; no row was invented for them.

| TTT2 row | TTT2 name | notation_std | condition |
| --- | --- | --- | --- |
| 3 | Left Right Dragon Fist Combo | 1, 2, f+2, 2 |  |
| 4 | Left Right Blazing Fist Combo | 1, 2, f+2, 1+2 |  |
| 7 | Rage Dragon Combo | 2, 2, 1, 2 |  |
| 14 | Rave War Combo | f+2, 2, 2 |  |
| 15 | Blazing Fist Combo | f+2, 2, 1+2 |  |
| 39 | Dragon Executioner | f+2, 2, 1, 2 | During Dragon Charge |
| 65 | Dragon Knuckle Combo | 1, f+1 | During Fake Step |
| 66 | Dragon Knuckle Flight | 1, 4 | During Fake Step |
| 72 | Dragon Roar | f+1 | During Fake Step |
| 80 | Blackout Muggin' | u/f+1, 3, 1, 3 | (or during Charge Power Punch ) |
| 85 | Backflipper | u/f+4, 3 |  |
| 87 | Dragon Strike Combo | f, f+2, 1, 3 |  |
| 88 | Dragon Dagger | f, f+2, 3 |  |
| 89 | Dragon Cannon | f, f+3 |  |
| 90 | Sun and Moon | f, f+4, 3 |  |
| 91 | Fury Fist Rush | d, d/f, f+1, 2, 1, 2 |  |
| 110 | 10 Hit Combo 2 | d/f+1, 2, 2, 1, 3, 3, d+3, 4, 4, 4 |  |
| 111 | 10 Hit Combo 3 | d/f+1, 2, 2, 1, 3, 3, d+3, 3, 4, 4 |  |
| 112 | 10 Hit Combo 4 | d/f+1, 3, 2, 2, 3, 3, 3, 4, 3, 4 |  |
| 113 | 10 Hit Combo 5 | d/f+1, 3, 2, 2, 3, 3, d+3, 4, 4, 4 |  |
| 114 | 10 Hit Combo 6 | d/f+1, 3, 2, 2, 3, 3, d+3, 3, 4, 4 |  |
| 125 | Knee Lift | f, f+3+4 | Approach enemy |

Unmatched names, plain list: Left Right Dragon Fist Combo (row 3); Left Right Blazing Fist Combo (row 4); Rage Dragon Combo (row 7); Rave War Combo (row 14); Blazing Fist Combo (row 15); Dragon Executioner (row 39); Dragon Knuckle Combo (row 65); Dragon Knuckle Flight (row 66); Dragon Roar (row 72); Blackout Muggin' (row 80); Backflipper (row 85); Dragon Strike Combo (row 87); Dragon Dagger (row 88); Dragon Cannon (row 89); Sun and Moon (row 90); Fury Fist Rush (row 91); 10 Hit Combo 2 (row 110); 10 Hit Combo 3 (row 111); 10 Hit Combo 4 (row 112); 10 Hit Combo 5 (row 113); 10 Hit Combo 6 (row 114); Knee Lift (row 125).

## Notes for the consuming lane

- Fake Step is the biggest encoding gap: Buffalo Bill has no FS-prefixed inputs at all, so the Fake Step-conditioned TTT2 records land in Ambiguous (neutral input only) or Unmatched (Dragon Knuckle Combo row 65, Dragon Knuckle Flight row 66, Dragon Roar row 72).
- Dragon Charge is partially encoded: the DSS-prefixed inputs that exist in Buffalo Bill take their TTT2 records as Unique; the DSS records whose prefixed form is absent (rows 33, 34, 35, 40, 43, 44, 45) are Ambiguous on the neutral entry, and Dragon Executioner (row 39) is Unmatched.
- The five 10 Hit Combo variants after the first (rows 110 to 114) are all Unmatched; only 10 Hit Combo 1 (row 109) has a Buffalo Bill entry.
- No Buffalo Bill entry was edited, added, or removed by this artifact.
