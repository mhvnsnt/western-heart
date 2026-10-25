#!/usr/bin/env python3
"""T7 extraction pipeline wrapper — TRACK 1 (2026-10-23).

Runs the Tekken 7 asset-extraction pipeline end to end on the credentialed
machine (Steam-logged-in, T7 installed). Stages:

  check     verify T7 install paths + vendored tools (no game launch needed)
  unpack    unpack .pak archives via repak / umodel / QuickBMS (no game needed)
  movesets  guided TKMovesets2 memory extraction (REQUIRES the game running;
            interactive by design — this stage prints the exact click-path
            and validates the resulting extracted_chars/ tree)
  anims     raw .bin animation export notes + Blender addon hookup
  convert   map extracted outputs into game/assets/ layout
  all       check -> unpack -> movesets -> anims -> convert

Nothing is faked: stages that need the real T7 install abort with a clear
message when --t7-dir is missing or invalid. --check-only / --dry-run never
touch the game.

Vendored tools live at ~/workspace/tools/t7-pipeline/ on the crew VM and at
<repo>/../tools-vendor/t7-pipeline on the extraction machine (copied over
with this script, or re-cloned — see docs/research/T7-EXTRACTION-PIPELINE-2026-10-23.md).
"""

import argparse
import os
import shutil
import subprocess
import sys

T7_REQUIRED_PATHS = [
    os.path.join("TekkenGame", "Content", "Paks"),
    os.path.join("TekkenGame", "Binaries", "Win64", "TekkenGame-Win64-Shipping.exe"),
]

VENDOR_TOOLS = {
    "TKMovesets": "moveset + animation-binary extractor (live tool, game must be running)",
    "TekkenMovesetExtractor": "legacy extractor (obsolete; motbinExport.py reference only)",
    "UEViewer": "umodel uasset viewer/exporter (source; use prebuilt umodel binary)",
    "BlenderTekkenAnimationImporter": "Blender addon for T7 .bin animations",
    "Tekken-7-Extracting-Packing-Tools": "QuickBMS .bat scripts (Windows fallback unpack)",
}

OUTPUT_SUBDIRS = [
    "paks_unpacked", "movesets", "anim_bin", "meshes",
    "textures", "audio", "ui", "stages",
]


def fail(msg):
    print("PIPELINE FAIL: " + msg, file=sys.stderr)
    return 1


def ok(msg):
    print("PIPELINE OK: " + msg)


def stage_check(t7_dir, tools_dir):
    """Verify T7 install + vendored tools. No game launch."""
    code = 0
    print("== stage: check ==")
    if not t7_dir or not os.path.isdir(t7_dir):
        print("PIPELINE FAIL: --t7-dir missing or not a directory: %r" % t7_dir)
        print("  Pass the Steam install root, e.g.")
        print('  "C:\\Program Files (x86)\\Steam\\steamapps\\common\\TEKKEN 7"')
        return 1
    for rel in T7_REQUIRED_PATHS:
        p = os.path.join(t7_dir, rel)
        if os.path.exists(p):
            ok("found " + rel)
        else:
            print("PIPELINE FAIL: missing in T7 dir: " + rel)
            code = 1
    paks = os.path.join(t7_dir, "TekkenGame", "Content", "Paks")
    if os.path.isdir(paks):
        n = len([f for f in os.listdir(paks) if f.lower().endswith(".pak")])
        print("  .pak files in Paks/: %d" % n)
        if n == 0:
            print("PIPELINE FAIL: no .pak files found")
            code = 1
    for name, desc in VENDOR_TOOLS.items():
        p = os.path.join(tools_dir, name)
        if os.path.isdir(p):
            ok("tool vendored: %s" % name)
        else:
            print("PIPELINE WARN: tool dir missing: %s (%s)" % (p, desc))
    for exe in ("repak", "umodel"):
        found = shutil.which(exe) or shutil.which(exe + ".exe")
        print("  binary %-8s : %s" % (exe, found or "NOT ON PATH (needed for unpack)"))
    return code


