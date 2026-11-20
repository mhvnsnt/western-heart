# Hand/Arm Rigging + Posing Reference — All Tekken Games + Teardown Games

**Date:** 2026-10-23
**Purpose:** Deeper rigging accuracy + deeper posing for ARMS AND HANDS (the wonky area),
pulled from every Tekken game and the teardown games whose hand/arm work fits
Western Heart's Tekken-style playstyle.
**Raw extracts:** teardown/<game>/rigging-reference/ (per-game files; JSON where parsed).

## 0. Source priority (standing directive 2026-10-23)

Pull order for hand/arm rigging + posing references:

1. **Tekken 5, Tekken 6, TTT2, Tekken 7 FIRST** — hand bones, finger weights,
   arm posing in stances/idles/win poses. A dedicated extraction coordinator
   is driving these games to 100%; use their output.
2. **Tekken 3 is FALLBACK-ONLY** — use teardown/tekken3/ only to fill gaps the
   newer games cannot cover. Do NOT default to T3 references.
3. Other teardown games (DOA, VF5, SC2, Urban Reign, wrestling) where their
   hand/arm work fits WH's Tekken-style playstyle.

Coordinator-output check 2026-10-23 ~15:00 CDT: no NEW T5/T6/TTT2/T7 hand-bone
extraction has landed since the last pull (tekken5-ps2-v1 still 0 assets;
ttt2-7z-v1 unchanged; teardown/tekken6/ still EBOOT-decrypt + customization
parts; teardown/tekken7/ unchanged since PR #813). The T5/T6/TTT2 sections below
still use the same-family T6-era proxy, flagged as such. NEW since the last
pull: Urban Reign's bone-name pool is decoded (49 names, no finger bones —
see below).

## 1. The comparison

| Game | Hand bones? | Fingers | Naming | Fist/open/grip | Status |
|---|---|---|---|---|---|
| Tekken 3 | NO — 18 rigid parts | None (mitten parts) | Part/slot indices | Baked into part geometry; wrist rotation only | FALLBACK-ONLY (standing directive 2026-10-23) — EXTRACTED via USA-verified parsers |
| Tekken 5 | Unknown (no native skeleton extracted) | Unknown | T6-era convention presumed | Unknown | OPEN — GLB releases are geometry-only |
| Tekken 6 PSP | Unknown (no native skeleton extracted) | Unknown | T6-era convention presumed | Unknown | OPEN — use T6-era proxy below |
| TTT2 | Unknown (extracted files encrypted) | Unknown | T6-era convention presumed | Unknown | OPEN — LIVE containers need decrypt |
| Tekken 7 | YES — SKT_CH_base_Skeleton | 5 digits, 2-3 segs | LeftHand/RightHand + digit+number (UE4 style) | Authored animation poses | EXTRACTED (53-joint WH derivative + T6-era 147-bone port) |
| Tekken 8 | — | — | — | — | QUEUED — pull only after the user's Steam purchase is confirmed |
| DOA4 | Stub chains (3-seg leaves, generic names) | Limited | node0..node57 (export) | Authored on stub chains | EXTRACTED (chrone skinned GLB) |
| VF5 | YES — 49 bones | 5 digits x 3 segs | Japanese: nl_{oya,hito,naka,kusu,ko}_{l,r}_wj + _b/_c | Authored animation poses | EXTRACTED (Dural SKIN blocks) |
| Soulcalibur II | Unknown (anim format open) | Unknown | Unknown | Unknown | OPEN — 577 anim clips extracted, format decode pending |
| Urban Reign | Terminal hand joint only (no fingers) | None (mitten) | SAKOTSU->KATA->UDE->TE_R/L | Wrist orientation per move (.gyu) | EXTRACTED 2026-10-23 — 49-name bone pool decoded, 72 skinned GLBs |
| WWF No Mercy (AKI) | NO — 19 hinge joints | None | Upper/LowerArm etc. | Wrist only | EXTRACTED (retarget doc) |
| WMXIX (Yukes) | YES — 70 bones | 5 digits x 3 segs | Bip R/L Finger0..4 (+N1/N2) | Per-move detail TRACKS | EXTRACTED (measured skeleton + YANM findings) |
| Def Jam FFNY | Shared skeleton (78 fighters) | Unknown | Unknown | hands_animation layer | PARTIAL — bone map open |
| KOF 3D | — | — | — | — | NO TEARDOWN EXISTS — future acquisition |

## 2. Bone naming conventions (arm + hand)

### Tekken 6-era (T5/T6/TR/TTT2 family) — 147 bones
`arm {left|right} shoulder 1 -> shoulder 2 -> elbow -> wrist`
Fingers: `arm {side} finger {1..5}{a|b|c}` — digits 1-5 (1 = thumb side),
a = proximal, b = middle, c = distal. Plus adjustment bones
(`elbow adj`, `shoulder 2 adj`, `shoulder 1 adj 1/2`, `back`) for deformation falloff.
Bind-pose positions for every joint in tekken6/rigging-reference/tekken6-era-hand-arm.json.

### Tekken 7 — SKT_CH_base_Skeleton (53-joint WH derivative)
`LeftShoulder -> LeftArm -> LeftForeArm -> LeftHand` (UE4 prefix convention).
Fingers: `LeftHandThumb1/2/3`, `LeftHandIndex1/2/3`, `LeftHandMiddle1/2/3`,
`LeftHandRing1/2/3`, `LeftHandPinky1/2` (right mirrors).
DEFECT (WH rigs): left hand missing LeftHandThumb3 + LeftHandPinky3 — fix by
adding the bones and mirroring weights; T7's convention is symmetric.

