/* ============================================================
   WESTERN HEART — Select Card Configuration
   Per-fighter character card data, structured for customization.

   Each fighter's select card is composed of separate fields:
   - portrait:   image source for the card portrait
                  (default: assets/portraits/<fighter-id>.png)
   - background: card background art / color theme
                  (default: null = theme default; future: customizable
                  customizable backgrounds from creation suite)
   - frame:      card frame/border style
                  (default: 'standard'; future: unlockable frames)

   Tekken-style card customization (portrait select, background cards,
   frame variants) plugs into this structure — the creation suite writes
   per-fighter overrides into CARD_CONFIG, and the select screen reads
   them via getCardConfig(). No visual change until overrides exist.

   UI source: teardown-sourced select screen (see game/ui_sources.json
   screen-select). This module is data structure only — no new visuals.
   ============================================================ */

const PORTRAIT_BASE = 'assets/portraits';

const DEFAULT_CARD = Object.freeze({
  portrait: null,    // null = PORTRAIT_BASE/<id>.png
  background: null,  // null = theme default
  frame: 'standard', // future: 'gold', 'soul', custom frames
  status: 'ready',   // 'ready' | 'coming_soon' — from model-readiness.json
});

/* Model readiness, loaded from game/data/model-readiness.json at runtime
   (same pattern as tripo-fighters.json). Fighters whose status is not
   'ready' get a MODEL COMING placeholder card — NEVER a broken body.
   Owner law 2026-10-23: broken/untextured/wrong-model fighters never
   appear on select, permanently, via CI guard select-model-guard.test.mjs. */
let READINESS = null;
export function setReadiness(data) {
  READINESS = data && data.fighters ? data.fighters : null;
}
export function modelStatus(fighterId) {
  if (READINESS && READINESS[fighterId]) return READINESS[fighterId].status || 'ready';
  const over = CARD_CONFIG[fighterId] || {};
  return over.status || DEFAULT_CARD.status;
}
export function isModelReady(fighterId) {
  return modelStatus(fighterId) === 'ready';
}

/* Per-fighter overrides. Empty by default — every fighter uses DEFAULT_CARD
   until the user customizes cards in the creation suite (Tekken-style card
   customization from teardown parts). */
export const CARD_CONFIG = {
  // e.g. 'pantera': { portrait: 'assets/portraits/pantera-alt.png', background: 'ember', frame: 'gold' },
};

export function getCardConfig(fighterId) {
  const over = CARD_CONFIG[fighterId] || {};
  return {
    portrait: over.portrait || `${PORTRAIT_BASE}/${fighterId}.png`,
    background: over.background ?? DEFAULT_CARD.background,
    frame: over.frame || DEFAULT_CARD.frame,
    status: modelStatus(fighterId),
  };
}

/* Card tier for the select strip grouping. Kept here so the strip builder
   and any future card UI share one source of truth. */
export function cardTier(fighterId, tripoIds) {
  return tripoIds && tripoIds.has(fighterId) ? 'tripo' : 'main';
}
