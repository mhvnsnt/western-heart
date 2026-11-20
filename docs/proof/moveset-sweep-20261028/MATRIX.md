# Moveset sweep matrix (2026-10-29)

97/129 fighters ran: 55986 moves, 49403 pass, 5171 fail, 1412 n/a. Full rerun 2026-10-29 (`rerun-20261029/`); 97 fighters re-swept after #1195/#1196 (r11); 97 fighters re-swept after #1195/#1196 (r11); whole roster re-swept after #1199/#1200/#1201 (r13, all 129: 97 ran, 32 blocked with no model on box), whole roster re-swept after #1202/#1203/#1204 (r14, all 129: 97 ran, 32 blocked; kronos 4 throw rows flaked in batch, pass solo), whole roster re-swept after #1205 batch 3 (r15, all 129: 97 ran, 32 blocked; batch 3 regressed throw-opener string follow-ups on dorowani/pantera/samura1, fixed in #1213), core 8 (bruno pantera demonio cyborgx burger chatur deathfang dio) re-swept after #1219-#1222/#1224 batches 8-12 (r16; per-fighter failing rows in `docs/proof/moveset-sweep-20261028/r16-core8-failing.json`), one result per fighter; per-fighter failing rows in `r15-failing.json` (r14 in `r14-failing.json`). Bodies follow the game's default attire (sweep-bodies.md); blockers are listed with their reason.

Moveset editor e2e: 128/128 open/edit/save/reload/reset (`editor.json`). Fight shots: `sweep-*.png`.

