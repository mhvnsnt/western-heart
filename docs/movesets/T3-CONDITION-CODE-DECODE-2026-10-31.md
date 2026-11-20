# T3 Branch Condition-Code Decode — 2026-10-31

Lane: owner's "B — strings" unblocking research, resumed by direct owner order
2026-10-31 ("Resume the stalled lanes now"). Decode research ONLY: no moveset
JSON was changed and no REVIEW row was promoted by this lane.

Companion artifacts (same PR):

- `tools/anim/t3_condition_codes.json` — the machine-usable condition table
  (per-code census stats + semantics + walk rule + confidence).
- `tools/anim/t3_condition_walk.py` — condition-aware branch walk + the
  validation harness used for §5 (`walk` and `validate` modes).

Data: all 20 T3 bank graphs in `teardown/tekken3/movesets/moveset_<bank>.json`
at main `24058f8a2273cdfe553c3598856ab2eaadb941be`, and the 37 Phase-1 moveset
files under `game/assets/movesets/` carrying `provenance_fix` records.

## 1. Census (measured from the data, not from memory)

- 8,910 move rows across 20 banks; **27,480 real branches** (plus 8,910
  `<end>` sentinels — every row ends its branch list with exactly one).
- **60 distinct condition values** occur (0–75, sparse). Condition 0 covers
  18,985 branches and always has param 0.
- **4,160 hub splits**: branch groups sharing source row + command that differ
  only in condition (and target) — the raw material of the decode.
- The second gate field, `restriction`, is nonzero on ~4,180 branches
  (0 = 23,300). It is a separate axis from `condition` (§4).

## 2. Graph architecture the decode rests on

Established by direct inspection (bank/rows named per claim):

- Every bank has **two standing hubs** (stance_slot 3, state_word
  `0x00000842`, stream_frames 50, 44–47 branches; e.g. bryan/jin/paul rows
  22/23, king 21/22, anna 17/18). Their condition-0 targets agree 345/345
  across each pair; the pair is two parallel copies of the standing state
  table (physical identity of the pair — the leading hypothesis is a facing
  pair — is **not** proven).
- Almost nothing in-bank branches *into* the hubs: they are engine-entered
  states, not string targets.
- Each hub's basics fan out to a **stride-3 variant family** (jin LP →
  rows 32/35/38/41 at windows [1-8]/[1-15]/[1-23]/[1-31]) plus one
  long-window local row and, for some buttons, a `common:N` target — the
  shared common-bank row space, for which no bank JSON exists in the repos
  (open unknown U4).
- Rows 12–16 of each bank form the **crouch state machine** (stance_slot
  40/54/57, state_words `0x00003129`/`0x00002021`/`0x00002829`, 70-frame
  dmg-0 rows) interlinked by directional `any-button` branches; FC/WS move
  rows hang off its sub-states (e.g. kuma row 174 ← row 18 `LP`, and row 18 ←
  row 12 `3+any-button`).
- A small set of **dispatcher rows** (stance_slot 3525, ~93 branches; anna
  245, jin 317, nina 328, paul 277; bosconovitch row 470) are engine dispatch
  tables, not player states (§3, codes 72–75).

## 3. Per-code findings

Confidence grades: **proven** (structural, no free parameters), **strongly
supported** (multiple converging structural tests), **unknown** (census and
site profile recorded; semantics not claimed).

### Proven
- **0 — unconditional** (18,985 branches, param always 0). The baseline every
  Phase-1 proof already relied on.

### Strongly supported
- **36 — variant selector** (1,677). From one source row and command, the
  cond-36 branch picks the parallel variant row of the same move: target-row
  deltas vs the cond-0 sibling cluster at +3/+6/+9/+12/−3/−2/+2/−6/−9/+1
  (table offsets), and cond-36 targets' follow-up command sets match cond-0
  targets far above chance (mean Jaccard 0.359 vs 0.023 random-row baseline;
  twin test 223 identical / 706 different / 314 unresolved). Windows skew
  early ([1-8] on 803) but [1-255] also occurs (503). *Which physical state
  36 names is not identified* — for notation→row mapping both targets are
  the same move, so the walk passes it as a variant edge.
- **37/38, 62/63, 64/65 — paired binary selectors.** Within each pair the
  source profile is identical (37/38: 495/497 branches; 62/63: exactly
  428/428; 64/65: exactly 209/209) and the pair picks paired targets. For
  62/63 the targets **swap** between up-inputs and down-inputs (anna rows
  181/345), i.e. the pair tests a direction-relative state (facing), not
  the input. Which code is which physical value is not identified.
- **18/19** (xiaoyu only, param constant 640) and **40/41** (bosconovitch
  only) — same paired-selector pattern on a single bank each.
- **48 — crouch-state family gate** (639). Sources are *only* the crouch
  cluster (stance_slot 40/54/57; the three state_words above) and its
  branches come in window pairs splitting at the family rows' durations
  ([1-59]+[60-60] ×300, [1-37]+[38-38], [1-75]+[76-76]): the continuation
  edges of the crouch machine (visible directly in kuma rows 12–16).