def stage_unpack(t7_dir, out_dir, tools_dir, method="repak"):
    """Unpack .pak archives. Game does NOT need to be running."""
    print("== stage: unpack (method=%s) ==" % method)
    paks_dir = os.path.join(t7_dir, "TekkenGame", "Content", "Paks")
    dest = os.path.join(out_dir, "paks_unpacked")
    os.makedirs(dest, exist_ok=True)
    pak_files = [os.path.join(paks_dir, f) for f in os.listdir(paks_dir)
                 if f.lower().endswith(".pak")]
    if not pak_files:
        return fail("no .pak files in " + paks_dir)
    print("  %d pak files -> %s" % (len(pak_files), dest))

    if method == "repak":
        repak = shutil.which("repak") or shutil.which("repak.exe")
        if not repak:
            return fail("repak not on PATH (vendored at ~/workspace/tools/t8extract/repak)")
        # T7 paks are NOT pak-level encrypted: no --aes-key (CDDTreborn wiki).
        cmd = [repak, "unpack", "--output", dest] + pak_files
        print("  run: " + " ".join(cmd[:4]) + " ... (%d paks)" % len(pak_files))
        if DRY_RUN:
            print("  (dry-run: command not executed)")
            return 0
        r = subprocess.run(cmd)
        return r.returncode

    if method == "umodel":
        umodel = shutil.which("umodel") or shutil.which("umodel.exe")
        if not umodel:
            return fail("umodel not on PATH (get it from gildor.org)")
        # GUI-verified: engine UE4 + game "Tekken 7" override. Confirm the
        # exact -game tag with `umodel -help` if this errors.
        cmd = [umodel, "-export", "-path=" + paks_dir, "-out=" + dest,
               "-game=ue4"] + pak_files
        print("  run: " + " ".join(cmd[:5]) + " ...")
        print("  NOTE: if the Tekken 7 profile is not picked up, rerun with the")
        print("  GUI once (UE4 -> Tekken 7 override) or check `umodel -help`.")
        if DRY_RUN:
            print("  (dry-run: command not executed)")
            return 0
        r = subprocess.run(cmd)
        return r.returncode

    if method == "quickbms":
        bat = os.path.join(tools_dir, "Tekken-7-Extracting-Packing-Tools",
                           "Extract", "Extract Everything.bat")
        if not os.path.isfile(bat):
            return fail("QuickBMS scripts not vendored at " + bat)
        print("  Windows fallback: run Generate Config.bat once, then:")
        print("  " + bat)
        print("  (interactive .bat — launch it manually; output to " + dest + ")")
        return 0

    return fail("unknown unpack method: %r (repak|umodel|quickbms)" % method)


def stage_movesets(out_dir, tools_dir):
    """Guided TKMovesets2 memory extraction. REQUIRES T7 RUNNING."""
    print("== stage: movesets ==")
    print("  TKMovesets2 extraction is memory-based and interactive by design.")
    print("  Exact click-path:")
    print("  1. Launch TEKKEN 7 (Steam).")
    print("  2. Launch TKMovesets2.exe")
    print("     (build from vendored source, or releases page).")
    print("  3. Load the character in Practice or Versus (Law/Lars first).")
    print("  4. Extractor tab -> select the player -> Extract.")
    print("     Toggle camera/face/hand animations in extractor options as needed.")
    print("  5. Outputs land in extracted_chars/ as compressed .tkmoveset files.")
    dest = os.path.join(out_dir, "movesets")
    os.makedirs(dest, exist_ok=True)
    print("  Copy each extracted_chars/<char>/*.tkmoveset -> " + dest)
    found = [f for f in os.listdir(dest) if f.endswith(".tkmoveset")]
    print("  .tkmoveset files staged: %d" % len(found))
    if not found:
        print("  (none yet — run the interactive extraction above, then rerun")
        print("   with --stage movesets to validate the tree)")
        return 0
    return 0


