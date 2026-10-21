# Tekken 6 PSP — Teardown ROUND 4: PPSSPP live trace / encode-context hunt

Date: 2026-10-21. Lane: teardown sweep, Tekken 6 PSP round 4 (follow-on to
PR #413, branch `teardown/tekken6-round3-length-crack`).
This round's branch: `teardown/tekken6-round4-ppsspp-trace` (off the
round-3 branch; new PR, additions only).

Owner acceptance target (2026-10-20 ~20:57 CDT): DONE for this game is its
content LIVE in the western-heart playable build — T6-derived fighters /
movesets / animations usable in a real fight or the customization suite,
verified in `game/` — not just GLBs + docs in `teardown/tekken6/`.

## State file (kept current after every step — round-4 discipline)

- [x] Step 0: read PR #413 / ROUND3-STATUS.md (A–F + addendum) +
  WIRING-INVENTORY.md. Score at entry: **20/76 byte-exact**. Round-3 reframing
  accepted as entry state: the Python decoder is a faithful reproduction of
  the EBOOT wrapper 0x8b559c8 + inflate 0x8b55bf0 (Unicorn ground truth —
  the game's own code returns 0x80000108 on container 0 after the identical
  2,815 bytes). The 56 failing containers are not standalone-decodable with
  raw container bytes; an unidentified ENCODE CONTEXT is the open question.
- [ ] Step 1: re-pull tooling (PPSSPP headless + ISO pieces + recon EBOOT/bulk
  materials), minimal footprint, pull-ins logged in §Pull-ins.
- [ ] Step 2: static loader chain — full arg trace of sole wrapper caller
  0x89d27a0 and its callers (what src pointer/length, what dest, any
  chunking/slicing/looping), byte-scan for any other wrapper/inflate callers.
- [ ] Step 3: PPSSPP live trace of a real DATA401 load of a FAILING container
  (start: container 0): record (buffer address, offset, size) passed to the
  wrapper/inflate + dump the exact input bytes fed; diff vs the raw container
  bytes the Unicorn harness used.
- [ ] Step 4: encode-context verdict. If identified: implement in
  `tekken6_gzip.py`, re-run all 76, regression-check the 20, report honest
  score (size + adler32).
- [ ] Step 5: if 76/76 (or decode otherwise proven): QuickBMS .bms + Target 2
  COM/GMO batch (40 meshes / 18 COM files → per-character GLBs, ≥4 viewed
  front renders) + WIRING-INVENTORY.md update.
- [ ] Step 6: if the trace shows raw-bytes-in (context truly absent):
  land that proof + context candidates ranked by evidence.

## Pull-ins (research mandate: source / license / where landed)

| What | Source | License | Where it landed |
|---|---|---|---|
| (pending) | | | |

## Findings

(appended as they land — emulator/code evidence only, no formula guessing)

## Scoreboard (live)

- GZIP containers byte-exact: **20/76** (entry state, round 3).
- PPSSPP trace: NOT YET RUN.
- COM/GMO batch: blocked on the decode (round 3 §F stands until §Step 4).
