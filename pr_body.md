Creation Suite Pass — Worker D (the proof): differentiate Master White toward Kevin with the landed suite/bake machinery, prove it with renders, and name every gap honestly.

## Owner instruction (verbatim quote)
"Master White (roster/baek/attires/master-white/, a retexture on Baek's Tekken model) is a PARKED weak attire (owner law 2026-10-20) until the Creation Suite differentiates it into looking like KEVIN — a whole different person than Baek. Kevin IS the fighter; his face is his Tripo model (roster/baek/attires/attire1/model.glb, unrigged static — reference only). Owner presentation law: when showing Kevin, show KEVIN's side honestly — this attire remains "Master White, differentiated toward Kevin," not a fake Kevin replacement."

## Method the owner specified
Render Kevin (Tripo attire1) and the Master White base as references with the locked docs/RENDER-ORIENTATION.md method; author the differentiation through the Creation Suite UI's own machinery (Baek → Master White, MPFB face/body morphs toward Kevin, CC0 hair part + brow-cc0-regular equipped, Save to Attire producing roster/baek/attires/master-white/customization.json in the v1 schema, hand-authoring only fields the UI cannot set and disclosing them); bake with customization/tools/apply_customization.py to model-kevin-diff.glb plus the game/js/attire-customizations.js registry entry; prove the game resolves it with customization/tools/test_game_hook.mjs; render AFTER front + head close-up with the same locked method; give an own-eyes three-way verdict (BEFORE / AFTER / Kevin) with exactly what's missing for full Kevin; keep everything in roster/baek/attires/master-white/proof-kevin-diff/ and ship via a feature-branch PR, merging only when checks pass and the merge is clean, with zero deletions and no changes to game/js/select-screen.js, game/js/fighter.js, or portraits.

## Method actually used
Render Kevin (Tripo attire1) and the Master White base as references with the locked docs/RENDER-ORIENTATION.md method; author the differentiation through the Creation Suite UI's own machinery (Baek → Master White, MPFB face/body morphs toward Kevin, CC0 hair part + brow-cc0-regular equipped, Save to Attire producing roster/baek/attires/master-white/customization.json in the v1 schema, hand-authoring only fields the UI cannot set and disclosing them); bake with customization/tools/apply_customization.py to model-kevin-diff.glb plus the game/js/attire-customizations.js registry entry; prove the game resolves it with customization/tools/test_game_hook.mjs; render AFTER front + head close-up with the same locked method; give an own-eyes three-way verdict (BEFORE / AFTER / Kevin) with exactly what's missing for full Kevin; keep everything in roster/baek/attires/master-white/proof-kevin-diff/ and ship via a feature-branch PR, merging only when checks pass and the merge is clean, with zero deletions and no changes to game/js/select-screen.js, game/js/fighter.js, or portraits.

## Deviations (none / list, each with owner approval link)
- Fixed a bake bug that made the specified job impossible: apply_customization.py set placement rotation_euler on glTF-imported part roots that are in QUATERNION mode, so placement rotations were silently ignored and every part baked flipped 180° (Kabsch-proven); the in-place fix sets rotation_mode first, per the repo's build-on-existing-work rule — https://github.com/mhvnsnt/western-heart/pull/396
- Fixed a latent baseline bug in the specified smoke test (customization/tools/test_game_hook.mjs phase 4b compared an empty-registry load against the real-registry load, failing by construction once any real override exists); baseline now comes from a pristine empty-registry load, assertions unchanged — https://github.com/mhvnsnt/western-heart/pull/396
- Wired the suite's per-attire restore for this attire only (customization_json was null in customization/creation-suite-ui/data/roster-attires.json), without which the specified Save-to-Attire record could never be restored by the suite — https://github.com/mhvnsnt/western-heart/pull/404
- The first worktree for this pass was deleted by an external disk process mid-task; the pass was rebuilt in a fresh clone and every value re-derived or reproduced deterministically (rebake matched the lost bake's byte size exactly) — https://github.com/mhvnsnt/western-heart/pull/409

## Proof (paths to files, frames, test output)
- `roster/baek/attires/master-white/proof-kevin-diff/PROOF.md`
- `roster/baek/attires/master-white/proof-kevin-diff/before_front.png`
- `roster/baek/attires/master-white/proof-kevin-diff/before_head.png`
- `roster/baek/attires/master-white/proof-kevin-diff/after_front.png`
- `roster/baek/attires/master-white/proof-kevin-diff/after_head.png`
- `roster/baek/attires/master-white/proof-kevin-diff/after_head_min.png`
- `roster/baek/attires/master-white/proof-kevin-diff/kevin-ref_front.png`
- `roster/baek/attires/master-white/proof-kevin-diff/kevin-ref_head.png`
- `roster/baek/attires/master-white/proof-kevin-diff/suite-full.png`
- `roster/baek/attires/master-white/proof-kevin-diff/suite-controls.png`
- `roster/baek/attires/master-white/proof-kevin-diff/suite-brow.png`
- `roster/baek/attires/master-white/proof-kevin-diff/suite-report.json`
- `roster/baek/attires/master-white/customization.json`
- `roster/baek/attires/master-white/model-kevin-diff.glb`
- `game/js/attire-customizations.js`
- Smoke test output (this PR's worktree): `SMOKE roster: 103 MODEL_URLS keys` / `SMOKE registry: 1 override(s), all resolve + applied` / `SMOKE no-op: empty registry leaves MODEL_URLS untouched` / `SMOKE PASS`

## Self-check: I verified the result against the literal instruction
- [x] I verified the result against the literal instruction

Yes — every render and screenshot in the proof pack was viewed with my own eyes; the verdict states plainly that he reads as a different person than Baek but not yet as Kevin, with the missing pieces named; the attire is labeled "Master White, differentiated toward Kevin" everywhere, never a Kevin replacement; Kevin's own side is shown from his actual Tripo model; zero files deleted (the only two removed lines in the diff are the two intended one-line replacements, named in the commit history); select-screen.js, fighter.js and portraits untouched.
