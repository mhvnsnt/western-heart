# State / stance reachability audit (`tools/input-verify/stance_reachability_audit.mjs`)

**Universal fixes so far (2026-11-01/02):** NO ENTRY **2,237 → 1,363**.
- **Side and back throws:** keys `SIDE_L` / `SIDE_R` / `BACK` resolve like `FLANK_*` (`movesets.js` `FLANK_KEYS`).
- **Heat moves** (`H.`) resolve while Soul Urge is on.
- **Tackles:** a throw named "…Tackle" opens the `TACKLE.` follow-ups.
- **Stance entries from the frame data** (`fighter.js` `stanceAfterFromNotes`): a frame-advantage note naming a stance (`-5 (BT)`, `+3 (MNT)`) or a note saying so ("Transition to NSS", "> DEW") enters that stance. BT works for 48 fighters, plus NSS, MNT, KIN, DEW, HAM, ZEN …
- **Ground states by how the fighter fell:** hit in the back or screwed gives FDFA (face down, head towards). Head towards gives FUHT / FUFA. A normal fall gives FUFT.
- `OTG.` fires on a grounded foe, `WALL.` with the fighter's own back to the wall, and T8 `hFC.` as crouch moves.
- Guard test: `test/stance-reachability.test.mjs`.

**Left:** `TACKLE.` rows of fighters with no tackle throw, and character stances whose entry the data does not name (DRU, NSS remainder, SNA, DRG, CD …).


55 fighters, 15737 move inputs, 5577 of them state / stance-prefixed: engine context 2859, stance entered by a move 1258, chain-throw stage 97, **NO ENTRY 1363** (can never fire).

## Prefixes nothing in the game enters, by moves affected

| prefix | moves | fighters |
|---|---|---|
| TACKLE | 118 | rin, sha, kai, retsu, zen, pantera, demonio, diablo, skull, samura1, sakura, zui +17 |
| DRU | 96 | byou, zui, rave |
| NSS | 91 | phantom, koreshi |
| SNA | 56 | byou, rave |
| DRG | 48 | byou, rave |
| KIN | 48 | phantom, koreshi |
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
| DGF | 22 | phantom, koreshi |
| KND | 20 | byou, rave |
| TGR | 19 | byou, rave |
| MED | 19 | phantom, koreshi |
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
| BT_RFF | 10 | gyou, tobi |
| FUJ | 10 | diablo |
| IZU | 10 | megami |
| ZEN | 9 | demonio |
| SLS | 9 | skull |
| INT | 9 | negativo |
| SNE | 8 | retsu, skull |
| HAR | 8 | michiko |
| HAZ | 7 | pond |
| MD1 | 6 | kai, kingtyrant, star |
| MD2 | 6 | kai, kingtyrant, star |
| SWA | 6 | skull, awapop |
| SLI | 6 | waterfall |
| CH | 6 | waterfall, dio, negativo, slice, chordz |
| CES | 6 | nightwolf |
| DFLIP | 6 | dio |
| BT | 6 | koreshi |
| SWS | 5 | waterfall |
| BKP | 5 | cyborgx |
| CHIN_BASH | 5 | torch |
| DEEP | 5 | pond |
| MIST | 5 | pond |
| STRIDE | 5 | pond |
| BDS | 4 | phantom, koreshi |
| WFL | 4 | phantom, koreshi |
| CROUCHING | 4 | samura1, nightwolf |
| CHARGE | 4 | kinpo, yukihyo |
| FORWARD_OR_BACKWARD_JUMP | 4 | dio |
| JUMP | 4 | dio |
| VERTICAL_JUMP | 4 | dio |
| BACKUP | 4 | cyborgx |
| TOM | 4 | torch |
| t8 | 4 | megami |
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
| CDS | 1 | rin |
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
| CATCH | 1 | yukihyo |
| COUNTER_HIT | 1 | yukihyo |
| ORB | 1 | mariposa-monarch |
| TFS | 1 | buffalo-bill |

## Per fighter

