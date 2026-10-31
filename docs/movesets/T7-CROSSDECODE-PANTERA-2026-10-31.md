# T7 CROSS-DECODE — PANTERA (2026-10-31)

Lane B2. Owner order (2026-10-31): "those strings that are stuck and blocked
behind Pantera step promotions behind a undeciphered piece of tech and three
data — let's decipher the stuff from the Tekken seven data instead to fix
that."

**The undeciphered piece, named:** King's Tekken 7 **move-link/branch data** —
the cancel graph inside `kinmot.bin` (GRE `teardown/tekken7-steam/tkdata/
mothead/bin/kinmot.bin`, 2,551,112 bytes, sha256
`48f9c91fcdbd0519d1ece97ff827001fe1a3155a6dd775d203be93b42952c729`;
2,787 moves, 11,862 table cancels / 11,879 derived). Two parts of it were
undeciphered when this lane started; both are now deciphered (§1, §2). The
T3 condition decode (#1370) stands untouched — this lane derived nothing
from T3 conditions for Pantera, per the owner's pivot.

All promotions in this lane are **data-level only**. The FK soft gate and
play-verify are still owed before any promoted step is called verified
in-game; every promoted step's appended evidence line says so.

---

## 1. DECIPHERED — the alias table (cancel targets ≥ 0x8000)

Cancel records whose `move_id` is ≥ 0x8000 do not name a move directly; the
low bits are a slot into an alias table. The Batch-1 record noted "the
converter emits no aliases table; 20 distinct King alias slots observed,
slot 1 dominant" — the table itself was never recovered.

**It sits at file offset 0x28 in `kinmot.bin`, inside MovesetInfo: 56 × u16.
A second, byte-identical copy sits at 0x98.** All 56 values are < 2,787
(the move count); 43 are distinct. King's table (slot → move id):

| slot | move | slot | move | slot | move | slot | move |
|---|---|---|---|---|---|---|---|
| 0 | 2699 | 14 | 2720 | 28 | 1423 | 42 | 41 |
| 1 | **1423** | 15 | 1436 | 29 | 1423 | 43 | 44 |
| 2 | 1435 | 16 | 1437 | 30 | 1 | 44 | 2642 |
| 3 | 361 | 17 | 1438 | 31 | 4 | 45 | 2643 |
| 4 | 70 | 18 | 1436 | 32 | 5 | 46 | 241 |
| 5 | 73 | 19 | 338 | 33 | 6 | 47 | 47 |
| 6 | 75 | 20 | 1447 | 34 | 2 | 48 | 1423 |
| 7 | 74 | 21 | 2573 | 35 | 3 | 49 | 1423 |
| 8 | 82 | 22 | 351 | 36 | 1423 | 50 | 1423 |
| 9 | 85 | 23 | 352 | 37 | 33 | 51 | 1423 |
| 10 | 84 | 24 | 353 | 38 | 35 | 52 | 1423 |
| 11 | 83 | 25 | 354 | 39 | 36 | 53 | 1423 |
| 12 | 86 | 26 | 1423 | 40 | 39 | 54 | 1423 |
| 13 | 2719 | 27 | 1423 | 41 | 40 | 55 | 554 |

Semantic confirmation: slot 1 → move **1423 `Kg_sKAM00_`**, the standing
hub (independently identified as the hub in REQUIREMENTS-DECODE-2026-10-30);
2,350 cancels target it (return-to-hub). Slot 2 → 1435 `cKAM__00_` (crouch
hub). Slot 0 → 2699 `Kg_Direct`. Slots 13/14 → 2719/2720 `Grd_STEP_L/R`.
Unused slots default to 1423. The 20 distinct slots actually used by King's
cancels match the old record exactly ({1:2350, 2:189, 3:35, 4:194, 6:83,
7:20, 8:32, 9:75, 10:50, 11:17, 12:36, 13:1, 14:1, 15:36, 16:36, 17:36,
19:54, 21:4, 44:2, 47:1}).

## 2. DECIPHERED — the GROUP cancel system (0x800B delegation)

Requirement decode had named direction `0x800B` "group-list delegation"
without the addressing rule. It is:

- A cancel with **direction 0x800B** delegates to a shared cancel list; its
  **`move_id` field is the start index into the group-cancel pool**
  (3,350 records).
- Groups are **delimited by 0x800C (group-end) rows** in the pool: 82
  groups. **Every one of the 47 start indices delegated from any King move
  coincides exactly with a 0x800C-delimited segment start** — the rule is
  proven, not fitted.
- A move's usable cancels = its own cancel range + the groups it delegates
  to. Moves with `cancel_idx == 0` inherit motOrigin's list (converter rule,
  re-verified here).

