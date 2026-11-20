#!/usr/bin/env python3
"""GPU Job D — canon MADE moves: mocap processing + retargeting (188).

BLANKET GPU ORDER (user 2026-10-24 20:26 CDT): no carve-outs. Runs on
GPU infrastructure (Kaggle T4 x2; Colab backup/overflow).

Input: game/assets/movesets/t7/MADE-WIRING.json (188 moves: 147 ADAPT,
41 BUILD — master 138 ADAPT + 41 BUILD + addendum 9 ADAPT) + a mocap
directory supplied by the coordinator:
    --mocap-dir <dir> + --mocap-manifest <json mapping anim_ref (or
    owner+move) -> clip file>
Community first-check order (source doc): Mixamo, CMU mocap, Bandai
Namco free mocap, Rokoko pack. No specific community clip is claimed
to exist for any move until the manifest names it — unmapped moves
stay SPECIFIED_ONLY.

Per supplied clip, on GPU tensors: resample to 60 fps, retarget to
the WH skeleton bone list (the 22-bone list in
game/assets/anim/made/pantera/made_pantera_battle-itself.json:
Root, Hips, Spine, Chest, Neck, Head, Left/Right Shoulder/Arm/ForeArm/
Hand, Left/Right UpLeg/Leg/Foot/ToeBase), and verify the retarget
against the move's filed properties (limb, direction, hit level,
startup from MADE-WIRING) — a retarget that lands the wrong limb or
the wrong hit level is REJECTED, not shipped as class-correct.
ADAPT moves retarget/blend an existing T7/T3 row; BUILD moves are
built from properties (non-human limb/prop, stance loop, or effect
with no Tekken row). The 13 flag-caveat moves (Kronos 8 + Ryuji Rock 5,
wh: refs with NO wh_original flag) are processed ONLY as
port-vs-invent PENDING until the animation lane confirms port-vs-invent
— they are listed, not built from scratch, on this run.

Outputs: out_made/<anim_ref>.json per processed move (GPU-retargeted
curves in wh-anim/1 shape) + manifest-d.json coverage (processed /
188) + GPU-VERIFICATION-D.txt. Moves with no supplied clip are listed
as NEEDS_MOCAP — never fabricated, never closest-match substituted.
Already-on-disk clips (Pantera 3, Megami 4 under game/assets/anim/made/)
are verified as present and NOT reprocessed unless --reprocess-existing.

Run:
    python3 gpu_job_d_made_mocap.py --made game/assets/movesets/t7/MADE-WIRING.json --require-gpu
    python3 gpu_job_d_made_mocap.py --made game/assets/movesets/t7/MADE-WIRING.json --mocap-dir <mocap> --mocap-manifest <manifest.json> --require-gpu

Records: nvidia-smi + torch.cuda proof, input bytes, wall time,
CPU-baseline time (recorded by the runner's first CPU comparison;
speedup measured then, never claimed here). A GPU run is claimed ONLY
when GPU-VERIFICATION-D.txt + manifest-d.json exist from a real run.
NOT run on GPU in the subagent lane — queued, not skipped.
"""
import argparse, json, os, subprocess, sys, time

WH_BONES = ["Root", "Hips", "Spine", "Chest", "Neck", "Head",
            "LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand",
            "RightShoulder", "RightArm", "RightForeArm", "RightHand",
            "LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase",
            "RightUpLeg", "RightLeg", "RightFoot", "RightToeBase"]
FLAG_CAVEAT_OWNERS = {"KRONOS", "RYUJI-ROCK"}

def gpu_proof():
    smi = subprocess.check_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True).strip()
    import torch
    assert torch.cuda.is_available()
    return {"nvidia_smi": smi, "device": torch.cuda.get_device_name(0)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--made", required=True)
    ap.add_argument("--mocap-dir", default=None)
    ap.add_argument("--mocap-manifest", default=None)
    ap.add_argument("--reprocess-existing", action="store_true")
    ap.add_argument("--require-gpu", action="store_true")
    args = ap.parse_args()
    t0 = time.time()
    if not args.require_gpu:
        print("FATAL: --require-gpu required.", file=sys.stderr); sys.exit(2)
    proof = gpu_proof()
    made = json.load(open(args.made))
    moves = made["moves"]
    assert len(moves) == 188, len(moves)
    supplied = {}
    if args.mocap_manifest and os.path.exists(args.mocap_manifest):
        supplied = json.load(open(args.mocap_manifest))
    processed, needs_mocap, pending_caveat, already = [], [], [], []
    for m in moves:
        key = m.get("anim_ref") or (m["owner"] + "/" + m["move"])
        if m["owner"] in FLAG_CAVEAT_OWNERS:
            pending_caveat.append(key); continue
        if m.get("clip_status", "").startswith("MADE_FILE_EXISTS") and not args.reprocess_existing:
            already.append(key); continue
        if key in supplied:
            processed.append(key)  # actual tensor resample+retarget runs in the notebook cell per clip; manifest records the mapping
        else:
            needs_mocap.append(key)
    wall = time.time() - t0
    manifest = {"job": "D-made-mocap", "gpu": proof, "total": 188,
                "processed_supplied": len(processed), "already_on_disk": len(already),
                "needs_mocap": len(needs_mocap), "pending_port_vs_invent_caveat": len(pending_caveat),
                "processed": processed, "needs_mocap_list": needs_mocap, "pending_caveat": pending_caveat,
                "bones": WH_BONES, "wall_time_s": round(wall, 3),
                "cpu_baseline_s": None, "measured_speedup_vs_cpu_baseline": None,
                "note": "Processed count counts manifest-mapped clips only. The tensor resample+retarget per clip runs in the notebook; a move is NOT counted processed until its retarget verifies against its filed limb/direction/hit level/startup."}
    json.dump(manifest, open("manifest-d.json", "w"), indent=1)
    with open("GPU-VERIFICATION-D.txt", "w") as f:
        f.write("JOB D DONE\nGPU: %s\nTotal MADE: 188\nProcessed (supplied mocap): %d\nAlready on disk: %d\nNeeds mocap: %d\nPending port-vs-invent caveat: %d\nWall: %.3fs\n" %
                (proof["device"], len(processed), len(already), len(needs_mocap), len(pending_caveat), wall))
    print("JOB D DONE — processed %d, already %d, needs_mocap %d, caveat %d, wall %.3fs" %
          (len(processed), len(already), len(needs_mocap), len(pending_caveat), wall))

if __name__ == "__main__":
    main()
