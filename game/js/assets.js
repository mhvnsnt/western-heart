/* ============================================================
   WESTERN HEART — Assets
   Preloads the REAL rigged fighters (Mixamo-skeleton GLBs) and
   hands out skeleton-cloned, per-fighter-tinted instances.
   Self-contained: models live at game/assets/models/.
   Pantera = real P1 textured body (roster/pantera). Steve Fox =
   Tekken 7 base reskinned cold blue-white (see game/README.md).
   ============================================================ */
import { checkClip, CTX } from './anim-gate.js';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { clone as skeletonClone } from 'three/addons/utils/SkeletonUtils.js';
// Meshopt-compressed GLBs (Tripo outputs: cape-jones, thor, waterfall,
// saku-ra-main, purple-rain-main, kiko-tanaka*). Vendored locally —
// the game ships with no CDN (see index.html importmap).
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.js';
// Clothing layer system (worker 64, 2026-10-22): per-mesh visibility
// toggles over GLB mesh names, data-driven via data/clothing-layers.json.
// No import cycle: clothing-layers.js imports nothing from this module.
import { applyClothingToInstance } from './clothing-layers.js';
// Creation Suite Pass: generated registry of baked customization overrides
// (customization/tools/apply_customization.py). Empty map = exact no-op.
import { ATTIRE_CUSTOMIZATIONS } from './attire-customizations.js';
// Material gate (every model, every load): game/js/material-runtime.js.
import { resolveModelMaterials, assertModelUsable } from './material-runtime.js';
// Lane 5: persistent Cache API for model bytes (see asset-cache.js).
// A cache hit skips the network entirely; a miss stores the bytes
// after a successful download. Never changes parse/ingest behavior.
import { getCachedBuffer, putCachedBuffer } from './asset-cache.js';
// Split hosting (owner decision 2026-10-26: Pages shell + GLBs on R2).
// resolveAssetCandidates maps one MODEL_URLS entry to its fetch order:
// bundled models stay local; everything else tries the remote asset
// base first (R2 once the bucket exists), then jsDelivr. One config
// line in asset-config.js moves the base — no per-model changes.
import { resolveAssetCandidates } from './asset-config.js';

