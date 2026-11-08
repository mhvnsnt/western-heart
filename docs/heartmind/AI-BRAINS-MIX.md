# AI brains — the mix: Devil Within × Urban Reign, for Western Heart

**Date:** 2026-11-08
**Task:** design the mix of Devil Within's AI brains and Urban Reign's AI
brains into Western Heart's brawler (HeartMind), per Jay (2026-11-08 ~13:03):
get all the AI brains wired up — a mix of how it works in Devil Within
(Tekken 5) and especially how it works in Urban Reign. UR is one of his
favorite games.
**Method:** design + decode first; no code changes, no PR. The wiring goes
through the wiring coordinator (Pieces 4–5) once this design lands.
**Principle:** DW gives the brawler its brain SCRIPTS — per-archetype trick
tables, counters, mode changes, anti-juggle-lock. UR gives the brawler its
FEEL + its partner system — the 3-press string, timed dodge, grapple depth,
weapons, SPA, and the earned corner partner with double-team. Ours is the
frame: the descent (5 stages, waves → boss), the souls (Nine-Soul Meter,
embers, stands), the wrestling language (card / corner / tag), and
per-character stories. Nothing in either source game's story is copied.
**Canon:** no Jin Kazama in the game at all (only the soul JIN); Pantera is
male (he/him). No commercial code copied — behavior is measured and rebuilt
in our own code.

## 1. The Devil Within brains (measured)

Source: 12 `bhb_ai_*.dat` BHEV compiled behavior scripts in
`~/workspace/devil-within-decode/raw/romd_out/` — inventoried in
`~/workspace/devil-within-decode/numbers-hunt/NUMBERS-HUNT-LOG.md` §5 and
re-verified this pass by `strings` with byte offsets (all 12 files).
Format: `BHEV` magic + u32 size + `UPDT ` + build date (Jan 2004–Jan
2005) + `NAME` + script name; sections `NAME` / `PROG` / `AAS2` /
`IFDT` / `CODE` / `FTBL` / `CTBL` / `DATA` / `SUB`. A behavior-script VM.
**The numeric tuning values (ATTACK_RATIO values, SHOTGUN_TABLE entries,
COUNTER values, guard-ratio numbers) live as bytecode immediates inside
the DATA/CODE sections — extracting exact values needs the BHEV opcode
map, which is NOT on disk.** Follow-up agent 7c62d5d1 is on that decode
(Tekken5_Tools decompressor + BHEV opcode map). Until it lands, the mix
uses the TABLE SHAPES with our own values, labelled with source +
uncertainty — never presented as DW's numbers.

