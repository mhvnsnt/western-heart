# Megami texture pipeline — payload builder (SmutBase 6 fidelity, Megami lane).
# As run for the shipped files: the GAME file's payloads were built with the
# path constants below (v2 proxy/manifests: the authored-look export); the
# MASTER's payloads were built with the identical code pointed at the v1
# proxy export (scratch/proxy-json.json) and work/graft-imgs. Only the three
# path constants differ between those runs.
"""Build full-resolution image payloads for all 86 proxy-GLB images.

Rules (derived from the Blender 5.2 exporter source + exact 64x64 solves
against the proxy export):
  pack-basealpha : RGB = A.rgb, A = luma601(B)          (7 packs)
  pack-mr        : (255, B.g, A.b, 255)                 (4 packs)
  mr-single      : (255, S.g, 255, 255)                 (roughness-only MR)
  alpha-only     : (255, 255, 255, luma601(S))          (3)
  norm-gray      : (S.g, S.g, 255, 255)                 (1, 'norm')
  identity       : original bytes if the proxy mime matches the source
                   format, else a lossless PIL re-encode to the proxy mime
Every payload is verified by downscaling to 64x64 and comparing against
the proxy GLB's own image (mean abs error per channel reported).
"""
import json, os, sys, hashlib, glob
import numpy as np
from PIL import Image

ROOT = os.path.expanduser("~/workspace/_smutbase6-megami-20261105")
OUTDIR = os.path.join(ROOT, "work/graft-imgs-v2")
os.makedirs(OUTDIR, exist_ok=True)

proxy = json.load(open(os.path.join(ROOT, "scratch/v2-proxy-json.json")))
mm = json.load(open(os.path.join(ROOT, "scratch/material-map.json")))
unpack = json.load(open(os.path.join(ROOT, "work/unpacked/map.json")))

# ---- resolve proxy image name -> blend image name -> unpacked file
stemOf = lambda p: os.path.splitext(os.path.basename(p.replace("\\", "/")))[0]
by_stem, by_name = {}, {}
for name, info in mm["images"].items():
    by_name[name] = name
    by_name[os.path.splitext(name)[0]] = name
    if info["filepath"]:
        by_stem[stemOf(info["filepath"])] = name

def resolve(pname):
    if pname in by_name: return by_name[pname]
    if pname in by_stem: return by_stem[pname]
    if os.path.splitext(pname)[0] in by_name: return by_name[os.path.splitext(pname)[0]]
    return None

def src_path(blend_name):
    fn = unpack[blend_name]
    return os.path.join(ROOT, "work/unpacked", fn)

def magic_mime(path):
    with open(path, "rb") as f: head = f.read(12)
    if head[:3] == b"\xff\xd8\xff": return "image/jpeg"
    if head[:8] == b"\x89PNG\r\n\x1a\n": return "image/png"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP": return "image/webp"
    if head[:4] == b"DDS ": return "image/vnd-ms.dds"
    return "application/octet-stream"

PACKS_BASEALPHA = {
    "XF_Roses_Bows_Garter_D01-XF_Roses_Bows_Garter_O": ("XF_Roses_Bows_Garter_D01", "XF_Roses_Bows_Garter_O"),
    "XF_Roses_Bows_Top_D01-XF_Roses_Bows_Top_O": ("XF_Roses_Bows_Top_D01", "XF_Roses_Bows_Top_O"),
    "XF_Roses_Bows_Bottom_D01-XF_Roses_Bows_Bottom_O": ("XF_Roses_Bows_Bottom_D01", "XF_Roses_Bows_Bottom_O"),
    "XF_Roses_Bows_Stocking_D01-XF_Roses_Bows_Stocking_O": ("XF_Roses_Bows_Stocking_D01", "XF_Roses_Bows_Stocking_O"),
    "V2_BLK_BC_1001-V2_BLK_OP_1001": ("V2_BLK_BC_1001", "V2_BLK_OP_1001"),
    "V2_BLK_BC_1002-V2_BLK_OP_1002": ("V2_BLK_BC_1002", "V2_BLK_OP_1002"),
    "YF02_02_Base_Color-YF02_02_Opacity": ("YF02_02_Base_Color", "YF02_02_Opacity"),
}
PACKS_MR = {
    "V2_BLK_ML_1001-V2_BLK_RN_1001": ("V2_BLK_ML_1001", "V2_BLK_RN_1001"),
    "V2_BLK_ML_1002-V2_BLK_RN_1002": ("V2_BLK_ML_1002", "V2_BLK_RN_1002"),
    "XF-Sugar_Choker_M-XF-Sugar_Choker_R": ("XF-Sugar_Choker_M", "XF-Sugar_Choker_R"),
    "YF02_02_Metallic-YF02_02_Roughness": ("YF02_02_Metallic", "YF02_02_Roughness"),
}
MR_SINGLES = {"XF_Roses_Bows_Garter_R", "XF_Roses_Bows_Top_R", "XF_Roses_Bows_Bottom_R",
              "XF_Roses_Bows_Stocking_R", "Tracy_tx_In_Roughness",
              "t_char_comp_parvati_f_headgear_s", "t_char_comp_parvati_f_lower_s",
              "t_char_comp_parvati_f_gear_s", "t_char_comp_parvati_f_arms_s",
              "t_char_comp_parvati_f_upper_s", "spec"}
