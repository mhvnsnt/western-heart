/* ============================================================
   WESTERN HEART — Attire picker (Stream 4 parity push, item 3)
   Every fighter's attires browsable and selectable, mobile touch.
   Attires are model variants (MODEL_URLS keys in assets.js).
   Selection persists per-fighter in localStorage `wh_attires_v1`
   and is applied when the fighter is confirmed for a match.
   ============================================================ */

import { FULL_ROSTER } from './roster-full.js';

const LS_KEY = 'wh_attires_v1';
// Fighter ids: a model key that is another fighter's own id is that fighter's body.
const FIGHTER_IDS = new Set(FULL_ROSTER.map(f => f.id));

/* model base -> [{ model, label }]. Labels from owner notes / CANON.md.
   Fighters not listed here get a single default (their base model). */
export const ATTIRE_VARIANTS = {
  // RAVE / Kiko Tanaka — roster/TRIPO-REGISTRY.md slot order
  'kiko-tanaka': [
    { model: 'kiko-tanaka', label: 'ATTIRE 1 · HOODED' },
    { model: 'kiko-tanaka_alt1', label: 'ATTIRE 2 · GHOST TANAKA' },
    { model: 'rave', label: 'ATTIRE 3 · MUTA' },
  ],
  'thor': [
    { model: 'thor', label: 'ATTIRE 1' },
    { model: 'thor-attire2', label: 'ATTIRE 2 · ONI MASK' },
  ],
  /* NEGATIVO's ladder (owner 2026-10-22): per-attire EYE GLOW — each slot
     carries its own emissive eye config (data-driven, never hardcoded in the
     renderer). Attire 1 = glowing RED eyes, Attire 2 (before the trials) =
     glowing WHITE eyes. `materials` names the eye meshes as identified from
     the model (n3g4tiv0.glb's dedicated eye material ModelEyes_Material028).
     Slot 2 is pending: its Tripo original is archived (immutable) at
     roster/negativo/attires/attire2/source/ but the rigged playable model
     hasn't landed — the white-eye config is wired and waiting; the picker
     hides pending slots (selectableAttires) so nothing unplayable shows. */
  'negativo': [
    { model: 'n3g4tiv0', label: 'ATTIRE 1',
      eyeGlow: { color: 0xff2222, intensity: 2.4, materials: ['ModelEyes_Material028'] } },
    { model: 'negativo-attire2', label: 'ATTIRE 2 · BEFORE THE TRIALS (PARKED — AWAITING RIG)',
      pending: true,
      eyeGlow: { color: 0xffffff, intensity: 2.4, materials: ['ModelEyes_Material028'] } },
  ],
  /* TORCH's ladder — keyed by fighter id ('torch'; attiresFor() falls back
     to the id when the model key misses), same pattern as Doc Frank's and
     Kevin's ladders. LADDER ORDER (owner rule 2026-10-21): her Tripo
     original at the FOREFRONT; the Anna Williams base model ladders BACK
     behind it. Default = first entry = Attire 1 'Valkyrie of Flame'
     (also the main roster entry's model). Provenance per slot:
     roster/torch/ATTIRE-SLOTS.md. */
  'torch': [
    { model: 'torch-tripo-a1', label: 'ATTIRE 1 · VALKYRIE OF FLAME (TRIPO)' },
    { model: 'torch-tripo-a2', label: 'ATTIRE 2 · RED DEMON (TRIPO)' },
    { model: 'torch', label: 'ANNA BASE (TEKKEN BASE)' },
  ],
  'demonio': [
    { model: 'demonio', label: 'BASE' },
    { model: 'demonio-a1', label: 'ATTIRE 1' },
    { model: 'demonio-winged', label: 'WINGED DEVIL' },
    { model: 'demonio-human', label: 'HUMAN' },
    { model: 'demonio-bloodline-ember', label: 'BLOODLINE EMBER' },
  ],
  'deathfang': [
    { model: 'deathfang', label: 'ATTIRE 1 · CHAINED PRISONER' },
    { model: 'deathfang-werewolf', label: 'ATTIRE 2 · WEREWOLF' },
  ],
  /* DOC FRANK's ladder — keyed by fighter id ('docfrank'), same pattern as
     Kevin's ladder below: attiresFor() looks up fighter.model, then
     fighter.id (model-key audit, docs/MODEL-KEY-AUDIT-2026-10-21.md).
     LADDER ORDER (owner override 2026-10-21 ~23:14 CDT, verbatim: "his
     1, 2, 3, 4, 5 should be his Tripo models; the Tekken reskins go toward
     the back, not 1 or 2. Stop showing me the Tekken versions first —
     show the Tripo 3D models I made for him."): every Tripo model (all
     four attires, base + transformed forms, pairs together) ladders FIRST;
     the Tekken-based models ladder BACK. That includes Attire 1's pre-form
     old man ('doc-frank-a1'): its file lineage is the PR #263 machine-shop
     texture reskin of the Bosconovitch base, so per the owner's override it
     sits with the back-slot Tekken entries, not at the forefront (this
     supersedes the 2026-10-21 ~19:08 CDT rule that had put it first).
     Default = first entry = Attire 1's Tripo bigger form ('doc-frank-big').
     Provenance per slot: roster/doc-frank/ATTIRE-SLOTS.md.
     NOTE: with the Tripo bigger form as the default, TRANSFORM from the
     default swaps big->big (no visual change); picking a back-slot old-man
     form and transforming still lands on the Tripo bigger form. */
  'docfrank': [
    { model: 'doc-frank-big', label: 'ATTIRE 1 · TRANSFORMED (TRIPO)' },
    { model: 'doc-frank-wowomomo', label: 'ATTIRE 2 · WOWOMOMO (TRIPO)' },
    { model: 'doc-frank-wowomomo-big', label: 'ATTIRE 2 · WOWOMOMO XL (TRIPO)' },
    { model: 'doc-frank-hood', label: 'ATTIRE 3 · HOOD SCIENTIST (TRIPO)' },
    { model: 'doc-frank-hood-big', label: 'ATTIRE 3 · HOOD XL (TRIPO)' },
    { model: 'doc-frank-frankenstein', label: "ATTIRE 4 · FRANKENSTEIN'S CYBORG (TRIPO)" },
    { model: 'doc-frank-frankenstein-big', label: 'ATTIRE 4 · FRANKENSTEIN XL (TRIPO)' },
    { model: 'doc-frank-a1', label: 'ATTIRE 1 · OLD MAN (TEKKEN RESKIN)' },
    { model: 'doc-frank', label: 'BOSCONOVITCH BASE (TEKKEN CANON)' },
    { model: 'doc-frank-machine-shop', label: 'MACHINE SHOP (TEKKEN RESKIN)' },
  ],
  /* MARIPOSA's ladder — re-keyed 2026-10-22 to her roster card id
     ('mariposa-monarch'): the old 'mariposa' key matched no fighter id or
     model, so the whole documented slot map (roster/mariposa/ATTIRE-SLOTS.md:
     "Mariposa is ONE character ... Never split into two characters") was
     unreachable from her picker. Ladder contents/order untouched — Butterfly
     Default stays the owner-designated Slot 1 default. DEDUP 2026-10-22:
     ladder order corrected to the slot map — Slot 1 Butterfly Default first
     (owner 2026-10-19 exception to the Tripo-first law, like Pantera's
     Attire 1), Slot 2 Tripo, Slot 3 Monarch (owner-locked), Slot 6+ the
     Tekken Zafina in-game model ladders BEHIND every custom attire (Zafina
     is never a separate fighter — Mary Posa goes over her).
     'mariposa-slot2' omitted: byte-identical to 'mariposa'
     (roster/TRIPO-REGISTRY.md). */
  'mariposa-monarch': [
    { model: 'mariposa-butterfly-default', label: 'SLOT 1 · BUTTERFLY DEFAULT' },
    { model: 'mariposa', label: 'SLOT 2 · TRIPO' },
    { model: 'mariposa-monarch', label: 'SLOT 3 · MONARCH' },
    { model: 'zafina-golden-pharaoh', label: 'GOLDEN PHARAOH (WH RESKIN)' },
    { model: 'zafina', label: 'SLOT 6+ · TEKKEN ZAFINA' },
  ],
  'burger': [
    { model: 'burger', label: 'ATTIRE 1 · DEMON' },
    { model: 'burger-attire2', label: 'ATTIRE 2' },
    { model: 'burger-attire3', label: 'ATTIRE 3' },
    { model: 'burger-attire4', label: 'ATTIRE 4' },
    { model: 'burger-attire5', label: 'ATTIRE 5' },
    { model: 'burger-attire6', label: 'ATTIRE 6' },
    { model: 'burger-attire7', label: 'ATTIRE 7' },
  ],
  'cain-elias': [
    { model: 'cain-elias', label: 'ATTIRE 1 · BIKER' },
    { model: 'cain-elias-attire2', label: 'ATTIRE 2 · FIGHT GEAR' },
  ],
  'vainabel': [
    { model: 'vainabel-attire2', label: 'ATTIRE 2' },
    { model: 'vainabel-attire3', label: 'ATTIRE 3 · MASKED DEMON OF THE PURPLE HAZE' },
    { model: 'vainabel-attire4', label: 'ATTIRE 4 · HALF MASK HORROR OF THE HAZE' },
  ],
  /* DXMMII's ladder — re-keyed 2026-10-22 to its roster card id
     ('dxmmii-patchwork'): the old 'dxmmii' key matched no fighter id or
     model, so the slot map (roster/dxmmii/ATTIRE-SLOTS.md) was unreachable
     from its picker. DEDUP 2026-10-22: ladder order corrected to the slot
     map (roster/dxmmii/ATTIRE-SLOTS.md) — Slot 1 = the 60MB Tripo Default
     that replaced the wooden dummy per owner 2026-10-19 (the old 'dxmmii'
     base key was the retired dummy, so it no longer leads); Slot 2 =
     Patchwork DJ (owner-approved 2026-10-18); Slot 3 = Blockhead. */
  'dxmmii-patchwork': [
    { model: 'dxmmii-tripo', label: 'SLOT 1 · TRIPO DEFAULT' },
    { model: 'dxmmii-patchwork', label: 'SLOT 2 · PATCHWORK DJ' },
    { model: 'dxmmii-a2', label: 'SLOT 3 · BLOCKHEAD' },
  ],
  /* KEVIN's ladder (owner 2026-10-20): A1 = kevin-tripo (his face, pending
     rig/wiring), A2 = original Baek model, A3 = Master White (PARKED).
     Keyed by fighter id so Kevin's entry finds it. */
  'baek-master-white': [
    { model: 'kevin-tripo', label: 'KEVIN · A1 TRIPO (DEFAULT)' },
    { model: 'baek', label: 'KEVIN · A2 BAEK MODEL' },
    { model: 'baek-master-white', label: 'MASTER WHITE (PARKED)' },
  ],
  'purple-rain': [
    { model: 'purple-rain', label: 'BASE' },
    { model: 'purple-rain-main', label: 'MAIN' },
  ],
  'saku-ra': [
    { model: 'saku-ra', label: 'BASE' },
    { model: 'saku-ra-main', label: 'MAIN' },
  ],
  /* PHANTOM's ladder — JIN re-homed here 2026-10-22 (owner directive:
     "Yoshimitsu is supposed to ladder into Phantom's attires, not stand
     alone"). Canon: Phantom is the vessel of JIN, the Blade Soul
     (CANON.md). Model preserved, just re-homed from the removed 'jin_soul'
     card. */
  'phantom': [
    { model: 'phantom', label: 'BASE' },
    { model: 'phantom-t8', label: 'T8' },
    { model: 'steve-fox', label: 'JIN · BLADE SOUL' },
    { model: 'jin-bloodline-ember', label: 'JIN KAZAMA · BLOODLINE EMBER (TEKKEN RESKIN)' },
  ],
  /* CHARGER's ladder (dedup 2026-10-22): the standalone 'charger-attire2'
     card folded in (owner rule: attires ladder into their fighter). Without
     this list Attire 2 would be unreachable — no key existed before. Labels
     from the folded cards' titles. */
  'charger': [
    { model: 'charger', label: 'ATTIRE 1 · ICE MONSTER' },
    { model: 'charger-attire2', label: 'ATTIRE 2 · WILD CURRENT' },
  ],
  /* KINPO's ladder — slot order per roster/kinpo/ATTIRE-SLOTS.md (owner 2026-10-20):
     Slot 1 = Tripo main, Slot 2 = "Goth Sport" Tripo (was wired as a MODEL_URLS
     key with no variant list, unreachable from the picker), Slot 3+ = T8 alts. */
  'kinpo': [
    { model: 'kinpo', label: 'ATTIRE 1 · TRIPO' },
    { model: 'kinpo-attire2', label: 'ATTIRE 2 · GOTH SPORT (TRIPO)' },
    { model: 'kinpo-t8', label: 'T8' },
  ],
  /* KING TYRANT's ladder (wire-up 2026-10-22): his four owner Tripo originals
     (roster/king-tyrant/attires/ATTIRE-SLOTS.md) were on disk with no MODEL_URLS
     keys and no variant list. Slot order = the slot map; the in-game base
     build ladders back. */
  'king-tyrant': [
    { model: 'king-tyrant-attire1', label: 'ATTIRE 1 · WHITE TYRANT (TRIPO)' },
    { model: 'king-tyrant-attire2', label: 'ATTIRE 2 · TYRANT KING (TRIPO)' },
    { model: 'king-tyrant-attire3', label: 'ATTIRE 3 · BLACK SNOW (TRIPO)' },
    { model: 'king-tyrant-attire4', label: 'ATTIRE 4 · FIGHT GEAR (TRIPO)' },
    { model: 'king-tyrant', label: 'BASE BUILD (TEKKEN BASE)' },
  ],
  /* NIGHTWOLF's ladder (wire-up 2026-10-22): his Tripo "tribal warrior" DEFAULT
     (roster/nightwolf/attires/ATTIRE-SLOTS.md, tribute to Serena Misae Brown)
     was on disk with no key. Tripo first per the display law; base ladders back. */
  'nightwolf': [
    { model: 'nightwolf-attire1', label: 'ATTIRE 1 · TRIBAL WARRIOR (TRIPO)' },
    { model: 'nightwolf', label: 'BASE BUILD (TEKKEN BASE)' },
  ],
  /* DIABLO's ladder (fighter-completeness audit 2026-10-21): Attire 2
     "Devil God" was wired as a MODEL_URLS key + GLB (PR #419) but had no
     variant list, so the picker only ever offered Attire 1. Labels from
     roster/diablo/ATTIRE-SLOTS.md. First entry stays the current default. */
  'diablo': [
    { model: 'diablo', label: 'ATTIRE 1 · FANTASY DEMON' },
    { model: 'diablo-attire2', label: 'ATTIRE 2 · DEVIL GOD' },
  ],
  /* KRONOS's ladder (fighter-completeness audit 2026-10-21): Attires 2
     "Timberwolf" and 3 "TimberWolf Fully Suited" keys + GLBs existed
     (roster/kronos/ATTIRE-SLOTS.md marks them wired) but no variant list
     reached them. First entry stays the current default. */
  'kronos': [
    { model: 'kronos', label: 'ATTIRE 1' },
    { model: 'kronos-attire2', label: 'ATTIRE 2 · TIMBERWOLF' },
    { model: 'kronos-attire3', label: 'ATTIRE 3 · TIMBERWOLF FULLY SUITED' },
  ],
  /* MICHIKO's ladder (owner 2026-10-21, Tripo-first rule): her two Tripo
     originals lead — Attire 1 "bone goddess amazonian M rated nude attire
     with bone accessories" (owner's words), Attire 2 "biker chick" — and
     the Katarina-based source model ladders back as the fallback.
     Provenance per slot: roster/michiko/ATTIRE-SLOTS.md. First entry =
     default = Attire 1. */
  'michiko': [
    { model: 'michiko-attire1', label: 'ATTIRE 1 · BONE GODDESS (TRIPO)' },
    { model: 'michiko-attire2', label: 'ATTIRE 2 · BIKER CHICK (TRIPO)' },
    { model: 'michiko', label: 'KATARINA BASE (TEKKEN BASE)' },
  ],
  /* AWA POP's ladder (fighter-completeness audit 2026-10-21): Attire 2's
     GLB sat in roster/awa-pop/attires/attire2/ with no MODEL_URLS key and
     no variant list. Key added in assets.js. First entry = current default. */
  'awa-pop': [
    { model: 'awa-pop', label: 'ATTIRE 1' },
    { model: 'awa-pop-attire2', label: 'ATTIRE 2' },
  ],
  /* PANTERA's ladder — owner reorder 2026-10-21: his TRIPO ORIGINALS at
     the forefront (slots 1-2), the Tekken-version reskins ladder BACK
     behind them. This supersedes the 2026-10-17 Pantera exception (the
     T7King reskin sat at Attire 1 because he did the reskin first) and
     the 2026-10-20 swap. Audited Tripo inventory (roster/TRIPO-REGISTRY.md
     + docs/ROSTER-COUNT-CANON-2026-10-21.md): exactly TWO Pantera Tripo
     originals exist — Leo man (owner-provided via Google Drive,
     'pantera-leoman') and Leopard King (Tripo 094c2f37,
     'pantera-leopard-king'). The reskins keep their previous relative
     order behind them. Default = first entry = Leo man (selectedAttireModel
     returns list[0]). Provenance per slot:
     roster/pantera/attires/ATTIRE-SLOTS.md. The base 'pantera' MODEL_URLS
     key itself is untouched — the souled vessels ride it. */
  'pantera': [
    { model: 'pantera-leoman', label: 'ATTIRE 1 · LEO MAN (TRIPO)' },
    { model: 'pantera-leopard-king', label: 'ATTIRE 2 · LEOPARD KING (TRIPO)' },
    { model: 'pantera', label: 'ATTIRE 3 · T7 KING P1 RESKIN' },
    { model: 'pantera-snow-leopard', label: 'ATTIRE 4 · SNOW LEOPARD' },
    { model: 'pantera-crimson-rage', label: 'ATTIRE 5 · CRIMSON RAGE' },
    { model: 'pantera-p2', label: 'ATTIRE 6 · T7 P2' },
  ],
  /* SLICE's ladder (owner 2026-10-21 ~08:42 CDT): A1 = the owner's own Tripo
     (DEFAULT — skull mask, jagged chrome arm blades), A2 = our Dragunov build
     (PR #433, was A1; laddered back byte-identical, never deleted). Keyed by
     his roster model id 'slice' — attiresFor finds it on the model lookup. */
  'slice': [
    { model: 'slice-attire1', label: 'ATTIRE 1 · SKULL MASK (OWNER TRIPO)' },
    { model: 'slice-attire2', label: 'ATTIRE 2 · T7 DEFAULT — BERET (DRAGUNOV BUILD)' },
  ],
  /* STAR's ladder (wire-up 2026-10-22): her Tripo main + colorways
     (roster/star/ATTIRE-SLOTS.md, Tripo ea73eeb3) sat in roster/star/attires/
     with no MODEL_URLS keys and no variant list. Slot order = the slot map:
     Tripo A1 DEFAULT first, colorways next, the house-49 Classic ladders back. */
  'star': [
    { model: 'star-attire1', label: 'ATTIRE 1 · RED LATEX (TRIPO)' },
    { model: 'star-attire2', label: 'ATTIRE 2 · AFTER DARK' },
    { model: 'star-attire3', label: 'ATTIRE 3 · CAPOEIRA GOLD' },
    { model: 'star-attire5', label: 'ATTIRE 5 · RATED-M' },
    { model: 'star', label: 'CLASSIC (HOUSE-49)' },
  ],
  /* SILVERTONGUE's ladder (wire-up 2026-10-22): all four attires
     (roster/silvertongue/ATTIRE-SLOTS.md — Slot 1 Tripo "Metallic Bodysuit",
     Slot 2 Spy Debut, Slot 3 Rated-M Nude, Slot 4 Noir Gala) sat on disk with
     no MODEL_URLS keys and no variant list. Keyed by her fighter name so the
     picker resolves the moment her select card lands; no roster entry is
     created here (owner roster decision). */
  'silvertongue': [
    { model: 'silvertongue', label: 'ATTIRE 1 · METALLIC BODYSUIT (TRIPO)' },
    { model: 'silvertongue-spy-debut', label: 'ATTIRE 2 · SPY DEBUT' },
    { model: 'silvertongue-attire3', label: 'ATTIRE 3 · RATED-M NUDE' },
    { model: 'silvertongue-noir-gala', label: 'ATTIRE 4 · NOIR GALA' },
  ],
  /* ZUI's ladder (model-key audit follow-up, 2026-10-21): A1 = Drunken Monk
     Tripo (DEFAULT), A2 = Rework v2 Tripo; the steve-fox canon base and the
     T7 Steve reskins (zui_alt1/zui_alt2) ladder back as alternates. Keyed by
     fighter id — his roster model is 'zui-attire1', so attiresFor's id
     fallback is what finds this list (same pattern as Kevin's entry above). */
  /* ZEN — keyed by fighter id ('zen'); his model key is also 'zen', so the
     ladder resolves either way. Attire 1 = his SPIRIT BODY (owner Tripo
     8c46e379, 2026-10-21) — Zen is unvesseled; this is his own body, his
     main model. His legacy body (game/assets/models/zen-body.glb, key
     'zen-body') ladders back as Attire 2, never deleted. His SPIRIT FORM
     ('zen-spirit', roster/zen/spirit/model.glb) is deliberately NOT in
     this ladder: it is not an attire — it is Zen himself as a spirit, a
     separate model entity in the stand system. */
  'zen': [
    { model: 'zen-attire1', label: 'ATTIRE 1 · SPIRIT BODY (TRIPO)' },
    { model: 'zen-body', label: 'ATTIRE 2 · LEGACY BODY' },
  ],
  'zui': [
    { model: 'zui-attire1', label: 'ATTIRE 1 · DRUNKEN MONK (TRIPO)' },
    { model: 'zui-attire2', label: 'ATTIRE 2 · REWORK V2' },
    { model: 'steve-fox', label: 'BASE · STEVE FOX (CANON)' },
    { model: 'zui_alt1', label: 'ALT 1 · T7 STEVE RESKIN' },
    { model: 'zui_alt2', label: 'ALT 2 · T7 STEVE RESKIN' },
  ],
};

