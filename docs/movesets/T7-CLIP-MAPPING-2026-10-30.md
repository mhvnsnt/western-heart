# T7 Clip Mapping — the 781 UNMAPPED anim_refs, resolved from real Tekken 7 code (2026-10-30)

Owner order (2026-10-30): pull from the real code in the games in his Steam
library to fill the gaps. Source of record: the owner's own Steam TEKKEN 7
(app 389730), previously pulled via DepotDownloader into the PRIVATE
game-reverse-engineering repo (`teardown/tekken7-steam/`). No fighter
moveset file was edited by this lane; the per-fighter JSONs in
`game/assets/anim/t7/clip-maps/` are the supply layer for the provenance
lane to wire, per-character, at its own pace.

## What was blocking

The 781 moves (`anim_ref: UNMAPPED:t7-clip-pending`, audit 2026-10-29) needed
two things: (1) which real T7 move each WH move is, and (2) that move's actual
animation clip bytes. The clip bytes lived in `tkdata/mothead/mask/*.rotsm.arc`
— MOTA banks no lane had ever decoded (the "0x8000-bank clip bytes").

## What landed

**MOTA format cracked + validated** (full spec in GRE
`teardown/tekken7-steam/tkdata/mothead/mask/MOTA-FORMAT.md`): a `.rotsm.arc`
is a little-endian outer header wrapping big-endian MOTA sections (offset
table at +0x14 after a 0x14-byte header). Signature validation: 11,690/11,690
table entries across 10 arcs land on clip-start words 100/200. Bank map:
anim_id ≥ 0x8000 → `common.arc` (bare MOTA, 1,711 entries, key = id − 0x8000);
0x4000 ≤ id < 0x8000 → the character's own arc, section 0 (key = id − 0x4000);
id < 0x4000 → a bank whose file is NOT in the pulled tkdata tree (bounded,
see remainder). Clip format: header word 100/200 + track count; the 200-family
body is fully decoded (dense float32 BE, frames × tracks × vec3, size equation
exact on every clip); the 100-family body is sliced and indexed but its
quantised encoding is not yet decoded.

**The join** (WH move → real T7 motbin move): MVL display-name+notation exact
matches, the motbin cancel graph (incl. group cancels decoded from raw bytes),
and damage/startup fingerprint corroboration. The t7_id ordinal → MVLT row
shortcut was TESTED AND REJECTED with counterexamples (king_87 "Atlas Hammer"
is MVLT row 37, motbin move 2556 `Kg_WHummer`). Every mapping carries its
evidence and a confidence; no closest-match substitutes anywhere.

## Counts (of the 781)

| Outcome | Count |
|---|---|
| Mapped to a real T7 move AND clip byte-range resolved | **450** |
| Mapped to a real T7 move, clip in the un-located bank-0x0000 file | 31 |
| Honestly unmapped, with per-move reasons + candidate pools | 300 |

Per fighter (clip-resolved / bank-0 / unmapped): pantera 68/4/37,
phantom 67/1/59, skull 63/6/45, burger 80/3/28, kinpo 49/7/47,
demonio 48/0/32, diablo 39/8/33, scimitar 36/2/19. Confidence over the 481
mapped: 208 high, 273 medium. Scimitar's base Shaheen is T7 code `arb`
(`arbmot.json`, "[SHAHEEN]") — he is not T7-missing.

Clip blobs are on GRE release `t7-rotsm-clips-v1` (59.2 MB, sha256 manifest
included); per-entry locators (section, offset, size, format word, sha256)
are in GRE `.../mothead/mask/indexes/` and repeated inside each clip-map JSON.

## Remainder (explicit, not deferred silently)

- 300 unmapped: 81 strong T8-only candidates (moves T7 simply does not have —
  the T8 pass's exact workload), 91 in ambiguous candidate pools (a
  TheBigTuna startup/damage fingerprint pass would resolve many), 39
  MVL-confirmed but requirement-gated in the graph (chain throws etc. — needs
  the motbin requirements-table decode), the rest no-evidence.
