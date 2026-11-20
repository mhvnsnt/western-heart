# nw-unirig-run2 v17: skin prediction + merge (assumes v1 produced stage_out/nightwolf_skeleton.fbx
# in THIS kernel's input via kernel_sources, or re-runs skeleton first if missing)
# v17 (2026-11-08 ~16:45 CST): v4 died at BEAT 349s on the BOX ALLOWLIST
# probe itself — add_safe_globals lets the Box global be NAMED, but torch
# 2.11's weights_only unpickler still cannot rebuild a Box (dict subclass:
# "Can only SETITEM for dict..."). The allowlist alone can never work.
# Fix: wrap torch.load in the v10 sitecustomize to force weights_only=False
# for this kernel's processes. The checkpoint comes from the trusted
# upstream HF repo (VAST-AI/UniRig) — torch's own error message option (1).
# The probe now proves the override end-to-end instead of the allowlist.
# RECONSTRUCTED 2026-11-08 ~11:35 CST: the local v7 copy was zeroed by a failed
# EDQUOT write during the v8 edit (file left 0 bytes). Rebuilt from the
# Kaggle-pulled v2 driver (the run2 kernel was never re-pushed past v2 —
# watch_run2 gates on run1 COMPLETE, which never happened in v3–v7) plus
# run1 v8's shared blocks verbatim (TBB split, PyG, spconv, v7 include, v8
# arch). v3–v8 changes re-applied: split extract/inference, npz guard on the
# input's own dir, TBB probe, pristine-extract restore before merge, bpy-first
# merge wrapper. Verified by compile only — run2 has never executed past v2.
import subprocess, sys, os, shutil, glob, time
W = "/kaggle/working"
OUT = os.path.join(W, "out")
os.makedirs(OUT, exist_ok=True)
T0 = time.time()
def beat(msg):
    print(f"BEAT {time.time()-T0:.0f}s {msg}", flush=True)
def sh(cmd, cwd=None, fatal=False, env=None):
    print("+ " + cmd, flush=True)
    e = dict(os.environ); e.update(env or {})
    r = subprocess.run(cmd, shell=True, cwd=cwd, env=e)
    if fatal and r.returncode != 0:
        beat(f"FATAL rc={r.returncode}: {cmd}")
        sync(); sys.exit(1)
    return r.returncode
def sync():
    subprocess.run(f"cp -r {W}/UniRig/experiments {OUT}/ 2>/dev/null; cp -rf {W}/stage_out/* {OUT}/ 2>/dev/null; true", shell=True)

beat(f"probe py={sys.version.split()[0]}")
sh("nvidia-smi; python3 -c 'import torch; print(\"TORCH\", torch.__version__, torch.version.cuda, torch.cuda.get_device_name(0) if torch.cuda.is_available() else None, torch.cuda.get_device_capability(0) if torch.cuda.is_available() else None)'")
sh("df -h /kaggle/working | tail -1; free -g | head -2; ls /kaggle/input/")

# v4: SKEL/STAT discovery BEFORE extract (skeleton arrives via kernel_sources).
# v15.1 (2026-11-08 ~16:02 CST): run2 kernel v2 died in 27 s — STAT glob found
# nothing. Root cause, proven by the v2-era log AND the v2 push's own log:
# Kaggle mounts datasets at /kaggle/input/datasets/<owner>/<slug>/, NOT at
# /kaggle/input/<slug>/ (the v2 log lists the real path outright:
# /kaggle/input/datasets/marsfmmg/nw-rig-input/nightwolf_static.glb). The
# old non-recursive glob /kaggle/input/nw-rig-input/*.glb could never match.
# Fix: recursive globs for both inputs + a diagnostic find so the next log
# shows the true layout instead of guessing.
sh("find /kaggle/input -name '*.glb' -o -name '*.fbx' 2>/dev/null | head -20")
SKEL = glob.glob("/kaggle/input/**/nightwolf_skeleton.fbx", recursive=True)
STAT = glob.glob("/kaggle/input/**/nightwolf_static.glb", recursive=True)
beat(f"skeleton inputs: {SKEL}; static: {STAT}")
if not SKEL or not STAT:
    beat("FATAL: skeleton or static GLB missing from /kaggle/input"); sync(); sys.exit(1)
