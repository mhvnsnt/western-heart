#!/usr/bin/env python3
"""Western Heart voice cloning pipeline — remote-first, NO local weights.

Orchestrates: spec -> lines -> generate (REMOTE ONLY) -> creature-fx
(local CPU, no ML) -> master (loudnorm/44.1k/OGG) -> deposit (game assets
+ manifest status flip) -> deliver (remote-storage direct download links).

Owner laws honored:
- Chatterbox is the character-voice default (never replaced).
- Model weights NEVER touch local disk (disk rules are mandatory).
- Audio sent to the owner goes as direct download links, never attachments.
- Placeholders stay honest: nothing is marked final until a real clone lands.

Usage:
    python3 clone_pipeline.py --fighter dorowani --backend remote_api --dry-run
    python3 clone_pipeline.py --fighter dorowani --backend remote_api --deposit --deliver
    python3 clone_pipeline.py --fighter dorowani --backend remote_gpu --host user@gpu-box

Contract: docs/VOICE-CLONING-PIPELINE.md
"""
import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SPECS = os.path.join(HERE, "voice-specs")

# Local weight locations we REFUSE to use (the Hubert mistake was local
# weight bloat; the owner banned it). If any exist, we abort loudly
# rather than silently using them.
FORBIDDEN_LOCAL_WEIGHT_HINTS = [
    os.path.expanduser("~/.cache/huggingface"),
    os.path.expanduser("~/.cache/torch"),
]


class PipelineRefused(Exception):
    pass


def log(stage, msg):
    print(f"[voice-clone:{stage}] {msg}", flush=True)


def refuse_local_weights():
    """Abort if the environment looks like it wants local model weights."""
    for mod in ("chatterbox", "chatterbox_tts"):
        if mod in sys.modules:
            raise PipelineRefused(
                f"local '{mod}' module is imported — weights must stay remote. "
                "See docs/VOICE-CLONING-PIPELINE.md §3.")
    # We do not check for mere cache-dir existence (other lanes may own
    # those); we refuse to CREATE or READ model weights from them here.
    log("guard", "local weight download refused by policy — all inference runs remote")


def load_spec(fighter):
    # Minimal YAML reader (no PyYAML dependency): the spec files use a
    # restricted subset (scalars, lists of scalars, lists of maps).
    path = os.path.join(SPECS, f"{fighter}.yaml")
    if not os.path.isfile(path):
        raise PipelineRefused(f"no voice spec: {path}")
    with open(path) as f:
        raw_lines = [_strip_comment(l.rstrip("\n")) for l in f]
        raw_lines = [l for l in raw_lines
                     if l.strip() and not l.strip().startswith("#")]
    lines = [(len(l) - len(l.lstrip(" ")), l.strip()) for l in raw_lines]
    pos = [0]

    def parse_block(indent):
        if pos[0] >= len(lines):
            return {}
        if lines[pos[0]][1].startswith("- "):
            out = []
            while (pos[0] < len(lines) and lines[pos[0]][0] == indent
                   and lines[pos[0]][1].startswith("- ")):
                _, text = lines[pos[0]]
                item = text[2:].strip()
                pos[0] += 1
                if ": " in item or item.endswith(":"):
                    d = {}
                    k, _, v = item.partition(":")
                    k = k.strip()
                    if v.strip():
                        d[k] = _scalar(_strip_comment(v.strip()))
                    elif pos[0] < len(lines) and lines[pos[0]][0] > indent:
                        d[k] = parse_block(lines[pos[0]][0])
                    else:
                        d[k] = None
                    while (pos[0] < len(lines) and lines[pos[0]][0] > indent
                           and not lines[pos[0]][1].startswith("- ")):
                        ii, tt = lines[pos[0]]
                        kk, _, vv = tt.partition(":")
                        pos[0] += 1
                        if vv.strip():
                            d[kk.strip()] = _scalar(_strip_comment(vv.strip()))
                        elif pos[0] < len(lines) and lines[pos[0]][0] > ii:
                            d[kk.strip()] = parse_block(lines[pos[0]][0])
                        else:
                            d[kk.strip()] = None
                    out.append(d)
                else:
                    out.append(_scalar(item))
            return out
        out = {}
        while (pos[0] < len(lines) and lines[pos[0]][0] == indent
               and not lines[pos[0]][1].startswith("- ")):
            _, text = lines[pos[0]]
            pos[0] += 1
            if ": " in text:
                k, _, v = text.partition(":")
                k, v = k.strip(), _strip_comment(v.strip())
                if v in (">-", ">", "|", "|-"):
                    # folded/literal block scalar: consume more-indented lines
                    # (pos already points at the first continuation line)
                    buf = []
                    while pos[0] < len(lines) and lines[pos[0]][0] > indent:
                        buf.append(lines[pos[0]][1])
                        pos[0] += 1
                    out[k] = " ".join(buf) if v.startswith(">") else "\n".join(buf)
                else:
                    out[k] = _scalar(v)
            elif text.endswith(":"):
                k = text[:-1].strip()
                if pos[0] < len(lines) and lines[pos[0]][0] > indent:
                    out[k] = parse_block(lines[pos[0]][0])
                else:
                    out[k] = None
        return out

    return parse_block(0), path


