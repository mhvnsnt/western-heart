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
- [x] Step 1: tooling re-pulled by the predecessor (PPSSPP v1.20.4 +
  ISO + recon bulk in `_t6r4-work/`, inherited intact by the recovery
  lane — see §Pull-ins).
- [x] Step 2: static loader chain — DONE 2026-10-21 (see §Findings F1–F3,
  evidence `round4-evidence/dis_loader.py` + `loader_dis.txt`).
- [x] Step 3: PPSSPP live trace — RUN (recovery lane, 2026-10-21; see
  F7). Result is a NEGATIVE with a positive control: breakpoints proven
  working, loader/wrapper/inflate fired ZERO times across reset-boot +
  menu inputs (this lane) and the predecessor's full autopilot run to a
  stage/saving screen. No failing-container load through 0x89d27a0 was
  observed in any driven path, so no RAM-vs-bulk byte diff could be taken.
- [x] Step 4: encode-context verdict — NARROWED, not closed (see F4–F7).
  Header/flag difference: DEAD (F4). Bit-reversed extra values: DEAD
  (F5). Every held candidate dictionary: DEAD, and the output-length
  shortfall is dictionary-invariant, so a window alone cannot be the
  whole answer (F6). No change to `tekken6_gzip.py` is justified by
  evidence yet; score stays 20/76.
- [ ] Step 5: if 76/76 (or decode otherwise proven): QuickBMS .bms + Target 2
  COM/GMO batch (40 meshes / 18 COM files → per-character GLBs, ≥4 viewed
  front renders) + WIRING-INVENTORY.md update.
- [ ] Step 6: if the trace shows raw-bytes-in (context truly absent):
  land that proof + context candidates ranked by evidence.

## Pull-ins (research mandate: source / license / where landed)

| What | Source | License | Where it landed |
|---|---|---|---|
| PPSSPP v1.20.4 (AppImage, extracted) | PPSSPP project release (predecessor pull) | GPL-2.0+ | `_t6r4-work/ppsspp/` (local working set only, not vendored into the repo) |
| Tekken 6 PSP ISO | owner's disc image, release `tekken6-psp-v1` (sha256 b5e52660…) | owner's copy | `_t6r4-work/iso/` (local working set only) |
| Recon bulk (`bulk_decrypted.bin` + manifest) | team's round-3 decrypt (PR #388/#413 lineage) | ours | `_t6r4-work/recon/x/tekken6/work/decrypt3/` (local working set only) |

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

## Findings — recovery lane (2026-10-21, after the runtime-restart kill)

Predecessor state recovered intact: branch 2 commits ahead of PR #413,
PPSSPP v1.20.4 setup + ISO + recon bulk in `_t6r4-work/`. PR #446 opened
by this lane FIRST (the predecessor died with commits but no PR).

### F4. Container header / manifest fields do NOT separate PASS from FAIL

`round4-evidence/header_field_test.py` compared all 76 containers:
header words w[0..4], prefix16 presence+values, zlib header bytes,
manifest layout/magic, sizes. Result: w[1]=w[2]=1 for all 76; zlib
header `78 da` for all 76; prefix16 occurs in both sets (PASS 19/20,
FAIL 16/56); layout H1/relaxed occurs in both sets. The ONLY systematic
split is SIZE: every PASS container is tiny (uncompressed 336–1,088,
file 80–144 bytes); every FAIL container is ≥9,040 uncompressed /
≥7,104 file bytes. There is no type/flag context in the container table.
The "failing blocks are a different container type" candidate is DEAD.

### F5. Bit-reversed extra-bit VALUES are DEAD (length, distance, both)

`round4-evidence/rev_extras_test.py` re-decoded idx0/11/40 with the
length-extra bits, the distance-extra bits, and both, bit-reversed
within their (unchanged) bit counts: end-of-stream stayed exact (bit
consumption unchanged, as designed) but violations got WORSE
(idx0: 117 → 118 revL, 133 revD, 133 revLD) and the length shortfall
barely moved (−1,418 → −1,376). This closes the value-orientation class
left open by round 3 session 1's ambiguous "bit-reversed extras" note.

### F6. No held dictionary works — and a dictionary alone CANNOT be it

