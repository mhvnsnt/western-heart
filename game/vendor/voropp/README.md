# voro++ — vendored reference (BSD, LBNL-modified)

**What:** Voro++ — "a three-dimensional Voronoi cell library in C++" by
Chris H. Rycroft (Lawrence Berkeley National Laboratory / UC Berkeley).
Repo: https://github.com/chr1shr/voro — License: BSD 3-clause (LBNL
modification), full text in `LICENSE` (this directory).

**Why it's here:** Western Heart's arena destruction (Red Faction-style
Geo-Mod) fractures breakable walls/floors procedurally. Voronoi diagrams
are the standard way to shatter a surface into organic shards.

**The voro++ algorithm (from its docs — this is what we reimplement):**
voro++ is *cell-based*: it computes the Voronoi cell for each particle
**individually**, rather than building a global vertex/edge network.
Each cell starts as the container bounding box and is carved by a
sequence of **plane cuts** — one perpendicular-bisector plane per
neighboring particle. Cells expose volume, centroid, vertex lists.

**How WH uses it:** The C++ source is NOT vendored (kept lean; clone at
build time if a native/WASM path is ever wanted). `game/js/destruction.js`
is an original, dependency-free JavaScript implementation of the same
cell-by-plane-cuts algorithm, specialized to 2D surface fracture
(Sutherland–Hodgman half-plane clipping per cell, Lloyd relaxation for
organic shard distribution). Pure math — no THREE, no DOM — so it runs in
the game's node test harness.

**Attribution:** Algorithm after Voro++ (Rycroft, LBL). If this work is
published academically, cite: Chris H. Rycroft, "Voro++: A
three-dimensional Voronoi cell library in C++", Chaos 19, 041111 (2009).

**Integration point:** `game/js/stagebreaks.js` (Tekken wall/floor/balcony
breaks) registers breakable surfaces with `DestructionSystem` and spawns
the resulting Voronoi shards as debris meshes on break.