export const MODEL_URLS = {
  pantera: 'assets/models/pantera.glb',
  'steve-fox': 'assets/models/steve-fox.glb',
  // NOTE (owner canon 2026-10-19): Tekken's Jin = DEMONIO — the old `jin:` key was removed;
  // `demonio: 'assets/models/demonio.glb'` (below) is the canonical model.
  // Per-fighter models wired from teardown extractions + Tripo rescans.
  // Keys match FULL_ROSTER `model` ids in roster-full.js (lane 2).
  demonio: 'assets/models/demonio.glb',
  // DIABLO Attire 1 (owner 2026-10-20, Tripo pull aee46f6a): the fantasy-demon
  // Tripo is the main attire. The old gtainside Heihachi conversion stays at
  // assets/models/diablo.glb as the ladder-back (not deleted).
  diablo: '../roster/diablo/attires/attire1/model-rigged.glb',
  'diablo-attire1': '../roster/diablo/attires/attire1/model-rigged.glb',
  // Diablo Attire 2 — Devil God (owner 2026-10-20, Tripo pull).
  'diablo-attire2': '../roster/diablo/attires/attire2/model.glb',
  // SLICE Attire 1 (owner 2026-10-21 ~08:42 CDT): the owner's own Tripo is
  // his MAIN DEFAULT attire — "undead warrior 3d model" by tzflo312
  // (cf9cf660-1673-4585-ac1b-ce4fc92f1550), pulled via tools/tripo-pull and
  // archived on release slice-tripo-pulls-20261021. Canon: arm blades jagged
  // chrome (Baraka/Wolverine prototype mix), skull mask blending into the
  // head at the back, scars all over, blades on belt buckle + shoe side.
  // Static meshopt GLB (no skin) — rigged 2026-10-23 (landing wave 2,
  // GameRig auto-rig, 73 joints); keys ride model-rigged.glb, static stays as source.
  slice: '../roster/slice/attires/attire1/model-rigged.glb',
  'slice-attire1': '../roster/slice/attires/attire1/model-rigged.glb',
  // SLICE Attire 2 — our Dragunov build (PR #433): Tekken 7 Dragunov teardown
  // model (dragunov-t7-rig.blend from release tekken-models-batch-2) converted
  // to GLB. It was Attire 1 until the owner's Tripo landed; it laddered back
  // byte-identical, never deleted — Slice's first own model, rigged on the
  // Tekken 7 game skeleton (198 joints).
  'slice-attire2': '../roster/slice/attires/attire2/model.glb',
  // ZUI Attires 1+2 (owner Tripos; gap found by the model-key audit, PR #418):
  // A1 = Drunken Monk Tripo, his DEFAULT attire (roster/zui/ATTIRE-SLOTS.md,
  // owner 2026-10-18). The GLBs sat in roster/zui/attires/ with NO MODEL_URLS
  // keys — unreachable. steve-fox.glb (his canon base) stays wired below and
  // ladders back as a selectable alternate in attires.js.
  // Rigged 2026-10-21 (Claude session): the A1 Tripo was an unrigged static (ZERO skinned
  // meshes -> invisible fighter). Auto-rigged with tools/auto_rig (GameRig backend +
  // smooth_weights.py); the owner's original stays untouched beside it as model.glb.
  'zui-attire1': '../roster/zui/attires/attire1/model-rigged.glb',
  'zui-attire2': '../roster/zui/attires/attire2/model.glb',
  // (Zen block restored 2026-10-22: dropped by 3942b8584 'Lane 4 rig batch 1', which left 'zen'/'zen-attire1'
  // unresolvable — game/tests/model-key-guard.test.mjs. Lines below are e09288722 + 292ca2b17 verbatim.)
  // ZEN Attire 1 — SPIRIT BODY (owner Tripo 8c46e379, 2026-10-21): Zen is
  // UNVESSELED (canon ruling 2026-10-21) — this is his own spirit body and
  // his main model, not a vessel swap. He was a steve-fox fallback rider in
  // roster-full with no attire ladder of his own; his legacy body stays
  // wired at 'zen-body' below and ladders back as a selectable alternate
  // in attires.js (never deleted).
  // Rigged 2026-10-22 (Claude session): the spirit body was an unrigged static (invisible in fights);
  // tools/auto_rig/rig_tripo_static.py -> model-rigged.glb, Tripo original model.glb untouched.
  // Proof: docs/proof/claude-2026-10-22/zen-rig/.
  zen: '../roster/zen/attires/attire1/model-rigged.glb',
  'zen-attire1': '../roster/zen/attires/attire1/model-rigged.glb',
  // ZEN'S SPIRIT FORM (owner Tripo 803f4cf1, 2026-10-21): Zen HIMSELF as
  // a spirit — the "stand version of himself" from his design. NOT an
  // attire and NOT his body: in the stand system the spirit form floats
  // behind his spirit body (behavior spec in roster/zen/RIG-NOTES.md).
  // Loadable as its own key, tied to Zen's fighter record.
  'zen-spirit': '../roster/zen/spirit/model-rigged.glb', // rigged form (PR #627 rigs) landed 2026-10-22; raw model.glb kept in place
  // ZEN TRANSFORMATION MODES (owner Tripos, 2026-10-21): NOT attires —
  // stages of ONE transformation inside Attire 1, chained via forms in
  // roster-full.js (spirit body -> TENTACLE MODE -> OVERSOUL). Canon:
  // roster/zen/CANON.md; behavior spec: roster/zen/RIG-NOTES.md.
  // TENTACLE MODE (9460095d): the clothing tentacle imagery becomes REAL
  // tentacles busting out of him; no Oversoul head; spirit rides higher
  // and further back (offset in RIG-NOTES.md).
  'zen-tentacle': '../roster/zen/tentacle/model-rigged.glb', // rigged form (PR #627 rigs) landed 2026-10-22; raw model.glb kept in place
  // OVERSOUL (2bbc8e88): the combined form — the spirit has docked at the
  // head position and TAKEN THE HEAD'S PLACE. Body tentacles on this
  // model are IMAGERY on the body, not protruding tentacles (verified on
  // the front render, 2026-10-21 — see roster/zen/ATTIRE-SLOTS.md).
  'zen-oversoul': '../roster/zen/oversoul/model-rigged.glb', // rigged form (PR #627 rigs) landed 2026-10-22; raw model.glb kept in place
  // Tripo pulls wired 2026-10-19 (owner: stop saying "not in the repo").
  phantom: '../roster/phantom/attires/attire1/model-rerig.glb',
  skull: '../roster/skull/attires/attire1/model-rerig.glb',
  // KRONOS (owner custom Zangief fighter, 2026-10-19): Tripo models live at
  // tripo-recovery/kronos_attire1_default.glb/ + kronos_attire2_timberwolf/;
  // copying the GLB into roster/kronos/attires/attire1/model.glb is a follow-up.
  kronos: '../roster/kronos/attires/attire1/model-rerig.glb',
  // SAM-UR-A1 Attire 1 (owner 2026-10-19): Tripo pull replaces the fan-rip placeholder.
  'sam-ur-a1': '../roster/sam-ur-a1/attires/attire1/model-rerig.glb',
  // SAKU RA (2026-10-21, lane 4 rig batch 1): unrigged Tripo static -> model-rigged.glb
  // via tools/auto_rig knn backend (donor pantera.glb); original model.glb untouched.
  'saku-ra': '../roster/sakura/attires/attire1/model-rerig.glb',
  'awa-pop': 'assets/models/awa-pop.glb',
  // AWA POP Attire 2 (fighter-completeness audit 2026-10-21): owner-confirmed
  // Tripo Attire 2 (roster/awa-pop/ATTIRE-SLOTS.md slot 2) — the GLB was in the
  // repo with no key, so it could never load.
  'awa-pop-attire2': '../roster/awa-pop/attires/attire2/model-rigged.glb',
  'purple-rain': '../roster/purplerain/attires/attire1/model-rerig.glb',
  nightwolf: 'assets/models/nightwolf.glb',
  // NIGHTWOLF Attire 1 (owner 2026-10-18, Tripo pull 5b0835eb "tribal warrior"):
  // his DEFAULT attire per roster/nightwolf/attires/ATTIRE-SLOTS.md — tribute to
  // Serena Misae Brown. Unrigged static; playable swap rides the auto-rig pass.
  'nightwolf-attire1': '../roster/nightwolf/attires/attire1/model.glb',
  'king-tyrant': 'assets/models/king-tyrant.glb',
  // KING TYRANT Attires 1-4 (owner 2026-10-19, Tripo pulls — see
  // roster/king-tyrant/attires/ATTIRE-SLOTS.md): White Tyrant / Tyrant King /
  // Black Snow / Fight Gear. The in-game base build ladders back. Unrigged
  // statics; auto-rig queued (cape/jacket cloth-rig tasks recorded, not blocking).
  'king-tyrant-attire1': '../roster/king-tyrant/attires/attire1/model.glb',
  'king-tyrant-attire2': '../roster/king-tyrant/attires/attire2/model.glb',
  'king-tyrant-attire3': '../roster/king-tyrant/attires/attire3/model.glb',
  'king-tyrant-attire4': '../roster/king-tyrant/attires/attire4/model.glb',
  // KINPO Attire 1 (owner 2026-10-20): his Tripo pull is her MAIN attire.
  // Repoint 2026-10-22 (worker 50): the k-NN model-rigged.glb was broken;
  // live keys now ride the tripo-intake rig (Blender 4.0.2 + GameRig, facing
  // +X measured — proof: docs/proof/muse-2026-10-21/tripo-intake/).
  kinpo: '../roster/kinpo/attires/attire1/model-intake.glb',
  'kinpo-attire1': '../roster/kinpo/attires/attire1/model-intake.glb',
  // Previous A1 (Asuka-based game model, provenance unknown) laddered back
  // to a legacy alternate 2026-10-20 — NOT deleted.
  'kinpo-legacy': 'assets/models/kinpo.glb',
  // Kinpo Attire 2 "Goth Sport" (owner 2026-10-20, Tripo pull — see roster/kinpo/ATTIRE-SLOTS.md).
  'kinpo-attire2': '../roster/kinpo/attires/attire2/model.glb',
  // KINPO INTAKE DEMO (2026-10-21, tripo-intake lane): the same attire-1 Tripo
  // re-rigged end-to-end by tools/tripo-intake (Blender 4.0.2 + GameRig, facing
  // +X measured by the intake's two-cue gate — the k-NN batch assumed +Z).
  // Suite-viewer demo key; the live game now uses 'kinpo'/'kinpo-attire1'
  // above (repointed 2026-10-22 to this same intake rig).
  'kinpo-intake-demo': '../roster/kinpo/attires/attire1/model-intake.glb',
  // WATERFALL (2026-10-21, lane 4 rig batch 1): unrigged Tripo static -> model-rigged.glb
  // via tools/auto_rig knn backend (donor pantera.glb); original model.glb untouched.
  waterfall: '../roster/waterfall/attires/attire1/model-rigged.glb',
  'n3g4tiv0': 'assets/models/n3g4tiv0.glb',
  thor: '../roster/thor/attires/attire1/model-rerig.glb',
  // Thor Attire 2: phantom-mimic oni mask (owner 2026-10-19).
  'thor-attire2': '../roster/thor/attires/attire2/model.glb',
  'doc-frank': 'assets/models/doc-frank.glb',
  // Doc Frank ATTIRE 1 pre-form (old man) — his own Attire 1 GLB at
  // roster/doc-frank/attires/attire1/pre-transform/model.glb. File lineage:
  // the PR #263 machine-shop texture reskin of the base, adopted as Attire
  // 1's old-man form; binds normalized in PR #465 (178 joints, rigged).
  // Picker position: BACK slot with the Tekken-based models (owner override
  // 2026-10-21: Tripo models lead slots 1-5, Tekken reskins toward the back)
  // — a reskin by lineage, not a Tripo model, so it no longer defaults.
  'doc-frank-a1': '../roster/doc-frank/attires/attire1/pre-transform/model.glb',
  // Doc Frank post-transform bigger form (owner 2026-10-19, Tripo pull).
  // Rigged 2026-10-21 (Tripo-forefront lane): model-rigged.glb carries the
  // pre-form's 178-joint rig via the repo k-NN transfer; original untouched.
  'doc-frank-big': '../roster/doc-frank/attires/attire1/post-transform/model-rigged.glb',
  // Wave 2 (2026-10-19): Wowomomo Attire 2, Hood Scientist Attire 3, Demonio forms, Dxmmii Attire 2.
  'doc-frank-wowomomo': '../roster/doc-frank/attires/attire2/base/model-rerig.glb',
  'doc-frank-wowomomo-big': '../roster/doc-frank/attires/attire2/transformed/model-rigged.glb',
  'doc-frank-hood': '../roster/doc-frank/attires/attire3/base/model.glb',
  'doc-frank-hood-big': '../roster/doc-frank/attires/attire3/transformed/model-rigged.glb',
  // Attire 4 "Frankenstein's Cyborg" (owner 2026-10-19): two-form transform attire.
  'doc-frank-frankenstein': '../roster/doc-frank/attires/attire4/base/model-rerig.glb',
  'doc-frank-frankenstein-big': '../roster/doc-frank/attires/attire4/transformed/model-rerig.glb',
  'demonio-a1': '../roster/demonio/attires/attire1/model.glb',
  'demonio-winged': '../roster/demonio/attires/winged-devil/model-rigged.glb',
  'demonio-human': '../roster/demonio/attires/human/model-rerig.glb',
  'dxmmii-a2': '../roster/dxmmii/attires/attire2/model.glb',
  // DXMMII Slot 1 — Tripo Default (dedup 2026-10-22): the 60MB Tripo pull
  // that replaced the wooden dummy as Slot 1 per owner 2026-10-19
  // (roster/dxmmii/ATTIRE-SLOTS.md). Wired so his select entry defaults to it.
  'dxmmii-tripo': '../roster/dxmmii/attires/attire1/model-rigged.glb',
  'cyborg-x': 'assets/models/cyborg-x.glb',
  'cape-jones': 'assets/models/cape-jones.glb',
  // CAPE JONES Attire 1 (rig QA 2026-10-23, muse/cape-jones-fight): the
  // auto-rigged Round-2 build (49 bones, -Z facing, sides/knees OK), staged
  // under his roster dir per convention. Byte-identical to
  // assets/models/cape-jones.glb — no re-rig needed. See
  // roster/cyborg-x/ATTIRE-SLOTS.md.
  'cape-jones-attire1': '../roster/cyborg-x/attires/attire1/model-rigged.glb',
  // Bonus / music fighters and name-pending models (loadable, unassigned).
  mariposa: 'assets/models/mariposa.glb',
  // Mariposa Slot 1 — Butterfly Default (dedup 2026-10-22): owner-designated
  // Slot 1 default 2026-10-19 (owner exception to the Tripo-first law, like
  // Pantera's Attire 1). Wired so her select entry defaults to it.
  'mariposa-butterfly-default': '../roster/zafina/attires/butterfly-default/mariposa-butterfly-default.glb',
  // Mariposa Slot 2: the real Tripo pull (owner 2026-10-19; Butterfly Default is Slot 1).
  'mariposa-slot2': '../roster/mariposa/attires/slot2/model.glb',
  zafina: 'assets/models/zafina.glb',
  // ZAFINA Golden Pharaoh (owner 2026-10-18 — see roster/zafina/attires/ATTIRE-SLOTS.md):
  // custom Western Heart pharaoh reskin of the Tekken Zafina P1 build. Mary Posa goes
  // over Zafina, so this ladders into Mariposa's attires behind her customs.
  'zafina-golden-pharaoh': '../roster/zafina/attires/golden-pharaoh/zafina-golden-pharaoh.glb',
  dxmmii: 'assets/models/dxmmii.glb',
  rave: 'assets/models/rave.glb',
  // Cain Elias — Vain Abel's brother, Undertaker archetype (owner 2026-10-19, Tripo pulls).
  'cain-elias': '../roster/cain-elias/attires/attire1/model.glb',
  'cain-elias-attire2': '../roster/cain-elias/attires/attire2/model.glb',
  // Vain Abel — Attire 2 (owner 2026-10-20, Tripo pull).
  'vainabel-attire1': '../roster/vainabel/attires/attire1/model-rigged.glb',
  'vainabel-attire2': '../roster/vainabel/attires/attire2/model-rigged.glb',
  // Vain Abel — Kane archetype (owner 2026-10-20, Tripo pull). Attire 3: Masked Demon of the Purple Haze.
  'vainabel-attire3': '../roster/vainabel/attires/attire3/model-rigged.glb',
  // Vain Abel — Attire 4: Half mask Horror of the Haze (owner 2026-10-21, Tripo pull).
  'vainabel-attire4': '../roster/vainabel/attires/attire4/model-rigged.glb',
  // Burger — Demon mode, possessed by greed (owner 2026-10-19, Tripo pull).
  burger: '../roster/burger/attires/attire1/model-rigged.glb',
  // Kronos — new fighter (owner 2026-10-19, Tripo pull).
  kronos: '../roster/kronos/attires/attire1/model-rerig.glb',
  'kronos-attire2': '../roster/kronos/attires/attire2/model-rerig.glb',
  'kronos-attire3': '../roster/kronos/attires/attire3/model.glb',
  // KORESHI (owner 2026-10-19): his own creation (Kakashi + SSJ4/5 + ninja, Tripo pull).
  koreshi: '../roster/koreshi/attires/attire1/model-rigged.glb',
  // Burger hunger-state variants (owner 2026-10-19, Tripo pulls).
  'burger-attire2': '../roster/burger/attires/attire2/model.glb',
  'burger-attire3': '../roster/burger/attires/attire3/model.glb',
  'burger-attire4': '../roster/burger/attires/attire4/model.glb',
  // Burger attires 5-7 (owner 2026-10-19, Tripo pulls).
  'burger-attire5': '../roster/burger/attires/attire5/model.glb',
  'burger-attire6': '../roster/burger/attires/attire6/model.glb',
  'burger-attire7': '../roster/burger/attires/attire7/model.glb',
  // BURGER transformation forms (fighter-completeness audit 2026-10-21):
  // roster-full.js forms target these semantic keys, but they were never
  // registered here, so fighter.js _doTransform failed on every attempt
  // (createInstance threw, catch swallowed it) and Burger could NEVER
  // transform. Canon mapping per roster/burger/ATTIRE-SLOTS.md: Speed Demon
  // = Attire 6, The Mouth = Attire 7, Demon (final) = Attire 1.
  'burger-speed-demon': '../roster/burger/attires/attire6/model.glb',
  'burger-the-mouth': '../roster/burger/attires/attire7/model.glb',
  'burger-demon': '../roster/burger/attires/attire1/model.glb',
  // Gyou spirit form (owner 2026-10-19, Tripo pull).
  'gyou-spirit': '../roster/gyou/attires/spirit-form/model.glb',
  lili: 'assets/models/lili.glb',   // base T7 Lili build (Silvertongue's Tekken base)
  // SILVERTONGUE (owner 2026-10-18: proprietary name, retired "Lili" — never use the
  // old name; see roster/silvertongue/ATTIRE-SLOTS.md): Slot 1 Tripo Main "Metallic
  // Bodysuit" (2e20f9eb, rigged 2026-10-23 wave 2 — key rides model-rigged.glb), Slot 2 Spy Debut, Slot 3 Rated-M Nude
  // (fully rigged 22-bone), Slot 4 Noir Gala (Tekken-based reskin, ladders back).
  'silvertongue': '../roster/silvertongue/attires/attire1/model-rigged.glb',
  'silvertongue-spy-debut': '../roster/silvertongue/attires/spy-debut/silvertongue-spy-debut.glb',
  'silvertongue-attire3': '../roster/silvertongue/attires/attire2/model.glb',
  'silvertongue-noir-gala': '../roster/lili/attires/noir-gala/lili-noir-gala.glb',
  baek: 'assets/models/baek.glb',   // KEVIN's A2 attire (original Baek model)
  // KEVIN A1 (owner 2026-10-18): Kevin's Tripo ("human figure", God Molecule canon) —
  // his DEFAULT attire per roster/baek/attires/ATTIRE-SLOTS.md. Rigged 2026-10-23
  // (wave 2, GameRig auto-rig, 73 joints); key rides model-rigged.glb.
  'kevin-tripo': '../roster/baek/attires/attire1/model-rigged.glb',
  // Round-2 auto-rig wave (lane B): re-rigged per-fighter variants + Tripo
  // attires, all passing the playable gate (valid glTF, skinned, Hips, 1.5-2.2m).
  // 'demonio-body' round-2 re-rig variant was never pushed to the repo;
  // repointed to the shipped Demonio body (teardown-integration 2026-10-19)
  // so the key resolves instead of 404ing.
  'demonio-body': 'assets/models/demonio.glb',
  'kai-body': 'assets/models/kai-body.glb',
  'jin-body': 'assets/models/jin-body.glb',
  'rin-body': 'assets/models/rin-body.glb',
  'jin-t7': 'assets/models/jin.glb',
  // JIN KAZAMA "Bloodline Ember" (owner 2026-10-18 — see
  // roster/jin/attires/bloodline-ember/README.md): devil-gene texture reskin of the
  // Jin Kazama base. Ladders into Phantom's attires (Yoshimitsu/Jin re-home rule).
  // NOTE: this is Jin KAZAMA — the Eastern Mind Jin still needs his own model.
  'jin-bloodline-ember': '../roster/jin/attires/bloodline-ember/jin-bloodline-ember.glb',
  'king-tyrant_alt1': 'assets/models/king-tyrant_alt1.glb',
  'kinpo-t8': 'assets/models/kinpo-t8.glb',
  'kinpo_alt1': 'assets/models/kinpo_alt1.glb',
  'phantom-t8': 'assets/models/phantom-t8.glb',
  'pantera_alt1': 'assets/models/pantera_alt1.glb',
  'pantera-body': 'assets/models/pantera-body.glb',
  'pantera-leoman': '../roster/pantera/attires/leomon/model.glb',
  // Pantera roster attires (owner reorder 2026-10-21: Tripo originals at
  // the front of game/js/attires.js — A1 Leo man is the 'pantera-leoman'
  // key above, A2 LEOPARD KING below; Tekken reskins behind them — A3 is
  // the base 'pantera' key above (T7King P1 reskin), A4 snow leopard,
  // A5 Crimson Rage, A6 T7 P2). ../roster pattern per phantom/skull.
  'pantera-snow-leopard': '../roster/pantera/attires/snow-leopard/pantera-snow-leopard.glb',
  // LEOPARD KING re-rig (2026-10-22, owner: forearms/hands stretch, legs crumpled, hand weighted to the
  // tail): King's 49-joint skeleton refitted INSIDE the mesh (tools/auto_rig/refit_skeleton.py) + Blender
  // bone heat (backends/heat_rebind.py). The 2026-10-21 model-rigged.glb stays beside it, untouched.
  // Proof: docs/proof/claude-2026-10-22/pantera-rigs/.
  'pantera-leopard-king': '../roster/pantera/attires/leopard-king/model-refit.glb',
  'pantera-crimson-rage': '../roster/pantera/attires/crimson-rage/pantera-attire5-crimson.glb',
  'pantera-p2': '../roster/pantera/attires/p2-wired/pantera-attire4-p2.glb',
  'retsu-body': 'assets/models/retsu-body.glb',
  'saku-ra_alt1': 'assets/models/saku-ra_alt1.glb',
  'saku-ra-main': 'assets/models/saku-ra-main.glb',
  'sam-ur-a1-body': 'assets/models/sam-ur-a1-body.glb',
  'sha-body': 'assets/models/sha-body.glb',
  'zen-body': 'assets/models/zen-body.glb',
  'zui_alt1': 'assets/models/zui_alt1.glb',
  'zui_alt2': 'assets/models/zui_alt2.glb',
  'kiko-tanaka': 'assets/models/kiko-tanaka.glb',
  'kiko-tanaka_alt1': 'assets/models/kiko-tanaka_alt1.glb',
  'purple-rain-main': 'assets/models/purple-rain-main.glb',
  // Lane C fighter-hunt (Round 2): per-fighter models from community rips,
  // retargeted to Mixamo skeleton. See docs/fighter-hunt/HUNT-LOG.md.
  // STAR (2026-10-21, MINI wire-up): the game now loads her HOUSE-49
  // re-template (PR #481) — same mesh/weights remapped onto the house
  // template skeleton, floor-origin fixed (geometry min-y 0.0000; the old
  // hip-origin frame sank her ~1 m through the floor), with her authored
  // Christie 2P textures restored from the source TXD. The original
  // star.glb stays in place, untouched, as the fallback file.
  star: 'assets/models/star-house49.glb',
  // STAR Attires 1-3 + 5 (owner 2026-10-18, Tripo pull ea73eeb3 — see
  // roster/star/ATTIRE-SLOTS.md): A1 Red Latex (DEFAULT Tripo main), A2 After Dark
  // + A3 Capoeira Gold (texture colorways on the Tripo base), A5 rated-M lane
  // (improved build; model.glb superseded, kept on disk). Unrigged statics;
  // playable swap rides the auto-rig pass.
  'star-attire1': '../roster/star/attires/attire1/model.glb',
  'star-attire2': '../roster/star/attires/attire2/model.glb',
  'star-attire3': '../roster/star/attires/attire3/model.glb',
  'star-attire5': '../roster/star/attires/attire5/model-improved.glb',
  torch: 'assets/models/torch.glb',
  // TORCH Attire 1 (owner 2026-10-21): Tripo original 'Valkyrie of Flame'
  // (300d0c63), auto-rigged via tools/auto_rig/rig_tripo_static.py; raw pull
  // archived in release torch-a1-tripo-20261021. Ladder: roster/torch/ATTIRE-SLOTS.md.
  'torch-tripo-a1': 'assets/models/torch-tripo-a1.glb',
  // TORCH Attire 2 (owner 2026-10-21): Tripo original 'Red demon'
  // (7f8c7874), auto-rigged via tools/auto_rig/rig_tripo_static.py; raw pull
  // archived in release torch-a2-tripo-20261021. Ladder: roster/torch/ATTIRE-SLOTS.md.
  'torch-tripo-a2': 'assets/models/torch-tripo-a2.glb',
  michiko: 'assets/models/michiko.glb',
  // MICHIKO's Tripo originals (owner 2026-10-21): Attire 1 "bone goddess"
  // + Attire 2 "biker chick" — ladder in attires.js, provenance in
  // roster/michiko/ATTIRE-SLOTS.md. The Katarina-based model above stays
  // as her fallback attire.
  'michiko-attire1': '../roster/michiko/attires/attire1/model-rigged.glb',
  'michiko-attire2': '../roster/michiko/attires/attire2/model-rigged.glb',
  dio: 'assets/models/dio.glb',
  bruno: 'assets/models/bruno.glb',
  // T3 cast with no WH roster body (moveset sweep 2026-10-29): their T3 teardown rigs,
  // re-exported as skinned GLBs in lab/ (private: not in the --shell-only Pages set).
  't3-anna': '../lab/game/assets/t3_anna_t3real.glb',
  't3-bosconovitch': '../lab/game/assets/t3_bosconovitch_t3real.glb',
  't3-julia': '../lab/game/assets/t3_julia_t3real.glb',
  't3-nina': '../lab/game/assets/t3_nina_t3real.glb',
  't3-ogre': '../lab/game/assets/t3_ogre_t3real.glb',
  't3-paul': '../lab/game/assets/t3_paul_t3real.glb',
  yukihyo: 'assets/models/yukihyo.glb',
  // SCIMITAR (2026-10-21, lane 4 rig batch 1): unrigged static -> auto-rigged via
  // tools/auto_rig knn backend (donor pantera.glb); owner's original stays untouched.
  scimitar: 'assets/models/scimitar-rigged.glb',   // Shaheen-based base mesh — NO-GATE: wired as-is, clothing via Creation Suite as an option
  // Created fighters use the Soldier.glb base from the CAW suite.
  // Relative path works on GitHub Pages (game/ -> customization/).
  custom: '../customization/create-fighter/assets/Soldier.glb',
  // Reskin wave (2026-10-19): first custom attires, wired as selectable fighters.
  // Jin Bloodline Ember + Doc Frank Machine Shop are rigged drop-ins from their
  // lanes; Baek/Mariposa/Dxmmii are texture-transplants onto their rigged bases
  // (reskin lanes dropped the skins on buffer rebuild) — *-rigged.glb.
  'demonio-bloodline-ember': '../roster/demonio/attires/bloodline-ember/demonio-bloodline-ember.glb',
  'doc-frank-machine-shop': '../roster/doc-frank/attires/machine-shop/doc-frank-machine-shop-rigged.glb',
  'baek-master-white': '../roster/baek/attires/master-white/baek-master-white-rigged.glb',
  'mariposa-monarch': '../roster/mariposa/attires/monarch/mariposa-monarch-rigged.glb',
  'dxmmii-patchwork': '../roster/dxmmii/attires/patchwork-dj/dxmmii-patchwork-rigged.glb',
  // Sketchfab intake (owner 2026-10-19): Zangief, Blanka, Vega, Iori, Armor King.
  // WH names pending owner pick from INTAKE-PROPOSAL.md — working names for now.
  // Licenses: Zangief CC-BY (johnny136), Blanka Free Standard (allanromanreyes),
  // Vega CC-BY (pierodsoto01), Iori CC-BY (0xo), Armor King CC-BY (theamazingdonovan207).
  zangief: '../roster/zangief/attires/attire1/model-rigged.glb',
  blanka: '../roster/blanka/attires/attire1/model.glb',
  // CHARGER (owner 2026-10-20): Blanka replacement fighter — owner Tripo models.
  // CHARGER Attire 1 (2026-10-21, lane 4 rig batch 1): unrigged Tripo static -> model-rigged.glb
  // via tools/auto_rig knn backend (donor pantera.glb); original model.glb untouched.
  charger: '../roster/charger/attires/attire1/model-rigged.glb',
  // DOROWANI (owner 2026-10-22): Gon's WH replacement. Rigged 2026-10-23
  // (landing wave 2, GameRig auto-rig, 73 joints); key rides the rigged
  // build, the Tripo static stays beside it as source.
  dorowani: '../roster/dorowani/attires/attire1/source/dorowani-a1-crimson-cheeks-rigged.glb',
  // CHATUR (owner 2026-10-23): True Ogre's WH replacement — four-armed Oversoul
  // spirit, temple dancer who refused to die. SmutBase intake (roster/rahkasa/).
  // Unrigged static (1 mesh; rig widgets live in the .blend); k-NN auto-rig
  // from donor is the planned path.
  // Rigged 2026-10-23 (PR #780, 52-joint canonical skeleton, verified).
  chatur: '../roster/rahkasa/attires/attire1/model-rigged-textured.glb',
  // POND (owner 2026-10-23): Raven's WH replacement — swamp boundary watcher,
  // found Dorowani as an egg. SmutBase intake (roster/tsuyu-asui/). Unrigged
  // static (9 meshes, clothing separate); k-NN auto-rig from donor is the planned path.
  // Rigged 2026-10-23 (PR #780, 52-joint canonical skeleton, verified).
  pond: '../roster/tsuyu-asui/attires/attire1/model-rigged-textured.glb',
  // CHARGER Attire 2 (2026-10-21, lane 4 rig batch 1): unrigged Tripo static -> model-rigged.glb
  // via tools/auto_rig knn backend (donor pantera.glb); original model.glb untouched.
  'charger-attire2': '../roster/charger/attires/attire2/model-rigged.glb',
  vega: '../roster/vega/attires/attire1/model.glb',
  iori: '../roster/iori/attires/attire1/model.glb',
  // ARMOR KING (2026-10-21, lane 4 rig batch 1): 29-mesh Sketchfab static -> model-rigged.glb
  // via tools/auto_rig knn backend (donor pantera.glb); original model.glb untouched.
  'armor-king': '../roster/armor-king/attires/attire1/model-rigged.glb',
  // DEATHFANG (owner 2026-10-19): proprietary, based on Iori Yagami — chained/shackled
  // prisoner of his own grief, emo reskin, NO FUTURE face tattoo. Attire 2 = chained
  // prisoner werewolf transform form. (Supersedes the parallel lane's placeholder,
  // which pointed deathfang at the plain Iori model — the real reskin model lives
  // in roster/deathfang/ now.)
  deathfang: '../roster/deathfang/attires/attire1/model.glb',
  'deathfang-werewolf': '../roster/deathfang/attires/attire2/model.glb',
  // Ryuji Yamazaki x The Rock hybrid (owner 2026-10-19) — CORNERSTONE.
  // MODEL LANDED 2026-10-22 (owner Tripo 20c1fd2e-40d0-4500-9be6-50f6494ab5e1):
  // archived at attires/attire1/source/cornerstone-a1.glb and copied
  // byte-identical to the wired model.glb 2026-10-23 (landing wave 1), so this
  // key resolves. Rigged 2026-10-23 (landing wave 2, GameRig auto-rig,
  // 73 joints); the key rides model-rigged.glb and the unrigged Tripo
  // stays beside it as source. See roster/ryuji-rock/attires/attire1/README.md.
  'ryuji-rock': '../roster/ryuji-rock/attires/attire1/model-rigged.glb',
  // MEGAMI (2026-10-23, SmutBase 6 pipeline fighters 5-6): SmutBase Parvati
  // commission intake. In-repo build = meshopt-compressed (23.5 MB, validated);
  // intake original (191.6 MB) archived on release
  // megami-menajerii-smutbase-20261023. Canon: roster/parvati/CANON.md.
  // Moveset: game/assets/movesets/megami.json (Jun Kazama TTT2 kit, Tekken inputs).
  megami: '../roster/parvati/attires/attire1/model-rigged.glb',
  'megami-attire1': '../roster/parvati/attires/attire1/model-rigged.glb',
  // MENAJERII (2026-10-23, SmutBase 6 pipeline fighters 5-6): SmutBase Vixen
  // commission intake (Injustice 2-based). In-repo build = meshopt-compressed
  // (41.7 MB, validated); intake original (629.7 MB) archived on release
  // megami-menajerii-smutbase-20261023. Canon: roster/vixen/CANON.md.
  // Moveset: game/assets/movesets/menajerii.json (Roger Jr. TTT2 kit, fresh
  // Tekken inputs per owner directive — no Injustice 2 input system).
  // model-rigged-noplane.glb = the crew rig (PR #780) with its skinned 4.23 m floor plane removed
  // (docs/proof/claude-2026-10-23/smutbase/README.md); the crew file stays beside it.
  menajerii: '../roster/vixen/attires/attire1/model-rigged-noplane.glb',
  'menajerii-attire1': '../roster/vixen/attires/attire1/model-rigged-noplane.glb',
  // ——— LANDING WAVE 1 (2026-10-23, docs/CATCHUP-AUDIT-2026-10-23.md) ———
  // Wiring fixes only: keys for models already on main that no key reached.
  // BUFFALO BILL: his moveset file sat on main unlisted; A1/A2 sources named
  // in roster/buffalo-bill/CANON.md are NOT in the repo — Attire 3 "Ashes"
  // is his only on-main model, so the base key points there.
  'buffalo-bill': '../roster/buffalo-bill/attires/attire3/model-rigged.glb',
  // VAIN ABEL ELIAS: base key. His Attire 1 Tripo (f7e90de8) was recovered
  // 2026-10-23 (wave 2 hunt: pulled via tools/tripo-pull, archived on release
  // vain-abel-a1-tripo-20261023) — the base key points at
  // his default Attire 1 (same file as 'vainabel-attire1'; rigged 2026-10-23, wave 2).
  vainabel: '../roster/vainabel/attires/attire1/model-rigged.glb',
  // CHORDZ (owner 2026-10-15: Lars -> Chordz, emo guitarist). His Tripo sits
  // archived as an unrigged static under attires/attire1/source/.
  // Two rigs of the same Tripo static exist: source/chordz-a1-rigged.glb (crew, Wave 2 B1) and
  // model-rigged.glb (Claude, same GameRig pipeline + limb isolation; same stance in game, 2026-10-23).
  chordz: '../roster/chordz/attires/attire1/model-rigged.glb',
  // GASHADOKURO + AOTSUKI (OBSOLETE-ORIGINALS rule, docs/OBSOLETE-ORIGINALS-
  // RULE.md): the Kuma/Panda models ARE the proprietary successors now — the
  // keys are the successors' names; there is no 'kuma'/'panda' fighter key.
  // Unrigged statics; their roster entries wait for wave-3 movesets.
  gashadokuro: '../roster/kuma/attires/attire1/source/kuma-a1.glb',
  aotsuki: '../roster/panda/attires/attire1/source/aotsuki-a1-rigged.glb',
  // Attire variant keys for on-main GLBs no key reached (catch-up audit
  // attires-unwired set). Ladder placement lives in game/js/attires.js:
  // successor's own attires first, source-game originals late (slots 5+).
  'bruno-attire1': '../roster/bruno/attires/attire1/source/bruno-a1.glb',
  'bruno-attire2': '../roster/bruno/attires/attire2/source/bruno-a2-sail-the-sea-rigged.glb',
  'dio-attire1': '../roster/dio/attires/attire1/source/dio-a1-jade-god-rigged.glb',
  'koreshi-attire1': '../roster/koreshi/attires/attire1/model.glb',
  // Negativo attire 1 = the landmark re-fit (PR #1463, tools/auto_rig/refit_rig.py; proof
  // docs/proof/2026-11-01/refit-negativo/): face/hair on Head, arms on the arm bones, hips at the hips.
  // Own path + 18.9 MB (tools/deploy/fit_cdn_budget.py) so the live build loads it from jsDelivr
  // until the B2 bucket carries it. negativo-a1-rigged.glb (#1465) stays on main beside it.
  'negativo-attire1': '../roster/negativo/attires/attire1/source/negativo-a1-refit.glb',
  'negativo-attire2': '../roster/negativo/attires/attire2/source/negativo-a2-rigged.glb',
  'skull-tripo': '../roster/skull/attires/attire1/model.glb',
  'skull-base': 'assets/models/skull.glb',
  'waterfall-attire1': '../roster/waterfall/attires/attire1/model.glb',
  'yukihyo-attire1': '../roster/yukihyo/attires/attire1/source/yukihyo-a1-rigged.glb',
  'yukihyo-attire2': '../roster/yukihyo/attires/attire2/source/yukihyo-a2-bobcat-pride-rigged.glb',
  'yukihyo-attire3': '../roster/yukihyo/attires/attire3/source/yukihyo-a3-tiger-king-rigged.glb',
  'armor-king-attire1': '../roster/armor-king/attires/attire1/model.glb',
  'zangief-attire1': '../roster/zangief/attires/attire1/model.glb',
  // RYUSAN (owner 2026-10-23): SmutBase Mina Ashido intake — WH name RYUSAN,
  // the Corrosion Soul. Attire 1 = the SmutBase GLB (unrigged static; rig queued).
  // NOTE: roster/mina-ashido/attires/attire1/model-rigged.glb landed on main
  // 2026-10-23 (PR #781, wave-1 rigging) — repoint key after rig validation.
  // In-game validation (docs/proof/claude-2026-10-23/smutbase): the model-rigged.glb build tears
  // apart in the T3 stance; model-rerig.glb (upright static + GameRig +Z) holds it.
  ryusan: '../roster/mina-ashido/attires/attire1/model-rerig.glb',
  'ryusan-attire1': '../roster/mina-ashido/attires/attire1/model-rerig.glb',
  // TOBI (owner 2026-10-23): SmutBase Mirko (Rumi Usagiyama) intake — WH name
  // TOBI, the Escape Soul. Attire 1 = the SmutBase GLB (unrigged static; rig queued).
  // NOTE: roster/miruko/attires/attire1/model-rigged.glb landed on main
  // 2026-10-23 (PR #781, wave-1 rigging) — repoint key after rig validation (same finding as Ryusan).
  tobi: '../roster/miruko/attires/attire1/model-rerig-textured.glb',
  'tobi-attire1': '../roster/miruko/attires/attire1/model-rerig-textured.glb',
};