SKEL, STAT = SKEL[0], STAT[0]
# The skeleton FBX is the extract/run.py --input, and UniRig writes the npz
# NEXT TO that input (absolute-path join discards output_dataset_dir — the
# v4 finding). /kaggle/input is read-only, so copy both inputs into the
# writable stage_in first and use the copies.
stage_in = os.path.join(W, "stage_in"); os.makedirs(stage_in, exist_ok=True)
SKEL_W = os.path.join(stage_in, "nightwolf_skeleton.fbx")
STAT_W = os.path.join(stage_in, "nightwolf_static.glb")
shutil.copy(SKEL, SKEL_W)
shutil.copy(STAT, STAT_W)
beat(f"inputs staged: {SKEL_W}; {STAT_W}")

# clone upstream UniRig (official repo)
if not os.path.isdir(os.path.join(W, "UniRig")):
    sh("git clone --depth 1 https://github.com/VAST-AI-Research/UniRig.git", cwd=W, fatal=True)
sh("git -C UniRig rev-parse HEAD; git -C UniRig log -1 --format=%ci", cwd=W)
UR = os.path.join(W, "UniRig")

# --- v4 TBB fix: bpy FIRST in bpy processes, lazy ONLY on the torch path ---
# v3 lesson (2026-11-08 08:03 CST): the lazy patch fixed the torch inference
# import (TBB-ISOLATION probe passed), but it BROKE the extract step:
# generate_skin.sh runs extract as its own `python -m src.data.extract`
# process, where bpy now loads LAST (after numpy/scipy/trimesh/
# fast_simplification pull in a conflicting libtbb) and dies at clean_bpy()
# with the same libopenvdb ImportError. v2 proved extract works with bpy
# FIRST (module-top import, line 1). So this driver SPLITS
# generate_skin.sh into its two documented steps and patches BETWEEN
# them: extract runs on the pristine file (bpy first), then the lazy patch is
# applied, then the torch inference runs. Runtime patch to the vendored
# upstream file; no model/joint/weight code touched. Do NOT re-push v3 as-is.
import re
_ext = os.path.join(UR, "src", "data", "extract.py")
shutil.copy(_ext, _ext + ".orig")  # pristine, for restore/verification
assert open(_ext).read().startswith("import bpy, os\n"), "extract.py header changed upstream — patch does not apply"

def _lazy_bpy_patch():
    _src = open(_ext).read()
    assert _src.startswith("import bpy, os\n"), "extract.py header changed upstream — lazy-bpy patch does not apply"
    _src = _src.replace("import bpy, os\n", "import os\n", 1)
    for _fn in ("load", "clean_bpy", "process_mesh", "process_armature"):
        # NOTE: the def header may carry a `-> ...:` return annotation
        # (process_armature does), so anchor on the closing paren + optional
        # annotation, NOT on `):`.
        _m = re.search(r"(def %s\(.*?\)[^:]*:\n)" % _fn, _src, re.DOTALL)
        assert _m, f"def {_fn} not found in extract.py"
        _src = _src[:_m.end()] + "    import bpy  # lazy: keeps bpy out of torch processes (TBB ABI clash)\n" + _src[_m.end():]
    open(_ext, "w").write(_src)
    assert "import bpy, os" not in open(_ext).read()
    beat("extract.py lazy-bpy patch applied (load/clean_bpy/process_mesh/process_armature)")

# deps (skip bpy/flash_attn pins from requirements; handled explicitly)
sh(f"{sys.executable} -m pip install -q transformers==4.51.3 python-box einops omegaconf pytorch_lightning lightning addict timm fast-simplification trimesh open3d pyrender huggingface_hub wandb psutil numpy==1.26.4 scipy")
beat("deps base installed")
pyv = sys.version_info
# 2026-11-08: bpy 4.5.0 has NO cp313 wheel on PyPI (only 5.1.0-5.2.3 exist), which is
# why v1 failed with ModuleNotFoundError. 5.2.3 is cp313-only and requires numpy>=2.2,
# so pip will upgrade numpy past the 1.26.4 pin above; the fatal checks below catch any
# fallout loudly instead of swallowing it.
bpyver = "5.2.3" if (pyv.major, pyv.minor) == (3, 13) else ("4.2.0" if (pyv.major, pyv.minor) == (3, 11) else None)
if bpyver:
    rc = sh(f"{sys.executable} -m pip install -q bpy=={bpyver}")
    beat(f"bpy=={bpyver} rc={rc}")
