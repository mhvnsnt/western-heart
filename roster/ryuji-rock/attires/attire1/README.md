# RYUJI (Yamazaki x The Rock hybrid) — Attire 1

Owner order 2026-10-19 ~20:07-20:08 CDT: "Ryuji Yamazaki version… black shirt, blonde top hair. Version based on The Rock (Dwayne Johnson) mixed with Ryuji Yamazaki — obnoxious like Ryuji, sticks his tongue out, personality mixed with The Rock."

**NAME LOCKED (owner 2026-10-21): CORNERSTONE.** This fighter's Western Heart name is **CornerStone** — see CANON.md ("CORNERSTONE — The Obnoxious One (Bonus)") and RENAME-MAP.md (CORNERSTONE section). The "Ryuji / RYUJI ROCK" wording in the rest of this document is the pre-rename record and stays as history. Internal id / moveset key / model key remain `ryuji-rock` so every loader reference stays valid.

## MODEL STATUS: LANDED (2026-10-21)

The owner delivered his Tripo link on 2026-10-21 — exactly the next step this document was waiting on: https://studio.tripo3d.ai/3d-model/20c1fd2e-40d0-4500-9be6-50f6494ab5e1 ("tattooed man 3d model"). Pulled with `tools/tripo-pull/tripo-pull.py` (no sign-in): `tattooed_man_3d_model.glb`, 18,872,720 B, sha256 `658848674696b6c4e47c55f773d2c55e07359595e51e57ce273704dc4871049d`, 1 mesh / 1 material / 3 textures, meshopt. Original archived in release `cornerstone-tripo-pulls-20261021` (asset size verified server-side). Dropped at `model.glb` in this folder; the pre-wired `assets.js` URL now resolves and his roster-full entry (which already carried model key `ryuji-rock`) shows his locked name **CORNERSTONE**. Front render: `docs/tpose-refs/ryuji-rock/a1_front.png`.

Model hunt (2026-10-19, lane ryuji-rock — pre-landing record, kept as history):
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
