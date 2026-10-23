"""tools/auto_rig/backends/weight_conventions.py — WH skin-weight conventions.

Post-heat weight fixup applied by the auto-rig backends (wired into
blender_heat.py). Runs INSIDE Blender (needs bpy + the imported meshes and
the built WH_Skeleton armature).

Conventions (WH standard, codified 2026-10-22):
  1. ISLAND FIXUP (carried over verbatim from blender_heat.py): bone heat can
     leave disconnected islands with zero weights; unweighted verts crash the
     glTF exporter. Assign them to the nearest bone head with weight 1.0.
  2. NORMALIZE: every vertex's weights sum to 1.0 (Blender auto-normalizes at
     export, but downstream tools — k-NN transfer, anim_check, gltfpack —
     read the blend-time weights; normalized here, once, deterministically).
  3. MAX-INFLUENCES CAP: at most 4 bones per vertex (glTF vec4 + UE4
     standard, per the DOA/SF/Tekken teardown research), dropping the
     smallest weights and renormalizing. Enforced by default; pass
     max_influences=0 to disable.

Teardown-derived per-bone rules (DOA/SF/Tekken weight conventions from
~/workspace/jiggle-face-hands-teardown.md) land in TEARDOWN_RULES below —
per-region weight caps and region->bone allow-lists applied here, so the
auto-rig system enforces them instead of relying on per-model hand fixes.
"""

# Teardown-derived rules (DOA/SF/Tekken research, 2026-10-22).
# From ~/workspace/jiggle-face-hands-teardown.md:
#   - glTF JOINTS_0/WEIGHTS_0 are vec4 and UE4 defaults to 4 influences:
#     MAX 4 bones per vertex, weights normalized to 1.0.
#   - Tekken skeleton uses Left/Right prefixes (UE4 convention); weight
#     painting requires consistent L/R naming for X-mirror.
#   - Weight work is PAINTING quality, not placement: region isolation
#     (finger verts never dominated by palm/wrist; face-region verts never
#     dominated by head/neck on rigs that carry face bones).
TEARDOWN_RULES = [
    {"rule": "max_influences_4",
     "note": "at most 4 influencing bones per vertex; drop smallest, "
             "renormalize. Enforced via max_influences=4."},
    {"rule": "normalize",
     "note": "every vertex's weights sum to 1.0."},
    {"rule": "lr_symmetric_names",
     "note": "every Left* bone weight group must have a Right* twin and "
             "vice versa (Tekken/UE4 Left/Right-prefix convention); "
             "asymmetric chains are a rig-authoring bug, not a convention."},
    {"rule": "finger_region_isolation",
     "note": "finger/thumb bones may not dominate verts whose dominant "
             "bone is palm/wrist/forearm, and vice versa (the recurring "
             "cause of 'fingers stretch when the wrist moves')."},
]


def apply(meshes, arm, max_influences=0):
    import bpy  # noqa: E402
    from mathutils import Vector  # noqa: E402

    bones = [(b.name, arm.data.bones[b.name].head_local)
             for b in arm.data.bones]

    for m in meshes:
        vgroups = m.vertex_groups
        mw = m.matrix_world
        for v in m.data.vertices:
            groups = [(g.group, g.weight) for g in v.groups]
            if not groups:
                # 1. island fixup: nearest bone head, weight 1.0
                co = mw @ v.co
                bn, _ = min(bones, key=lambda b: (b[1] - co).length)
                vg = vgroups.get(bn) or vgroups.new(name=bn)
                vg.add([v.index], 1.0, "REPLACE")
                continue
            # 2. normalize
            total = sum(w for _, w in groups)
            if total <= 0.0:
                co = mw @ v.co
                bn, _ = min(bones, key=lambda b: (b[1] - co).length)
                vg = vgroups.get(bn) or vgroups.new(name=bn)
                vg.add([v.index], 1.0, "REPLACE")
                continue
            # 3. optional max-influences cap (drop smallest, renormalize)
            if max_influences and len(groups) > max_influences:
                groups.sort(key=lambda gw: gw[1])
                drop = groups[:len(groups) - max_influences]
                keep = groups[len(groups) - max_influences:]
                for gi, _ in drop:
                    vg = vgroups[gi]
                    vg.remove([v.index])
                groups = keep
                total = sum(w for _, w in groups)
            scale = 1.0 / total
            for gi, w in groups:
                vgroups[gi].add([v.index], w * scale, "REPLACE")
    return len(meshes)