else:
    beat(f"no bpy mapping for python {pyv.major}.{pyv.minor}")
sh("python3 -c 'import bpy; print(\"BPY OK\", bpy.app.version_string)'", fatal=True)

# v4: torch_cluster + torch_scatter were missing in v3 (ModuleNotFoundError:
# sal_perceiver.py:28 `from torch_cluster import fps`; PTv3Object.py /
# unirig_skin.py import torch_scatter). Wheels come from the PyG index keyed
# to the kernel's exact torch build (2.11.0+cu130 on T4); --only-binary fails
# fast if no wheel exists instead of burning time on a source build.
def _pyg_install():
    import torch
    tv = torch.__version__
    url = f"https://data.pyg.org/whl/torch-{tv}.html"
    beat(f"pyg index: {url}")
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                        "--only-binary", ":all:",
                        "torch-cluster", "torch-scatter", "-f", url])
    return r.returncode
_rc = _pyg_install()
if _rc != 0:
    beat(f"FATAL: torch-cluster/torch-scatter install rc={_rc}"); sync(); sys.exit(1)
sh("python3 -c 'import torch_cluster, torch_scatter; print(\"PYG OK\", torch_cluster.__version__)'", fatal=True)

# v6: spconv was missing in v5 (ModuleNotFoundError at PTv3Object.py:6
# `import spconv.pytorch as spconv`, ~19 s into inference). No spconv-cu130
# wheel exists on PyPI (404); spconv-cu124 2.3.8 has a cp313 wheel and its
# core_cc.so bundles its own cudart (RPATH $ORIGIN/../spconv_cu124.libs,
# hashed libcudart .so.12.4.127 — verified by readelf on the real wheel),
# so no system CUDA 12.4 is needed. pip resolves cumm-cu124 0.7.11
# (spconv needs <0.8.0,>=0.7.11; cp313 wheel exists) automatically.
# Probe the import BEFORE extract so a failure exits in seconds instead of
# after the ~15-min extract + ~35-min inference. No torch pin anywhere in
# spconv's deps, so torch 2.11.0+cu130 is untouched.
_rc = sh(f"{sys.executable} -m pip install -q spconv-cu124==2.3.8")
if _rc != 0:
    beat(f"FATAL: spconv install rc={_rc}"); sync(); sys.exit(1)
# v8: the v7 tensorview fix worked (build reached [27/814]) but cumm's JIT
# arch list includes compute_52 (Maxwell), which CUDA 13.0's nvcc rejects
# ("nvcc fatal: Unsupported gpu architecture 'compute_52'"). The T4 is
# sm_75 — restrict the JIT to 7.5 only (also cuts the 814-step build down).
for _k, _v in (("TORCH_CUDA_ARCH_LIST", "7.5"), ("CUDAARCHS", "75")):
    os.environ[_k] = _v
beat("cuda arch list restricted to sm_75")
# v7: spconv installs but its import JIT-builds core_cc via pccm/ccimport,
# and the v6 build died on missing tensorview headers. The headers DO ship
# in the cumm wheel (cumm/include/tensorview/, 103 files incl.
# pybind_utils.h + core/all.h — verified by wheel inspection); the build's
# -I flags just never include that dir. (The PyPI `tensorview` 0.4.1 package
# is an unrelated ML-viz library, NOT the headers — do not install it.)
# Fix: point the compiler at the bundled headers before importing spconv.
# CPLUS_INCLUDE_PATH/CPATH propagate through sh() to every subprocess, so
# the later run.py inference inherits them too.
import sysconfig
_cumm_inc = os.path.join(sysconfig.get_paths()["purelib"], "cumm", "include")
assert os.path.isfile(os.path.join(_cumm_inc, "tensorview", "pybind_utils.h")), "cumm tensorview headers not found"
for _k in ("CPLUS_INCLUDE_PATH", "CPATH"):
    os.environ[_k] = _cumm_inc + os.pathsep + os.environ.get(_k, "")
