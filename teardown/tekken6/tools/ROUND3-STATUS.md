# Tekken 6 PSP — Teardown ROUND 3: length composition, COM/GMO batch, in-game wiring

Date: 2026-10-20. Lane: teardown sweep, Tekken 6 PSP round 3 (follow-on to
PR #388, branch `teardown/tekken6-round2-decrypt-gmo`).
This round's branch: `teardown/tekken6-round3-length-crack` (off the round-2
branch; new PR, additions only).

Owner acceptance target (2026-10-20 ~20:57 CDT): DONE for this game is its
content LIVE in the western-heart playable build — T6-derived fighters /
movesets / animations usable in a real fight or the customization suite,
verified in `game/` — not just GLBs + docs in `teardown/tekken6/`. The
decrypt crack + GMO batch below are the foundation; §5 is the wiring step
that follows them, per PR #379 (No Mercy wiring), PR #382 (Tekken 3
wiring), PR #385 (full-wiring audit) and PR #397 (wiring standard + gates).

Research basis: game-reverse-engineering PR #29
(`docs/research/teardown-completion-2026-10-20/tekken6-psp.md`) — PROVEN
NEGATIVE: no public decryptor, QuickBMS script, Noesis plugin or GMO parser
exists for this game anywhere (searched GitHub, QuickBMS/ZenHAX, XeNTaX/
ResHax, Noesis indexes). Any claim of a public spec/tool for this format
needs a URL; there is none. The RE therefore comes from our own files:
Ghidra decompilation of the decrypted EBOOT + emulator ground truth
(PPSSPP trace / Unicorn emulation of the game's own inflate). "No public
spec exists" is not a stop sign — the files we hold ARE the spec.

Completion gates (PR #397, Tekken 6 PSP): G1 decryption proof on ≥2
previously unseen files via known-plaintext anchors; G2 trace evidence
archived with the decoder and reproduced exactly; G3 every GMO→GLB
imports clean with skeleton (bones > 0) and normalized weights (geometry-
only = FLAGGED "weights pending"); G4 inventory completeness 40/40
characters listed with status. The strict oracle used throughout this
lane (uncompressed size + adler32 trailer, the value the EBOOT wrapper at
0x8b559c8 itself returns) is stronger than a magic-anchor spot check:
a container is byte-exact only when size AND adler32 both match.

## 1. SOLVED at table level — the length table packing (round-3, code-derived)

Rounds 4–11 and round 2's `exp_len.py` read the EBOOT length table at
0x8bd637c as `LT[symbol - 257]`. **That indexing is off by one.** The
table has 32 halfwords for symbols 256..287; entry `LT[symbol - 256]`
is the length symbol's descriptor (LT[0] = −25 belongs to symbol 256,
the end-of-block code, and is never used as a length; LT[30..31] = −1
are the invalid symbols 286/287).

With the correct indexing, for every one of the 29 length symbols:

- `base = -(LT[sym-256] >> 4)` (arithmetic shift on the signed halfword)
  equals the standard RFC 1951 LBASE **exactly** — 3, 4, 5, …, 227, 258.
- The extra-bit count is the standard RFC 1951 LEXT, packed into the
  same halfword as: `-LT = (base<<4)` when LEXT = 0, and
  `-LT = ((base-1)<<4) + 1 + bitrev4(LEXT-1)` otherwise — i.e. the low
  nibble carries a sentinel 1 plus the bit-reversed (LEXT−1), the form a
  BITREV-first main loop (BITREV at 0x8b55de4, `sra s4, v0, 4` at
  0x8b55de8) consumes.

Proof: `round3-evidence/lt_table_verify.py` — all 29 symbols match both
the base and the packed-extra formula (ALL MATCH: True). This kills the
round-2 framing "lengths are NOT plain LBASE+extra": the bases and the
extra-bit COUNTS are standard. What remains open is only the extra-bit
VALUE composition in the main loop (the shared getbits at
0x8b55e70/0x8b55e8c deriving its count from the descriptor,
`sra t2, t2, 0x1c`) — see §2.

Corollary: round 2's four emulated readings (−(X>>4) ± extra, ± 1) all
desynced because they indexed LT off by one; their negative result does
not constrain the correct composition.

## 2. STILL OPEN — extra-bit value composition (target 1, remainder)

Status at this commit: being fitted against (a) the decompiled main
loop, (b) emulator ground truth — Unicorn emulation of the game's own
inflate at 0x8b55bf0 logging (symbol, length, distance) triples for
container 0 (the PPSSPP WebSocket debugger trace of PR #29's method is
the same ground truth by another route; the Unicorn harness from round 2,
`round2-evidence/experiments/exp_emu.py`, executes the identical EBOOT
code deterministically), and (c) the adler32 oracle over all 76
containers. The crack is claimed only when the full 76-container run is
byte-exact; per PR #397 G1 the formula must also verify on ≥2 files not
used for fitting.

Current score (unchanged until the fit lands): **20/76 byte-exact.**

Named hypotheses under test (in order):
- H1: extra values are consumed bit-reversed (the loop's BITREV-first
  buffer orientation) for length extras only / distance extras only /
  both.
- H2: length-extra and distance fields are emitted in swapped order by
  the custom encoder.
- H3: the getbits count for length extras is the descriptor top-nibble
  value, which differs from LEXT for a subset of symbols.

## 3. COM / GMO batch (target 2)

Blocked on §2 (the 18 COM containers, gzip idx 58–75, are among the 56
failing containers). The GMO→GLB pipeline is proven (round 2 §5:
PiosGmoLibrary → gmo2json → Blender glTF export; `cloud.glb` re-imported
and front-rendered). The often-quoted "40 character meshes / 18 COM
files" is roster scope, not a measured mesh count — per PR #29 the
content type of the COM containers is NOT confirmed until a full decode
exists. Per-character isolation law applies end-to-end (round 2 §7):
each character's meshes/skeleton/animations/add-ons in its own directory,
each GLB self-contained with its own skeleton and clips.

Gate status: G3/G4 cannot be scored until the first COM container
decodes; the inventory in §5 will be built from the decoded data, not
from the roster assumption.

## 4. Research / pull-in log (round 3)

| What | Source | License | Where it landed | What it unlocks |
|---|---|---|---|---|
| Deep-research docs (PR #29 + PR #397) | mhvnsnt/game-reverse-engineering + mhvnsnt/western-heart (team research lane) | ours | read-only reference | proven negative (no public tool), PPSSPP-trace method, gates G1–G4 |
| Unicorn 2.1.4 + Capstone (round-2 harness) | pip | BSD / BSD | lane scratch only | emulator ground truth for §2 (executes EBOOT inflate directly) |
| Ghidra 12.1.4 | NSA Ghidra (team tools dir) | Apache-2.0 | used from tools/ghidra/ (not vendored) | targeted main-loop decompilation |

Nothing new was pulled for a public T6 decryptor/GMO parser because none
exists (PR #29 proven negative, with URLs for every tool checked there).

## 5. In-game wiring (acceptance target, after §2/§3 land)

Planned, following the #379/#382 precedents: `teardown/tekken6/
WIRING-INVENTORY.md` covering every decoded file (WIRED with the
consuming path in `game/` / `moveset-library/` / `customization/`, or
FLAGGED with a named reason); canon conversion logged in
`CANON-CONVERSION.md` + RENAME-MAP discipline (no invented identities);
T6-derived fighter content registered in the build the same way Tekken 3
content was (PR #382); verification evidence from the build itself
before any "playable" claim. Once proven, the decoder is also encoded
as a QuickBMS script alongside `tekken6_gzip.py` (PR #29 delivery form).

## 6. Scoreboard (live)

- GZIP containers byte-exact: **20/76** (target: 76/76).
- Length table packing: **SOLVED** (§1, script-verified 29/29).
- Extra-bit value composition: OPEN (§2).
- COM containers decoded: 0/18 (blocked on §2).
- Tekken 6 GMO→GLB: 0 (blocked on §2); pipeline proven on samples.
- Wired into playable build: 0 (blocked on §2/§3; plan in §5).

---

## Round 3 — session 2 addendum (2026-10-20, emulator ground truth)

### A. THE LENGTH TABLE IS FULLY SOLVED (verification strengthened)

`lt_table_verify.py` was re-run against values read DIRECTLY from
`EBOOT.DECRYPTED.ELF` (LT at file offset 0x3d337c, vaddr 0x8bd637c): the
transcription used in round 2 matches the binary byte-exact, and with the
corrected index `LT[sym-256]` all 29 length bases and extra-bit counts equal
RFC1951 LBASE/LEXT. The DIST table at 0x8bd63bc = DBASE-1, byte-exact.
So: length/distance BASES and EXTRA COUNTS are standard. No table defect
remains. (Deliverable formality still owed: a QuickBMS script — pointless
until a full decode exists to encode; deferred with the decode itself, not
dropped.)

### B. EMULATOR GROUND TRUTH — THE GAME'S OWN INFLATE REJECTS THE STREAMS

Built a Unicorn harness (`round3-evidence/emu3.py`) that executes the
EBOOT's real wrapper 0x8b559c8 / inflate 0x8b55bf0 from the decrypted ELF
(Allegrex BITREV/CLZ/MAX/MIN emulated via NOP-patch + code hook; QEMU's
MIPS core cannot execute them natively). Validation: container 19 output
byte-identical to the Python decoder (960 B, adler-exact file).

Result on container 0 (entry 454): the game's inflate returns its own
error 0x80000108 after producing EXACTLY the same 2,815 bytes as the
Python decoder, failing at the same match (sym 258, len 4, dsym 24,
dist 5978 > out 2815). An instrumented run
(`round3-evidence/emu_log.py`) logging (out, len, dist) per match from
the game code matches the Python decoder's log for every match including
the failing one (emu dist reads 1 lower — an artifact of the copy loop's
-1(s4) addressing in the logger, identified and accounted).

The loader was also fully traced in the EBOOT:
- Sole wrapper caller: 0x89d27a0 — checks "GZIP" magic, passes
  (dest, len, container+0x14, &adler). No priming, no dictionary, no
  preprocessing.
- Its callers (0x887e56c, 0x887e7fc, 0x89dab8c) pass a FRESHLY ALLOCATED
  buffer of exactly w[3] bytes.
- The only other inflate caller (0x8b55728, in a gzip-file library whose
  magic check is 1f 8b) is a plain single-shot uncompress; it is not a
  streaming/dictionary variant.

CONCLUSION (proven by executing the game's own code): the "main-loop
length composition" defect chased since round 2 DOES NOT EXIST in the
game's inflate — its composition is standard, and it cannot decode these
containers standalone either. The defect framing is retired.

### C. WHAT THE STREAMS ACTUALLY DO (all measured, idx0 unless noted)

- Bit-exactness: block 2's dynamic header (bit 182,510) parses
  Kraft-exact (CL/lit/dist all 1.000000). Base-rate control: 0/3000
  random bit offsets in the same stream yield a Kraft-exact header.
  The bitstream, symbols and extra values are exactly as parsed; there
  is no desync.
- Violations: 117 of 9,460 matches in idx0 have dist > out (excess
  7..20,628 bytes); ALL other matches are standard-valid. Same pattern
  in all 56 failing files: first violation at compressed bit
  ~7,900–9,300 (scoreboard: `round3-evidence/scoreboard_strict.txt`,
  20/76 byte-exact — unchanged).
- Length sum: standard composition yields 104,054 of 105,472 bytes
  (-1,418) for idx0 — independent of any dictionary (dictionaries do
  not change output length). Other files range widely (idx5 -19,949;
  idx17 lenient parse terminates at 24,407 of 122,288 with 280,790
  stream bits unconsumed; idx58 misreads as stored blocks with bad
  NLEN after its first dynamic block).
- Population split: 23/76 files parse cleanly to the exact end of
  their stream under lenient continuation; 53/76 hit invalid codes
  during lenient continuation, i.e. at least one match class consumes
  a different number of bits in the true format for those files.
- Ruled out with evidence: per-entry raw sub-file as dictionary
  (zlib zdict test — output length unchanged at 104,054, adler still
  fails); predecessor-plaintext dictionary (same test class); symbol
  table shifts (len+1/dist+1 tested, worse); bit-reversed extras
  (tested round 3 session 1 — breaks good matches); field reordering
  (breaks at match 2-3); layout field correlation (exact files occur
  in both 'relaxed' and 'H1'); sector-cipher corruption (streams
  parse bit-exact — a wrong cipher gives garbage, not a valid parse);
  a second decoder anywhere (EBOOT-wide: exactly ONE code-length ORDER
  table; bulk-wide scan: 0 ELF headers, 0 ORDER-table copies, 0 LT
  copies in 384 MB; no zlib/kernel-decompress imports in EBOOT
  strings).

### D. REFRAMED DEFECT + NAMED NEXT STEP

The containers were encoded against a decode context the EBOOT's
bundled inflate does not provide (pre-window data plus value/bit
consumption differences that vary by file population). No decoder for
this encoding exists in any artifact we hold, and the deep-research
proven negative stands (no public spec/tool exists anywhere; this doc
is the citation). The mandated ground-truth method is the PPSSPP live
trace: run the retail game, breakpoint 0x89d27a0 / 0x8b559c8 during a
real DATA401 load, and record whether the runtime calls this inflate
for these entries at all, with what (dest, src) — plus a WebSocket
debugger trace of (block index, offset, size) per the teardown-
completion gates (PR #397, gates G1/G2). Setup is documented in the
recon archive (`PPSSPP-LIVE-RUN-GUIDE.md`). PPSSPP is not currently on
disk (cleared under the store-and-work law); re-pulling it plus the
ISO is the first step of that lane. The Unicorn harness above is the
offline equivalent for the code path itself and stays as evidence.

### E. GATE STATUS (PR #397)

- G1 (decryption proof on >=2 unseen files): NOT MET — 20/76 decode
  byte-exact (those 20 are proven), 56 do not decode with any decoder
  available; the encode context is unidentified.
- G2 (emulator/debugger offset log archived): PARTIAL — Unicorn trace
  logs archived here (emu3/emu_log + this doc) proving the EBOOT code
  path; the PPSSPP WebSocket trace is still owed (see D).
- G3 (GMO->GLB clean imports): NOT MET for Tekken 6 content — blocked
  on G1 for the 18 COM containers (idx58-75).
- G4 (inventory 40/40 with status): MET as an inventory — see
  WIRING-INVENTORY.md (this PR): all 76 containers + the 18 COM files
  listed with per-file status; character assignment of COM files
  remains impossible until they decode (round 11 proved the COM
  container header from clean prefixes; content type unconfirmed).

### F. TARGET 2 (COM/GMO batch) — BLOCKED, honestly

The 18 COM containers (gzip idx 58-75, entries 709-735) share the
same decode defect (first violations at bit ~7,947-8,242). Zero T6
character meshes can be converted until the decode lands; claiming
otherwise would require fabricating models. The GMO->GLB pipeline
itself remains proven from round 2 (PiosGmoLibrary + Blender,
cloud.glb in PR #388). Per-character directories will be created from
the decoded COM inventory in the same PR series once G1 lands.
