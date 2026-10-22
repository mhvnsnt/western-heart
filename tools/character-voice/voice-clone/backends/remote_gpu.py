"""Remote-GPU backend — Chatterbox runs on a GPU box, weights live THERE.

The model weights are downloaded and cached on the REMOTE machine only
(RunPod pod, Kaggle, or any SSH-reachable GPU box). This VM never sees a
weight file: the spec + reference audio go up, finished WAVs come back.

One-time remote setup (run ONCE on the GPU box — weights download there):
    pip install chatterbox-tts torchaudio
    # weights land in the REMOTE ~/.cache/huggingface — never here.

Per run, this backend:
  1. rsyncs the voice spec + reference audio to the remote workdir
  2. writes + executes the remote runner (template below) over SSH
  3. scp's the finished WAVs back

Needs: WH_GPU_SSH (e.g. "user@gpu-box") or --host flag; ssh key auth.
"""
import json
import os
import subprocess
import tempfile

REMOTE_RUNNER = r'''
"""Runs ON THE GPU BOX. Downloads Chatterbox weights THERE (remote disk only)."""
import json, sys, torchaudio
from chatterbox.tts import ChatterboxTTS

spec_path, out_dir = sys.argv[1], sys.argv[2]
spec = json.load(open(spec_path))
params = spec.get("chatterbox_params", {})
ref = (spec.get("clone") or {}).get("reference_audio")

# Weights download to the REMOTE ~/.cache — this machine's disk, not the VM's.
model = ChatterboxTTS.from_pretrained(device="cuda")
if ref:
    # zero-shot clone from the direction-matched reference
    model = model  # chatterbox voices via prepare_conditionals on ref wav

import torch
for line in spec["lines"]:
    wav = model.generate(
        line["text"],
        audio_prompt_path=ref if ref else None,
        exaggeration=float(params.get("exaggeration", 0.5)),
        cfg_weight=float(params.get("cfg_weight", 0.5)),
    )
    torchaudio.save(f"{out_dir}/{line['id']}.raw.wav", wav, 24000)
print(json.dumps({"ok": True, "lines": len(spec["lines"])}))
'''


class RemoteGpuError(Exception):
    pass


class RemoteGpuBackend:
    name = "remote_gpu"

    def __init__(self, host=None):
        self.host = host or os.environ.get("WH_GPU_SSH")
        if not self.host:
            raise RemoteGpuError(
                "no remote GPU host — pass --host user@gpu-box or set WH_GPU_SSH. "
                "See docs/VOICE-CLONING-PIPELINE.md §3.")
        self.remote_dir = "/tmp/wh-voice"

    def _ssh(self, *cmd, check=True):
        r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
                            self.host, "--"] + list(cmd),
                           capture_output=True, text=True, timeout=600)
        if check and r.returncode != 0:
            raise RemoteGpuError(f"ssh failed: {r.stderr[:400]}")
        return r

    def _scp_to(self, local, remote):
        r = subprocess.run(["scp", local, f"{self.host}:{remote}"],
                           capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            raise RemoteGpuError(f"scp up failed: {r.stderr[:300]}")

    def _scp_from(self, remote, local):
        r = subprocess.run(["scp", f"{self.host}:{remote}", local],
                           capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            raise RemoteGpuError(f"scp down failed: {r.stderr[:300]}")

    def _ref_path(self, ref_audio):
        # reference audio may be a local path (uploaded) or remote path
        if ref_audio and os.path.isfile(ref_audio):
            self._scp_to(ref_audio, f"{self.remote_dir}/ref.wav")
            return f"{self.remote_dir}/ref.wav"
        return ref_audio  # URL or already-remote path; runner resolves

    def generate(self, text, ref_audio, params):
        raise RemoteGpuError(
            "use generate_batch() — the remote GPU backend batches all lines "
            "in one SSH session (one GPU spin-up per fighter, not per line).")

    def generate_batch(self, lines, ref_audio, params, workdir):
        """lines: [(clip_id, text)]. Returns {clip_id: wav_bytes}."""
        self._ssh("mkdir", "-p", self.remote_dir, check=True)
        spec_remote = {
            "chatterbox_params": params,
            "clone": {"reference_audio": self._ref_path(ref_audio)},
            "lines": [{"id": cid, "text": t} for cid, t in lines],
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(spec_remote, f)
            spec_local = f.name
        runner_local = spec_local + ".runner.py"
        with open(runner_local, "w") as f:
            f.write(REMOTE_RUNNER)
        try:
            self._scp_to(spec_local, f"{self.remote_dir}/spec.json")
            self._scp_to(runner_local, f"{self.remote_dir}/runner.py")
            r = self._ssh("mkdir", "-p", f"{self.remote_dir}/out",
                          "&&", "python3", f"{self.remote_dir}/runner.py",
                          f"{self.remote_dir}/spec.json", f"{self.remote_dir}/out")
            print(r.stdout[-500:])
            out = {}
            for cid, _ in lines:
                local = os.path.join(workdir, f"{cid}.raw.wav")
                self._scp_from(f"{self.remote_dir}/out/{cid}.raw.wav", local)
                with open(local, "rb") as f:
                    out[cid] = f.read()
            return out
        finally:
            for p in (spec_local, runner_local):
                try:
                    os.remove(p)
                except OSError:
                    pass
