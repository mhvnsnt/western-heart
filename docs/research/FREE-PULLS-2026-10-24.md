# Free pulls catalog — 2026-10-24 (open source, experimental, industry-standard, free APIs, free GPU)

Every item below is wired into tools/free-pulls/ in this same PR. Status words
mean exactly this: VERIFIED = checked by a real call, run, or file read on
2026-10-24/25; NOT RUN = script and run-guide done, execution still needs a
live-browser notebook run; NOT DELIVERED = named in the brief but no file
exists, and nothing here claims otherwise.

## Free APIs (all in tools/free-pulls/apis/)

| Item | Source | License | Free tier / auth | WH use | Status |
|---|---|---|---|---|---|
| Poly Haven | api.polyhaven.com | CC0 | No account, no key | Arena ground/road/rock textures, HDRI stage lighting | VERIFIED live: 869 textures, sand_01 1K JPG byte-exact |
| AmbientCG | ambientcg.com/api/v3 | CC0 | No account, no key | Material textures (Diffuse/Normal/Roughness/Displacement) | VERIFIED live: 2037 materials, Fabric086 zip downloaded and zip-tested |
| Google Fonts | fonts.googleapis.com/css2 | OFL | No key | Game UI fonts (menu, HUD, VS banners) | VERIFIED live: Bebas Neue, Inter variable, Oswald variable, byte-identical on re-pull |
| Hugging Face | huggingface.co/api | Varies per model/dataset | No key for metadata search | Asset-generation model/dataset discovery | VERIFIED live: metadata only, no weights downloaded |
| Sketchfab | api.sketchfab.com/v3 | Varies per model | Search: no auth. Download: token required | Free 3D models (fighters, stages, props) | SPLIT: search VERIFIED, download 401 without token, script exits 2 cleanly |
| Free Music Archive | freemusicarchive.org | Varies | No working API | Music search/download | DEAD: API HTTP 404, FMA developer page says shut down; candidates only |
| OpenGameArt | opengameart.org | Varies per item | No JSON API exists | Fighting-game art search | NO API: format=json returns HTML; records are manual curation, labeled as such |
| Kaggle | kaggle.com | Varies per dataset | Auth required (kaggle.json mode 600) | Public datasets (motion capture, pose, animation) | CHECK-ONLY: auth file presence/mode verified without reading it; CLI not installed; no live call made |

Correct Poly Haven host is api.polyhaven.com. The api.polyhaven.org host
returned HTTP 522. Poly Haven single-asset path GET /assets/id returns 404;
the list endpoint plus GET /files/id is the working pair.

## Free GPU (all in tools/free-pulls/gpu/)

| Option | Free tier | Limits | WH use | Status |
|---|---|---|---|---|
| Kaggle Notebooks | Free account, phone verification for GPU | About 30 GPU hrs/week, 2x Tesla T4 15 GB each, sessions about 12 h | Primary batch lane: Nosferatu cut, UniRig, Real-ESRGAN, pre-render | VERIFIED GPU itself by parent browser task (nvidia-smi 2x T4, CUDA 13.0); queue jobs NOT RUN |
| Google Colab free | Free Google account, no card | No published quota; runtimes at most 12 h, idle timeout; GPU type varies | Backup/overflow when Kaggle quota runs out | Script + run path ready; live Colab run NOT RUN |
| Hugging Face ZeroGPU | Free signed-in Spaces | About 3.5 min/day, per-call reservation, Gradio only | Demo-only inference, never a batch lane | Cataloged with current docs figure; demo sketch included; NOT a batch lane |
| WebGPU (browser) | Free, runs on player device | Depends on player hardware/browser | Game-side GPU compute (particles, post-processing) | Demo page included; game integration is a follow-up, not claimed |

GPU job queue order (tools/free-pulls/gpu/gpu-queue/): A Nosferatu 25-track
cut, B UniRig auto-rigging, C Real-ESRGAN upscale, D gltfpack batch
(CPU tool, batch parallelism only, never reported as GPU compute),
E character-card and stage-preview pre-render. Failover: Kaggle, then
Colab, then WebGPU on-device (game-side only), then stamped CPU fallback.
Jobs A and B wait for quota reset rather than running silently on CPU.

## Free assets pulled during verification (re-pullable, not vendored)

Poly Haven 1K CC0 textures (aerial_asphalt_01, sand_01, rock_01), AmbientCG
Fabric086 1K-JPG zip, GPU-lane texture sets (concrete, dry ground, metal
plate, rocky terrain, wood floor, 1K diffuse + roughness) plus studio_small_09
1K HDRI, Google Fonts woff2 set (vendored: only the fonts, about 84 KB,
because they are tiny and directly game-usable). Large binaries are not
vendored; manifests record exact URLs, sizes, and licenses, and the scripts
re-pull them with one command each.

## Free tools (partial — tools/free-pulls/tools/)

- wh_audio_loudnorm.sh: ffmpeg loudnorm to -14 LUFS plus WAV to Opus.
  Tested on a generated tone (44.1 kHz stereo, 128 kb/s Opus output).
- wh_glb_audit.py: GLB audit script.

NOT DELIVERED from the tools lane brief: Blender pipeline script, WASM
integration sketch, Stable Diffusion Kaggle skeleton, Tripo/Meshy client
skeletons, Wwise/FMOD tier facts, university/experimental repo picks.
A follow-up PR adds them when that lane reports. Nothing in this PR
claims them.

## Industry-standard notes

- Wwise-style audio for the browser game is covered by the separate
  studio-workflow lane (WebAudio engine design, FMOD-via-Wasm documented
  as an alternative, not the default). This PR does not re-litigate it.
- Git LFS is deliberately NOT adopted here: GitHub free LFS is about
  1 GB storage plus 1 GB per month bandwidth, and LFS pointers do not
  mix with the Git Data API merge flow this repo relies on. Opt-in for
  private repos only is the standing honest call.
- gltfpack measurement (fresh, this session): main stance GLB 128,296
  down to 53,828 bytes, -58 percent, bone names kept, source never
  overwritten. Prior-lane figures (hand stance -54 percent, IK stance
  -65 percent, Jungle Outpost -59 percent with meshes merged 203 to 111)
  are cited in tools/free-pulls/MEASURED-OPTIMIZATION.md, not re-run.

## What still needs a browser task (parent delegation, not faked)

1. Run the five GPU queue jobs in the Kaggle notebook, in order, and
   record nvidia-smi plus outputs per job into the results template.
2. Land the 25 Nosferatu mp3s in game/assets/music/ and copy loop
   points into the music library. Live main already carries the
   44-track library (verified 2026-10-24), so no code change is needed
   once the mp3s land. The 1980s VHS synth score is NOT automatically
   public domain: do not label it PD.
3. Sign-in-gated items, parent decision each: Sketchfab download token
   (only if a specific free model is chosen), Kaggle CLI install plus
   dataset pulls once authenticated, Colab notebook creation for
   overflow, Mixamo/Cascadeur/DeepMotion/Auto-Rig Pro decisions from
   the studio-workflow lane (unchanged by this PR).