- **57–61 — the `0x3884` state-family gates.** Sources are the stance_slot
  153/157/158/166/167/168 rows with state_words
  `0x00003884`/`0x00004284`/`0x00004c02`. The family gate is established;
  what distinguishes the five codes individually is not.
- **39 — throw gate** (834; 817/834 directional-first inputs). Constant on
  throw branches while `restriction` varies over opponent-state values
  selecting the variant/target kind (same restriction → same local target;
  other values → common-table targets). For string walks the throw is
  terminal; the gate does not block the notation→row mapping.
- **25 / 24 / 55 — distance-parameter gates.** Params are round thresholds
  (25: 1800 on 160/196; also 600/1000/1201/2000/2200/3000/3072/3800),
  commands are motion-sequence heavy (129/196 for 25) and sources include
  the `0x00400842` running-state rows: the branch is range-gated (dash/
  running move activation family). Exact unit and comparison direction are
  not decoded.
- **Codes 2–23 with param 1536 (`0x600`) — engine dispatch family.**
  `any-button` transitions off standing/state rows, including 4-way dispatch
  sites (bryan rows 209/210 carry codes 2/3/4/5 to four different targets at
  identical param; family params are `0x580`/`0x600`/`0x700`). Not
  player-input string gates; individual code semantics unknown.
