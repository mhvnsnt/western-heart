// PRIVATE BUILDS ONLY (same gate as the Mishima Dojo stage, js/stages.js):
// a private build copies the real Tekken 7 UI textures (Bandai Namco; kept in
// mhvnsnt/game-reverse-engineering, never in this public repo) into
// game/assets/private/t7-ui/ and sets globalThis.__WH_PRIVATE_ASSETS = true.
// The public build keeps the CSS-drawn equivalents in t7-skin.css.
const MAP = {
  '--t7-slot-red': 'SW_UI_CharacterSelect/SlotRed_OnGradient.png',
  '--t7-slot-blue': 'SW_UI_CharacterSelect/SlotBlue_OnGradient.png',
  '--t7-info-red': 'SW_UI_StageSelect/InfoRed_Base.png',
  '--t7-red-panel': 'SW_UI_StageSelect/RedPanel_Base.png',
  '--t7-result-bolt': 'SW_UI_Result_Lightning/Result_Lightning_02.png',
  '--t7-menu-base': 'SW_UI_MainMenu/Base_OnlineMenu.png',
};
export function applyT7PrivateUI(base = 'assets/private/t7-ui/') {
  if (!globalThis.__WH_PRIVATE_ASSETS) return false;
  const root = document.documentElement.style;
  for (const [v, f] of Object.entries(MAP)) root.setProperty(v, `url('${base}${f}')`);
  document.documentElement.classList.add('t7-private');
  return true;
}
applyT7PrivateUI();
