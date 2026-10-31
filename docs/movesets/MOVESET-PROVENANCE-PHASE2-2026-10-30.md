# Moveset Provenance — Phase 1 Completion + Phase 2 Findings (2026-10-30)

Companion to `docs/movesets/MOVESET-PROVENANCE-2026-10-30.md` (the classification, PR #1264).
Owner's order (2026-10-30): classify donor moves (owner-approved vs placeholders), then work the
single-source straight ports first ("only have 1 moveset straight from 1 character base"), and
"once those are all done do the rest." Owner addendum: gaps fill only from a fighter's own base
source (Steam-library Tekken 7/8 extraction is the named source for T7/T8 bases/forms); a data
fix is **data-corrected**, never video-verified — only fight video verifies a move.

## Phase 1 — COMPLETE (36 files, 2,097 anim_t3 mappings data-corrected)

Method: for each class 1-W file, guess-grade `anim_t3` mappings (`nearest … (approximate)` /
`same-notation` labels) were corrected only where the fighter's own T3 bank branch graph
(`teardown/tekken3/movesets/moveset_<bank>.json`) proves the real row, via four proof types —
A: verified same-bank twin with the identical input; B: branch walk from a verified anchor
through graph branches, gated by the bank's `hit_frames.json`; C: the graph holds exactly one
row for the input and the file's claimed row equals it; S: the file's own strings table row-set
validated against the graph. Unproven mappings were left exactly as-is. Every correction is
recorded in the file's `provenance_fixes` entry (the numbers below are read from those entries
on current main / the merged PR diffs — not from worker reports).

| File | Corrected | Remaining guess-grade | PR |
|---|---|---|---|
| t3-nina.json | 114 | 311 | #1272 |
| doc-frank-hood.json | 100 | 232 | #1284 |
| doc-frank-machine-shop.json | 100 | 232 | #1284 |
| doc-frank-wowomomo.json | 100 | 232 | #1284 |
| t3-hwoarang.json | 94 | 402 | #1266 |
| tobi.json | 94 | 402 | #1273 |
| t3-anna.json | 88 | 312 | #1274 |
| gyou.json | 87 | 409 | #1270 |
| buffalo-bill.json | 85 | 305 | #1308 |
| t3-law.json | 84 | 306 | #1267 |
| t3-eddy.json | 84 | 280 | #1268 |
| awapop.json | 82 | 204 | #1299 |
| aotsuki.json | 81 | 170 | #1278 |
| gashadokuro.json | 81 | 170 | #1279 |
| t3-kuma.json | 81 | 170 | #1277 |
| doc-frank-frankenstein.json | 80 | 186 | #1284 |
| kai.json | 79 | 285 | #1269 |
| torch.json | 63 | 207 | #1287 |
| t3-paul.json | 51 | 227 | #1289 |
| tou.json | 51 | 227 | #1290 |
| kingtyrant.json | 50 | 200 | #1305 |
| t3-lei.json | 39 | 425 | #1271 |
| demonio-bloodline-ember.json | 35 | 232 | #1280 |
| retsu.json | 35 | 353 | #1304 |
| rin.json | 33 | 213 | #1301 |
| t3-julia.json | 32 | 147 | #1292 |
| nightwolf.json | 30 | 149 | #1293 |
| phantom.json | 27 | 268 | #1286 |
| samura1.json | 26 | 192 | #1294 |
| diablo.json | 23 | 115 | #1297 |
| skull.json | 19 | 225 | #1285 |
| sakura.json | 18 | 167 | #1288 |
| sha.json | 18 | 167 | #1291 |
| demonio.json | 17 | 136 | #1295 |
| demonio-human.json | 13 | 140 | #1276 |
| pantera.json | 3 | 195 | #1283 |
| **Total** | **2,097** | **8,593** | |

Notes on specific files:

- **pantera.json (3):** of its 198 guess-grade mappings, only 3 sit on plain T3 King keys the
  graph proves (all proof-C, rows already correct, labels upgraded — applied as a surgical text
  edit because the file does not round-trip reserialization). 69 T3-floor guesses are unproven
  (see the blocker below). 126 sit on T7/T8-form keys (`~t7`/`~t8` suffixes, `t7.king_NNN`
  motbin keys) and were deliberately **not** corrected against the T3 graph — their real source
  is the Steam Tekken 7/8 extraction named in the owner's addendum.
- **rin.json (33):** two proof-B corrections for `b+2,1` → Jin row 217 were **reverted inside
  PR #1301**: row 217 is graph-proven but not baked into `game/assets/anim/t3/jin/rows.pack.json`,
  and the attack-anim baked-rows test must stay green. Landing them needs a rows.pack bake
  (`tools/anim/t3_row_bake.py --merge --bank jin`) — a shared-bank step outside one file's
  isolation, left as a named follow-up.
