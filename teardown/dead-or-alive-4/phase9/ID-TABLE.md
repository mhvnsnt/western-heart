# DOA4 Phase 9 — ID table (extends phase8/ID-TABLE.md format)

Method: same as phase 8 (front bind-pose Cycles renders of phase-6 skinned GLBs, viewed by this agent) + phase-9 head-package renders (`phase9/renders/p9-head-*`). Confidence: certain | strong | tentative. A name is claimed only with evidence; `unidentified` is a valid final state.

## chrone — phase-9 viewed rows (phase-8 rows for pkg00–08+10 stand as-is)

| package | identification | evidence (viewed render) | confidence | competing candidates |
|---|---|---|---|---|
| chrone-pkg09 | group C katana ninja (see phase-8 pkg06 row) | VIEWED `renders/p9-chrone-pkg09.png`: katana grip rising over shoulder, diagonal back sword, bulky shattered armored torso, single leg column — visually confirms the stats-based group C assignment | tentative (group) | Ryu Hayabusa vs Hayate (as phase 8) |
| chrone-pkg11 | unidentified (dress pair with pkg12) | VIEWED `renders/p9-chrone-pkg11.png`: wide flared dress, shattered chest mass, round bowl/bell ornament at front waist, short sleeve stubs; 84 joints (hair/cloth bones) | — | — |
| chrone-pkg12 | unidentified (dress pair with pkg11) | VIEWED `renders/p9-chrone-pkg12.png`: same flared dress + front-waist bell ornament as pkg11, cleaner skirt; 86 joints | — | — |
| chrone-pkg13 | unidentified (long-dress group 13–16) | VIEWED `renders/p9-chrone-pkg13.png`: floor-length dress, high collar, coherent torso, segmented round object at front waist, long lower body (Ymin −0.64) | — | Helena-style formal gown noted, not claimed |
| chrone-pkg14 | unidentified (long-dress group 13–16) | VIEWED `renders/p9-chrone-pkg14.png`: floor-length dress, large front sash/bow, segmented round pouch at front waist, small chest ornament | — | — |
| chrone-pkg15 | unidentified (long-dress group 13–16) | stats identical to pkg14/16 (28,313 verts, 66 joints); render pending in this batch (pkg16 viewed as group representative) | — | — |
| chrone-pkg16 | unidentified (long-dress group 13–16) | VIEWED `renders/p9-chrone-pkg16.png`: visually identical to pkg14 (same dress, sash, front pouch) | — | — |

## chrtwo HEAD packages (phase-9 discovery — see HEAD-HUNT.md)

| package | identification | evidence (viewed render) | confidence | competing candidates |
|---|---|---|---|---|
| chrtwo-pkg04 | HEAD package, unidentified character | VIEWED `renders/p9-head-chrtwo-pkg04.png`: face (lips/chin), slotted cap/helmet hair, very long straight hair panels both sides; 8-joint own Hie skeleton, head-local, base at origin | strong (head package) | — |
| chrtwo-pkg20 | HEAD package, unidentified character | VIEWED `renders/p9-head-chrtwo-pkg20.png`: face, braided pigtails, large smooth cap + wide rounded collar under chin; 12-joint own Hie | strong (head package) | — |
| chrtwo-pkg24 | HEAD package, unidentified character | VIEWED `renders/p9-head-chrtwo-pkg24.png`: face (nose/lips), spiky star-like hair ornaments, long thin ponytail/braid strand dropping far below head (geometry Ymin −0.75) | strong (head package) | — |
| chrtwo-pkg29 | HEAD package, unidentified character; anchor family = chrone pkg00/01/02 (anchor 0.486, Δ=0.000) | VIEWED in composite `renders/p9-composite-chrone00-head29-neckbase.png`: smooth bob/helmet hair, visible face (nose/lips), straight side hair panels, ruffled collar; seated on chrone-pkg00 body at the neck-base anchor | strong (head package + family) | — |

## Phase-9 re-grading of phase-8 tentative rows (with head evidence)
- chrone pkg02 (kimono → Kokoro, tentative): pkg02 shares the EXACT head-joint height (0.486) with pkg00/pkg01 — same base skeleton = same fighter family as group A. The heads anchoring to this family (0.483–0.486 cluster: chrtwo pkg17, 18, 19, 20, 29, 30, 34, 35–40 copies) include braided-pigtail (pkg20) and bob-cut (pkg29) heads. The kimono + this head set keeps Kokoro plausible but the head↔costume pairing inside the family is not yet 1:1 proven — **stays tentative**, evidence strengthened (same-skeleton family confirmed).
- Group C (chrone pkg06–09, Hayabusa vs Hayate): group C bodies' head-joint family matches head anchors 0.519–0.525 (chrtwo pkg10, 11–16 copies, 31). Those heads not yet rendered in phase 9 — **stays tentative** until the 0.519-family heads are viewed.
- chrone pkg10 (Leifang vs Helena): pkg10's head-joint (0.478) family includes chrone pkg13 (long-dress group) + chrtwo pkg46/49 bodies and heads chrtwo pkg08, 09, 33 (anchor 0.478). Heads not yet viewed — **stays tentative**.

## Head-package census (chrtwo pkg04–45)
42 packages, 31 distinct GLBs (md5-verified): identical runs pkg11–16 (×6), pkg35–40 (×6), pkg44=45; near-twin pkg34 vs 35–40 group. Anchor families: 0.468 → chrone 17/18/20 family; 0.477 → chrtwo 50/51/52/55 family; 0.478 → chrone 10/13 + chrtwo 46/49 family; 0.483–0.486 → chrone 00/01/02 family; 0.519–0.525 → chrtwo 00 + chrone 07/08 family. No anchor under central-joint filter: pkg05, 06, 23, 24, 27, 28, 32 (unresolved sub-case, named in HEAD-HUNT.md).

## Coverage
- chrone: viewed 00–16 except 15 (17/30 viewed incl. phase 8); stats-only: none remaining below 17 — remaining to render: 15, 17–28 (29 = non-character, phase-8 strong).
- chrtwo: heads viewed 3/42 small packages; full packages 0/26 rendered this phase.
- chrthree: 0/50 rendered this phase.
