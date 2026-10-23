# DOA4 Phase 13 — Job 3: the 8 unpaired heads vs two new evidence classes

Heads in question (chrtwo packages, distinct): **05, 06, 23, 24,
26, 27, 28, 32**. Proven context: 23/31 distinct heads are paired
by Hie node identity + skin-bind Δ = 0.000 (phases 10–11); the 8
were tested against ALL 148 bodies by skin-bind Δ with no proof
(phase 12). This phase tested the two remaining quantitative
evidence classes. **Proof bar (unchanged): a pairing ships only
when the combined evidence is unique + quantitative.**

Tools: `phase13/tools/texrecord_census_p13.py` (directory + payload
census over mirror range-fetches), `phase13/tools/
texrecord_analyze_p13.py` (family matrices). Data:
`phase13/texrecord_census_l1.json` (all 148 packages), scratch
`p13/texrecord_census.json` (payload hashes), `p13/l1_analysis.txt`.

## §0 Calibration — the method proves itself on knowns first

- **Identical-copy controls (must share 100%):** chrtwo
  pkg11–16 share 17/17 L1 keys and 28/28 descriptor hashes;
  pkg35–40 share 14/14 and 20/20; pkg44 = pkg45 share 10/10 and
  23/23. At payload level (L2) the identical runs likewise share
  100% of TX2D payload hashes. The census machinery is exact.
- **Premise test (the signal must fire on PROVEN pairs):** for
  each of the 23 proven heads, count TX2D identities shared with
  its own family's bodies vs the best other family. A pairing
  signal exists only if own-family sharing is systematically
  higher. Results per level below.

## §1 Class (a) — shared texture-record identity

TX2D identity at three strengths: **L1** layout key
(fmt/endian/tiled/pitch/w/h — pool base excluded, it is
package-local layout); **DESC** the full 40-byte descriptor hash;
**L2** sha256 of the raw payload bytes (the task's stated signal:
byte-identical TX2D records).

- **L1: premise FAILS.** Proven heads share layout keys with
  own-family bodies at the same rate as with unrelated bodies —
  e.g. head17 (fam486): own-max 9, other-max 14; head10 (fam581):
  own 8, other 12; head31 (famC): own 15, other 11. Texture
  SHAPES are generic across the roster; layout identity carries
  no character information. (Unpaired heads at L1: famC reads
  highest for 05/06/23/24/26/27/28 — inside the same shallow
  gradient proven heads show toward wrong families; not proof.)
