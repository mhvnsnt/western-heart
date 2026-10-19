# Multi-Arm / Retracting-Limb Research — 2026-10-19

**Owner order:** Real, 2026-10-19 — "Study things and characters like DXMMII and multi armed fighters or characters or retracting limb characters to help u wire up and pull in stuff to help into the repo."

**Scope:** how games/engines handle multi-armed fighters and retracting/detachable limbs, and what applies to DXMMII's open issues:
1. Leg DEF chains have 5 segments but parts exist only for 3 → 268mm/226mm visual gaps (KNOWN_ISSUE_EXTRA_ARMS.md TODO).
2. Detach/reattach uses structural reparenting which is NOT keyframable → parts don't follow the gyro during playback f168–240.

Dxmmii pronouns: it/its.

---

## 1. Character studies

### 1a. Mortal Kombat Shokan — Goro, Sheeva, Kintaro (4 arms)
- The genre's reference implementation. Four arms are built as **extra bone chains rooted off the chest/shoulder** — exactly DXMMII's layout (Rigify `limbs.arm` samples socketed at `spine.003`, BUILD.md §1).
- **Gameplay readability:** Shokan lower arms telegraph low attacks (sweeps); upper arms telegraph overheads. Lesson for DXMMII: when all 4 arms are attached, give each PAIR a distinct combat role so the player can read it.
- **Animation:** from MK: Deadly Alliance on, Goro's fighting styles were designed around 4 arms. You cannot retarget 2-arm mocap onto 4 arms — the extra pair needs custom keys or procedural layering on top of the base body animation.
- Prior art in-repo: RESEARCH.md already studied the Goro MK Onslaught FBX (a9strack3d, real game bones, 4-arm hierarchy intact) as DXMMII's anatomy reference.

### 1b. Asura's Wrath — six arms as a FORM (arm states)
- Asura's extra arms are a **power-up state** (Vajra Asura): arms grow in when the rage meter fills, retract when it drains. Spawning is done by "spreading both analogue sticks outwards."
- **Direct mapping to DXMMII's 5-state machine** (attached / retracting / detached / floating / growing): treat extra arms as STATE-DRIVEN, not always-on. Asura's Wrath proves players read arm-count changes as power changes — DXMMII's gyro/fighting-style switching is the same design language.
- The grow/retract transition is a scripted, exaggerated beat (not a subtle blend) — matches DXMMII's shape-key "growing" approach in RESEARCH.md.

### 1c. Doctor Octopus — tentacle actuators (independent arm control)
- 4 mechanical tentacles, each with **independent targeting**: in the Insomniac Spider-Man games the arms act with their own seek/block/attack behaviors layered over Otto's body animation.
- Rigging pattern: each tentacle is an **IK chain with its own target control**, rooted to the harness (spine). The chains are independent objects — the same architecture as DXMMII's separate-object extra arms.
- **Lesson for DXMMII's floating state:** give each detached arm its own free control object (not one shared control). Independent controls let the two floating arms drift/fight separately — the "gyro" feel.
- Rigify (ships with Blender, GPL) has a **`tentacle` rig-type module** purpose-built for this: stretchy IK chains with FK/IK blending. Documented as a future path if DXMMII ever gets true doc-ock tentacle arms instead of rigid arm parts.

### 1d. General Grievous — split-arm gimmick (2→4 transition)
- Grievous's arms SPLIT mid-fight (2 arms become 4). Games animate this as a **scripted transition beat** — a short, readable transformation, not a continuous blend.
- Maps to DXMMII's growing state: the grow/retract should be a discrete, punchy transition (with the shoulder-stump blend shapes from RESEARCH.md), not a slow morph.

### 1e. Tekken's Jack robots — modular mechanical parts
- Jack-series robots are built exactly like DXMMII: **one mesh per part, rigidly parented to its bone, no smooth skinning**. This validates the KatsBits method in BUILD.md §2 as the correct approach for a patchwork robot — do not "fix" it by smooth-skinning.

---

## 2. The keyframing problem — industry-standard fix

### The problem (DXMMII today)
`scripts/04_states_demo.py` drives detach/reattach with **structural reparenting** (`ob.parent` reassignment). Blender cannot keyframe a parent change, so in playback f168–240 the parts stay near the socket instead of following the gyro. (KNOWN_ISSUE_EXTRA_ARMS.md TODO.)

### The fix: Child Of constraints with keyframed Influence
This is the standard, documented Blender technique for detachable props/limbs (Blender 5.x manual, Blender Artists, polycount):

