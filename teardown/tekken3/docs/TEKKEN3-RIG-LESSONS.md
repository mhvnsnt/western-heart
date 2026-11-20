# What Tekken 3 Teaches Us About Fighting Game Rigs

**The goal:** Understand how Tekken 3 rigs and animates characters, apply to Bannon, AshLane, Concrete Dragon, Brutal Fist.

> We study their methods. We build our characters.

---

## 1. Characters Are Multi-Part Meshes, Not Single Models

**Finding:** Each 3DMK character record contains 27 mesh segments (rows), each pointing to its own vertex/face/UV data in the payload.

**What this means:**
- A Tekken 3 fighter is ~27 separate mesh pieces parented in a hierarchy
- Head, torso, upper arms, forearms, hands, thighs, shins, feet, etc. are SEPARATE meshes
- They move as rigid bodies connected at joints — NOT skinned with smooth vertex weights

**Why this matters for us:**
- PS1 had no hardware skinning. Every "bone" is a separate mesh transformed by a matrix.
- This is actually SIMPLER than modern skinning — and it still looks great
- For our games: rigid-part characters are easier to rig, easier to debug, and perform better
- **Bannon/AshLane:** Consider rigid-part rigs for background NPCs or low-poly fighters. Full skinning for heroes, rigid parts for everyone else.

---

## 2. The Bone Hierarchy Is the Animation

**Finding:** With 27 mesh parts, the "rig" is a transform hierarchy. Each frame, the game computes a matrix for each part based on the current animation pose.

**How PS1 fighting games animate:**
1. Animation data = keyframed rotations (and sometimes positions) per joint
2. Each frame: walk the hierarchy, compute world matrix per part
3. Send each part's matrix + mesh to the GPU (GTE for transforms)
4. No vertex skinning — each vertex belongs to exactly one part

**What this means for us:**
- **Animation compression:** Store only rotations per joint per keyframe. Positions are derived from the hierarchy. This is incredibly compact.
- **Blending:** To blend between animations (idle → punch), interpolate joint rotations. Simple quaternion/SLERP or Euler lerp.
- **Concrete Dragon:** Our 3D brawler should use this exact approach. Hierarchical rigid parts, rotation-only keyframes.

---

## 3. Polygon Budget: Less Than You Think

**Finding:** 3DMK character records are ~24-29KB each. At ~27 parts per character, that's roughly **1KB per body part**.

Estimating from PS1-era Tekken 3:
- Full character: approximately **800–1,200 triangles**
- Per body part: approximately **30–50 triangles**

**The lesson:** Tekken 3 looks amazing with ~1K triangles per fighter. Our games on modern hardware can do 10-50x this, but the PRINCIPLE matters:
- Silhouette > detail. Tekken 3 characters read clearly because the shapes are strong
- Texture does the heavy lifting. Small textures (32×32!) on simple geometry
- Animation sells it. Great animation on simple models beats bad animation on complex models

**For our games:**
- **AshLane** (2D/3D hybrid): Keep 3D models lean. Let the art style and animation carry them.
- **Bannon:** Don't over-model. A clean 5K-triangle fighter with great textures and animation will look better than a 50K-triangle fighter with stiff animation.

---

## 4. Hitboxes Are Separate From Visuals

**Finding (from executable strings + architecture):** The game has distinct systems for rendering (3DMK meshes) and gameplay (hit detection). "STHITUI" string suggests a hit UI/state system.

**How fighting games do hitboxes:**
- Each attack has **startup frames** (wind-up), **active frames** (hitbox exists), **recovery frames** (vulnerable)
- Hitboxes are simple shapes (boxes, spheres) attached to bones — NOT the visible mesh
- Hurtboxes (where you can be hit) are also simple shapes, usually a capsule around the torso + head

**What this means for us:**
- **NEVER use the visible mesh for hit detection.** Always use simplified proxy shapes.
- Each move needs: startup count, active frames, recovery count, damage, hitbox size/position per active frame
- **Brutal Fist / Bannon:** Build a move data format: `{startup, active, recovery, damage, hitbox:{bone, offset, size}, blockstun, hitstun}`

---

## 5. Animation Is Data, Not Code

**Finding:** 1.2MB executable (pure logic) vs 37MB BNS (all content). Animations are data loaded from the archive.

**The architecture:**
```
Executable (logic):
  - Reads animation ID
  - Looks up keyframe data in BNS
  - Interpolates between keyframes
  - Computes joint matrices
  - Sends to renderer

BNS Archive (data):
  - Animation clips (per character, per move)
  - Keyframe data (rotations per joint per frame)
  - No logic — just numbers
```

**For our games:** Animations should be data files, not hardcoded. This lets designers/animators iterate without touching code.

---

## 6. The 60fps Fighting Game Formula

Tekken 3 runs at 60fps. Every frame:
1. Read inputs (both players)
2. Update game state (positions, velocities, timers)
3. Check collisions (hitbox vs hurtbox)
4. Update animations (advance frame counters, interpolate)
5. Compute matrices for all mesh parts
6. Render

**Frame data is everything.** A punch that starts up in 10 frames, is active for 3, recovers in 15 — these numbers ARE the game feel. Tekken's depth comes from hundreds of moves each with precise frame data.

---

## Mapping to Our Games

| Tekken 3 System | Our Equivalent | Game |
|---|---|---|
| 3DMK multi-part mesh | Rigid-part character rigs | Bannon, Concrete Dragon |
| BNS asset archive | Indexed asset packs | All games |
| Rotation-only keyframes | Animation clip format | All games |
| Hitbox/hurtbox system | Move data + collision | Brutal Fist, Bannon |
| 60fps fixed timestep | Fixed simulation step | All games |
| Small texture atlas | Texture budget discipline | AshLane, Concrete Dragon |
| Data-driven animations | Animation as data files | All games |

---

## Action Items

1. **Define our move data format** — startup/active/recovery/damage/hitbox per move
2. **Prototype rigid-part character** — build one Bannon fighter as hierarchical rigid parts, compare to skinned version
3. **Set polygon budgets** — heroes: 5-10K tris, NPCs: 1-3K tris (Tekken proved 1K works)
4. **Animation as data** — no hardcoded animation in game code, all from data files
5. **Fixed 60fps simulation** — game logic ticks at fixed rate, rendering interpolates
