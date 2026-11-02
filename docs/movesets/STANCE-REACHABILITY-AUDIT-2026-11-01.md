# State / stance reachability audit (`tools/input-verify/stance_reachability_audit.mjs`)

**Universal fixes so far (2026-11-01/02):** NO ENTRY **2,237 → 1,701**.
- **Side and back throws:** keys `SIDE_L` / `SIDE_R` / `BACK` now resolve like `FLANK_*` (`movesets.js` `FLANK_KEYS`).
- **Heat moves** (`H.`, 99 across 33 fighters): resolve while Soul Urge is on.
- **Tackles:** a throw named "…Tackle" opens the `TACKLE.` follow-ups (`fighter.js` `_throwChainPress`).
- **Back-turned (BT):** a frame-advantage note "(BT)" (`-5 (BT)` on block / hit / counter hit) puts the attacker back-turned (`fighter.js` `backTurnAfter`). This unlocks BT for 48 fighters (399 BT moves); BT is no longer on the list.
- Guard test: `test/stance-reachability.test.mjs`.

**Next:** the TACKLE follow-ups with no tackle throw, the ground states (FDFA ...), hFC, WALL, and character stances with no entry move (DRU, NSS ...).


55 fighters, 15737 move inputs, 5577 of them state / stance-prefixed: engine context 2625, stance entered by a move 1154, chain-throw stage 97, **NO ENTRY 1701** (can never fire).

## Prefixes nothing in the game enters, by moves affected

