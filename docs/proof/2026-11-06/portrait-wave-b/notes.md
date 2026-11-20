# M3 — portrait recapture Wave B (2026-11-06)

## Method

- Pipeline: `tools/portraits/capture.mjs` (the S4 pipeline), unmodified,
  run from a serve tree pinned to main `839565071bf9152b54dec0cb515bd1ca1dbb84d2`
  (the M2 merge). The tree was seeded file-by-file from that ref (GitHub API /
  raw content at the ref) and completed on demand by a local caching proxy
  fetching the same pinned ref; the lane scratch `fetched.log` holds the
  per-file fetch record. The portraits gate passed on the unmodified tree
  before any capture ran.
- Asset-source guard: `game/js/asset-config.js` sends non-bundled models to a
  remote asset bucket first, so an unmodified serve could have rendered bucket
  copies instead of the pinned tree's rebuilt models. In the SERVE COPY ONLY,
  the remote candidates were neutralized (remoteBase emptied, fallback base
  pointed at the local server) so every model byte came from the pinned main
  tree. No repo file carries this change; it is disclosed as a deviation in
  the PR body.
- Captures: ryusan alone first (currency check against her #1588 card), then
  one batch: pond, tobi, chatur, megami, menajerii, kingtyrant, nightwolf,
  michiko, cainelias. star and gashadokuro were NOT attempted (blocked on L2).

## Outcomes

Shipped (6) — all stance:true via the roster-standard cmu-14_01 select
stance, framed:true, cards viewed before shipping (framed head-and-shoulders;
no head-crop defect of the diablo/burger class):

- pond — bones 52 → 224, bank recorded null → raven
- tobi — bones 73 → 255, bank null → hwoarang
- ryusan — bones 521, stance false → true (see below)
- chatur — bones 52 → 264, bank ogre
- megami — bones 52 → 469, bank null → jun
- menajerii — bones 52 → 450, bank kuma → roger

The bank stances themselves were rejected by the PreviewPane fit gate
(pond's bank stance: left shoulder swung 1.61 rad from bind; ryusan's:
1.23 rad) and the select screen's own cmu stance carried each pose — the
manifest records exactly that (stanceSource cmu-14_01). No fallback-framed
card is shipped as a stance card.

Ryusan: the #1588 card did not match a fresh capture, so she was not
skipped. That card was a framed bind/aim card (stance false, armDeg 87/87).
Her bank stance still fails the fit gate, but the cmu select stance now
retargets cleanly onto her full 521-bone rig (armDeg 23/12), so her
POSE-BLOCKERS entry is removed in this PR, as `test/portraits.test.mjs`
requires once a manifest records stance:true. The bank-stance rejection is
unchanged and remains a rig/anim-lane item, recorded in the handoff.

Captured, not shipped (3):

- michiko — capture reproduced her current card byte-for-byte; no change.
- kingtyrant, nightwolf — bones 0 / stance false / framed false: the
  attire-1 GLBs present no skinned mesh/skeleton to the select screen, so
  no posed card exists. Their fallback captures are byte-identical to
  their current cards; cards and POSE-BLOCKERS entries retained.
- cainelias — same unposed class (skeleton-less; the S3 scale fix added no
  skeleton). His fallback capture differs from his current card (framing
  of the rescaled model) but is not a posed card; current card retained
  per the Wave 2 brief. POSE-BLOCKERS entry retained.

Not attempted (2): star, gashadokuro — still blocked on L2 (gashadokuro
re-rig).

## Gate

`test/portraits.test.mjs` re-run on the post-change tree:
"portraits: 50 select fighters, 5 pose blockers, 7 registered placeholders"
— PASS, exit 0.

## Files

- `capture-log-m3-20261106.json` — the capture.mjs result lines, exactly as printed.
- `portrait-hashes-m3-20261106.json` — per-card sha256/bytes, main vs captured, for all 10 attempted.
- `contact-sheet-m3-20261106.png` — the six shipped cards (pond, tobi, ryusan / chatur, megami, menajerii).