This matters because the landed T7 join walked the group pool **flat**
(any group edge available from any state). The flat pool over-approximates:
it lets sidestep/turn-state edges fabricate string continuations. All walks
in this lane are **group-correct** (per-move delegation), with two further
rules the data forced:

- **Hub resets end strings.** An auto-cancel back to the standing/crouch
  hub (1423/1435) is a string end, not a continuation; steps are never
  chained through a hub reset.
- **No start pre-expansion.** A string's first step is consumed from the
  hub's own cancels + its delegated groups only. (Pre-expanding the hub
  pulls in walk/dash/sidestep states whose edges invent continuations.)

**Walker validation** (group-correct, against the landed clip-map
terminals — every one the *unique* open-tier terminal of its walk):
`2,1` → 1550 `Kg_rplu4t` · `f+2,1` → 1594 `Kg_6rplp` · `d+1+2` → 2556
`Kg_WHummer` · `1,2,1` → 1685 `Kg_rplu6` (path: hub —1→ 1592 `Kg_lp00F`
—2→ 1548 `Kg_lprpF` —1→ 1685, all ungated) · `1,2` → 1548 `Kg_lprpF`.

Requirement gates were classified per REQUIREMENTS-DECODE-2026-10-30:
empty runs = **open**; runs inside the standing-action family
{636, 73, 809, 33812, 33471, 33499, 356, 32946} = **basic**; runs adding
the string-stage latch family {811, 361, 33005, 362, 33042, 33044, 33468}
= **stage** (satisfied by being at that string stage — the 361/33005 latch
params increment per stage); anything else = **other** (recorded, never
used as proof).

## 3. THE STUCK SET (F9)

