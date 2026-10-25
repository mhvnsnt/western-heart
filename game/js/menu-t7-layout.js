/* T7 main menu / mode select / options proportion system (owner t182u
   follow-up to PR #901, 2026-10-23). Every number below is measured from
   the real Tekken 7 files in the private repo mhvnsnt/game-reverse-engineering
   (teardown/tekken7-steam/, 1920x1080 authoring) -- see
   docs/select-redesign/T7-PROPORTIONS.md "Menus":
     SW_UI_MainMenu/Base_OnlineMenu.png      572x1080  -> menu column 29.8% W,
                                                         drawn alpha rows 0..1004
     tkdata/list/SW_UI_MainMenu.bin          MainMenu_mc.Main0..Main13 (14 slots)
                                             -> slot pitch 1004/14 = 71.7 px
                                             SubMenu_mc.SubMenu_Base_mc.Sub0..Sub9
     SW_UI_PauseMenu_Replay/Cursor_Sub.png   688x80    -> sub row 35.8% W x 80 px
     SW_UI_PauseMenu_Replay/NavigationBar_Waku.png 1264x48 -> help bar 48 px
     tkdata/list/SW_UI_Option.bin            ListArea_mc Title1/Title2 + List1
                                             Panel0..11 (OptionName | OptionValue)
     SW_UI_ControllerSetup/PanelBase1.png    560x40    -> option row 40 px
     SW_UI_StoryMode_Option/Win_3line.png    1168x372  -> option window 60.8% W
   Phones: landscape scales by height (s = H/1080, T7's own axis);
   portrait has no 16:9 frame, so the 572-wide column is scaled to fill the
   width (s = W/572). Touch floors (44 px) only ever grow a row, never
   re-shape the layout. */
export const T7M = {
  ref: [1920, 1080], column: 572, columnDrawnH: 1004, mainSlots: 14,
  sub: [688, 80], subSlots: 10, nav: 48, optRow: 40, optWin: 1168, touch: 44,
};

export function menuMetrics(W, H, items = 10) {
  const land = W > H;
  const s = land ? H / T7M.ref[1] : W / T7M.column;
  const colW = land ? Math.round(W * T7M.column / T7M.ref[0]) : W;
  const nav = Math.max(24, Math.round(T7M.nav * s));
  const pitchT7 = (T7M.columnDrawnH / T7M.mainSlots) * s;
  // landscape: the column is the full height (T7), minus the nav bar
  const avail = land ? H - nav : H;
  const pitch = Math.round(Math.max(pitchT7, Math.min(T7M.touch, avail / items)));
  const subW = land ? Math.round(W * T7M.sub[0] / T7M.ref[0]) : W;
  const subH = Math.round(Math.max(T7M.sub[1] * s, T7M.touch));
  const optW = land ? Math.round(W * T7M.optWin / T7M.ref[0]) : Math.round(W - 16);
  const optH = Math.round(Math.max(T7M.optRow * s, T7M.touch));
  return { land, s, colW, nav, pitch, subW, subH, optW, optH };
}

export function layoutMenus() {
  const m = menuMetrics(innerWidth, innerHeight,
    document.querySelectorAll('#mm-list .mm-item').length || 10);
  const r = document.documentElement.style;
  r.setProperty('--t7m-col-w', m.colW + 'px');
  r.setProperty('--t7m-pitch', m.pitch + 'px');
  r.setProperty('--t7m-nav', m.nav + 'px');
  r.setProperty('--t7m-sub-w', m.subW + 'px');
  r.setProperty('--t7m-sub-h', m.subH + 'px');
  r.setProperty('--t7m-opt-w', m.optW + 'px');
  r.setProperty('--t7m-opt-h', m.optH + 'px');
  r.setProperty('--t7m-s', m.s.toFixed(4));
  document.documentElement.classList.add('t7m');
  document.documentElement.classList.toggle('t7m-land', m.land);
}

let raf = 0;
const schedule = () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(layoutMenus); };
addEventListener('resize', schedule);
addEventListener('orientationchange', schedule);
if (document.readyState === 'loading') addEventListener('DOMContentLoaded', schedule); else schedule();