beat(f"cumm include path set: {_cumm_inc}")
# v9: same SPCONV_DISABLE_JIT fix as run1 (env vars don't reach pccm).
os.environ["SPCONV_DISABLE_JIT"] = "1"
beat("spconv JIT disabled (prebuilt core_cc)")
# v10: same cumm.core_cc pre-import fix as run1 (tv::Tensor registrar).
os.environ["CUMM_DISABLE_JIT"] = "1"
_sc_dir = os.path.join(os.getcwd(), "nw_sitecustomize")
os.makedirs(_sc_dir, exist_ok=True)
open(os.path.join(_sc_dir, "sitecustomize.py"), "w").write(
    "# v10: pre-register tv::Tensor before spconv.core_cc init needs it.\n"
    "try:\n    import cumm.core_cc  # noqa\n"
    "except Exception:\n    pass\n"
    "# v16: the UniRig skin checkpoint stores a box.box.Box config object\n"
    "# and Lightning restores it via torch.load(weights_only=True) (torch\n"
    "# 2.11), which refuses the global unless allowlisted (v3 died on\n"
    "# exactly this at BEAT 421s). The checkpoint comes from the trusted\n"
    "# upstream HF repo (VAST-AI/UniRig); Box is a plain data container\n"
    "# (python-box) — narrow allowlist, NOT weights_only=False. Runs at\n"
    "# interpreter startup in every python process on this PYTHONPATH,\n"
    "# so run.py inherits it before Lightning loads the checkpoint.\n"
    "try:\n"
    "    import torch as _torch\n"
    "    from box import Box as _Box\n"
    "    _torch.serialization.add_safe_globals([_Box])\n"
    "except Exception:\n"
    "    pass\n"
    "# v17: torch 2.11 weights_only unpickler cannot rebuild a box.box.Box\n"
    "# (dict subclass — SETITEM blocked) even when the global is\n"
    "# allowlisted (v16 proved this: the probe died with 'Can only\n"
    "# SETITEM for dict...'). The UniRig skin checkpoint stores its\n"
    "# config as a Box, so Lightning's checkpoint restore can never load\n"
    "# it weights_only. Force weights_only=False for torch.load calls in\n"
    "# this kernel's processes. The checkpoint comes from the trusted\n"
    "# upstream HF repo (VAST-AI/UniRig) — the same source whose code we\n"
    "# already clone and execute — so full unpickling is the documented\n"
    "# option (1) from torch's own error message. Narrow scope: this\n"
    "# kernel only runs UniRig inference. sitecustomize runs at\n"
    "# interpreter startup, before run.py imports Lightning, so the\n"
    "# wrapper is in place when cloud_io binds torch.load.\n"
    "try:\n"
    "    import torch as _torch2\n"
    "    _orig_torch_load = _torch2.load\n"
    "    def _load_trusted(*_a, **_kw):\n"
    "        _kw['weights_only'] = False\n"
    "        return _orig_torch_load(*_a, **_kw)\n"
    "    _torch2.load = _load_trusted\n"
    "except Exception:\n"
    "    pass\n")
os.environ["PYTHONPATH"] = _sc_dir + os.pathsep + os.environ.get("PYTHONPATH", "")
beat("cumm.core_cc pre-import armed (sitecustomize)")
sh("python3 -c 'import cumm.core_cc; print(\"CUMM_CC OK\")'")
sh("python3 -c 'import spconv.pytorch; import spconv; print(\"SPCONV OK\", spconv.__version__)'", fatal=True)
# v17: FATAL round-trip probe — the exact v3/v4 failure mode, now proving
# the torch.load override. Save a Box via torch.save, reload with
# weights_only=True (what Lightning does for the skin checkpoint). The
# sitecustomize wrapper forces weights_only=False, so this must load; if
# the wrapper did not apply, it dies here in seconds with the same
# UnpicklingError instead of after extract.
sh("python3 -c 'import torch; from box import Box; torch.save({\"cfg\": Box({\"a\": 1})}, \"/tmp/nw_box_probe.pt\"); d = torch.load(\"/tmp/nw_box_probe.pt\", weights_only=True); assert d[\"cfg\"][\"a\"] == 1; print(\"BOX ALLOWLIST OK\")'", fatal=True)

