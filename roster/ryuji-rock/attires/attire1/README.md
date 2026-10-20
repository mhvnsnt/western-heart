# RYUJI (Yamazaki x The Rock hybrid) — Attire 1

Owner order 2026-10-19 ~20:07-20:08 CDT: "Ryuji Yamazaki version… black shirt, blonde top hair. Version based on The Rock (Dwayne Johnson) mixed with Ryuji Yamazaki — obnoxious like Ryuji, sticks his tongue out, personality mixed with The Rock."

## MODEL STATUS: PENDING — no model pulled yet

Model hunt (2026-10-19, lane ryuji-rock):
- `~/workspace/game-reverse-engineering/` — no KOF XIV/XV / Maximum Impact teardown exists on disk (dirs checked: tekken3/5/6/7/8, DOA, SC, VF5, SF, Urban Reign, wrestling — no KOF). Nothing to extract from.
- `~/workspace/tripo-recovery/` — no Yamazaki GLB.
- Sketchfab public API search (`q=yamazaki`, `q=ryuji+yamazaki+kof`, `q=kof+yamazaki`, `q=ryuuji`): NO downloadable KOF Ryuji Yamazaki full-body model. Only hits: an unrelated "Yamazaki Character Face" head, non-downloadable namesakes, Taiko drums.
- Web search: only Yamazaki lead is a nude KOF XV commission rip on DeviantArt (adult + game rip — unusable, not pulled).

**Next step to land the model:** owner sends a Tripo share link for a Yamazaki/Rock-style model (black shirt, blonde top hair) → pull with `tools/tripo-pull/tripo-pull.py` → drop `model.glb` here → textured T-pose render → done. Per standing law, Tripo models wire in automatically the moment he sends the link. NO model was fabricated for this lane.

## Moveset
Full 22-move moveset in `game/assets/movesets/ryuji-rock.json`:
- 10 base strikes from the T3 King bank (grappler proxy)
- 2 standard King throws (1+3, 2+4)
- Yamazaki base: SERPENT SLASH (snake-arm), SAND KICK, KNIFE SLASH, THE GUILLOTINE (Drill DM)
- The Rock wrestling moves: ROCK BOTTOM (frame data from T3 King chain-starter row 281 per owner: "King has it in Tekken"), PEOPLE'S ELBOW, SHARPSHOOTER, BRAHMA BULL LARIAT, LAYIN' THE SMACKDOWN
- TONGUE OUT taunt (S): sticks his tongue out, eyebrow raised

## Wiring
- `game/js/assets.js` — model URL entry `ryuji-rock` → this folder's `model.glb` (activates when the GLB lands)
- `game/js/movesets.js` — `ryuji-rock` in MOVESET_IDS (22 moves live)
- `game/js/roster-full.js` — entry lands together with `model.glb` (intake convention: roster entry is only added once the model is on disk, so the fighter is never selectable with a missing model)
