# DOA4 Phase 15 — Package Name Map

First name-grade identities for the phase 6–12 package library.
Machine-readable form: `package-name-map.json` (per package: span,
assigned entry, evidence tier). Evidence and method:
CONTAINMENT-AUDIT.md §Identity bridges.

## Evidence tiers

- **proven-byte+fingerprint** — the retail entry occurs
  byte-identical and contiguous inside the package's span, AND the
  package bundle's XPR2 directory fingerprint equals the entry's.
- **proven-fingerprint** — bundle directory fingerprint exactly
  equals the retail `.tpr`'s (the entry itself is not contiguous).
- **proven-graphkey** — the assembly-graph key (directory record
  count, MdlGeo/MdlInfo/Hie sizes, object count), produced by the
  phase-3/6 parser on both sides, matches exactly and uniquely.
- **proven-shared-order** — several packages share ONE fingerprint/
  graph-key identity (e.g. colorway sets with identical directory
  structure); the entries and packages are assigned pairwise by
  relative order. Bundle order == TOC order is confirmed by every
  uniquely-matched run in all three volumes.
- **unassigned** — no exact evidence. NOT a guess: these packages'
  bundles differ from every retail counterpart (re-authored
  region). No name is claimed.

## Assigned (70 / 148)

### chrone (7 / 30)

| package | entry | tier |
|---|---|---|
| chrone-pkg23 | zac00.tpr | proven-byte+fingerprint |
| chrone-pkg24 | zac01.tpr | proven-byte+fingerprint |
| chrone-pkg25 | zac02.tpr | proven-byte+fingerprint |
| chrone-pkg26 | zac04.tpr | proven-byte+fingerprint |
| chrone-pkg27 | tin00.tpr | proven-byte+fingerprint |
| chrone-pkg28 | tin01.tpr | proven-byte+fingerprint |
| chrone-pkg29 | tin02.tpr | proven-fingerprint |

Unassigned: chrone-pkg00 – chrone-pkg22 (23).

### chrtwo (22 / 68)

| package | entry | tier |
|---|---|---|
| chrtwo-pkg46 | gen00.tpr | byte+fingerprint |
| chrtwo-pkg47 | gen01.tpr | byte+fingerprint |
| chrtwo-pkg48 | gen02.tpr | byte+fingerprint |
| chrtwo-pkg49 | gen03.tpr | byte+fingerprint |
| chrtwo-pkg50 | hel00.tpr | byte+fingerprint |
| chrtwo-pkg51 | hel01.tpr | byte+fingerprint |
| chrtwo-pkg52 | hel02.tpr | byte+fingerprint |
| chrtwo-pkg53 | hel03.tpr | byte+fingerprint |
| chrtwo-pkg54 | hel05.tpr | byte+fingerprint |
| chrtwo-pkg55 | hel06.tpr | byte+fingerprint |
| chrtwo-pkg56 | leo00.tpr | byte+fingerprint |
| chrtwo-pkg57 | leo01.tpr | byte+fingerprint |
| chrtwo-pkg58 | leo02.tpr | byte+fingerprint |
| chrtwo-pkg59 | leo03.tpr | byte+fingerprint |
| chrtwo-pkg60 | bas00.tpr | byte+fingerprint |
| chrtwo-pkg61 | bas01.tpr | byte+fingerprint |
| chrtwo-pkg62 | bas02.tpr | byte+fingerprint |
| chrtwo-pkg63 | bas03.tpr | byte+fingerprint |
| chrtwo-pkg64 | hak00.tpr | proven-shared-order (with pkg66) |
| chrtwo-pkg65 | hak03.tpr | byte+fingerprint |
| chrtwo-pkg66 | hak04.tpr | proven-shared-order (with pkg64) |
| chrtwo-pkg67 | hak05.tpr | proven-fingerprint |

Note: hak08.tpr's graph key equals hak03.tpr's identity class;
pkg65 is assigned hak03 by the byte+fingerprint tier, which
outranks the shared graph key. Unassigned: chrtwo-pkg00 –
chrtwo-pkg45 (46).

