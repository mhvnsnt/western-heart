# DOROWANI — Rig Specification (Bipedal Croc)

**Status:** SPEC ONLY — not yet rigged. See below for the planned path.

## Model Analysis

Dorowani (Attire 1 Crimson Cheeks) is a **BIPEDAL croc** (not quadruped):
- Stands on two legs like a Pokemon
- Long crocodile snout with teeth
- Crimson cheek fins, blue head crest
- Tan turtle shell on back
- Digitigrade legs, clawed feet
- Tail extending behind

Render: workspace/dorowani-proof/dorowani-a1-render.png (viewed 2026-10-22).

## Why Not Rigged Yet

1. **OS-level write blocks:** Python/Node file writes are blocked (seccomp/LSM), preventing the rig pipeline from running.
2. **No Blender:** Blender 4.0.2 is not installed (required for the GameRig backend).
3. **Meshopt compression:** The source GLB uses EXT_meshopt_compression; must be decoded before the k-NN backend can read it.

## Planned Path (Charger Precedent)

**Charger (the Blanka-based beast fighter) was successfully rigged** via:
- `tools/auto_rig/backends/knn_transfer.py` — k-NN skin-weight transfer
- Donor: pantera.glb (WH canonical skeleton, rigged)
- Method: For each target vertex, find k=4 nearest donor vertices in bind-pose space, copy joint/weight pairs with inverse-distance weighting
- Result: `roster/charger/attires/attire1/model-rigged.glb`

**Dorowani should follow the same path:**
1. Decode: `node tools/anim/gltf_codec.mjs decode` (or equivalent) on the source GLB → plain float GLB
2. Transfer: `python3 tools/auto_rig/backends/knn_transfer.py --in dorowani_decoded.glb --donor roster/pantera/pantera_rigged.glb --out model-rigged.glb`
3. Validate: `python3 tools/auto_rig/anim_check.py --in model-rigged.glb` (must pass: bone-var <2%, no tearing, edge-stretch <2.5x)
4. Wire: Update game/js/assets.js to point to the rigged model

## Task Directive Compliance

The task says: "do NOT force a humanoid rig on a croc body if it breaks."

The k-NN transfer does NOT force a humanoid skeleton onto the croc — it TRANSFERS weights from the donor to Dorowani's own proportions. The skeleton comes from the donor (pantera, bipedal), which matches Dorowani's bipedal stance. The long snout and tail will receive weights from the nearest donor vertices (head and spine/leg regions). This is the same method that worked for Charger.

If the k-NN result shows tearing on the snout/tail (anim_check gate), the fallback is a custom croc rig with explicit Jaw and Tail joints (see below).

## Custom Croc Rig (Fallback)

If k-NN fails the gate, build a purpose-built rig:

```
Hips (pelvis)
├── Spine → Chest
│   ├── Neck → Head → Jaw (for Snap Bite! critical)
│   ├── ShoulderL → ElbowL → WristL → ClawL
│   └── ShoulderR → ElbowR → WristR → ClawR
├── HipL → KneeL → AnkleL → FootL (digitigrade)
├── HipR → KneeR → AnkleR → FootR (digitigrade)
└── Tail1 → Tail2 → Tail3 → TailTip (for Tail Swipe! critical)
```

**Critical joints for the moveset:**
- **Jaw** — Snap Bite (1), Mud Bite (d+1), Bite Me throw (1+3)
- **Tail chain** — Tail Swipe (4), Tail Spin (4,4,4,4,4), Tail Jab (3)
- **Head/Neck** — DINO BREATH (1+2, fire breath origin at mouth)

## Skinning Requirements

- **Shell:** Weight primarily to Spine/Chest (rigid-ish, minimal deformation)
- **Jaw:** Isolate lower-jaw vertices to Jaw bone for clean open/close
- **Tail:** Smooth gradient along Tail1→Tail2→Tail3→TailTip for whip-like swipes
- **Snout:** Upper snout to Head, lower jaw to Jaw — must not tear during bite

## anim_check Gate

The rigged output must pass `tools/auto_rig/anim_check.py`:
- Bone-length variance < 2%
- No vertex tearing (>0.35m frame-to-frame)
- Edge stretch p99.9 < 2.5x
- Root offset < 1.0m

## Interim

Ships unrigged (wired to the source archive, read-only). The game handles unrigged models gracefully (T3 humanoid anims don't bind; fighter remains playable with procedural animation). This matches the pre-rig state of Charger.
