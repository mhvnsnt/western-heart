# Tripo auto-intake — rig new Tripo statics ASAP to their character rig

Owner directive (2026-10-21, verbatim): *"As soon as a Tripo model comes in you
need to get it rigged automatically ASAP to the character rig that it goes to."*
No more unrigged statues sitting unprocessed.

## Quick start

```bash
# 1. drop the new Tripo GLB in the inbox, named for its fighter + attire slot
cp new-tripo.glb tools/tripo-intake/inbox/kinpo/attire3.glb
#    (optional sidecar: tools/tripo-intake/inbox/kinpo/attire3.json)

# 2. run the intake
python3 tools/tripo-intake/intake.py --scan
```

That's it. The intake decodes the model, determines which way it faces (with a
confidence gate — it REFUSES rather than guess), rigs it with the proven
`tools/auto_rig/rig_tripo_static.py` pipeline, checks the validate + anim_check
gates, and stages the result at
`roster/<fighter>/attires/attire<N>/model-rigged.glb` with a `WIRING-CHECKLIST.md`
for the reviewer. The inbox original is archived to `outbox/`, never modified.

One-shot form (also the dry-run form):

```bash
python3 tools/tripo-intake/intake.py --in /tmp/new.glb --fighter kinpo --attire 3 \
    --stage-root /tmp/stage --report-root /tmp/reports --dry-run
```

`--dry-run` runs the FULL pipeline (facing, rig, gates, staging) but stages to
`--stage-root` and never touches the inbox, outbox, ledger, or roster tree.

## Inbox convention (read this before dropping a model in)

- Path: `tools/tripo-intake/inbox/<fighter>/attire<N>.glb`
- `<fighter>` is the **roster directory name** (`roster/kinpo` → `kinpo`), and it
  must already exist. The intake **never guesses** which fighter a model belongs
  to: an unknown name is REFUSED with the valid list, not fuzzy-matched.
- `<N>` is the attire slot number, explicit. The intake never auto-picks a slot.
- Optional sidecar `attire<N>.json` (same dir): `{"tripo_uuid": "...",
  "source": "tripo-pull share URL", "notes": "..."}` — provenance, archived
  with the model.
- Only UNRIGGED statics (0 skins). An input that already has skins is refused
  ("wire the existing file instead"). A slot that already holds a
  `model-rigged.glb` is never overwritten — replacements are the owner's call.

## What the intake does, stage by stage

| # | Stage | Tool | Refuse / fail behavior |
|---|-------|------|------------------------|
| 0 | Env check | — | Missing Blender/node/xvfb/node_modules/numpy → clear error, exit 1 |
| 1 | Claim | — | Unknown fighter, clobber risk, or skinned input → REFUSE (exit 2), archived to outbox with a FLAG file |
| 2 | Fingerprint | sha256 | `ledger.json` hit: identical bytes re-decide identically, never re-guessed |
| 3 | Decode | `tools/anim/gltf_codec.mjs` decode | decode error → FAILED (exit 3) |
| 4 | **Facing** | `facing_check.py` (see below) | Low confidence → **REFUSE** (exit 2). `FLAG-FACING-NEEDED.md` in the outbox; a human views rest renders, then re-runs with `--facing <axis>` |
| 5 | Rig | `tools/auto_rig/rig_tripo_static.py` (the proven pipeline: decode → gamerig Blender rig → smooth_weights → validate + anim_check → render_poses → encode) with `--facing <axis>` | pipeline error → FAILED (exit 3) |
| 6 | Gates | `rig_report.json` | `validate.py` (the playable gate: valid glTF, skinned mesh, canonical bones, height 1.5–2.2 m) must PASS or nothing stages → FAILED. `anim_check` flags are RECORDED (even the shipped Zui A1 carries flags on the CMU stress clip) and must be explained by viewing the renders before wiring — flags never silently pass |
| 7 | Stage + checklist | — | `roster/<fighter>/attires/attire<N>/model-rigged.glb` + `WIRING-CHECKLIST.md`; inbox original moved to `outbox/<fighter>/attire<N>/<timestamp>/`; ledger appended |

Exit codes: `0` all done · `2` any item refused · `3` any item failed a gate/step.
In `--scan` mode one bad item never kills the rest; the summary JSON lists all.

## Facing: how it's determined, and the confidence gate

A wrong rotation bakes backwards skin weights (the demonio-a1 case: the old
estimate landed 16° off-axis and bone heat failed for every vertex). The k-NN
backend (`knn_transfer.py --rotate-y`) has no automatic alignment at all. So
the intake determines facing from **two independent geometry cues** on the
decoded mesh, and refuses when they don't strongly agree:

- **cue1 (gamerig math)** — `tools/auto_rig/backends/gamerig_backend.py`
  `normalize_and_face()`: the foot band (bottom 8% of height) vs the shin band
  (18–30%) horizontal centroids. Same computation, re-implemented in plain
  numpy so it runs without Blender. The raw yaw is SNAPPED to the nearest of
  `+X / -X / +Z / -Z`; the raw angle is never trusted directly.
- **cue2 (runtime math)** — `game/js/assets.js` `feetFacingCue()`: the lowest-5%
  band's toe-vs-heel extent asymmetry near each ankle (ankle positions come from
  the shin band above each foot; no bones exist on a static). Run on both the Z
  and X axes with the game's own `|score| >= 0.05` threshold; the dominant axis
  wins.

The gate — ALL must hold, else REFUSE (never guess):

