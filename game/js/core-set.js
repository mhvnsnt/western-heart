/* game/js/core-set.js — Milestone 1 "One clean fight on the live link"
 * (docs/PROGRESSION-PLAN.md, owner direction 2026-10-29).
 *
 * The select screen and stage select show the CORE set by default: the
 * 8 starter fighters and 3 polished stages. Nothing is deleted or cut;
 * add ?roster=all to the URL to see every fighter and stage again.
 * The Pages shell bundles exactly these fighters' fight models
 * (asset-config.js SHELL_BUNDLED_MODELS), so every core pick loads.
 */
export const CORE_FIGHTERS = ['bruno', 'pantera', 'demonio', 'cyborgx', 'burger', 'chatur', 'deathfang', 'dio'];
export const CORE_STAGES = ['shrine', 'tong-nou', 'cape-jones-arena'];

/* The 31 fighters the 2026-10-29 moves sweep blocked for having no
 * playable model (docs/proof/moveset-sweep-20261028/MATRIX.md BLOCKER rows).
 * Hidden from select, never deleted: they return when they get models. */
export const MODELLESS_HIDDEN = [
  'doa-ayane',
  'doa-hayabusa',
  'doa-jannlee',
  'doa-kasumi',
  'doa-tina',
  'hugo',
  'kutz',
  'marduk',
  'megami',
  'menajerii',
  'raiden',
  'realizzt',
  'sf-cammy',
  'sf-chunli',
  'sf-dhalsim',
  'sf-guile',
  'sf-ken',
  'sf-mbison',
  'sf-ryu',
  'sf-sagat',
  'sf-vega',
  'sf-zangief',
  'sunra',
  't3-forestlaw',
  'vf-akira',
  'vf-elblaze',
  'vf-jeffry',
  'vf-kage',
  'vf-leifei',
  'vf-sarah',
  'vf-wolf',
];

const _q = typeof location !== 'undefined' ? new URLSearchParams(location.search) : new URLSearchParams();
export const SHOW_ALL = _q.get('roster') === 'all';

export function isCoreFighter(id) { return CORE_FIGHTERS.includes(id); }
export function isCoreStage(id) { return CORE_STAGES.includes(id); }
/* Select-grid filter: model-less fighters are always hidden; outside
 * ?roster=all only the core 8 show. */
export function selectVisible(id) {
  if (MODELLESS_HIDDEN.includes(id)) return false;
  return SHOW_ALL || isCoreFighter(id);
}
export function stageVisible(id) { return SHOW_ALL || isCoreStage(id); }

/* ?quick=p1,p2,stage — straight into a fight for testing. */
export function quickFightParams() {
  const v = _q.get('quick');
  if (!v) return null;
  const [p1, p2, stage] = v.split(',').map(s => s.trim()).filter(Boolean);
  return p1 ? { p1, p2: p2 || null, stage: stage || null } : null;
}