### chrthree (41 / 50)

| package | entry | tier |
|---|---|---|
| chrthree-pkg09 | boy00.tpr | byte+fingerprint |
| chrthree-pkg10 | boy02.tpr | byte+fingerprint |
| chrthree-pkg11 | boy03.tpr | byte+fingerprint |
| chrthree-pkg12 | boy04.tpr | byte+fingerprint |
| chrthree-pkg13 | lis00.tpr | byte+fingerprint |
| chrthree-pkg14 | lis01.tpr | byte+fingerprint |
| chrthree-pkg15 | lis02.tpr | proven-shared-order (with pkg17) |
| chrthree-pkg16 | lis03.tpr | byte+fingerprint |
| chrthree-pkg17 | lis04.tpr | proven-shared-order (with pkg15) |
| chrthree-pkg18 | alp01.tpr | byte+fingerprint |
| chrthree-pkg19 | alp01-class | proven-fingerprint (shared with pkg18; second alp bundle) |
| chrthree-pkg20 | tng00.tpr | byte+fingerprint |
| chrthree-pkg21 | tng02.tpr | byte+fingerprint |
| chrthree-pkg22–28 | spa00–spa06.tpr | proven-shared-order (7 colorways) |
| chrthree-pkg29 | bra01.tpr | byte+fingerprint |
| chrthree-pkg30 | bra02.tpr | byte+fingerprint |
| chrthree-pkg31 | bra03.tpr | byte+fingerprint |
| chrthree-pkg32 | cri00.tpr | byte+fingerprint |
| chrthree-pkg33 | cri01.tpr | byte+fingerprint |
| chrthree-pkg34 | cri04.tpr | byte+fingerprint |
| chrthree-pkg35 | cri05.tpr | byte+fingerprint |
| chrthree-pkg36 | cri06.tpr | byte+fingerprint |
| chrthree-pkg37 | kor00.tpr | byte+fingerprint |
| chrthree-pkg38 | kor01.tpr | byte+fingerprint |
| chrthree-pkg39 | kor02.tpr | byte+fingerprint |
| chrthree-pkg40 | kor03.tpr | byte+fingerprint |
| chrthree-pkg41 | kor05.tpr | byte+fingerprint |
| chrthree-pkg42 | kor06.tpr | byte+fingerprint |
| chrthree-pkg43 | kor07.tpr | byte+fingerprint |
| chrthree-pkg44 | kor08.tpr | byte+fingerprint |
| chrthree-pkg45 | kor09.tpr | byte+fingerprint |
| chrthree-pkg46 | rtm00.tpr | byte+fingerprint |
| chrthree-pkg47 | rtm01.tpr | byte+fingerprint |
| chrthree-pkg48 | rtm02.tpr | byte+fingerprint |
| chrthree-pkg49 | rtm03.tpr | proven-fingerprint |

Unassigned: chrthree-pkg00 – chrthree-pkg08 (9). These precede
boy00 in the stream; the retail chrthree entries with no package
(25 small `*A`-suffixed head-class `.tpr`s + bay/rtm04) outnumber
them, so no 1:1 order assignment is even arithmetically possible.

## Fighter-code reading (context, not evidence)

The retail 3-letter codes read: zac = Zack, tin = Tina, gen =
Gen Fu, hel = Helena, leo = Leifang (`leifan` in mot.afs),
bas = Bass, hak = Hayate (cf. hyt in the same volume), boy =
Bayman (`bay` in mot.afs), lis = Lisa, alp = Alpha-152 class,
tng = Tengu, spa = Spartan, bra = Brad Wong, cri = Christie,
kor — kor's reading is open; rtm's plain/c_ slots in mot.afs are
named kasumi.mot / c_kasumi.mot and are byte-identical copies of
kasumi's files (phase 15 Job 2), so the rtm slots hold Kasumi
motion data under chrthree's rtm naming. These readings are context for
the corrections log; the assignments above rest on bytes, not on
the readings.
