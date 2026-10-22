# Tekken 6 PSP — ROUND 15 STATE (FINAL static round)

Branch: `teardown/tekken6-round15-glyph-tail-final` stacked on PR #705
(`teardown/tekken6-round14-textures-vtype7` @ 3c0dd6e4).
Started: 2026-10-22. This is the final static round: glyph tail,
COM slots 25/26/30 structure, and the static final-state closeout.

## Input note (recorded at lane start, own-eyes)

`~/workspace/_t6r4-work/` does not exist on this VM (verified by
direct `ls`). The round-14 scratch `~/workspace/_t6r14-work/` DOES
exist on this VM and carries the round-14 regeneration: ISO
sha256 `b5e52660a52caeca351e93c54bb4db0011325af0c1e3c67230bddde8f7cecf44`
== GitHub release `tekken6-psp-v1` asset digest (re-verified this
round via `gh release view`), `bulk_decrypted_r14.bin`, and
`decoded76/` container outputs. The 18 COM files are re-verified
sha256 against the round-7 moveset JSONs before use in Jobs 1/2
(verification output lands with each job's evidence). Repo work
happens in a blobless sparse clone at
`~/workspace/_t6r15-work/western-heart` (sparse: `teardown/tekken6`
only; HEAD == 3c0dd6e4 at lane start, verified).

## Jobs

1. **GLYPH TAIL** — 12 unproven codepoints (E006, E008, E009,
   E00A, E00B, E00E, E00F, E01A, E01D, E01F, E021, E022, E023)
   gating 605 partially-decoded moves. Proof standard unchanged:
   a codepoint is fixed only when >=1 move carrying it decodes
   EXACTLY to that move's cited T6 notation AND its charmap
   position is consistent. Enumeration hypotheses are tested,
   never assumed. Deliverables: completed glyph map (or exact
   per-codepoint remainder), additive v3 moveset JSONs (v2 files
   untouched), evidence table with named external sources.
   Status: **COMPLETE** — all 13 codepoints PROVEN
   (`tools/round15-evidence/JOB1-GLYPH-TAIL.md`): E006=u; the
   hold-direction ring E008-E00F = D/B, D, D/F, B, F, U/B, U, U/F
   (E00C revised to its glyph identity F; E00D never occurs in
   the corpus, ring-assigned only); buttons E01A=2+3, E01D=1+4,
   E01F=1+2+4, E021=1+3+4, E022=2+3+4, E023=1+2+3+4 (the block
   E015-E023 is exactly the 15 non-empty subsets of {1,2,3,4},
   highest-button-major). 18 additive v3 moveset JSONs:
   6,814/6,814 notation moves fully decoded (605 partial -> 0);
   0 field diffs vs v2/originals outside the notation layer.

2. **COM SLOTS 25/26/30 PACKED-STRUCTURE RECOVERY** — cross-file
   structural analysis over the 18-file panel (correlations,
   entropy profiling, autocorrelation, first-bytes classification).
   A structure is PROVEN only when a parser reads >=2 files' slots
   into records cross-validating against known data. Status:
   PENDING.

3. **TEKKEN6-FINAL-STATE.md** — static closeout with PR/round
   citations + final WIRING-INVENTORY section. Status: PENDING.

## Proven ground (not redone, per brief)

Containers 76/76 adler-exact; NDPP fully decoded (3,444/3,444
slice parts incl. VTYPE-7 RGBA8888); skeletons = r11 set only;
stage packages = placement+texture containers (closed);
count-word 176 closed (external count); COM tail records = empty
MOTA stubs (closed); NTPP pixels + palette unit->bone are
CAPTURE-CLASS (rounds 12+14 terminal negatives — not re-hunted;
the PPSSPP GE capture spec stands in rounds 12/13 docs).

## Method notes
- Capstone targeted reads only if needed; NO full Ghidra analysis.
- Additions-only; no `git add -A`; pathspec commits after EVERY job.
- Per-character isolation: moveset JSONs stay per-character files.
- `/tmp` is a volatile 512 MB tmpfs — scratch lives in
  `~/workspace/_t6r15-work/` or the repo tree, never `/tmp`.

## Deletions
None.
