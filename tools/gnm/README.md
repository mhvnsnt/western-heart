# tools/gnm — GNM (Generative aNthropometric Model) head/face generation

GNM (github.com/google/GNM) is Google Research's parametric model of the
human head: **head, face, neck, eyeballs, teeth, tongue**, built from
high-resolution 3D scans + artist-made anatomy samples. Apache-2.0, publicly
released with the paper (arxiv.org/pdf/2607.23687v2).

## Place in the Western Heart pipeline

```
PARAMETRIC FACE CREATION (this tool)
  GNM samples an identity (gender + ethnicity) and a semantic expression,
  evaluates the real model (17,821-vertex topology, identity/expression
  bases, 4-joint skeleton + LBS weights for pose/gaze)
        |
        v
UNIFIED FACE SYSTEM
  GNM output merges with MB-Lab face morphs behind ONE face panel —
  see docs/CREATION-SUITE-UNIFICATION-MAP.md
        |
        v
WRAP -> RIG -> EXPORT (same as MB-Lab path: tools/mb-lab/README.md)
```

GNM is the **FACE-system parametric source**. The suite already carries
GNM-derived data (customization/face-morphs/MANIFEST.json + FACE_PRESETS /
FACE_PARAMS in customization/create-fighter/js/morphdata.js, via
mhvnsnt/cape-jones 3d-assets/face-rig/ PR #125) — this tool adds the LIVE
model: real GNM evaluation instead of baked tables.

## License — VERIFIED ✅

**Apache-2.0** (github.com/google/GNM LICENSE). Commercial-friendly,
no copyleft on generated heads. GNM ships no appearance model (no skin
texture, no hair) — we add skin via the suite's skin system and hair from
the extracted WWE parts library.

## Blender compatibility

GNM itself is a **Python/numpy model, not a Blender addon** — it runs
anywhere Python runs. `run_gnm_job.py` evaluates the model headlessly and
writes an OBJ/GLB head that the Blender job chain (wrap → rig → export)
consumes. No Blender version constraint. Tested with the pipeline's
Python 3.12 + numpy.

Related browser-native path: huikku's gnm-head-studio
(huikku.github.io/gnm-head-studio) precomputes GNM's linear bases as
vertex deltas (`mesh = neutral + Σ delta`, verified 0.00% error) — the
same math our suite's in-browser face preview uses.

## Fetch-on-demand (DISK RULES)

GNM weights are large — **never committed to git**. The fetch script is
the install:

```bash
bash tools/gnm/fetch-gnm.sh [dest]   # default: tools/gnm/vendor
```

Clones google/GNM at the pinned commit and pulls the released model
assets. Re-running is a no-op when the pinned version is present.

## Headless generation (the wired path)

```bash
python3 tools/gnm/run_gnm_job.py \
  --spec tools/gnm/specs/face-determined.json \
  --out /tmp/gnm-head.glb
```

Or through the suite job queue:

```bash
python3 tools/suite-jobs/run_job.py --spec jobs/gnm-face-01.json
```

Job spec: `{"tool":"gnm","params":{...},"out":"path/to.glb"}` —
see tools/suite-jobs/README.md. The suite's FACE panel submits these jobs
and polls status; no dead buttons.

## Param spec reference

```json
{
  "identity": { "gender": "female", "ethnicity": "east_asian", "seed": 7 },
  "shape": { "head_000": 0.4, "head_007": -0.2 },
  "expression": { "happy": 0.8, "jaw_open": 0.25 },
  "pose": { "head_turn": 0, "head_nod": 0, "gaze_x": 0, "gaze_y": 0 },
  "parts": { "teeth": true, "tongue": false, "eyeballs": true }
}
```

`identity.seed` picks from GNM's sampled identity bank (the "72 people"
approach: gender + ethnicity + seed). `shape` takes raw PCA components
(`head_000…`, honest numbered sliders — see the studio's labeling note).
`expression` takes GNM's semantic VAE categories. Output: rigged head GLB
(4-joint neck/head/eyes skeleton) ready for the wrap stage.