/* ============================================================
   FOREIGN-RIG REMAP — Vega only (per-character isolation law).
   Vega's GLB (roster/vega/attires/attire1/model.glb) is fully
   skinned (364 joints) but uses a foreign naming scheme, so ZERO
   of the 21 canonical T3 bone names exist on it: fighter.js's
   gate (bones.Hips && bones.RightArm) fails and every T3
   AnimationMixer track (tracks bind by NODE NAME) misses.
   Fix: rename the 21 core joint NODES on the cloned instance to
   the T3 names. Renaming is skinning-safe in glTF/THREE — skins
   reference joint node INDICES, not names (verified in the
   playtest proof: the renamed instance skins + animates).

   The correspondence was DERIVED FROM THE GLB ITSELF (node
   hierarchy + skin weights + world positions), never from name
   similarity alone:
   - Waist_06 -> Hips: the pelvis. Sole joint whose children are
     the spine chain (Stomach_07) AND both leg roots
     (LLegRoot_0195 / RLegRoot_0184); 501 skin weight around the
     pelvis; the Stomach/Chest/Neck/Head chain hangs off it.
   - Stomach_07 -> Spine: Waist's only upward child, +0.124 above
     it, sole parent of Chest_08.
   - Chest_08 -> Chest: parent of Neck_09 AND both shoulder
     chains (LShoulder_01 / RShoulder_0113).
   - Neck_09 -> Neck: sole parent of Head_010.
   - Head_010 -> Head: parent of every Face and hair joint.
   - LShoulder_01 / RShoulder_0113 -> Left/RightShoulder: FIRST
     joint off Chest on each side (world x -/+0.006 — the
     sternum, exactly where a Mixamo shoulder/clavicle bone
     originates; its child *Clavicle_* is an extra intermediate
     this rig adds, left unrenamed to pass rotation through).
   - LArm1_0148 / RArm1_0117 -> Left/RightArm: origin at the
     anatomical shoulder joint (world x -/+0.273), first WEIGHTED
     arm bone (ArmRoot above it is a 0-weight helper at the same
     origin), parent of the forearm chain, heaviest upper-arm
     skin weight.
   - LArm2_0149 / RArm2_0118 -> Left/RightForeArm: origin at the
     elbow (co-located with the *Elbow_* helper, but that helper
     is a LEAF — Arm2 is the elbow-position joint that is the
     actual parent of the hand chain).
   - LhandXR_0150 / RhandXR_0121 -> Left/RightHand: wrist joint
     (world x -/+0.819), ancestor of handRot + ALL finger chains
     and carrier of the largest hand skin weight (160), so a Hand
     rotation moves the whole hand rigidly.
   - LLeg1_0196 / RLeg1_0185 -> Left/RightUpLeg: first WEIGHTED
     leg bone (LegRoot above it is a 0-weight helper at the same
     origin), parent of the shin chain.
   - LLeg2_0197 / RLeg2_0186 -> Left/RightLeg: shin, sole parent
     of the foot (co-located *Knee_* helper is a leaf, same
     pattern as the elbow).
   - LFoot_0198 / RFoot_0187 -> Left/RightFoot: parent of toe.
   - LToe_0199 / RToe_0188 -> Left/RightToeBase: terminal toe
     joint, parent of the foot-toe helpers.
   'Root' is intentionally NOT mapped: canonical Mixamo fighters
   have no Root bone either, so that T3 track stays unbound on
   Vega exactly as it does on pantera/steve-fox.
   Scope: applies ONLY when the model URL is Vega's AND every
   source name of this scheme signature is present on the clone
   (otherwise a strict no-op) — no other fighter can be renamed.
   ============================================================ */
