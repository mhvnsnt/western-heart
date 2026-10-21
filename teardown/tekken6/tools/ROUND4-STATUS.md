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
- [x] Step 2: static loader chain — DONE 2026-10-21 (see §Findings F1–F3,
  evidence `round4-evidence/dis_loader.py` + `loader_dis.txt`).
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

### F1. Call graph is closed (byte-scan of the whole EBOOT image)

`round4-evidence/dis_loader.py` scanned every aligned word of the loaded
image for `jal`/`j` targets and for data-word references:

- Wrapper `0x8b559c8` has exactly ONE caller: `jal` at `0x89d27e4`, inside
  the GZIP loader function at `0x89d27a0`.
- Inflate `0x8b55bf0` has exactly TWO callers: the wrapper (`0x8b55a48`)
  and the gzip-file library's single-shot uncompress (`0x8b55728`).
- Loader `0x89d27a0` has exactly THREE callers: `0x887e56c`, `0x887e7fc`,
  `0x89dab8c`.
- ZERO data-word references to wrapper/inflate/loader anywhere in the
  image (no function pointers, no vtables). There is no other route to
  this inflate.

### F2. The loader passes RAW container bytes — no slicing, no priming

Loader `0x89d27a0` (full disassembly in `round4-evidence/loader_dis.txt`):
takes `(holder, dest, dest_len, adler_out)`, reads `container = *holder`,
checks `*(u32*)container == "GZIP"` (0x50495a47 LE), and calls the wrapper
ONCE with `(dest, dest_len, container + 0x14, adler_out)`. No loop, no
chunking, no offset other than +0x14, no window/dictionary priming (the
wrapper itself rejects FDICT — round 2 §3 stands). Neighbour accessors
confirm the header layout the callers use: `0x89d2740` returns
`container[+0xc]` (w[3], uncompressed size), `0x89d2770` returns
`container[+0x10]` (w[4]).

### F3. All three callers feed (fresh dest, w[3]) the same way

- Caller A `0x887e56c` and caller B `0x887e7fc` (resource-manager loads):
  dest size `s = (manager_field_0x70 < 2) ? 0xABC00 : container[+0xc]`;
  a buffer of that size is obtained from the allocator pair
  `0x8a69538`/`0x8a694d8` immediately before the single loader call
  (freshly allocated per load). `0xABC00` = 703,104 — a capacity floor,
  near the largest COM expectation (703,400) but not equal to it.
- Caller C `0x89dab8c`: dest from accessor `0x8aab8c8(holder)`, length
  w[3] (recovered through the MIPS delay slot at `0x89dab30`:
  `move s3, v0` executes before the `+0x10` accessor returns, so s3
  holds the `+0xc` value); the non-GZIP twin path plain-copies w[3]
  bytes — same length field, no slicing either.

CONCLUSION SO FAR: statically, the game's own load path feeds the wrapper
exactly the bytes the Unicorn harness fed it (raw container body at
+0x14, fresh dest, length w[3]). If a live PPSSPP load of a failing
container SUCCEEDS, the difference must be in the container bytes as they
exist in RAM at load time (i.e. upstream of the resource manager — the
DATA401 read/decrypt path that produced our `bulk_decrypted.bin` is the
remaining place a transform could hide), or the failing containers are
never loaded through this path at all. The live trace (Step 3) decides
between those two.

## Scoreboard (live)

- GZIP containers byte-exact: **20/76** (entry state, round 3).
- PPSSPP trace: NOT YET RUN.
- COM/GMO batch: blocked on the decode (round 3 §F stands until §Step 4).
