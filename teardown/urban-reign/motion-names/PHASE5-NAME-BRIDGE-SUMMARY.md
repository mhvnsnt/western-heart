# Urban Reign Phase 5 — Name-Bridge Generalization Summary (Job 1)

Method: Phase-4 proven P1 method, applied per fighter. Each fighter's
`motion/test/motdatP<n>` record payloads (root stream = first frames×3 f32,
×1000) matched against that fighter's OWN pmot bank root tracks
(`tools/ur_gyu.py` decode; type-14 = Phase-5 cracked decode, see
`../PHASE5-JOB2-TYPE14.md`). **Gate applied uniformly to every fighter:
max deviation ≤ 0.10 mm over all frames/components AND unique under the
gate in the own bank.** (Phase-4's P1 proven pairs had max dev ≤0.0603 mm. Across all 27
fighters the largest proven maxDev is 0.0924 mm. Exactly three unproven
records sit within 0.102–0.136 mm of a frame-unique candidate with a
bounded, non-growing noise profile and the next candidate ≥1443 mm
away — char042 rec50, char055 rec34, char057 rec32; they are almost
certainly true pairs whose payload noise floor exceeds the gate on
long, large-excursion motions (174–270 frames, up to 9 m of root
travel), and they were left UNPROVEN under the never-force rule, with
the evidence recorded in their fighters' proven files. Every other
unproven record with an own-bank frame candidate is ≥12.7 mm away;
263 unproven records have no own-bank motion with their frame count
at all.) Unproven records were additionally cross-searched against
all other decoded banks (other fighters' pmot, tmot001–010,
general_normal / general_30frame / general_weapon); identities found
there are recorded per record as `crossBankHits` in each fighter's
proven file — they prove the record's source bank, they are NOT
assigned to this fighter's clips (per-character isolation).
`.info`/`.bin` name parity held for every record of every fighter.

| fighter | records held | proven (own bank) | unproven | of unproven: proven in another bank |
|---|---|---|---|---|
| char001 | 35 | 27 | 8 | 3 |
| char002 | 35 | 27 | 8 | 3 |
| char003 | 35 | 27 | 8 | 3 |
| char004 | 24 | 9 | 15 | 14 |
| char016 | 44 | 33 | 11 | 8 |
| char020 | 34 | 21 | 13 | 8 |
| char021 | 40 | 31 | 9 | 7 |
| char022 | 32 | 21 | 11 | 6 |
| char030 | 37 | 25 | 12 | 12 |
| char031 | 37 | 25 | 12 | 12 |
| char032 | 39 | 27 | 12 | 6 |
| char041 | 45 | 38 | 7 | 4 |
| char042 | 55 | 41 | 14 | 6 |
| char043 | 32 | 11 | 21 | 19 |
| char044 | 26 | 5 | 21 | 21 |
| char045 | 23 | 7 | 16 | 12 |
| char046 | 17 | 8 | 9 | 9 |
| char054 | 33 | 8 | 25 | 23 |
| char055 | 35 | 15 | 20 | 11 |
| char056 | 17 | 11 | 6 | 6 |
| char057 | 37 | 20 | 17 | 10 |
| char058 | 34 | 25 | 9 | 9 |
| char059 | 33 | 5 | 28 | 23 |
| char060 | 22 | 4 | 18 | 12 |
| char061 | 18 | 4 | 14 | 10 |
| char062 | 33 | 5 | 28 | 24 |
| char063 | 34 | 4 | 30 | 25 |
| **total (27 fighters with held pairs)** | **886** | **484** | **402** | **306** |

Per-record unproven reasons (frame-count candidate absent, or best
candidate's max deviation, or ambiguity) are in each fighter's
`name-bridge-<char>-proven.json` under `unprovenRecords`.

## Fighters with NO held pair (4 of 31 pmot fighters)

char005, char070, char071, char072 have pmot banks but NO motdat
P-list exists for them in the shipped AFS: the full `motion/` census
(162 entries: test / test30 / wptest × Gnrl + P + T lists) contains
no motdatP5, motdatP70, motdatP71 or motdatP72 in any context.
No bridge can be run for them; nothing was fabricated. Their
movesets are unchanged.

## Notes

- char001: the 27 proven pairs are identical to Phase 4's (same pairs,
  same deviations; record 16 maxDev 0.0603 vs Phase 4's rounded 0.06).
  Phase 5 adds cross-bank identities for records 7, 13, 29 (see Job 2).
- char002 / char003 proven sets are identical to char001's: their P2/P3
  lists and pmot002/pmot003 banks are record-for-record clones of P1's
  for the proven subset (verified by the match itself, not assumed).
- char030 / char031 likewise share identical proven sets (clone pair).
- Names assigned are MOTION names from motdat (e.g. `cbco_*`, `moco_*`),
  annotated as `motdatName` on clips `ur_mNNN`. They are not fighter
  identities; CANON-CONVERSION identities stay OWNER-pending.