| fighter | moves | pass | fail | n/a | juggles | status |
|---|---|---|---|---|---|---|
| armor-king | 524 | 481 | 28 | 15 | 111/142 | ran |
| awapop | 938 | 866 | 58 | 14 | 25/49 | ran |
| baek-master-white | 310 | 227 | 81 | 2 | 3/12 | ran |
| baek | 130 | 130 | 0 | 0 | 3/12 | ran |
| blanka | 218 | 171 | 44 | 3 | 3/14 | ran |
| bob | 581 | 557 | 13 | 11 | 46/107 | ran |
| bruno | 352 | 333 | 0 | 19 | 6/9 | ran (core-8 r16) |
| buffalo-bill | 824 | 722 | 92 | 10 | 56/110 | ran |
| burger-demon | 490 | 465 | 13 | 12 | 44/110 | ran |
| burger-speed-demon | 478 | 453 | 13 | 12 | 44/107 | ran |
| burger-the-mouth | 478 | 454 | 13 | 11 | 44/111 | ran |
| burger | 576 | 555 | 11 | 10 | 11/21 | ran (core-8 r16) |
| byou | 757 | 641 | 110 | 6 | 33/72 | ran |
| cainelias | 65 | 63 | 2 | 0 | 3/12 | ran |
| charger-attire2 | 218 | 171 | 44 | 3 | 3/14 | ran |
| charger | 222 | 175 | 44 | 3 | 3/15 | ran |
| chatur | 300 | 293 | 7 | 0 | 3/6 | ran (core-8 r16) |
| chordz | 492 | 458 | 17 | 17 | 11/53 | ran |
| cyborgx | 648 | 607 | 21 | 20 | 104/108 | ran (core-8 r16) |
| deathfang-werewolf | 146 | 128 | 18 | 0 | 3/12 | ran |
| deathfang | 146 | 128 | 9 | 9 | 3/6 | ran (core-8 r16) |
| demonio-bloodline-ember | 710 | 662 | 34 | 14 | 40/100 | ran |
| demonio-human | 707 | 665 | 28 | 14 | 10/28 | ran |
| demonio-winged | 1092 | 990 | 75 | 27 | 35/105 | ran |
| demonio | 793 | 744 | 31 | 18 | 13/18 | ran (core-8 r16) |
| diablo | 685 | 599 | 69 | 17 | 1/29 | ran |
| dio | 294 | 257 | 18 | 19 | 21/23 | ran (core-8 r16) |
| doa-ayane | | | | | | BLOCKER: no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls |
| doa-bass | 41 | 41 | 0 | 0 | 3/14 | ran |
| doa-hayabusa | | | | | | BLOCKER: no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls |
| doa-jannlee | | | | | | BLOCKER: no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls |
| doa-kasumi | | | | | | BLOCKER: no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls |
| doa-tina | | | | | | BLOCKER: no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls |
| doc-frank-frankenstein | 817 | 696 | 87 | 34 | 0/26 | ran |
| doc-frank-hood | 921 | 775 | 104 | 42 | 0/28 | ran |
| doc-frank-machine-shop | 962 | 821 | 99 | 42 | 0/28 | ran |
| doc-frank-wowomomo | 921 | 775 | 104 | 42 | 0/28 | ran |
| docfrank | 404 | 350 | 46 | 8 | 4/17 | ran |
| dorowani | 194 | 176 | 18 | 0 | 3/13 | ran |
| dxmmii-patchwork | 189 | 189 | 0 | 0 | 3/12 | ran |
| dxmmii | 169 | 169 | 0 | 0 | 3/12 | ran |
| gyou-spirit-body | 590 | 505 | 72 | 13 | 101/193 | ran |
| gyou | 1033 | 942 | 70 | 21 | 64/104 | ran |
| hugo | | | | | | BLOCKER: no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls |
| iori | 215 | 206 | 8 | 1 | 3/12 | ran |
| jin_soul | 1041 | 853 | 148 | 40 | 80/222 | ran |
| kai | 906 | 797 | 82 | 27 | 51/166 | ran |
| kingtyrant | 877 | 796 | 61 | 20 | 25/71 | ran |
| kinpo | 549 | 521 | 18 | 10 | 74/103 | ran |
| koreshi | 1109 | 918 | 175 | 16 | 5/29 | ran |
| kronos-attire2 | 2629 | 1797 | 772 | 60 | 5/78 | ran |
| kronos | 929 | 677 | 234 | 18 | 5/36 | ran |
| kutz | | | | | | BLOCKER: no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls |
| lili | 532 | 483 | 25 | 24 | 45/86 | ran |
| marduk | | | | | | BLOCKER: no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls |
| mariposa-monarch | 542 | 508 | 12 | 22 | 51/112 | ran |
| mariposa | 396 | 363 | 11 | 22 | 46/111 | ran |
| megami | | | | | | BLOCKER: material gate quarantine: megami (20 untextured), megami-attire1 (20 untextured) |
| menajerii | | | | | | BLOCKER: material gate quarantine: menajerii (55 untextured), menajerii-attire1 (55 untextured) |
| michiko | 368 | 344 | 4 | 20 | 4/15 | ran |
| negativo | 311 | 289 | 6 | 16 | 4/15 | ran |
| nightwolf | 591 | 560 | 22 | 9 | 14/59 | ran |
| pantera | 903 | 818 | 70 | 15 | 13/19 | ran (core-8 r16) |
| phantom | 1048 | 855 | 154 | 39 | 24/57 | ran |
| pond | 644 | 553 | 59 | 32 | 58/139 | ran |
| purplerain | 593 | 503 | 72 | 18 | 8/22 | ran |
| raiden | | | | | | BLOCKER: no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls |
| rave | 1115 | 995 | 102 | 18 | 24/80 | ran |
| realizzt | | | | | | BLOCKER: no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls |
| retsu | 768 | 729 | 26 | 13 | 44/138 | ran |
| rin | 739 | 686 | 39 | 14 | 39/84 | ran |
| ryuji-rock | 148 | 137 | 10 | 1 | 3/14 | ran |
| ryuji | 146 | 136 | 9 | 1 | 3/14 | ran |
| ryusan | 230 | 193 | 16 | 21 | 6/23 | ran |
| sakura | 793 | 716 | 61 | 16 | 25/60 | ran |
| samura1 | 889 | 761 | 111 | 17 | 17/39 | ran |
| scimitar | 385 | 366 | 9 | 10 | 8/20 | ran |
| sf-akuma | 187 | 166 | 11 | 10 | 77/99 | ran |
| sf-blanka | 56 | 53 | 3 | 0 | 3/13 | ran |
| sf-cammy | | | | | | BLOCKER: no model on box (source URLs only) |
| sf-chunli | | | | | | BLOCKER: no model on box (source URLs only) |
| sf-dhalsim | | | | | | BLOCKER: no model on box (source URLs only) |
| sf-guile | | | | | | BLOCKER: no model on box (source URLs only) |
| sf-ken | | | | | | BLOCKER: no model on box (source URLs only) |
| sf-mbison | | | | | | BLOCKER: no model on box (source URLs only) |
| sf-ryu | | | | | | BLOCKER: no model on box (source URLs only) |
| sf-sagat | | | | | | BLOCKER: no model on box (source URLs only) |
| sf-vega | | | | | | BLOCKER: no model on box (source URLs only) |
| sf-zangief | | | | | | BLOCKER: no model on box (source URLs only) |
| sha | 814 | 715 | 79 | 20 | 25/60 | ran |
| skull | 712 | 678 | 22 | 12 | 11/39 | ran |
| slice | 510 | 458 | 36 | 16 | 34/63 | ran |
| star | 937 | 865 | 50 | 22 | 65/152 | ran |
| sunra | | | | | | BLOCKER: no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls |
| t3-anna | 772 | 697 | 63 | 12 | 73/184 | ran |
| t3-bosconovitch | 285 | 258 | 27 | 0 | 0/12 | ran |
| t3-eddy | 736 | 659 | 56 | 21 | 46/169 | ran |
| t3-forestlaw | | | | | | BLOCKER: no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls |
| t3-gon | 170 | 151 | 19 | 0 | 3/11 | ran |
| t3-hwoarang | 752 | 696 | 45 | 11 | 46/87 | ran |
| t3-julia | 443 | 409 | 25 | 9 | 3/52 | ran |
| t3-kuma | 554 | 506 | 30 | 18 | 51/117 | ran |
| t3-law | 716 | 623 | 83 | 10 | 55/107 | ran |
| t3-lei | 819 | 737 | 72 | 10 | 108/398 | ran |
| t3-nina | 783 | 716 | 52 | 15 | 37/141 | ran |
| t3-ogre | 180 | 165 | 15 | 0 | 3/12 | ran |
| t3-paul | 520 | 446 | 61 | 13 | 5/157 | ran |
| thor | 346 | 276 | 64 | 6 | 4/25 | ran |
| tobi | 758 | 700 | 46 | 12 | 46/88 | ran |
| torch | 921 | 848 | 61 | 12 | 75/148 | ran |
| tou | 704 | 589 | 94 | 21 | 59/179 | ran |
| vainabel | 79 | 77 | 2 | 0 | 3/12 | ran |
| vega | 226 | 201 | 25 | 0 | 3/13 | ran |
| vf-akira | | | | | | BLOCKER: no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls |
| vf-elblaze | | | | | | BLOCKER: no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls |
| vf-jeffry | | | | | | BLOCKER: no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls |
| vf-kage | | | | | | BLOCKER: no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls |
| vf-leifei | | | | | | BLOCKER: no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls |
| vf-sarah | | | | | | BLOCKER: no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls |
| vf-wolf | | | | | | BLOCKER: no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls |
| waterfall | 389 | 370 | 7 | 12 | 15/32 | ran |
| yukihyo | 584 | 511 | 46 | 27 | 37/68 | ran |
| zangief | 236 | 189 | 44 | 3 | 3/15 | ran |
| zen | 668 | 562 | 86 | 20 | 42/106 | ran |
| zui | 678 | 598 | 48 | 32 | 31/80 | ran |
| gashadokuro | 554 | 506 | 30 | 18 | 51/117 | ran |
| aotsuki | 554 | 501 | 35 | 18 | 5/102 | ran |
| silvertongue | 532 | 483 | 25 | 24 | 45/86 | ran |