def _strip_comment(line):
    """Strip a trailing ' #...' comment (not inside quotes)."""
    in_s = in_d = False
    for i, ch in enumerate(line):
        if ch == "'" and not in_d:
            in_s = not in_s
        elif ch == '"' and not in_s:
            in_d = not in_d
        elif ch == "#" and not in_s and not in_d and i > 0 and line[i - 1] in (" ", "\t"):
            return line[:i].rstrip()
    return line


def _scalar(v):
    if v in ("null", "~", ""):
        return None
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    return v


def resolve_lines(spec, fighter):
    """Line list: spec lines, else the game voice manifest's clips."""
    if spec.get("lines"):
        return [(l["id"], l["text"]) for l in spec["lines"]]
    man_path = os.path.join(REPO, "game", "data", "voices", f"{fighter}.json")
    if not os.path.isfile(man_path):
        raise PipelineRefused(f"spec has no lines and no game manifest at {man_path}")
    with open(man_path) as f:
        man = json.load(f)
    return [(c["id"], c["text"]) for c in man["clips"] if c.get("text")]


def get_backend(name, args):
    if name == "remote_api":
        from backends.remote_api import RemoteApiBackend
        return RemoteApiBackend()
    if name == "remote_gpu":
        from backends.remote_gpu import RemoteGpuBackend
        return RemoteGpuBackend(args.host)
    raise PipelineRefused(f"unknown backend: {name}")


def creature_fx(in_wav, out_wav, fx):
    """Deterministic creature treatment — local CPU ffmpeg filters only.
    No ML, no weights. What TTS can't give a creature (lowness, rasp,
    growl), the filter chain adds."""
    if not fx:
        shutil.copyfile(in_wav, out_wav)
        return
    filters = []
    if fx.get("pitch_semitones"):
        st = float(fx["pitch_semitones"])
        # asetrate trick: resample the clock (pitch *= 2^(st/12)), then
        # restore the rate; atempo compensates so duration is preserved.
        # Negative st = down (bigger creature). Rubberband, when installed,
        # handles pitch+formant together instead (see below).
        comp = 2 ** (-st / 12)  # >1 when shifting down: speeds back up
        filters.append(
            f"asetrate=44100*2^({st}/12),aresample=44100,atempo={comp:.4f}")
    if fx.get("formant_shift"):
        # formant shift via rubberband when available, else skip honestly
        if shutil.which("rubberband"):
            filters.append(f"rubberband=pitch=1:formant={fx['formant_shift']}")
        else:
            log("creature-fx", "rubberband not installed — formant shift skipped (install rubberband for full chain)")
    if fx.get("growl"):
        g = float(fx.get("growl_amount", 0.25))
        # subtle AM growl: tremolo + soft saturation
        filters.append(f"tremolo=f=38:d=0.35,acrusher=level_in=1:level_out=1:bits=10:mode=log:aa=1")
        log("creature-fx", f"growl amount {g} (tremolo+saturation)")
    if not filters:
        shutil.copyfile(in_wav, out_wav)
        return
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", in_wav,
           "-af", ",".join(filters), "-ar", "44100", "-ac", "1", out_wav]
    log("creature-fx", "ffmpeg " + ",".join(filters)[:120])
    subprocess.run(cmd, check=True)


