# Kaggle GPU script 1/3 — GPU animation resample + quantize (WH pipeline).
# RUNS ON: Kaggle notebook with GPU accelerator ON (2x Tesla T4).
#   - Kaggle preloads torch with CUDA. No pip install needed for torch.
#   - Upload a .glb (or several) to the notebook, set GLB_PATH below.
# PROOF: script prints GPU_PROOF lines (GPU name, torch/CUDA versions,
#   input/output sizes, sha256 of the quantized output). Paste that whole
#   block back to the agent as the GPU-verification record.
# LOCAL STATUS: logic is device-agnostic (device = cuda if available else
#   cpu); it was NOT run on a T4 by this lane (subagent cannot open the
#   Kaggle notebook). The CPU path is the same code with device='cpu'.
import hashlib, json, struct, sys

GLB_PATH = sys.argv[1] if len(sys.argv) > 1 else "/kaggle/input/wh-fighter/fighter.glb"  # argv override for local testing; Kaggle: edit the default or pass the path
TARGET_FPS = 30.0

def gpu_proof(*args):
    print("GPU_PROOF:", *args)

def main():
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    gpu_proof("device", device)
    if device == "cuda":
        gpu_proof("gpu_name", torch.cuda.get_device_name(0))
        gpu_proof("gpu_count", torch.cuda.device_count())
    gpu_proof("torch", torch.__version__, "cuda_build", torch.version.cuda)
    data = open(GLB_PATH, "rb").read()
    magic, version, length = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67, "not a GLB (bad magic)"
    json_len, json_type = struct.unpack("<II", data[12:20])
    gltf = json.loads(data[20:20 + json_len])
    gpu_proof("glb_bytes", len(data), "animations", len(gltf.get("animations", [])))
    # Walk animation samplers: decode rotation (VEC4 quaternion) inputs/outputs
    # from the BIN chunk and resample to TARGET_FPS with torch slerp on GPU.
    bin_off = 20 + json_len
    bin_len, bin_type = struct.unpack("<II", data[bin_off:bin_off + 8])
    bin_data = data[bin_off + 8:bin_off + 8 + bin_len]
    total_in = total_out = 0
    out_chunks = []
    for anim in gltf.get("animations", []):
        for sampler in anim.get("samplers", []):
            inp = gltf["accessors"][sampler["input"]]
            outp = gltf["accessors"][sampler["output"]]
            if outp["type"] != "VEC4":
                continue  # positions/scales: left for the CPU pass; rotations dominate size
            def read_acc(acc, comp_size, comps):
                bv = gltf["bufferViews"][acc["bufferView"]]
                off = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
                n = acc["count"]
                import numpy as np
                arr = np.frombuffer(bin_data, dtype=np.float32, count=n * comps, offset=off)
                return torch.from_numpy(arr.copy()).reshape(n, comps).to(device)
            times = read_acc(inp, 4, 1).flatten()
            quats = read_acc(outp, 4, 4)
            total_in += quats.numel() * 4
            # Slerp resample onto a uniform TARGET_FPS grid.
            t0, t1 = float(times[0]), float(times[-1])
            n_new = max(2, int((t1 - t0) * TARGET_FPS) + 1)
            grid = torch.linspace(t0, t1, n_new, device=device)
            idx = torch.searchsorted(times, grid, right=True).clamp(1, len(times) - 1)
            t_a, t_b = times[idx - 1], times[idx]
            f = ((grid - t_a) / (t_b - t_a + 1e-8)).clamp(0, 1).unsqueeze(1)
            q_a, q_b = quats[idx - 1], quats[idx]
            dot = (q_a * q_b).sum(-1, keepdim=True).clamp(-1, 1)
            q_b = torch.where(dot < 0, -q_b, q_b)
            dot = dot.abs()
            theta = torch.acos(dot)
            s = torch.sin(theta)
            w_a = torch.where(s > 1e-6, torch.sin((1 - f) * theta) / s, 1 - f)
            w_b = torch.where(s > 1e-6, torch.sin(f * theta) / s, f)
            resampled = w_a * q_a + w_b * q_b
            resampled = resampled / resampled.norm(dim=-1, keepdim=True)
            # Quantize: float32 -> float16 halves rotation payload.
            q16 = resampled.to(torch.float16)
            total_out += q16.numel() * 2
            out_chunks.append(q16.cpu().numpy().tobytes())
    blob = b"".join(out_chunks)
    gpu_proof("rotation_input_bytes", total_in, "rotation_output_bytes_fp16", total_out)
    gpu_proof("output_sha256", hashlib.sha256(blob).hexdigest())
    gpu_proof("status", "COMPLETE")
    print("Done. Quantized blob bytes:", len(blob), "(kept in memory; wire to a GLB writer as the next step)")

if __name__ == "__main__":
    main()