| Script (size, date) | Archetype | Trick tables + systems (byte offsets, this pass) |
|---|---|---|
| `ai_main` (1,328 B, Aug 4 2004) | The shared driver | DEFAULT_START / DEFAULT_RUN / DEFAULT_STOP; `AISCRIPT: ATTACK!!` @1112; ATTACK @1312. The attack driver every archetype runs under. |
| `ai_dummy` (160 B, Jan 26 2004) | The do-nothing brain | No trick tables, no systems. The held state — the model for a non-attacking echo under the closest-attacker rule (§3). |
| `ai_power1` (10,976 B) / `ai_power2` (10,800 B) (Jan 25 2005) | Brute (power) | TRICK_FLY @104, GROUND @304, ASSIST @504, NORMAL @648 (one table, not 1ST/2ND/3RD), AFTERATTACK @1768/1600, TRICK_COUNTER @3960/3792, CheckCritical @5680/5512, COUNTER_ATK @5768/5600, COUNTER_DMG @5880/5712, COUNTER_DEF @5992/5824, GetTrickID @6504/6336, DATA_TRICK_* @7024+/6856+. |
| `ai_speed` (10,688 B, Jan 25 2005) | Fast echo | Same shape as power (FLY @104, GROUND @304, ASSIST @504, NORMAL @648, AFTERATTACK @1488, COUNTER @3680, CheckCritical @5400, COUNTER_* @5488/5600/5712, GetTrickID @6224, DATA_TRICK_* @6744+). |
| `ai_standard1` / `ai_standard2` (10,688 B, Jan 25 2005) | Standard echo | Same shape as power/speed, PLUS **SHOTGUN_TABLE @3568** (a spread table — the gunner shape lives here too, not only in tricky). |
| `ai_tricky` (10,800 B, Jan 25 2005) | Gunner / tricky | Same shape, PLUS **SHOTGUN_TABLE @3680**. |
| `ai_boss1` (10,784 B, Jan 23 2005) | Warden (Modified Gun Jack) | TRICK_FLY @104, GROUND @224, ASSIST @344, NORMAL_1ST @464, 2ND @1008, 3RD @1552 (a 3-stage chain — the only boss with numbered NORMAL stages), AFTERATTACK @2344, Boss1_Jump @4784, TRICK_COUNTER @4816, CheckCritical @6152, COUNTER_ATK @6440, COUNTER_DMG @6552, COUNTER_DEF @6664, ModeChange @7432, GetTrickID @7752, DATA_TRICK_GROUND @8200, FLY @8219, ASSIST @8235, COUNTER @8254. |
| `ai_boss2` (12,288 B, Jan 24 2005) | Masks (Heihachi clones) | TRICK_FLY @104, GROUND @248, ASSIST @392, **TRICK_KAMAE @536 (a stance table)**, NORMAL_1ST @680, 2ND @1160, 3RD @1672, AFTERATTACK @2432, **TripleAttack @4600/4904/7064**, TRICK_COUNTER @5048, CheckCritical @6368, COUNTER_* @6456/6568/6680, ModeChange @6792, **AIS__GIDX_AI_MODE__I != 2 @7480 (a global AI-mode check)**, !STATE_TripleAttack, !MIS_VALI_ATTACK_INPUT, SHOTGUN_TABLE, GetTrickID @8320, DATA_TRICK_* @8840+. |
| `ai_boss3` (18,032 B, Jan 20 2005) | Drowned Ogre (True Ogre) | **TRICK_MODE_1 @104, MODE_2 @512, MODE_3 @920 (three modes)**, **ATTACK_RATIO @1328**, ModeChange start @1520 / end @1784 / ModeChange @1808, **SetWarpPos @1840, SetWarpPosForMISKEY2 @1992, SetWarpPosForHyperWarp @2400 (warp / hyperwarp)**, **AntiHamariInit @3608, AntiHamari @3704, Hamari Start @4232 / End @4488 / Hamari @4512, HamariAttack Start @4624 / End @4920 / HamariAttack @4944 (anti-juggle-lock + juggle punish)**, GetTrickTable @4976, GetTrickID @5120, **guard ratio = @6168**, ModeChangeCheck @6320, **Mode2FlyWarp START @8120 / END @8642/8768**. The richest AI in the set. |
| `ai_boss5_lv1` (8,912 B, Jan 20 2005) | Shadow / Unmasked | **TRICK_MODE_2 @104, MODE_3 @808, MODE_4 @1512 (three modes, numbered 2–4)**, **ATTACK_RATIO @2216**, AntiHamariInit @2320, AntiHamari @2416, Hamari Start @2904 / End @3160 / Hamari @3184, HamariAttack Start @3296 / End @3592 / HamariAttack @3616, GetTrickTable @3952, GetTrickID @4096, **guard ratio = @5272**, ModeChange start @5512 / end @5792 / ModeChange @5816, ModeChangeCheck @5848. |
| (no boss4) | Soul Sphere | **boss4 does NOT exist — the Soul Sphere needs no body, and that absence IS the design** (confirmed in the DW decode). No BHEV script for it. |

What DW's brains ARE, in one line: every enemy picks its next trick from
a named table (FLY / GROUND / ASSIST / NORMAL / COUNTER / AFTERATTACK),
checks whether it can counter or crit, watches for juggle-lock (and
punishes it), and the bosses switch MODES with different attack ratios —
plus warp. The wave fighters (power/speed/standard/tricky) share one
shape; the bosses each add their own systems.

