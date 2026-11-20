# Krita clean-up step — WH PROOFS ONLY

Scope: proof images only (stills and frames that will be shown for review).
This step does **not** touch fight code, game assets, or any commercial
asset. It does not install, license, or emulate any paid tool.

## Status: docs-only for the Krita GUI step, runnable check script

Krita is a GUI application and is **not installed on this CPU-only VM**
(checked 2026-11-02: no `krita` binary). So the clean-up itself cannot be
run headlessly here, and this document does not pretend otherwise. What
*is* runnable here is the checker, `krita-cleanup-check.py`, which verifies
the exported file and records the operator's attestation. The GUI steps
below are performed by a human operator on a machine with Krita installed,
using only free Krita (krita.org).

Paid tools are **not** part of this flow. Toon Boom Harmony, Adobe
Animate, and the Spine editor are not installed, have no licence in this
repo, and must not be claimed or faked. OpenToonz / Tahoma2D is the free
fallback for 2D animation work; it is not wired in this PR (see README).

## Operator steps (Krita, human, per proof image)

1. Open the proof render (PNG) in Krita. Work on a **copy**; never
   overwrite the raw render. Keep the raw render as the source of truth.
2. Clean up on separate, named layers (e.g. `cleanup`, never destructive
   edits on the background layer): remove stray marks, fix obvious
   artefacts, tidy edges. Do not alter the subject's proportions, pose,
   or identity — this is clean-up, not a redesign.
3. Keep the canvas size unchanged. Do not crop, rescale, or reframe
   unless the proof brief explicitly asks for it; if you do, note it in
   the delivery record.
4. Export a flattened PNG next to the source as
   `<name>-clean.png` (File → Export). Keep the working `.kra` file
   **out of the public repo** (local working files only) unless the
   team explicitly decides otherwise.
5. Run the checker (below). It fails unless you pass `--operator`
   confirming steps 1–4 were done in Krita — that flag is the honest
   record that a GUI step happened, not a machine verification of it.

## Checker

```sh
python3 tools/proofs/krita-cleanup-check.py \
  --source renders/proof.png \
  --cleaned renders/proof-clean.png \
  --operator "your-name" \
  --out proof-clean-check.json
```

The checker verifies, with no third-party deps: both files exist and are
valid PNGs, dimensions match (no silent rescale), the cleaned file is
non-empty, and — if Pillow is available — the cleaned image opens and
its mode is reported. It writes a JSON record; it never modifies images.
Exit 0 = record written, 1 = check failed, 2 = usage error.

## What is NOT covered here (owed, with reasons)

- Automated / headless Krita clean-up: owed — Krita has no supported
  headless clean-up mode relied on here, and it is not installed on
  this VM. A scripted Krita Python plug-in would need a Krita install
  to test against; claiming one untested would be fabrication.
- OpenToonz / Tahoma2D animation step, Synfig step, RIFE interpolation,
  DaVinci Resolve (free) edit: owed — see `tools/proofs/README.md`.
