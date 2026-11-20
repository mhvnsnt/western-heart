# WWE 2K18/2K19 Full-Game Transfer Plan — 2026-10-19

**Owner order:** "Pull them, find the roms/isos" + "Not to local disk tho."
**Constraint:** 51GB + 45GB must NEVER stage on local disk. TeraBox browser lane is the
only working upload path (custom.terabox connector: no API uploader, ≤225MB per browser task).

## Sources (verified live 2026-10-19)

| Pri | Game | Size | Archive.org ID | File | Direct URL |
|-----|------|------|---------------|------|-----------|
| 1 | WWE 2K19 (Clean Steam Files) | 50.96 GB | `WWE_2K19_CSF` | `WWE 2K19 [Build 3467910].7z` | `https://archive.org/download/WWE_2K19_CSF/WWE%202K19%20%5BBuild%203467910%5D.7z` |
| 2 | WWE 2K18 | 45.11 GB | `wwe-2k18` | `WWE 2K18/WWE 2K18.7z` | `https://archive.org/download/wwe-2k18/WWE%202K18/WWE%202K18.7z` |

PC versions (unencrypted, best for teardown). Already on TeraBox: nothing (31.7GB used of 5TB).

## The math (honest)

- Browser lane limit: ≤225MB per task (connector-verified).
- 2K19: 50,956 MB ÷ 225 MB ≈ **227 tasks**. 2K18: 45,113 MB ÷ 225 MB ≈ **201 tasks**.
- **Total: ~428 browser tasks** for both games.
- This is a multi-day background lane, NOT a single task. Do not attempt interactively.

## Recommended execution (for parent/main agent)

**Phase 1 — GitHub → TeraBox (fast, do first):**
The 343MB of animation packs already transfer cleanly via release-to-TeraBox:
- `wwe2k19-moves-pack.tar.gz` (123MB), `wwe2k19-entrance-pack.tar.gz` (175MB),
  `WWE.2K14.DLCS.zip` (45MB) → TeraBox `/CN-Gigaleak/wwe2k/` (match casing).
- Per GITHUB-TO-TERABOX TRANSFER RULE: download from release straight into the
  browser upload, transient pipe only, nothing staged.

**Phase 2 — Archive.org → TeraBox (the big ones):**
Option A (recommended): dedicated transfer lane running browser tasks in the background,
~225MB chunks, verifying each chunk in the TeraBox listing before proceeding.
Split the 7z files into 225MB parts at the SOURCE side is impossible (Archive.org serves
whole files) — instead the browser downloads ranges... in practice: one browser task
downloads the full 7z via Archive.org's HTTP (resumable) and uploads to TeraBox in the
same session is NOT possible (browser can't hold 51GB).

Option B (practical): **chunked via a cloud intermediary.** Kaggle/Colab (owner has both):
1. Download 7z from Archive.org to Kaggle/Colab (fast, free).
2. Split into 200MB parts (`split -b 200M`).
3. Browser lane uploads parts to TeraBox (each task ≤225MB).
4. Reassemble manifest on TeraBox side (document part order).

**Phase 3 — Selective extraction (what we actually need):**
Once the 7z lands on TeraBox, we do NOT need all 51GB locally. Priority extracts:
- `pac/edit/` (CAW parts — the actual goal)
- `pac/profile/` (CAW metadata)
- Game executable (for Ghidra+MCP: .pac loader, moveset engine)

## What the teardown needs (priority order)

1. `pac/edit/bbtemplate.pac` — base bodies + morph targets
2. `pac/edit/edit.pac` — full part library
3. `pac/edit/default.pac`, `sample.pac`, `ch/`, `body/`
4. `pac/profile/profile_dat.pac` — CAW metadata
5. Game .exe — Ghidra RE of the .pac loader + moveset engine

## Blockers / decisions for the owner

- The 428-task transfer is real. Recommend approving a dedicated background transfer lane.
- Alternative: owner pulls the 7z files himself via TeraBox PC client (one-time, fastest).