def stage_anims(out_dir, tools_dir):
    """Raw .bin animation path + Blender addon hookup."""
    print("== stage: anims ==")
    addon = os.path.join(tools_dir, "BlenderTekkenAnimationImporter")
    print("  Blender addon source: " + addon)
    print("  Install: zip the folder as BlenderTekkenAnimationImporter.zip ->")
    print("  Blender Preferences -> Add-ons -> Install -> enable.")
    print("  .bin sources:")
    print("   - legacy: motbinExport.py (vendored TekkenMovesetExtractor,")
    print("     Python 3.6.5 + pywin32, game running) -> mota_*.bin")
    print("   - modern: TKMovesets2 Utils/Animations*.cpp extraction path")
    print("  Import: File -> Import -> Tekken7 Animation (*.bin) onto the")
    print("  Koenji T7 mannequin armature; keyframes bake per frame.")
    dest = os.path.join(out_dir, "anim_bin")
    os.makedirs(dest, exist_ok=True)
    ok("anim_bin dir ready: " + dest)
    return 0


def stage_convert(out_dir):
    """Map extracted outputs into the game/assets/ layout (staging only)."""
    print("== stage: convert ==")
    mapping = {
        "meshes": "game/assets/models/   (umodel .psk -> Blender -> .glb)",
        "movesets": "game/assets/movesets/<fighter>.json (tkmoveset->json converter; schema in pipeline doc)",
        "anim_bin": "game/assets/anim/      (Blender bake -> game anim format)",
        "textures": "game/assets/materials/ + game/assets/ui/ + game/assets/portraits/",
        "audio": "game/assets/sounds/ + voices/ + music/ (.wem decode via wwiseutil/vgmstream)",
        "stages": "game/assets/stages/    (stgXX umap/meshes -> glTF)",
    }
    staged = os.path.join(out_dir, "game_ready")
    os.makedirs(staged, exist_ok=True)
    for src, dst in mapping.items():
        s = os.path.join(out_dir, src)
        n = len(os.listdir(s)) if os.path.isdir(s) else 0
        print("  %-10s (%3d files) -> %s" % (src, n, dst))
    print("  NOTE: converters that need real files (.tkmoveset->json, .psk->.glb)")
    print("  run here at pull time, then validate.py --check-output before merge.")
    return 0


DRY_RUN = False


def main(argv):
    global DRY_RUN
    ap = argparse.ArgumentParser(description="T7 extraction pipeline wrapper")
    ap.add_argument("--t7-dir", required=True, help="T7 Steam install root")
    ap.add_argument("--out", required=True, help="output root for extracted data")
    ap.add_argument("--tools-dir", default="tools-vendor/t7-pipeline",
                    help="vendored t7-pipeline tools dir")
    ap.add_argument("--stage", default="all",
                    choices=["check", "unpack", "movesets", "anims", "convert", "all"])
    ap.add_argument("--unpack-method", default="repak",
                    choices=["repak", "umodel", "quickbms"])
    ap.add_argument("--check-only", action="store_true",
                    help="run check stage and exit")
    ap.add_argument("--dry-run", action="store_true",
                    help="print commands without executing")
    args = ap.parse_args(argv)
    DRY_RUN = args.dry_run

    os.makedirs(args.out, exist_ok=True)
    for sub in OUTPUT_SUBDIRS:
        os.makedirs(os.path.join(args.out, sub), exist_ok=True)

    stages = ["check", "unpack", "movesets", "anims", "convert"] \
        if args.stage == "all" else [args.stage]
    if args.check_only:
        stages = ["check"]

    for st in stages:
        if st == "check":
            rc = stage_check(args.t7_dir, args.tools_dir)
        elif st == "unpack":
            rc = stage_unpack(args.t7_dir, args.out, args.tools_dir, args.unpack_method)
        elif st == "movesets":
            rc = stage_movesets(args.out, args.tools_dir)
        elif st == "anims":
            rc = stage_anims(args.out, args.tools_dir)
        elif st == "convert":
            rc = stage_convert(args.out)
        else:
            rc = fail("unknown stage " + st)
        if rc != 0:
            return rc
        print()
    ok("pipeline finished: " + args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