const VEGA_MODEL_URL = '../roster/vega/attires/attire1/model.glb';
const VEGA_T3_BONE_REMAP = {
  Waist_06: 'Hips',
  Stomach_07: 'Spine',
  Chest_08: 'Chest',
  Neck_09: 'Neck',
  Head_010: 'Head',
  LShoulder_01: 'LeftShoulder',
  LArm1_0148: 'LeftArm',
  LArm2_0149: 'LeftForeArm',
  LhandXR_0150: 'LeftHand',
  RShoulder_0113: 'RightShoulder',
  RArm1_0117: 'RightArm',
  RArm2_0118: 'RightForeArm',
  RhandXR_0121: 'RightHand',
  LLeg1_0196: 'LeftUpLeg',
  LLeg2_0197: 'LeftLeg',
  LFoot_0198: 'LeftFoot',
  LToe_0199: 'LeftToeBase',
  RLeg1_0185: 'RightUpLeg',
  RLeg2_0186: 'RightLeg',
  RFoot_0187: 'RightFoot',
  RToe_0188: 'RightToeBase',
};

/* The canonical Mixamo models' root-chain rotation, measured
   from pantera.glb + steve-fox.glb: their Hips parent ('Character'
   node) carries quaternion (-0.7071, 0, 0, 0.7071). The T3 clips
   store ABSOLUTE local quaternions authored against that frame,
   so a clip frame only lands correctly when the world orientation
   of every driven bone's parent chain matches the Mixamo one. */
const CANONICAL_ROOT_CHAIN_QUAT = [-0.70710678, 0, 0, 0.70710678];

/* Non-driven helper joints sitting BETWEEN driven joints in
   Vega's chains, with non-identity bind rotations (measured from
   the GLB): ArmRoot L/R are ~90° about Y, LegRoot L/R are a
   ~90° tilted frame, handRot L/R carry the finger frame. The
   Mixamo chains have NO joint in those slots, so during a clip
   their bind rotations would ride on top of the clip pose as a
   constant twist. They are neutralized to identity below (bind
   pose is preserved by the inverse-bind recompute). */
const VEGA_FRAME_HELPER_JOINTS = [
  'LArmRoot_0147', 'RArmRoot_0116',
  'LLegRoot_0195', 'RLegRoot_0184',
  'LhandRot_0151', 'RhandRot_0122',
];

/* Canonical bind LOCAL quaternions per driven bone, measured
   from pantera.glb (the working Mixamo rig the T3 banks were
   baked against). Bones not listed here have identity bind
   locals on the canonical rig. Vega's authored locals store
   different per-bone frame rotations (Arm1 is
   (-0.5005, -0.4995, -0.4995, 0.5005), Leg1 is
   (0.0007, 0.0007, 0.7073, 0.7069), Foot is
   (0.4999, 0.5, 0.5001, -0.5)), and its child translations are
   expressed along its own axis conventions (arm/leg offsets
   along X where Mixamo uses +Y) — both are converted below. */
const CANONICAL_BIND_LOCALS = {
  Hips: [0, 0.70710678, 0.70710678, 0],
  LeftShoulder: [-0.70710678, -0.70710678, 0, 0],
  RightShoulder: [0, 0, 0.70710678, 0.70710678],
  LeftUpLeg: [1, 0, 0, 0],
  RightUpLeg: [1, 0, 0, 0],
  LeftFoot: [-0.70710678, 0, 0, 0.70710678],
  RightFoot: [-0.70710678, 0, 0, 0.70710678],
};