# v13: same flash-attn shim as run1 — DO NOT build it (FA2 kernels are
# sm80/sm90 only; the T4 is sm_75, so even a successful build could not
# execute). UniRig calls MHA with use_flash_attn=False (default), so the
# real MHA code runs its pure-torch CrossAttention inner class. The stub
# package carries the real mha.py verbatim from the v2.8.3 tag
# (hash-pinned) plus the real utils/distributed.py.
import hashlib, urllib.request
_FA_DIR = os.path.join(os.getcwd(), "fa_shim")
_shim_pkg = os.path.join(_FA_DIR, "flash_attn")
os.makedirs(os.path.join(_shim_pkg, "modules"), exist_ok=True)
os.makedirs(os.path.join(_shim_pkg, "utils"), exist_ok=True)
def _fa_fetch(url, dst, sha256):
    urllib.request.urlretrieve(url, dst)
    _h = hashlib.sha256(open(dst, "rb").read()).hexdigest()
    assert _h == sha256, f"fa-shim {dst} hash mismatch: {_h} != {sha256}"
    beat(f"fa-shim fetched {os.path.basename(dst)} sha256 OK")
_fa_fetch("https://raw.githubusercontent.com/Dao-AILab/flash-attention/v2.8.3/flash_attn/modules/mha.py",
          os.path.join(_shim_pkg, "modules", "mha.py"),
          "881de9d2e0d6cb1ac406e2d138eaeb62f7193f42055bbfa5d302b2671b638305")
_fa_fetch("https://raw.githubusercontent.com/Dao-AILab/flash-attention/v2.8.3/flash_attn/utils/distributed.py",
          os.path.join(_shim_pkg, "utils", "distributed.py"),
          "aa17326d15edb25b2cb95f4b61a432dfb85a3da3ed925338614303c7d52f9e74")
open(os.path.join(_shim_pkg, "__init__.py"), "w").write(
    "# v13: pure-python flash_attn stub — no CUDA kernels.\n"
    "__version__ = \"2.8.3-shim\"\n"
    "flash_attn_kvpacked_func = None\n"
    "flash_attn_qkvpacked_func = None\n"
    "flash_attn_varlen_kvpacked_func = None\n"
    "flash_attn_varlen_qkvpacked_func = None\n"
    "flash_attn_with_kvcache = None\n")
open(os.path.join(_shim_pkg, "modules", "__init__.py"), "w").write("")
open(os.path.join(_shim_pkg, "utils", "__init__.py"), "w").write("")
os.environ["PYTHONPATH"] = _FA_DIR + os.pathsep + os.environ.get("PYTHONPATH", "")
beat("fa-shim on PYTHONPATH")
sh("python3 -c 'from flash_attn.modules.mha import MHA; import torch; m = MHA(embed_dim=256, num_heads=8, cross_attn=True); print(\"SHIM MHA params:\", sorted(n for n, _ in m.named_parameters())); q = torch.randn(1, 16, 256); kv = torch.randn(1, 24, 256); y = m(q, x_kv=kv); print(\"SHIM MHA forward OK:\", tuple(y.shape))'", fatal=True)

# skin task config copy: PTv3 encoder flash OFF via the system's own config surface
mc = os.path.join(UR, "configs", "model")
sk = open(os.path.join(mc, "unirig_skin.yaml")).read()
assert "mesh_encoder:" in sk
sk2 = sk.replace("mesh_encoder:\n  # vertex groups are handled in model\n  __target__: ptv3obj",
                 "mesh_encoder:\n  # vertex groups are handled in model\n  __target__: ptv3obj\n  enable_flash: False")
assert sk2 != sk, "mesh_encoder anchor not found"
open(os.path.join(mc, "unirig_skin_noflash.yaml"), "w").write(sk2)
tc = os.path.join(UR, "configs", "task")
ts = open(os.path.join(tc, "quick_inference_unirig_skin.yaml")).read()
open(os.path.join(tc, "nw_skin_noflash.yaml"), "w").write(ts.replace("unirig_skin", "unirig_skin_noflash"))
beat("skin noflash configs written")

os.makedirs(os.path.join(W, "stage_out"), exist_ok=True)