| prefix | moves | fighters |
|---|---|---|
| TACKLE | 118 | rin, sha, kai, retsu, zen, pantera, demonio, diablo, skull, samura1, sakura, zui +17 |
| DRU | 96 | byou, zui, rave |
| NSS | 91 | phantom, koreshi |
| FDFA | 83 | rin, byou, tou, sha, kai, retsu, zen, gyou, pantera, demonio, phantom, diablo +27 |
| hFC | 82 | tou, sha, gyou, pantera, phantom, samura1, sakura, kinpo, burger, awapop, cyborgx, star +6 |
| SNA | 56 | byou, rave |
| DRG | 48 | byou, rave |
| KIN | 48 | phantom, koreshi |
| WALL | 47 | rin, tou, sha, kai, retsu, zen, gyou, pantera, demonio, phantom, diablo, skull +20 |
| PHX | 42 | byou, zui, rave |
| LAB | 39 | pond |
| SAV | 35 | bruno |
| PAN | 33 | byou, rave |
| FLE | 33 | phantom, koreshi |
| DES | 32 | cyborgx |
| CD | 30 | rin, gyou, pantera, demonio, awapop, tobi |
| t7 | 25 | byou |
| CRA | 25 | byou, rave |
| CJM | 25 | torch |
| IND | 24 | phantom, koreshi |
| MNT | 24 | mariposa-monarch |
| DGF | 22 | phantom, koreshi |
| KND | 20 | byou, rave |
| TGR | 19 | byou, rave |
| MED | 19 | phantom, koreshi |
| ZEN | 18 | rin, demonio |
| SLS | 18 | retsu, skull |
| OTG | 17 | rin, tou, zen, demonio, diablo, zui, awapop, cyborgx, torch, yukihyo, slice |
| REV | 16 | rin, tou, sha, zen, demonio, diablo, sakura, kinpo, awapop, cyborgx, star, torch +2 |
| PLD | 16 | byou, rave |
| RAI | 16 | zen, diablo |
| SLD | 15 | byou, rave |
| FCD | 14 | byou |
| WAR | 14 | zen, diablo |
| INS | 14 | phantom |
| GMH | 14 | samura1 |
| DBT | 14 | cyborgx |
| SZN | 14 | pond |
| DVS | 13 | rin, demonio |
| HAM | 12 | torch |
| SWA | 11 | retsu, skull, awapop |
| LWV | 11 | zui |
| BT_RFF | 10 | gyou, tobi |
| FUJ | 10 | diablo |
| BT | 10 | mariposa-monarch, koreshi |
| IZU | 10 | megami |
| CH | 9 | pantera, waterfall, dio, negativo, slice, chordz |
| INT | 9 | negativo |
| SNE | 8 | retsu, skull |
| HAR | 8 | michiko |
| TRT | 8 | mariposa-monarch |
| HAZ | 7 | pond |
| MD1 | 6 | kai, kingtyrant, star |
| MD2 | 6 | kai, kingtyrant, star |
| SLI | 6 | waterfall |
| CES | 6 | nightwolf |
| DFLIP | 6 | dio |
| SWS | 5 | waterfall |
| BKP | 5 | cyborgx |
| CHIN_BASH | 5 | torch |
| SNK | 5 | slice |
| DEEP | 5 | pond |
| MIST | 5 | pond |
| STRIDE | 5 | pond |
| GEN | 5 | megami |
| BDS | 4 | phantom, koreshi |
| WFL | 4 | phantom, koreshi |
| CROUCHING | 4 | samura1, nightwolf |
| RWV | 4 | zui |
| CHARGE | 4 | kinpo, yukihyo |
| FORWARD_OR_BACKWARD_JUMP | 4 | dio |
| JUMP | 4 | dio |
| VERTICAL_JUMP | 4 | dio |
| BACKUP | 4 | cyborgx |
| TOM | 4 | torch |
| t8 | 4 | megami |
| MIA | 4 | megami |
| CHAOP | 3 | sha, sakura, star |
| SOMERSAULT | 3 | sha, sakura, star |
| BACKDROP | 3 | pantera |
| SLAP_U_SILLY | 3 | phantom |
| GMC | 3 | samura1 |
| NWG | 3 | kinpo |
| SWB | 3 | waterfall |
| BHS | 3 | awapop |
| SSL | 3 | purplerain, negativo |
| SSR | 3 | purplerain, negativo |
| CLK | 3 | cyborgx |
| REVERSE_ARM_LOCK | 3 | torch |
| SHADOW_STEP | 3 | yukihyo |
| PGR | 3 | slice |
| CDS | 2 | rin, demonio |
| SIT | 2 | byou |
| CHICKEN_WING_FACE_LOCK | 2 | pantera |
| DHH | 2 | pantera |
| DOUBLE_HEEL_HOLD | 2 | pantera |
| PD | 2 | pantera |
| POWER_BOMB | 2 | pantera |
| REVERSE_DDT | 2 | pantera |
| SLEEPER | 2 | pantera |
| VICTORY_BOMB | 2 | pantera |
| FDFL | 2 | pantera, yukihyo |
| FDFT | 2 | pantera, slice |
| FUFA | 2 | pantera, yukihyo |
| FUFL | 2 | pantera, yukihyo |
| DEATH_COPTER | 2 | phantom |
| MANJI_SPIN_LOW_KICKS | 2 | phantom |
| POI | 2 | phantom |
| ENEMY_WALL_STUN | 2 | samura1, slice |
| DST | 2 | kinpo |
| LCT | 2 | kinpo |
| ABK | 2 | awapop |
| ARM_BREAK | 2 | awapop |
| BTR | 2 | awapop |
| CHD | 2 | awapop |
| HEEL_HOLD | 2 | awapop |
| HHD | 2 | awapop |
| NTM | 2 | awapop |
| TRIPLE_SLAPS | 2 | awapop |
| TSS | 2 | awapop |
| TWISTED_NIGHTMARE | 2 | awapop |
| HISENKYAKU | 2 | dio |
| CLOCKWORK | 2 | cyborgx |
| ROLL | 2 | torch |
| UT | 2 | yukihyo |
| RAGE | 2 | pond |
| ALI | 1 | pantera |
| BLIND_KICK_HIT | 1 | pantera |
| BURNING_HAMMER | 1 | pantera |
| CANNONBALL_BUSTER | 1 | pantera |
| CROSS_ARM_LOCK | 1 | pantera |
| FDFR | 1 | pantera |
| GERMAN_SUPLEX | 1 | pantera |
| INDIAN_DEATH_LOCK | 1 | pantera |
| MANHATTAN_DROP | 1 | pantera |
| POISON_WIND | 1 | phantom |
| CSK | 1 | samura1 |
| STB | 1 | awapop |
| SPIN_BEHIND | 1 | nightwolf |
| FORWARD_JUMP_PEAK | 1 | dio |
| BM | 1 | yukihyo |
| CATCH | 1 | yukihyo |
| COUNTER_HIT | 1 | yukihyo |
| ORB | 1 | mariposa-monarch |
| TFS | 1 | buffalo-bill |

## Per fighter

