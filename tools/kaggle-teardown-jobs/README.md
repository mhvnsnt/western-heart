# Kaggle teardown jobs — GPU + CPU batch work for teardown files

Parent-browser jobs: these scripts run in the Kaggle GPU notebook
(https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit, 2x T4).
Subagents cannot run the browser; the parent runs these cells and commits
the outputs to the repo. Close the Kaggle session when idle (quota counts
while open).

## The honesty rule for this directory

GPU is used where it genuinely helps (vectorized batch math, ML
inference, upscaling). Where CPU is the right tool, the script says so
and never reports itself as GPU-accelerated. A small file does not
become a GPU job by being uploaded to Kaggle.

## Job index — every teardown group mapped

| Teardown group | Job | Why |
|---|---|---|
| T7 mot.bin decode (51 bins) | CPU sufficient — DONE | Converter runs seconds/file, I/O-bound. 51/51 decoded on CPU. No GPU job exists or is needed. Output: 51 JSONs + GRE PR #63. |
| T7 .mvl display lists | CPU sufficient — DONE | Small parse. Titles + demo inputs decoded. |
| T7 frame data (TheBigTuna) | CPU sufficient — DONE | JSON conversion. MOD damage wired (PRs #1000/#1002). |
| T7 pakchunk0 | BLOCKED on enumeration | manifest.json + models/ + textures/ exist; animation/MOTA entries unconfirmed. Read the manifest (CPU) before any batch job. Model conversion later = gltfpack, CPU-parallel (studio lane). |
| T3 banks (22) | JOB 02 (this dir) | Batch root-trajectory classification across all banks, torch CUDA vectorization when present. One bank alone is CPU-trivial; the GPU value is the all-bank batch. |
| T3 reactions | CPU sufficient — DONE | Already baked (reactions.pack.json). |
| T5 motion | BLOCKED — no bytes | gym_*.dat names cataloged, files absent. No job until bytes are located. |
| T6 IDX | CPU sufficient — BLOCKED on semantics | 26 KB file, 2 candidate keysets. This is NOT a brute-force problem; GPU brute-force would be theater. Blocker = tiling/sortedness mapping semantics. |
| TTT2 13 hash files | BLOCKED on identification | CPU header/content matching. No GPU job until Jun is identified. |
| WWE No Mercy / WMXIX | CPU sufficient — DONE/PARTIAL | Already decoded. WMXIX per-clip identity = analysis work, CPU. |
| WWE 2K19/20/22 | BLOCKED | 2K19 extracted dir unlisted; 2K20/2K22 = README stubs. Enumerate before any job. |
| VF5 | BLOCKED — nothing extracted | No files, no job. |
| DOA | BLOCKED — script only | doa4 = download script, no game files. |
| Gang Beasts dump | JOB 01 (this dir) | CPU-parallel mining + OPTIONAL GPU semantic search (--embed, sentence-transformers). Regex mining itself is never GPU-accelerated; the README and verification file say so. |
| Fire Pro / Wrestling Empire decompiled | JOB 01 pattern (CPU) | Reuse job 01 with a different keyword list (wrestling-system terms). CPU-parallel text mining. |
| Yakuza extracted | CPU — enumerate first | extracted/ + raw-small/ unlisted. List contents, then mine like job 01. |
| Eastern Mind stages/audio | CPU | Docs + stage dirs. Audio handled by the music lane. |
| UI / menu / frontend | CPU — measurement, not compute | Layout rules measured from T7/T8 docs + TIM textures. No GPU job: UI extraction is measurement + CSS, not batch math. See manifest section 16. |
| Model optimization (all GLBs) | CPU-parallel — studio lane | gltfpack batch (proven: -54% to -65% on WH files). GPU does not accelerate gltfpack. |
| Texture upscaling | GPU — studio lane | Real-ESRGAN on Kaggle (weights ~64 MB + ~18 MB). Real GPU job. |
| Rig/retarget (UniRig) | GPU — studio lane | UniRig skeleton + skin inference on Kaggle T4. Real GPU job. |
| Nosferatu track cutting | GPU — music lane | kaggle-cut-tracks.py proves CUDA with a matmul + fails loudly without it. Real GPU job. |
| Steam titles with no teardown | No job until a pull exists | See manifest section 18. A title with no files cannot be GPU-processed. |

## Job 01 — Gang Beasts dump mining

Inputs: upload GRE teardown/gang-beasts/dump.cs, il2cpp.h, script.json,
stringliteral.json as a Kaggle input dataset (150 MB total). No
credentials in the script; it never contacts GitHub.

Run: `python3 01-gang-beasts-dump-mine.py --input-dir /kaggle/input/gang-beasts-dump --out-dir ./gb-out`
Optional GPU semantic search: add `--embed` (needs sentence-transformers
installed in the notebook; without it the keyword job still completes).

Outputs to commit: gb-out/gang-beasts-physics-index.json,
gb-out/gang-beasts-physics-summary.json, gb-out/JOB-VERIFICATION.txt.
Commit target (repo path, docs or data — parent decides at commit time;
do NOT commit the 150 MB dump files themselves to the public repo):
docs/research/ as the mined index, or game/data/ if the ragdoll lane
wants it as data. The dump files stay in the private repo.

## Job 02 — T3 anim batch analysis

Inputs: none to upload — `--download` fetches all 22 bank packs from the
PUBLIC western-heart repo (no auth).

Run: `python3 02-anim-batch-analysis.py --download --out-dir ./anim-out`

Outputs to commit: anim-out/anim-classification.json,
anim-out/anim-classification-summary.json, anim-out/JOB-VERIFICATION.txt.
Commit target: docs/research/ (classification report) + feed the
move-matching system (docs/MOVE-MATCHING-SYSTEM.md) with any row whose
class contradicts its JSON label (starting with king row 38, Pantera's
LP1 — verify whether its ry curve rises and falls like a jump).

## Tested

Both scripts syntax-checked and run on synthetic inputs on CPU:
- Job 02: flat clip -> standing, arc clip (rise 0.4 m) -> jumping,
  drop clip (drop 0.3 m) -> crouching. Backend honestly reported as
  stdlib CPU (torch not installed on the test VM).
- Job 01: mini dump files -> 8 hits across 7 keywords, correct counts,
  GPU note honestly "NONE for regex mining".
Real-bank validation is owed on the first Kaggle run (king bank row 38
must classify jumping if the user report is right).
