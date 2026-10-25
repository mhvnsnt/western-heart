// Western Heart title-screen variant config (owner 2026-10-14).
// v1 "original": white 西部の心 lettering, Pantera arms folded (first ui-wh title).
// v2 "lunge":    purple パンテーラ lettering, Pantera P1 mid-lunge (grab clip @0.35s).
// v3 "folded":   v2 with Pantera's arms folded across his chest (idle clip @0.0s). DEFAULT.
// v4 "t3real": REAL decoded Tekken 3 King win pose (slot 0xD68 @3.3s) retargeted onto Pantera P1. Not default (owner picks).
// Override per launch with ?title=v1|v2|v3 (also accepts original|lunge|folded),
// or persist with localStorage wh_title.
window.WH_TITLE_CONFIG = {
  default: "v3",
  variants: {
    v1: { name: "original", wallpaper: "art/wallpaper_wh_v1.png", jp: "西部の心" },
    v2: { name: "lunge", wallpaper: "art/wallpaper_wh_v2.png", jp: "パンテーラ ・ 黒豹" },
    v3: { name: "folded", wallpaper: "art/wallpaper_wh_v3.png", jp: "パンテーラ ・ 黒豹" },
    v4: { name: "t3real", wallpaper: "art/wallpaper_wh_v4.png", jp: "パンテーラ ・ 黒豹" },
  },
};