- 31 bank-0x0000 moves: move identity proven; their clip file was not in the
  pulled `tkdata/mothead/` tree (names are facial/`vlc_` cutscene-flavoured).
  Needs a wider game-data pull or a runtime trace to locate.
- Format-100 clip bodies: sliced + indexed, encoding not yet decoded
  (format-200 bodies are fully decoded). Most clips are format 100, so this
  is the gate on converting clips into WH-playable animation data; the
  mapping layer above is complete regardless.
- T8 pass not started: no T8 moveset data exists in any of our stores
  (models/UI only). It needs the same DepotDownloader route on the owner's
  Steam TEKKEN 8 — the T7 lane's Steam credentials were session-supplied and
  never committed — or community TKMovesets2 outputs.

## V2 re-run over the held "other" pool (2026-10-30, Worker C)

The B2b/c lane resolved 4 moves incidentally from the 89-entry "other" pool
(entries whose v1 reason read "motbin graph candidate exists but no MVL
corroboration and/or non-unique — held as unmapped per no-guess rule"). This
lane ran the v2 channels **systematically** over all 89.

**Method.** Each entry's full input sequence was walked over the v2 cancel
graph: v1 plain/group edges + input-sequence commands (0x800D+k, expanded
from `raw.input_sequences`/`raw.inputs`), dash/tap/flag command edges,
unconditional empty-input auto-cancels as pass-through intermediates, and
bound/throw/pose-class terminals (damage/startup carried in hit conditions,
not the move record). Direction-set chords (a cancel whose direction bits
name a set of directions, GRE REQUIREMENTS-DECODE §2.2) were also checked —
they could only veto a promotion, never create one. Promotion required the
walk to terminate at **exactly one** motbin move **and** that move's anim to
resolve to a concrete clip locator in the GRE bank indexes
(`teardown/tekken7-steam/tkdata/mothead/mask/indexes/`). No fingerprint
evidence was used as a basis for any promotion. The ambiguous pool (90),
the requirement-held pool (10), the T8-only pool (81) and the flagged
pantera f,f,n,1+2 "Lay Off" adjudication were not touched.

**Graph source.** mhvnsnt/game-reverse-engineering main at
967d5d85e47d6c392d56b6b80fd57c246f08691e (includes PR #76, merge 6c1a8c85e6a84be3d92844197d38cc14a499dc8b): `teardown/tekken7-steam/tkdata/mothead/t7_req_graph.py`
(v2 steps + requirement runs) and `teardown/tekken7-steam/tkdata/mothead/REQUIREMENTS-DECODE-2026-10-30.md`;
motbin JSONs under `teardown/tekken7-steam/tkdata/mothead/json/` — sha256-verified
byte-identical to the clip lane's worker-B sources for all 8 fighters. The v1
graph code (worker-B `join_engine.py`/`run_join.py` in
`~/workspace/agent-ops/t7-clip-lane/`) was reused unmodified; the combined v2
walk was rebuilt for this lane because the B2 lane saved only its results,
not its walk code.

**Sanity check (graph re-derivation).** Sample of 48 already-mapped entries
(6 per fighter, spread across each clip-map): the v2 walk's terminal pool
contains the mapped motbin move for **48/48**. Over all 514 mapped entries
the same membership check gives **511/514**; the 3 misses are the B2 lane's
hand-adjudicated special readings (diablo f,F+3 dash-state reading, kinpo
1+4,2,d+4 direction-set finisher, phantom f,F+1+4,F hit-variant parent),
not systematic walk failures. The clip-locator builder used for promotions
reproduces the clip blocks of all 481 clip-resolved mapped entries exactly.

**Results.** 11 promoted, 78 held with a `v2_rerun_20261030` record and an
updated reason per entry (terminal ids + what the re-run found):

| Fighter | Other pool | Promoted | Held |
|---|---|---|---|
| burger | 13 | 4 (f,F+4, f,n,d,df+1+2*, f,n,d,df+3, f,n,d,df+3,2) | 9 |
| demonio | 9 | 1 (f,F+3,1) | 8 |
| diablo | 12 | 1 (f,n,d,df+2) | 11 |
| kinpo | 19 | 4 (f,F+1+2, f,F+2, f,F+2,3*, NWG.f,F+1+2) | 15 |
| phantom | 10 | 1 (f,F+3+4,1+2) | 9 |
| pantera | 12 | 0 | 12 |
| skull | 8 | 0 | 8 |
| scimitar | 6 | 0 | 6 |
| **Total** | **89** | **11** | **78** |

The v2 channels also *blocked* promotions the v1 graph had left as single
candidates: pantera f,F+2 gains the bound-class sibling Kg_p00_2; phantom
f,f,F+3 gains Ym_runlk00; diablo's f,n,d,df+3 pair gains He_sjk02; demonio
f,n,d,d/f+1+2 gains Jz_shoryu_EX2; and the direction-set check adds a running
kick terminal against skull f,F+3 (Co_runlk00), burger f,F+3 (Ft_runlk00)
and a second string terminal against demonio f+3,1 (Jz_lk00_lp) — all held,
with the competitor named in each entry's record as a lead for a future
adjudication. The kinpo f+3 Spinning Heel Drop family stays held: its
Jn_66LK terminal is bank-0x0000 (no located clip file) and the v2 walk adds
further terminals.

**New net totals (recounted from the clip-map files): 525 mapped /
256 unmapped of 781.** Per fighter mapped/unmapped after this lane:
burger 89/22, demonio 51/29, diablo 54/26, kinpo 64/39, pantera 77/32,
phantom 76/51, scimitar 40/17, skull 74/40. No mapping here is claimed
play-verified; clip-maps remain the supply layer for the wiring lane, and
this lane did not run the PR #1282 republish.

---

## FILL 2 ADDENDUM — 2026-11-06 (group-correct re-walk + bank-0x0000 solved)

Owner fill order: "1, 2, 3, then 4, remember then all til we get em done" — Fill 2 (Tekken 7 held-data gaps).

### F2 — bank-0x0000 SOLVED

Bank 0x0000 is **MotaList slot 0: the MOTA section embedded in each character's own `bin/<code>mot.bin`** (the rule is stated in the header docs of GRE's own `t7_motbin_to_json.py`). Verified 10/10 characters: exactly one embedded section per motbin whose entry count equals the bank-0 anim_id count, 404/404 signature checks. All **33** clip-map bank-0 entries are now clip-resolved (locators in the clip-maps; indexes in GRE `mask/indexes/<code>_bank0_index.json`; clip bytes in GRE release `t7-bank0-clips-v1`, pull-back verified). The 2026-10-30 hunt's §3c claim ("no MOTA data in bin/") was wrong and is superseded by §10 of the hunt doc.

### F1 — group-correct re-walk of the 256 unmapped

Walker: GRE `t7_string_walk.py` (0x800B group-cancel partition + alias-table hub rules, 2026-10-31 — postdates the v1/v2 flat-pool runs). Validation on the 525 mapped entries: unique verdicts 280 correct / 28 differ / 217 no-unique — so uniqueness alone did not promote. Promotion required unique terminal + concrete clip locator + corroboration (two-notation agreement and/or a v1 MVL row and/or fingerprint damage+startup double-true-unique), with a fingerprint veto. **Promoted: 22. Held: 234** (walk-multi-terminal 114, walk-no-terminal 68, unique-but-held 24, walk-dies 24, t8-sourced-entry 4) — per-entry verdicts are recorded in each clip-map (`fill2_20261106` addenda; prior reasons preserved). New totals: **547/781 clip-resolved, 234 unmapped**.

**Correction applied:** pantera `df+1` was remapped 1611 `Kg_syalp00` → **1652 `Kg_t_slpF`** — the ALIAS-AND-GROUP-DECODE doc itself names the old mapping a flat-pool false join; the group-walk reproduces the correction.

**Contested (reported, NOT edited):** 26 mapped entries the group-walk uniquely contradicts. These need a provenance-lane adjudication, one by one:

| fighter | input | mapped (kept) | group-walk unique |
|---|---|---|---|
| pantera | Behind.b,f+1+2 | Kg_Akelbow2 | Kg_rpspxk |
| pantera | df+1,2 | Kg_syalp01 | Kg_t_slpF03B |
| pantera | df+2 | Co_syarp00 | Kg_t_srpF |
| phantom | 1+2_t8 | Co_s_tlp00 | Ym_vs_yos2 |
| phantom | df+2 | Co_syarp00 | Ym_t_XsrpF |
| phantom | df+3 | Co_syalkF | Ym_maegeri |
| phantom | qcb,f+2 | Thrmv_Ym_neg | Ym_rp00F |
| phantom | qcf+1 | Ym_spinjp_0 | Ym_lp00F |
| phantom | u+1+2 | Ym_Xhoba | Ym_hoba |
| skull | b,df+4 | Bx_MAPPALOW | Bx_t_srkF |
| skull | df+3 | Co_syalkF | Bx_back_LK |
| skull | df+4 | Co_syarkF | Bx_t_srkF |
| skull | f+1+2 | ___________ | Bx_roll_LP1 |
| skull | f,n,b+2 | Bx_MAPPA00 | Bx_back_RP |
| burger | b+3+4 | Ft_lrk00D_B | Ft_Broll00 |
| burger | df+2 | Ft_syarp00 | Ft_t_srpF |
| burger | f+3+4 | Ft_JWheel | Ft_Froll00 |
| burger | ws3,3+4 | Ft_s_tlk01 | Ft_lk00 |
| demonio | b,f+2 | JIN_up06 | Jz_rp00F |
| demonio | b,f+2,3 | Jz_karatekick | Jz_10comb2 |
| demonio | df+4 | Jz_syarkF | Jz_3rk |
| diablo | df+4 | He_syarkF | He_t_srkF |
| diablo | qcf+2 | He_hadoh03 | He_rp00F |
| scimitar | df+2 | Co_syarp00 | Co_t_srpF |
| scimitar | df+4 | Co_syarkF | Ab_t_srk00 |
| scimitar | f,b+2 | Ab_64rp | Ab_rp00B |

### F5 — no-anim moves wired from held data

Census of current main: 433 moves carry no animation binding of any kind (the audit's 453 was its own count). New clip-maps: **pond** (Master Raven/frv — 40 of 151 bare moves wired) and **thor** (Ganryu/gan — 14 of 78). The 9 bare moves across the 8 clip-mapped fighters all walked to no terminal (0 wired, recorded). Not wireable from T7 data: baek-master-white (153 — Baek is not in Tekken 7), menajerii (32 — Roger Jr. is TTT2), megami (5 — Jun is TTT2), street-reign (5 — not Tekken).

### F11 — format-100 SOLVED (record correction)

Format-100 (0x64) bodies were solved 2026-11-01 on WH main (axis-angle rotation encoding decoded from the shipping EXE's sampler; `tools/anim/t7_anim64.py`, `tools/anim/t7_anim64_to_c8.py`). Fill 2 independently re-verified 2026-11-06: decoder `validate()` over kinmot.bin = 118 clips / 17,239 frames / 0 errors; Unicorn round-trip 0x64 → 0xC8 → the game's own sampler reproduced the game's 0x64 quaternions with worst error **3.58e-07** over 8 King clips. Remaining work is application (baking), not format RE.

