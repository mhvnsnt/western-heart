// Western Heart roster for the menus. Source: CANON.md (names, souls, Tekken body).
// Origin is not in canon for anyone yet, so it reads "parts unknown" (owner rule).
// portrait: only fighters with a real owner GLB get a render; the rest show the
// Pantera-GLB silhouette marked MODEL PENDING (no AI faces).
// Card art that is a work-in-progress kitbash of an existing model (see docs/roster/<id>/parts.json).
const ART = {
  zui: { label: "WIP KITBASH A1", bust: "portraits/zui_a1wip_bust.png", full: "portraits/zui_a1wip_full.png" },
};
// Unlock state is data, not art: only Pantera by default. Promo/showcase: ?unlock=all
// Game progress: localStorage "wh_unlocked" = JSON array of ids.
export const DEFAULT_UNLOCKED = ["pantera"];
export function isUnlocked(id) {
  const q = typeof location !== "undefined" ? new URLSearchParams(location.search) : null;
  if (q && q.get("unlock") === "all") return true;
  let saved = [];
  try { saved = JSON.parse(localStorage.getItem("wh_unlocked") || "[]"); } catch {}
  return DEFAULT_UNLOCKED.includes(id) || saved.includes(id);
}
export const ROSTER = [
  ["pantera", "PANTERA", "The Panther Soul", "豹", "King", true],
  ["demonio", "DEMONIO", "The Demon Soul", "鬼", "Jin"],
  ["phantom", "PHANTOM", "The Ghost Blade Soul", "幽", "Yoshimitsu"],
  ["diablo", "DIABLO", "The Devil Soul", "魔", "Heihachi"],
  ["skull", "SKULL", "The Punisher Soul", "骨", "Bryan"],
  ["sam_ur_a1", "SAM-UR-A1", "The Mech Soul", "機", "Gun Jack"],
  ["saku_ra", "SAKU RA", "The Idol Soul", "桜", "Xiaoyu"],
  ["zui", "ZUI", "The Drunken Soul", "酔", "Steve"],
  ["kinpo", "KINPO", "The Buttercup Soul", "金", "Asuka"],
  ["waterfall", "WATERFALL", "The Weeping Soul", "滝", "Josie"],
  ["king_tyrant", "KING TYRANT", "The Showman Soul", "王", "Eddy"],
  ["burger", "BURGER", "The Hunger Soul", "飢", "Bob"],
  ["awa_pop", "AWA POP", "The Bubble Soul", "泡", "Nina"],
  ["scimitar", "SCIMITAR", "The Vizier Soul", "刃", "Shaheen"],
  ["purple_rain", "PURPLE RAIN", "The Performer Soul", "紫", "Lee"],
  ["nightwolf", "NIGHTWOLF", "The Guide Soul", "狼", "Julia"],
  ["michiko", "MICHIKO", "The Outlaw Soul", "道", "Katarina"],
  ["star", "STAR", "The Current Soul", "星", "Christie"],
  ["torch", "TORCH", "The Flame Soul", "炎", "Anna"],
  ["dio", "DIO", "The Demon That Is", "獄", "Akuma"],
  ["cyborg_x", "CYBORG X", "The Trapped Soul", "鋼", "Alisa"],
  ["bruno", "BRUNO", "The Heartbreak Soul", "恋", "Miguel"],
  ["negativo", "N3GΔTIV0", "The Hunter", "負", "Negan"],
].map(([id, name, soul, kanji, body, model]) => {
  const art = ART[id];
  return {
    id, name, soul, kanji, body, origin: "parts unknown", model: !!(model || art),
    art: art ? art.label : model ? "ATTIRE 1" : "MODEL PENDING",
    bust: art ? art.bust : model ? `portraits/${id}_bust.png` : "portraits/unknown_bust.png",
    full: art ? art.full : model ? `portraits/${id}_full.png` : "portraits/unknown_full.png",
    unlocked: isUnlocked(id),
  };
});
