export async function loadT3Clips() {}

// DW kind binding (brawler.js imports this since the kit-pack mapping
// follow-up, 2026-11-08): the headless sim loads no DW packs, so it
// always resolves null — same contract as the real ensureDwKindMoves
// for an unbound kind (see game/js/t3anims.js DW_KIND_MOVES).
export async function ensureDwKindMoves(kind, THREE) { return null; }
