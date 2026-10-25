/* SOUL SYSTEMS (owner 2026-10-23) — docs/design/SOUL-SYSTEMS.md.
   Built on the Tekken base as extensions; KESSHOU (finisher.js) stays THE finisher.
   • 九魂解放 NINE-SOUL RELEASE — super, full Nine-Soul Meter, 1+2+3+4 at full meter.
     HUD: meter-ready indicator (ui.setSoulReady) — no center-screen text (Tekken-exact UI, 2026-10-24).
   • 霊放 REIHOU "Spirit Release" — 1+4 while the foe is raging, costs 50 meter;
     spirit channels flare, the foe's rage is purged for the round.
   • 試練の封 TRIAL'S SEAL — decisive round-ending verdict seal (not a death).
   Per-fighter variants: game/data/soul-variants.json (tools/soul-variants/gen.mjs). */
import { detectKindlePress } from './soul-kindle.js';
export const RELEASE_COST = 100, REIHOU_COST = 50, RELEASE_DMG = 30, REIHOU_DMG = 6;
export const LABELS = { release: 'NINE-SOUL RELEASE 九魂解放', ready: 'SOUL RELEASE READY', reihou: 'REIHOU 霊放', seal: "TRIAL'S SEAL 試練の封" };
let VARIANTS = null;
export function setVariants(v) { VARIANTS = v; }
export async function loadVariants(url = new URL('../data/soul-variants.json', import.meta.url)) {
  try { VARIANTS = await (await fetch(url)).json(); } catch { VARIANTS = null; } return VARIANTS;
}
export function variantsFor(fighterId, system, formId) {
  const f = VARIANTS && VARIANTS.fighters && VARIANTS.fighters[fighterId]; if (!f) return [];
  return (formId && f.forms && f.forms[formId] && f.forms[formId][system]) || f[system] || [];
}
/* Variant pick: match the move type the fighter last used, else rotate by use count. */
export function pickVariant(f, system) {
  const id = f.char && f.char.id, list = variantsFor(id, system, f._formId); if (!list.length) return null;
  const mc = f._lastMoveType || (f.attack && (f.attack.move_class || (f.attack.heavy ? 'heavy' : null)));
  const hit = mc && list.find(v => v.moveType === mc); if (hit) return hit;
  f._soulUses = (f._soulUses || 0) + 1; return list[(f._soulUses - 1) % list.length];
}
function hitFoe(d, a, dmg, v, tag) {
  if (typeof d.receiveHit === 'function') { try { return d.receiveHit({ damage: dmg, level: 'mid', unblockable: true, name: v ? v.name : tag, soul: tag }, a); } catch (e) { } }
  else if (typeof d.hp === 'number') d.hp = Math.max(0, d.hp - dmg);
}
export class SoulSystems {
  constructor(game) { this.game = game; this._ready = { p1: false, p2: false }; this.lastSoulKill = null; this.seals = { p1: 0, p2: 0 }; }
  canRelease(f) { return !!f && (f.meter || 0) >= RELEASE_COST && (!f.canAct || f.canAct()); }
  release(a, d) {
    if (!this.canRelease(a) || !d) return null;
    const v = pickVariant(a, 'release'); a.meter -= RELEASE_COST;
    hitFoe(d, a, Math.round(RELEASE_DMG * (v ? v.power : 1)), v, 'release');
    this.lastSoulKill = a; return v || { id: 'release' };
  }
  claimRelease(a, d, queue) { return this.canRelease(a) && detectKindlePress(queue) ? !!this.release(a, d) : false; }
  canReihou(a, d) { return !!a && !!d && !!d._rageOn && (a.meter || 0) >= REIHOU_COST && (!a.canAct || a.canAct()); }
  tryReihou(a, d) {
    if (!this.canReihou(a, d)) return null;
    const v = pickVariant(a, 'reihou'); a.meter -= REIHOU_COST;
    d._rageOn = false; d._rageUsed = true; if (d.setRageAura) d.setRageAura(false);
    if (this.game && this.game.ui && this.game.ui.setRage) this.game.ui.setRage(d === this.game.p1 ? 'p1' : 'p2', false);
    a._spiritFlare = 1.0; if (a.setAuraFlare) a.setAuraFlare(1.0);
    hitFoe(d, a, REIHOU_DMG, v, 'reihou'); return v || { id: 'reihou' };
  }
  /* Per step: SOUL RELEASE READY callout when a meter first fills. */
  update() {
    const g = this.game; if (!g) return;
    for (const [f, k] of [[g.p1, 'p1'], [g.p2, 'p2']]) {
      if (!f) continue; const r = (f.meter || 0) >= RELEASE_COST;
      if (r && !this._ready[k]) { this._ready[k] = true; if (g.ui && g.ui.setSoulReady) g.ui.setSoulReady(k, true); }
      else if (!r && this._ready[k]) { this._ready[k] = false; if (g.ui && g.ui.setSoulReady) g.ui.setSoulReady(k, false); }
      if (f._spiritFlare > 0) f._spiritFlare = Math.max(0, f._spiritFlare - 1 / 120);
    }
  }
  /* 試練の封: a decisive round end — winner >= 50% HP, or the KO came from a soul system. */
  sealVerdict(winner, viaSoul) { return !!winner && (viaSoul || (winner.hp / (winner.maxHp || 100)) >= 0.5); }
  onRoundEnd(p1Down, p2Down) {
    const g = this.game; if (!g || p1Down === p2Down) { this.lastSoulKill = null; return null; }
    const w = p1Down ? g.p2 : g.p1, k = p1Down ? 'p2' : 'p1';
    const sealed = this.sealVerdict(w, this.lastSoulKill === w); this.lastSoulKill = null;
    if (!sealed) return null;
    this.seals[k]++; const v = pickVariant(w, 'seal');
    if (g.matchStats) g.matchStats.seals = { ...this.seals };
    this._banner(LABELS.seal); return v || { id: 'seal' };
  }
  _banner(t) { const ui = this.game && this.game.ui; if (ui && ui.banner) { try { ui.banner(t); } catch (e) { } } }
}
