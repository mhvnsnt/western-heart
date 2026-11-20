# Stance NO-ENTRY close-out — 1,363 → 593 (2026-11-02)

Lane A / A2 (banks + NO-ENTRY lane), Step 2. Tool:
`tools/input-verify/stance_reachability_audit.mjs`, run fresh on `main`
HEAD `1a6c77a7` before and after. Baseline reproduced exactly before any
change (55 fighters, 15,737 inputs, 5,577 prefixed, **NO ENTRY 1,363** —
byte-identical report to the 2026-11-02 Claude-lane baseline).

| run | engine | stance | chain-throw | **NO ENTRY** |
|---|---|---|---|---|
| BEFORE (main) | 2,859 | 1,258 | 97 | **1,363** |
| after stance_after data fixes | 2,859 | 1,968 | 97 | **653** |
| after audit chain-graph fix | 2,859 | 1,968 | 123 | **627** |
| FINAL (both, full-tree re-run) | 2,859 | 2,002 | 123 | **593** |

`tools/anim/plan_coverage_audit.mjs` before/after (real runs):
**1,403 no-clip of 16,696 moves — unchanged.** Expected: `stance_after`
does not affect clip planning. The 1,403 are exactly the six no-bank
fighters (vainabel 75 + ryuji 142 + ryusan 226 + pond 312 + zen 324 +
megami 324), corroborating `docs/handoffs/NO-BANK-FIGHTERS-EVIDENCE-2026-11-02.md`.

## Class (a) — FIXED: 770 moves

### a1. stance_after completions — 744 moves, 19 moveset files

Rule applied, strictly: an entry was added only where the fighter's OWN
file already contains the entry move, identified by (i) the move's name
being the stance itself ("No Sword Stance", "Kincho", "Fujin", "Zenshin",
"Intimidation", "Flea", "Meditation", "Indian Stance"), (ii) the name
carrying the code ("Bad Stomach (BDS)", "Slither Step (SLS)",
"Clockwork (CLK)", "Forward Roll (ROLL)"), (iii) an explicit
"…to \<Stance\>" transition name ("…to Savage Stance (chain)",
"…to Harrier (chain)", "…to Switch Stance", "&gt; Snake Eyes"), or
(iv) anim_ref identity with the base character's own in-repo data file
(byou/rave Five Gates: `3+4` anim `t7:lei:lei_433` = t3-lei's
"Five Gates Form - Snake", etc.). No move was renamed, re-keyed, or
re-classed; the only change in each file is inside its `stance_after`
object (verified: parsed deep-equality outside `stance_after`).

Per fighter (NO-ENTRY before → after): phantom 164→17, koreshi 111→8,
byou 257→65, rave 126→15, bruno 35→0, diablo 30→12, torch 44→9,
zui 36→6, waterfall 19→5, demonio 25→16, michiko 12→4, negativo 14→5,
skull 21→4, retsu 9→4, sha 7→6, sakura 7→6, star 11→10, awapop 39→30
(stance part; see a2 for its throw stages).

Highlights: Yoshimitsu set (phantom/koreshi) — NSS, KIN, FLE, IND, MED,
BDS, DGF, POI + phantom's SLAP_U_SILLY / DEATH_COPTER /
MANJI_SPIN_LOW_KICKS state rows, all from name-exact entry moves that
were already in the files with empty `stance_after`. Lei set (byou/rave)
— the full Five Gates (SNA/DRG/PAN/TGR/CRA) + PHX + PLD + DRU, proven by
anim_ref. Bruno's 35 Savage transitions and Michiko's Harrier
transitions were already named in their data; only the table link was
missing.

### a2. Audit chain-graph correction — 26 moves (tool fix, separate PR)

`fighter.js` `_throwChainPress` / `_startThrowChain`: a chain row that
executes becomes the current throw (its attack is forced `isGrab`), so
the next stage opens from THAT row's name tag. The audit only collected
tags from raw-data grab-flagged moves, so every mid-chain stage read
NO ENTRY even though the engine traverses it. The audit now mirrors the
engine: engine grab test (incl. T3 throw-situation conditions 2..0x17)
plus closure over rows keyed by a reachable tag. Effect: pantera
BACKDROP / POWER_BOMB / SLEEPER / REVERSE_DDT / CHICKEN_WING_FACE_LOCK /
VICTORY_BOMB / BURNING_HAMMER / CANNONBALL_BUSTER / GERMAN_SUPLEX /
INDIAN_DEATH_LOCK / MANHATTAN_DROP stages and awapop ARM_BREAK /
HEEL_HOLD / TRIPLE_SLAPS / TWISTED_NIGHTMARE stages resolve
(chain-throw count 97 → 123). No engine behaviour changed; the audit
was wrong, the game was right.