| fighter | inputs | prefixed | engine | stance | throw | NO ENTRY | no-entry prefixes |
|---|---|---|---|---|---|---|---|
| rin | 385 | 103 | 66 | 13 | 0 | 24 | CD (10), DVS (7), TACKLE (5), CDS (1), REV (1) |
| byou | 753 | 366 | 62 | 47 | 0 | 257 | SNA (38), DRU (36), DRG (35), t7 (25), PAN (24), PHX (22), CRA (16), KND (14), FCD (14), TGR (11), PLD (10), SLD (10), SIT (2) |
| tou | 304 | 95 | 64 | 23 | 7 | 1 | REV (1) |
| sha | 350 | 164 | 75 | 82 | 0 | 7 | TACKLE (4), CHAOP (1), REV (1), SOMERSAULT (1) |
| kai | 403 | 156 | 85 | 63 | 0 | 8 | TACKLE (4), MD1 (2), MD2 (2) |
| retsu | 373 | 91 | 64 | 18 | 0 | 9 | SNE (5), TACKLE (4) |
| zen | 324 | 87 | 53 | 14 | 0 | 20 | RAI (8), WAR (7), TACKLE (4), REV (1) |
| gyou | 383 | 191 | 63 | 117 | 4 | 7 | BT_RFF (5), CD (2) |
| pantera | 429 | 191 | 78 | 28 | 45 | 40 | TACKLE (6), CD (4), BACKDROP (3), CHICKEN_WING_FACE_LOCK (2), DHH (2), DOUBLE_HEEL_HOLD (2), PD (2), POWER_BOMB (2), REVERSE_DDT (2), SLEEPER (2), VICTORY_BOMB (2), ALI (1), BLIND_KICK_HIT (1), BURNING_HAMMER (1), CANNONBALL_BUSTER (1), CROSS_ARM_LOCK (1), FDFL (1), FDFR (1), FUFL (1), GERMAN_SUPLEX (1), INDIAN_DEATH_LOCK (1), MANHATTAN_DROP (1) |
| demonio | 326 | 93 | 63 | 5 | 0 | 25 | ZEN (9), DVS (6), TACKLE (5), CD (4), REV (1) |
| phantom | 563 | 260 | 82 | 13 | 1 | 164 | NSS (59), KIN (26), FLE (17), INS (14), IND (12), DGF (11), MED (11), SLAP_U_SILLY (3), BDS (2), DEATH_COPTER (2), MANJI_SPIN_LOW_KICKS (2), POI (2), WFL (2), POISON_WIND (1) |
| diablo | 319 | 87 | 53 | 4 | 0 | 30 | FUJ (10), RAI (8), WAR (7), TACKLE (4), REV (1) |
| skull | 313 | 79 | 54 | 4 | 0 | 21 | SLS (9), SWA (5), TACKLE (4), SNE (3) |
| samura1 | 395 | 148 | 106 | 17 | 0 | 25 | GMH (14), TACKLE (4), GMC (3), CROUCHING (2), CSK (1), ENEMY_WALL_STUN (1) |
| sakura | 350 | 164 | 75 | 82 | 0 | 7 | TACKLE (4), CHAOP (1), REV (1), SOMERSAULT (1) |
| zui | 343 | 175 | 47 | 92 | 0 | 36 | DRU (30), TACKLE (4), PHX (2) |
| kinpo | 251 | 92 | 73 | 4 | 6 | 9 | NWG (3), DST (2), LCT (2), CHARGE (1), REV (1) |
| waterfall | 204 | 72 | 47 | 6 | 0 | 19 | SLI (6), SWS (5), TACKLE (4), SWB (3), CH (1) |
| kingtyrant | 390 | 156 | 85 | 63 | 0 | 8 | TACKLE (4), MD1 (2), MD2 (2) |
| burger | 262 | 80 | 63 | 13 | 0 | 4 | TACKLE (4) |
| awapop | 429 | 132 | 82 | 4 | 7 | 39 | CD (8), TACKLE (5), BHS (3), ABK (2), ARM_BREAK (2), BTR (2), CHD (2), HEEL_HOLD (2), HHD (2), NTM (2), TRIPLE_SLAPS (2), TSS (2), TWISTED_NIGHTMARE (2), REV (1), STB (1), SWA (1) |
| scimitar | 182 | 70 | 53 | 13 | 4 | 0 |  |
| purplerain | 286 | 105 | 68 | 29 | 0 | 8 | TACKLE (4), SSL (2), SSR (2) |
| nightwolf | 243 | 66 | 49 | 4 | 0 | 13 | CES (6), TACKLE (4), CROUCHING (2), SPIN_BEHIND (1) |
| dio | 149 | 59 | 33 | 0 | 0 | 26 | DFLIP (6), FORWARD_OR_BACKWARD_JUMP (4), JUMP (4), TACKLE (4), VERTICAL_JUMP (4), HISENKYAKU (2), CH (1), FORWARD_JUMP_PEAK (1) |
| cyborgx | 323 | 151 | 67 | 19 | 0 | 65 | DES (32), DBT (14), BKP (5), BACKUP (4), TACKLE (4), CLK (3), CLOCKWORK (2), REV (1) |
| michiko | 181 | 56 | 40 | 4 | 0 | 12 | HAR (8), TACKLE (4) |
| star | 427 | 207 | 86 | 110 | 0 | 11 | TACKLE (4), MD1 (2), MD2 (2), CHAOP (1), REV (1), SOMERSAULT (1) |
| torch | 419 | 135 | 73 | 18 | 0 | 44 | CJM (25), CHIN_BASH (5), TACKLE (4), TOM (4), REVERSE_ARM_LOCK (3), ROLL (2), REV (1) |
| bruno | 192 | 89 | 46 | 4 | 4 | 35 | SAV (35) |
| negativo | 155 | 60 | 40 | 6 | 0 | 14 | INT (9), CH (2), SSL (1), SSR (1), TACKLE (1) |
| thor | 342 | 20 | 20 | 0 | 0 | 0 |  |
| yukihyo | 284 | 120 | 71 | 25 | 12 | 12 | CHARGE (3), SHADOW_STEP (3), UT (2), CATCH (1), COUNTER_HIT (1), FDFL (1), FUFL (1) |
| slice | 230 | 79 | 61 | 10 | 3 | 5 | PGR (3), CH (1), ENEMY_WALL_STUN (1) |
| docfrank | 196 | 22 | 22 | 0 | 0 | 0 |  |
| baek-master-white | 51 | 15 | 15 | 0 | 0 | 0 |  |
| mariposa-monarch | 224 | 111 | 48 | 58 | 0 | 5 | TACKLE (4), ORB (1) |
| dxmmii-patchwork | 72 | 15 | 15 | 0 | 0 | 0 |  |
| charger | 218 | 15 | 15 | 0 | 0 | 0 |  |
| dorowani | 108 | 17 | 17 | 0 | 0 | 0 |  |
| chatur | 214 | 31 | 31 | 0 | 0 | 0 |  |
| pond | 312 | 176 | 53 | 39 | 4 | 80 | LAB (39), SZN (14), HAZ (7), DEEP (5), MIST (5), STRIDE (5), REV (3), RAGE (2) |
| ryusan | 226 | 23 | 20 | 3 | 0 | 0 |  |
| tobi | 360 | 193 | 65 | 117 | 0 | 11 | BT_RFF (5), TACKLE (4), CD (2) |
| megami | 324 | 73 | 50 | 9 | 0 | 14 | IZU (10), t8 (4) |
| menajerii | 208 | 15 | 15 | 0 | 0 | 0 |  |
| kronos | 113 | 32 | 32 | 0 | 0 | 0 |  |
| deathfang | 142 | 15 | 15 | 0 | 0 | 0 |  |
| ryuji | 142 | 15 | 15 | 0 | 0 | 0 |  |
| koreshi | 376 | 172 | 61 | 0 | 0 | 111 | NSS (32), KIN (22), FLE (16), IND (12), DGF (11), MED (8), BT (6), BDS (2), WFL (2) |
| rave | 477 | 212 | 59 | 27 | 0 | 126 | DRU (30), PHX (18), SNA (18), DRG (13), CRA (9), PAN (9), TGR (8), KND (6), PLD (6), SLD (5), TACKLE (4) |
| buffalo-bill | 351 | 107 | 79 | 22 | 0 | 6 | TACKLE (4), REV (1), TFS (1) |
| vainabel | 75 | 15 | 15 | 0 | 0 | 0 |  |
| cainelias | 61 | 15 | 15 | 0 | 0 | 0 |  |
| chordz | 225 | 89 | 55 | 29 | 0 | 5 | TACKLE (4), CH (1) |