1. cue1's snapped axis == cue2's dominant axis (sign included)
2. `|cue1 raw yaw − snapped axis| <= 15°` (tunable `--residual-deg`)
3. cue1 toe-offset magnitude `>= 1.5%` of height (tunable `--min-mag-frac`)
4. `>= 500` verts in each band (tunable `--min-band-verts`)

Adversarial cases verified: a 16°-off-axis mesh REFUSEs (the demonio-a1 failure
mode), a skirt-occluded foot band REFUSEs, a featureless sphere REFUSEs, and all
four cardinal facings resolve CONFIDENT on synthetic T-poses. On the real
kinpo attire-1 Tripo pull both cues agree on **+X** (residual 2.8°, toe offset
3.2% of height) — note the earlier k-NN batch lanes assumed `+Z` for every Tripo
pull ("Tripo export convention"); the gate exists precisely because that
assumption is not always true.

Truth-source alignment: `game/assets/models/model-facing.json` (hand-verified
rest renders) remains authoritative for WIRED models; this script is the
automatic gate for NEW, never-before-seen statics. The intake's own
`ledger.json` (keyed by sha256) makes re-intakes of identical bytes decide
identically. The manual escape hatch is `--facing <axis>` — the operator states
they viewed rest renders; the override is recorded in the report.

## What "done" looks like

- `intake.py` exits 0; `outbox/<fighter>/attire<N>/<timestamp>/` holds the
  archived inbox original + sidecar + all reports.
- `ledger.json` has the sha256 → facing/gate decision.
- `roster/<fighter>/attires/attire<N>/model-rigged.glb` exists (sha256 in the
  summary), `WIRING-CHECKLIST.md` beside it.
- `docs/proof/muse-<date>/tripo-intake/<fighter>-attire<N>-<stamp>/` holds
  `facing_report.json`, `rig_report.json`, `validate`/`anim_check` JSONs, the
  pose renders, and `steps.log`. Any `anim_check` flags are listed in
  `intake_summary.json` (`anim_check_flags`) and in `WIRING-CHECKLIST.md` —
  they must be explained, never ignored.
- **A human has VIEWED the pose renders** (front/back/side at the gate's worst
  frames) before wiring. UNKNOWN is never PASS.

## Wiring (manual, reviewed — the intake never touches game code)

The reviewer completes `WIRING-CHECKLIST.md` in the staged slot dir:

1. `game/js/assets.js` `MODEL_URLS`: add the base key + `<id>-attire<N>` key →
   `'../roster/<fighter>/attires/attire<N>/model-rigged.glb'` (keys MUST match
   the FULL_ROSTER `model` ids in `game/js/roster-full.js` — verify, don't copy
   blindly). Keep the old file as the ladder-back; never delete a wired model.
2. `game/js/roster-full.js`: confirm the fighter's `model` id; add the attire
   entry for a new slot.
3. Moveset: `game/assets/movesets/index.json` + `MOVESET_MAP` in
   `game/js/movesets.js` cover the fighter.
4. `game/assets/models/model-facing.json`: record the new model's mesh facing
   from a rest render (the runtime's truth table).
5. `roster/<fighter>/ATTIRE-SLOTS.md`: document the slot (Tripo UUID, sha256,
   render proof). Honor `RIG-NOTES.md` if present (jiggle sets, M-rated
   anatomy — the auto-rig does not implement per-fighter specs; flag them).
6. Node test suites + proof-harness fight for the fighter; VIEW the frames.
7. Delete the checklist file when wiring lands.

## Watcher: cron vs manual (recommendation)

**Recommended: manual trigger.** A rig run holds Blender for tens of minutes on
a loaded VM, needs `WH_BLENDER`/node_modules on PATH, and the facing-refuse
path needs a human anyway — an unattended daemon would pile up Blender jobs and
bury REFUSEs. Run `intake.py --scan` when a model lands in the inbox.

If you want a cron, make it a **notifier only**: scan the inbox and write
`INBOX-PENDING.md` (or a feed note) when unprocessed models sit there — never
auto-rig unattended. Sample (not installed):

```cron
*/30 * * * * ls ~/workspace/.../tools/tripo-intake/inbox/*/*.glb >/dev/null 2>&1 && echo "tripo-intake: models waiting in the inbox"
```

## Environment

```bash
# one-time (pins match tools/setup/setup_toolchain.sh)
bash tools/setup/setup_toolchain.sh            # Blender 4.0.2, gitleaks, node modules, t3r, pip deps
export NODE_PATH=$HOME/workspace/tools/gltf/node_modules   # or tools/anim/node_modules
# WH_BLENDER defaults to $HOME/workspace/tools/blender/blender-4.0.2-linux-x64/blender
python3 tools/tripo-intake/intake.py --scan
```

## Troubleshooting

- `intake env check FAILED` — read the listed item; usually `NODE_PATH` or
  `WH_BLENDER`.
- `REFUSED ... facing confidence too low` — view rest renders
  (`tools/proof-harness/rest.mjs` + `game/poselab.html`), decide facing, re-run
  with `--facing +X|-X|+Z|-Z`.
- `FAILED ... gates not all green` — read `rig_report.json` in the report dir;
  `validate`/`anim_check` failures name the check. The model stays un-staged;
  fix the source or the pipeline, don't hand-tweak the GLB.
- Blender `libEGL.so.1` error on minimal containers — install `libegl1`/`libgl1`
  or point `LD_LIBRARY_PATH` at extracted debs (see WORKLOG 2026-10-21 intake).