## Class (b) — the six no-bank fighters: 114 moves (not fixable here)

pond 80 (LAB/SZN/HAZ/DEEP/MIST/STRIDE/RAGE/REV — Raven T7 stance rows),
zen 20 (RAI/WAR/TACKLE/REV), megami 14 (IZU/t8). These belong to the
fighters whose clip banks do not exist; per the Step-1 evidence
(`docs/handoffs/NO-BANK-FIGHTERS-EVIDENCE-2026-11-02.md`) they resolve
only with those banks (T7 live-memory extraction for pond; zen is an
owner-decision no-wire — `docs/decisions/2026-10-24-zen-base-decision.md`;
megami's IZU entry move `f+1+2` "Izumo (stance)" exists in her data and
the one-line `stance_after` wiring is ready to land with the TTT2 bank,
not before). vainabel / ryuji / ryusan have 0 NO-ENTRY inputs.

## Class (c) — remainder: 479 moves, grouped (holdings searched)

- **Tackle-mount family — 128** (TACKLE 114, MD1 6, MD2 6, UT 2).
  Every fighter's TACKLE.\* mount rows exist, and tackle-named openers
  exist (e.g. pantera "Ultimate Tackle"), but NO fighter's data flags a
  tackle as a throw (`isGrab` / `move_class` / T3 throw condition all
  absent), so no tackle can execute as a throw and the mount can never
  open. Fixing this means re-classing strikes as throws — a gameplay
  decision for the moveset lane, not a table completion.
- **Engine contexts that do not exist — 128** (CD 30 crouch dash,
  REV 12 reversal window, ground-state spellings KND 20 / FCD 14 /
  FDFL / FUFL / FDFR / SIT 7, jump spellings 21 incl. dio's JUMP /
  VERTICAL_JUMP / DFLIP set, CH 6 counter-hit, SSL/SSR 6, CROUCHING 4,
  CHARGE 4, ENEMY_WALL_STUN 2, COUNTER_HIT 1, CATCH 1). The data exists;
  `fighter.js` `_inputCtx` / `TekkenBuffer` have no such context to
  resolve against. Engine feature work, itemised here, not table work.
- **Duplicate / artifact spellings — 47** (byou `t7` 25 = T7 bank
  row-id keys `t7.lei_158` with no input notation at all; phantom INS 14
  = the T7-layer spelling of the Indian Stance set — the T8-layer IND
  set is the one wired, from the T8-sourced entry move `d+3+4`;
  cyborgx BKP 5 = second spelling of the wired BACKUP set; CLOCKWORK 2
  = second spelling of the wired CLK set; phantom POISON_WIND 1 =
  second spelling of the wired POI set). One stance can carry only one
  `stance_after` value per entry move; the duplicate sets need a
  dedupe/alias call from the moveset lane.
- **No entry move in the fighter's own data — 176.** Searched per
  fighter; the entry move is simply absent: cyborgx DES 32 + DBT 14
  (Alisa Destroy Form entry absent; DBT's own entry row `DES.f+3`
  "Dual Boot" is gated behind DES), samura1 GMH 14 + GMC 3 + CSK 1
  (Jack codes, no named entries), rin/demonio DVS 13 (Devil rows, no
  entry), byou/rave SLD 15 (Lei lie-slide), gyou/tobi BT_RFF 10
  (back-turned RFF compound — RFF itself resolves), koreshi BT 6,
  phantom/koreshi WFL 4, nightwolf CES 6, diablo WAR 7 (Warrior
  Instinct is an install activation, `1+4__main`, not a stance entry),
  torch TOM 4, kinpo NWG/DST/LCT 7, slice PGR 3, yukihyo SHADOW_STEP 3,
  sha/sakura/star CHAOP 3, zui PHX 2 (his Lei fragment lacks the
  `b+1+4` Phoenix Illusion row), rin CDS 1 (its only candidate name is
  a polluted HTML stance-list blob), and chain stages whose parent
  stage/opener is absent from the file (pantera DHH 2, PD 2,
  DOUBLE_HEEL_HOLD 2 — its incoming row `AIR.d+1+3` is not throw-flagged
  — CROSS_ARM_LOCK 1, ALI 1, BLIND_KICK_HIT 1; awapop BHS 3, ABK 2,
  BTR 2, CHD 2, HHD 2, NTM 2, TSS 2, STB 1), plus ORB 1, TFS 1,
  SPIN_BEHIND 1.

Full per-prefix / per-fighter remainder tables: the FINAL audit report
(`tools/input-verify/stance_reachability_audit.mjs` re-run on the
merged tree) — headline NO ENTRY 593 with the tables reproduced in the
PR proof.
