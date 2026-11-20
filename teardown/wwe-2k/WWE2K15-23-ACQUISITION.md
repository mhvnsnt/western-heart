# WWE 2K15–2K23 — Acquisition Paths & Priority

Written 2026-10-14 (wh-wwe2k-100 lane). All identifiers re-verified LIVE on Archive.org via metadata API this session.

## Why not downloaded to VM

VM disk: 85% used, 16GB free (2026-10-14). Each game is 33–84GB compressed; extraction needs 2–3x.
**Verdict: no full-game download is feasible on the VM.** Acquisition must go through the
TeraBox browser lane (parent delegation — subagents cannot run browser tasks).

## Priority ranking (CAW / moveset / model value for the wrestling game)

| Pri | Game | Size | Identifier | File on Archive.org |
|-----|------|------|------------|---------------------|
| 1 | WWE 2K19 (Clean Steam Files) | 50.96GB | `WWE_2K19_CSF` | `WWE 2K19 [Build 3467910].7z` |
| 2 | WWE 2K15 (Clean Steam Files) | 33.13GB | `WWE_2K15_CSF` | `WWE_2K15_CSF.7z` |
| 3 | WWE 2K23 | 84.48GB | `wwe-2k23` | `WWE 2K23/WWE 2K23.7z` |
| 4 | WWE 2K18 | 45.11GB | `wwe-2k18` | `WWE 2K18/WWE 2K18.7z` |
| 5 | WWE 2K17 | 50.28GB | `wwe-2k17` | `WWE 2K17/WWE 2K17.7z` |
| 6 | WWE 2K16 | 44.20GB | `wwe-2k16` | `WWE 2K16.7z` |
| 7 | WWE 2K19 (repack) | 49.51GB | `wwe-2k19` | `WWE 2K19/WWE 2K19.7z` |
| 8 | WWE 2K20 (Clean Steam Files) | 53.62GB | `WWE_2K20_CSF` | `WWE_2K20_CSF.7z` |

**Total if all pulled: ~412GB.**

### Rationale
- **2K19 CSF first:** peak of the series, best mod-tool support, most complete CAW suite and
  moveset tables. "Clean Steam Files" = unmodified install, best teardown target.
  (Moves/entrance animation data for 2K15–2K20 is ALREADY secured — see wrestling-game
  release `wwe2k19-animation-packs-v1`. The full game is needed for MODELS, CAW parts, arenas.)
- **2K15 CSF second:** smallest full PC game (33GB); oldest Yukes-engine lineage, closest format
  relative to the already-torn-down WMXIX/SvR2011 PAC structures.
- **2K23 third:** newest roster and highest-fidelity models; largest file (84GB).
- **2K20 last:** widely regarded as the buggiest release; lowest value-per-GB.
- The non-CSF 2K19 repack is redundant if CSF is pulled — listed only as fallback.

## Exact download URLs (verified 2026-10-14)

- 2K19 CSF: `https://archive.org/download/WWE_2K19_CSF/WWE%202K19%20%5BBuild%203467910%5D.7z`
- 2K15 CSF: `https://archive.org/download/WWE_2K15_CSF/WWE_2K15_CSF.7z`
- 2K23: `https://archive.org/download/wwe-2k23/WWE%202K23/WWE%202K23.7z`
- 2K18: `https://archive.org/download/wwe-2k18/WWE%202K18/WWE%202K18.7z`
- 2K17: `https://archive.org/download/wwe-2k17/WWE%202K17/WWE%202K17.7z`
- 2K16: `https://archive.org/download/wwe-2k16/WWE%202K16.7z`
- 2K19 repack: `https://archive.org/download/wwe-2k19/WWE%202K19/WWE%202K19.7z`
- 2K20 CSF: `https://archive.org/download/WWE_2K20_CSF/WWE_2K20_CSF.7z`

Console sidecars (preservation metadata only, not full games):
- 2K14 Xbox 360: `xbox360-xboxkit-945f597ce2820d6adfacbe95`
- 2K15 Xbox 360: `xbox360-xboxkit-85242524ec40ac17f5d53486`
- 2K15 PS3: `ps-3-disc_20260511`

## TeraBox browser-lane spec (for parent delegation)

Per game, in priority order:
1. In the browser (TeraBox session), download the 7z from the URL above to local temp,
   then upload to TeraBox folder `/WesternHeart/teardowns/wwe2k/` (create if missing).
   Verify byte size matches the table before deleting local temp.
2. Do NOT attempt VM download — disk cannot hold these.
3. After TeraBox verify, a future extraction lane (machine with 200GB+ free) does:
   7z extract → Yukes PAC unpack (community PAC tools) →
   `pac/ingame/motion/*` (animations), `pac/menu/*` + model PACs (wrestler models),
   CAW parts, arena files → push extracts to `mhvnsnt/wrestling-game` teardown/ + TeraBox.

## Extraction notes (Yukes PAC, from the already-secured 2K19 packs)

- All `.pac` = Yukes PAC containers (same family as WMXIX — the wrestling-game lane's
  existing PAC tooling applies).
- Wrestler models: per-wrestler PACs (2K19 naming, e.g. entrance PACs carry wrestler names).
- CAW parts: `pac/root/` createmode PACs (seen in moves pack).
- Motion data: `_mpc.pac` + `_param.pac` pairs under `pac/ingame/motion/`.
- Arenas: venue PACs (same pattern as Def Jam's 858 venue files — AKI/Yukes lineage).

## What is already secured (no re-pull needed)

- `wwe-2k19-ported-moves-animations-pack` (121MB, 34 motion PACs, 2K15–2K20 moves)
- `wwe-2k19-ported-entrance-victory-motions-pack` (567MB, 445 entrance motions + 54 gimmicks + props)
- Both in wrestling-game repo `teardown/wwe-2k19-animation-packs/` (docs) + GitHub release
  `wwe2k19-animation-packs-v1` (tar.gz assets). PR #1 merged.
- WWE 2K14 DLCs (44MB, `wwe-2-k-14-dlcs`) — pulled 2026-10-14, extraction in progress.
