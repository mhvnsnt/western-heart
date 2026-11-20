# Lane F CPU baselines — measured 2026-10-24 on the local VM (no GPU)

Local GPU state: `nvidia-smi` command not found; `torch` not installed.
GPU-mode scripts exit 2 with a FATAL message on this VM (verified) — no
silent CPU fallback. GPU walls + speedups come from the coordinator's Kaggle
T4 runs of the same scripts; they are PENDING, not estimated here.

| Job | Input | CPU wall | Notes |
|---|---|---|---|
| VF5 offset-table parse + segment stats | `mot_DUR.bin` 8,078,704 B | 0.187 s | 2,648 table entries, 661 records |
| VF5 segC directory parse (all records) | same | 0.151 s | 652 directory + 9 float-led |
| VF5 full job (`vf5_decode_batch.py --mode cpu`) | same | 1.237 s | Incl. JSON output write |
| WWE corpus classify (`wwe_parse_batch.py --mode cpu`) | 157 moveset JSONs, 56,269 moves | 4.390 s | Earlier equivalent run 3.906 s; attire-ID checks 3/3 pass |
| WWE corpus classify (Node equivalent, earlier run) | same corpus | 3.906 s | Category counts: standing 1,297; tekken_striking 45,369; ground 5,542; grappling 3,956; turnbuckle 105 |
| Morph grid (`suite_morph_batch.py --mode cpu`) | 4 templates x 62 dials x 5 values = 1,240 | 1.067 s | Incl. interpreter + numpy import |
| Editor test (Node, `movelist-editor.js`) | 2K22-structured fixture, 6 moves | 42.0 ms | listAllMoves 6 rows; swapMove blocks limb mismatch; save payload OK |

Speedup formula (coordinator fills in): speedup = CPU wall / Kaggle GPU wall.
No speedup is reported in this lane until both walls exist.
