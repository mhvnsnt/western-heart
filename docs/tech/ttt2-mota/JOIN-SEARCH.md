# Anim-index join search — per-move → MOTA index (2026-11-03)

Question: where is the table that maps a character move (rog.json row /
jun.json row) to an index into data004's big MOTA table (0..1874)?
Already excluded before this run: data000/002/018/052 (prior lane).
This run: data001 exhaustive + re-verification of the excluded set with
anim-specific patterns.

## data001 (this run's target) — NEGATIVE, exhaustive

- File: `~/workspace/_ttt2-work/pulls/top__decoded-data001-full.bin`,
  851,749,584 B. NRFI boxes tile exactly: ftyp 20 + head 28 + idgt 200 +
  imge 851,749,336. Section table (repo:
  `teardown/tekken-tag-tournament-2/data001-section-table.json`): 2,943
  sections, sizes sum to the decoded total exactly.
- **Content is an NTXR texture container** (repo doc
  `DATA001-DATA028-DECODE-20261030.md`): imge payload signatures MBB, NTXR,
  eXt, GIDX, then texture data. Signature census on the decoded bytes:
  NTXR ×669, GIDX ×5,938, MBB ×128, **MOTA ×0**.
- Full-file regex census (authoritative, run on all 851,749,584 B):
  `bxml` ×0, `mvlt` ×0, `BXML` ×0, `MVLT` ×0, `\x00rog` ×0, `\x00jun` ×0.
  (An earlier partial count reported nonzero bxml/mvlt hits; the full-file
  scan supersedes it — there are not even false-positive hits.)
  ASCII `Jn_`/`Rg_`/`Jun`/`Rog` hits all sit in gibberish byte contexts
  (pixel data), none is a readable identifier.
- Anim-header patterns (`00 64 00 17` ×22, `00 64 00 1B` ×14, `00 C8 00 17`
  ×1) occur at texture-data density — the same patterns occur by chance in
  851 MB of pixel data and none is followed by a valid clip structure
  (spot-checked contexts are noise). No moveset binary, no index table,
  no per-character section exists in data001. **data001 cannot contain
  the join: it is textures only.**

## Re-verification of the previously excluded files (anim patterns)

| file | size | MOTA | anim headers | verdict |
|---|---|---|---|---|
| data000 | 17,755,827 B | 0 | 0 | XML joins (MainID↔BXML, repo `DATA000-XML-JOIN-20261025.md`) + PCTB/MCAM + menu scripts; no anim data |
| data002 | 126,254,992 B | 0 (prior lane) | — | NSXR texture program (repo doc) |
| data018 | 3,027,808 B | 0 | 0 | BXML/MVLT display movesets — move names/notation only (e.g. "Junkyard Kick"); rog.json/jun.json records carry NO numeric anim field (`anim_ref` is the synthetic `ttt2:rog:row:N`) |
| data052 | 15,463,552 B | 0 | 0 | card/customization text ("Roger Cards", localized names); no movesets |

## Where the join actually lives (evidence-based pointer)

Kiloutre's pipeline never reads a file-based join: `motbinExport.py` parses
the moveset binary **from live game memory** (T7/Tag2 motbin), where each
move record carries `anim_addr` — a pointer into the loaded MOTA — plus
`anim_name`. motasearch.py documents the in-memory reference value format
`0xYZZ` (Y = animation number, ZZ = blend frames). No such binary exists in
any decoded dataNNN file checked so far. Remaining unexamined sources, in
order of promise:

1. **Per-character containers data007–data017, data025, data027,
   data034–data047** — the repo decode doc's own remainder list calls these
   the "per-character model/animation container mapping" targets; 33/42
   dataNNN files were never pulled. Pull + section-decode these next.
2. **The X360 executable** (default.xex in the ISO) — the MOTA loader /
   moveset tables may be static data there; Ghidra route.
3. **RPCS3/live-memory motbin extraction** (Kiloutre's native route) —
   needs the game running; produces anim_addr directly per move.

## Verdict

Exhaustive negative for data001 and for every locally decoded container
(000/001/002/004/018/052): the per-move → MOTA-index join is **not in the
dataNNN containers examined**. Next step = pull + decode the
per-character containers (data007–017 etc.) OR extract the join from the
executable / live memory. Do NOT substitute another character's motion or
guess indices meanwhile.
