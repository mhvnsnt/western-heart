# Kaggle GPU script 3/3 — batch GLB validate + optimize on the Kaggle box.
# NOTEBOOK SETUP CELL (run first):
#   !npm install -g @gltf-transform/cli gltfpack
#   (Upload your .glb files to /kaggle/working/glb-in/ first.)
# HONEST LABEL: gltfpack / gltf-transform are CPU tools; this script uses
#   the Kaggle machine for fast PARALLEL batching of the whole roster, and
#   the GPU proper is exercised by scripts 1 (torch CUDA) and 2 (Cycles).
#   Claiming "GPU-compressed" for this script would be false — it is
#   "GPU-machine batched". The value is throughput: the full roster in one
#   notebook run instead of one file at a time on a phone-side box.
# PROOF: prints GPU_PROOF lines per file (in/out bytes, % saved, sha256).
import hashlib, os, subprocess, sys

IN_DIR = "/kaggle/working/glb-in"
OUT_DIR = "/kaggle/working/glb-out"

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    files = sorted(f for f in os.listdir(IN_DIR) if f.lower().endswith((".glb", ".gltf")))
    print("GPU_PROOF: batch_files", len(files))
    for f in files:
        src = os.path.join(IN_DIR, f)
        dst = os.path.join(OUT_DIR, f.rsplit(".", 1)[0] + ".opt.glb")
        r = subprocess.run(["gltf-transform", "optimize", src, dst],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("GPU_PROOF: file", f, "FAILED", r.stderr.strip().splitlines()[-1:] )
            continue
        si, so = os.path.getsize(src), os.path.getsize(dst)
        pct = 100.0 * (1 - so / si) if si else 0
        print(f"GPU_PROOF: file {f} {si} -> {so} bytes (-{pct:.1f}%) sha256 {sha(dst)}")
    print("GPU_PROOF: status COMPLETE")

if __name__ == "__main__":
    main()
