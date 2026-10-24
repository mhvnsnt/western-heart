# Western Heart roster cards

Every fighter gets a card in the Pantera style: render, name, kanji, soul, canon tier line, quote, Tekken body, element, `ORIGIN parts unknown`, signature detail. **All text comes from CANON.md** through `game/ui-wh/tools/canon_to_roster.py` → `game/ui-wh/roster_canon.json`. Never hand-type card text.

- Card page: `game/ui-wh/cards.html#<id>` (one card), `cards.html#strip?ids=a,b,c` (promo strip).
- Select screen: `game/ui-wh/index.html#select`. Lock state is data (`roster.js` `isUnlocked`): Pantera only by default; `localStorage.wh_unlocked` for progress; `?unlock=all` for promo/showcase captures only.
- Captures: `docs/qa/roster-cards/` (select_default, select_unlock_all, card_<id> x23, promo_strip).

## Rules
1. A real render only when a model exists that fits the canon description. Otherwise MODEL PENDING silhouette with full canon text.
2. Never generate a face with AI. Never call a recolor a "rescan". Label WIP art as WIP on the card flag.
3. Every non-owner part goes in `docs/roster/<id>/parts.json` with source, SHA-256, `third_party` and the pre-sale action.
4. Originals are never edited: recipes (`docs/roster/<id>/kitbash_vN.json`) are applied at render time on the untouched GLB; new versions get a new N.

## Make a card (exact steps)
```
python3 game/ui-wh/tools/canon_to_roster.py                         # canon -> json
# if a fitting model exists: write docs/roster/<id>/kitbash_v1.json (hide/tint/props), then
cp game/ui-wh/tools/render_card.gd lab/game/tools/render_card.gd     # godot needs it inside a project
xvfb-run -a godot --rendering-driver opengl3 --path lab/game -s res://tools/render_card.gd -- \
   $PWD/<model.glb> /tmp/<id>_a1 $PWD/docs/roster/<id>/kitbash_v1.json 20
# bust = crop of full (the 2nd framing pass drops props; known bug): PIL crop (56,0,456,400) -> 512x512
cp /tmp/<id>_a1_full.png game/ui-wh/portraits/<id>_a1wip_full.png   # never overwrite an existing file
# add the id to ART{} in game/ui-wh/roster.js
python3 -m http.server 18437 -b 127.0.0.1 -d game &                 # pick a free port; 8765 is often taken
WH_PORT=18437 PW_CHROMIUM=/usr/bin/google-chrome node game/ui-wh/tools/capture_cards.mjs docs/qa/roster-cards
```
Then open the PNGs yourself and check them (no blank frames, flags right, text not overflowing) before saying done. `sha256sum` the outputs into parts.json.

## Status and T-pose refs needed
T-pose standard: [docs/tpose-refs/MUSE_TPOSE_SPEC.md](../tpose-refs/MUSE_TPOSE_SPEC.md) (one-to-one T-pose, pure white background, fingertips inside frame, flat light, every attire).