The gap inventory's F9 set is the 57 REVIEW occurrences recorded by PR
#1232 (Batch-1 step plans, `candidate_source: t3-branch-graph`). Since
then the FK wave (#1097 era, landed 2026-10-30) promoted 35 of them;
**19 t3-branch-graph occurrences remained at REVIEW** entering this lane
(3 occurrences from the #1232 record no longer exist as steps — the plan
set was rebuilt by Batches 2–4). The current plan set holds **82 REVIEW
occurrences** in total (19 t3-branch-graph + 62 prefix-move + 1
recorded-dest); this lane adjudicated **all 82** from the T7 graph.

Identity chain used per step (plan key S, step i, candidate row R):
prefix notation → the WH move record for the prefix (authoritative row =
its `t3_row`; `anim_t3` is an approximate anim match and was NEVER used as
identity) → the clip-map join for that move (by its `t7.id`, else by key)
→ the T7 walk of S: the motbin move occupying step i.

### Outcomes (82 occurrences)

| outcome | count | meaning |
|---|---|---|
| PROVEN-T7 | 9 | walk reaches the joined motbin move at the step, open tier |
| PROVEN-STEP0 | 13 | step 0 IS the prefix move (its authoritative row == candidate) and the T7 walk of that input from the hub reaches a unique open-tier attack move — 10 promoted (row 135); 3 withheld (row 117, recorded FK failure) |
| NO-T7-CHAIN | 57 | the T7 walk dead-ends before/at that step — T7 King positively has no such continuation |
| NO-JOIN | 2 | walk reaches the step but there is no clip-map identity bridge, and the occupant is not unique |
| ROW-CONFLICT | 1 | T7 corroborates the move, but WH's own T3 records conflict on its row |

### Promoted (19 occurrences — PR #1384, pantera.json + the FK test)

- **Row 198** — `1,2,1` step 2 (plan keys `1,2,1`, `1,2,1~t7.king`,
  `1,2,1~t7.king.2`, `1,2,1~t7.king.3`) and `f+2,1` step 1 (plan keys
  `f+2,1`, `f+2,1,1`, `f+2,1,1,2`, `f+2,1~t7.king`, `f+2,1~t7.king.2`).
  T7 walks reach motbin 1685 `Kg_rplu6` / 1594 `Kg_6rplp` at open tier —
  exactly the clip-map joins of those strings (king_11 / king_37). The
  candidates came from the T3 branch graph (HARD gates passed); T7 now
  independently proves the strings and their enders. Grade: **strongly
  supported → promoted** (the moves carry no authoritative `t3_row`, so
  the row itself rests on the T3 graph, now T7-corroborated).
- **Row 135** — `d/f+4` family step 0 (10 plan keys: `d/f+4,2`, `d/f+4,3`,
  `d/f+4,3,4` + twins, `d/f+4,3,d+4` + twins, `d/f+4,3~t7.king`,
  `d/f+4,4`). The step is `d/f+4` itself, whose authoritative row is 135.
  Group-correct T7 identity of standing `d/f+4`: the unique open-tier
  move **1660 `Kg_t_srkF`**. Grade: **proven** (own-row + unique T7
  identity). Its Batch-2 record carries a limb-peak *proxy* fail — the
  cheap pre-filter, not the bank-row FK re-run; the full FK re-run and
  play-verify remain owed (the evidence line says so).
- Plan-level fields were updated where the promotions changed the truth:
  `1,2,1` ×4 keys, `f+2,1` ×3 keys and `d/f+4,4` are now `verified-all`;
  `d/f+4,2` is now `partial`. The FK test
  (`test/pantera-fk-promotion.test.mjs`) was updated in the same PR:
  tallies and a locked PROMOTED_T7 set; its FK PROMOTED/GUARDS lists are
  untouched.

Census after promotion: verified 155 → **174**, review 82 → **63**,
unmapped 389 (unchanged).

### Proven identity, promotion withheld (3 occurrences)

- **Row 117** — `d/f+1,2` step 0 (plan keys `d/f+1,2`, `d/f+1,2~t7.king`,
  `df+1,2`). The step is `d/f+1` itself (authoritative row 117), and the
  group-correct T7 identity of standing `d/f+1` is confirmed: the unique
  open-tier move **1652 `Kg_t_slpF`** (dmg 15, startup 14 — startup
  matches Pantera's frame-data record). **Not promoted**: the bank-row
  FK re-run recorded a failure for row 117 (in-window peak 70% of the
  85% bar) and the FK test guards these steps at review. A T7 identity
  proof does not address an FK failure — the unblock for 117 is an FK
  re-run/repair or an owner ruling, not more T7 evidence.

### Not promoted — the evidence

- **NO-T7-CHAIN (57).** Every `d+1+2,2,…` step past step 0 (2556
  `Kg_WHummer` has no input exits at all — in T7 the Atlas Hammer is a
  standalone move, there is no `d+1+2,2,1,1` chain); every `f+2,1,1,…`
  step past `f+2,1` (1594 has no `1` exit — the long T3/T8-era chains do
  not exist in T7); `f+2,1,1,2` step 3 (candidate 258) and all deeper
  `…4,4,4` / `…3,3,4` steps (259/260/261/266/267); `d/f+4,2` step 1
  (candidate 196, recorded-dest — 1660 `Kg_t_srkF` has no `2` exit; the
  string `d/f+4,2` does not exist in T7). These steps stay REVIEW: T7
  absence does not disprove a T3 row, it removes the corroboration the
  owner asked for. They can only move on T3-side proof (branch graph +
  FK) or T8 data.
- **NO-JOIN (2).** `d+3+4,2` step 1 (candidate 196) in plan keys
  `d+3+4,2` and `d+3+4,2,1`. The T7 string exists (step 0 = 1641
  `Kg_Ari_kick`, unique open), but step `2` has **two** open-tier
  occupants — 1642 `Kg_Ari_kick_B` and 1643 `Kg_AriPunch` — and
  `d+3+4,2` has no clip-map join to break the tie. Ambiguous ⇒ stays.
- **ROW-CONFLICT (1).** `d/b+1+2,2` step 0, candidate **131**. The T7 walk
  corroborates the move (joined motbin 1631 `Kg_t_slp00_EX`, open tier),
  but the move record for `d/b+1+2` carries authoritative `t3_row` **286**
  (`anim_ref: t3:king:row:286`). The branch-graph anchor (131) and the
  move record (286) conflict inside WH's own T3 data; T7 cannot settle a
  T3 row number. Stays REVIEW; the conflict is named here for the T3
  provenance lane — do not silently substitute either value.

### Side finding — a false clip-map join

The pantera clip-map joins `df+1` → motbin **1611 `Kg_syalp00`** (dmg 5).
Under group-correct walking, 1611 is reachable on `d/f+1` only through
other-gated sidestep/turn-state detours; the standing `d/f+1` is uniquely
**1652 `Kg_t_slpF`**. The 1611 join is an artifact of the flat-pool walk.
Flagged for the clip-mapping lane; this lane did not edit the clip-map
(Pantera step-plan scope only).

### Lead for the clip lane (not a promotion)

`1,2` step 2 is UNMAPPED (no candidate) and out of F9's scope, but the
walk now identifies its T7 occupant uniquely: **1548 `Kg_lprpF`**
(hub —1→ 1592 —2→ 1548, open). The clip-map lists `1,2` (king_3) as
unmapped; 1548 is the anchor when that join is picked up.

## 4. THE ORPHAN STRINGS (F8) — all four, by name

1. **chatur `d/b+1,2`** (T3 Ogre) — **stays UNMAPPED by name.** Anchors
   confirmed: move `d/b+1` = row 127 (direct record); the hits-model
   second hit `d/b+2` = row 128 (direct record). But in the Ogre bank
   graph, rows 127 and 128 carry only an `<end>` branch — **no branch
   connects 127 —RP→ 128**, and no `<common>` branch is recorded on
   either row. T3 string continuations route through the **common bank**,
   for which no JSON exists in WH or GRE (Lane B follow-up U4, still
   open). The chain is unprovable with the data in the repos. Chatur's
   list-valued `t3_row` records (the G-R3-adjacent class) were not
   touched.
2. **chatur `1,2,1+2`** (T3 Ogre) — **stays UNMAPPED by name.** Same wall:
   the `1,2,1` chain record ends at row 56; row 56 carries only `<end>`;
   the hits-model destination `1+2` = row 168 exists as a record but no
   branch connects 56 —LP+RP→ 168. Blocked on the same unextracted
   common bank (U4).
3. **pond `MIST 1,2`** (T7 Master Raven, frv) — **stays UNMAPPED by
   name, with a T7-proven negative.** MIST is Raven's Haze stance
   (pond.json: "Raven's Haze, renamed", entry `3+4`). Group-correct frv
   walk: `3+4` from the hub (1427 `Nj_sKAM00_`) reaches the stance root
   **1806 `Nj_commetSP`** at open tier. Its stance move set: `1` → 1809
   `Nj_steplp02` (dmg 20), `2` → 1801 `Nj_meteo01` (dmg 23), `3` → 1807
   `Nj_commetlk`, `4` → 1802 `Nj_commet01`, `1+2` → 1808 `Nj_commetlrp`.
   But 1809's only exits return to the hub — **MIST 1 has no `2` cancel;
   the string `MIST 1,2` is not a cancel chain in T7.** (Pond's own
   total_damage for the string, 18, also matches neither T7 hit.)
   The stance-root and per-button identities above are recorded here as
   the anchor set for the pond T7-clip lane; the string itself cannot be
   wired truthfully.
4. **ryusan `WR f,f,F (Mid Screen)`** (T7 Lucky Chloe, dnc) —
   **RESOLVED.** The notation is a duplicate spelling of the already-wired
   move `WR,f,f,F` (ryusan.json), whose frame-data command is literally
   "WR f, f, F (Mid Screen)". Its T7 anchor is now proven from the dnc
   motbin: **1778 `Co_runtac00`** — startup 16 and throw-class damage
   encoding match the frame-data record for luckychloe_182 (mid throw,
   startup 16), and 1778 is entered by an auto cancel from `sRUN__01F`
   (the mid-range run state). The sibling entry cross-checks: "WR f,f,F
   (Full Screen)" (luckychloe_84; dmg 30, startup 8) = **209
   `Co_runspA00`** (dmg 30, startup 8), auto-fired from `sRUN__02F/03F`.
   The strings entry already carries `t7_move_id: luckychloe_182`,
   identical to the move's — no file change was needed or made.

## 5. WHAT REMAINS OWED

- FK soft gate + play-verify for the 19 promoted steps (data-level only
  until then) — the standing gate from the step-plan law. Row 117's
  recorded FK failure (70%) is the named blocker for the 3 withheld
  `d/f+1,2` step-0 occurrences.
- The 63 remaining REVIEW occurrences: T7 cannot move them (57 no-chain,
  2 ambiguous, 1 row conflict, 3 FK-blocked). Routes: T3-side proof
  machinery, T8 data, an FK re-run for 117, or — for the 131-vs-286
  conflict — a T3 provenance ruling on evidence.
- Chatur's two orphans: blocked on extracting the T3 **common bank**
  (U4). That extraction, not more T7 work, is their unblock.
- The clip-map `df+1` → 1611 false join (§3) for the clip-mapping lane.
- Tools: the group-correct walker + this decipherment are recorded for
  GRE in the companion PR (alias table + group system + walker) so the
  next motbin character (frv/dnc banks included) starts deciphered.

## Appendix — all 82 adjudicated REVIEW occurrences

| plan key | step | candidate row | source | outcome |
|---|---|---|---|---|
| 1,2,1 | 2 | 198 | t3-branch-graph | PROVEN-T7 |
| 1,2,1~t7.king | 2 | 198 | t3-branch-graph | PROVEN-T7 |
| 1,2,1~t7.king.2 | 2 | 198 | t3-branch-graph | PROVEN-T7 |
| 1,2,1~t7.king.3 | 2 | 198 | t3-branch-graph | PROVEN-T7 |
| d+1+2,2,1,1 | 3 | 257 | t3-branch-graph | NO-T7-CHAIN |
| d+1+2,2,1,1,2 | 3 | 257 | t3-branch-graph | NO-T7-CHAIN |
| d+1+2,2,1,1,2 | 4 | 258 | t3-branch-graph | NO-T7-CHAIN |
| d+1+2,2,1,1,2,4 | 3 | 257 | prefix-move | NO-T7-CHAIN |
| d+1+2,2,1,1,2,4 | 4 | 258 | prefix-move | NO-T7-CHAIN |
| d+1+2,2,1,1,3 | 3 | 257 | prefix-move | NO-T7-CHAIN |
| d+1+2,2,1,1,3,3 | 3 | 257 | prefix-move | NO-T7-CHAIN |
| d+3+4,2 | 1 | 196 | prefix-move | NO-JOIN |
| d+3+4,2,1 | 1 | 196 | prefix-move | NO-JOIN |
| d/b+1+2,2 | 0 | 131 | t3-branch-graph | ROW-CONFLICT |
| d/f+1,2 | 0 | 117 | t3-branch-graph | PROVEN-STEP0 |
| d/f+1,2~t7.king | 0 | 117 | t3-branch-graph | PROVEN-STEP0 |
| d/f+4,2 | 0 | 135 | prefix-move | PROVEN-STEP0 |
| d/f+4,2 | 1 | 196 | recorded-dest | NO-T7-CHAIN |
| d/f+4,3 | 0 | 135 | prefix-move | PROVEN-STEP0 |
| d/f+4,3,4 | 0 | 135 | prefix-move | PROVEN-STEP0 |
| d/f+4,3,4~t7.king | 0 | 135 | prefix-move | PROVEN-STEP0 |
| d/f+4,3,4~t7.king.2 | 0 | 135 | prefix-move | PROVEN-STEP0 |
| d/f+4,3,d+4 | 0 | 135 | prefix-move | PROVEN-STEP0 |
| d/f+4,3,d+4~t7.king | 0 | 135 | prefix-move | PROVEN-STEP0 |
| d/f+4,3,d+4~t7.king.2 | 0 | 135 | prefix-move | PROVEN-STEP0 |
| d/f+4,3~t7.king | 0 | 135 | prefix-move | PROVEN-STEP0 |
| d/f+4,4 | 0 | 135 | prefix-move | PROVEN-STEP0 |
| df+1,2 | 0 | 117 | t3-branch-graph | PROVEN-STEP0 |
| f+2,1 | 1 | 198 | t3-branch-graph | PROVEN-T7 |
| f+2,1,1 | 1 | 198 | t3-branch-graph | PROVEN-T7 |
| f+2,1,1 | 2 | 257 | t3-branch-graph | NO-T7-CHAIN |
| f+2,1,1,2 | 1 | 198 | t3-branch-graph | PROVEN-T7 |
| f+2,1,1,2 | 2 | 257 | t3-branch-graph | NO-T7-CHAIN |
| f+2,1,1,2 | 3 | 258 | t3-branch-graph | NO-T7-CHAIN |
| f+2,1,1,2,4 | 2 | 257 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4 | 3 | 258 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4 | 4 | 259 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4 | 2 | 257 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4 | 3 | 258 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4 | 4 | 259 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4 | 5 | 260 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4 | 2 | 257 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4 | 3 | 258 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4 | 4 | 259 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4 | 5 | 260 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4 | 6 | 261 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4,1 | 2 | 257 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4,1 | 3 | 258 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4,1 | 4 | 259 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4,1 | 5 | 260 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4,1 | 6 | 261 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4,1,1 | 2 | 257 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4,1,1 | 3 | 258 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4,1,1 | 4 | 259 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4,1,1 | 5 | 260 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4,1,1 | 6 | 261 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4,1,3 | 2 | 257 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4,1,3 | 3 | 258 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4,1,3 | 4 | 259 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4,1,3 | 5 | 260 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,2,4,4,4,1,3 | 6 | 261 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,3 | 2 | 257 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,3,3 | 2 | 257 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,3,3,4 | 2 | 257 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,3,3,4 | 5 | 266 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,3,3,4,3 | 2 | 257 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,3,3,4,3 | 5 | 266 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,3,3,4,3 | 6 | 267 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,3,3,4,3,2 | 2 | 257 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,3,3,4,3,2 | 5 | 266 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,3,3,4,3,2 | 6 | 267 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,3,3,4,3,2,1+2 | 2 | 257 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,3,3,4,3,2,1+2 | 5 | 266 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,3,3,4,3,2,1+2 | 6 | 267 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,3,3,4,3,2,1+2,1 | 2 | 257 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,3,3,4,3,2,1+2,1 | 5 | 266 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,3,3,4,3,2,1+2,1 | 6 | 267 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,3,3,4,3,2,1+2~t3.king | 2 | 257 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,3,3,4,3,2,1+2~t3.king | 5 | 266 | prefix-move | NO-T7-CHAIN |
| f+2,1,1,3,3,4,3,2,1+2~t3.king | 6 | 267 | prefix-move | NO-T7-CHAIN |
| f+2,1~t7.king | 1 | 198 | t3-branch-graph | PROVEN-T7 |
| f+2,1~t7.king.2 | 1 | 198 | t3-branch-graph | PROVEN-T7 |
*Outcomes key: PROVEN-T7 (9) and PROVEN-STEP0 for row 135 (10) = promoted in
PR #1384. PROVEN-STEP0 for row 117 (3: the `d/f+1,2` / `df+1,2` step-0 rows) =
identity proven, promotion withheld — recorded FK failure (see §3).
NO-T7-CHAIN / NO-JOIN / ROW-CONFLICT = stays REVIEW, evidence in §3.*
