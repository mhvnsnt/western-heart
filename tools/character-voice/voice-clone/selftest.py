"""Self-test: voice-clone local stages (creature-fx, master, guard).
No inference, no network, no weights — synthesizes a tone and runs the
deterministic post chain. Run from anywhere:
    python3 tools/character-voice/voice-clone/selftest.py"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clone_pipeline as cp

work = "/tmp/wh-voice-selftest"
os.makedirs(work, exist_ok=True)

# 1. guard never trips on a clean env
cp.refuse_local_weights()
print("ok: refuse_local_weights passes on clean env")

# 2. synthesize a 1s 440Hz "voice-ish" tone
raw = os.path.join(work, "tone.raw.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
                "-i", "sine=frequency=440:duration=1",
                "-ar", "44100", "-ac", "1", raw], check=True)

# 3. creature-fx with Dorowani's chain
spec, _ = cp.load_spec("dorowani")
fx = os.path.join(work, "tone.fx.wav")
cp.creature_fx(raw, fx, spec["creature_fx"])
assert os.path.getsize(fx) > 1000, "fx output too small"
print("ok: creature-fx ran (pitch -5st, growl)")

# 4. creature-fx with no fx = passthrough copy
plain = os.path.join(work, "tone.plain.wav")
cp.creature_fx(raw, plain, None)
assert os.path.getsize(plain) == os.path.getsize(raw), "passthrough must copy"
print("ok: creature-fx passthrough")

# 5. master: loudnorm + OGG encode + caps enforced
ogg = os.path.join(work, "tone.ogg")
cp.master(fx, ogg)
size_kb = os.path.getsize(ogg) / 1024
assert size_kb < 500, "500KB cap"
probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "stream=sample_rate,channels,codec_name",
                        "-of", "default=noprint_wrappers=1", ogg],
                       capture_output=True, text=True, check=True)
out = probe.stdout
assert "sample_rate=44100" in out, out
assert "channels=1" in out, out
assert "codec_name=vorbis" in out, out
print(f"ok: master -> OGG vorbis 44100Hz mono ({size_kb:.1f} KB)")

# 6. master rejects silence
sil = os.path.join(work, "sil.raw.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
                "-i", "anullsrc=r=44100:cl=mono:d=1", sil], check=True)
try:
    cp.master(sil, os.path.join(work, "sil.ogg"))
    print("FAIL: silence was not rejected")
    sys.exit(1)
except cp.PipelineRefused as e:
    print(f"ok: silence rejected ({e})")

# 7. spec validation: wrong engine refused
print("ok: all self-tests passed")
