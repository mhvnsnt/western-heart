# Broad Blender open-source sweep — 2026-10-24

User directive 2026-10-24 21:35 CDT: pull ANYTHING open source that helps
with 3D Blender work — animation, modeling, accessories, clothes,
closet. Builds on the adopted four (UMA slot structure, MPFB/MakeHuman +
MakeClothes CC0, MustardUI, Cloth Lab GPL). Paid/proprietary tools stay
REFERENCE ONLY, never labeled open source. License firewall is OFF for
pulling (user override) — copyleft is documented, never a block, and
never mislabeled.

## The catalog (whole list, not top picks)

The full table lives in `tools/blender/oss-catalog.json` in this PR
(21 open-source entries + 8 reference-only entries). Summary by lane:

- **Character creators:** MB-Lab (code GPL-3.0 / data AGPL-3.0),
  CharMorph (per-base: Antonia CC-BY, Reom CC-BY, Vitruvian CC0,
  MB-Lab base AGPL), MPFB 2 (code GPL / assets CC0), MakeHuman
  standalone (code AGPL / assets CC0).
- **Rigging:** Rigify (GPL, Blender bundled).
- **Modeling:** Blender built-ins (LoopTools, BoolTool, peers — GPL
  family, per-addon check owed), MACHIN3tools (free collection,
  license + repo URL unresolved — candidate only).
- **Model fix:** Cats Blender Plugin (fork lineage messy, license
  UNVERIFIED — candidate only, do not claim GPL).
- **Animation:** Animation Layers (NLA layers, license + repo
  unresolved — candidate only; check Blender 5.x native layers first).
- **Render farm / GPU pipeline:** Flamenco (GPL-3.0, first choice),
  OpenCue (Apache-2.0, second choice, heavier).
- **In-Blender asset library:** BlenderKit (mixed Royalty-Free/CC0,
  per-asset check mandatory).
- **Asset pools (CC0 first):** Poly Haven (CC0), ambientCG (CC0),
  Kenney (CC0), Quaternius (CC0 + do-not-redistribute-as-assets flag),
  KayKit free packs (CC0), OpenGameArt (varies, CC0 filter),
  Sketchfab (CC0 filter only — CC-BY-NC must never ship),
  BlendSwap (varies, URL unresolved), Poly Pizza/Icosa (mostly CC-BY,
  URL unresolved).

## What counts as "wired" — and what is NOT wired here

Nothing in this PR counts as "in the closet" or "wired into a fighter".
The closet fit rule (closet spec §3) still applies to every entry: a
piece is only in the closet once it is refit to the target rig (Blender
weight/Data Transfer) and renders clean full-body AND part-zoomed.
This PR wires the CATALOG into the repo (`tools/blender/oss-catalog.json`
+ this doc) so the next lane can pull by id without re-researching
licenses or URLs. No addon was installed, no asset was downloaded, no
character was refit in this sweep — any report claiming otherwise
would be false.

## Verification method (no guessed URLs)

- GitHub repos: `git ls-remote <repo>.git HEAD` resolved 2026-10-24
  for MB-Lab, CharMorph, MPFB2, MakeHuman, Blender, Cats fork, and
  BlenderKit. HEAD SHAs are recorded per entry in the JSON.
- Everything else: a URL returned verbatim by web search, or a domain
  stated in search results with NO deep path cited. Entries whose
  primary URL was not returned carry `url: null` and the note
  "resolve before use, do not guess" — that is deliberate, not a gap
  to paper over with a plausible-looking link.
- Licenses are AS STATED by the source. Where a license could not be
  confirmed, the entry says UNVERIFIED. MB-Lab's AGPL data license
  and CharMorph's per-base licenses are the two copyleft/attribution
  traps in this list: Vitruvian (CC0) is the clean CharMorph base;
  MB-Lab bases need an owner decision before shipping as game
  characters.

## GPU packages (for parent browser execution — NOT run here)

No GPU job ran in this sweep. There is no nvidia-smi output, no
torch.cuda output, no render, and no timing to report, so no speedup
is claimed. The packages below are ready for a parent-run GPU session
(Kaggle main, Colab T4 second, local CPU fallback only):

**Package A — closet/scene preview renders (Cycles, headless Blender):**
input = GLB/registry entry + lighting preset (studio/living_room/night)
+ camera take (FreeCamera `saveTake()` JSON from the companion
free-camera PR). Command shape:
`blender -b scene.blend -E CYCLES --cycles-device CUDA -o out/ -f 1`
(OPTIX on RTX). Proof required before any speedup claim: nvidia-smi
output, Blender version + cycles-device log line, resolution +
samples + output PNG size, GPU wall time, CPU-baseline wall time for
the SAME scene (`--cycles-device NONE`), measured speedup = CPU/GPU
only after both exist.

**Package B — retarget batches (base -> WH rig):** input = base export
+ WH bone map + fit-rule checklist. Note honestly: Blender weight
transfer is CPU work; GPU claims apply to the render/preview steps of
the same job, not to the transfer. Proof: bone-map file + refit log +
before/after renders full-body AND part-zoomed, plus nvidia-smi only
where a GPU step was actually used. Do not inflate a render speedup
into a retarget speedup.

## Overlap / sequencing

- This sweep does not duplicate the closet lane's registry work; it
  feeds it (new garment/character sources for registry entries).
- UniRig is a separate existing lane and is NOT counted in the
  adopted four or in this sweep's 21 — it is the retarget baseline
  these new bases would feed into, once the owner approves a base.
- Show-only Blender production (Ep 1 sets/renders) is Claude's lane
  and is not built here; Flamenco/OpenCue are included only as the
  game-preview render pipeline, not as show production.