# STEP 1 — extract, on the PRISTINE extract.py (bpy FIRST, v2-proven).
# generate_skin.sh step 1, replicated exactly (force_override true is the
# skin script's documented arg; input = the staged skeleton copy, since
# UniRig writes the npz NEXT TO the input and /kaggle/input is read-only).
rc = sh(f"bash launch/inference/extract.sh --config configs/data/quick_inference.yaml --require_suffix obj,fbx,FBX,dae,glb,gltf,vrm --force_override true --num_runs 1 --faces_target_count 50000 --input {SKEL_W} --output_dir tmp", cwd=UR, fatal=True)
beat(f"extract rc={rc}")
# v5 npz guard (same absolute-input mechanism as run1; the input lives in
# stage_in, so its own directory is the third glob).
_npz = glob.glob(os.path.join(UR, "tmp", "**", "raw_data.npz"), recursive=True) + glob.glob(os.path.join(UR, "stage_in", "**", "raw_data.npz"), recursive=True) + glob.glob(os.path.join(os.path.dirname(SKEL_W), "**", "raw_data.npz"), recursive=True)
beat(f"extract npz: {_npz}")
if not _npz:
    beat("FATAL: extract produced no raw_data.npz"); sync(); sys.exit(1)

# STEP 2 — lazy patch, only now that the bpy process is done.
_lazy_bpy_patch()

# v15: the FBX export must not import bpy into the torch process.
# v14 proved the shim + inference work end-to-end (SHIM MHA forward OK,
# extract rc=0, skeleton prediction reached ar.py write_on_batch_end) and
# died ONLY at src/data/exporter.py:348 _export_fbx `import bpy` inside the
# torch process — the same TBB clash as v3, now on the export side. The
# lazy-bpy patch covered extract.py only; exporter.py was never patched.
# Fix (same split pattern as the v4 extract/inference split): replace
# _export_fbx with a delegator that serializes its args (all numpy /
# lists / scalars — verified own-eyes in the vendored exporter.py) and
# runs the REAL upstream export in a fresh bpy-FIRST subprocess. The
# helper loads a PRISTINE copy of exporter.py by file path, so the
# patched method never recurses. The subprocess env is SANITIZED:
# PYTHONPATH is dropped, because the v10 sitecustomize on PYTHONPATH
# pre-imports cumm.core_cc (-> torch -> libtbb) at interpreter startup
# in EVERY python process — which would reintroduce the clash before
# the helper's own `import bpy` runs. No model/joint/weight code
# touched; dependency/export plumbing only. Run2 needs this too:
# skin.py:292 calls exporter._export_fbx directly in the torch process.
_exp = os.path.join(UR, "src", "data", "exporter.py")
_exp_pristine = os.path.join(W, "exporter_pristine.py")
shutil.copy(_exp, _exp_pristine)
os.environ["NW_EXPORTER_PRISTINE"] = _exp_pristine
_fbx_helper = os.path.join(W, "export_fbx_bpy.py")
os.environ["NW_FBX_HELPER"] = _fbx_helper
open(_fbx_helper, "w").write(
    "# v15: bpy-FIRST FBX export subprocess. No torch in this process, ever.\n"
    "# Loads the PRISTINE upstream exporter.py by file path (NOT the patched\n"
    "# in-tree copy) so the patched _export_fbx delegator never recurses.\n"
    "import bpy  # FIRST — before numpy/open3d and any sitecustomize-adjacent import\n"
    "import sys, os, json, importlib.util\n"
    "import numpy as np\n"
    "_npz_path, _json_path, _out_path = sys.argv[1:4]\n"
    "_spec = importlib.util.spec_from_file_location('nw_exporter_pristine', os.environ['NW_EXPORTER_PRISTINE'])\n"
    "_mod = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_mod)\n"
    "_d = np.load(_npz_path)\n"
    "_meta = json.load(open(_json_path))\n"
    "_exp = _mod.Exporter()\n"
    "_exp._export_fbx(path=_out_path, vertices=_d['vertices'] if 'vertices' in _d else None, joints=_d['joints'], skin=_d['skin'] if 'skin' in _d else None, parents=_meta['parents'], names=_meta['names'], faces=_d['faces'] if 'faces' in _d else None, extrude_size=_meta['extrude_size'], group_per_vertex=_meta['group_per_vertex'], add_root=_meta['add_root'], do_not_normalize=_meta['do_not_normalize'], use_extrude_bone=_meta['use_extrude_bone'], use_connect_unique_child=_meta['use_connect_unique_child'], extrude_from_parent=_meta['extrude_from_parent'], tails=_d['tails'] if 'tails' in _d else None)\n"
    "assert os.path.isfile(_out_path) and os.path.getsize(_out_path) > 0, 'helper produced no FBX'\n"
    "print(f'FBX SUBPROCESS OK: {_out_path} {os.path.getsize(_out_path)} bytes', flush=True)\n")
