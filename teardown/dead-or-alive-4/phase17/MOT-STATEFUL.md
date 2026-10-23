# DOA4 Phase 17 — Job 3: the .mot stateful per-item length rule

Source bytes: release `doa4-mot-20261022` (tar sha256
`026592a0…21c` re-verified this lane; zack triple re-verified
against `phase15/mot-entries-manifest.json`). Tools:
`phase17/tools/mot_parse_p17.py` (record parser),
`phase17/tools/mot_state_p17.py` (generalized constraint
propagation). Grades as before.

## §1 Method

Phase 16 falsified the per-item length as a PURE function of
the tag (item = u16 tag + k data u16s, k in {1,2}) by
constraint propagation, and named the rule "stateful". This
lane generalizes the same propagation to stateful rule
classes: a rule is a function k = f(state, tag); the
propagator computes, per sub-block, every (state, tag, k)
transition used by SOME exact tiling consistent with the
current table, intersects the per-key k-sets over the whole
corpus, and iterates to a fixpoint. The method is sound for
falsification: under the true rule (if the class contains it),
every block keeps its true tiling, so no block can go dead and
the true transition can never be intersected away. A class is
FALSIFIED when blocks go dead at the fixpoint while the table
is still non-deterministic; it would be a CANDIDATE only with
a deterministic fixpoint and zero dead blocks (proof then
requires >=99% deterministic tiling on plain + m_ files —
never reached here).

Corpus for the falsification sweep: the zack triple
(zack.mot + m_zack.mot + c_zack.mot) = 17,688 sub-blocks of
>= 4 B (16,500 fighter sub-blocks of phase 16's census, plus
the >= 4 B filter). A rule that cannot tile the zack triple
cannot be the rule, so falsification on this subset is
complete; no class survived to need the full 41,096-block
corpus. Scope note: the plain+m_ proof gate would have used
zack + m_zack at full scope — moot, all classes falsified.

## §2 Results (all on the zack triple, k in {1,2} unless noted)

| class | rule shape | keys at fixpoint | deterministic keys | dead blocks | verdict |
|---|---|---|---|---|---|
| 0 | k = f(tag) (phase-16 control) | 729 | 608 | **17,601 / 17,688** | FALSIFIED (reproduces phase 16, harder numbers) |
| i | k = f(tag, previous tag) | 46,172 | 419 | **17,479 / 17,688** | FALSIFIED |
| ii K=2 | k = f(tag, item index mod 2) | — | — | **17,601 / 17,688** | FALSIFIED |
| ii K=3 | k = f(tag, item index mod 3) | — | — | **16,102 / 17,688** | FALSIFIED |
| ii K=4 | k = f(tag, item index mod 4) | 658 | 543 | **17,602 / 17,688** | FALSIFIED |
| ii K=5 | k = f(tag, item index mod 5) | 3,080 | 2,439 | **17,458 / 17,688** | FALSIFIED |
| ii K=6 | k = f(tag, item index mod 6) | 1,261 | 1,025 | **17,568 / 17,688** | FALSIFIED |
| iv | k = f(tag, block's first u16) | 1,992 | 1,954 | **15,652 / 17,688** | FALSIFIED |
| v | k = f(tag, channel index) | 729 | 608 | **17,601 / 17,688** | FALSIFIED |
| 0 widened | k = f(tag), k in {0,1,2,3} | 65,458 | 4,333 | 0 | UNFALSIFIABLE by tiling (61,125 keys ambiguous) — see §3 |
| i widened | k = f(tag, prev tag), k in {0,1,2,3} | — | — | — | NOT COMPLETED in-lane (compute-bound; immaterial: §3 shows widening destroys falsifiability, so this run could at best return 'unfalsifiable', never a proof) |
| count-header | first u16 = item count | — | — | only 2,117 / 17,688 blocks count-feasible | REFUTED |

Class (iii) bit-packed / interleaved-control probes: word
positions mod 2/3/4 show NO control-like residue class (every
residue carries ~57–64k distinct u16 values with ~30% top-16
concentration — uniform), and byte-parity vocabularies show
no tag/data byte split beyond the known u16 structure. A
bit-packed item stream with no positional signature at u16 or
byte granularity is not excluded by these probes; it is also
not evidenced by anything in the file bytes.

Two framing facts worth banking: the first-u16 distribution
is tag vocabulary, not a count (top values 0x000C ×5,575,
0x0010 ×1,483, 0xF00C ×1,391, 0x0014 ×1,135 — the same
multiples-of-4 low bytes {0x0C,0x10,0x14,0x18,0x1C,0x24} that
dominate item-start positions corpus-wide); and the
previous-tag state (class i) constrains almost nothing —
46k surviving (prev, tag) keys with only 419 deterministic —
i.e. knowing the previous item's tag tells you nearly nothing
about the next item's length. Whatever state the rule uses,
it is not carried in the tag stream's local history.

## §3 On the widened length universe

Widening items to k in {0,1,2,3} data words makes tiling
arc-consistency vacuous (0 dead, 93% of keys ambiguous): with
four lengths available, almost any segmentation can be
explained. The {1,2} universe is the one phase 16's hand
parses support (item cadence of tag + 1–2 data words; the
8 B constant-channel form = two 2-word items), and inside it
every functional class above is falsified. The residual is
therefore not "the table is bigger" — it is that **item
length is decided by state that does not live in the
(tag, position, channel, header) features the file bytes
expose locally**: the remaining candidates are (a) a
bit-level control stream with no positional signature,
(b) state set by the RECORD context outside the sub-block
(e.g. a per-record mode word in the descriptor's slack — the
descriptor values are all proven offsets, so this means
state in the table-A/index layer or in the paired .bin),
or (c) a length PREFIX structure (items self-delimiting via
a count/escape the {1,2} cadence misreads — e.g. 0xF0xx tags
as escape markers; the 0xF00C first-tag frequency is
consistent with an escape class but no concrete escape
grammar tested tiles better than the falsified classes).

## §4 CODE route (bounded)

The registry-side loader is proven at instruction level
(`phase17/GHIDRA-PROJECT.md` §3.2): the loader resolves
zack.mot's registry record and opens the file through
0x8238ED10. Forward from there, the record-expansion consumer
was NOT isolated statically — it sits behind the same
indirection wall as Job 2's writer (opened buffers land in
loader-struct destinations; playback reads through pointer
globals; no function in .text walks a loaded .mot buffer's
descriptor with a statically visible 44-loop tied to the
registry record). 44-count loops exist (35 cmpwi/cmplwi 0x2C
sites in .text) but none could be tied to a .mot buffer
without the destination map. This is stated as the code
route's exact frontier, not a negative result about the
consumer's existence.

## §5 Verdict: RESIDUAL (exact) + dynamic closure spec'd

Item 1 is NOT proven. No rule class tested tiles the zack
triple; no expander is shipped; no clip is assembled; no
curves are shipped (curves without a proven rule would be
guesses). The exact residual: the per-item length rule
depends on state not recoverable from the sub-block bytes'
local features by any class in §2. The dynamic closure is
spec'd in `phase17/XENIA-TRACE-SPEC.md` (Capture 1: registry
watchpoint + loaded-buffer dump + expanded-buffer dump for
one zack motion — the consumer's executed loop IS the rule,
read off the trace, then re-proven offline at the >=99%
zack + m_zack tiling gate before any clip work).
