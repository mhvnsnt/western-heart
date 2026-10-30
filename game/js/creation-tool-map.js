/* ============================================================
   WESTERN HEART — Creation-suite tool map (menu -> tool)
   Every step of the creation pipeline maps to exactly one tool
   family, and every tool dir listed here ALREADY EXISTS in the
   repo — no duplicate tools/gltfpack, tools/mb-lab, tools/mpfb2
   dirs are created by this lane (verified on main 2026-10-24):
     body    -> MB-Lab / Build-A-Bod (tools/mb-lab, GPL) +
                MPFB (tools/mpfb2, parametric human)
     rigging -> GameRig / NaughTyRig (Blender rigging; outputs
                feed rig-compat.js + the UniRig pipeline)
     skin    -> Fluid Painter (texture/skin painting, Blender lane)
     import  -> Tripo intake / extraction (tools/tripo-intake;
                Tripo open-source auto-rigging runs on Kaggle GPU)
     export  -> gltfpack / glTF-Transform (tools/gltfpack, MIT;
                -cc measured 59-87% reduction on real WH assets)
   Statuses are honest: 'repo' = tool dir + script in repo;
   'blender-lane' = needs Blender (not on this VM — Kaggle GPU /
   Blender-lane job in tools/gpu-lane/); 'gpu-lane' = needs Kaggle
   GPU + keys via Secure Vault (never in files, never in chat).
   ============================================================ */

export const CREATION_TOOL_MAP = Object.freeze({
  body: { tools: ['MB-Lab', 'Build-A-Bod', 'MPFB'], toolDirs: ['tools/mb-lab', 'tools/mpfb2'], license: 'GPL / open source', status: 'blender-lane', output: 'parametric human mesh (GLB)' },
  rigging: { tools: ['GameRig', 'NaughTyRig'], toolDirs: ['tools/rig-intake'], license: 'open source (Blender addons)', status: 'blender-lane', output: 'rigged GLB + bone map for rig-compat.js' },
  skin: { tools: ['Fluid Painter'], toolDirs: ['tools/texture-pipe'], license: 'open source (Blender addon)', status: 'blender-lane', output: 'painted textures (KTX2/Basis)' },
  import: { tools: ['Tripo intake', 'Tripo open source (auto-rigging, animatable generation)', 'extraction pipeline'], toolDirs: ['tools/tripo-intake', 'tools/tripo-pull'], license: 'open source (Tripo) / WH pipeline', status: 'gpu-lane', output: 'rigged GLB in a rig-compat.js rig type' },
  export: { tools: ['gltfpack', 'glTF-Transform'], toolDirs: ['tools/gltfpack'], license: 'MIT', status: 'repo', output: 'optimized GLB (-cc, MeshoptDecoder in assets.js)' },
});

export function toolForStep(step) {
  const entry = CREATION_TOOL_MAP[step];
  if (!entry) throw new Error('creation-tool-map: unknown step ' + step);
  return entry;
}

export function creationSteps() {
  return Object.keys(CREATION_TOOL_MAP);
}

// Full pipeline for a model of a given rig type: every step, with
// the rig-compat contract (which rig type the output must declare).
export function pipelineForModel(rigType) {
  return creationSteps().map((step) => ({ step, ...CREATION_TOOL_MAP[step], rigType }));
}
