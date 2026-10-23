# RULES: No guessing, no faking (owner law, 2026-10-14)

Applies to every agent (Grok Bot, Muse/Ashes, Producerbot, Repo Co Dev, Jigglebot, any new agent) in Western Heart and every repo that feeds it. The owner owns every game torn down here (Tekken 3, TTT2, Tekken 6 and the other fighting games modded in). Western Heart is a private Tekken mod until the owner says otherwise.

1. **Never hand-make, procedurally generate, IK-author or guess** an animation, pose, model, texture, stage, frame-data value or stat when teardown or owned data for it exists. "Looks about right" is not allowed.
2. **Search first, in this order**, and write down what you searched:
   1. decoded teardown data in this repo (`teardown/**`, `assets/anim/**`, `lab/game/assets/*_t3real.glb`, movesets, `docs/anim/PROCEDURAL_AUDIT.md`);
   2. teardown releases and box storage (`gh release list -R mhvnsnt/western-heart`, `/home/box/offload`, `/workspace/*teardown*`), plus the other owner repos (`gh repo list mhvnsnt`);
   3. the decoders/tools already built (`teardown/tekken3/tools/local/pose_assemble.py`, `lab/tools/t3_motion_bake.py`, `lab/tools/t3_to_gltf.py`, `lab/tools/autorig.py`, per-game TEARDOWN.md);
   4. only then public reference data (frame data wikis, n0madic/Tekken3Remake docs).
3. **Log the source of everything** you put in the game: file path, slot/row/frame, tool + command, SHA-256 of the input. GLB clips carry it in `animations[].extras`; poses in their JSON; docs in a table.
4. **If the real source is not found, report it as MISSING** (what, where you looked, how to unblock) in `docs/anim/PROCEDURAL_AUDIT.md` section 5 and in your report. Do not fill the gap with a placeholder, an authored clip, an IK pose or an AI image and call it done.
5. Existing procedural/authored clips stay in place (never delete) but are **flagged** and must not be used for new art, cards, title screens or renders when a real clip exists. Real clips are preferred at runtime (`fighter.gd` `REAL` map).
6. **Proof of real bytes** per Producerbot's `media-proof-standard`: SHA-256 of inputs and outputs, frames/screenshots actually viewed, the command that made them, before/after images. UNKNOWN is never PASS.
7. Never claim "the real pose" or "from the teardown" unless the bytes trace back to a decoded teardown file. Say "closest real frame" when that is what it is.
8. Don't hold back owned data over sale worries (see AGENTS.md "Sale status"). Do respect lane ownership: creation suite = Repo Co Dev, physics = Jigglebot.


## INSTRUCTION GATE: Owner law, data source priority (Oct 23, 2026, 2:19 PM CT)

> **Western Heart data (moves, animations, frame data, menus, character select) comes from Tekken 5, 6, 7, 8 and TTT2. Tekken 3 is only a last-resort fallback, and every T3 use must be logged with the reason no T5/6/7/8/TTT2 source was available.**

- Search T5/T6/T7/T8/TTT2 teardowns first. Use T3 only when none of them has the data, and log the T3 use (file, clip, reason) in `docs/anim/PROCEDURAL_AUDIT.md`.
