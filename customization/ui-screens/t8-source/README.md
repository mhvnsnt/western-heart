# t8-source — extracted Tekken 8 UI art (reserved)

Sourcing order, owner directive: **all UI assets from Tekken 8 FIRST — get T8's
UI to 100%** — then layer other games' UI from teardown files on top.

This directory is where the extraction lane drops T8's UI (panel/frame/cursor/
icon sprites, fonts, layout data) when it lands. The UI WORKSHOP prefers
t8-source assets whenever present; until then the `*.t8-template.json` screens
in the parent dir (recreated layouts, zero extracted art) stand in.

Layout: mirror the game's own structure, e.g.
`t8-source/stage-select/`, `t8-source/char-select/`, `t8-source/fonts/`.
Each drop gets a `SOURCE.md` naming the teardown origin + extraction tool.