## 2. The Urban Reign brains (measured)

Source: UR-AI-DECODE.md (this pass) + TEARDOWN-PART-C-URBAN-REIGN.md
§2.2–2.5 (manual). The behavior inventory, with the measured basis per
item:

| UR behavior | Measured basis | What it is |
|---|---|---|
| 3-press string, 3rd juggles → free choice | Manual (Tekken Wiki); Part C §2.2 | The combo shape every fighter uses: three presses, third juggles, then air grapple / special / reposition / grab a weapon. |
| Direction = body region | Manual pp. 22–25 | Up = Head, Left/Right = Upper Body, Down = Lower Body, on strikes AND grapples. |
| Timed dodge / deflect / grapple-break | Manual pp. 32–33 | No block button. Square timed to the attack dodges (several attackers at once); Up/Down + Square reverses; direction + Square deflects (off-balance + reduces enemy SPA); Square timed right breaks a grapple at the grabbed region. |
| Grapple depth | Tekken Wiki; manual | Low/high grapples, air grapples, counters, reversals — each with its own per-character animation. Neutral grapple grabs and holds, front or back. |
| Dash / wall run-up / diving | Manual p. 31 | X to run; run into a wall/enemy/partner → run up it → Circle = Diving Strike, Triangle = Diving Grapple. |
| Double Attack | Manual p. 30 | Triangle when facing, or surrounded by, two enemies hits both at once. |
| Quick Recovery | Manual p. 33 | Square before landing after being launched — up at once, in a chosen direction; avoids down strikes/grapples. |
| SPA meter + 4-direction SPAs + buffs | Manual p. 8, p. 28 | Gauge builds on attacking / being hit / dodging; spendable to recover from stun. Neutral = knockback (cheapest); Up = big slow charged; L/R = multi-hit; Down = buff (Power Up +50% atk / Concentration auto-deflect+break / Super Armor / Arcanum). Un-counterable except by SPA; bufferable. |
| Weapons 30+ | Manual pp. 26–27 | No durability; L1 pickup/discard; thrown-into-air weapons can be caught; Circle/Triangle = weapon attacks (direction = region); Square + X throws (at locked target or nearest enemy); thrown weapons can be knocked down with Circle. Enemies drop recovery items (health / SPA). |
| Environment as weapon | Manual p. 20 | Smash launched enemies into walls/cars/crates/furniture for extra damage; furniture breaks, shelves shed boxes, cars/pinball shatter. |
| Body-region damage | Manual pp. 8, 25 | Head/Upper/Lower each have a health bar; yellow = injured, red = destroyed. Lower destroyed → stuns easily; upper destroyed → drops weapon. |
| Target lock | Manual p. 21 | R1 locks; right stick switches while held. |
| Partner earned by beating | Manual p. 34 / HG101 | A partner is gained by first defeating that character. |
| Partner commands (R2 + button) | Manual p. 34 | R2 = Call for Double-Team; R2 + X = Call for Help (concentrated attack on locked-on enemy); R2 + Circle = Split Up; R2 + Square = Pass Weapons/Items; R2 + Triangle = Switch Fighters. |
| Double-team attacks | Manual p. 34 | R2 near partner, or attack when player + partner surround / face / stand behind an enemy — attack differs by partner. Signature: launch an enemy and the partner catches + slams them on the concrete. |
| Grapple assist | Manual p. 34 | Approach an enemy the partner is grappling, press Circle for an extra attack on the held enemy. |
| Switch rule + fail condition | Manual p. 34, p. 20 | Switching is seamless, but the mission FAILS if Brad Hawk's HP hits zero even while controlling the partner. |
| Mission cast (named, 1–5 fighters) | Mission .bin 172-byte records (§2.2 of UR-AI-DECODE.md): 255 records, 51 ids; spawn X/Z + facing per fighter; +22 stat (1000 default; 1500 in mission 100; 100 once in mission 59) | UR missions name their exact cast — not a random mob. Each fighter spawns at a measured point, facing a measured direction. |
| Objectives as AI drivers | FAQ mission list (100 missions) | Take everyone down (49); single target (27); any-one (4, 5); time limit (6, 18, 38, 57, 80); body-region (23, 47, 65, 87); protect (36, 40, 41, 42, 46, 60, 71, 76, 77, 84, 92); crew-first (10, 79). |
| Partner timeline | FAQ mission list | Missions 1–30: NO partner. Mission 31: first partner (Shun Ying Lee). Named partners: Shun Ying Lee, Glen Kluger, Jake Hudson, Dwayne Davis, Grimm, Tong Yoon, Chris Bowman, Kadonashi, Dae-Suk Park, Alex Steiner. |
| Boss shape (single-target duels) | FAQ: Golem (78, 86, 91, 93, 98), Napalm 99 (68, 70, 80, 98), Shinkai (99), Bordin (100) | UR's bosses are single-target "take X down" duels, most with no partner. |

