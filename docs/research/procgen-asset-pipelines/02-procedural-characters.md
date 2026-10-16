# 02 — Procedural Characters (2026 research)

**Date:** 2026-10-16 · **Scope:** parametric humanoid generators, MakeHuman/MB-Lab state 2026,
actually-open MetaHuman alternatives.

## What we found

### MakeHuman (makehumancommunity/makehuman) — DOCUMENTED, not pulled
- Community edition **1.2.0 alpha 1** in testing; **MakeHuman 2** at alpha III
  (srasgod/makehuman2, pushed Sept 2026) adds PBR shading and **glTF export**.
- License (verified from repo LICENSE.md via GitHub API): **code = AGPL-3.0**,
  assets = separate license, **output from MakeHuman is NOT AGPL-encumbered**
  (section D of their LICENSE.md). The copyleft binds the program, not characters you make.
- Verdict: safe to *use* as a base-mesh generator for WH roster prototyping; do not fork
  the codebase into the repo without legal review of AGPL. Models export to Blender/glTF
  and enter our pipeline as ordinary assets.

### MB-Lab (animate1978/MB-Lab) — DOCUMENTED, not pulled (archived)
- Blender 4.x parametric humanoid lab, 470+ morphs, FACS facial rig, GPL-3.0 code
  (verified `license.txt` via GitHub API).
- **Repo archived; last push 2024-07-21.** All forks are stale mirrors (0–1 stars, 2026).
  It likely still installs on Blender 4.x but has no maintainer. Use at own risk for
  prototyping; do not build the pipeline on it.
- Commercial alternative that appeared 2026: **Avatar Creator (avcsuite.com)** — morphs,
  MetaHuman/Genesis 9 conversion — but it is **paid/commercial, not open**. Excluded from
  pull per license honesty (documented, not pulled).

### Actually-open MetaHuman alternatives: the honest answer
- There is **no maintained open-source MetaHuman equivalent** in 2026. The open options are
  MakeHuman (AGPL, alive), MB-Lab (GPL, archived), and HumGen3D (code GPL-3.0 on GitHub,
  **3D assets paid via BlenderMarket** — mixed model, excluded from pull).
- WH position: our roster comes from **teardown reverse-engineering + parametric tooling we
  write ourselves** (steal-like-an-artist: study, never copy). Parametric *body-shape*
  variation for crowd/NPC fighters is the gap MB-Lab/MakeHuman could fill; for hero
  fighters the teardown base meshes remain canonical.
- Watch item: **OpenUSD v26.03 experimental character rigging extensions** — if USD rigging
  standardizes, a future open parametric-human-on-USD project becomes plausible. Revisit 2027.

## Wire-up
- No code pull this round (both candidates are copyleft/archived — wrong foundation for the
  hero pipeline). Decision documented here per RESEARCH-TO-REPO law.
- Follow-up thread for idle queue: prototype MakeHuman 1.2.0a1 → glTF → WH rig for one
  background NPC body type; evaluate before any pipeline commitment.
