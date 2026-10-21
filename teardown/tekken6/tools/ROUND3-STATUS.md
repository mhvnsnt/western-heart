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