- **72/73/74/75 — dispatcher-row param families.** Concentrated on the
  stance_slot-3525 dispatcher rows on `any-button` branches. Params: 72/73
  ∈ {6,10,14,17} (×50 each for 72); 74 = large slot-range integers
  (247…3898, never equal to the branch's own target_slot); 75 ∈ 0…51 at the
  dispatcher row — a dispatch index over a ~52-entry table. Family
  established; per-code semantics unknown.
- **26 / 27 — state-continuation markers.** 26: `any-button` transitions to
  the same or next state row (anna 162→163; bosconovitch 119→120, 124→125).
  27: `any-button` self-loops on stance rows. Not input steps.
- **28 — alternate-path variant selector** (31): in splits its target
  coincides with the sibling branch's target in 10 of 13 resolvable cases.

### Unknown (census + site profile recorded in the JSON table; no semantics claimed)
- **34, 35, 49** — `any-button` state-exit/continuation branches (34: 21
  branches in 19 banks, one attested target is the bank's idle row, anna
  163→325). Family resemblance to 26/27 only.
- **42** — lei 15 / xiaoyu 7 / bosconovitch 2 / forestlaw 2, `any-button`
  from stance_slot-3 rows.
- **46** — only on the `[4 5 6+LP+RP]` motion branch in king and law.
- **51** — sources cluster on stance_slot-21 rows (19/34).
- **53** — rare per-bank gates on individual basics (13 banks, 1–3 each).
- **67** — 3 branches (anna, bosconovitch).
- **29, 43, 44, 45, 52, 68** — 1–2 branches each.

### Confidence summary
60 codes total: **1 proven** (0), **30 strongly supported** (36; the pairs
18/19, 37/38, 40/41, 62/63, 64/65; 48; 57–61; 39; 24/25/55; 28; 26/27 as
state-continuation markers; the 2–23 param-1536 family and 72–75 as dispatch
families — family-level, with individual semantics of 2–23 and 72–75
explicitly unknown), **29 unknown** at the individual level (incl. 34, 35,
42, 46, 49, 51, 53, 67 and the singletons). By branch volume, the decoded
families cover 26,000+ of 27,480 branches (94%+); the unknown codes are
individually rare.

## 4. The `restriction` axis

Restriction is a **second, independent gate** on the same branch record.
Evidence (throw-input table across all 20 banks): under fixed condition 39,
the restriction value selects the throw variant/target kind — restriction
sets {3,6,7,13,2,11,4,18…} reach the same local target, others reach
common-table (EMPTY-in-this-bank) targets; under condition 0, throws with
restriction 0 stay local (256) while restrictions 4/3/10/17 go common.
Reading: **restriction is an opponent-state axis** for gates (throw
variants first). Per-value semantics are NOT decoded. Nonzero restrictions
also sit on 655 hub condition-0 branches and 1,824 non-hub condition-0
branches, so Phase-1 walks evidently did not evaluate them; the walk tool
records but does not evaluate restrictions.

## 5. Validation (measured with the shipped tool)

Method: replay all **2,097** `provenance_fix` records (the Phase-1 corrected
set) through the walk in three condition modes — `decoded` (this table),
`all_blocked` (every nonzero condition blocked), `all_pass` (every condition
passable) — holding the walk model fixed, so the deltas isolate the
condition table's contribution. Two walk models were measured:

**Model 1 — standing hubs only, input edges only.**
decoded: 192/2097 reached (81 unique-hit, 111 hit, 660 miss, 1,245 no-walk).
all_blocked: 188. all_pass: 192.

**Model 2 — + zero-input closure** (`<common>` links, `<end>` successors,
no-input transitions) around each step.
decoded: 317/2097 (1 unique, 316 hit, 669 miss, 1,111 no-walk); mean
terminal set 3.1 rows. all_blocked: 313. all_pass: 317.

**Model 3 — + state-transition closure + per-file anchors** (directional
`any-button` and direction-only branches as state edges; start set = the
file's own pre-existing `anim_t3` rows + standing hubs, mirroring the
provenance lane's anchor method).
decoded: **973/2097 reached** (1 unique-hit, 972 hit, 607 miss, 517
no-walk); mean terminal set 44.1 rows. all_blocked: 920/2097.
all_pass: 975/2097. By proof grade (1,809 of the 2,097 records carry an
A/B/C/S grade token): A 62/75 reached, B 72/246, C 738/1,483, S 0/5.

**Transition-level support** (final-step test, model-independent): the share
of proven records whose expected row has an inbound branch spelling the
record's final input step with a condition the mode allows:
decoded **1,335/2097 (63.7%)**; all_blocked 1,327; all_pass 1,335.

Honest reading of these numbers:

1. **Soundness: the decoded rules exclude zero proven transitions.** At the
   transition level the decoded table supports exactly as many proven
   records as the allow-everything baseline (1,335 = 1,335) — no proven
   record's final step needs a condition this table blocks — while the
   naive all-blocked baseline loses 8. On full walks, decoded beats
   all-blocked by +53 records (973 vs 920) and trails all-pass by only 2
   (both grade-S records whose paths run through dispatch-family edges).
   The table discriminates (it blocks the dispatch families and the
   unknowns) without contradicting any proven evidence.
2. **The decode does not retroactively change any Phase-1 verdict, and this
   lane claims no promotions from it.** Most existing proofs run through
   condition-0 spines; the conditions were never their blocker.
3. Full-string reproduction is limited by the *walk model*, not the
   conditions: no-walk is 517 even in all-pass mode, and the anchor-expanded
   terminal sets are large (mean 44.1 rows) — the walk is a candidate
   generator, not a prover. 762 records lack transition support in *every*
   mode: their expected row has no inbound branch spelling the final step
   in these bank graphs at all, which points at the missing common-bank
   graph (U4) and notation/anchor limits — the next lane's walk-model work,
   now unblocked on the condition side.
4. Where the table *is* the deciding factor is the previously unwalkable
   territory the provenance doc named: stance-state and directional-first
   strings. The crouch family (48) and the `0x3884` family (57–61) are now
   traversable under explicit source-profile rules instead of blanket
   blocks, and the throw gate (39) + variant pairs no longer force
   guess-grade on the transitions they govern.

## 6. What remains unknown (for the next lane)

- **U1. Physical identity of the paired selectors and of 36.** The pairs
  (37/38, 62/63, 64/65, 18/19, 40/41) and code 36 select variant rows; which
  physical state each value names (facing L/R is the leading hypothesis for
  62/63 from the up/down swap) is unproven. This does not block row mapping
  (variants are the same move) but blocks any *state-exact* replay.
- **U2. Individual semantics inside the dispatch families** (2–23 at param
  `0x600`; 72–75). Family + sites + params are documented; the per-code
  referents (esp. 74's slot-range params and 75's 0…51 index) need the
  dispatcher rows' target table, which lives outside the bank JSONs.
- **U3. The rare codes** (34, 35, 42, 46, 49, 51, 53, 67, 29, 43, 44, 45, 52,
  68): census + sites recorded; each needs targeted ground truth (a known
  move whose path is forced through the code).
- **U4. The common bank.** `common:N` branch targets (e.g. jin hub RP →
  common:60/61) resolve to a shared bank that has no JSON in either repo.
  Extracting it (same extractor family as the 20 banks) is the single
  biggest walk-model gap: several standing basics route through it.
- **U5. Restriction per-value semantics** (opponent-state axis; throw table
  is the entry point).
- **U6. Distance-gate units** for 24/25/55 (threshold param's unit and
  comparison direction).
- **U7. Window semantics within families** — e.g. cond-36's [1-8] skew and
  the crouch family's [1-59]/[60-60] split are structural facts recorded
  here; their timing meaning (buffer windows vs state phases) is open.

## 7. How the provenance lane resumes from this

- Use `tools/anim/t3_condition_walk.py walk --bank <bank> --input "<string>"`
  for candidate paths; treat `variant` edges as same-move, `state-family`
  edges as gated on the source profiles in the JSON table, and
  `blocked_dispatch`/`blocked_unknown` edges as still-unproven.
- F9's Pantera step-plan REVIEW candidates and F8's orphan strings were the
  named consumers of this decode: their graph-side blocker is now the walk
  model (anchors + common bank, U4), not the condition codes for the
  families decoded here. Promotions still require the play-verify lane's FK
  gate — unchanged by this lane.
- Nothing in this doc changes any moveset data; the 8,593 guess-grade
  mappings stay exactly as they are until a promotion lane proves them.
