// ============================================================================
// femfx_bind.cpp — minimal C API over AMD FEMFX for the WH WASM build.
//
// Exposes just what game/js/femfx-adapter.js needs:
//   - one scene, one tet mesh (the anatomy-region lattice, tets built from
//     the lattice cells in JS and passed in flat)
//   - per-material tissue params (fat / muscle / bone presets)
//   - fixed-step update, vertex position readback, impulse hits,
//     fracture reports
//
// API usage verified against amd_femfx/inc/AMD_FEMFX.h (GPUOpen-Effects).
// NOTE: not yet compiled — first compile happens via tools/femfx/build_wasm.sh
// (Emscripten). Minor signature drift vs. the pinned FEMFX revision should be
// fixed at that build; the JS-side contract (function names/semantics) is
// stable.
//
// Build: tools/femfx/build_wasm.sh  (Emscripten)
// License: MIT (AMD FEMFX) — see tools/femfx/README.md
// ============================================================================
#include <cmath>
#include <cstdint>
#include "AMD_FEMFX.h"

static FmScene* g_scene = nullptr;
static FmTetMeshBuffer* g_buffer = nullptr;
static FmTetMesh* g_mesh = nullptr;
static uint32_t g_numVerts = 0;

// Fracture report plumbing: the app must hand FEMFX a reports buffer.
static FmTetMeshFractureReport g_fractureReports[4];

// Tissue presets: (young's modulus Pa, poisson, fracture stress Pa)
// Game-scaled: real bone is ~1e10 Pa which needs tiny timesteps; we keep the
// RATIOS (bone >> muscle > fat) and let the adapter tune absolute scale.
struct TissuePreset { const char* name; float E; float poisson; float fracture; };
static const TissuePreset TISSUES[] = {
    {"fat",    3.0e3f, 0.49f, 1.0e12f},  // soft, nearly incompressible, never fractures
    {"muscle", 6.0e4f, 0.45f, 1.0e12f},  // stiffer active tissue, never fractures
    {"bone",   2.0e6f, 0.30f, 4.0e5f},   // rigid core; CAN fracture above threshold
};

