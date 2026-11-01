# WWE 2K19 teardown transfer — GRE → western-heart (2026-11-01)

**Owner order (2026-11-01):** the WWE 2K19 teardown material in mhvnsnt/game-reverse-engineering was pulled
FOR Western Heart — copy everything the game needs from it into mhvnsnt/western-heart, 100%. This supersedes
the earlier repo-landing call that left it in GRE to avoid duplication. GRE keeps its copy; this was a copy,
nothing was deleted or moved out of GRE.

## What was transferred

Source: `mhvnsnt/game-reverse-engineering` `teardown/wwe2k19/` @ GRE main 05578ee8.
Target: `teardown/wwe2k19/` in this repo (mirror path). **1,677 files, 753,921,882 bytes, additions only.**

| Subtree | Files | Bytes | Contents |
|---|---|---|---|
| (top level) | 4 | 200,900 | FILES-SHA256.txt, SOURCE-SHA256.txt, PULL.md, batch1.txt (pull manifests) |
| extracted/ch/ | 32 | 69,553,058 | Character packages ch10002 + ch10102, incl. the Yuke .yobj models |
| extracted/edit/ | 641 | 661,723,220 | CAW edit-mode parts: edit/ch (607), fullbody_type (28), body (2), hair (2), head (2) |
| extracted/ingame/ | 1,000 | 22,444,704 | Motion data (ingame/motion) |

File types: 1,059 .bin, 597 .dds (textures), 6 .yobj (models), 5 .cnpc, 5 .cnct, 1 .onet, plus the 4 text manifests.

Other GRE locations checked for 2K19 material: `teardown/` contains no other WWE folder; GRE root
`wrestling-games/` holds acquisition/catalog documents only (WWE2K-TERABOX-SPEC.md, WWE2K15-23-ACQUISITION.md,
DLC catalogs) — planning docs, not game data, not transferred; `wwe-wrestlemania-xix/` is a different game.

## Target pre-state and conflicts

western-heart's `teardown/wwe2k19/` previously held only a README.md. It does not collide with any GRE path
and was left untouched. **Conflicts: none. Overwrites: none. Deletions: none.**

## Method

Every file was compared by git blob SHA against the GRE source tree before landing and the whole subtree was
re-audited on main after merging (see Verification). Files up to ~13 MB came down through the GitHub blob API;
the 34 largest files (up to 23.4 MB) truncate mid-transfer through this network on every bulk channel, and
were pulled from raw.githubusercontent.com with curl resume until size + blob SHA matched — the route this
house already proved on the 18.9 MB Negativo refit.

## PRs

| PR | Contents | Merge commit |
|---|---|---|
| #1480 | Manifests + extracted/ch + extracted/ingame (1,036 files) | 728e41ab |
| #1481 | extracted/edit/ch (607 files) | 5eb2db67 |
| #1483 | extracted/edit body + fullbody_type + hair + head (34 files) | 82f929aa |
| (this doc's PR) | this handoff | — |

All merged with full CI green, instruction-gate format, gitleaks clean.

## Verification (post-merge, on main)

Full recursive tree diff of `teardown/wwe2k19/` on western-heart main vs the GRE source tree:
**1,678 files present (1,677 transferred + the pre-existing README.md), 0 missing, 0 blob-SHA mismatches.**
Spot-check record (12 files across every subtree — all MATCH): both ch .yobj models
(83b20b782bbb…, b57d44b6f9f4…), edit/body body_10000 (1f26c87076d6…), fullbody_type_00034 (57e0b498ea5c…),
FILES-SHA256.txt (d4a422108daf…), PULL.md (661454b2a374…), three .dds textures under edit/ch/48202,
three ingame/motion bins.

## What the creation suite can now use

- The 6 Yuke .yobj character models and their .bin geometry/texture payloads (extracted/ch) — raw material for
  WWE-style base bodies and parts.
- The CAW edit-mode part library: 607 part files under extracted/edit/ch, 28 full-body types, body/hair/head
  parts — the part tables the CAW-style creation flow is modeled on.
- 597 DDS textures.
- 1,000 motion files under extracted/ingame/motion.
- The pull manifests (FILES-SHA256.txt / SOURCE-SHA256.txt) as the provenance record for the set.

## Known follow-on

**YOBJ-to-glTF conversion is still pending.** The models landed in their raw Yuke formats (.yobj + .bin),
exactly as they sit in GRE; no converter was landed in this transfer. Converting them is the next step before
the suite can load the meshes directly.
