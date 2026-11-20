# Creation suite phase 1: proof (2026-11-01)

`tools/proof-harness/creation_suite_phase1_shots.cjs` (local build, phone viewports 844x390 landscape and 390x844 portrait,
fresh browser: no saved fighter).

| shot | what it shows |
|---|---|
| `before_landscape.png`, `before_portrait.png` | before: NEW FIGHTER defaulted to the stock Soldier model in a T-pose, the top bar overlapped itself, body types named after real wrestlers / Tekken fighters, developer notes on screen |
| `after_1_create_base_body_select.png` | first visit: CREATE opens on CHOOSE A BASE BODY (9 WWE-style templates in Heavyweight / Cruiserweight / Women's) in the Tekken 7 menu look |
| `after_2_template_landscape.png` | the Texas Powerhouse template: real skin at the chosen tone (was an empty `setSkinTone` stub), standing relaxed instead of its T-pose, framed in the free area between the bars and the side panel |
| `after_3_portrait.png` | portrait (the owner's main orientation): fighter on top, menus in a bottom sheet, both visible; top bar in two rows, safe-area aware |
| `after_4_create_edit_portrait.png` | CREATE / EDIT: CREATE A FIGHTER (base-body select) or EDIT A FIGHTER (fighter, then attire) |