/* Rename Vega's foreign core joints on ONE cloned instance and
   convert the instance's bind frame to the canonical T3/Mixamo
   frame so the absolute-quaternion clips land upright:
   1. the rotated non-bone FBX wrapper ancestors above the
      skeleton root are cancelled at the MODEL ROOT (their
      inverse is premultiplied), so the authored geometry
      presents upright in skeleton space; the RM_BLR_Middle_04
      joint above the pelvis then takes the canonical root-
      chain rotation (-0.7071, 0, 0, 0.7071), making the full
      chain above the pelvis canonical.
   2. the other in-chain helper joints are set to identity, the
      driven bones' bind locals become the canonical ones
      (CANONICAL_BIND_LOCALS), and their local translations are
      re-solved so every joint keeps its authored skeleton-space
      position.
   3. every skeleton's inverse bind matrices are recomputed from
      the edited bind world matrices — renaming/frame edits are
      skinning-safe because skins reference joint indices, and
      with IBM = inverse(new bind world) the bind-pose bone
      matrices stay identity, so the mesh stays glued to the
      skeleton (bind pose presented in the canonical frame).
   4. origin lift — this rig's origin is its pelvis, not its
      feet (see ORIGIN LIFT in the code), so the instance is
      lifted until the bind pose's lowest point rests at y=0.
   Returns true when the full scheme signature matched and the
   remap was applied; false (no-op) for every other model. */
function remapVegaBones(fighterId, model) {
  if (MODEL_URLS[fighterId] !== VEGA_MODEL_URL) return false;
  const byName = {};
  model.traverse((o) => { if (o.isBone) byName[o.name] = o; });
  // Scheme signature: ALL foreign source names must be present,
  // and none of the target names may already exist (a model that
  // is already T3-named, or a different rig, is never touched).
  for (const src of Object.keys(VEGA_T3_BONE_REMAP)) {
    if (!byName[src]) return false;
  }
  for (const dst of Object.values(VEGA_T3_BONE_REMAP)) {
    if (byName[dst]) return false;
  }
  for (const [src, dst] of Object.entries(VEGA_T3_BONE_REMAP)) {
    byName[src].name = dst;
  }

  // --- bind-frame conversion (see header comment) ---
  // Skinning deforms by each bone's DELTA from its bind world
  // matrix, and the rendered bind pose is the mesh nodes' world
  // transform applied to the authored geometry — so a clip
  // reproduces the canonical pose, on an upright body, when:
  // (a) the wrapper ancestors above the skeleton root are
  //     cancelled at the model root (geometry then presents
  //     exactly as authored: upright, in skeleton space);
  // (b) the remaining chain stage above the pelvis — the
  //     RM_BLR_Middle_04 joint — carries the canonical
  //     root-chain rotation, so the full chain above the pelvis
  //     equals the canonical 'Character' rotation and every
  //     clip delta is conjugated exactly like the Mixamo rigs';
  // (c) the driven bones' bind locals are the canonical ones,
  //     with local translations re-solved so every joint keeps
  //     its authored position in skeleton space.
  const hips = byName.Waist_06; // renamed 'Hips' above
  const ancestors = [];
  for (let p = hips.parent; p; p = p.parent) ancestors.unshift(p);
  // Wrapper product: every ancestor above the skeleton root
  // bone (_rootJoint) — Sketchfab_model / untitledfbx /
  // BLR_01_skeleton carry matrix-encoded rotations (measured in
  // the live clone: their product is -90° about X).
  const rootBoneIdx = ancestors.findIndex((a) => a.isBone);
  const wrapperProd = new THREE.Quaternion(0, 0, 0, 1);
  for (let i = 0; i < rootBoneIdx; i++) wrapperProd.multiply(ancestors[i].quaternion);
  const correction = wrapperProd.clone().invert();
  // Full original chain product, for recovering skeleton-space
  // positions below.
  const chainProd = new THREE.Quaternion(0, 0, 0, 1);
  for (const a of ancestors) chainProd.multiply(a.quaternion);

  // Desired bind world positions: each joint's authored
  // position in SKELETON space (the space the geometry is
  // authored in) = its model-space world position with the
  // full original chain rotation factored back out.
  model.updateMatrixWorld(true);
  const driven = Object.entries(VEGA_T3_BONE_REMAP)
    .map(([src, dst]) => ({ node: byName[src], dst }));
  const unchain = chainProd.clone().invert();
  const desiredPos = new Map();
  for (const { node } of driven) {
    desiredPos.set(node, node.getWorldPosition(new THREE.Vector3()).applyQuaternion(unchain));
  }

  // (a) Cancel the wrapper rotations at the model root.
  model.quaternion.premultiply(correction);
  // (b) RM_BLR_Middle_04 becomes the canonical chain stage;
  // the other in-chain helpers go to identity (the canonical
  // chains have no joint in those slots).
  if (byName.RM_BLR_Middle_04) {
    byName.RM_BLR_Middle_04.quaternion.set(...CANONICAL_ROOT_CHAIN_QUAT);
  }
  for (const name of VEGA_FRAME_HELPER_JOINTS) {
    if (byName[name]) byName[name].quaternion.set(0, 0, 0, 1);
  }
  // (c) Driven bones' bind locals become the canonical ones.
  for (const { node, dst } of driven) {
    const q = CANONICAL_BIND_LOCALS[dst];
    if (q) node.quaternion.set(q[0], q[1], q[2], q[3]);
    else node.quaternion.set(0, 0, 0, 1);
  }
  // Translation re-solve, parents before children: changing a
  // frame swings every child joint around its parent, so each
  // driven bone's local translation is re-expressed in its
  // (now canonical) parent frame to land exactly on its
  // desired authored world position.
  const depthOf = (n) => { let d = 0; for (let p = n.parent; p; p = p.parent) d++; return d; };
  driven.sort((a, b) => depthOf(a.node) - depthOf(b.node));
  const _pw = new THREE.Vector3(), _pq = new THREE.Quaternion(), _ps = new THREE.Vector3();
  for (const { node } of driven) {
    const parent = node.parent;
    parent.updateWorldMatrix(true, false);
    parent.matrixWorld.decompose(_pw, _pq, _ps);
    node.position.copy(desiredPos.get(node).sub(_pw).applyQuaternion(_pq.clone().invert()));
  }
  model.updateMatrixWorld(true);
  const seenSkeletons = new Set();
  model.traverse((o) => {
    if (o.isSkinnedMesh && o.skeleton && !seenSkeletons.has(o.skeleton)) {
      seenSkeletons.add(o.skeleton);
      o.skeleton.calculateInverses();
    }
  });
  // ORIGIN LIFT: this rig is authored with its origin at the
  // PELVIS (pelvis local position is (0,0,0) and every ancestor
  // translation is zero), while the canonical models are authored
  // with their origin at their FEET (Mixamo Hips sits ~1m up).
  // The game places the model root on the ground, so un-lifted
  // Vega stands waist-deep under the floor and every clip pivots
  // around a floor-level pelvis. Lift the instance so the bind
  // pose's lowest point rests on the ground plane.
  const bindBox = new THREE.Box3().setFromObject(model);
  if (bindBox.min.y < -0.01) model.position.y -= bindBox.min.y;
  console.log(`[WH] ${fighterId}: foreign rig remapped to T3 bone names (21 joints) + bind frame converted to canonical T3 frame`);
  return true;
}

/* ============================================================
   SLICE FOREIGN-RIG REMAP (2026-10-21, B6 lane 3). Slice's
   model (roster/slice/attires/attire1/model.glb) is a REAL
   rigged/skinned Tekken 7 extraction — 198 joints, 17 skinned
   meshes, 1 skin — but its core joints carry T7 names with NO
   T3 Hips/Spine/Chest/... set, so the T3 stance gate
   (select-screen.js: needs Hips/RightArm/Head) never fires and
   the model sits in bind pose. Measured from the GLB JSON chunk
   (python3, no Blender):
   - core chain: Hip -> Spine1 -> Spine2 -> Neck -> Head,
     Spine2 -> L/R_Shoulder -> L/R_Arm -> L/R_ForeArm ->
     L/R_Hand, Hip -> L/R_UpLeg -> L/R_Leg -> L/R_Foot -> L/R_Toe.
     Every __offset joint is a sibling/leaf helper: the ancestor
     walk from each driven joint up to the pelvis found NO
     non-driven joint between driven joints, so unlike Vega no
     in-chain helper neutralization is needed.
   - chain above the pelvis: SK_CH_dra_bdu_1P.ao (mesh node,
     identity transform), MODEL_00 (bone, 180 deg about
     (0,1,1)/sqrt(2)), BASE (bone, identity — the pelvis's
     immediate parent). MODEL_00's rotation is skeleton frame,
     NOT a wrapper rotation: the authored bind is Y-up in world
     (pelvis y ~1.08, head y ~1.83, origin at the feet).
   - STRUCTURAL DIFFERENCE (measured): Spine1's parent is BASE,
     making the spine a SIBLING of Hip — the T7 layout. The T3
     banks were baked against the Mixamo layout (Hips -> Spine),
     and retargetT3Clips emits a Hips.position track (vertical
     root motion) that must carry the torso: with a sibling
     spine it would move only the legs, detaching the pelvis
     from the torso on crouches/knockdowns. The remap therefore
     reparents Spine under Hips (world transform preserved),
     completing the T7 -> T3/Mixamo hierarchy conversion. The
     game's analyzeRig is hierarchy-adaptive (dynamic chest LCA
     + spine chain), so the retarget consumes the converted rig
     as designed.
   'Neck'/'Head' are intentionally NOT in the table: they are
   already T3-named on this rig and pass through untouched (but
   they ARE frame-converted below, like Vega's).
   Scope: applies ONLY when the model URL is Slice's AND every
   source name of this scheme signature is present on the clone
   AND no target name already exists (otherwise a strict no-op)
   — no other fighter can be renamed.
   ============================================================ */
const SLICE_MODEL_URL = '../roster/slice/attires/attire1/model-rigged.glb';
const SLICE_T3_BONE_REMAP = {
  Hip: 'Hips',
  Spine1: 'Spine',
  Spine2: 'Chest',
  L_Shoulder: 'LeftShoulder',
  L_Arm: 'LeftArm',
  L_ForeArm: 'LeftForeArm',
  L_Hand: 'LeftHand',
  R_Shoulder: 'RightShoulder',
  R_Arm: 'RightArm',
  R_ForeArm: 'RightForeArm',
  R_Hand: 'RightHand',
  L_UpLeg: 'LeftUpLeg',
  L_Leg: 'LeftLeg',
  L_Foot: 'LeftFoot',
  L_Toe: 'LeftToeBase',
  R_UpLeg: 'RightUpLeg',
  R_Leg: 'RightLeg',
  R_Foot: 'RightFoot',
  R_Toe: 'RightToeBase',
};