def _exporter_fbx_patch():
    _src = open(_exp).read()
    _m = re.search(r"    def _export_fbx\(.*?    def _export_render\(", _src, re.DOTALL)
    assert _m, "_export_fbx.._export_render anchor not found in exporter.py"
    _delegator = '''    def _export_fbx(
        self,
        path: str,
        vertices,
        joints,
        skin,
        parents,
        names,
        faces=None,
        extrude_size: float=0.03,
        group_per_vertex: int=-1,
        add_root: bool=False,
        do_not_normalize: bool=False,
        use_extrude_bone: bool=True,
        use_connect_unique_child: bool=True,
        extrude_from_parent: bool=True,
        tails=None,
    ):
        """v15 delegator: serialize args, run the real upstream export in a fresh bpy-first subprocess (see header comment)."""
        import subprocess, sys as _sys, json as _json
        _npz = path + ".export.npz"
        _meta = {"parents": parents, "names": names, "extrude_size": extrude_size, "group_per_vertex": group_per_vertex, "add_root": add_root, "do_not_normalize": do_not_normalize, "use_extrude_bone": use_extrude_bone, "use_connect_unique_child": use_connect_unique_child, "extrude_from_parent": extrude_from_parent}
        _arrays = {"joints": np.asarray(joints)}
        if vertices is not None:
            _arrays["vertices"] = np.asarray(vertices)
        if skin is not None:
            _arrays["skin"] = np.asarray(skin)
        if faces is not None:
            _arrays["faces"] = np.asarray(faces)
        if tails is not None:
            _arrays["tails"] = np.asarray(tails)
        np.savez(_npz, **_arrays)
        with open(path + ".export.json", "w") as _f:
            _json.dump(_meta, _f)
        _env = dict(os.environ)
        _env.pop("PYTHONPATH", None)
        _env.pop("PYTHONSTARTUP", None)
        _r = subprocess.run([_sys.executable, os.environ["NW_FBX_HELPER"], _npz, path + ".export.json", path], capture_output=True, text=True, env=_env)
        print(_r.stdout, end="")
        print(_r.stderr, end="", file=_sys.stderr)
        if _r.returncode != 0 or not (os.path.exists(path) and os.path.getsize(path) > 0):
            raise RuntimeError(f"v15 fbx subprocess export failed rc={_r.returncode} path={path}")
'''
    _src = _src[:_m.start()] + _delegator + "    def _export_render(" + _src[_m.end():]
    open(_exp, "w").write(_src)
    _check = open(_exp).read()
    assert _check.count("def _export_fbx") == 1, "exporter patch: _export_fbx count != 1"
    assert "bpy.ops.export_scene.fbx" not in _check, "exporter patch: original bpy export still in-tree"
    beat("exporter.py _export_fbx delegator applied (v15 subprocess export)")
_exporter_fbx_patch()
sh("python3 -m py_compile " + _exp, fatal=True)
# v15 FATAL probe: exercise the whole subprocess export path on a tiny
# synthetic skeleton BEFORE burning ~10 min on inference. The probe runs
# the helper directly with the same sanitized env the delegator uses.
import numpy as _np, json as _json
_probe_npz = os.path.join(W, "stage_out", "probe_skeleton.export.npz")
_probe_json = os.path.join(W, "stage_out", "probe_skeleton.export.json")
_probe_out = os.path.join(W, "stage_out", "probe_skeleton.fbx")
_np.savez(_probe_npz, joints=_np.array([[0., 0., 0.], [0., 0., 0.5], [0., 0., 1.0]], dtype=_np.float32), vertices=_np.array([[0., 0., 0.], [0.1, 0., 0.], [0.1, 0.1, 0.], [0., 0.1, 0.]], dtype=_np.float32), faces=_np.array([[0, 1, 2], [0, 2, 3]]))
_json.dump({"parents": [None, 0, 1], "names": ["Root", "Spine", "Head"], "extrude_size": 0.03, "group_per_vertex": -1, "add_root": False, "do_not_normalize": False, "use_extrude_bone": True, "use_connect_unique_child": True, "extrude_from_parent": True}, open(_probe_json, "w"))
_probe_env = dict(os.environ)
_probe_env.pop("PYTHONPATH", None)
_probe_env.pop("PYTHONSTARTUP", None)
_r = subprocess.run([sys.executable, _fbx_helper, _probe_npz, _probe_json, _probe_out], capture_output=True, text=True, env=_probe_env)
print(_r.stdout, end="")
print(_r.stderr, end="", file=sys.stderr)
if _r.returncode != 0 or not (os.path.isfile(_probe_out) and os.path.getsize(_probe_out) > 0):
    beat("FATAL: FBX subprocess export probe failed"); sync(); sys.exit(1)
