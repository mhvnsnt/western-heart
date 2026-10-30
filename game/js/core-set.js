/* game/js/core-set.js — Milestone 1 "One clean fight on the live link"
 * (docs/PROGRESSION-PLAN.md, owner direction 2026-10-29).
 *
 * Milestone 1 showed the CORE set by default: the 8 starter fighters
 * and 3 polished stages, with ?roster=all showing the rest.
 *
 * OWNER REVERSAL (2026-10-29, later the same day): "Bring all the
 * fighters back to the fighter select screen" + "Put all my western
 * heart arenas back in the stage select list." The full roster and the
 * full stage list are the default again — the deployable version the
 * owner asked for. The CORE sets stay defined here because the Pages
 * shell bundles exactly the core fighters' fight models
 * (asset-config.js SHELL_BUNDLED_MODELS) and ?quick= defaults to core
 * picks; every other fighter's model loads from the remote asset base
 * at runtime, exactly as it did before Milestone 1. Nothing is deleted.
 */
export const CORE_FIGHTERS = ['bruno', 'pantera', 'demonio', 'cyborgx', 'burger', 'chatur', 'deathfang', 'dio'];
export const CORE_STAGES = ['shrine', 'tong-nou', 'cape-jones-arena'];

/* The 31 fighters the 2026-10-29 moves sweep blocked for having no
 * playable model (docs/proof/moveset-sweep-20261028/MATRIX.md BLOCKER rows).
 * Kept as the record of who still lacks a model. As of the owner's
 * 2026-10-29 reversal above this list no longer hides anyone from
 * select — they were on the pre-Milestone-1 deployable select and the
 * owner ordered all fighters back. */
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
/* Select-grid + stage-select filters (owner order 2026-10-29): every
 * fighter and every stage shows by default, restoring the deployable
 * select screens from before the Milestone 1 core-only default. The
 * select screen's own SELECT_HIDDEN set (the nine souls and other
 * entries with no body of their own, owner law 2026-10-22) still
 * applies in select-screen.js — those were never standalone cards on
 * the deployable version either. */
export function selectVisible(id) { return true; }
export function stageVisible(id) { return true; }

/* ?quick=p1,p2,stage — straight into a fight for testing. */
export function quickFightParams() {
  const v = _q.get('quick');
  if (!v) return null;
  const [p1, p2, stage] = v.split(',').map(s => s.trim()).filter(Boolean);
  return p1 ? { p1, p2: p2 || null, stage: stage || null } : null;
}
