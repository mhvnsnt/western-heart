# Urban Reign AI — decode (measured)

**Date:** 2026-11-08
**Task:** decode Urban Reign's enemy AI + partner AI from real bytes, for the
AI-brains mix with Devil Within. Jay's direction (2026-11-08 ~13:03): get all
the AI brains wired up, the mix of how it works in Devil Within (Tekken 5)
and especially how it works in Urban Reign. UR is one of his favorite games.
**Method:** Capstone 5.0.7 MIPS32 LE on SLUS_212.09 (the same method as the
mission decode); Python `struct` parsing of all 100 mission `.bin` files
(`decoded/inputs/mission_defs/`, 8,300 B each); the mission census
(`decoded/missions/census/`, 404 files); the FAQ mission list
(`decoded/missions/mission-list-faq.txt`, 100 lines); the USA manual as
recorded in TEARDOWN-PART-C-URBAN-REIGN.md §2.2–2.5. No big downloads, no
new clone. Every claim carries its file + field/offset. UNMEASURED stays
UNMEASURED with the reason.
**Canon:** no Jin Kazama in the game at all (only the soul JIN); Pantera is
male (he/him). UR's STORY (Brad Hawk, Green Harbor, the gang plot) is NOT
copied — the AI BEHAVIOR is what's mixed in, not the plot. No commercial
code copied — behavior is measured and rebuilt in our own code.

## 1. UR AI as the player meets it (manual — the behavior list)

Source: the USA manual itself, as recorded in
TEARDOWN-PART-C-URBAN-REIGN.md §2.2–2.5 (manual page cites there). This is
what the AI does in play; §2–§5 below are what the data files say about
who does it and when.

**Enemy behaviors (all fighters, player + AI):**
- **3-press strike string, third hit juggles** — then a free choice: air
  grapple, special move, keep comboing, or run off to grab a weapon /
  reposition. (Manual; Tekken Wiki.)
- **Direction = body region** — Up = Head, Left/Right = Upper Body, Down =
  Lower Body — on strikes AND grapples. One idea, reused everywhere.
- **No block button — timed dodge instead.** Square timed to the attack
  dodges it; dodges several attackers at once. Up/Down + Square reverses
  it. Direction + Square deflects (throws the opponent off balance and
  reduces the enemy SPA gauge). Square timed right breaks a grapple,
  aiming at the body region grabbed. (Manual pp. 32–33.)