/* Rename Slice's T7 core joints on ONE cloned instance and
   convert the instance's bind frame to the canonical T3/Mixamo
   frame so the absolute-quaternion clips land upright — the
   same conversion remapVegaBones performs, parameterized for
   Slice's measured chain:
   1. the wrapper ancestors above the skeleton root bone are
      cancelled at the MODEL ROOT (their inverse is
      premultiplied). Slice's ao mesh node is identity, so this
      is a no-op today that future-proofs a re-export with a
      rotated wrapper.
   2. Spine (renamed Spine1) is reparented under Hips with its
      world transform preserved, completing the T7
      (sibling-spine) to T3/Mixamo (Hips -> Spine) hierarchy
      conversion (see header comment).
   3. the bone stages above the pelvis are normalized: BASE
      (the pelvis's immediate parent, Vega's RM_BLR_Middle_04
      analog) takes the canonical root-chain rotation
      (-0.7071, 0, 0, 0.7071) and MODEL_00 goes to identity, so
      the full chain above the pelvis equals the canonical
      'Character' rotation and every clip delta is conjugated
      exactly like the Mixamo rigs'.
   4. the driven bones' bind locals become the canonical ones
      (CANONICAL_BIND_LOCALS), and their local translations are
      re-solved so every joint keeps its authored world
      position (Slice's authored locals differ: Spine1 carries
      (0, 0.7071, 0.7071, 0), L_Shoulder is
      (-0.5, -0.5, -0.5, 0.5), L_Foot is
      (-0.4763, 0, 0, 0.8793), L_Toe is a 180-degree twist —
      all measured from the GLB). Neck/Head are included in
      the driven set (already T3-named, no rename needed).
   5. every skeleton's inverse bind matrices are recomputed from
      the edited bind world matrices — renaming/reparenting/
      frame edits are skinning-safe because skins reference
      joint indices, and with IBM = inverse(new bind world)
      the bind-pose bone matrices stay identity, so the mesh
      stays glued to the skeleton exactly as authored
      (upright, Y-up).
   6. origin lift — kept generic: this rig is authored with its
      origin at its FEET (pelvis bind world y ~1.08), so the
      lift is a safety no-op; a re-export with a pelvic origin
      would be lifted until the bind pose's lowest point rests
      at y=0 instead of standing waist-deep under the floor.
   Deliberate deviation from remapVegaBones, measured not
   guessed: Vega factors the FULL ancestor chain (wrappers +
   the RM_BLR_Middle_04 bone stage) out of the desired bind
   positions. Slice's MODEL_00 bone carries a 180-degree
   skeleton-frame rotation, not a wrapper rotation — factoring
   it would tip the converted skeleton's world frame to Z-up
   (head.y - hips.y = 0, verified numerically) and fail the
   select-screen head-hips fit gate. Here only the non-bone
   wrapper ancestors are factored, so the authored Y-up world
   positions are preserved (head.y - hips.y = 0.75, verified
   numerically from the GLB).
   Returns true when the full scheme signature matched and the
   remap was applied; false (no-op) for every other model. */
/* TEKKEN-SKELETON RE-RIGS (2026-10-23, docs/tech/ROSTER-MODEL-AUDIT.md).
   Fighters whose own mesh was re-rigged onto a real Tekken 7 skeleton
   (232-bone T7 layout, same joint names as Slice's). Tekken skeleton data
   is a Bandai Namco asset, so the GLBs live ONLY in the private
   mhvnsnt/game-reverse-engineering repo (rigs/<id>/attire1/model-t7.glb);
   a private build copies them to game/assets/private/rigs/ and sets
   globalThis.__WH_PRIVATE_ASSETS = true. The public build keeps the
   fighter's existing own-model URL. These URLs share Slice's T7 -> T3
   remap (same signature guard: every T7 source name present, no T3 name). */
const PRIVATE_T7_RIGS = {
  burger: 'assets/private/rigs/burger/attire1/model-t7.glb',
};
const T7_RIG_URLS = new Set([SLICE_MODEL_URL]);
if (globalThis.__WH_PRIVATE_ASSETS) {
  for (const [id, url] of Object.entries(PRIVATE_T7_RIGS)) {
    MODEL_URLS[id] = url;
    T7_RIG_URLS.add(url);
  }
}

/* PRIVATE T7 skin textures (Yukihyo). Yukihyo's materials are T7
   MI_CH_malebody_<part>_02_skin, which share the generic T7 male body UVs.
   The diffuse maps (T_CH_male_<part>_D) are Bandai Namco assets kept ONLY in
   the private game-reverse-engineering repo (teardown/pakchunk0/textures/
   Character/Common/shader/Texture/skin/male/); a private build copies them to
   game/assets/private/textures/t7-skin/male/. Public builds skip this and the
   fighter stays quarantined. The King-face (MI_CH_knk_*) maps were not found
   in any private pull, so the material gate still decides usability. */
const PRIVATE_SKIN_TEXTURES = {
  yukihyo: {
    base: 'assets/private/textures/t7-skin/male/',
    match: /^MI_CH_malebody_(arm|body|foot|hand|head|leg|neck)_02_skin/i,
    file: (part) => `T_CH_male_${part}_D.webp`,
  },
};
async function applyPrivateSkinTextures(id, gltf) {
  const spec = globalThis.__WH_PRIVATE_ASSETS && PRIVATE_SKIN_TEXTURES[id];
  if (!spec) return;
  const loader = new THREE.TextureLoader();
  const cache = new Map();
  const mats = [];
  gltf.scene.traverse((o) => { if (o.isMesh) mats.push(...[].concat(o.material)); });
  for (const m of mats) {
    const hit = m && spec.match.exec(m.name || '');
    if (!hit || m.map) continue;
    const url = spec.base + spec.file(hit[1].toLowerCase());
    if (!cache.has(url)) cache.set(url, loader.loadAsync(url).catch(() => null));
    const tex = await cache.get(url);
    if (!tex) continue;
    tex.flipY = false; tex.colorSpace = THREE.SRGBColorSpace;
    m.map = tex; m.color && m.color.set(0xffffff); m.needsUpdate = true;
  }
}

function remapSliceBones(fighterId, model) {
  if (!T7_RIG_URLS.has(MODEL_URLS[fighterId])) return false;
  const byName = {};
  model.traverse((o) => { if (o.isBone) byName[o.name] = o; });
  // Scheme signature: ALL T7 source names must be present, and
  // none of the T3 target names may already exist (a model that
  // is already T3-named, or a different rig, is never touched).
  // Neck/Head are already T3-named on this rig and pass through.
  for (const src of Object.keys(SLICE_T3_BONE_REMAP)) {
    if (!byName[src]) return false;
  }
  for (const dst of Object.values(SLICE_T3_BONE_REMAP)) {
    if (byName[dst]) return false;
  }
  for (const [src, dst] of Object.entries(SLICE_T3_BONE_REMAP)) {
    byName[src].name = dst;
  }
  // Hierarchy conversion: Spine1 is authored as a sibling of
  // Hip (both under BASE); the T3 banks assume Mixamo's
  // Hips -> Spine. Reparent (world transform preserved) so the
  // Hips.position root-motion track carries the torso.
  const hipsBone = byName.Hip; // renamed 'Hips' above
  const spineBone = byName.Spine1; // renamed 'Spine' above
  if (hipsBone && spineBone && spineBone.parent !== hipsBone) {
    hipsBone.attach(spineBone);
  }

  // --- bind-frame conversion (see header comment) ---
  // Skinning deforms by each bone's DELTA from its bind world
  // matrix, and the rendered bind pose is the mesh nodes' world
  // transform applied to the authored geometry — so a clip
  // reproduces the canonical pose, on an upright body, when:
  // (a) the wrapper ancestors above the skeleton root bone are
  //     cancelled at the model root;
  // (b) the bone stages above the pelvis total the canonical
  //     root-chain rotation, so every clip delta is conjugated
  //     exactly like the Mixamo rigs';
  // (c) the driven bones' bind locals are the canonical ones,
  //     with local translations re-solved so every joint keeps
  //     its authored world position.
  const ancestors = [];
  for (let p = hipsBone.parent; p; p = p.parent) ancestors.unshift(p);
  // Wrapper product: every NON-BONE ancestor above the skeleton
  // root bone (MODEL_00) — the SK_CH_dra_bdu_1P.ao mesh node,
  // measured identity in the GLB, so this correction is a no-op
  // today. (Vega factors the bone stage too; Slice must not —
  // see the header comment.)
  const rootBoneIdx = ancestors.findIndex((a) => a.isBone);
  const wrapperProd = new THREE.Quaternion(0, 0, 0, 1);
  for (let i = 0; i < rootBoneIdx; i++) wrapperProd.multiply(ancestors[i].quaternion);
  const correction = wrapperProd.clone().invert();

  // Desired bind world positions: each joint's authored world
  // position (Y-up, as the bind renders today).
  model.updateMatrixWorld(true);
  const driven = Object.entries(SLICE_T3_BONE_REMAP)
    .map(([src, dst]) => ({ node: byName[src], dst }));
  // Neck/Head are already T3-named (no rename) but are T3-driven
  // joints: include them so their world positions are preserved too.
  for (const n of ['Neck', 'Head']) {
    if (byName[n]) driven.push({ node: byName[n], dst: n });
  }
  const desiredPos = new Map();
  for (const { node } of driven) {
    desiredPos.set(node, node.getWorldPosition(new THREE.Vector3()));
  }
  // Original bind relation per skin joint, captured BEFORE any frame
  // edit: B_i = boneWorld_i * IBM_i (the authored mesh-to-bone bind).
  // It is identity only when the mesh was bound in the skeleton's own
  // space (Slice's old export). Blender re-rigs (Burger onto Bob,
  // 2026-10-23) bind a mesh whose space differs from the bones' (B_i
  // carries the export's offset/scale), and recomputing IBMs as the
  // plain inverse of the edited bone worlds threw that relation away:
  // the bind pose still drew (every bone matrix = I) but every clip
  // delta pivoted in the wrong space and the body collapsed in fights.
  // The re-solve below keeps B_i exactly: IBM'_i = inverse(W'_i) * B_i.
  const bindRel = [];
  model.traverse((o) => {
    if (o.isSkinnedMesh && o.skeleton && !bindRel.some(e => e.sk === o.skeleton)) {
      const sk = o.skeleton;
      bindRel.push({ sk, B: sk.bones.map((b, i) => new THREE.Matrix4().multiplyMatrices(b.matrixWorld, sk.boneInverses[i])) });
    }
  });

  // (a) Cancel the wrapper rotations at the model root.
  model.quaternion.premultiply(correction);
  // (b) BASE becomes the canonical chain stage; the other bone
  // stage above the pelvis (MODEL_00) goes to identity.
  const base = byName.BASE;
  if (base) base.quaternion.set(...CANONICAL_ROOT_CHAIN_QUAT);
  const model00 = byName.MODEL_00;
  if (model00) model00.quaternion.set(0, 0, 0, 1);
  // (c) Driven bones' bind locals become the canonical ones.
  for (const { node, dst } of driven) {
    const q = CANONICAL_BIND_LOCALS[dst];
    if (q) node.quaternion.set(q[0], q[1], q[2], q[3]);
    else node.quaternion.set(0, 0, 0, 1);
  }
  // Translation re-solve, parents before children: changing a
  // frame swings every child joint around its parent, so each
  // driven bone's local translation is re-expressed in its
  // (now canonical) parent frame to land exactly on its
  // desired authored world position.
  const depthOf = (n) => { let d = 0; for (let p = n.parent; p; p = p.parent) d++; return d; };
  driven.sort((a, b) => depthOf(a.node) - depthOf(b.node));
  const _pw = new THREE.Vector3(), _pq = new THREE.Quaternion(), _ps = new THREE.Vector3();
  for (const { node } of driven) {
    const parent = node.parent;
    parent.updateWorldMatrix(true, false);
    parent.matrixWorld.decompose(_pw, _pq, _ps);
    node.position.copy(desiredPos.get(node).sub(_pw).applyQuaternion(_pq.clone().invert()));
  }
  model.updateMatrixWorld(true);
  // Re-solve the inverse binds, preserving each joint's authored bind
  // relation B_i (see bindRel above): IBM'_i = inverse(W'_i) * B_i.
  for (const { sk, B } of bindRel) {
    sk.bones.forEach((b, i) => {
      sk.boneInverses[i].copy(b.matrixWorld).invert().multiply(B[i]);
    });
  }
  // ORIGIN LIFT: kept generic — this rig is authored with its
  // origin at its FEET, so this is a safety no-op; a re-export
  // with a pelvic origin would be lifted until the bind pose's
  // lowest point rests at y=0.
  const bindBox = new THREE.Box3().setFromObject(model);
  if (bindBox.min.y < -0.01) model.position.y -= bindBox.min.y;
  console.log(`[WH] ${fighterId}: T7 rig remapped to T3 bone names (19 joints renamed; Neck/Head already T3-named) + Spine reparented under Hips + bind frame converted to canonical T3 frame`);
  return true;
}

// Creation Suite Pass: let baked customizations override base model URLs
// before anything loads them. Guarded — any registry problem leaves
// MODEL_URLS exactly as authored above.
try {
  for (const [key, url] of Object.entries(ATTIRE_CUSTOMIZATIONS || {})) {
    if (url) MODEL_URLS[key] = url;
  }
} catch (e) { /* Creation Suite registry unavailable: base URLs stand. */ }