function loadMap() {
  try { return JSON.parse(localStorage.getItem(LS_KEY) || '{}'); }
  catch (e) { return {}; }
}
function saveMap(m) {
  try { localStorage.setItem(LS_KEY, JSON.stringify(m)); } catch (e) {}
}

/** Attires available for a roster fighter (by model, falls back to roster id). */
export function attiresFor(fighter) {
  if (!fighter) return [];
  // A soul riding another fighter's body (TOU / KAI / RETSU / GYOU on 'pantera') keeps that base model:
  // the body owner's ladder (Pantera's Tripo-first reorder, 2026-10-21) is his, not the riders'
  // (game/tests/model-key-guard.test.mjs "declared-base riders stay on their declared base").
  const ridesOther = fighter.model && fighter.model !== fighter.id && FIGHTER_IDS.has(fighter.model);
  const list = ridesOther ? ATTIRE_VARIANTS[fighter.id] : (ATTIRE_VARIANTS[fighter.model] || ATTIRE_VARIANTS[fighter.id]);
  if (list && list.length) return list;
  // Default: single attire = the fighter's own model
  return [{ model: fighter.model || 'pantera', label: 'ATTIRE 1' }];
}

/** The persisted attire model id for this fighter (or their base).
 * Pending slots (model not yet playable — e.g. Negativo Attire 2 awaiting its
 * rig) are never selectable: the default and any stale saved choice fall back
 * to the first playable slot. */
