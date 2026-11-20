# Arena drafts — 2026-10-22

**What this is:** every playable Western Heart arena EXACTLY as it was before the
arena upgrade pipeline began. This is the revertible baseline the owner asked for:
"save every current arena EXACTLY as it is right now — these become 'arena drafts.'"

**Source:** `mhvnsnt/western-heart` @ main `92bf1f77` (2026-10-22). The draft of
`game/js/stages.js` was verified byte-identical to main (git blob
`6497507d280daa3cfb8d20109e0353725971d09d`) before snapshotting.

## Contents (148 files, ~24 MB)

| Folder | Source in repo | What it holds |
|---|---|---|
| `code/stages.js` | `game/js/stages.js` | The full stage registry + all builders (the arena definitions and their procedural blockout geometry) |
| `assets/` | `game/assets/stages/` | All stage assets: T3 panorama OBJs + texture atlases, No Mercy OBJs/GLBs, Eastern Mind panos, thumbnails |
| `prototype-stages/` | `prototype/stages/` | Original stage concept JSONs (shrine, tong-nou, tree-of-life, plains-of-chi-u, octagonal-shrine, helix-palace, palace-of-dreaming, phantom-marketplace, t3-retro-manifest) |
| `docs-arenas/` | `docs/arenas/` | Arena research docs as they stood (t3-texture-pipeline, RESEARCH.md) |
| `manifest.json` | — | SHA-256 hash of every file above — the proof of "exactly as it was" |

**Not included (by design):** `teardown/` sources — those are the *inputs* to the
upgrade pipeline, versioned separately and never modified by it.

## How to verify

```bash
cd arenas/drafts/2026-10-22
python3 -c "
import hashlib, json
m = json.load(open('manifest.json'))
bad = [f['path'] for f in m['files']
       if hashlib.sha256(open(f['path'],'rb').read()).hexdigest() != f['sha256']]
print('MISMATCH:', bad if bad else 'none — draft intact')
"
```

## How to revert one arena

The builders all live in `code/stages.js`. To restore a single arena's pre-upgrade
builder, copy its builder function from the draft back into `game/js/stages.js`
(the draft `stages.js` is the approved blockout). To revert everything, check out
the commit that introduced this folder.

## Pipeline

Upgrades follow `docs/arenas/ARENA-UPGRADE-PIPELINE.md`. Each arena moves through
concept → blockout (this draft) → detail → materials → lighting → polish, with
owner handoffs at every stage.
