# BHEV — Tekken 5 Devil Within AI script format (bhb_ai_*.dat)

Decoded 2026-11-08 from the 12 `bhb_ai_*.dat` files in `raw/romd_out/`
(236/242 DW files extracted). Every file parses cleanly to EOF (+ 8 zero
pad bytes). Parser: `bhev_parse.py` / extractor `bhev_extract.py` /
`bhev_json.py` (in `numbers-hunt/`, plus `/tmp/bhev_full.json` — the full
extraction: states, SUBs, tables, FTBLs, comments, CODE hex).

## 1. Container format (measured, all 12 files)

```
BHEV u32            ; root: 'BHEV' + u32 = total children bytes + 1
  UPDT u32 date     ; 'UPDT ' + 32-byte date string, e.g. "Wed Aug  4 12:11:49 2004"
  NAME u32 name     ; script name, e.g. "ai_main", "ai_boss1"
  ATR  u32 8 zero   ; 8 zero bytes
  DATA ...          ; data tables (see §3)
  STAT ...          ; states (see §2)
  SUB  ...          ; subroutines / named functions (see §4)
  (8 zero pad bytes at EOF)
```

Chunk = `tag(4B) + u32 size + payload`.
- Leaf chunks (UPDT, NAME, ATR, INFO, CODE, STR, CTBL, FTBL, IFDT):
  payload = `size` bytes; span = 8 + size.
- Container chunks (SUB, STAT, STRT, AAS2, RUN, STOP, DATA-outer):
  payload = `size - 1` bytes; span = 8 + size - 1. (The size field counts
  one phantom byte; verified on every container in all 12 files.)
