#!/usr/bin/env python3
"""PANTERA entrance v1 — post-production: frames + music -> MP4.
- Upscale 960x540 -> 1920x1080
- Letterbox (2.35:1)
- Color grade: warm fire tones, slight contrast boost
- Mux with pantera_theme_v1.wav (-14 LUFS)
- 30fps, 50.0s, H.264
"""
import subprocess, os, sys

KIT = "/home/hatch/workspace/wh-kit/wh/promo/pantera-entrance-v1"
FRAMES = KIT + "/build/frames_v1"
MUSIC = KIT + "/build/pantera_theme_v1.wav"
OUT = KIT + "/build/pantera_entrance_v1.mp4"

# Verify inputs
frames = sorted([f for f in os.listdir(FRAMES) if f.endswith('.png')])
print(f"frames: {len(frames)} (expect 1500)")
assert len(frames) == 1500, f"expected 1500 frames, got {len(frames)}"
assert os.path.exists(MUSIC), "music missing"

# FFmpeg: upscale, letterbox, grade, mux audio
# Letterbox 2.35:1 on 1920x1080 -> 1920x817 with bars
cmd = [
    "ffmpeg", "-y",
    "-framerate", "30",
    "-i", f"{FRAMES}/f%05d.png",
    "-i", MUSIC,
    "-vf", (
        "scale=1920:1080:flags=lanczos,"  # upscale
        "eq=contrast=1.08:saturation=1.15,"  # grade: warm fire
        "colorchannelmixer=rr=1.05:gg=0.98:bb=0.92,"  # warm shift
        "drawbox=y=0:h=132:w=iw:c=black:t=fill,"  # top bar (2.35:1)
        "drawbox=y=ih-132:h=132:w=iw:c=black:t=fill"  # bottom bar
    ),
    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k",
    "-shortest",
    "-movflags", "+faststart",
    OUT
]
print("running ffmpeg...")
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print(r.stderr[-2000:])
    sys.exit(1)
print(f"done: {OUT}")
print(f"size: {os.path.getsize(OUT)} bytes")

# Verify with ffprobe
r = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries",
     "format=duration:stream=width,height,r_frame_rate,codec_name",
     "-of", "default=noprint_wrappers=1", OUT],
    capture_output=True, text=True
)
print(r.stdout)
