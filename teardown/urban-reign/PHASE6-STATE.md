# Urban Reign — Phase 6 State

Branch: `ur-phase6-bank-completion` — base: PR #518 branch `ur-phase5-names-polish` @ c76eaaa8 (stacked PR).
Lane: TEARDOWN COMPLETION SWEEP, Phase 6: motion-AFS bank completion — decode every bank, re-run every unproven record.

## Inherited truth (Phases 1–5, verified — not re-derived)

- 72 chars skinned+textured (`textured-models/` canonical, PR #464); char064 complete 1260/1260 (PR #518).
- Motion: `.gyu` cracked (`tools/ur_gyu.py`, incl. Phase-5 type-14 fix: BE s16 second differences, double-integrated per 8-key block); 56,844 tracks, 0 failures. 31/72 fighters natively animated; 41 proxy fighters have NO assignment table in any shipped file (CLOSED SEARCH, Phase 4) — PCSX2-capture-gated, not touched here.
- Name bridge gate (DOES NOT MOVE): maxDev ≤ 0.10 mm over all frames/components + unique under gate, uniform for all fighters.
- 886 P-list records held across 27 fighters → 484 proven own-bank (annotated `motdatName` in `game/assets/movesets/ur-charNNN.json`; evidence in `motion-names/`), 402 unproven, of which 306 proven in ANOTHER bank (cross-bank evidence only, never assigned).
- char005/070/071/072 hold NO P-list — nothing to bridge.
- 3 borderline pairs (char042 rec50 0.1361 mm, char055 rec34 0.1253, char057 rec32 0.1020; next candidates ≥1443 mm away) stay UNPROVEN under the gate unless NEW bank evidence changes the picture.
- Phase-5 Job-2 verdict: 5 P1 records (6, 10, 11, 12, 14) + an unknown share of the 402 unproven have NO identity in the 46 banks searched; source bank judged OUTSIDE the searched set. Full `motion/` AFS census (Phase 5) = 162 entries; shipped/decoded bank set is smaller; DVD001 entries are unnamed `file_NNNNN.bin` (not name-searchable).

## Jobs

- JOB 1 — BANK CENSUS + COMPLETION: enumerate the motion AFS's 162 entries against the banks decoded/searched in Phases 2–5 (pmot/tmot/general); identify every entry NOT yet decoded as a motion bank; decode each with `tools/ur_gyu.py` (type-14 fix included) into the bridge's bank structure; commit a decoded-bank inventory (entry → bank id, motion count, frame stats). Non-motion-bank entries get a one-line evidence classification (header/magic).
- JOB 2 — RE-RUN THE UNPROVEN SETS: run the Phase-5 bridge (same gate, unchanged) for (a) the 5 unsourced P1 records and (b) every fighter's unproven-own-bank records, against the NEWLY decoded banks. Own-bank proof only from the fighter's OWN bank (newly decoded own-bank entries count) → annotate `motdatName` + evidence; cross-bank proof → evidence only, never annotate; still unproven → stays, searched set now stated as the full AFS. Update per-fighter summary to Phase-6 totals + cross-check (total `motdatName` annotations == own-bank proven total).
- JOB 3 — CLOSEOUT DOCS: this file final; `WIRING-INVENTORY.md` name/motion rows updated; `BANK-COMPLETION.md` stating total banks in the AFS, total decoded, total motions searchable, and the definitive unproven remainder by reason class (no-bank-in-AFS vs borderline-over-gate vs no-P-list fighter). If the 5 P1 records close, say so plainly; if not, the AFS-complete searched set makes the negative definitive.

## Progress log

- Phase 6 start: branch `ur-phase6-bank-completion` created from `ur-phase5-names-polish` @ c76eaaa8 + this state file + PR opened BEFORE analysis (stacked on #518).
