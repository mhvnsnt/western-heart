#!/usr/bin/env python3
"""phone_cleanup_chain.py — phone-recorded fighter line -> broadcast-ready.

Chain: DeepFilterNet (de-reverb + denoise) -> resemble-enhance (neural polish)
       -> ffmpeg loudnorm (I=-16, TP=-1.5, LRA=11).

Install: pip install deepfilternet==0.5.6 resemble-enhance==0.0.1
(or run cape-jones production/pipeline/audio-2026/kaggle_setup_audio2026.py)

Usage: python3 phone_cleanup_chain.py raw_line.wav clean_line.wav [--skip-enhance]
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile


def run(cmd):
    print(f"$ {cmd}")
    r = subprocess.run(cmd, shell=True)
    if r.returncode != 0:
        sys.exit(f"FAILED: {cmd}")
    return True


def main():
    ap = argparse.ArgumentParser(description="phone line -> broadcast-ready")
    ap.add_argument("input", help="raw phone-recorded wav")
    ap.add_argument("output", help="cleaned wav out")
    ap.add_argument("--skip-enhance", action="store_true",
                    help="skip resemble-enhance stage")
    ap.add_argument("--keep-intermediate", action="store_true")
    ns = ap.parse_args()

    if shutil.which("deepfilternet") is None:
        sys.exit("ERROR: deepfilternet not installed (pip install deepfilternet==0.5.6)")

    tmp = tempfile.mkdtemp(prefix="wh_voice_")
    stage1 = os.path.join(tmp, "stage1_df.wav")
    stage2 = os.path.join(tmp, "stage2_re.wav")

    print("== stage 1: DeepFilterNet (de-reverb + denoise) ==")
    run(f"deepfilternet --noisy-audio {ns.input} --output {stage1}")

    if not ns.skip_enhance:
        print("== stage 2: resemble-enhance (neural polish) ==")
        run(f"{sys.executable} -m resemble_enhance.inference "
            f"--input {stage1} --output {stage2}")
        polished = stage2
    else:
        polished = stage1

    print("== stage 3: loudnorm (broadcast I=-16) ==")
    run(f"ffmpeg -y -v error -i {polished} "
        f"-af loudnorm=I=-16:TP=-1.5:LRA=11 {ns.output}")

    if not ns.keep_intermediate:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"wrote {ns.output}")


if __name__ == "__main__":
    main()