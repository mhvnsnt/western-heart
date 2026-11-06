# State / stance reachability audit (`tools/input-verify/stance_reachability_audit.mjs`)

**Universal fixes so far (2026-11-01/02, roster-100 S9 2026-11-05):** NO ENTRY **2,237 → 1,363 → 593 → 561**.
- **Side and back throws:** keys `SIDE_L` / `SIDE_R` / `BACK` resolve like `FLANK_*` (`movesets.js` `FLANK_KEYS`).
- **Heat moves** (`H.`) resolve while Soul Urge is on.
- **Tackles:** a throw named "…Tackle" opens the `TACKLE.` follow-ups.
- **Stance entries from the frame data** (`fighter.js` `stanceAfterFromNotes`): a frame-advantage note naming a stance (`-5 (BT)`, `+3 (MNT)`) or a note saying so ("Transition to NSS", "> DEW") enters that stance. BT works for 48 fighters, plus NSS, MNT, KIN, DEW, HAM, ZEN …
- **Ground states by how the fighter fell:** hit in the back or screwed gives FDFA (face down, head towards). Head towards gives FUHT / FUFA. A normal fall gives FUFT.
- `OTG.` fires on a grounded foe, `WALL.` with the fighter's own back to the wall, and T8 `hFC.` as crouch moves.
- Guard test: `test/stance-reachability.test.mjs`.
- **Stance entries completed from each fighter's own data (2026-11-02 closeout):** NO ENTRY **1,363 → 593** (`docs/handoffs/STANCE-NOENTRY-CLOSEOUT-2026-11-02.md`).
- **Duplicate stance spellings + Megami's Izumo entry (roster-100 S9, 2026-11-05):** NO ENTRY **593 → 561** — `stance_alias` in the moveset data slots the duplicate-spelling rows on the entered spelling (phantom INS → IND, POISON_WIND → POI; cyborgx BKP → BACKUP, CLOCKWORK → CLK), and Megami's own `stance_after` wires f+1+2 → IZU (`docs/movesets/NO-ENTRY-S9-REAUDIT-2026-11-05.md`).

