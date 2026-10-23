# DOA4 Phase 13 — Job 2 CORRECTED: the definition layer EXISTS — inside anm.afs (the container nobody opened)

**This doc supersedes `phase13/ANM-DEFINITION.md`'s central claim.**
That doc declared the definition files absent from the ISO and ANM
statically exhausted. Its census was complete over every storage it
examined — but it examined the WRONG anm.afs. Within the same
session, extraction of the ISO's actual anm.afs entry (XDVDFS
sector 416009) proved:

## §1 The find

The ISO's `anm.afs` (2,949,120 B, ISO offset 0x42A14800, sha256
`18eed8a09bb37ea6bc83e5572dd648fd55def823ebdcb6994adf8bb3a918b85a`)
is a **standard CRI AFS container with 26 named entries**:

| # | entry | size | sha256 (head) |
|---|---|---|---|
| 0 | anm_version.bin | 16 | cc5f6bb5ea2a5926 |
| 1–24 | zack, tina, janlee, karate, ryu, kasumi, genfu, hika, bayman, bass, hakyo, ninja, leifang, ayane, boy, lisa, alpha, tengu, spartan, suiken, gokei, koryu, rtm, sambo (.bin) | 61,844–145,504 | see manifest |
| 25 | **anime_cm.bin** | 177,580 | 8d85206c26fac24c |

Full per-file sha256 + AFS offsets: `phase13/definition-manifest.json`.
The files are released as `doa4-anime-definition-20261022`
(assets: `anm.afs` the container + `definition.tar` the 26
entries; both digests verified against the GitHub API).
Container round-trip: the extracted entries are byte-identical to
their container spans (gate-1 structural proof for the container
layer — `phase13/tools/definition_census_p13.py`).

**Why thirteen phases missed it:** every phase after phase 1
studied a 2,949,120-byte file (head `c1ff2852…`, the 27,392×16 B
records) that the phase-1 extraction had labeled `anm.afs` and
that the mirrors faithfully propagated. That file is NOT this
ISO's anm.afs — its head pattern does not occur in the assembled
ISO's landed first 1 GB, nor in avt/cmn; its provenance is the
project's earlier source image (a different pressing's animation
data is the standing hypothesis; it remains a real, censused
animation-data file whose records the phases 7–12 work describes
accurately — under a wrong name). The loader's `anm%d.afs`
enumeration (phase 11) fits: the game opens anm.afs the container
and its siblings by index; the definition entries inside the
container are what phases 11–12's residual always pointed at.

## §2 What the definition files contain (census)

Tool: `phase13/tools/definition_census_p13.py`; data: scratch
`p13/definition_census.json` + `p13/bin_headers.txt`.

- **Per-fighter `.bin`** (24 files): a 136-byte BE header of 34
  u32s, then data sections. Header word 0 is always 136 (the
  header size); words 1–3 are large section magnitudes
  (18,080–35,208 / 4,992–8,560 / 11,904–21,424); later words form
  near-duplicate clusters (e.g. zack w24–w29 ≈ 139,956 / 30,812 /
  30,816 / 140,040 / 30,832 / 30,820 against a 140,044-byte file —
  section offsets/sizes in mixed units). Section probes (zack):
  at +136 a u16 index table; at word-2 offset, BE f32 keyframe
  values with 0xFFFFFFFF separators; at word-3 offset, s16
  timing/index pairs (`00a2 00a6…`); further sections hold float
  curve pairs (0.9 / 1.1 constants) and ascending s16 ramps. File
  entropies 4.15–5.53 — structured animation definitions WITH
  their curve data, self-contained per fighter.
- **anime_cm.bin** (the common table): header (0, 3592, 0…, 3744
  at +0x20, 0…); byte-equality 0.813 at lag 16 — a **16-byte
  record grid** in the body, whose records carry small id fields
  (0x2210 / 0x221F / 0x2220 / 0x2223… series) and parameter words —
  the shared motion/clip index the per-fighter files hang off.
- **anm_version.bin**: 16 B, version u32 = 1.

## §3 Verdict — route OPEN, decode is the next lane (honest gates)

- G2 (census): **landed** — container, headers, sections, strides.
- G3 (parser + clips): **NOT claimed.** The mapping the job asked
  to derive lives in these files' section semantics (34-word
  headers + the anime_cm record table + per-fighter curve
  sections). That decode — section identification, clip framing,
  joint/track assignment, then the gate-2 posed render on a
  phase-6 skeleton — is a full RE lane of its own and is NOT
  honestly compressible into this lane's remainder; no layout is
  guessed and no clip is shipped on spec.
- The phase 8–12 XEX-side negatives STAND (the record consumer is
  not in the loader/translator family — those reads were of this
  game's code and remain correct). What dies is only the
  inference "therefore the mapping is nowhere": it was in the
  one container nobody had opened since phase 1 mislabeled its
  neighbour.

**Exact next steps for the ANM decode lane (named):** (1) decode
the 34-word fighter header (section table) against the section
probes; (2) decode anime_cm's 16 B records (id series ↔ fighter
clip tables); (3) identify which data file the definitions index
(their own curve sections vs mot.afs vs the c1ff file — test by
offset bounds); (4) gate-1 round-trip a full clip parse; (5)
gate-2 posed render on a phase-6 GLB skeleton.