- **buffalo-bill.json (85):** two passes over the Law lineage (Marshall Law graph 81, Forest
  Law graph 4), one file, one PR.
- **samura1.json (26):** Gun Jack portion only; its other-bank entries were not touched.
- **docfrank.json:** no Phase 1 pass — the file carries **zero** guess-grade `anim_t3` (all 104
  are `true-map …` labels from the 2026-10-23 anim-fix lane). Correction to the classification
  doc: the real Doc Frank files are `docfrank.json`, `doc-frank-frankenstein.json`,
  `doc-frank-hood.json`, `doc-frank-machine-shop.json`, `doc-frank-wowomomo.json` (the
  classification table's `doc-frank-hoodless` / `doc-frank-towel` names do not exist), and its
  per-file guess counts were audit-definition counts; the operative counts are the
  `provenance_fixes` records above.
- **Tests:** every PR passed the repo CI (including game-unit-tests) and the four local suites
  (`batch1-step-plans`, `attack-anim`, `combat-systems`, `root-motion`). The baked-rows gate
  above was applied to every surgical file before commit.
- **Verification discipline:** two worker reports in this lane contained merges that never
  happened (phantom PR numbers/SHAs). They were caught by re-checking the remote; no bad data
  landed. Every number in this doc was read from the merged files or PR diffs directly.

## Phase 2 — findings (no replacement PRs warranted)

The classification named three residue layers for Phase 2. Inspected on current main, all three
are **T8-form layers**, not placeholder donor data: their `anim_t3` entries carry
`true-map … (anim-fix 2026-10-23)` labels and their `anim_ref`s point at T8 sources — the same
structure as Pantera's T7/T8 forms, whose source is the Steam T7/T8 extraction.

- **koreshi.json — Yoshimitsu layer (312) + Heihachi (48):** `anim_ref: t8:yoshimitsu:…`. The
  fighter's core is already Vega (`vega` 372 + `sf-vega` 160 mappings in place). Canon records
  the Yoshimitsu base as rejected, and the classification's owner Decision List item 10 asks the
  owner to confirm this layer's treatment. **Untouched — it is the owner's call, not a clear
  placeholder case.**
- **demonio.json — Devil Jin layer (34):** `anim_ref: t8:devil_jin:…`, the T8 Devil Jin form
  layer of a Jin-base fighter. Not donor-flagged placeholder data. **Untouched** (Steam T8
  source governs it).
- **gyou.json — Paul layer (47):** `anim_ref: t8:paul:…`, the T8 Paul form layer; Gyou's own
  bank (Hwoarang) was corrected in Phase 1 (#1270). **Untouched** (same reasoning).
- **street-reign.json:** the one whole-file class-3 stub is on the owner Decision List
  (existence/base unrecorded). **Untouched.**
- **Class-2 (owner-approved mix) files** were not reworked, per the order: zui, zen, ryuji-rock
  (CornerStone), kronos, kronos-attire2, rave, cainelias. The 13 SUSPECT No Mercy rows stay
  flagged for the separate true-window re-extraction program; none were silently fixed.

## What remains

1. **8,593 guess-grade mappings are unproven** across the 36 Phase 1 files. The dominant
   blocker, by the tool's own failure counts: T3 branch **condition codes** (stance-state and
   directional transitions — WS/FC/BT/stance inputs) are not yet decoded, so most strings have
   no walkable anchor. Decoding them is the research step that unlocks the bulk of the rest.
2. **T7/T8-form mappings** (pantera 126, the Phase 2 layers above, and similar form keys across
   the roster) wait on the Steam Tekken 7/8 extraction lane; when it lands, it supersedes
   branch-graph inference for those fighters/forms.
3. **rin `b+2,1` row 217** waits on a Jin rows.pack bake (above).
4. **Play-verification is still owed for everything in this doc.** These are data corrections
   against the real T3 source data; per the owner's video-evidence standard, none of it reads
   as verified until the play-verify lane shows it working in a fight. Pantera's Batch 1
   step-plan candidates from PR #1232 remain REVIEW-grade on their own track (FK soft gate +
   play-verify), unchanged by this lane.
5. **The owner Decision List stands** — 10 items in
   `docs/movesets/MOVESET-PROVENANCE-2026-10-30.md` (star, byou, jin_soul, demonio-winged,
   gyou-spirit-body, charger ×2, street-reign, cainelias, Echo, koreshi layer). Those 7 files
   were not touched by this lane.