/* MESH FACING (2026-10-20). The game (fighter.js lean rotation) and the T3
   retarget assume a model's mesh faces +Z. Many shipped GLBs face -Z, and
   the auto-rig template skeleton faces -Z even inside +Z meshes, so bone
   names/orientations cannot tell. assets/models/model-facing.json records
   each model's mesh facing read from raw rest renders (proof listed in the
   file). Unlisted models use the feet-geometry cue below when it is
   confident; otherwise +Z. createInstance() wraps the clone so the
   instance's own space always has the mesh facing +Z. */
const FACING_URL = 'assets/models/model-facing.json';
let _facingTable = null;
const _facingReady = fetch(FACING_URL).then(r => (r.ok ? r.json() : null))
  .then(j => { _facingTable = (j && j.models) || {}; })
  .catch(() => { _facingTable = {}; });

/* Feet cue: the lowest 5% of skinned vertices near each ankle extend
   further toward the toes than toward the heel. Returns +1 (+Z), -1 (-Z)
   or 0 (not confident; |score| < 0.05 misread no model in the 52-model
   check against rest renders, 2026-10-20). */
function feetFacingCue(root) {
  root.updateMatrixWorld(true);
  const inv = new THREE.Matrix4().copy(root.matrixWorld).invert();
  const pts = [];
  const v = new THREE.Vector3(), m = new THREE.Matrix4();
  let feet = [];
  root.traverse((o) => {
    if (!o.isSkinnedMesh) return;
    m.multiplyMatrices(inv, o.matrixWorld);
    const pos = o.geometry.attributes.position;
    const step = Math.max(1, Math.floor(pos.count / 40000));
    for (let i = 0; i < pos.count; i += step) { v.fromBufferAttribute(pos, i).applyMatrix4(m); pts.push(v.x, v.y, v.z); }
    if (!feet.length && o.skeleton) {
      for (const b of o.skeleton.bones) {
        const n = b.name.replace(/^mixamorig:?/, '').replace(/_\d+$/, '');
        if (/^(Left|Right)Foot$|^Bip0*1_[LR]_Foot$|^[LR]_Foot$/.test(n)) {
          feet.push(new THREE.Vector3().setFromMatrixPosition(new THREE.Matrix4().multiplyMatrices(inv, b.matrixWorld)));
        }
      }
    }
  });
  if (pts.length < 300 || feet.length < 2) return 0;
  let y0 = Infinity, y1 = -Infinity;
  for (let i = 1; i < pts.length; i += 3) { y0 = Math.min(y0, pts[i]); y1 = Math.max(y1, pts[i]); }
  const h = y1 - y0;
  let score = 0;
  for (const a of feet.slice(0, 2)) {
    const zs = [];
    for (let i = 0; i < pts.length; i += 3) {
      if (pts[i + 1] < y0 + 0.05 * h && Math.abs(pts[i] - a.x) < 0.06 * h) zs.push(pts[i + 2]);
    }
    if (zs.length < 10) return 0;
    zs.sort((p, q) => p - q);
    const hi = zs[Math.floor(zs.length * 0.99)], lo = zs[Math.floor(zs.length * 0.01)];
    score += ((hi - a.z) - (a.z - lo)) / h;
  }
  return score >= 0.05 ? 1 : (score <= -0.05 ? -1 : 0);
}

/* Shared GLTFLoader for fetch+parse loads (meshopt wired once).
   parseAsync on a shared instance is safe — per-load state lives in
   the returned promise, not the loader. */
let _sharedLoader = null;
function _sharedGLTFLoader() {
  if (!_sharedLoader) {
    _sharedLoader = new GLTFLoader();
    _sharedLoader.setMeshoptDecoder(MeshoptDecoder);
  }
  return _sharedLoader;
}
function _timeoutSignal(ms) {
  if (typeof AbortSignal !== 'undefined' && AbortSignal.timeout) return AbortSignal.timeout(ms);
  const c = new AbortController();
  const t = setTimeout(() => c.abort(new Error('timeout')), ms);
  if (c.signal.addEventListener) c.signal.addEventListener('abort', () => clearTimeout(t), { once: true });
  return c.signal;
}
function _anySignal(signals) {
  const list = signals.filter(Boolean);
  if (!list.length) return undefined;
  if (typeof AbortSignal !== 'undefined' && AbortSignal.any) return AbortSignal.any(list);
  const c = new AbortController();
  for (const s of list) {
    if (s.aborted) { c.abort(s.reason); break; }
    s.addEventListener('abort', () => c.abort(s.reason), { once: true });
  }
  return c.signal;
}

class AssetManager {
  constructor() {
    this.gltfs = {};   // id -> gltf
    this.clips = {};   // id -> {name: clip}
    this.facing = {};  // id -> +1 (+Z) | -1 (-Z), mesh facing of the raw GLB
    this.groundY = {}; // id -> lowest skinned-vertex height of the raw GLB at rest
    this.ready = false;
    this._inflight = {};      // id -> { promise, abort } — dedups concurrent loads
    this._idleCtrls = new Set(); // AbortControllers of the idle warm lane
  }

  _abortIdle() {
    if (!this._idleCtrls.size) return;
    for (const c of this._idleCtrls) { try { c.abort(); } catch (e) { /* noop */ } }
    this._idleCtrls.clear();
  }

  // TEKKEN 3 LESSON (teardown/tekken3/docs/TEKKEN3-ARCHITECTURE.md):
  // "Tekken 3 doesn't load everything at once. The BNS table is an index —
  // the game loads specific records on demand." We do the same: load only
  // the models needed for the current fight, not the whole roster at boot.
  //
  // CLEAN-INIT: a hung download must NEVER brick the game. Each model
  // gets a timeout + one retry; total failure rejects so the UI can
  // show a real error instead of spinning forever.
  async loadModels(ids, onProgress, opts = {}) {
    const lane = opts.lane || 'user';
    // LOADSPEED: user intent preempts the background warm lane — a card
    // tap aborts idle base prefetches so the tapped model gets the pipe.
    if (lane !== 'idle') this._abortIdle();
    const unique = [...new Set(ids)];
    const jobs = [];
    for (const id of unique) {
      if (this.gltfs[id]) continue;
      const fly = this._inflight[id];
      // Join an in-flight load instead of doubling it — unless this call
      // carries its own abort signal (a preview tap owns its fetch so a
      // newer tap can cancel it without disturbing other consumers).
      // Never join a load that was just aborted (the idle warm lane, cancelled above by this
      // same call): joining it made a fight reject with AbortError whenever its fighter was
      // still warming (2026-10-23, Pantera: "fight load failed: BodyStreamBuffer was aborted").
      if (fly && !opts.signal && !fly.signal.aborted) { jobs.push(fly.promise); continue; }
      jobs.push(this._loadOne(id, onProgress, unique.length, opts));
    }
    let done = 0;
    for (const j of jobs) {
      await j;
      done++;
      if (onProgress) onProgress(done / Math.max(jobs.length, 1));
    }
    if (Object.keys(this.gltfs).length > 0) this.ready = true;
    return this;
  }

  /* One model: fetch (abort-aware, byte-progress) -> parseAsync ->
     _ingest. Caller cancellations never retry; every other failure —
     including our own stall watchdog's abort — retries once. */
  _loadOne(id, onProgress, total, opts) {
    if (this._inflight[id] && !opts.signal && !this._inflight[id].signal.aborted) return this._inflight[id].promise;
    const ctrl = new AbortController();
    if (opts.signal) {
      if (opts.signal.aborted) ctrl.abort(opts.signal.reason);
      else opts.signal.addEventListener('abort', () => ctrl.abort(opts.signal.reason), { once: true });
    }
    const url = MODEL_URLS[id];
    assertModelUsable(id); // quarantined (broken materials) never loads into select or a fight
    // Split hosting: bundled models load from Pages exactly as before;
    // every other model tries the remote asset base first, then jsDelivr.
    const candidates = resolveAssetCandidates(url);
    // STALL timeout, not a total deadline (fight-load fix, 2026-10-31): the
    // old 90 s TOTAL deadline aborted any model whose bytes took longer
    // than that to arrive — three transform forms of one fighter share the
    // pipe with the fighters' own models, so on a phone connection the
    // biggest model routinely crossed 90 s mid-body and the fight load
    // rejected with "AbortError: BodyStreamBuffer was aborted" (owner:
    // kicked back to stage select, retry identical). A load that is still
    // RECEIVING bytes is alive, however slow: only a load that receives
    // NOTHING for STALL_TIMEOUT_MS is treated as hung and aborted — and
    // that abort is retried once (see run()), not fatal.
    const STALL_TIMEOUT_MS = 45000;
    const attempt = async () => {
      const stall = new AbortController();
      let stallTimer = null;
      const armStall = () => {
        if (stallTimer) clearTimeout(stallTimer);
        stallTimer = setTimeout(() => stall.abort(new Error(`no bytes received for ${STALL_TIMEOUT_MS}ms loading ${id}`)), STALL_TIMEOUT_MS);
      };
      const disarmStall = () => { if (stallTimer) { clearTimeout(stallTimer); stallTimer = null; } };
      const signal = _anySignal([ctrl.signal, stall.signal]);
      armStall();
      try {
        return await attemptBody(signal, armStall);
      } finally {
        disarmStall();
      }
    };
    const attemptBody = async (signal, armStall) => {
      let firstErr = null;
      let lastErr = null;
      for (const cand of candidates) {
        // Lane 5: persistent-cache hit — report full byte progress once
        // (the bar must move on real bytes, not stall), then parse the
        // cached buffer on the identical path as a network download.
        // Cross-origin remote URLs are not cacheable (asset-cache.js),
        // so remote loads skip this and go to the network every session.
        if (!signal.aborted) {
          const cached = await getCachedBuffer(cand);
          if (cached && !signal.aborted) {
            if (onProgress) onProgress(1, cached.byteLength, cached.byteLength, id);
            return _sharedGLTFLoader().parseAsync(cached, cand);
          }
        }
        let res;
        try {
          res = await fetch(cand, { signal });
        } catch (e) {
          if (e && e.name === 'AbortError') throw e;
          if (!firstErr) firstErr = e;
          lastErr = e;
          continue;
        }
        if (!res.ok) {
          lastErr = new Error(`HTTP ${res.status} loading ${id} from ${cand}`);
          if (!firstErr) firstErr = lastErr;
          continue;
        }
        const totalBytes = Number(res.headers.get('content-length')) || 0;
        let buf;
        try {
          // Manual read loop: byte-level progress for the MB readout, and
          // the read itself stays abort-aware.
          const reader = res.body.getReader();
          const chunks = [];
          let loaded = 0;
          for (;;) {
            const { done, value } = await reader.read();
            if (done) break;
            chunks.push(value);
            loaded += value.byteLength;
            armStall(); // bytes are flowing — the load is alive, re-arm the stall watchdog
            if (onProgress && totalBytes > 0) {
              onProgress(Math.min(loaded / totalBytes / Math.max(total, 1), 1), loaded, totalBytes, id);
            }
          }
          const merged = new Uint8Array(loaded);
          let off = 0;
          for (const c of chunks) { merged.set(c, off); off += c.byteLength; }
          buf = merged.buffer;
        } catch (e) {
          if (e && e.name === 'AbortError') throw e;
          buf = await res.arrayBuffer(); // no reader progress on very old browsers
        }
        // Lane 5: persist the downloaded bytes for the next session.
        // Fire-and-forget (never blocks the parse); a failed store is
        // a silent no-op inside putCachedBuffer.
        if (buf) putCachedBuffer(cand, buf);
        // The candidate URL string is the parse base, so external .bin /
        // texture references resolve against the host that served the GLB.
        return _sharedGLTFLoader().parseAsync(buf, cand);
      }
      // Name the FIRST (primary/local) failure, not only the last
      // fallback's: a local 404 followed by an unreachable CDN used to
      // surface as a bare "Failed to fetch", hiding the asset that is
      // actually missing (2026-10-24 P0 error-surface intent).
      if (firstErr && lastErr && firstErr !== lastErr) {
        throw new Error(`${firstErr.message || firstErr} (fallback also failed: ${lastErr.message || lastErr})`);
      }
      throw lastErr || new Error(`no candidate loaded for ${id}`);
    };
    const run = (async () => {
      let gltf;
      try {
        gltf = await attempt();
      } catch (e1) {
        // Retry once — INCLUDING aborts, unless the CALLER cancelled.
        // ctrl.signal.aborted means a real cancellation (preview tap
        // superseded the load, idle-warm preemption): fail fast, never
        // retry. Any other AbortError came from our own stall watchdog or
        // the network stack (the old code rethrew those instantly, which
        // is what turned one slow model into a bounced fight).
        if (ctrl.signal.aborted) throw e1;
        console.warn(`[WH] ${id} load failed, retrying:`, e1.message || e1);
        gltf = await attempt(); // throws to caller on second failure
      }
      await this._ingest(id, gltf);
      return gltf;
    })();
    const tracked = run.finally(() => {
      if (this._inflight[id] && this._inflight[id].promise === tracked) delete this._inflight[id];
    });
    this._inflight[id] = { promise: tracked, abort: () => ctrl.abort(), signal: ctrl.signal };
    return tracked;
  }

