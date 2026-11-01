# State / stance reachability audit (`tools/input-verify/stance_reachability_audit.mjs`)

55 fighters, 15737 move inputs, 5577 of them state / stance-prefixed: engine context 2372, stance entered by a move 903, chain-throw stage 65, **NO ENTRY 2237** (can never fire).

## Prefixes nothing in the game enters, by moves affected

| prefix | moves | fighters |
|---|---|---|
| BT | 261 | rin, byou, tou, kai, retsu, zen, pantera, demonio, phantom, diablo, skull, zui +20 |
| TACKLE | 150 | rin, tou, sha, kai, retsu, zen, gyou, pantera, demonio, phantom, diablo, skull +25 |
| H | 99 | rin, tou, sha, kai, retsu, zen, gyou, pantera, demonio, phantom, diablo, skull +21 |
| DRU | 96 | byou, zui, rave |
| NSS | 91 | phantom, koreshi |
| FDFA | 83 | rin, byou, tou, sha, kai, retsu, zen, gyou, pantera, demonio, phantom, diablo +27 |
| hFC | 82 | tou, sha, gyou, pantera, phantom, samura1, sakura, kinpo, burger, awapop, cyborgx, star +6 |
| SIDE_R | 69 | rin, tou, sha, kai, retsu, zen, gyou, pantera, demonio, phantom, diablo, skull +28 |
| SNA | 56 | byou, rave |
| DRG | 48 | byou, rave |
| KIN | 48 | phantom, koreshi |
| WALL | 47 | rin, tou, sha, kai, retsu, zen, gyou, pantera, demonio, phantom, diablo, skull +20 |
| BACK | 45 | rin, tou, sha, kai, retsu, zen, gyou, pantera, demonio, phantom, diablo, skull +28 |
| PHX | 42 | byou, zui, rave |
| SIDE_L | 40 | rin, tou, sha, kai, retsu, zen, gyou, pantera, demonio, phantom, diablo, skull +28 |
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
| rin | 385 | 103 | 52 | 0 | 0 | 51 | CD (10), ZEN (9), DVS (7), H (5), TACKLE (5), BT (4), FDFA (2), OTG (2), SIDE_R (2), BACK (1), CDS (1), REV (1), SIDE_L (1), WALL (1) |
| byou | 753 | 366 | 59 | 0 | 0 | 307 | BT (47), SNA (38), DRU (36), DRG (35), t7 (25), PAN (24), PHX (22), CRA (16), KND (14), FCD (14), TGR (11), PLD (10), SLD (10), FDFA (3), SIT (2) |
| tou | 304 | 95 | 43 | 19 | 0 | 33 | H (11), TACKLE (7), BT (4), BACK (2), FDFA (2), SIDE_R (2), OTG (1), REV (1), SIDE_L (1), WALL (1), hFC (1) |
| sha | 350 | 164 | 58 | 82 | 0 | 24 | hFC (7), TACKLE (4), FDFA (2), H (2), SIDE_R (2), WALL (2), BACK (1), CHAOP (1), REV (1), SIDE_L (1), SOMERSAULT (1) |
| kai | 403 | 156 | 74 | 58 | 0 | 24 | BT (5), TACKLE (4), H (3), FDFA (2), MD1 (2), MD2 (2), SIDE_R (2), WALL (2), BACK (1), SIDE_L (1) |
| retsu | 373 | 91 | 55 | 0 | 0 | 36 | SLS (9), SNE (5), SWA (5), BT (4), TACKLE (4), FDFA (2), SIDE_R (2), WALL (2), BACK (1), H (1), SIDE_L (1) |
| zen | 324 | 87 | 40 | 10 | 0 | 37 | RAI (8), WAR (7), H (5), BT (4), TACKLE (4), FDFA (2), SIDE_R (2), BACK (1), OTG (1), REV (1), SIDE_L (1), WALL (1) |
| gyou | 383 | 191 | 51 | 117 | 0 | 23 | BT_RFF (5), TACKLE (4), H (3), CD (2), FDFA (2), SIDE_R (2), hFC (2), BACK (1), SIDE_L (1), WALL (1) |
| pantera | 429 | 191 | 62 | 17 | 45 | 67 | BT (8), TACKLE (6), CD (4), BACK (3), BACKDROP (3), CH (3), FDFA (3), WALL (3), CHICKEN_WING_FACE_LOCK (2), DHH (2), DOUBLE_HEEL_HOLD (2), PD (2), POWER_BOMB (2), REVERSE_DDT (2), SLEEPER (2), VICTORY_BOMB (2), hFC (2), ALI (1), BLIND_KICK_HIT (1), BURNING_HAMMER (1), CANNONBALL_BUSTER (1), CROSS_ARM_LOCK (1), FDFL (1), FDFR (1), FDFT (1), FUFA (1), FUFL (1), GERMAN_SUPLEX (1), H (1), INDIAN_DEATH_LOCK (1), MANHATTAN_DROP (1), SIDE_L (1), SIDE_R (1) |
| demonio | 326 | 93 | 50 | 0 | 0 | 43 | ZEN (9), DVS (6), TACKLE (5), BT (4), CD (4), H (4), FDFA (2), OTG (2), SIDE_R (2), BACK (1), CDS (1), REV (1), SIDE_L (1), WALL (1) |
| phantom | 563 | 260 | 65 | 0 | 0 | 195 | NSS (59), KIN (26), FLE (17), INS (14), BT (13), IND (12), DGF (11), MED (11), hFC (6), H (3), SLAP_U_SILLY (3), BDS (2), DEATH_COPTER (2), FDFA (2), MANJI_SPIN_LOW_KICKS (2), POI (2), SIDE_R (2), WALL (2), WFL (2), BACK (1), POISON_WIND (1), SIDE_L (1), TACKLE (1) |
| diablo | 319 | 87 | 40 | 0 | 0 | 47 | FUJ (10), RAI (8), WAR (7), H (5), BT (4), TACKLE (4), FDFA (2), SIDE_R (2), BACK (1), OTG (1), REV (1), SIDE_L (1), WALL (1) |
| skull | 313 | 79 | 45 | 0 | 0 | 34 | SLS (9), SWA (5), BT (4), TACKLE (4), SNE (3), FDFA (2), SIDE_R (2), WALL (2), BACK (1), H (1), SIDE_L (1) |
| samura1 | 395 | 148 | 82 | 17 | 0 | 49 | GMH (14), hFC (13), TACKLE (4), GMC (3), H (3), BACK (2), CROUCHING (2), FDFA (2), SIDE_R (2), CSK (1), ENEMY_WALL_STUN (1), SIDE_L (1), WALL (1) |
| sakura | 350 | 164 | 58 | 82 | 0 | 24 | hFC (7), TACKLE (4), FDFA (2), H (2), SIDE_R (2), WALL (2), BACK (1), CHAOP (1), REV (1), SIDE_L (1), SOMERSAULT (1) |
| zui | 343 | 175 | 38 | 73 | 0 | 64 | DRU (30), LWV (11), BT (4), RWV (4), TACKLE (4), H (3), FDFA (2), PHX (2), BACK (1), OTG (1), SIDE_L (1), SIDE_R (1) |
| kinpo | 251 | 92 | 59 | 0 | 2 | 31 | hFC (5), BT (4), TACKLE (4), NWG (3), DST (2), FDFA (2), LCT (2), SIDE_R (2), WALL (2), BACK (1), CHARGE (1), H (1), REV (1), SIDE_L (1) |
| waterfall | 204 | 72 | 41 | 0 | 0 | 31 | BT (6), SLI (6), SWS (5), TACKLE (4), SWB (3), FDFA (2), BACK (1), CH (1), SIDE_L (1), SIDE_R (1), WALL (1) |
| kingtyrant | 390 | 156 | 74 | 58 | 0 | 24 | BT (5), TACKLE (4), H (3), FDFA (2), MD1 (2), MD2 (2), SIDE_R (2), WALL (2), BACK (1), SIDE_L (1) |
| burger | 262 | 80 | 49 | 8 | 0 | 23 | BT (5), TACKLE (4), hFC (4), FDFA (2), H (2), SIDE_R (2), WALL (2), BACK (1), SIDE_L (1) |
| awapop | 429 | 132 | 66 | 0 | 7 | 59 | CD (8), TACKLE (5), hFC (5), BT (4), BHS (3), ABK (2), ARM_BREAK (2), BTR (2), CHD (2), FDFA (2), H (2), HEEL_HOLD (2), HHD (2), NTM (2), SIDE_R (2), TRIPLE_SLAPS (2), TSS (2), TWISTED_NIGHTMARE (2), WALL (2), BACK (1), OTG (1), REV (1), SIDE_L (1), STB (1), SWA (1) |
| scimitar | 182 | 70 | 42 | 9 | 0 | 19 | BT (4), TACKLE (4), H (3), FDFA (2), SIDE_R (2), WALL (2), BACK (1), SIDE_L (1) |
| purplerain | 286 | 105 | 57 | 25 | 0 | 23 | BT (4), TACKLE (4), H (3), FDFA (2), SIDE_R (2), SSL (2), SSR (2), WALL (2), BACK (1), SIDE_L (1) |
| nightwolf | 243 | 66 | 42 | 0 | 0 | 24 | CES (6), BT (4), TACKLE (4), BACK (2), CROUCHING (2), FDFA (2), SIDE_L (1), SIDE_R (1), SPIN_BEHIND (1), WALL (1) |
| dio | 149 | 59 | 28 | 0 | 0 | 31 | DFLIP (6), FORWARD_OR_BACKWARD_JUMP (4), JUMP (4), TACKLE (4), VERTICAL_JUMP (4), FDFA (2), HISENKYAKU (2), BACK (1), CH (1), FORWARD_JUMP_PEAK (1), SIDE_L (1), SIDE_R (1) |
| cyborgx | 323 | 151 | 55 | 12 | 0 | 84 | DES (32), DBT (14), BT (7), BKP (5), BACKUP (4), TACKLE (4), CLK (3), H (3), CLOCKWORK (2), FDFA (2), SIDE_R (2), BACK (1), OTG (1), REV (1), SIDE_L (1), WALL (1), hFC (1) |
| michiko | 181 | 56 | 35 | 0 | 0 | 21 | HAR (8), BT (4), TACKLE (4), FDFA (2), BACK (1), SIDE_L (1), SIDE_R (1) |
| star | 427 | 207 | 67 | 110 | 0 | 30 | hFC (7), H (4), TACKLE (4), FDFA (2), MD1 (2), MD2 (2), SIDE_R (2), WALL (2), BACK (1), CHAOP (1), REV (1), SIDE_L (1), SOMERSAULT (1) |
| torch | 419 | 135 | 64 | 0 | 0 | 71 | CJM (25), HAM (12), BT (6), CHIN_BASH (5), TACKLE (4), TOM (4), REVERSE_ARM_LOCK (3), FDFA (2), ROLL (2), SIDE_R (2), BACK (1), H (1), OTG (1), REV (1), SIDE_L (1), WALL (1) |
| bruno | 192 | 89 | 41 | 0 | 0 | 48 | SAV (35), BT (4), TACKLE (4), FDFA (2), BACK (1), SIDE_L (1), SIDE_R (1) |
| negativo | 155 | 60 | 35 | 0 | 0 | 25 | INT (9), BT (6), CH (2), FDFA (2), BACK (1), SIDE_L (1), SIDE_R (1), SSL (1), SSR (1), TACKLE (1) |
| thor | 342 | 20 | 20 | 0 | 0 | 0 |  |
| yukihyo | 284 | 120 | 47 | 25 | 8 | 40 | OTG (5), hFC (5), H (4), TACKLE (4), CHARGE (3), FDFA (3), SHADOW_STEP (3), SIDE_R (2), UT (2), BACK (1), BM (1), CATCH (1), COUNTER_HIT (1), FDFL (1), FUFA (1), FUFL (1), SIDE_L (1), WALL (1) |
| slice | 230 | 79 | 49 | 5 | 3 | 22 | SNK (5), FDFA (4), PGR (3), H (2), SIDE_R (2), BACK (1), CH (1), ENEMY_WALL_STUN (1), FDFT (1), OTG (1), SIDE_L (1) |
| docfrank | 196 | 22 | 22 | 0 | 0 | 0 |  |
| baek-master-white | 51 | 15 | 15 | 0 | 0 | 0 |  |
| mariposa-monarch | 224 | 111 | 41 | 22 | 0 | 48 | MNT (24), TRT (8), BT (4), TACKLE (4), FDFA (2), SIDE_R (2), BACK (1), H (1), ORB (1), SIDE_L (1) |
| dxmmii-patchwork | 72 | 15 | 15 | 0 | 0 | 0 |  |
| charger | 218 | 15 | 15 | 0 | 0 | 0 |  |
| dorowani | 108 | 17 | 17 | 0 | 0 | 0 |  |
| chatur | 214 | 31 | 31 | 0 | 0 | 0 |  |
| pond | 312 | 176 | 45 | 0 | 0 | 131 | BT (39), LAB (39), SZN (14), HAZ (7), DEEP (5), MIST (5), STRIDE (5), TACKLE (4), REV (3), FDFA (2), RAGE (2), SIDE_R (2), BACK (1), H (1), SIDE_L (1), WALL (1) |
| ryusan | 226 | 23 | 20 | 0 | 0 | 3 | BT (3) |
| tobi | 360 | 193 | 53 | 117 | 0 | 23 | BT_RFF (5), TACKLE (4), H (3), CD (2), FDFA (2), SIDE_R (2), hFC (2), BACK (1), SIDE_L (1), WALL (1) |
| megami | 324 | 73 | 42 | 0 | 0 | 31 | IZU (10), GEN (5), t8 (4), MIA (4), H (2), hFC (2), BACK (1), WALL (1), SIDE_L (1), SIDE_R (1) |
| menajerii | 208 | 15 | 15 | 0 | 0 | 0 |  |
| kronos | 113 | 32 | 32 | 0 | 0 | 0 |  |
| deathfang | 142 | 15 | 15 | 0 | 0 | 0 |  |
| ryuji | 142 | 15 | 15 | 0 | 0 | 0 |  |
| koreshi | 376 | 172 | 48 | 0 | 0 | 124 | NSS (32), KIN (22), FLE (16), IND (12), DGF (11), MED (8), BT (6), hFC (6), H (3), BDS (2), WFL (2), BACK (1), SIDE_L (1), SIDE_R (1), WALL (1) |
| rave | 477 | 212 | 54 | 0 | 0 | 158 | DRU (30), BT (27), PHX (18), SNA (18), DRG (13), CRA (9), PAN (9), TGR (8), KND (6), PLD (6), SLD (5), TACKLE (4), FDFA (2), BACK (1), SIDE_L (1), SIDE_R (1) |
| buffalo-bill | 351 | 107 | 63 | 12 | 0 | 32 | BT (10), hFC (6), TACKLE (4), H (3), FDFA (2), SIDE_R (2), BACK (1), REV (1), SIDE_L (1), TFS (1), WALL (1) |
| vainabel | 75 | 15 | 15 | 0 | 0 | 0 |  |
| cainelias | 61 | 15 | 15 | 0 | 0 | 0 |  |
| chordz | 225 | 89 | 41 | 25 | 0 | 23 | H (6), BT (4), TACKLE (4), FDFA (2), SIDE_R (2), BACK (1), CH (1), SIDE_L (1), WALL (1), hFC (1) |
