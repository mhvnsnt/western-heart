# 2026-10-22 — Suite round trip: tweak-kit fix panel + wh-tweak-patch v1

Lane: DoggByte 99fca62a. Owner: "ROUND-TRIP SPEC NAILED DOWN — TOP suite priority. ONE export button, ONE patch format, documented in suite docs."

## What was built

**Suite side** (PR #522, merged as bc5d0188):
- `game/js/fix-panel.js` — loads a crew-staged tweak kit
  (`customization/tweak-kits/<kit-id>.json`), resolves the 8 part groups
  (`head`, `torso`, `upper_arms`, `forearms`, `hands`, `thighs`, `shins`, `feet`)
  to bone targets via the kit's `part_map` (Mixamo-style defaults; bones are wrapped
  in identity groups so the live preview survives animation; mesh fallback for
  multi-mesh fighters). Per-group rotate/flip/offset/scale controls, and the ONE
  "EXPORT TWEAK PATCH" button downloading a `wh-tweak-patch` v1 JSON.
- `game/customization-harness.html` — `?tweak=<kit-id>` mounts the panel (no-op without it).
- `customization/TWEAK-PATCH-SPEC.md` — the ONE patch format: self-describing, versioned,
  validatable.
- `customization/tweak-kits/` — kit dir + README. Staged
  `customization/tweak-kits/julia-parts-fix-1.json` (nightwolf = Julia's body; flagged
  parts are proof placeholders — the parts-audit lane's real finding was a whole-model
  facing error, fixed via `model-facing.json`, not per-part flips).

**Crew side** (PR #524, merged as 03314dc3):
- `tools/customization/import_tweak_patch.py` — strict validator (bad format/version,
  unknown fighter/kit, kit/fighter mismatch, empty changes, unknown part group, duplicate
  group, non-finite or out-of-range numbers — ANY failure rejects the whole patch with a
  clear error and writes nothing) + applier (merges into the kit's `adjustments`, bumps
  kit version, appends history, writes a canonical applied record under
  `customization/tweak-kits/<fighter>/applied/`). `--check` validates only; `--pr`
  pushes and opens a PR.
- `tools/customization/tests/test_import_tweak_patch.py` — 18 tests, all pass.
- `tools/customization/README.md` — usage docs.

## The round trip (user flow)

1. Crew stages a tweak kit → goes live with the Pages build.
2. User opens `game/customization-harness.html?tweak=<kit-id>&p1=<fighter>&demo=1` live,
   tweaks parts with the fix panel, hits EXPORT TWEAK PATCH → JSON downloads.
3. User sends the file back in chat → coordinator runs
   `tools/customization/import_tweak_patch.py <patch> --pr` → validated + applied + PR.
4. The kit's `adjustments` now hold the user's values, so the next round starts from latest.

## Proof

- Node logic tests for fix-panel (part-group resolution incl. Hips-root exclusion and mesh
  fallback, bone wrapping, adjust math, patch build/export shape) — ALL PASS.
- 18/18 importer unit tests pass (valid apply + every malformed shape rejected).
- Mechanical round trip: panel `buildPatch` output accepted by importer `--check` against
  the real repo (`PATCH VALID: fighter=nightwolf kit=julia-parts-fix-1 changes=2 (head, hands)`).
- Harness inline module `node --check` OK. Gitleaks clean.
- CI green on both PRs (instruction-gate / deletion-guard / guard). Merged via
  `git_merge.py` (real 3-way merges through the Git Database API).
- Live (post-Pages-build):
  https://mhvnsnt.github.io/western-heart/game/customization-harness.html?tweak=julia-parts-fix-1&p1=nightwolf&demo=1

## Still open

- Live-browser pass (subagent has no live browser — needs parent/delegation): open the URL,
  screenshot the panel, drag a part, hit EXPORT, screenshot the download, feed the file to
  the importer `--pr`.
- When the parts-audit lane's real per-fighter findings land, stage real kits (the
  `julia-parts-fix-1` flagged parts are placeholders).
- Note: this log lives here instead of WORKLOG.md because WORKLOG.md is a contention
  hotspot (every lane appends; PR #532 kept conflicting). Same substance.