`round4-evidence/dict_sweep.py`: history-aware decode of idx0/11/40
with candidate 32,768-byte windows — zeros, 0xFF, concatenated PASS
plaintexts, EBOOT head/tail, and the manifest-predecessor files (bulk
order, 1–3 back, per target). Every candidate: adler32 FAILS and the
output length is IDENTICAL to the no-dictionary decode (idx0 104,054
of 105,472; idx11 11,287 of 12,080; idx40 70,615 of 70,704). Output
length is a pure function of the symbol stream, so the shortfall is in
the length accounting itself (or in what w[3] counts), independent of
any window. Combined with F5 and round 3 §C, the remaining shape of the
defect is: bit consumption is exact end-to-end on the clean-parsing
files, lengths sum short, and early matches reference up to ~20 KB
before the output start. Any future hypothesis must explain ALL THREE.

### F7. PPSSPP live trace: breakpoint mechanism PROVEN, loader NEVER fires

Evidence: `round4-evidence/ppsspp_control_out.txt` (predecessor's
`ws_control.py`, written but never run to a saved result before the
kill; run by this lane) and `round4-evidence/trace_r5.jsonl`.

- POSITIVE CONTROL: a breakpoint on a hot PC sampled from the running
  game (0x8ac6c74, a polling loop) fired repeatedly (cpu.stepping
  events) and SURVIVED `game.reset`. The WebSocket breakpoint mechanism
  works; a zero-hit result on other addresses is meaningful.
- With breakpoints on loader 0x89d27a0, wrapper 0x8b559c8, inflate
  0x8b55bf0 (+ the hot-PC control), across a reset-boot followed by the
  menu input schedule (cross/start ×7 over ~6 minutes), EVERY event
  was the hot PC (exact tick cadence +3,703,700/event in the follow-up
  probe). Loader/wrapper/inflate hits: **ZERO**.
- The predecessor's longer autopilot run (boot → menus → stage
  background → saving screen, screenshots in `_t6r4-work/`) likewise
  recorded loads: 0 in every trace file.
- Supporting scan: the decrypted EBOOT's import library names contain
  NO sceDeflate/sceZlib-style stub (libraries: sceAtrac3plus, sceAudio,
  sceCtrl, sceDisplay, sceGe_user, sceImpose, sceMpeg, sceNet*, scePower,
  scePsmfPlayer, sceRtc, sceSasCore, sceUmdUser, sceUtility, sceWlanDrv,
  Kernel_Library, …), and the ISO's only loadable modules are the two
  psmf (video) PRXs. No second decoder ships as a separate module.

VERDICT (evidence-bounded): the 56 failing containers are NOT decoded
through loader 0x89d27a0 in any path driven so far (boot, title, menus,
arcade stage load). Remaining candidates, ranked:
1. **Mode-specific loads not yet driven** — the COM set (idx58–75) is
   plausibly customization/model-viewer data; drive CUSTOMIZATION and
   GALLERY modes specifically under the same breakpoints before
   concluding the loader is never used for them.
2. **A decoder inside a DATA401-loaded overlay** — the game loads code
   overlays from DATA401; F1's closed call graph covers only the EBOOT
   image. A RAM dump during an active fight/customization screen
   (breakpoint-independent) searching for GZIP container bytes and for
   decoded GMO/COM plaintext decides this and candidate 1 together:
   if decoded plaintext is in RAM, diff the RAM container bytes vs
   `bulk_decrypted.bin` at the same addresses.
3. **Upstream transform of the container bytes** (the Step-2/F3
   hypothesis) — only testable once a real load is observed (candidate
   1/2 produce one); statically there is no second route (F1).

## Scoreboard (live)

- GZIP containers byte-exact: **20/76** (unchanged — no evidence-justified
  decoder change exists yet).
- PPSSPP trace: RUN — control positive, loader hits 0 (F7).
- New exclusions landed: header/flag type difference (F4), bit-reversed
  extras (F5), all held dictionary candidates + dictionary-only class
  for the length shortfall (F6).
- COM/GMO batch: still blocked (COM idx58–75 all in the failing set);
  QuickBMS .bms still deferred WITH the decode (encoding a 20/76
  partial result as the format would be a false claim).