- **DESC: premise FAILS.** Proven heads share 0–3 full
  descriptors with their own families (head21: 3; head22: 2;
  head07: 1; the other twenty: 0) — the same band as cross-family
  noise. The one apparent exception, head31 at 21/21, was a
  self-match artifact (chrtwo-pkg31 is head31's OWN package;
  phase 11's famC body list mis-included it) — corrected in the
  analyzer and recorded here so it is never re-cited.
- **L2 (payload bytes): the premise FIRES on proven pairs —
  selectively — and fires on NONE of the 8.** Artifact
  `phase13/texrecord_census.json` (42 head packages + 41
  proven-family bodies, every TX2D payload sha256'd; resume tool
  `phase13/tools/texrecord_census_l2resume_p13.py`). Controls:
  identical heads share 28/28, 20/20, 23/23 payloads — the tier
  is calibrated. Proven pairs: head41–44 (fam477) share **13 of
  23** payloads with fam477 bodies, other-max 0; head31 (famC)
  shares **15 of 21**, other-max 2; head21 (fam468) shares 7,
  other-max 1; head10/11 (fam581) share 4, other-max 2; the
  remaining proven heads sit at own-max 0–3 ≈ other-max (fam486
  0–2, fam478 2–3) — payload sharing exists where a family's
  heads and bodies share costume texture data, and is absent
  where they do not. **The 8 unpaired heads (per-family L2
  maxima):** 05: 477=1, all others 0 · 06: 477=1, others 0 ·
  23: 478=1, 468=1, C=1 · 24: 478=1, 468=1, 477=1, C=1 · 26:
  477=1, others 0 · 27: 478=1, 468=1, 477=1, C=1 · 28: 477=2,
  others 0 · 32: 478=2, C=2, 468=1. Every unpaired head sits at
  0–2 shared payloads with EVERY family — inside the proven-nil
  band (0–4) and far below the proven-signal band (7–15,
  unique). No unpaired head has a unique dominant family at L2.

**Class (a) verdict:** at L1 and DESC the class carries no
pairing signal at all (premises fail on proven pairs). At L2
the signal is real but family-dependent: it certifies the
fam477 / famC / head21-style sharing where it exists — and for
the 8 unpaired heads it returns 0–2 against every family.
Because the tier demonstrably detects sharing where sharing
exists, these are meaningful negatives, not method blindness.
**Class (a) yields no pairing for any of the 8 heads**, with
the full three-tier matrices as the proof.

## §2 Class (b) — slot-grid adjacency

Head packages occupy chrtwo 04–45 in a family-interleaved order
(proven families by index): 04·468, 07·468, 08·478, 09·478,
10–16·581 (identical ×6 run at 11–16), 17–20·486, 21·468, 22·477,
25·477, 29·486, 30·486, 31·C, 33·478, 34·486, 35–40·486
(identical ×6), 41–44·477 (44=45 ×2). The 8 unpaired sit at:

| head | left neighbour (proven) | right neighbour (proven) | slot reading |
|---|---|---|---|
| 05 | 04 · fam468 | 07 · fam468 | both sides fam468 |
| 06 | 04 · fam468 | 07 · fam468 | both sides fam468 |
| 23 | 22 · fam477 | 25 · fam477 | both sides fam477 |
| 24 | 22 · fam477 | 25 · fam477 | both sides fam477 |
| 26 | 25 · fam477 | 29 · fam486 | split |
| 27 | 25 · fam477 | 29 · fam486 | split |
| 28 | 25 · fam477 | 29 · fam486 | split |
| 32 | 31 · famC | 33 · fam478 | split |

Cross-checks that break the slot theory as a proof mechanism:
(1) run-length vs family size does not hold — the ×6 identical
run at 11–16 belongs to fam581, which has only 3 known bodies
(chrone14–16), while fam486's ×6 run (35–40) matches its 6
bodies; a costume-slot grid would not produce both. (2) Families
interleave (468 appears at 04, 07, 21; 486 at 17–20, 29–30,
34–40) — slots are grouped by neither fighter nor family
consistently. (3) For heads 26/28 the slot reading (fam477/486)
CONTRADICTS their measured skin-bind heights (0.277 / 0.310 —
no body family exists at either height): at most one of the two
signals can be right, and the bind measurement is the physical
one. Slot adjacency therefore nominates at most a FAMILY (7–12
candidate bodies), never a unique body — it cannot meet the
proof bar alone, and class (a) cannot break its ties (§1).

## §3 Verdict

**No new pairings. Composites stay 23/31 — final.** The 8 heads
(05, 06, 23, 24, 26, 27, 28, 32) remain unpaired, now with FOUR
exhausted evidence classes on record: Hie anchor copies
(phase 10: identity/absent for exactly these), skin-bind Δ
(phases 11–12: no Δ = 0.000 vs any of 148 bodies; six are
origin-bound and carry no signal by construction), TX2D record
identity at L1/DESC/L2 (phase 13: L1/DESC carry no signal; L2
fires strongly on some proven pairs — 13–15 shared payloads,
unique family — and returns 0–2 against every family for all
8), and slot-grid adjacency (phase 13: nominates families at
best, contradicted for 26/28). No composite was built and no
render ships for an unproven pairing — the discipline that made
the 23 proven composites trustworthy is the same one that
refuses these 8.