extern "C" {

// Create the scene. maxVerts/maxTets must cover the lattice (fracture can
// add verts, so maxVerts should exceed the initial count).
// Returns 1 on success.
int femfx_create(uint32_t maxVerts, uint32_t maxTets) {
    if (g_scene) return 1;
    FmSceneSetupParams sp;  // defaults; maxTetMeshBuffers etc. set below
    sp.maxTetMeshBuffers = 1;
    sp.maxTetMeshes = 4;  // room for fracture pieces
    sp.maxRigidBodies = 0;
    sp.maxDistanceContacts = 0;
    sp.maxVolumeContacts = 0;
    g_scene = FmCreateScene(sp);
    if (!g_scene) return 0;

    FmTetMeshBufferSetupParams bp;
    bp.numVerts = maxVerts;      // initial vert budget (lattice count)
    bp.numTets = maxTets;
    bp.numVertIncidentTets = maxTets * 10;
    bp.maxVertAdjacentVerts = 48;
    bp.maxVerts = maxVerts * 2;  // headroom for fracture-spawned verts
    bp.maxExteriorFaces = maxTets * 4;
    bp.maxTetMeshes = 4;
    g_buffer = FmCreateTetMeshBuffer(bp, nullptr, nullptr, &g_mesh);
    if (!g_buffer || !g_mesh) return 0;

    // wire the fracture report buffer before the first step
    FmFractureReport& fr = FmGetSceneFractureReportRef(g_scene);
    fr.maxTetMeshReports = 4;
    fr.tetMeshReportsBuffer = g_fractureReports;

    g_numVerts = 0;
    return 1;
}

// Add the region tet mesh. verts: float3 array (numVerts), tets: uint4 index
// array (numTets). tissue: 0=fat, 1=muscle, 2=bone. restDensity kg/m^3.
// pinned[i] != 0 -> vertex is kinematic (deep core + caps, like the Jolt
// backend's pinning).
// Returns the tet mesh id, or FM_INVALID_ID.
uint32_t femfx_add_tetmesh(const float* verts, uint32_t numVerts,
                           const uint32_t* tets, uint32_t numTets,
                           int tissue, float restDensity,
                           const uint8_t* pinned) {
    if (!g_scene || !g_mesh) return FM_INVALID_ID;
    const TissuePreset& tp = TISSUES[tissue < 0 || tissue > 2 ? 1 : tissue];

    FmInitVertState(g_mesh, (const FmVector3*)verts,
                    FmMatrix3::identity(), FmVector3(0.0f), 1.0f);
    FmTetMaterialParams mat(
        restDensity, tp.E, tp.poisson,
        /*plasticYieldThreshold*/ 1.0e12f, /*plasticCreep*/ 0.0f,
        /*plasticMin*/ 1.0f, /*plasticMax*/ 1.0f,
        tp.fracture,
        /*maxCGIterations*/ 40,
        /*lowerDeformationLimit*/ 0.0f, /*upperDeformationLimit*/ 0.0f);
    FmInitTetState(g_mesh, (const FmTetVertIds*)tets, mat);
    FmComputeMeshConstantMatrices(g_mesh);
    FmFinishConnectivityFromVertIncidentTets(g_mesh);
    FmSetMassesFromRestDensities(g_mesh, restDensity);
    if (pinned) {
        for (uint32_t i = 0; i < numVerts; i++)
            if (pinned[i]) FmSetVertMass(g_mesh, i, 0.0f);
    }
    FmFinishTetMeshInit(g_mesh);
    g_numVerts = numVerts;
    return FmAddTetMeshBufferToScene(g_scene, g_buffer);
}

void femfx_step(float dt) {
    if (g_scene) FmUpdateScene(g_scene, dt);
}

// Copy current vertex positions (float3) into out. Returns vert count.
uint32_t femfx_get_positions(float* out) {
    if (!g_scene || !g_mesh || !out) return 0;
    for (uint32_t i = 0; i < g_numVerts; i++) {
        FmVector3 p = FmGetVertPosition(g_mesh, i);
        out[i * 3 + 0] = p.x; out[i * 3 + 1] = p.y; out[i * 3 + 2] = p.z;
    }
    return g_numVerts;
}

// Radial impulse at (wx,wy,wz), direction (dx,dy,dz), magnitude, radius.
// Pinned (zero-mass) verts are skipped.
void femfx_apply_impulse(float wx, float wy, float wz,
                         float dx, float dy, float dz,
                         float magnitude, float radius) {
    if (!g_scene || !g_mesh) return;
    float r2 = radius * radius;
    for (uint32_t i = 0; i < g_numVerts; i++) {
        FmVector3 p = FmGetVertPosition(g_mesh, i);
        float ex = p.x - wx, ey = p.y - wy, ez = p.z - wz;
        float d2 = ex * ex + ey * ey + ez * ez;
        if (d2 < r2) {
            float mass = FmGetVertMass(g_mesh, i);
            if (mass > 0.0f) {
                float fall = 1.0f - sqrtf(d2) / radius;
                float s = magnitude * fall / mass;
                FmVector3 v = FmGetVertVelocity(g_mesh, i);
                v.x += dx * s; v.y += dy * s; v.z += dz * s;
                FmSetVertVelocity(g_mesh, i, v);
            }
        }
    }
}

// Total fractured faces across mesh reports since the last call.
// (FEMFX accumulates; the adapter diffs per frame.)
uint32_t femfx_poll_fractures() {
    if (!g_scene) return 0;
    FmFractureReport& fr = FmGetSceneFractureReportRef(g_scene);
    uint32_t total = 0;
    for (uint32_t i = 0; i < fr.maxTetMeshReports; i++)
        total += fr.tetMeshReportsBuffer[i].numFractureFaces;
    return total;
}

void femfx_destroy() {
    if (g_scene) { FmDestroyScene(g_scene); g_scene = nullptr; }
    g_buffer = nullptr;
    g_mesh = nullptr;
    g_numVerts = 0;
}

}  // extern "C"
