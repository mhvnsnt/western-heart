# Semantic motion retargeting (`tools/anim-retarget/`)

WH-native implementation of the **semantic joint alignment** core of
[SATA — "Semantic-Aware Motion Encoding for Topology-Agnostic Character
Animation"](https://arxiv.org/abs/2605.27055) (Zhang et al., arXiv:2605.27055,
May 2026, ICML 2026; official code Apache-2.0 at
https://github.com/zzysteve/SATA).

## What problem this solves

`game/js/t3anims.js` `retargetT3Clips()` maps Tekken animation bones to a
fighter's rig **by bone name** against a hardcoded canonical list
(`['Hips','Chest','Head','LeftShoulder',...]`). Any WH character whose rig
doesn't use those exact names and topology — creatures, extra limbs
(Chatur's four arms), different proportions — needs manual rig mapping.
This tool removes that bottleneck: give it a Tekken clip and ANY target
rig, and it aligns joints by **functional semantics**, never names.

## How it works (paper Sec. 3.1–3.3, analysis mode)

1. **Topology-agnostic graphs** (`graph_rep.py`, paper Sec. 3.1): each rig
   becomes a graph with static features
   `F_s = (X_g` global offset, `X_l` parent-relative rest,
   `X_t` semantic tags) plus depth / reverse-depth edge features.
2. **Semantic tags** (`semantic_tags.py`, paper Sec. 3.2 / Table 11):
   every joint gets a taxonomic-neutral functional description
   ("the pelvis and hip root anchor", "the left upper arm bone"),
   embedded with deterministic TF-IDF (offline stand-in for the paper's
   frozen T5 encoder; `SEMRET_EMBED=hf` selects a sentence-transformer
   backend when closer parity is wanted).
3. **Semantic-spatial correspondence** (paper Sec. 3.2, eq. 1–3): per
   target joint, softmax over source joints of
   `0.65·cos(semantic) + 0.35·cos(structure)`. The structural vector is
   deliberately **direction-free** (bone-length proportions, depth,
   branching, subtree size) — a creature's "shoulder" can point down
   while a human's points up, so rest-pose directions are not a valid
   cross-species cue.
4. **Motion transfer** (`semantic_retarget.py`, paper Sec. 3.3): the
   matched source joint's local rotation transfers verbatim (hard top-1
   semantic mapping); root translation scales by leg-length ratio
   (decoder conditioned on target rest-pose geometry `{X'_t,X'_g,X'_l}`).
   Target joints with no confident counterpart (weight < 0.40) **hold
   rest pose** — the paper's zero-shot behavior for novel limbs
   (a tail stays neutral instead of inheriting wrong motion).
5. **Validation**: FK bone-length preservation + character-normalized
   retarget error (paper App. D.2, eq. 4 / SAN).

## Documented deviations from the paper

The paper trains a spatio-temporal interleaved graph VAE on 80k human +
30k animal sequences. This tool implements the *semantic joint alignment*
core in **training-free analysis mode** (numpy only, no torch, no
checkpoints): the learned FiLM projections become an explicit
correspondence computation, and the learned decoder becomes direct
rotation transfer + geometric root scaling. The alignment *mechanism* —
functional correspondence from semantic tags plus spatial structure,
no canonical joint set, no source-target pairs, no hand-crafted maps —
is fully preserved. A checkpoint-backed SATA VAE backend can be added
later; see `docs/research/SEMANTIC-RETARGET-2026-10-23.md`.

## Usage

```bash
python3 tools/anim-retarget/semantic_retarget.py \
  --src-clip game/assets/anim/t3/paul/t3_light.json \
  --src-skel game/assets/anim/t3/paul/skeleton.json \
  --tgt-skel game/assets/anim/t3/gon/skeleton.json \
  --out /tmp/gon_t3_light.json \
  --map-report /tmp/gon_t3_light.map.json \
  --bank gon --slot t3_light_retarget
```

Output is a `wh-anim/1` clip JSON loadable by `game/js/t3anims.js`
`jsonToClip()` (bones / rot_xyzw / root_t), plus a map report showing
every target joint's source match, confidence, and validation metrics.
`--map-report` is the inspectable proof that no manual mapping was used.

## Tests

```bash
python3 tools/anim-retarget/tests/test_semantic_retarget.py
```

Real-data tests (no fixtures, no mocks):

| test | what it proves |
|---|---|
| `identity` (Paul→Paul) | 22/22 identity map, bit-exact rotation transfer, E=0 |
| `paul->gon` (punch→creature) | 18/18 functional maps, exact transfer, leg-ratio 0.205 |
| `name-invariance` | synonym-renamed rig maps identically — alignment is semantic, not name-based |
| `extra-limbs` | 4-arm + tail rig: 18 core mapped, 16 extra arm joints inherit counterpart motion, tail holds rest |
| `reduced-rig` | missing joints still retarget cleanly |

## Wiring into the pipeline

Today `retargetT3Clips()` runs at load time in the browser, name-based.
This tool is the **offline intake path**: run it per bank/slot to bake
`wh-anim/1` clips for non-standard rigs, then register the bank in
`T3_BANKS`/`SOURCE_TO_BANK` as usual. It does not change any runtime
code path until a crew wires its output into a bank.

## License note

Paper/code: Zhang et al., Apache-2.0 (verified on the GitHub repo).
This WH-native reimplementation is original code following the paper's
published methodology; no SATA source files are vendored.
