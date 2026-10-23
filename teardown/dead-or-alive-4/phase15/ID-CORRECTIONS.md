# DOA4 Phase 15 — ID Corrections

Every phases 8–12 render-based tentative identification that the
phase-15 filename-grade evidence (CONTAINMENT-AUDIT.md,
PACKAGE-NAME-MAP.md) can grade. **Filenames win.** Grades:
CONFIRMED (filename-grade evidence agrees), REFUTED (filename-grade
evidence contradicts — the correction stands plainly), RESOLVED
(a previously unnamed group gets its name), UNRESOLVED (no
filename-grade evidence either way — the tentative stands as a
tentative, explicitly NOT confirmed).

## REFUTED

1. **chrone-pkg29 = "non-character package (accessory/prop class)"
   — phase 8, graded "strong". REFUTED.** chrone-pkg29's bundle
   directory fingerprint equals retail **tin02.tpr** exactly (251
   records) and its assembly-graph key matches tin02's. pkg29 is
   Tina's costume 02, the last bundle of the mirror chrone stream.
   Its small phase-6 GLB (2,913 verts, 7 meshes) was a decode
   artifact of that package, not evidence about its nature. Any
   downstream use of pkg29 as a prop/accessory package is wrong.

## RESOLVED (unnamed groups get filename-grade names)

2. **chrone pkg23–26 "cord-loop family", fighter unidentified
   (phases 9–10). RESOLVED: Zack.** pkg23 = zac00, pkg24 = zac01,
   pkg25 = zac02, pkg26 = zac04 — all proven-byte+fingerprint.
   The "central weapon/cord" reading was Zack's costume geometry.
   Also resolved in the same run: pkg27 = tin00, pkg28 = tin01
   (Tina), pkg29 = tin02 (see #1).
3. **chrthree pkg22–28 "one armored costume across seven
   packages" (phases 11–12). CONFIRMED as a group + NAMED:**
   spa00–spa06, the Spartan costume set (proven-shared-order).
   The phase-12 grouping was right; it now has its filename.
4. **chrthree pkg39/41/42/43 "cat-ear group" + pkg40 (phase 12).
   CONFIRMED as a group + NAMED:** pkg39 = kor02, pkg40 = kor03,
   pkg41 = kor05, pkg42 = kor06, pkg43 = kor07 (all
   proven-byte+fingerprint). The cat-ear/bell-dress costumes are
   the kor set's costumes 02/03/05/06/07.
5. **chrtwo tail runs (previously structurally-described only).
   NAMED:** pkg46–49 = gen00–03, pkg50–55 = hel00–03/05/06,
   pkg56–59 = leo00–03, pkg60–63 = bas00–03, pkg64–67 =
   hak00/03/04/05. In particular chrtwo-pkg59 — the "3-ornament
   signature" package phase 11 cross-linked to chrone pkg17/19 —
   is **leo02**; the chrone side of that signature link remains in
   the unassigned region (see UNRESOLVED note below).
6. **chrthree pkg09–21, 29–38, 44–49. NAMED:** boy00/02/03/04,
   lis00–04, alp01 (pkg18; pkg19 is a second bundle with alp01's
   directory fingerprint), tng00/02, bra01–03, cri00/01/04/05/06,
   kor00/01/08/09, rtm00–03.

## UNRESOLVED (no filename-grade evidence — stated plainly)

7. **chrone-pkg02 → Kokoro (phases 8–9, tentative: kimono costume,
   braided-pigtail head family). UNRESOLVED.** pkg02 is in the
   re-authored region: no byte containment, no fingerprint match,
   no graph-key match against any retail `.tpr`. Its directory
   count (222) has no unique neighbor among the unmatched retail
   `.tpr`s (jan02 208, kas02 205, ryu02 223 — all within noise, and
   record counts are non-discriminative per CONTAINMENT-AUDIT.md).
   The Kokoro tentative is neither confirmed nor refuted; it
   remains a render-based tentative and must be cited as such.
8. **chrone-pkg06/07/08/09 (katana-ninja group C) → Ryu Hayabusa
   vs Hayate (phases 8–9, tentative). UNRESOLVED.** Same region,
   same absence of filename-grade evidence (bundle nrecs
   372/292/355/293; nearest retail nrecs non-unique). The
   phase-9 head-joint family link to the chrtwo pkg31 head is a
   structural observation, and chrtwo-pkg31 is itself unassigned.
9. **chrone-pkg10 → Leifang vs Helena (phase 8, tentative:
   Chinese dress, frog toggles). UNRESOLVED.** Bundle nrec 291;
   no exact evidence. (Context only: leo00–03 are proven in
   chrtwo-pkg56–59 — that is Leifang's other-costume volume; it
   says nothing about chrone-pkg10.)
10. **All other phases 8–12 group/family labels for packages in
    the unassigned regions** (chrone group A pkg00/01/05, group B
    pkg03/04, the chrone 13–16 long-dress group, chrtwo head
    packages and the hyt/lei/aya runs, chrthree pkg00–08):
    **UNRESOLVED** — no filename-grade evidence exists for them
    yet. They keep their group labels; no character name may be
    attached to them on the strength of this lane.

## What would resolve the remainder

The unassigned packages are re-authored, not permuted, so no
amount of byte searching will name them. The two evidenced paths:
(a) texture-payload identity — `.cat` data survived at 61–88 %
in the re-authored region (CONTAINMENT-AUDIT.md), so a `.cat`
TX2D payload census against the mirror packages' texture pools
could name packages through their texture sets; (b) structural
graph-key NEAREST-neighbor grading with an explicit distance
threshold, published as tentative-grade (never proven). Neither
was run in this lane; both are scoped here so the residual is
exact.