export function selectedAttireModel(fighter) {
  const map = loadMap();
  const list = selectableAttires(fighter);
  const saved = map[fighter.id];
  if (saved && list.some(a => a.model === saved)) return saved;
  return list[0].model;
}

/** Attire slots the picker may offer: pending (not yet playable) slots stay
 * in the config (their per-attire data, like eyeGlow, is wired and waiting)
 * but are hidden from selection until their model lands. */
export function selectableAttires(fighter) {
  return attiresFor(fighter).filter(a => !a.pending);
}

/** Per-attire eye-glow config for a model id (owner 2026-10-22): each attire
 * slot carries its own emissive eye color — e.g. Negativo Attire 1 red,
 * Attire 2 (before the trials) white. Undefined when the slot has none. */
export function attireEyeGlow(fighter, modelId) {
  const slot = attiresFor(fighter).find(a => a.model === modelId);
  return slot ? slot.eyeGlow : undefined;
}

/** Persist the attire choice for a fighter. */
export function setAttire(fighter, modelId) {
  const map = loadMap();
  map[fighter.id] = modelId;
  saveMap(map);
}

/** The label for a model id within a fighter's attire list. */
export function attireLabel(fighter, modelId) {
  const a = attiresFor(fighter).find(x => x.model === modelId);
  return a ? a.label : 'ATTIRE 1';
}

/**
 * Resolve a roster fighter to the version used in a match:
 * a shallow copy with `model` swapped to the selected attire.
 * Carries the selected attire slot's `eyeGlow` (per-attire emissive eye
 * config, owner 2026-10-22) so the renderer applies the right eye color.
 * The original roster entry is never mutated.
 */
export function resolveFighterAttire(fighter) {
  if (!fighter) return fighter;
  const model = selectedAttireModel(fighter);
  return { ...fighter, model, eyeGlow: attireEyeGlow(fighter, model) };
}