- PROG: span = 8 + size. Payload is either a full AAS2 chunk tree, or an
  8-byte reference `AAS2 <u32 index>` (a stub that runs AAS2 program #1).

## 2. States (STAT)

```
STAT
  STRT  PROG > AAS2 > INFO + CODE (+ FTBL + CTBL)   ; start program
  RUN   PROG > AAS2 > INFO + CODE (+ FTBL + CTBL)   ; run program
  STOP  PROG > AAS2 > INFO + CODE (+ FTBL + CTBL)   ; stop program
  NAME  state name
```

- INFO: 16 bytes, always `ff ff ff ff` + 12 zero bytes.
- CODE: bytecode, sizes all multiples of 8 (8–688 B). 8-byte codes are
  single instructions (`A0/A1/A2 00 0f 00 00 00 00 00` in STOP phases).
- FTBL: per-state float parameters (2–8 f32s). Examples: main ATTACK
  STRT (2.0, 30.0), RUN (180.0, 0.0); boss1 (500000.0, 9500.0),
  (60.0, 3.0), (180.0, 3.0), (24000.0, 13000.0). 180.0 = an angle;
  500000/24000/32000/38000 look like distances (mm); 3.0/60.0/0.1/0.5/
  0.75/0.85 = ratios or times. Exact meaning per parameter is UNMEASURED
  (needs the CODE semantics).
- CTBL: comment strings from the .bhs source, e.g. `mine: ai_main.bhs:
  Last-update`, `AISCRIPT: ATTACK!!`, `aasThkAutoSetAtkTgtToMovePnt`,
  `guard ratio = `, `score = `, `MODE = `, `dist `, `trickcnt `,
  `--------Target Is Near--------`, `!!!COUNTER!!!!`, `btn : -1`.

States per file:
- ai_main: INIT, WAIT, WALK, ATTACK.
- ai_dummy: Dm (empty state, no CODE).
- ai_boss1 (Warden): Start, Wait, Approach, StandUp, Chance, Boss1_Jump,
  AttackNormal, FrontStep. (16 SUBs)
- ai_boss2 (Masks): Start, Wait, Approach, StandUp, Chance,
  TripleAttack, AttackNormal, FrontStep. (19 SUBs)
- ai_boss3 (Drowned Ogre): ModeChange, Hamari, HamariAttack, Start,
  Wait, Mode2Fly, Mode2FlyMove, Mode2FlyWarp, Wait2, Mode2FlyAttack,
  Mode2FlyHoming, Mode2HyperWarp, Mode2ReturnWarp, Mode2FlyEndReq,
  Approach, Attack, JustApproach, Fly, FlyMove, FlyAttack, FlyEndReq,
  HyperWarp, ReturnWarp, Halt, StandUp, Guard, Jump. (13 SUBs)
- ai_boss5_lv1 (Shadow/Unmasked): Hamari, HamariAttack, Start,
  ModeChange, Wait, Approach, Attack, StandUp, Guard. (8 SUBs)
- Wave archetypes (power1, power2, speed, standard1, standard2,
  tricky): Start, Wait, Approach, StandUp, Chance, AttackNormal,
  FrontStep. (18 SUBs each, same names.)

## 3. Data tables (DATA) — the tuning numbers

Outer DATA = NAME + PROG > AAS2 > IFDT + inner DATA (raw numeric table).
IFDT = 4 u32s: `[is_float (0=int, 1=float), dims (1=1D, 2=2D),
rows/count, cols (0 for 1D)]` — verified against every table's length.

Table names (21) and shapes:
- TRICK_FLY / TRICK_GROUND / TRICK_ASSIST / TRICK_COUNTER: trick rows.
  Row = [flag (single-bit u32), min, max, ratings...]. boss1: 1 row x 7
  cols, e.g. TRICK_FLY [2097152, 500, 3000, 1, 1, 1, 1] (flag 2^21,
  range 500–3000). Archetypes: 2 rows x 13 cols, e.g. power1 TRICK_FLY
  row0 [65536, 1000, 4500, 1x10], row1 [4, 0, 2000, 1x10]. Ranges
  differ per archetype: tricky [500, 2500], power1 [1000, 4500],
  speed [1000, 4000], standard1 [2000, 3500]. min/max are most plausibly
  distances (mm); the trailing ratings (4 for boss1, 10 for archetypes)
  are per-level weights — exact meaning UNMEASURED.
- TRICK_NORMAL_1ST/2ND/3RD (boss1/boss2): 14 rows x 7 cols. Row =
  [flag (2^17..2^30, one bit each), min, max, 4 ratings]. Flags ascend
  2^21, 2^22, ... 2^30, then 2^20, 2^19, 2^18, 2^17.
- TRICK_NORMAL (archetypes): 14 rows x 13 cols (same flags, wider rows).
- TRICK_MODE_1/2/3/4 (boss3/boss5): 10 rows x 7 cols.
- TRICK_KAMAE (boss2 only): 1 table.
- WAIT: 1D int, 11 values descending [50, 45, 40, 35, 30, 25, 20, 10,
  5, 2, 0] + trailing slot 17.
- GROUND_WAIT: 1D int, 11 values [120, 105, 90, 75, 60, 50, 40, 30,
  20, 10, 0] + trailing slot 17.
- AFTERATTACK: 2D int, 3 rows x 11 cols: [5,4,3,2,1,1,...] + trailing
  [17, 137285944, 16, 137285904, 0] — the two large values look like
  PS2 addresses (0x082F...); meaning UNMEASURED.
- SPEED: 1D float, 11 values [1.0, 1.0, 1.1, 1.1, 1.2, 1.2, 1.2, 1.3,
  1.3, 1.4, 1.4] + 0.0. IDENTICAL in all 8 files that carry it.
- COUNTER_ATK: 1D int, 6 values [12016, 11842, 11843, 11844, 11845,
  11846] (move IDs) + 2 trailing zeros.
- COUNTER_DMG: [-1, 4036, 4036, 4033, 4033, -1] + 2 zeros.
- COUNTER_DEF: [-1, 12021 x5] + 2 zeros. (-1 = 0xFFFFFFFF = none.)
- SHOTGUN_TABLE (boss2, archetypes): 1D int, 7 bit flags [2^23, 2^24,
  2^25, 2^26, 2^30, 2^20, 2^18] + trailing slot 17.
- ATTACK_RATIO (boss3, boss5 only): 1D float, 4 values [1.43, 1.0,
  0.8, 0.67] + 2 trailing slots (boss3 5th = 2.2528, boss5 5th = 0.0 —
  the one real difference between the two files' ratios).

Full values: `/tmp/bhev_full.json` (also in numbers-hunt/ when landed).

## 4. Subroutines (SUB) — the function table

SUB = NAME + PROG > AAS2 > INFO + CODE (+ FTBL + CTBL). The SUBs' order
in the file defines their function index — that is what the CODE
bytecode calls. Complete lists (index: name):

- boss1 (16): 0 StandUp, 1 Move, 2 CheckTargetEscape, 3 TargetIsEscape,
  4 TargetIsNotEscape, 5 Pursue, 6 CheckCritical, 7 Boss1,
  8 CounterAttack, 9 ModeChange, 10 All, 11 GetTrickID,
  12 CheckEnemyDamege [sic — source typo], 13 PreCheckResetPosition,
  14 ResetPosition, 15 Approach.
- boss2 (19): StandUp, Move, CheckTargetEscape, TargetIsEscape,
  TargetIsNotEscape, Pursue, CheckCritical, ModeChange, TripleAttack,
  CounterAttack, All, Attack, GetTrickID, GetRand, SetAssistData,
  CheckEnemyDamege, PreCheckResetPosition, ResetPosition, Approach.
- boss3 (13): SetWarpPos, SetWarpPosForMISKEY2, SetWarpPosForHyperWarp,
  toStandup, toGuard, GuardAndStandup, GetModeNonBuffer, GetMode,
  AntiHamariInit, AntiHamari, GetTrickTable, GetTrickID, ModeChangeCheck.
- boss5_lv1 (8): AntiHamariInit, AntiHamari, GetModeNonBuffer, GetMode,
  GetTrickTable, GetTrickID, toGuard, ModeChangeCheck.
- power1/power2/speed/standard1/standard2/tricky (18 each, same names):
  Destroy, StandUp, Move, CheckTargetEscape, TargetIsEscape,
  TargetIsNotEscape, Pursue, CheckCritical, CounterAttack, All, Attack,
  GetTrickID, GetRand, SetAssistData, CheckEnemyDamege,
  PreCheckResetPosition, ResetPosition, Approach.
- main (3): DEFAULT_START, DEFAULT_RUN, DEFAULT_STOP (state hooks, not
  callable functions). dummy: none.

## 5. CODE opcodes — NOT decoded (exact gap)

No public BHEV opcode map exists. Searched: GitHub code search for
`bhb_ai`, `BHEV`, `AAS2`, `PROGX` (all dead ends — `bhb_ai` 6 noise
hits, `AAS2` 184k substring hits, `PROGX` no relevant hit); the
Tekken5_Tools repo (smb123w64gb, commit a1df7018) has no BHEV tool.
The CODE bytes ARE extracted (hex in bhev_full.json, ~400 chunks,
sizes multiples of 8). Recurring patterns, recorded not decoded:
`31 XX 08 35 00 11` repeated (XX varies: 00, 20, 29, 2b, 37);
8-byte codes `A0/A1/A2 00 0f 00 00 00 00 00` in STOP phases; `0f 00`
near the end of many CODEs. The map must be derived from the game's
own MIPS BHEV interpreter in the decompressed code blob
(TK5DATA3_code.bin) — find the interpreter loop, recover the opcode
dispatch, and match opcodes against the SUB index tables (§4) and the
IFDT/FTBL parameters (§2–3). That is the precise next step; nothing
here guesses an opcode meaning.

## 6. What this gives HeartMind (no guessing)

- The wave-echo archetype AI shape is now data, not prose: 7 states,
  18 named subroutines, per-archetype TRICK ranges (tricky closes
  [500,2500], power1 reaches [1000,4500]), shared SPEED ladder
  1.0→1.4, shared WAIT/GROUND_WAIT decays, shared COUNTER tables.
- The boss AI shape is data: boss3's 27 states (fly/warp/homing
  modes), boss5's 8 SUBs, ATTACK_RATIO [1.43, 1.0, 0.8, 0.67].
- The DW numbers (meter fill, gem heal/Force, rank thresholds,
  symbols) are NOT in these files — they live in the TK5DATA0/1
  tables (Job 1). The bhb_ai tables cover AI decisions only.