**Left (2026-11-05):** the tackle family (owner gameplay decision), Pond's SZN / DEEP / REV / RAGE rows (no entry move named anywhere in her data — Wave 3 item 6 record in the roster-100 handoff), the dataset row-id artifact keys (byou `t7.*`, megami `t8.*` — no input notation exists for them anywhere in the repo), Zen's stance rows (owner no-bank decision), and genuine no-entry-move gaps — full accounting in `docs/movesets/NO-ENTRY-S9-REAUDIT-2026-11-05.md`.
- **Crouch-dash + sidestep-side contexts (roster-100 L5, 2026-11-06):** NO ENTRY **561 → 539** — `CD.` resolves while a fighter's OWN declared crouch-dash entry move is in its window (`cd_entry` in the moveset data: rin `f,n,d,d/f`, demonio `f,n,d,df`, gyou `d,d/f`; the buffer latches the context off the f,n,d,d/f motion itself), and `SSL.` / `SSR.` resolve during a sidestep toward the foe's left / right (`ssSide` in `fighter.js` `_inputCtx`, side derived from the engine's own flank convention). Fight-proven: demonio/rin/gyou CD rows fire from the motion, Purplerain's SSL.3+4 and SSR.3+4 fire off the matching sidesteps. CD rows for awapop / pantera / tobi stay NO ENTRY — their files declare no crouch-dash entry anywhere (no entry move named, no `stance_after` into CD). Guard test: `test/cd-ss-contexts.test.mjs`.
- **Pond's stance entries (roster-100 Wave 3 item 6, 2026-11-06):** NO ENTRY **539 → 483** — Pond's `stance_after` now wires the entries her own data declares, on every playable spelling: LAB via b+3+4 (her T7-layer row is named "Labyrinth"), MIST via 3+4 (her canon row is named "MIST"; the T7-layer spelling is named "Haze"), STRIDE via qcf (her canon row is named "WATER STRIDE"). `stance_alias` unifies HAZ into MIST — the HAZ rows are renamed duplicates of the canon MIST rows, so the alias slots the two HAZ-only inputs (HAZ.F / HAZ.U) onto MIST.F / MIST.U and the canon rows keep the five shared strike inputs. Fight-proven through the real input path (entries end in their stances; follow-ups fire LAB.1 / MIST.1 / STRIDE.1): `docs/proof/2026-11-06/item6-pond-stances/`. SZN / DEEP / REV / RAGE stay NO ENTRY — no entry move is named for them anywhere in her data (SZN's "Blind Labyrinth" is a from-SZN row, input `SZN.B`, not an entry). Guard test: `test/pond-stances.test.mjs`.


55 fighters, 15737 move inputs, 5577 of them state / stance-prefixed: engine context 2881, stance entered by a move 2090, chain-throw stage 123, **NO ENTRY 483** (can never fire).

## Prefixes nothing in the game enters, by moves affected

| prefix | moves | fighters |
|---|---|---|
| TACKLE | 118 | rin, sha, kai, retsu, zen, pantera, demonio, diablo, skull, samura1, sakura, zui +17 |
| DES | 32 | cyborgx |
| t7 | 25 | byou |
| KND | 20 | byou, rave |
| REV | 16 | rin, tou, sha, zen, demonio, diablo, sakura, kinpo, awapop, cyborgx, star, torch +2 |
| SLD | 15 | byou, rave |
| FCD | 14 | byou |
| WAR | 14 | zen, diablo |
| CD | 14 | pantera, awapop, tobi |
| GMH | 14 | samura1 |
| DBT | 14 | cyborgx |
| SZN | 14 | pond |
| DVS | 13 | rin, demonio |
| BT_RFF | 10 | gyou, tobi |
| RAI | 8 | zen |
| MD1 | 6 | kai, kingtyrant, star |
| MD2 | 6 | kai, kingtyrant, star |
| CH | 6 | waterfall, dio, negativo, slice, chordz |
| CES | 6 | nightwolf |
| DFLIP | 6 | dio |
| BT | 6 | koreshi |
| DEEP | 5 | pond |
| WFL | 4 | phantom, koreshi |
| CROUCHING | 4 | samura1, nightwolf |
| CHARGE | 4 | kinpo, yukihyo |
| FORWARD_OR_BACKWARD_JUMP | 4 | dio |
| JUMP | 4 | dio |
| VERTICAL_JUMP | 4 | dio |
| TOM | 4 | torch |
| t8 | 4 | megami |
| CHAOP | 3 | sha, sakura, star |
| GMC | 3 | samura1 |
| NWG | 3 | kinpo |
| BHS | 3 | awapop |
| SHADOW_STEP | 3 | yukihyo |
| PGR | 3 | slice |
| SIT | 2 | byou |
| DHH | 2 | pantera |
| DOUBLE_HEEL_HOLD | 2 | pantera |
| PD | 2 | pantera |
| FDFL | 2 | pantera, yukihyo |
| FUFL | 2 | pantera, yukihyo |
| ENEMY_WALL_STUN | 2 | samura1, slice |
| PHX | 2 | zui |
| DST | 2 | kinpo |
| LCT | 2 | kinpo |
| ABK | 2 | awapop |
| BTR | 2 | awapop |
| CHD | 2 | awapop |
| HHD | 2 | awapop |
| NTM | 2 | awapop |
| TSS | 2 | awapop |
| HISENKYAKU | 2 | dio |
| UT | 2 | yukihyo |
| RAGE | 2 | pond |
| CDS | 1 | rin |
| ALI | 1 | pantera |
| BLIND_KICK_HIT | 1 | pantera |
| CROSS_ARM_LOCK | 1 | pantera |
| FDFR | 1 | pantera |
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
| rin | 385 | 103 | 76 | 13 | 0 | 14 | DVS (7), TACKLE (5), CDS (1), REV (1) |
| byou | 753 | 366 | 62 | 239 | 0 | 65 | t7 (25), KND (14), FCD (14), SLD (10), SIT (2) |
| tou | 304 | 95 | 64 | 23 | 7 | 1 | REV (1) |
| sha | 350 | 164 | 75 | 83 | 0 | 6 | TACKLE (4), CHAOP (1), REV (1) |
| kai | 403 | 156 | 85 | 63 | 0 | 8 | TACKLE (4), MD1 (2), MD2 (2) |
| retsu | 373 | 91 | 64 | 23 | 0 | 4 | TACKLE (4) |
| zen | 324 | 87 | 53 | 14 | 0 | 20 | RAI (8), WAR (7), TACKLE (4), REV (1) |
| gyou | 383 | 191 | 65 | 117 | 4 | 5 | BT_RFF (5) |
| pantera | 429 | 191 | 78 | 28 | 63 | 22 | TACKLE (6), CD (4), DHH (2), DOUBLE_HEEL_HOLD (2), PD (2), ALI (1), BLIND_KICK_HIT (1), CROSS_ARM_LOCK (1), FDFL (1), FDFR (1), FUFL (1) |
| demonio | 326 | 93 | 67 | 14 | 0 | 12 | DVS (6), TACKLE (5), REV (1) |
| phantom | 563 | 260 | 82 | 175 | 1 | 2 | WFL (2) |
| diablo | 319 | 87 | 53 | 22 | 0 | 12 | WAR (7), TACKLE (4), REV (1) |
| skull | 313 | 79 | 54 | 21 | 0 | 4 | TACKLE (4) |
| samura1 | 395 | 148 | 106 | 17 | 0 | 25 | GMH (14), TACKLE (4), GMC (3), CROUCHING (2), CSK (1), ENEMY_WALL_STUN (1) |
| sakura | 350 | 164 | 75 | 83 | 0 | 6 | TACKLE (4), CHAOP (1), REV (1) |
| zui | 343 | 175 | 47 | 122 | 0 | 6 | TACKLE (4), PHX (2) |
| kinpo | 251 | 92 | 73 | 4 | 6 | 9 | NWG (3), DST (2), LCT (2), CHARGE (1), REV (1) |
| waterfall | 204 | 72 | 47 | 20 | 0 | 5 | TACKLE (4), CH (1) |
| kingtyrant | 390 | 156 | 85 | 63 | 0 | 8 | TACKLE (4), MD1 (2), MD2 (2) |
| burger | 262 | 80 | 63 | 13 | 0 | 4 | TACKLE (4) |
| awapop | 429 | 132 | 82 | 5 | 15 | 30 | CD (8), TACKLE (5), BHS (3), ABK (2), BTR (2), CHD (2), HHD (2), NTM (2), TSS (2), REV (1), STB (1) |
| scimitar | 182 | 70 | 53 | 13 | 4 | 0 |  |
| purplerain | 286 | 105 | 72 | 29 | 0 | 4 | TACKLE (4) |
| nightwolf | 243 | 66 | 49 | 4 | 0 | 13 | CES (6), TACKLE (4), CROUCHING (2), SPIN_BEHIND (1) |
| dio | 149 | 59 | 33 | 0 | 0 | 26 | DFLIP (6), FORWARD_OR_BACKWARD_JUMP (4), JUMP (4), TACKLE (4), VERTICAL_JUMP (4), HISENKYAKU (2), CH (1), FORWARD_JUMP_PEAK (1) |
| cyborgx | 323 | 151 | 67 | 33 | 0 | 51 | DES (32), DBT (14), TACKLE (4), REV (1) |
| michiko | 181 | 56 | 40 | 12 | 0 | 4 | TACKLE (4) |
| star | 427 | 207 | 86 | 111 | 0 | 10 | TACKLE (4), MD1 (2), MD2 (2), CHAOP (1), REV (1) |
| torch | 419 | 135 | 73 | 53 | 0 | 9 | TACKLE (4), TOM (4), REV (1) |
| bruno | 192 | 89 | 46 | 39 | 4 | 0 |  |
| negativo | 155 | 60 | 42 | 15 | 0 | 3 | CH (2), TACKLE (1) |
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
| pond | 312 | 176 | 53 | 95 | 4 | 24 | SZN (14), DEEP (5), REV (3), RAGE (2) |
| ryusan | 226 | 23 | 20 | 3 | 0 | 0 |  |
| tobi | 360 | 193 | 65 | 117 | 0 | 11 | BT_RFF (5), TACKLE (4), CD (2) |
| megami | 324 | 73 | 50 | 19 | 0 | 4 | t8 (4) |
| menajerii | 208 | 15 | 15 | 0 | 0 | 0 |  |
| kronos | 113 | 32 | 32 | 0 | 0 | 0 |  |
| deathfang | 142 | 15 | 15 | 0 | 0 | 0 |  |
| ryuji | 142 | 15 | 15 | 0 | 0 | 0 |  |
| koreshi | 376 | 172 | 61 | 103 | 0 | 8 | BT (6), WFL (2) |
| rave | 477 | 212 | 59 | 138 | 0 | 15 | KND (6), SLD (5), TACKLE (4) |
| buffalo-bill | 351 | 107 | 79 | 22 | 0 | 6 | TACKLE (4), REV (1), TFS (1) |
| vainabel | 75 | 15 | 15 | 0 | 0 | 0 |  |
| cainelias | 61 | 15 | 15 | 0 | 0 | 0 |  |
| chordz | 225 | 89 | 55 | 29 | 0 | 5 | TACKLE (4), CH (1) |