| Fighter | Tier | Card art | Tripo T-pose reference needed |
|---|---|---|---|
| PANTERA | THE SEVEN | ATTIRE 1 (owner GLB) | - |
| DEMONIO | THE SEVEN | MODEL PENDING | Tripo T-pose of DEMONIO: Jin's karate frame, precise and fundamental |
| PHANTOM | THE SEVEN | MODEL PENDING | Tripo T-pose of PHANTOM: Yoshimitsu's armored frame, the sword, the mask |
| DIABLO | THE SEVEN | MODEL PENDING | Tripo T-pose of DIABLO: Heihachi's devastating frame, the boss's body |
| SKULL | THE SEVEN | MODEL PENDING | Tripo T-pose of SKULL: Punisher / Finn Balor demon-paint direction. Keep Bryan's pants. Alternate attires pending review. |
| SAM-UR-A1 | THE SEVEN | MODEL PENDING | Tripo T-pose of SAM-UR-A1: Gundam/Transformer/Power Ranger mech mashup. Name styled as mech designation (∪ for U, Λ for A). Gun Jack base. |
| SAKU RA | THE SEVEN | MODEL PENDING | Tripo T-pose of SAKU RA: Name Saku Ra (咲 = bloom). K-pop idol Powerpuff Girl direction, CN gigaleak PPG construction. Xiaoyu base. |
| ZUI | THE FOUR | WIP KITBASH A1 (T7 Steve Fox import, recolored + props) | Tripo T-pose of ZUI: Drunken master ex-monk hedonist. Sagat-meets-Chinese-mountain-monk visual. Sake bottle prop, supernatural sway, sketchbook tattoos. Name from 醉 (zuì), 醉拳 (zuìquán) = drunken fist. Steve Fox base. |
| KINPO | THE FOUR | MODEL PENDING | Tripo T-pose of KINPO: Buttercup (green Powerpuff Girl) to Saku Ra's Blossom. Name from kinpōge. Asuka base. |
| WATERFALL | THE FOUR | MODEL PENDING | Tripo T-pose of WATERFALL: Name Waterfall (owner-named — tears like a waterfall). Soul-bearer concept: her tears are the nine souls passing through. Josie Rizal base. |
| KING TYRANT | THE FOUR | MODEL PENDING | Tripo T-pose of KING TYRANT: Booker T style. Name King Tyrant (from Booker's "King Booker" gimmick). Keep capoeira movement. Eddy Gordo base. Straightforward reskin. |
| BURGER | THE TWELVE | MODEL PENDING | Tripo T-pose of BURGER: Name BURGER. Gluttonous, fast, insatiable — hunger as curse. Slim Bob (Tekken Tag 2) as the uncursed attire, not a separate character. Bob Richards base. |
| AWA POP | THE TWELVE | MODEL PENDING | Tripo T-pose of AWA POP: Name AWA POP (泡 awa = bubble + Pop). Bubbles of the PPG trio. Sweet but deadly. Nina Williams base. |
| SCIMITAR | THE TWELVE | MODEL PENDING | Tripo T-pose of SCIMITAR: Name SCIMITAR (named for his weapon). Scar × Jafar — scheming, manipulative, regal, sinister. Saudi military precision × desert warrior. Shaheen base. |
| PURPLE RAIN | THE TWELVE | MODEL PENDING | Tripo T-pose of PURPLE RAIN: Name PURPLE RAIN (Prince reference). MJ × Prince × Slickback — flamboyant but dangerous. Lee Chaolan base. |
| NIGHTWOLF | THE TWELVE | MODEL PENDING | Tripo T-pose of NIGHTWOLF: Name NIGHTWOLF. Native American spirit warrior, full commitment. Julia Chang base. |
| MICHIKO | THE TWELVE | MODEL PENDING | Tripo T-pose of MICHIKO: Name MICHIKO. Michiko Malandro × Tier Harribel — free-spirited outlaw × regal composed power. Dangerous but magnetic. Katarina Alves base. |
| STAR | THE TWELVE | MODEL PENDING | Tripo T-pose of STAR: Name STAR. Capoeira dancer — graceful, rhythmic, deadly. Pairs with King Tyrant as the two capoeira fighters. Christie Monteiro base. |
| TORCH | THE TWELVE | MODEL PENDING | Tripo T-pose of TORCH: Name TORCH. Ruthless elegant assassin — Nina's sister with the darker edge. Sister rivalry with Awa Pop. Anna Williams base. |
| DIO | THE TWELVE | MODEL PENDING | Tripo T-pose of DIO: Name DIO. Street Fighter's Akuma as he appears in Tekken 7 (not Kuma the bear — the bear, if ever pulled, is URSA). Master of the Satsui no Hado. Pure destructive force. Akuma base. |
| CYBORG X | THE TWELVE | MODEL PENDING | Tripo T-pose of CYBORG X: Name CYBORG X. The android — detachable head, chainsaw arms, jetpack. Pairs with SAM-UR-A1 as the two built souls. Alisa Bosconovitch base. |
| BRUNO | THE TWELVE | MODEL PENDING | Tripo T-pose of BRUNO: Name BRUNO (owner: "Miguel is Bruno already"). The Weeknd × Bruno Mars × Boomhauer × Johnny Bravo. Moody R&B mystery + smooth showmanship + mumbling drawl + vain pretty-boy swagger. Spanish brawler. Miguel base. |
| N3GΔTIV0 | THE HUNTER | MODEL PENDING | Tripo T-pose of N3GΔTIV0: Name N3GΔTIV0 (leetspeak for "Negativo"). Zombie bounty hunter across the galaxies × Sinestro (fear as weapon) × Black Flash (death itself, unstoppable). Kills for bounties, for hire, or for fun. Negan base. |
| SUN RĀ | BOSS | not a select-screen fighter (boss realm) | Tripo T-pose of SUN RĀ: the round, cute, evil sun — the least threatening shape for the most threatening appetite |

Zui is the worked customization example: see `docs/roster/zui/` (recipe, parts.json, proof/zui_before_after.jpg).