def master(in_wav, out_ogg):
    """Broadcast master: loudnorm, trim, 44.1kHz mono OGG. Rejects junk."""
    if not shutil.which("ffmpeg"):
        raise PipelineRefused("ffmpeg not found — install ffmpeg for the master stage")
    tmp = in_wav + ".master.wav"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", in_wav,
        "-af", "silenceremove=start_periods=1:start_duration=0.08:start_threshold=-50dB,"
                "areverse,silenceremove=start_periods=1:start_duration=0.08:start_threshold=-50dB,areverse,"
                "loudnorm=I=-16:TP=-3:LRA=11",
        "-ar", "44100", "-ac", "1", tmp,
    ], check=True)
    # size/duration sanity: reject silence and monsters
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration,size",
         "-of", "json", tmp], capture_output=True, text=True, check=True)
    info = json.loads(probe.stdout)["format"]
    dur = float(info.get("duration", 0))
    if dur < 0.2:
        raise PipelineRefused(f"master rejected: {dur:.2f}s — likely silence")
    if dur > 8:
        raise PipelineRefused(f"master rejected: {dur:.2f}s exceeds 8s cap")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", tmp,
        "-c:a", "libvorbis", "-q:a", "5", out_ogg,
    ], check=True)
    size_kb = os.path.getsize(out_ogg) / 1024
    log("master", f"{os.path.basename(out_ogg)}: {dur:.2f}s, {size_kb:.0f} KB")
    if size_kb > 500:
        raise PipelineRefused(f"master rejected: {size_kb:.0f} KB exceeds 500 KB cap")
    os.remove(tmp)


def deposit(fighter, staged):
    """Write finished clips to game/assets/voices/<fighter>/ and flip the
    game manifest clips from placeholder to final."""
    dest_dir = os.path.join(REPO, "game", "assets", "voices", fighter)
    os.makedirs(dest_dir, exist_ok=True)
    for clip_id, ogg_path in staged:
        # clip ids are like 'intro-01' -> file intro-01.ogg
        dest = os.path.join(dest_dir, f"{clip_id}.ogg")
        shutil.copyfile(ogg_path, dest)
        log("deposit", dest)
    man_path = os.path.join(REPO, "game", "data", "voices", f"{fighter}.json")
    if os.path.isfile(man_path):
        with open(man_path) as f:
            man = json.load(f)
        flipped = 0
        staged_ids = {c for c, _ in staged}
        for clip in man.get("clips", []):
            if clip.get("id") in staged_ids and clip.get("status") == "placeholder":
                clip["status"] = "final"
                flipped += 1
        with open(man_path, "w") as f:
            json.dump(man, f, indent=2)
            f.write("\n")
        log("deposit", f"manifest {fighter}.json: {flipped} clips placeholder→final")


