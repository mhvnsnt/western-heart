# Urban Reign Phase 5 — Job 3 executions (the steps named in PHASE4-JOB3-POLISH.md)

## (a) char064 missing group — RECOVERED (1260/1260)

**Decoder reject-log step, run.** The Phase-1 decoder
(`tools/ur_decode.py`, landed on this branch from the PR #429 tree
for reproducibility) was re-run on `char064.ppk` with its own stats.
Its log reproduces the shipped state exactly: **1260 verts parsed,
1197 placed**. The reject is identified to the packet:

- Group 0, **packet 3** (63 verts, file offset 0x62b0 in the .vmd) is
  the only parsed piece with no assignment. It is a batched strip of
  **two rigid sub-objects**: verts 0–41 single-influence on slots
  {19, 20}, verts 42–62 single-influence on slots {23, 24}. All its
  sibling packets are pure ({19,20} or {23,24} only).
- Exact reject reason, from the decoder's own logic
  (`assign_by_trusted_fit` final placement pass): the piece's four
  slots are four singleton islands (no blended verts → no internal
  relations), and placement requires ONE palette candidate that
  anchors every island to the merged skeleton. Sub-object A's window
  (P27, offset 4, reversed — the candidate its {19,20} siblings took)
  does not anchor slots 23/24; sub-object B's window (P27, offset 0,
  reversed — its {23,24} siblings' candidate) does not anchor
  19/20. No single candidate anchors all four islands, so the piece
  falls through `continue` and is dropped. (Phase 4's "s16 group"
  guess was wrong: the packet parses cleanly under the float
  grammar — the loss is at assignment, not parse.)

**Recovery.** The slot transition at vert 42 coincides exactly with
a **uvflag segment break** (vert 42 carries uvflag=1, which starts a
new face segment in the decoder's own strip grammar — no triangle
spans the boundary). `tools/ur_char064_recover.py` splits that one
run at the break (42 + 21 verts) and runs the standard pipeline
unchanged. Result: **1260/1260 placed**, and the two halves
independently chose exactly their sibling sub-objects' candidates
({19,20} half → P27 offset 4 reversed, as packet 0; {23,24} half →
P27 offset 0 reversed, as packets 4–7) — the split is validated by
the decoder's own candidate machinery, not by hand.

**Rebuild + asserts.** The recovered phase-1 GLB was rebuilt into
the canonical textured GLB with the Phase-3 pipeline
(`tools/ur_build_textured.py`, same as every other character) and
`textured-models/char064_textured.glb` + the MANIFEST entry updated:

| count | shipped | recovered | delta |
|---|---|---|---|
| verts (prim-0 POSITION) | 1197 | **1260** | +63 |
| indices (total) | 1674 | **1737** | +63 |
| joints | 14 | 14 | 0 |
| embedded images | 13 | 13 | 0 |

The build's own geometry identity also holds (output prim-0
POSITION 1260 = input 1260; total indices 1737 = input 1737).
Recovered-verts spatial sanity (verified): the full model's
bounding box is identical to the shipped model's (min
(−1.11, −0.136, −0.106), max (0.336, 0.163, 0.439)); every one of
the 1197 shipped vertex positions is present in the recovered GLB;
the recovered verts' novel positions (10 unique positions among the
63, the rest duplicating existing positions at strip seams) lie
inside the existing extent (x −0.809…−0.487, y −0.047…0.043,
z −0.025…0.05) — a compact piece of the model, not an outlier cloud.

Note: char042 and char068 are the same small-fighter class
(1260 parsed) and shipped complete — their group-0 packet 3 was
placed whole as an anchored piece, which is why only char064 lost
it (its packet-3 slot mix differs).

## (b) Accessory pieces — PPK 0xae00 decode test executed

**The test.** Decode the PPK header-graph zone (the zone the
`0xae00` header tag points into, ppk offset 0x17d in char001) into
an explicit parent/bone list and diff it against the GLB node
order. The zone was fully enumerated for char001, char064, char056
and char042 (representative + worst-residual characters). Contents,
in every case: the palette records (`01 <tag> 03 <n> <bone ids>` —
the P27/P16/P6 families and per-character permutations the decoder
already parses and uses as candidate families) and node-order/group
lists (`01 <tag> 07 <n>` in char001: one record,
`[12,17,18,19,20] / [51,13,14,15,16] / [52,53,54,55] / [56] / [57]`
separated by 0xff — sub-object node groups, not child lists; the
same list appears inside char056 as a type-03 record payload).
**No record type in the zone encodes a parent, a child list per
node, or any per-accessory bone assignment beyond the palette
windows the decoder already searches.** There is nothing in the
0xae00 zone left to decode that the decoder does not already use.

