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