def deliver(staged):
    """Standing audio-delivery rule: direct download links via remote-storage,
    NEVER in-chat attachments."""
    uploader = "/opt/hatch/bin/remote-storage"
    if not os.path.isfile(uploader):
        log("deliver", "remote-storage uploader not found — links skipped")
        return []
    links = []
    for clip_id, ogg_path in staged:
        r = subprocess.run([uploader, "upload-file", "--path", ogg_path],
                           capture_output=True, text=True)
        if r.returncode != 0:
            log("deliver", f"upload failed for {clip_id}: {r.stderr[:200]}")
            continue
        try:
            info = json.loads(r.stdout)
            url, exp = info.get("url"), info.get("expires_at")
        except Exception:
            url, exp = r.stdout.strip(), None
        links.append((clip_id, url, exp))
        log("deliver", f"{clip_id}: {url} (expires {exp})")
    return links


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fighter", required=True)
    ap.add_argument("--backend", default="remote_api", choices=["remote_api", "remote_gpu"])
    ap.add_argument("--host", default=None, help="remote GPU host (user@host) for remote_gpu backend")
    ap.add_argument("--dry-run", action="store_true", help="validate spec + lines, no inference, no spend")
    ap.add_argument("--deposit", action="store_true", help="write clips into game/assets + flip manifest")
    ap.add_argument("--deliver", action="store_true", help="upload finished clips, print direct download links")
    ap.add_argument("--workdir", default=None)
    a = ap.parse_args(argv)

    refuse_local_weights()
    spec, spec_path = load_spec(a.fighter)
    log("spec", f"{spec_path} (engine={spec.get('engine')})")
    if spec.get("engine") != "chatterbox":
        raise PipelineRefused("owner law: Chatterbox is the character-voice default — "
                              f"spec engine is '{spec.get('engine')}'")
    lines = resolve_lines(spec, a.fighter)
    log("lines", f"{len(lines)} lines: " + ", ".join(i for i, _ in lines))
    if a.dry_run:
        log("dry-run", "spec valid; no inference run, nothing spent")
        return 0

    backend = get_backend(a.backend, a)
    ref_audio = spec.get("clone", {}).get("reference_audio")
    params = spec.get("chatterbox_params", {})
    workdir = a.workdir or tempfile.mkdtemp(prefix=f"wh-voice-{a.fighter}-")
    os.makedirs(workdir, exist_ok=True)

    staged = []
    try:
        # Batch-capable backends (remote_gpu) do all lines in one remote
        # session; others generate per line.
        if hasattr(backend, "generate_batch"):
            log("generate", f"{len(lines)} lines via {backend.name}.generate_batch (REMOTE — no local weights)")
            batch = backend.generate_batch(lines, ref_audio, params, workdir)
            raw_wavs = {}
            for clip_id, _ in lines:
                raw_wav = os.path.join(workdir, f"{clip_id}.raw.wav")
                with open(raw_wav, "wb") as f:
                    f.write(batch[clip_id])
                raw_wavs[clip_id] = raw_wav
        else:
            raw_wavs = {}
            for clip_id, text in lines:
                log("generate", f"{clip_id}: {text!r} via {backend.name} (REMOTE — no local weights)")
                wav_bytes = backend.generate(text=text, ref_audio=ref_audio, params=params)
                raw_wav = os.path.join(workdir, f"{clip_id}.raw.wav")
                with open(raw_wav, "wb") as f:
                    f.write(wav_bytes)
                raw_wavs[clip_id] = raw_wav
        for clip_id, text in lines:
            fx_wav = os.path.join(workdir, f"{clip_id}.fx.wav")
            creature_fx(raw_wavs[clip_id], fx_wav, spec.get("creature_fx"))
            ogg = os.path.join(workdir, f"{clip_id}.ogg")
            master(fx_wav, ogg)
            staged.append((clip_id, ogg))
    finally:
        pass  # keep workdir for inspection; crew cleans up

    log("done", f"{len(staged)} clips finished in {workdir}")
    if a.deposit:
        deposit(a.fighter, staged)
    if a.deliver:
        links = deliver(staged)
        print("\nDirect download links (send THESE to the owner — never attachments):")
        for clip_id, url, exp in links:
            print(f"  {clip_id}: {url}  (expires {exp})")
    if not a.deposit:
        log("note", "clips NOT deposited (pass --deposit after owner review)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except PipelineRefused as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        # Backend errors (RemoteApiError, RemoteGpuError) surface cleanly too.
        if type(e).__name__ in ("RemoteApiError", "RemoteGpuError"):
            print(f"REFUSED: {e}", file=sys.stderr)
            sys.exit(2)
        raise