**Per-piece outcomes.** The unproven set (Phase-4's "11 characters"
were never named in its doc; the Phase-1 inventory —
`URBAN-REIGN-CHAR-INVENTORY.md` on the PR #429 branch — is the only
census, and it supports the 11 below: 9 characters with
placed-but-unproven pieces at trusted residual ≥0.02, plus char001
whose anchored accessory piece is the one Phase 2 measured swinging,
plus char064 whose dropped piece is (a) above). For every piece:
the 0xae00 test produced **no new placement/bone evidence**, so no
placement was changed and none is claimed proven; the exact
residual stands as the piece's record. No guessed placements shipped.

| character | piece | trusted residual | 0xae00 outcome |
|---|---|---|---|
| char007 | g5:1-2 | 0.27449 | no graph data; residual stands |
| char010 | g9:0-1 | 0.08458 | no graph data; residual stands |
| char010 | g10:7-8 | 0.24264 | no graph data; residual stands |
| char010 | g10:9-10 | 0.20584 | no graph data; residual stands |
| char019 | g10:0-1 | 0.24149 | no graph data; residual stands |
| char027 | g6:0-2 | 0.02 (at threshold) | no graph data; residual stands |
| char027 | g7:0-2 | 0.02 (at threshold) | no graph data; residual stands |
| char029 | g11:1-2 | 0.5522 | no graph data; residual stands |
| char029 | g11:5-6 | 0.26843 | no graph data; residual stands |
| char056 | g1:12-13 | 0.37607 | zone enumerated for char056; no graph data; residual stands |
| char056 | g13:5-6 | 0.45567 | no graph data; residual stands |
| char056 | g13:7-8 | 0.70773 | no graph data; residual stands |
| char056 | g13:10-11 | 0.39372 | no graph data; residual stands |
| char056 | g13:13-14 | 1.11226 | no graph data; residual stands |
| char057 | g1:7-8 | 0.14146 | no graph data; residual stands |
| char057 | g16:0-1 | 0.03176 | no graph data; residual stands |
| char062 | g13:6-7 | 0.4355 | no graph data; residual stands |
| char062 | g13:13-14 | 0.67321 | no graph data; residual stands |
| char067 | g14:2-3 | 0.34086 | no graph data; residual stands |
| char067 | g14:5-6 | 0.44837 | no graph data; residual stands |
| char067 | g14:12-13 | 0.36999 | no graph data; residual stands |
| char001 | g3:0-1, g4:0-1, g8:1-2 (anchored, single-bone) | −1.0 (anchored, unvalidated) | zone enumerated for char001; the type-07 node-group list names nodes 51–57 in accessory-range groups but assigns no parents; swing piece's bone assignment NOT independently proven; status unchanged |
| char064 | g0 packet 3 + g4:0-1 (anchored) | −1.0 (anchored) | recovered in (a) by run split; placement now stands on the same anchored basis as its sibling packets |

(Residuals are the Phase-1 inventory's published values from the
decoder's raw stats; −1.0 is the decoder's "anchored, not
independently validated" marker, per the inventory's own legend.)

## (c) Does the 0xae00 test close the node-graph accessory suspicion?

**No — explicitly not.** The test was executed in full and its
result is negative: the header-graph zone contains palette and
node-group lists only; the true node graph (parent array) is not
present there, just as Phase 4 found it absent from every other
shipped file searched. What remains, exactly:

- The H-index mapping (motion bone b → GLB node b) stays **proven
  for bodies** (Phase-2 embedded-clip check, max dev 1.8e-07) and
  **suspect for the rigid accessory pieces** listed in (b), whose
  placements rest on single-bone anchors + best-candidate fits.
- The only remaining discriminating evidence source is runtime:
  a PCSX2 capture of a known motion's pose (the same capture class
  as Phase-4 Job 1's spec) would let the accessory bones' true
  parents be read off the game's own evaluated skeleton. No shipped
  file can settle it; nothing further was guessed or shipped.
