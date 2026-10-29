# Cape arenas GPU job pack (prepared — NOT run)

Blanket GPU order 2026-10-24 20:26 CDT: GPU works everything. This pack
is ready for the coordinator's GPU session; NO job in it has run yet,
because its inputs do not exist yet (house GLB export + beach pack
download are both pending — see `docs/arenas/cape-jones-arenas.md`).
No time, size, or speedup is claimed here. Every job run through
`cape-gpu-jobs.py` records nvidia-smi + torch.cuda proof, input bytes,
output bytes, wall time, AND CPU-baseline time in its report JSON —
measured at run time, never claimed in advance.

## Queue (in order, jobs queue continuously; Kaggle first, Colab overflow)

Kaggle T4 x2 notebook: https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
(Colab as overflow — switch, never stop.)

1. Beach prop GLBs (when the itch pack lands): `cape-gpu-jobs.py` over
   `game/assets/stages/cape-beach/*.glb` → optimized outputs beside
   the inputs. Pinned flags (Lane 5 policy): `-cc` always; `-kn` ONLY
   for skinned fighters — stage props are unskinned, so no `-kn`;
   `-tc` (KTX2/BasisU) ONLY if the output measures smaller, per asset;
   simplification allow-list only, never a skinned fighter blind.
   Do NOT touch `burger-fixed.glb` (re-export from source only).
2. House GLB (when `stages/cape-house/living-room.glb` lands): same
   batch, same flags (unskinned room props).
3. Real-ESRGAN upscale batch for the beach pano + prop textures (Lane
   5's `tools/gltfpack/gpu/esrgan-upscale.py` pattern: CUDA required,
   fails loudly without weights). Inputs pending.
4. Card pre-renders for both arenas (thumb atlas tiles:
   `assets/stages/thumbs/atlas.png` + `atlas.json`) + LOD generation
   for the beach prop set, same pipeline, same proof fields.

## Running

```bash
# GPU run (records nvidia-smi + torch.cuda proof + timings):
python3 tools/cape-arenas-gpu/cape-gpu-jobs.py \
  --manifest tools/cape-arenas-gpu/jobs.example.json \
  --out tools/cape-arenas-gpu/report.json
# CPU baseline for the same manifest (attach both times to the report):
python3 tools/cape-arenas-gpu/cape-gpu-jobs.py \
  --manifest tools/cape-arenas-gpu/jobs.example.json \
  --out tools/cape-arenas-gpu/report-cpu.json --cpu-baseline
```

A GPU step with no GPU present fails loudly (exit non-zero) instead of
silently running a CPU substitute and calling it a GPU result. The
report JSON is the proof artifact: attach it to the follow-up PR that
lands the optimized assets.