## 3. The mapping — which brain goes to which of OUR roles

Our roles are the brawler's kinds (`game/js/brawler.js`: echo / brute /
gunner / warden / masks / ogre / sphere / shadow) plus the corner partner
(`game/js/heartmind.js` party + `heartmind-flows.js` partnerAfter /
partnerId). Each row names its DW donor, its UR donor, and the measured
basis. Where a DW value is locked behind the BHEV opcode map, the row
says so — the shape wires in now, the exact number wires in when the
decode lands.

| Our role | DW donor (brain script) | UR donor (behavior) | Measured basis |
|---|---|---|---|
| **Echo** (standard wave fighter) | `ai_standard1/2` — TRICK_FLY/GROUND/ASSIST/NORMAL + AFTERATTACK + TRICK_COUNTER + CheckCritical + COUNTER_ATK/DMG/DEF + GetTrickID + DATA_TRICK_* | 3-press string (3rd juggles) + direction = region + timed dodge | DW scripts exist per archetype with the same table shape; UR manual gives the string shape. Echoes are the standard fighters — the standard scripts are their brains. |
| **Echo, fast variant** | `ai_speed` — same table shape, speed archetype | Timed dodge + Quick Recovery | Speed archetype is the fast standard. Quick Recovery is UR's fast-get-up; the fast echo gets it. |
| **Brute** (heavy wave fighter) | `ai_power1/2` — TRICK_FLY/GROUND/ASSIST/NORMAL (one table) + AFTERATTACK + TRICK_COUNTER + COUNTER_* | Grapple depth (low/high/air/counters/reversals) + Double Attack (hit two at once when surrounded) | Power archetype is the heavy standard. Brutes already hunt throws in code (22% — `brawler.js` `_updateMelee`); the mix makes it table-driven (TRICK_NORMAL chain + COUNTER tables) and adds the surround Double Attack. |
| **Gunner** (ranged wave fighter) | `ai_tricky` + `ai_standard1/2` — **SHOTGUN_TABLE** (tricky @3680, standard1/2 @3568) — a spread table | Weapon behavior (pick up / use / throw; thrown weapons can be caught or knocked down) + keep-distance | The SHOTGUN_TABLE is a spread-shot table in the tricky + standard scripts — the gunner's spread shape. UR gives the weapon rules (no durability, throw at locked/nearest target). Exact spread values stay UNMEASURED until the BHEV opcode map lands. |
| **Warden** (stage 1 boss) | `ai_boss1` — NORMAL_1ST/2ND/3RD chain + Boss1_Jump + TRICK_COUNTER + ModeChange + AFTERATTACK | Boss shape: single-target "take X down" duel (UR's Golem/Napalm/Shinkai/Bordin missions) | Boss1 is the first boss script (Jan 23 2005, the earliest boss). Its 3-stage NORMAL chain is the Warden's chain. The Warden already slams a heavy projectile (`brawler.js` `_wardenSlam`); the mix adds the chain + jump + counter + mode change. |
| **Masks** (stage 2 boss) | `ai_boss2` — TRICK_KAMAE (stance) + TripleAttack + AI-mode check (`AIS__GIDX_AI_MODE__I != 2`) + SHOTGUN_TABLE | Crew-first shape (missions 10/79: "take X's men down" — the leader is not the target, the crew is) + the multi-face idea | Boss2 is the clones boss (many faces, same man). TRICK_KAMAE is the only stance table in the set — the Masks change stance between faces. The Masks already wear echo faces in code; the mix adds the stance + triple attack + the AI-mode gate. |
| **Drowned Ogre** (stage 3 boss) | `ai_boss3` — TRICK_MODE_1/2/3 + ATTACK_RATIO + AntiHamari/Hamari + warp/hyperwarp + Mode2FlyWarp + guard ratio | Toughest-single-enemy shape (UR's Golem: missions 78/86/91/93/98) + "take X down" duel | Boss3 is the richest AI in the set (18,032 B, the biggest script). The ogre already teleports + fires a homing volley + fire blast (`brawler.js` `_ogreTricks`); the mix makes it MODE-driven (3 modes, different attack ratios, warp per mode) and adds anti-juggle-lock + the juggle punish. |
| **Soul Sphere** (stage 4 boss) | **NONE — boss4 does not exist** (confirmed absence; the Sphere needs no body) | Wave structure: the mission cast (named fighters, measured spawn points) + "take everyone down" objective | The Sphere spawns monsters the way UR missions spawn their fighter roster — a named cast at measured points, not a random mob. No brain script is owed for it; the spawn logic IS its brain. |
| **Shadow / Unmasked** (stage 5 boss) | `ai_boss5_lv1` — TRICK_MODE_2/3/4 + ATTACK_RATIO + AntiHamari/Hamari + ModeChange + guard ratio | Final-boss duels (Shinkai m99, Bordin m100 — single enemy, no partner, "take X down") | Boss5 is the last boss script (the shadow/unmasked). Its modes are numbered 2–4 (the mode the fight starts in is itself a state). The shadow already surges at full meter in code; the mix adds modes + ratios + anti-juggle-lock. |
| **Corner partner** (e.g. Demonio in Pantera's corner) | `ai_main` — DEFAULT_START/RUN/STOP + `AISCRIPT: ATTACK!!` (the shared attack driver) | **The full UR partner system** — earned by beating; 5 R2 commands; double-team triggers (surround/face/behind + launch-and-catch slam); grapple assist; protect objectives; switch rule; fail condition | UR's partner system is the only partner AI in either source — DW has no partner. Pantera's flow already names it (`heartmind-flows.js`: `PANTERA_PARTNER_AFTER = 'masks'`, `PANTERA_PARTNER_ID = 'demonio'`; `heartmind.js` party.members + partnerBeat). The partner runs the shared attack driver (ai_main) + the UR command set. |

## 4. Wiring spec — what changes, in what order

Target files (all read this pass, repo-main sparse clone at `fcaa8b1d` —
read-only; the wiring coordinator owns the branches + PRs):
`game/js/brawler.js` (1,492 lines; `BrawlerAI` + `BrawlerGame`),
`game/js/heartmind-flows.js` (243 lines; per-character flows),
`game/js/heartmind.js` (661 lines; party + story hooks),
`game/js/ai.js` (413 lines; `AIController` + YUKA CombatBrain, versus),
`game/js/ai-behavior.js` (135 lines; behavior-tree layer +
`pickAttacker` + `chooseStrategy`/`chooseExecution` + `AIPool`).
Integration law (repo AGENTS.md): everything wires INTO the Tekken
menu/system structure — the brawler already lives inside it; the
partner commands go through the existing input/command layer, never a
new parallel menu. Work-order law: short jobs first, one piece playable
before the next; the partner AI is the long job — checkpoint it.

### Step 1 — Trick-table attack selection (BrawlerAI) [SHORT]
Replace the random limb picks in `BrawlerAI._updateMelee`
(`brawler.js`, in-range branch: `['1','2','3','4']` random + brutes
hunt throws at 22%) with per-kind trick tables: FLY / GROUND / ASSIST /
NORMAL (+ NORMAL_1ST/2ND/3RD chains for bosses) + COUNTER +
AFTERATTACK, driven by `GetTrickID` shape (pick by state: airborne →
FLY table; grounded → GROUND; after an attack → AFTERATTACK; on a
read → COUNTER). Data shape from the DW scripts (§1); values are OURS
until the BHEV values land (labelled with source + uncertainty).
Proof: a wave fight where echoes visibly use different tricks by
state (air vs ground vs after-attack), watched in motion.

### Step 2 — Closest-attacker-only (BrawlerAI + ai-behavior.js) [SHORT]
Wire `ai-behavior.js` `pickAttacker` (already written, tested, NOT used
by the brawler today) into `BrawlerAI.update`: in multi-enemy waves
only the closest echo attacks; the rest hold / orbit (the DW packs
already circle the player — `brawler.js` orbit strafing stays).
Non-attacking echoes run the `ai_dummy` shape (the do-nothing brain).
This is the anti-overwhelm rule (Glasheer pattern, already cited in
ai-behavior.js). Proof: a 4-echo wave where only one presses at a time.

### Step 3 — Timed dodge / deflect / grapple-break for enemies [SHORT]
Replace the random 50/50 block-or-dodge roll in `_updateMelee`
(reactive defense: `Math.random() < react * dt * 2.4`, then 50% block /
50% dodge) with UR's timed window: the enemy dodges when the player's
attack is about to land (timed to the attack), deflects on direction +
dodge (throws the player off balance, reduces the player's SPA gauge),
and breaks a grapple timed to the grabbed region. The reaction stat
stays as the timing window (tighter window = better enemy). Proof:
enemies visibly dodging on the player's swing, not blocking at random.

### Step 4 — Counter system (CheckCritical + COUNTER_*) [MEDIUM]
Enemies counter on a read: after a successful dodge/deflect, or when
the player whiffs in range, the enemy answers from its COUNTER table
(COUNTER_ATK / COUNTER_DMG / COUNTER_DEF shape from the DW scripts).
`CheckCritical` shape: a crit check on counter hits (DW's critical
hits). Values ours until the BHEV values land. Proof: a counter
exchange watched in motion (dodge → counter → damage number).

### Step 5 — Anti-juggle-lock (AntiHamari / Hamari) [MEDIUM]
Cap consecutive juggle hits per enemy (DW's AntiHamari): after N
juggle hits the enemy breaks out (Hamari) and answers with a
HamariAttack punish. This is the juggle-lock guard — the player can
still juggle, but not forever. N is OURS until the BHEV values land.
Proof: a juggle that breaks out at the cap, with the punish visible.

### Step 6 — Boss modes (TRICK_MODE + ATTACK_RATIO + ModeChange) [MEDIUM]
Ogre + Shadow switch modes at HP thresholds (DW's TRICK_MODE_1/2/3 and
2/3/4 + ATTACK_RATIO + ModeChange): each mode has its own attack
ratio (which tricks it favors) and its own movement (ogre warp per
mode — the existing teleport becomes mode-driven; Mode2FlyWarp shape).
Warden gets its NORMAL_1ST/2ND/3RD chain + Boss1_Jump + its own
ModeChange. Masks get TRICK_KAMAE (stance per face) + TripleAttack +
the AI-mode gate. Mode changes are telegraphed (the DW scripts have
ModeChange start/end markers — ours shows the change). Proof: a boss
fight where the boss visibly changes behavior at each HP threshold.

### Step 7 — Gunner spread + weapons [MEDIUM]
Gunners fire a spread from the SHOTGUN_TABLE shape (values ours until
the BHEV values land) instead of the single shot today
(`_updateRanged` fires one projectile). Then UR's weapon rules: enemies
pick up weapons lying in the arena, use them (direction = region),
throw them (at the locked/nearest target), and drop recovery items
(health / SPA) on defeat. The brawler already has a pickups array
(`this.pickups`, embers heal 22) — weapons join it as a pickup kind.
Proof: a gunner firing a spread; an enemy picking up and throwing a
weapon; a recovery drop on defeat.

### Step 8 — Partner AI, the corner (the long job) [LONG — checkpoint it]
The biggest piece; checkpoint after each sub-step. Target: the corner
partner fights beside the player under the UR command set, translated
to wrestling language (mission = CARD, partner = CORNER, double-team =
TAG — Pantera's flow already uses this language).
- 8a. **Follow + fight:** the partner follows the player, attacks the
  nearest enemy (closest-attacker rule, Step 2), and runs the shared
  attack driver (`ai_main` shape) + the 3-press string. The partner is
  a second `BrawlerAI` instance with kind `partner` (new kind) driven
  by the flow's `partnerId`.
- 8b. **Commands:** the five R2 commands, on the existing input layer:
  Call for Double-Team (partner comes to double-team position), Call
  for Help (partner concentrates on the locked-on enemy), Split Up
  (partner handles the other enemies), Pass Weapons/Items (partner
  hands over a weapon or ember), Switch Fighters (take control of the
  partner — between fights only, per the campaign rule; the trial
  still fails if the anchor fighter's HP hits zero, UR's Brad rule).
  Names stay OUT of UI until Jay calls them (calls #5 Twin Strike for
  the double-team name; the command names are PROPOSED, not used).
- 8c. **Double-team attacks:** launch-and-catch slam (player launches
  an enemy, the partner catches + slams them on the concrete) +
  surround/face/behind triggers (attack when player + partner
  surround an enemy, face one directly, or stand behind one) +
  grapple assist (approach an enemy the partner is grappling, extra
  attack on the held enemy). The attack differs by which character
  the partner is (per the flow's partnerId).
- 8d. **Protect objectives:** in protect cards (UR missions 36, 40,
  41, 42, 46, 60, 71, 76, 77, 84, 92), the partner is a VIP — the
  trial fails if the partner's HP hits zero. The partner AI plays
  defensively in those cards (stays near the player, dodges more).
- Proof per sub-step: a live playthrough, phone-size, video — the
  partner visibly following, answering a command, landing a
  double-team slam, and (for 8d) a protect card failed by the
  partner falling.

### Step 9 — Objectives as AI drivers [MEDIUM]
Wave tables (`brawler.js` WAVE_TABLES + per-character
`waveTables` in `heartmind-flows.js`) gain an objective per zone,
from UR's taxonomy (§2 of UR-AI-DECODE.md): take everyone down
(default), single target (the boss is the target; the crew is not),
any-one (first takedown ends the zone), time limit (the AI presses
harder as the clock runs down), body-region (the AI guards the
targeted region; destroying it stuns/disarms per UR's rules),
protect (Step 8d). The objective drives spawn (the mission cast:
named fighters at measured points — UR-AI-DECODE.md §2.2) and AI
aggression. Proof: one zone per objective type, played.

### Step 10 — SPA use by AI [MEDIUM — after Piece 4]
After Piece 4 wires the SPA meter shape into the brawler: AI fighters
spend their gauge on the 4-direction SPAs (neutral knockback when
surrounded, Up big hit, L/R multi-hit, Down buff) and spend it to
recover from stun — the same rules as the player (UR manual p. 8, p.
28). SPAs stay un-counterable except by SPA. Proof: an enemy visibly
spending its gauge on a SPA.

## 5. What stays OUT until its decode lands

- **Exact DW tuning values** — ATTACK_RATIO numbers, SHOTGUN_TABLE
  entries, COUNTER_ATK/DMG/DEF values, guard-ratio numbers. The mix
  uses the table SHAPES with our own values, labelled with source +
  uncertainty. They wire in when the BHEV opcode map lands
  (follow-up agent 7c62d5d1).
- **UR record-field meanings** — +4, +20, +22 (health-candidate),
  +24, +28, +30, +48 (= 77), +120/+124, +148, and header 0x02,
  0x1e, 0x24, 0x74, 0xac. Distributions measured
  (UR-AI-DECODE.md §2); meanings need the fighter-table consumers
  (global 0x94D170) — the next disassembly step.
- **The `ao_cplayer.cpp` decision logic** — the module is identified
  (string 0x006bb7d8), its reference sites were NOT located with the
  lui+addiu method (method limit). Next step: pointer-table scan +
  the fighter-table consumers. Until then, the per-decision triggers
  are UNMEASURED.
- **UR frame data / timings** — no UR frame data was measured. The
  mix uses the manual's shapes + our own timings, labelled as such.
- **UR's story** — Brad Hawk, Green Harbor, the gang plot, the
  named roster (Shun Ying Lee, Glen Kluger, Shinkai, Bordin…).
  Behavior only, never the plot or the names. The one documented
  canon link (Glen Kluger → Cain Elias's moveset source) is
  unchanged.
- **DW's numbers** — meter/gem/Force/rank/symbol values. The hunt
  proved no number table exists in any readable byte; they live
  inside TK5DATA0's encrypted bulk (follow-up agent 7c62d5d1).
  The flow keeps its built values until real numbers land.
- **Stage020 geometry** — LAST BOSS FLOOR (mission 99) is still
  undecodable in-VM; the Editor-on-Windows route is the unblocker.

## Sources

- `~/workspace/western-heart-audit/UR-AI-DECODE.md` (this pass) —
  UR's enemy + partner AI as measured (mission data, FAQ taxonomy,
  ELF module map).
- `~/workspace/western-heart-audit/TEARDOWN-PART-C-URBAN-REIGN.md`
  §2.2–2.5 — the manual behavior list with page cites.
- `~/workspace/devil-within-decode/numbers-hunt/NUMBERS-HUNT-LOG.md`
  §5 — the DW BHEV inventory (re-verified this pass with byte
  offsets for all 12 scripts).
- `~/workspace/devil-within-decode/raw/romd_out/bhb_ai_*.dat` — the
  12 BHEV scripts themselves (strings verified this pass).
- `~/workspace/western-heart-audit/PANTERA-HEARTMIND.md` +
  `game/js/heartmind-flows.js` (repo-main, `fcaa8b1d`) — Pantera's
  flow: partnerAfter 'masks', partnerId 'demonio', wave tables,
  echo pool, DW donors (the template the mix follows).
- `game/js/brawler.js` (repo-main, `fcaa8b1d`) — `BrawlerAI`
  (kinds, approach/orbit, reactive defense, ranged, ogre tricks,
  warden slam) + `BrawlerGame` (wave tables, spawn queue, embers,
  projectiles, pickups) — the code the wiring spec targets.
- `game/js/ai.js` + `game/js/ai-behavior.js` (repo-main,
  `fcaa8b1d`) — the versus AI (`AIController` + YUKA CombatBrain)
  and the behavior-tree layer (`pickAttacker` closest-only,
  `chooseStrategy`/`chooseExecution`, `AIPool`) the brawler mix
  reuses.
- `~/workspace/western-heart-audit/PIECE4-BRIEF.md` +
  `PIECE5-BRIEF.md` — the wiring pieces this design feeds (UR feel
  layer + UR structure layer); the wiring coordinator owns the
  branches + PRs.
- `~/workspace/western-heart-audit/HEARTMIND-JAY-CALLS.md` — call
  #5 (Twin Strike, the double-team name) and the other pending
  name calls the mix must not pre-empt in UI.