| fighter | inputs | prefixed | engine | stance | throw | NO ENTRY | no-entry prefixes |
|---|---|---|---|---|---|---|---|
| rin | 385 | 103 | 61 | 4 | 0 | 38 | CD (10), ZEN (9), DVS (7), TACKLE (5), FDFA (2), OTG (2), CDS (1), REV (1), WALL (1) |
| byou | 753 | 366 | 59 | 47 | 0 | 260 | SNA (38), DRU (36), DRG (35), t7 (25), PAN (24), PHX (22), CRA (16), KND (14), FCD (14), TGR (11), PLD (10), SLD (10), FDFA (3), SIT (2) |
| tou | 304 | 95 | 59 | 23 | 7 | 6 | FDFA (2), OTG (1), REV (1), WALL (1), hFC (1) |
| sha | 350 | 164 | 64 | 82 | 0 | 18 | hFC (7), TACKLE (4), FDFA (2), WALL (2), CHAOP (1), REV (1), SOMERSAULT (1) |
| kai | 403 | 156 | 81 | 63 | 0 | 12 | TACKLE (4), FDFA (2), MD1 (2), MD2 (2), WALL (2) |
| retsu | 373 | 91 | 60 | 4 | 0 | 27 | SLS (9), SNE (5), SWA (5), TACKLE (4), FDFA (2), WALL (2) |
| zen | 324 | 87 | 49 | 14 | 0 | 24 | RAI (8), WAR (7), TACKLE (4), FDFA (2), OTG (1), REV (1), WALL (1) |
| gyou | 383 | 191 | 58 | 117 | 4 | 12 | BT_RFF (5), CD (2), FDFA (2), hFC (2), WALL (1) |
| pantera | 429 | 191 | 68 | 25 | 45 | 53 | TACKLE (6), CD (4), BACKDROP (3), CH (3), FDFA (3), WALL (3), CHICKEN_WING_FACE_LOCK (2), DHH (2), DOUBLE_HEEL_HOLD (2), PD (2), POWER_BOMB (2), REVERSE_DDT (2), SLEEPER (2), VICTORY_BOMB (2), hFC (2), ALI (1), BLIND_KICK_HIT (1), BURNING_HAMMER (1), CANNONBALL_BUSTER (1), CROSS_ARM_LOCK (1), FDFL (1), FDFR (1), FDFT (1), FUFA (1), FUFL (1), GERMAN_SUPLEX (1), INDIAN_DEATH_LOCK (1), MANHATTAN_DROP (1) |
| demonio | 326 | 93 | 58 | 4 | 0 | 31 | ZEN (9), DVS (6), TACKLE (5), CD (4), FDFA (2), OTG (2), CDS (1), REV (1), WALL (1) |
| phantom | 563 | 260 | 72 | 13 | 1 | 174 | NSS (59), KIN (26), FLE (17), INS (14), IND (12), DGF (11), MED (11), hFC (6), SLAP_U_SILLY (3), BDS (2), DEATH_COPTER (2), FDFA (2), MANJI_SPIN_LOW_KICKS (2), POI (2), WALL (2), WFL (2), POISON_WIND (1) |
| diablo | 319 | 87 | 49 | 4 | 0 | 34 | FUJ (10), RAI (8), WAR (7), TACKLE (4), FDFA (2), OTG (1), REV (1), WALL (1) |
| skull | 313 | 79 | 50 | 4 | 0 | 25 | SLS (9), SWA (5), TACKLE (4), SNE (3), FDFA (2), WALL (2) |
| samura1 | 395 | 148 | 90 | 17 | 0 | 41 | GMH (14), hFC (13), TACKLE (4), GMC (3), CROUCHING (2), FDFA (2), CSK (1), ENEMY_WALL_STUN (1), WALL (1) |
| sakura | 350 | 164 | 64 | 82 | 0 | 18 | hFC (7), TACKLE (4), FDFA (2), WALL (2), CHAOP (1), REV (1), SOMERSAULT (1) |
| zui | 343 | 175 | 44 | 77 | 0 | 54 | DRU (30), LWV (11), RWV (4), TACKLE (4), FDFA (2), PHX (2), OTG (1) |
| kinpo | 251 | 92 | 64 | 4 | 6 | 18 | hFC (5), NWG (3), DST (2), FDFA (2), LCT (2), WALL (2), CHARGE (1), REV (1) |
| waterfall | 204 | 72 | 44 | 6 | 0 | 22 | SLI (6), SWS (5), TACKLE (4), SWB (3), FDFA (2), CH (1), WALL (1) |
| kingtyrant | 390 | 156 | 81 | 63 | 0 | 12 | TACKLE (4), FDFA (2), MD1 (2), MD2 (2), WALL (2) |
| burger | 262 | 80 | 55 | 13 | 0 | 12 | TACKLE (4), hFC (4), FDFA (2), WALL (2) |
| awapop | 429 | 132 | 72 | 4 | 7 | 49 | CD (8), TACKLE (5), hFC (5), BHS (3), ABK (2), ARM_BREAK (2), BTR (2), CHD (2), FDFA (2), HEEL_HOLD (2), HHD (2), NTM (2), TRIPLE_SLAPS (2), TSS (2), TWISTED_NIGHTMARE (2), WALL (2), OTG (1), REV (1), STB (1), SWA (1) |
| scimitar | 182 | 70 | 49 | 13 | 4 | 4 | FDFA (2), WALL (2) |
| purplerain | 286 | 105 | 64 | 29 | 0 | 12 | TACKLE (4), FDFA (2), SSL (2), SSR (2), WALL (2) |
| nightwolf | 243 | 66 | 46 | 4 | 0 | 16 | CES (6), TACKLE (4), CROUCHING (2), FDFA (2), SPIN_BEHIND (1), WALL (1) |
| dio | 149 | 59 | 31 | 0 | 0 | 28 | DFLIP (6), FORWARD_OR_BACKWARD_JUMP (4), JUMP (4), TACKLE (4), VERTICAL_JUMP (4), FDFA (2), HISENKYAKU (2), CH (1), FORWARD_JUMP_PEAK (1) |
| cyborgx | 323 | 151 | 62 | 19 | 0 | 70 | DES (32), DBT (14), BKP (5), BACKUP (4), TACKLE (4), CLK (3), CLOCKWORK (2), FDFA (2), OTG (1), REV (1), WALL (1), hFC (1) |
| michiko | 181 | 56 | 38 | 4 | 0 | 14 | HAR (8), TACKLE (4), FDFA (2) |
| star | 427 | 207 | 75 | 110 | 0 | 22 | hFC (7), TACKLE (4), FDFA (2), MD1 (2), MD2 (2), WALL (2), CHAOP (1), REV (1), SOMERSAULT (1) |
| torch | 419 | 135 | 69 | 6 | 0 | 60 | CJM (25), HAM (12), CHIN_BASH (5), TACKLE (4), TOM (4), REVERSE_ARM_LOCK (3), FDFA (2), ROLL (2), OTG (1), REV (1), WALL (1) |
| bruno | 192 | 89 | 44 | 4 | 4 | 37 | SAV (35), FDFA (2) |
| negativo | 155 | 60 | 38 | 6 | 0 | 16 | INT (9), CH (2), FDFA (2), SSL (1), SSR (1), TACKLE (1) |
| thor | 342 | 20 | 20 | 0 | 0 | 0 |  |
| yukihyo | 284 | 120 | 55 | 25 | 12 | 28 | OTG (5), hFC (5), CHARGE (3), FDFA (3), SHADOW_STEP (3), UT (2), BM (1), CATCH (1), COUNTER_HIT (1), FDFL (1), FUFA (1), FUFL (1), WALL (1) |
| slice | 230 | 79 | 55 | 5 | 3 | 16 | SNK (5), FDFA (4), PGR (3), CH (1), ENEMY_WALL_STUN (1), FDFT (1), OTG (1) |
| docfrank | 196 | 22 | 22 | 0 | 0 | 0 |  |
| baek-master-white | 51 | 15 | 15 | 0 | 0 | 0 |  |
| mariposa-monarch | 224 | 111 | 46 | 22 | 0 | 43 | MNT (24), TRT (8), BT (4), TACKLE (4), FDFA (2), ORB (1) |
| dxmmii-patchwork | 72 | 15 | 15 | 0 | 0 | 0 |  |
| charger | 218 | 15 | 15 | 0 | 0 | 0 |  |
| dorowani | 108 | 17 | 17 | 0 | 0 | 0 |  |
| chatur | 214 | 31 | 31 | 0 | 0 | 0 |  |
| pond | 312 | 176 | 50 | 39 | 4 | 83 | LAB (39), SZN (14), HAZ (7), DEEP (5), MIST (5), STRIDE (5), REV (3), FDFA (2), RAGE (2), WALL (1) |
| ryusan | 226 | 23 | 20 | 3 | 0 | 0 |  |
| tobi | 360 | 193 | 60 | 117 | 0 | 16 | BT_RFF (5), TACKLE (4), CD (2), FDFA (2), hFC (2), WALL (1) |
| megami | 324 | 73 | 47 | 0 | 0 | 26 | IZU (10), GEN (5), t8 (4), MIA (4), hFC (2), WALL (1) |
| menajerii | 208 | 15 | 15 | 0 | 0 | 0 |  |
| kronos | 113 | 32 | 32 | 0 | 0 | 0 |  |
| deathfang | 142 | 15 | 15 | 0 | 0 | 0 |  |
| ryuji | 142 | 15 | 15 | 0 | 0 | 0 |  |
| koreshi | 376 | 172 | 54 | 0 | 0 | 118 | NSS (32), KIN (22), FLE (16), IND (12), DGF (11), MED (8), BT (6), hFC (6), BDS (2), WFL (2), WALL (1) |
| rave | 477 | 212 | 57 | 27 | 0 | 128 | DRU (30), PHX (18), SNA (18), DRG (13), CRA (9), PAN (9), TGR (8), KND (6), PLD (6), SLD (5), TACKLE (4), FDFA (2) |
| buffalo-bill | 351 | 107 | 70 | 22 | 0 | 15 | hFC (6), TACKLE (4), FDFA (2), REV (1), TFS (1), WALL (1) |
| vainabel | 75 | 15 | 15 | 0 | 0 | 0 |  |
| cainelias | 61 | 15 | 15 | 0 | 0 | 0 |  |
| chordz | 225 | 89 | 51 | 29 | 0 | 9 | TACKLE (4), FDFA (2), CH (1), WALL (1), hFC (1) |