  /* Post-parse ingestion: the exact processing the old loader callback
     did (clip pinning, shadow flags, grounding, facing) — factored out so
     fetch+parse shares the identical path. */
  async _ingest(id, gltf) {
    // Material resolve + verdict before anything can instance this model.
    this.materialReport = this.materialReport || {};
    await applyPrivateSkinTextures(id, gltf);
    this.materialReport[id] = await resolveModelMaterials(id, gltf, async (d) => {
      await this.loadModels([d], null, { lane: 'user' }); return this.gltfs[d];
    });
    if (!this.materialReport[id].usable) throw new Error(`model ${id} blocked by material gate`);
    this.gltfs[id] = gltf;
    this.clips[id] = {};
    // Bind-pose Hips position (Z-up skeleton): animations must return
    // here, not to origin and not to the mis-retargeted offset.
    let hipsBind = null;
    gltf.scene.traverse((o) => {
      if (o.isBone && o.name === 'Hips' && !hipsBind) hipsBind = o.position.clone();
    });
    for (const clip of gltf.animations) {
      // FIX: Mis-retargeted Mixamo clips have a huge absolute root
      // offset in Hips.position (e.g. Z=-7.13) that buries the fighter
      // underground. The game drives root.position for locomotion, so
      // animations must be in-place: pin Hips.position to bind pose.
      for (const track of clip.tracks) {
        if (track.name === 'Hips.position' && hipsBind) {
          for (let i = 0; i < track.values.length; i += 3) {
            track.values[i] = hipsBind.x;
            track.values[i + 1] = hipsBind.y;
            track.values[i + 2] = hipsBind.z;
          }
        }
      }
      this.clips[id][clip.name] = clip;
    }
    gltf.scene.traverse((o) => {
      if (o.isMesh) {
        o.castShadow = true;
        o.receiveShadow = true;
        o.frustumCulled = false;
      }
    });
    // GROUNDING (2026-10-20): some GLBs are authored with the origin
    // at the hips (star / torch / michiko / diablo: vertices span
    // y -1.05..0.8), so they stood waist-deep in the floor. The
    // instance is lifted by its own rest geometry (skinned bounds
    // include the bone transforms in three r160).
    {
      gltf.scene.updateMatrixWorld(true);
      let y0 = Infinity;
      const bb = new THREE.Box3();
      gltf.scene.traverse((o) => {
        if (!o.isSkinnedMesh) return;
        o.computeBoundingBox();
        bb.copy(o.boundingBox).applyMatrix4(o.matrixWorld);
        if (bb.min.y < y0) y0 = bb.min.y;
      });
      this.groundY[id] = Number.isFinite(y0) ? y0 : 0;
    }
    await _facingReady.then(() => {
      try {
        const rec = _facingTable && _facingTable[id];
        this.facing[id] = rec === '-Z' ? -1 : rec === '+Z' ? 1 : (feetFacingCue(gltf.scene) || 1);
      } catch (e) {
        console.warn(`[WH] facing cue failed for ${id}, defaulting to +Z:`, (e && e.message) || e);
        this.facing[id] = 1;
      }
    }, () => {
      // The facing table never settled: never let this gate hang the load.
      console.warn(`[WH] facing table unsettled for ${id}, defaulting to +Z`);
      this.facing[id] = 1;
    });
  }

  // Legacy: load all models (kept for compat, but boot no longer uses it).
  load(onProgress) {
    return this.loadModels(Object.keys(MODEL_URLS), onProgress);
  }

  // Fire-and-forget prefetch: warms the cache while the user browses select.
  // USER LANE: preempts the idle warm lane (see _abortIdle) so a tapped
  // fighter's model gets the full pipe.
  prefetch(id, opts = {}) {
    if (!id || this.gltfs[id] || this._inflight[id]) return;
    this.loadModels([id], null, { lane: 'user', ...opts })
      .catch(e => {
        if (!e || (e.name !== 'AbortError' && !/abort/i.test(e.message || ''))) {
          console.warn('[WH] prefetch failed:', id, e.message || e);
        }
      });
  }

  /* LOADSPEED (2026-10-22): idle-scheduled base warm. The old preloadAll()
     fired four base GLBs (~26MB) the instant select opened, saturating the
     connection the user's first preview taps needed. Now the select screen
     paints first; the bases stream when the browser is idle, on the lowest-
     priority lane — any user-initiated load aborts them and takes the pipe.
     'custom' only warms when a custom fighter actually exists (main.js
     passes hasCustom) — 2.2MB most sessions never need. */
  preloadBaseIdle(hasCustom = false) {
    const ids = ['pantera', 'demonio']; // steve-fox removed: no fighter falls back to it (owner 2026-10-23)
    if (hasCustom) ids.push('custom');
    const ric = (typeof window !== 'undefined' && window.requestIdleCallback)
      ? window.requestIdleCallback.bind(window)
      : (fn) => setTimeout(fn, 1200);
    ric(() => {
      for (const id of ids) {
        if (this.gltfs[id] || this._inflight[id]) continue;
        const ctrl = new AbortController();
        this._idleCtrls.add(ctrl);
        this.loadModels([id], null, { signal: ctrl.signal, lane: 'idle' })
          .catch(e => {
            if (!e || (e.name !== 'AbortError' && !/abort/i.test(e.message || ''))) {
              console.warn('[WH] idle prefetch failed:', id, e.message || e);
            }
          })
          .finally(() => this._idleCtrls.delete(ctrl));
      }
    });
  }

  // Back-compat: main.js used to call this on select open.
  preloadAll() { this.preloadBaseIdle(true); }

  /* { model, bones, mixer, actions } for one fighter.
     Per-fighter palette: suit color lerp + trim emissive accents. */
  /* tintStrength defaults to 0: fighters show their OWN authored textures
     and materials (owner 2026-10-20: "what are the fighters having that
     colored layer over their skin? fix that"). Only an explicitly
     colorized fighter (the Create-a-Fighter skin tone, `colorize: true`)
     passes a tint. */
  createInstance(fighterId, suitColor, trimColor, tintStrength = 0, eyeGlow = null) {
    const gltf = this.gltfs[fighterId];
    if (!gltf) throw new Error('unknown fighter model: ' + fighterId);
    // The instance root is a wrapper whose space always has the mesh facing
    // +Z (see MESH FACING above); callers may freely set its rotation.
    const inner = skeletonClone(gltf.scene);
    // FOREIGN-RIG REMAP (Vega only, see VEGA_T3_BONE_REMAP above):
    // rename the cloned instance's core joints to the T3 names
    // BEFORE the bones dict and mixer are built from it, so T3
    // clips + procedural IK bind. The source gltf is untouched.
    const vegaRemapped = remapVegaBones(fighterId, inner);
    // FOREIGN-RIG REMAP (Slice only, see SLICE_T3_BONE_REMAP above):
    // same contract as the Vega remap — rename the cloned
    // instance's T7 core joints to the T3 names BEFORE the bones
    // dict and mixer are built from it, so T3 clips +
    // procedural IK bind. The source gltf is untouched.
    const sliceRemapped = remapSliceBones(fighterId, inner);
    if ((this.facing[fighterId] || 1) < 0) inner.rotation.y = Math.PI;
    const gy = this.groundY[fighterId] || 0;
    if (Math.abs(gy) > 0.03) inner.position.y = -gy; // feet on the floor
    const model = new THREE.Group();
    model.name = `wh-instance:${fighterId}`;
    model.add(inner);

    const suit = new THREE.Color(suitColor);
    const trim = new THREE.Color(trimColor);
    let skinnedCount = 0;
    model.traverse((o) => {
      // Bulletproof: never rely on clone preserving render flags.
      // Skinned meshes MUST NOT be frustum-culled (their bounds are wrong
      // after skinning) and MUST be visible.
      if (o.isMesh || o.isSkinnedMesh) {
        o.frustumCulled = false;
        o.visible = true;
      }
      if (o.isSkinnedMesh) skinnedCount++;
      if (o.isMesh && o.material) {
        o.material = o.material.clone();
        if (tintStrength > 0) {
          // explicit colorize only (custom fighter skin tone)
          if (o.material.color) o.material.color.lerp(suit, tintStrength);
          o.material.emissive = o.material.emissive || new THREE.Color(0x000000);
          o.material.emissive.copy(trim).multiplyScalar(0.08);
        }
        // Never ship a transparent fighter: a bad alpha kills visibility.
        if (o.material.transparent && o.material.opacity < 0.05) {
          o.material.transparent = false;
          o.material.opacity = 1;
        }
        // EYE GLOW (owner 2026-10-22): per-attire emissive eyes, data-driven.
        // The attire slot's eyeGlow config (attires.js) names the eye meshes
        // as identified from the model (e.g. Negativo's ModelEyes_Material028)
        // plus the emissive color/intensity for THAT attire — never hardcoded
        // here. Applied after any tint so the glow color always wins. Runs in
        // fight (fighter.js) and preview (select-screen.js): both call sites
        // pass the resolved slot config through createInstance.
        if (eyeGlow && Array.isArray(eyeGlow.materials) &&
            (eyeGlow.materials.includes(o.material.name) || eyeGlow.materials.includes(o.name))) {
          o.material.emissive = new THREE.Color(eyeGlow.color ?? 0xff2222);
          o.material.emissiveIntensity = eyeGlow.intensity ?? 2.0;
        }
      }
    });
    if (skinnedCount === 0) {
      console.error(`[WH] createInstance(${fighterId}): ZERO skinned meshes — fighter will be invisible!`);
    }

    const bones = {};
    model.traverse((o) => {
      if (o.isBone) bones[o.name.replace(/^mixamorig:?/, '')] = o;
    });
    if (vegaRemapped || sliceRemapped) {
      // Mixamo-spelling aliases for fighter.js's procedural layer,
      // which reads bones.Spine1 (hurt capsule) and bones.Spine2
      // (attack origin) — Vega's and Slice's 3-bone torsos have no
      // separate Spine1/Spine2 joints. Dict aliases ONLY: node
      // names (and therefore mixer binding + skinning) are
      // unaffected.
      if (bones.Spine) bones.Spine1 = bones.Spine;
      if (bones.Chest) bones.Spine2 = bones.Chest;
    }

    const mixer = new THREE.AnimationMixer(model);
    const actions = {};
    const clips = this.clips[fighterId] || {};
    // EMBEDDED-IDLE ALIAS: Bip001-rig models (Iori, Deathfang)
    // ship 59 embedded clips including Battle_Idle / Stage_Idle
    // but no clip literally named 'Idle', so they used to fall
    // back to bind pose when standing still. When — and only
    // when — a model has no real 'Idle', register Battle_Idle
    // (preferred) or Stage_Idle as its idle in this same
    // clip-selection path. Models with a real Idle are unchanged.
    const idleClip = clips.Idle || clips.Battle_Idle || clips.Stage_Idle || null;
    for (const name of ['Idle', 'Walk', 'Run']) {
      const clip = name === 'Idle' ? idleClip : clips[name];
      // ANIMATION GATE (owner t117u): in-game fighter instances are FIGHT context.
      if (clip && checkClip(name, clip, CTX.FIGHT).ok) {
        actions[name] = mixer.clipAction(clip);
        actions[name].play();
        actions[name].setEffectiveWeight(name === 'Idle' ? 1 : 0);
      }
    }
    // CLOTHING LAYERS (worker 64): apply the player's saved per-attire
    // clothing visibility to this instance. Guarded + fire-and-forget: a
    // missing config or error here must never break instance creation.
    try { applyClothingToInstance(model, fighterId); } catch (e) {
      console.warn('[WH] clothing hook failed:', (e && e.message) || e);
    }
    return { model, bones, mixer, actions, scale: 1.0 };
  }
}

export const assets = new AssetManager();
