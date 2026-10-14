# Title screen variants (owner, 2026-10-14)

| id | name | lettering | Pantera pose | wallpaper |
|---|---|---|---|---|
| v1 | original | white 西部の心 | arms folded (idle clip @0.0s, portrait camera) | art/wallpaper_wh_v1.png (restored byte-for-byte from c48c3817) |
| v2 | lunge | purple パンテーラ ・ 黒豹 | grab clip @0.35s, title camera | art/wallpaper_wh_v2.png (= current wallpaper_wh.png, kept) |
| v3 | folded, **DEFAULT** | purple, same as v2 | idle clip @0.0s (v1's pose), title camera | art/wallpaper_wh_v3.png |

Select: `game/ui-wh/title-config.js` (`default: "v3"`), or `?title=v1|v2|v3` (aliases original|lunge|folded), or localStorage `wh_title`. In the game, `?ui=wh&title=v1` passes through ui-wh-bridge.js.

## How v3 was made (no hand posing)
- Pose source: pantera_leoman.glb's own `idle` clip at 0.0s, which is the exact pose v1 used (render_ui_portraits.gd). Clips in the GLB: block, grab, heavy, hit, idle, ko, light, medium, walk_back, walk_fwd, win.
- Render: `lab/game/tools/render_title_hero.gd -- <out> idle 0.0`, the same camera, rotation, lights and environment as v2. Re-running it with `grab 0.35` reproduces v2's pantera_hero.png pixel-for-pixel (zero diff), so v2 and v3 come from the same render setup.
- Composite: `python3 game/ui-wh/tools/make_wallpaper.py v3`. One adjustment: the folded silhouette is wider and taller than v2's crop box, so v3 is cropped with (213,131,844,1144) instead of (235,144,844,1144). It's placed with v2's scale factor and the box offset, so the body sits in the same screen position at the same scale. Running the script without an argument still reproduces v2's wallpaper_wh.png byte-for-byte.
- v2 to v3 pixel diff is confined to x 937–1622 (the hero). Lettering, caption, sun disc and wallpaper are unchanged.
- Caveat: the GLB idle is a forearms-across-chest guard, the same as v1. It isn't a tight crossed-arm fold. A tighter fold would need a new clip; nothing was hand-keyed.

## Reusable poses
`assets/poses/pantera/{folded,lunge}.json` hold bone-local transforms for 22 bones, exported by `lab/game/tools/export_pose.gd`. The matching transparent 900x1200 renders are `{folded,lunge}.png`, and they're registered as `POSES` in game/ui-wh/roster.js.

## SHA-256
```
5d2ea0f23842e3cf2d1c30ed3b959fe68631f028eec4f56eb00f2fd1dd09c658  game/ui-wh/art/wallpaper_wh_v1.png
1a2608023367a1175275cbc0b482fb02849f156e740b9560dffac9d80556dd99  game/ui-wh/art/wallpaper_wh_v2.png
f0926dd480b1867748d49b90335e283f123594ced358f5606600ad275b2509da  game/ui-wh/art/wallpaper_wh_v3.png
1a2608023367a1175275cbc0b482fb02849f156e740b9560dffac9d80556dd99  game/ui-wh/art/wallpaper_wh.png
bfcc80ddd8c51786376adc00f4cdc856fa5ad2bf365308b39d5475470b4e207c  game/ui-wh/portraits/pantera_hero.png
0f4e77280c2c7f330d2199686d597b288a9aacbd30a803205b110386ddeeeda4  game/ui-wh/portraits/pantera_hero_folded.png
3d9064ff98f38452b467675b51419c9a52b314481ed0f1ca4c47ac082812c7b0  assets/poses/pantera/lunge.json
03ca22e87139fdc942ca55daab523623e827d256de6670b5ffbc2a8d5a4a7ba4  assets/poses/pantera/lunge.png
09aaaf5378561be7ac2a0bc5434575817a059ca30b72ea8b436fa1e56bf0656c  assets/poses/pantera/folded.json
55334b6166bcfd990dfd386970790faeeed37f53da40ea12a6c6fdfc40ec8c0f  assets/poses/pantera/folded.png
10061a0f75c6f2aa6b48f7a32d84a87bf3cbd0ad9c03882503ad8afd93722a20  docs/qa/ui-title/title_v1.jpg
2e59932041f82d7cfe8f63b21f42a48c386c5b209ece5fef8e486d58d3aa07c9  docs/qa/ui-title/title_v2.jpg
61c02697f5e1cb74113af369a69ab2b0f18d91f80fd64e88cd8438a049efe30b  docs/qa/ui-title/title_v3.jpg
ddac56f150903fb4459916f848715a176216dd5b3eaaed9e7c3108edd46becb5  docs/qa/ui-title/variants_v1_v2_v3.jpg
```
Proof captures: Playwright at 1920x1080, title_v1/v2/v3.jpg, no page errors or 404s. The v1 capture differs from title_before.jpg by a mean of about 2/255 (JPEG and the blinking PRESS START), and v2 from title_after.jpg by the same amount.