> "The main advantage over a regular parent-child relationship is that the constraint has an animatable *Influence*, which makes it possible to switch to different parents over time." — Blender Manual, Child Of constraint

**Concrete migration plan for the DXMMII pipeline:**

1. Per extra arm, add TWO Child Of constraints on the arm's root part object:
   - `ChildOf_socket` → target: the socket DEF bone (attached state)
   - `ChildOf_free` → target: a per-arm free control Empty (detached/floating state)
2. Click **Set Inverse** on each (from rest position) so nothing jumps.
3. Keyframe Influence on adjacent frames for snap transitions (the cursa.app attach/detach pattern):
   - Attach: frame N `ChildOf_socket.influence = 0` keyed, frame N+1 `= 1` keyed (and `ChildOf_free` inverse).
   - Detach: frame M `= 1` keyed, frame M+1 `= 0` keyed.
4. Animate the free control Empty for the floating drift — or drive it with Wiggle/spring physics (see §4) for the gyro-float feel.
5. Keep the tail-based Pinv math from KNOWN_ISSUE_EXTRA_ARMS.md (Blender 4.0.2 parents to the bone TAIL via RNA) — the constraint approach doesn't remove that quirk, it just makes the switch keyframable.

**Why two constraints instead of one:** you cannot keyframe a constraint's *target*. Two constraints with cross-faded influence is the canonical pattern (Blender Artists thread "Child of constraint", 2022).

**Validation plan:** re-run the 04 QC with the true-formula measurements (`true_world_of()` with tail-based X); detach/reattach deltas must stay < 1mm; all 9 QC stills re-rendered and eyes-checked limb-by-limb.

### Leg segment fix
Leg DEF chains: thigh→thigh.001→shin→shin.001→foot (5 segments), parts exist only for 3. Fix: build `thigh.001` and `shin.001` shell parts in `03_build_body.py` using the same KatsBits method, parented to their DEF bones. Straightforward — needs one Blender run to validate, no research risk.

---

## 3. Gameplay mechanics worth stealing

| Mechanic | Source | DXMMII application |
|---|---|---|
| Arm-pair role readability (low vs high telegraphs) | MK Shokan | When 4-arm attached, lower pair = sweeps/lows, upper pair = overheads |
| Arms as power-state (grow = power up) | Asura's Wrath | Gyro mode = 4-arm power state; human mode = 2-arm |
| Independent per-arm targets | Doc Ock (Insomniac) | One free control per floating arm, not shared |
| Scripted split/grow beat | Grievous | Grow/retract as punchy discrete transition + stump blend shapes |
| Modular rigid parts | Tekken Jacks | Keep KatsBits method; don't smooth-skin |

---

## 4. Pulled in (this lane)

- **`tools/limb-system/multi-arm-research/wiggle-bones-v3/`** — Wiggle 2 "Ultimate" (N30Z3N/Blender-Wiggle-Bones-V3), **GPL-3.0**, Blender 4.0/5.x compatible. Spring physics for bones (lag, bounce, stretch, collision). Intended use: drive DXMMII's floating-arm free controls with springy gyro drift instead of hand-keyed float curves. Includes upstream LICENSE verbatim.
- **Rigify (GPL, ships with Blender 4.0.2 — no pull needed):** `limbs.arm` (already used for DXMMII's extra arms), `tentacle` rig-type (future doc-ock arms), `limbs.super_limb`. Reference only.

## 5. Studied but NOT pulled (honest license calls)

| Item | License status | Why not pulled |
|---|---|---|
| tentacletk (m3trik/tentacle) | LGPL v3 | Maya-focused; Blender wrapper is a stub with no slot library |
| aditiapratama/tentacle_rigs | **No license** | Cannot verify redistribution rights — documented only |
| aresdevo/animaide | **No license detected** | Cannot verify redistribution rights — documented only |
| artellblender/springbones | **No license** | 809 stars but no license file — documented only |
| Auto-Rig Pro | Commercial (paid) | "Duplicate or remove limbs to rig spiders, centaurs" is the exact feature we want, but it's paid — documented, not cracked |
| Goro MK Onslaught FBX (a9strack3d) | Fan conversion (gray area) | Already documented in RESEARCH.md; not redistributed |

---

## 6. Open follow-ups (not this lane)

1. Implement the Child Of migration in `04_states_demo.py` + re-run QC (needs a Blender session; the approach above is the complete spec).
2. Build the 2 missing leg segment parts.
3. Try Wiggle 2 on a floating-arm free control and eyes-check the drift feel.
4. Retargeting: 4-arm characters need custom anim sets — the auto-rig wave's motion-retargeting work should treat DXMMII's extra arms as a special case.
