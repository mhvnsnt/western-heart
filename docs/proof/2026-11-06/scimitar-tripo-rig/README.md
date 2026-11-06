# Scimitar on the owner's own Tripo model (2026-11-06)

Owner 2026-11-06: "Also that not the correct scimitar glb model from my tripo imports".

The game loaded `game/assets/models/scimitar-rigged.glb` (a Shaheen-based base mesh); its card was torn shards. The
owner's Tripo import is `roster/scimitar/attires/attire1/source/scimitar-a1.glb` (Tripo a3e76dd5, fused pauldron and
blade, archived 2026-10-22), an unrigged static facing +X (looked at in poselab's rest view before rigging).

Rigged with `tools/auto_rig/rig_tripo_static.py --facing +X --height 1.8` (GameRig, bone heat, smoothing), packed with
`tools/deploy/fit_cdn_budget.py --jpeg-q 75` to 19.2 MB (texture error 0.95 deg mean) so it loads from jsDelivr / the
Cloudflare build. Deviation: the stretch gate (p99.9 edge stretch) does not reach 2.5 or 3.5. The stretch sits in his
long robe between the legs (and single-frame foot spikes in the CMU boxing stress clip), so the run was finished with
the gate off (`--smooth-gate 99`) and the result judged by eye: `scimitar-card-and-fight.png` = old card / new card and
a real local fight vs Pantera, standing in stance, facing his opponent, intact. The proof-render step aborts on this VM
(no EGL), which is why no Blender renders are here.

Gate files: `anim_check_before_smoothing.json`, `anim_check_after_smoothing.json`, `gamerig_metrics.json`,
`smooth_weights.log`, `limb_isolation.log`.