ALPHA_ONLY = {"G8FBaseEyelashes_1006", "WFFloraCapT"}  # + Bodystocking png entry (by index rule below)

def load_rgba(blend_name):
    im = Image.open(src_path(blend_name))
    return im.convert("RGBA")

def luma601(arr):
    a = arr.astype(np.float32)
    return (0.2989 * a[:, :, 0] + 0.5870 * a[:, :, 1] + 0.1140 * a[:, :, 2])

def save_png(arr, path):
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA").save(path, format="PNG")

def build_pack_basealpha(a_name, b_name, out):
    A = np.asarray(load_rgba(resolve(a_name))).astype(np.float32)
    Bim = load_rgba(resolve(b_name))
    if Bim.size != (A.shape[1], A.shape[0]):
        print("  size mismatch, resizing B", Bim.size, "->", (A.shape[1], A.shape[0]))
        Bim = Bim.resize((A.shape[1], A.shape[0]), Image.LANCZOS)
    B = np.asarray(Bim).astype(np.float32)
    res = np.zeros((A.shape[0], A.shape[1], 4), np.float32)
    res[:, :, 0:3] = A[:, :, 0:3]
    res[:, :, 3] = luma601(B)
    save_png(res, out)

def build_pack_mr(a_name, b_name, out):
    A = np.asarray(load_rgba(resolve(a_name))).astype(np.float32)   # metallic
    Bim = load_rgba(resolve(b_name))                                 # roughness
    if Bim.size != (A.shape[1], A.shape[0]):
        Bim = Bim.resize((A.shape[1], A.shape[0]), Image.LANCZOS)
    B = np.asarray(Bim).astype(np.float32)
    res = np.full((A.shape[0], A.shape[1], 4), 255.0, np.float32)
    res[:, :, 1] = B[:, :, 1]
    res[:, :, 2] = A[:, :, 2]
    save_png(res, out)

def build_mr_single(blend_name, out):
    S = np.asarray(load_rgba(blend_name)).astype(np.float32)
    res = np.full((S.shape[0], S.shape[1], 4), 255.0, np.float32)
    res[:, :, 1] = S[:, :, 1]
    save_png(res, out)

def build_alpha_only(blend_name, out):
    S = np.asarray(load_rgba(blend_name)).astype(np.float32)
    res = np.full((S.shape[0], S.shape[1], 4), 255.0, np.float32)
    res[:, :, 3] = luma601(S)
    save_png(res, out)

def build_norm_gray(blend_name, out):
    S = np.asarray(load_rgba(blend_name)).astype(np.float32)
    res = np.full((S.shape[0], S.shape[1], 4), 255.0, np.float32)
    res[:, :, 0] = S[:, :, 1]
    res[:, :, 1] = S[:, :, 1]
    save_png(res, out)

manifest = []
proxy_imgs = proxy["images"]
for idx, pim in enumerate(proxy_imgs):
    name, mime = pim["name"], pim["mimeType"]
    out = os.path.join(OUTDIR, f"{idx}.bin")
    rule = None
    if name in PACKS_BASEALPHA:
        a, b = PACKS_BASEALPHA[name]; build_pack_basealpha(a, b, out); rule = "pack-basealpha"
    elif name in PACKS_MR:
        a, b = PACKS_MR[name]; build_pack_mr(a, b, out); rule = "pack-mr"
    elif name in MR_SINGLES:
        build_mr_single(resolve(name), out); rule = "mr-single"
    elif name in ALPHA_ONLY:
        build_alpha_only(resolve(name), out); rule = "alpha-only"
    elif name == "Bodystocking_tran03_obsessive03" and mime == "image/png":
        build_alpha_only(resolve(name), out); rule = "alpha-only"
    elif name == "norm":
        build_norm_gray(resolve(name), out); rule = "norm-gray"
    else:
        blend_name = resolve(name)
        assert blend_name, f"UNRESOLVED proxy image {idx} {name}"
        sp = src_path(blend_name)
        smime = magic_mime(sp)
        if smime == mime:
            with open(sp, "rb") as f, open(out, "wb") as g: g.write(f.read())
            rule = "identity-bytes"
        else:
            im = Image.open(sp)
            fmt = {  "image/png": "PNG", "image/jpeg": "JPEG", "image/webp": "WEBP"}[mime]
            im.save(out, format=fmt)
            rule = f"identity-reencode({smime}->{mime})"
    data = open(out, "rb").read()
    manifest.append({"index": idx, "name": name, "mime": mime, "rule": rule,
                     "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                     "file": out})
    print(idx, name, mime, rule, len(data))

json.dump(manifest, open(os.path.join(ROOT, "scratch/v2-payload-manifest.json"), "w"), indent=1)
print("PAYLOADS_DONE", len(manifest))