beat("FBX SUBPROCESS OK (probe)")

# v3: prove the TBB clash is gone BEFORE burning ~35 min on inference.
# torch loads first (exactly as UniRig run.py does), then the extract import
# must succeed WITHOUT loading bpy into the process. Fatal if it doesn't.
sh("python3 -c \"import torch, sys; from src.data.extract import get_files; assert 'bpy' not in sys.modules, 'bpy leaked into torch process'; print('TBB-ISOLATION OK: torch+extract import, bpy not loaded')\"", cwd=UR, fatal=True)

# STEP 3 — skin inference, generate_skin.sh step 2, replicated exactly.
rc = sh(f"python run.py --task=configs/task/nw_skin_noflash.yaml --seed=12345 --input={SKEL_W} --output=/kaggle/working/stage_out/nightwolf_skin.fbx --npz_dir=tmp --data_name=raw_data.npz", cwd=UR, fatal=True)
beat(f"skin inference rc={rc}")
SKIN_OUT = "/kaggle/working/stage_out/nightwolf_skin.fbx"
if not (os.path.isfile(SKIN_OUT) and os.path.getsize(SKIN_OUT) > 0):
    beat("FATAL: generate_skin produced no skin FBX"); sync(); sys.exit(1)

# v4: RESTORE pristine extract.py before merge (merge.py imports open3d
# BEFORE bpy — the merge wrapper below loads bpy first instead).
shutil.copy(_ext + ".orig", _ext)
assert open(_ext).read().startswith("import bpy, os\n"), "extract.py restore failed"
beat("extract.py restored to pristine")

# STEP 4 — merge via a bpy-first wrapper (merge.py line 21 `import bpy` sits
# AFTER open3d, so running merge.sh directly risks the same TBB clash from
# the other side; the wrapper imports bpy first, then runs the module with
# merge.sh's exact args).
_merge_wrapper = os.path.join(W, "merge_bpy_first.py")
open(_merge_wrapper, "w").write(
    "import bpy  # noqa: F401  (bpy first — its libtbb must win over open3d's)\n"
    "import runpy, sys, os\n"
    "sys.path.insert(0, os.getcwd())  # v15: runpy needs UniRig on sys.path (script dir is /kaggle/working, not cwd)\n"
    "sys.argv = ['merge', '--require_suffix=obj,fbx,FBX,dae,glb,gltf,vrm', '--num_runs=1', '--id=0',"
    f" '--source={SKIN_OUT}', '--target={STAT_W}', '--output=/kaggle/working/stage_out/nightwolf_rigged.glb']\n"
    "runpy.run_module('src.inference.merge', run_name='__main__')\n")
# v15: run the wrapper with PYTHONPATH emptied — the driver's env carries
# the v10 sitecustomize dir, whose cumm.core_cc pre-import (-> torch ->
# libtbb) runs at interpreter startup in EVERY python process and would
# reintroduce the TBB clash before the wrapper's own `import bpy`. Merge
# needs nothing from PYTHONPATH (no flash_attn, no cumm in merge.py).
rc = sh(f"{sys.executable} merge_bpy_first.py", cwd=UR, fatal=True, env={"PYTHONPATH": ""})
beat(f"merge rc={rc}")
RIGGED_OUT = "/kaggle/working/stage_out/nightwolf_rigged.glb"
if not (os.path.isfile(RIGGED_OUT) and os.path.getsize(RIGGED_OUT) > 0):
    beat("FATAL: merge produced no rigged GLB"); sync(); sys.exit(1)
sh("ls -la /kaggle/working/stage_out/")
sync()
beat("DONE v17")
