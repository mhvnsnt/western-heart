# Push records

Receipts from Muse's snapshot-sync pushes into this repo: each
`.muse-github-snapshot-sync.json` records the owner/repo/branch, the source
directory on the agent VM, the commit SHA(s), and the exact file paths each
push landed. The `.paths` files are the plain path lists those pushes were
built from.

These are provenance, not content: they exist so a later sweep can tell what
already landed and where, without guessing. Swept in by the repo sweep
(2026-11-20); the local originals lived at the top of `~/workspace/`.

| File | What it records |
|---|---|
| `vpw2-english-complete-push.muse-github-snapshot-sync.json` | 1 push to `muse/vpw2-english-complete` (commit `adfeae4c`) — the VPW2 English-complete teardown: README + WORKLOG + 10 tools + 16 translation JSONs (28 files). Verified byte-identical 2026-11-20. |
| `vpw2-english-complete-push-paths.txt` | The 28-path list for that push (NUL-separated). |

The matching Bannon receipts live in that repo under the same path
(`docs/sweep/push-records/`).
