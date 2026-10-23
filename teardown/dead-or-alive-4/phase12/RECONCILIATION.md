# DOA4 Phase 12 — Job 0: RECONCILIATION (annotation only; nothing deleted, no history rewritten)

`ANM-READER4.md` (phase 11, PR #525) is the AUTHORITATIVE ANM doc. It
supersedes the addendum folded into `phase11/ANM-READER3.md` (commit
ae2bd66) on exactly two points:

## (a) The global stream object is 0x833FA3D0 — READER3/STATE's 0x82C3A3D0 is WRONG

Byte proof (quoted from ANM-READER4; re-verified this phase from
`teardown/dead-or-alive-4/workdir/default_pe.bin`): the advance helper
at true VA 0x8242EF58 (phase-11 PE-frame label 0x8243D758) reads

```
8242ef58  lis      r11, 0x8340        ; word 0x3D608340 — imm is 0x8340
8242ef5c  addi     r10, r11, -0x5c30  ; word 0x394BA3D0
8242ef60  lwz      r11, 0xbe0(r10)
8242ef64  lwz      r10, 0xbe4(r10)
```

0x83400000 − 0x5C30 = **0x833FA3D0**, inside `.data`. Every
`0x82C3A3D0` in the phase-11 docs (ANM-READER3 §"stream advance",
PHASE11-STATE) is to be read as 0x833FA3D0. The PHASE11-STATE.md
mention is annotated in place this phase (annotation appended, the
original text kept).

## (b) 0x8243DD08 (PE frame) is a 16-case TAG TRANSLATOR — not "a thunk to undecodable 0x829FD490"

The addendum's characterization rests on a 111-char Ghidra decompile
(`phase11/decomp2/func_0083dd08_FUN_0083dd08.c`) that is a
function-boundary artifact: the function's first two instructions are
the standard XDK prologue (`mflr r12; bl <register-save helper>`),
after which the real body follows in the same bytes. Read raw
(Capstone), the function (true VA 0x8242F508 — see ANM-READER5.md §0
for the frame correction) zeroes obj+0xBD8/+0xBDC, drains the ring via
the helpers, dispatches each entry's tag (≤ 0xF) through a 16-entry
jump table (true VA 0x8242F5F8), and emits records to output arrays at
obj+0x818…+0x858. Cases 7–10 share one handler. The "undecodable
0x829FD490" is the register-save helper's PE-frame label, not a
record consumer.

Phase 12 extends (b) rather than replacing it: the 16 "handlers" are
the translator's own inline case bodies — see
`phase12/ANM-READER5.md`.