### VF5 (Dural, 49 bones)
`j_ude (upper arm) -> n_hiji (elbow) -> n_sude (forearm) -> kl_te (hand)`,
with `kl_waki` (armpit) and `n_skata` (shoulder) in the chain.
Fingers: `nl_{oya=thumb, hito=index, naka=middle, kusu=ring, ko=pinky}_{l,r}_wj`
(base) + `_b_` (middle) + `_c_` (distal) = 3 segments x 5 digits x 2 hands.
VF5 also carries FACE bones (chin, eyelids, mouth, brows) — Tekken 7 does not.

### WMXIX (Yukes, 70 bones)
`Bip R Clavicle -> UpperArm (+UpperArm_s) -> Forearm -> Hand (+Hand_s)`.
Fingers: `Bip R Finger0..4` (0 = thumb, rotated rest euler), each with 3
segments (FingerN -> FingerN1 -> FingerN2); fingers parent to Hand, not Hand_s.
Full measured table (positions, eulers, lengths) in wmxix/rigging-reference/wmxix-hand-arm.md.

### DOA4 (58 skin joints, unnamed export)
Hand terminates in 2-3 short leaf chains (<=3 segments) — mitten-style stubs,
no 5-finger articulation. Holds/throws are authored on these stubs.

## 3. Finger segment counts per digit

| Game | Thumb | Index | Middle | Ring | Pinky |
|---|---|---|---|---|---|
| Tekken 6-era | 3 | 3 | 3 | 3 | 2-3 (right 2 in one port — artifact) |
| Tekken 7 (WH 53j) | 3 (2 left — BUG) | 3 | 3 | 3 | 2 (left BUG) |
| VF5 | 3 | 3 | 3 | 3 | 3 |
| WMXIX | 3 | 3 | 3 | 3 | 3 |
| DOA4 | stubs | stubs | stubs | stubs | stubs |
| T3 / No Mercy | 0 | 0 | 0 | 0 | 0 |

Convention across all articulated games: **3 segments per digit** is the norm
(thumb sometimes 2). WH's 53-joint skeleton should be 3/3/3/3/3 on BOTH hands
(fix the left-hand asymmetry).

## 4. How fists vs open hands vs grips are posed

**Every game does this with authored animation, none procedurally.**
- Tekken (all): fingers are keyframed per move — fist for punches, open for
  slaps/parries, grips per weapon/throw. No runtime curl/spread system in any teardown.
- WMXIX goes furthest: **per-move hand/foot detail POSES as separate YANM tracks**
  (finger pair A4955E6E/BA955E6E L/R, thumb tracks) — asymmetric grapple roles
  (one hand grips while the other releases) are authored per move. This is the
  model for WH's throw/grapple hand work.
- Def Jam FFNY: `<hands_animation>` config layer on the shared skeleton —
  same pattern, bone map still open.
- T3/No Mercy: wrist rotation only (no fingers to pose).

WH takeaway: build a **standard hand-pose library** as animations (fist, open,
point, grab/grip, weapon grip), not a procedural system. Author grapple hand
roles per throw (WMXIX pattern).

## 5. Arm pose in idle stance

- Tekken 6-era bind pose: arms straight out at shoulder height in the bind
  (positions in the JSON); stance pose bends elbow + rotates shoulder via animation.
- T3: stance = move-index slots 0-2 of the fighter's divmot bank; arm angles
  from the Euler slots (wrist-only hand motion).
- WMXIX: rest eulers measured per bone (R Hand rest euler 1.5700 rad about X —
  hand hangs ~90 deg from forearm in bind).

## 6. Weight-painting values

- 4 influences max, normalized (UE4/glTF standard) — all games.
- Tekken: heat-map/automatic skinning onto the shared skeleton; L/R symmetric
  naming required for X-mirror painting.
- Pipeline-level mis-weight guards (from WH defects): hand->tail, face->pelvis/spine —
  validate with bone-proximity checks at intake; never paint per-model.

## 7. What WH should do (priority order)

1. Fix the 53-joint finger asymmetry (add LeftHandThumb3, LeftHandPinky3; mirror weights).
2. Author the standard hand-pose animation library: fist (default), open, point,
   grab, weapon grip (Scimitar).
3. Per-throw grapple hand roles, WMXIX-style (separate hand detail tracks per move).
4. Bone-proximity weight validation at intake (kills the hand->tail class of bug).
5. Future pulls: T8 (queued on Steam purchase), SC2 anim bone-track decode
   (weapon grips), Urban Reign PPK/gyu bone map (grapple poses), T5/T6/TTT2
   native skeletons (confirm T6-era proxy 1:1).

## 8. Honesty log (what was NOT pulled)

- T5/T6/TTT2 native skeletons: no parseable skeleton in any release or repo dir;
  the T6-era 147-bone data is a same-family proxy, flagged as such per game.
- SC2 weapon-grip poses: anim files extracted, bone-track format not decoded.
- Urban Reign: bone-name pool DECODED 2026-10-23 (49 names, TE_R/L terminal — no finger bones); 72 skinned GLBs in teardown/urban-reign/models/; .gyu track format still pending for weapon-grip wrist poses.
- Def Jam FFNY: shared skeleton + hands layer confirmed, bone map open.
- DOA4 bone names: export uses generic node names (Team Ninja internals not in export).
- KOF 3D: no teardown exists.
- Tekken 3: FALLBACK-ONLY per standing directive 2026-10-23 — its 18-part rigid layout stays as the gap-filler, never the default reference.
- Tekken 8: queued — do NOT pull until the user confirms the Steam purchase.
