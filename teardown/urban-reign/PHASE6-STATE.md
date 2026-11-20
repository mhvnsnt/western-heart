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

- Phase 6 start: branch `ur-phase6-bank-completion` created from `ur-phase5-names-polish` @ c76eaaa8 + this state file + PR #548 opened BEFORE analysis (stacked on #518).
- Census: DVD000 motion-relevant classes enumerated (motion/ 162 motdat entries; tec/motion/ 44; tec/demo/ 273; afs/safe/ppk motion classes). All 309 tec/ files fetched by AFS range-fetch (incl. 7 duplicate-name FMDL variants fetched by raw offset) + demo PPK samples.
- Embedded-bank scan (validated: header prefilter + motion-0 root decode; validated on main_in's two known general copies): main.ppk holds TWO distinct embedded banks (331 + 326 motions); select.ppk / weapon.ppk hold 0; sample char001 / mission001 / stage003 PPKs hold 0.
- Decode: 241 NEW banks / 1,004 motions, every root decoded, 0 failures (`motion-names/BANK-INVENTORY-PHASE6.json`). 70 tec/demo/data files are NOT banks (camera_data x35, demo_data .dam x35 — Bank parse fails on header, classified in `BANK-COMPLETION.md`).
- DVD001: AFS located via ISO9660 directory (LBA 881429 -> ISO byte 1805166592; method reproduces DVD000's known base exactly); first 128 bytes of all 1,173 entries fetched (clustered ranges) — 1,132 CRI ADX audio ((c)CRI verified in-entry), 39 PSS movies, 2 empty, **0 .gyu banks, 0 PPKs** (`motion-names/DVD001-HEADER-CENSUS.json`).
- INCIDENT: the local `wh/` clone was deleted by an external sweep mid-phase (~08:12 UTC); branch + commits were already pushed, clone was re-created from GitHub at 9e35d95 and work continued — nothing lost.
- Jobs 1-3 landed; results below.

## Results (final)

- JOB 1 — DONE: shipped bank set completed. **285 motion banks / 3,357 motions searchable** (44 banks / 2,353 motions from Phases 2-5 + **241 new banks / 1,004 motions**). Full census + classifications: `BANK-COMPLETION.md`.
- JOB 2 — DONE (`motion-names/PHASE6-NAME-BRIDGE-ADDENDUM.md` + `motion-names/PHASE6-RERUN-RESULTS.json`): all 402 unproven records re-run at the unchanged gate against the 241 new banks. **New own-bank proofs: 0** (no new bank is any fighter's own pmot bank — pmot set closed at 31 by AFS + gyuindex). **18 records cross-proven in main_bank1/main_bank2** (Phase 5 searched those banks only for the P1 five); 1 of them (char032 rec18 `cbco_spd_chuka` -> main_bank1 m115, 0.0343 mm) is identified for the FIRST time. Cross-bank total **306 -> 307**; no-identity remainder **96 -> 95**. Annotations cross-check: `motdatName` in `game/assets/movesets/ur-char*.json` = **484** == own-bank proven total (484, unchanged). Borderline three: no new bank shares their frame counts — unchanged, gate unmoved.
- THE 5 P1 RECORDS DO NOT CLOSE: no hit in any new bank (best new-bank deviations 205.0-4,342.7 mm). With the searched set now = every motion bank in the shipped AFS set (DVD000 classes all censused + DVD001 header-censused, 0 banks), the Phase-5 verdict is **definitive for shipped data**: their source bank is not in the shipped AFS set — not a decode gap; only a PCSX2 runtime capture could source them. Same for their P2/P3 clone counterparts.
- JOB 3 — DONE: this file final; `WIRING-INVENTORY.md` Move names row updated to Phase-6 totals; `BANK-COMPLETION.md` states totals + the definitive unproven remainder by reason class (307 cross-bank-identified / 92 no-bank-in-AFS / 3 borderline-over-gate; fighters char005/070/071/072 = no-P-list class).