- **Grapple depth** — low and high grapples, air grapples, counters and
  reversals, each with its own per-character animation; neutral grapple
  grabs and holds, front or back. (Tekken Wiki: "highly reminiscent of
  Tobal 2".)
- **Dash / run-up** — X to run; running into a wall, enemy, or partner
  lets the character run up it, then Circle = Diving Strike, Triangle =
  Diving Grapple. (Manual p. 31.)
- **Double Attack** — Triangle when directly facing, or surrounded by,
  two enemies hits both at once. (Manual p. 30.)
- **Quick Recovery** — Square before landing after being launched gets the
  character up at once, in a chosen direction; avoids down strikes and
  down grapples. (Manual p. 33.)
- **SPA meter** — builds on attacking, being attacked, or dodging/
  deflecting; can also be spent to recover from a stunned state. Two
  buttons (Circle + Triangle): neutral = all-directions knockback
  (cheapest, usable standing or lying face-up); Up = big slow charged
  attack; Left/Right = quicker multi-hit combo; Down = status buff, not
  an attack (Power Up +50% attack, Concentration auto-deflects / auto
  grapple-breaks, Super Armor less damage + no stagger, Arcanum unlocks
  special moves). SPAs cannot be countered, reversed, or dodged except
  by another SPA; they can be buffered. (Manual p. 8, p. 28.)
- **Weapons** — 30+ (bats, pipes, bottles, shovels, 2x4s, knives, broken
  bottles). No durability — lasts until dropped. L1 pickup/discard; a
  weapon thrown into the air by a collision can be caught; Circle/
  Triangle while holding = weapon attacks (direction picks region);
  Square + X throws the weapon (at the locked target or nearest enemy);
  a thrown weapon can be knocked down with Circle. Enemies sometimes
  drop recovery items (health or SPA gauge). (Manual pp. 26–27.)
- **Environment as weapon** — smash launched enemies into walls, cars,
  crates, furniture for extra damage; furniture breaks, shelves shed
  boxes, cars and pinball machines shatter; run up walls for Diving
  Strikes. (Manual p. 20.)
- **Body-region damage** — Head / Upper Body / Lower Body each have their
  own on-screen health bar; yellow = injured, red = destroyed.
  Destroying lower body → stuns easily; destroying upper body → enemy
  drops weapon. (Manual pp. 8, 25.)
- **Target lock** — R1 locks a target; right stick switches target while
  R1 is held. (Manual p. 21.)

**Partner behaviors (the heart of it):**
- **Partner earned by first defeating that character.** (Manual p. 34 /
  HG101.)
- **Partner commands (R2):** R2 alone = Call for Double-Team; R2 + X =
  Call for Help (concentrated attack on the locked-on enemy); R2 +
  Circle = Split Up (partner handles the other enemies); R2 + Square =
  Pass Weapons/Items back and forth; R2 + Triangle = Switch Fighters
  (take control of the partner). (Manual p. 34.)
- **Double-Team Attacks:** press R2 near the partner, or attack when the
  player + partner surround an enemy / face one directly / stand behind
  one — the attack differs by which character the partner is. Signature:
  launch an enemy into the air and the partner catches and slams them
  onto the concrete. (Manual p. 34.)
- **Grapple assist:** approach an enemy the partner is grappling, press
  Circle for an extra attack on the held enemy. (Manual p. 34.)
- **Switching is seamless, but the mission still hinges on Brad Hawk:**
  the mission FAILS if Brad Hawk's health reaches zero even while the
  player controls the partner. (Manual p. 34, p. 20.)
- **Mission failure:** objectives unmet or Brad's HP zero → retry menu
  (RETRY / MISSION INFO / QUIT). (Manual p. 20.)

## 2. The mission data = the AI cast (who fights, where, with what)

### 2.1 Header fields — proven map + new correlations (this pass)

Source: SLUS_212.09 disassembly (`decoded/iso/slus_text.asm`, 596,814
instructions) + per-mission value distributions, missions 1–100. The
proven map is in UR-STAGE-MISSION-DECODE-FOLLOWON.md §3; this pass adds
the correlations below, each verified over all 100 missions.

| Offset | Type | Proven meaning | New finding (this pass) |
|---|---|---|---|
| 0x00 | u16 | Per-mission place label (0–25) → stage-name table | — |
| 0x02 | u16 | UNPROVEN | Values {0: 67, 99: 33}. No correlation with fighter count (99-missions have 1–4 fighters, 0-missions 1–5). Stays UNPROVEN. |
| 0x08/0x0c | i32 ×0.001 | Player spawn X/Z (m) | — |
| 0x10 | i16 /32768 | Player spawn facing | — |
| 0x14/0x18/0x1c | i32/i32/i16 | Slot-1 spawn X/Z/facing | — |
| 0x1e | i16 | UNPROVEN | **Measured biconditional: off1e = 1000 ⟺ slot-1 occupied-or-choice (off20 ∈ {−2, positive}), 53/53 missions; off1e ∈ {0, 200, 600, 1500} ⟹ slot-1 empty (off20 = −1), 25/25.** Same value family as the fighter-record field at +22 (see §2.2). Meaning still UNPROVEN — it is loaded as $a1 into the fighter-struct field copier (jal 0x236200, $a0 = slot 1). |
| 0x20 | i16 | Slot-1 presence: −1 = none (47), −2 = special/choice (38), positive = fixed id (15: 3, 15, 19, 20, 21, 30, 31, 40, 41, 42) | — |
| 0x24 | u16 | UNPROVEN | Values {2: 80, 0: 20}. No clean correlation with off02 or off20 (off24 = 0 with off20 = −2 happens once). → fighter struct +0x8C9A. Stays UNPROVEN. |
| 0x28 | u16 | UNPROVEN | **Always 0 in all 100 missions.** → sub-struct pointer in fighter +0x8CEC — always null. Measured constant. |
| 0x74/0x76 | i16 | Condition fields, UNPROVEN | off74 ∈ {0, 1, 3, 7, 8, 11, 21, 27, 28}, nonzero in 21 missions, all missions 50–97. **Tested and FAILED as a fighter id: off74's value is never in the mission's fighter-record ids (0/21 contains).** 18 of the 21 have off20 = −2 (choice path). off76 always 0. Stays UNPROVEN. |
| 0xa8 | u16 (1–5) | Count of 172-byte records at 0x1d4, copied into runtime fighter table (0x271d88) | **offa8 == off1d0 in ALL 100 missions** — the two counts are the same number (1–5). The fighter count. |
| 0xac | u16 | UNPROVEN | Values {0: 46, 65534 (−2): 51, 16: 1, 13: 1, 62: 1}. **Story-phase split measured: offac = 0 in ALL of missions 1–29; −2 in 51 of missions 30–100.** Mission 30 is "Showdown" (vs Dwayne Davis); mission 31 is the FIRST partner mission (Shun Ying Lee) — the switch sits exactly at the mission before partners first appear. The three one-off values (16 @ m46, 13 @ m64, 62 @ m92) are NOT in those missions' fighter-record ids (tested). Meaning still UNPROVEN. |
| 0x15c | u16 (0–2) | Count of 28-byte records at 0x162 | == 2 only in missions 5, 17, 22. |
| 0x1754/56/58 | u16 ×3 | Activation flags → flag array 0xABF9A0[id] = 1 | — |
| 0x1d0 | u16 (1–5) | UNPROVEN (what it counts) | == offa8 in all 100 missions (see above) — it counts the same thing (the fighter roster). |
| 0x1884 | slot table (22×24 B) | UNPROVEN — NO reader in SLUS main.text or any DVP overlay | — |

### 2.2 The 172-byte fighter records — the per-mission AI cast

**offa8 records at 0x1d4, stride 0xac (172 B). 255 records across the 100
missions. 51 distinct fighter ids (3–54 + 61).** Each record is one
fighter in the mission: who it is, where it spawns, which way it faces,
and its per-spawn parameters. Field map measured over all 255 records
(this pass):

| Offset | Type | Values (255 records) | Reading |
|---|---|---|---|
| +0 | u16 | 51 distinct ids (3–54 + 61) | Fighter id (charNNN numbering). Mission 99's single record is id 61 — the final boss Shinkai. Mission 100's two records are ids 8, 9. Mission 1's are 26, 27. |
| +2 | u16 | [0] always | Zero. |
| +4 | u16 | {0: 244, 1: 7, 2: 4} | Small enum, rare nonzero (11/255). **40/51 fighter ids hold a single value** — mostly a per-fighter constant. Meaning UNPROVEN. |
| +6 | u16 | [0] always | Zero. |
| +8 | i32 | 233 distinct | Spawn X (×0.001 m). |
| +12 | i32 | 227 distinct | Spawn Z (×0.001 m). |
| +16 | i16 | Full range −32768..32403 | Facing (i16/32768 of a turn — same unit as the player spawn facing at 0x10). |
| +18 | u16 | {0: 242, 1: 13} | A 0/1 flag on 13 records; clusters in missions 44 (records 1–3) and 78 (records 1–3) — all non-first records. Meaning UNPROVEN. |
| +20 | u16 | {0: 128, 3: 127} | A 0/3 flag, almost exactly half. **Per-mission, not per-fighter** (only 12/51 ids hold a single value; split ~50/50 at every record index 0–3). Meaning UNPROVEN — candidate: spawn group / wave / team, untested. |
| +22 | u16 | {1000: 252, 100: 1, 1500: 2} | **Per-fighter constant (48/51 ids hold a single value).** 1000 is the default (252/255). The two 1500s are BOTH in mission 100, records 0–1 (ids 8, 9 — the final mission's enemies). The single 100 is mission 59, record 1 (id 34). Consistent with a health/stat field (1000 base; tougher in the final mission; one weak enemy) — meaning UNPROVEN, the pattern is the evidence. Same value family as header off1e. |
| +24 | u16 | {0: 115, 20–31: 140} | Per-spawn, not per-fighter (only 7/51 ids hold a single value; id 26 takes {0, 27, 28, 29}). 12 values in 20–31. Meaning UNPROVEN — candidate: weapon / spawn-point / AI-type id, untested. Ids 15, 16, 29, 31, 40, 53, 55–61 (incl. 61 Shinkai) are ALWAYS 0 here. |
| +26 | u16 | [0] always | Zero. |
| +28 | u16 | {0: 156, 1–30} | 26 distinct small values. 22/51 ids hold a single value. Meaning UNPROVEN. |
| +30 | u16 | {0: 206, 23: 32, 24: 17} | 23/24 in 49 records. Meaning UNPROVEN. |
| +32…+46 | u16 | Mostly 0, sparse small values | +48 is constant **77 in all 255 records** (a fixed constant — version tag or fixed parameter, UNPROVEN). +52/+54 ∈ {0, 24} (paired); +62/+64/+66 ∈ {0, 15} (triple). |
| +80/+82/+84 | u16 | {0, 10} (triple) | Sparse. Meaning UNPROVEN. |
| +94…+116 | u16 | {0, 1} flags | Sparse flag fields. Meaning UNPROVEN. |
| +120/+124 | u16 | {0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 15, 20} (both fields, same set) | Paired fields with an identical value set — a progression (0–20). Candidate: AI timing parameters (delay/cooldown in frames?). Meaning UNPROVEN. |
| +144 | u16 | {0, 2, 3} | Sparse. Meaning UNPROVEN. |
| +148 | u16 | {0, 1, 2, 3, 4, 5, 6, 10, 20, 90, 120} | 90/120 stand out (at 60 fps: 90f = 1.5 s, 120f = 2 s). Candidate: a timer. Meaning UNPROVEN. |
| +152/+156/+160 | u16 | {0, 1, 3, 4} / {0, 1, 2} / {0, 2} | Sparse small values. Meaning UNPROVEN. |
| rest | — | 0 | Zero. |

What this gives the mix: UR missions do NOT spawn a generic crowd. Every
mission names its exact cast (1–5 fighters by id), each with its own spawn
point, facing, a 1000-default stat, and per-spawn parameters. That is the
measured shape of UR's encounter design — a named cast, not a random mob.

### 2.3 The mission taxonomy — objectives as AI drivers

From `decoded/missions/mission-list-faq.txt` (100 lines: title, opponents,
partner status, objective). Counts measured this pass:

| Objective | Missions | Shape |
|---|---|---|
| Take everyone down | 49 | Clear the cast. The default. |
| Take X down (single target) | 27 | Duel/boss shape — one named fighter is the target; the rest are the crew. |
| Take one of them down (any one) | 2 (missions 4, 5) | First blood — the fight ends on the first takedown. |
| Take X down within the Time Limit | 5 (6, 18, 38, 57, 80) | Timed — the AI must press, the player must finish. |
| Bust up X's lower body | 3 (23, 47, 87) | Body-region objective (legs). |
| Bust up their upper bodies | 1 (65) | Body-region objective (upper body). |
| Take the enemy down while protecting X | 11 (36, 40, 41, 42, 46, 60, 71, 76, 77, 84, 92) | Protect/escort — the partner is a VIP whose HP is the fail condition. |
| Take X's men down | 2 (10 — Glen's men; 79 — Lin Fong's men) | Crew-first — the leader is not the target, the crew is. |

**Partner timeline (FAQ):** missions 1–30 are ALL "(No Partner)". Mission
31 ("Chaos") is the FIRST partner mission (Shun Ying Lee, NAMED). After
that: "Partner Allowed" (any earned partner) or a NAMED partner. Named
partners earned by beating (mission of first appearance): Shun Ying Lee
(31, 71, 92, 93), Glen Kluger (36), Jake Hudson (37), Dwayne Davis (40),
Grimm (41, 61), Tong Yoon Bulsook (42), Chris Bowman (46, 84), Kadonashi
(48), Dae-Suk Park (60), Alex Steiner (67). Bosses: Golem (78, 86, 91,
93, 98), Napalm 99 (68, 70, 80, 98), Shinkai (99), William Bordin (100),
Douglas McKinzie (69, 70, 81, 94), Lin Fong Lee (79, 85, 93).

## 3. Where the AI code lives in the ELF (Capstone method)

Source: `SLUS_212.09` (6,366,044 B, on disk) + `decoded/iso/
slus_text.asm` (596,814 instructions) + `decoded/inputs/iso/
slus_rodata_strings.txt`. The game's own source paths leak through the
rodata string table — the module map below is measured from those paths
(`../../prog/game/*.cpp`).

| Module (rodata vaddr) | What it is | Code xref found (this pass) |
|---|---|---|
| `ao_cplayer.cpp` (0x006bb7d8) | **The computer player — the AI-controlled fighter module.** "cplayer" = computer player. This is where the enemy/partner decision logic lives. | **NOT located.** The lui+addiu string-address pattern (20-line window, Capstone method) found no reference site for this string. Method limit, NOT absence — the string exists in rodata; the code may load it via a pointer table or a wider window. Next step: pointer-table scan / wider xref pass. |
| `ao_actor.cpp` (0x006b68b0) | The actor/entity system — the base fighter entity the AI drives. | 1 xref at code 0x0020c7a4. |
| `ao_player.cpp` (0x006bb520) | The human player module. | NOT located (same method limit). |
| `ao_character.cpp` (0x006c3d98) | Character data / fighter definitions. | 2 xrefs: 0x0027cc90, 0x0027cd78. |
| `ao_direction.cpp` (0x006c2f40) | Direction / facing logic. | 1 xref at 0x00271b20 — immediately before the mission module. |
| `ao_mission.cpp` (0x006c2f90) | Mission loader (already mapped: 0x271b60–0x274000; loader reads `mission%03d.bin` via jal 0x32a970 sprintf + jal 0x28f480 read; buffer malloc 0x2800 stored at global 0x70BC6C; fighter table → global 0x94D170). | 1 xref at 0x00271bf4 (inside the module). |
| `ao_weapon.cpp` (0x006c3fd8) | Weapon system. | 2 xrefs: 0x0027e214, 0x0027e2dc. |
| `ao_lock.cpp` (0x006c3060) | Target lock (R1). | 1 xref at 0x0027542c. |
| `ao_bodyhit.cpp` (0x006bb6a7) | Body-hit / region damage. | NOT located (method limit). |
| `ao_game.cpp` (0x006b9ca0) | Game flow. | NOT located (method limit). |
| `kg_human.cpp` (0x006b4c28) | Human/character runtime. | 4 xrefs: 0x001e7ab8, 0x001e7e44, 0x001e7fb4, 0x001e8210. |
| `kg_weapon.cpp` (0x006b1930) | Weapon runtime. | 8 xrefs: 0x001cfc2c–0x001d3954. |
| `you_motdat.cpp` (0x006fc4d0) | Motion data. | NOT located (method limit). |

String-table check: the ELF's printable strings carry almost no AI
labels — `COOPER` (a fighter file name, `037_COOPER.gyu`), mission
titles (`$P1"Enemy Stronghold"`, `$P1"Despicable Ally"`), `weapon00–05.
vmd`, `%s %s TEAM WINS`, `Rain`/`RainSys`. The AI decision logic is in
code without string labels (or in the DVP overlays, not searched here).

**What this means:** the AI module is IDENTIFIED (`ao_cplayer.cpp`) but
its decision logic is NOT yet read. The next step is a wider xref pass
(pointer-table scan for 0x006bb7d8; the functions around the located
`ao_actor.cpp` site at 0x0020c7a4; the fighter-table consumers reading
global 0x94D170) — then the per-decision disassembly. Until then the
detailed decision logic (when an enemy attacks / dodges / picks up a
weapon / uses SPA, on what trigger, with what numbers) is UNMEASURED.
The behavior list in §1 + the cast data in §2 + the module map in §3
are what the mix is built on today.

## 4. What is still UNMEASURED

1. **The detailed AI decision logic** inside `ao_cplayer.cpp` /
   `ao_actor.cpp` — triggers, priorities, and numbers for attack /
   dodge / grapple / weapon / SPA decisions. Located the module,
   not the logic. Next step named in §3.
2. **Record-field meanings** — +4, +20, +22 (health-candidate),
   +24, +28, +30, +48 (= 77 constant), +120/+124, +148, and the
   header fields 0x02, 0x1e, 0x24, 0x74, 0xac. Distributions
   measured (§2); meanings need the code that reads them
   (the fighter-table consumers at global 0x94D170).
3. **Frame data / timings** — no UR frame data was measured (the
   manual gives the shape, not numbers; the 484 named moves are
   names on clips, not a frame-data table). Same gap as Part C §4.9.
4. **Per-fighter identities** — which charNNN is which named
   fighter (Brad Hawk, Glen Kluger, Shun Ying Lee, Shinkai…).
   OWNER-pending. The record ids (3–54 + 61) are numbers, not names;
   no identity was guessed here.
5. **Stage geometry for the AI arenas** — stage020 (LAST BOSS FLOOR,
   mission 99) still undecodable in-VM; the Editor-on-Windows route
   is the unblocker (see UR-STAGE-MISSION-DECODE-FOLLOWON.md §2).
6. **The 9 NOT-DECODED missions** (VMDs 7dd4, 01cd, bd01 — missions
   37, 50, 59, 61, 69, 77, 83, 92, 99) — their stage geometry is
   undecodable in-VM, so their arenas' AI navigation data is
   UNMEASURED. Their fighter records ARE decoded (§2.2 covers all
   100 missions).
7. **The 0x1884 slot table** — no reader in SLUS main.text or any
   DVP overlay; likely editor/legacy data the game never reads.

## Sources

- `~/workspace/urban-reign-redux/iso/SLUS_212.09` (6,366,044 B) —
  the ELF this pass disassembled (Capstone 5.0.7, MIPS32 LE).
- `~/workspace/urban-reign-redux/decoded/iso/slus_text.asm`
  (596,814 instructions) + `decoded/inputs/iso/
  slus_rodata_strings.txt` — prior pass's disassembly + string
  table; the xref pass in §3 is this pass's work
  (`/tmp/ur_xref.py`, `/tmp/ur_xref2.py` — ephemeral; method
  recorded here).
- `~/workspace/urban-reign-redux/decoded/inputs/mission_defs/
  mission000–255.bin` (8,300 B each) — the field + record analysis
  in §2 (`/tmp/ur_ai_fields.py`, `/tmp/ur_ai_fields2.py`,
  `/tmp/ur_ai_recs.py`, `/tmp/ur_ai_recs2.py`,
  `/tmp/ur_ai_recs3.py`, `/tmp/ur_ai_recs4.py` — ephemeral;
  distributions recorded here).
- `~/workspace/urban-reign-redux/decoded/missions/census/
  missionNNN.fighters.json` — per-mission fighter VMDs (used to
  test the off74/offac hypotheses; both FAILED as record ids).
- `~/workspace/urban-reign-redux/decoded/missions/
  mission-list-faq.txt` — the 100-mission title/opponent/partner/
  objective list (§2.3).
- `~/workspace/western-heart-audit/TEARDOWN-PART-C-URBAN-REIGN.md`
  §2.1–2.5 — the manual behavior list (§1) with manual page
  cites; §3 (Redux) for the craft references.
- `~/workspace/urban-reign-redux/UR-STAGE-MISSION-DECODE-FOLLOWON.md`
  §3–§4 — the proven mission .bin field map + stage-name table +
  mission→stage PPK links this pass builds on.
- `~/workspace/devil-within-decode/numbers-hunt/NUMBERS-HUNT-LOG.md`
  §5 — the DW BHEV inventory the mix pairs this with (see
  AI-BRAINS-MIX.md).
