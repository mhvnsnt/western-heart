/* SPIRIT ACTIONS — 魂 ACTION (canon, owner 2026-10-23). Context-sensitive
   finishers layered ON TOP of the existing HEAT/URGE gauge (2+3); they do not
   replace it. Clean-room design study of a brawler's context finishers
   (environment/position triggers). Player-visible label: '魂 ACTION'
   (ja locale: '魂アクション'). The source game's term must never appear on screen. */
export const SPIRIT_LABEL = { en: '魂 ACTION', ja: '魂アクション' };
export const SPIRIT_FONT_STACK = '"Hiragino Sans","Noto Sans JP","Noto Sans CJK JP","Yu Gothic","Meiryo",system-ui,sans-serif';
export function spiritLabel(locale = (globalThis.navigator && navigator.language) || 'en') {
  return String(locale).toLowerCase().startsWith('ja') ? SPIRIT_LABEL.ja : SPIRIT_LABEL.en;
}
/* Triggers: each needs gauge active (HEAT/URGE on) + a context. Ordered by priority. */
export const SPIRIT_TRIGGERS = [
  { id: 'wall-crush',   ctx: s => s.foeWall != null && s.foeWall < 1.0 && s.dist < 1.6, dmg: 28 },
  { id: 'ground-stomp', ctx: s => s.foeDowned && s.dist < 1.8, dmg: 22 },
  { id: 'back-turned',  ctx: s => s.foeBackTurned && s.dist < 1.4, dmg: 26 },
  { id: 'stun-burst',   ctx: s => (s.foeStun || 0) > 0.3 && s.dist < 1.6, dmg: 24 },
  { id: 'prop-strike',  ctx: s => !!s.nearProp && s.dist < 2.0, dmg: 30 },
];
export function availableSpirit(s) {
  if (!(s.urgeOn || s.heatOn) || s.spiritUsed) return null;
  return SPIRIT_TRIGGERS.find(t => t.ctx(s)) || null;
}
/* Fire one: consumes the gauge, returns the action. Cinematic clip (show-only,
   gated from movesets) is looked up from the private show-clip bank if present. */
export function trySpirit(attacker, s, ui) {
  const t = availableSpirit(s); if (!t) return null;
  attacker._urgeOn = false; attacker._spiritUsed = true;
  const bank = globalThis.__WH_PRIVATE_ASSETS && globalThis.__WH_SHOW_CLIPS;
  const clip = bank && bank.spirit && bank.spirit[t.id] ? { id: bank.spirit[t.id], showOnly: true } : null;
  if (ui && ui.surgeFlash) { try { ui.surgeFlash(0xffd76a, 0xfff2b0); } catch (e) {} }
  return { id: t.id, damage: t.dmg, label: spiritLabel(), clip };
}
