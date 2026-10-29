# Cape Jones playable on Alisa's select slot (2026-10-23)

## Owner directive (t118u #4 / t121u)
Cape Jones (secret identity Cyborg X, fighter id `cyborgx`) replaces Tekken's Alisa: takes her select slot, her FULL moveset + animations, plus his own extras. Proof owed: screenshot of him on character select + a frame of him doing one of Alisa's moves.

## Decisions
1. **Model**: `game/assets/models/cape-jones.glb` (auto-rigged Round-2 wave 2026-10-18, 49 bones, 1.75 m) staged as `roster/cyborg-x/attires/attire1/model-rigged.glb` — byte-identical, no re-rig (rig QA passed 2026-10-23).
2. **Wiring**: MODEL_URLS key `cape-jones-attire1`; ATTIRE_VARIANTS `cyborgx` → Attire 1 = the rigged build (default). The `cyborgx` roster entry already had `base: 'Alisa'`, `name: 'CAPE JONES'` (PR #759) — no select-layout edits (menu lane owns those files).
3. **Animations**: no Alisa motion bank exists in any repo teardown (T5/T6/T7/T8/TTT2) — searched 2026-10-23, only frame data found. The gunjack T3 fallback for cyborgx stays, logged as last resort in `game/data/cape-alisa-binding.json` per owner law t121u. Real Alisa motions are a follow-up for the T7 extraction lane (owner bought T7 2026-10-23).
4. **Attire ladder**: no Tekken Alisa original model exists in the repo, so the 5-7 ladder-back rule has nothing to seat yet — flagged, not guessed.
5. **Commit method**: Git Data API built from main's real tree SHAs (no-sparse-commit law; full clone impossible on this box — /tmp is 512 MB, repo is 10.6 GB). Worked from a blob:none sparse tree; commits reference verified tree/blob SHAs only.
6. **Lane boundaries respected**: did not touch `game/js/fighter.js` facing code, camera bounds, `game/assets/models/model-facing.json` (Claude's facing-audit lane), char-select layout, or MENU files (Grok's teardown-integration lane). The cape-jones repo show work runs in a sibling lane (agent-ops CLAIMS.md).

## Verification (verify-by-playing, owner law)
- Phone portrait 390x844, Playwright + SwiftShader, served from the working tree with this branch's edits.
- Select: CAPE JONES on the grid (card index 15), textured 3D preview, "Attire 1" picker entry live.
- Fight (cyborgx vs pantera, arcade): 10/10 state probes `"round":"fight"`; P1 attacks register `atk:"1"` (Jab) with clip `t3_gunjack_row44@cape-jones-attire1`; idle shows `t3_gunjack_stance` (not T-pose). Zero pageerrors.
- Proof frames: `docs/proof/cape-jones-fight-2026-10-23/` (in the PR as referenced PNGs — see PR body).

## Follow-ups (not this PR)
- Real Alisa T5/T6/T7/T8/TTT2 animation bank → replace the gunjack T3 fallback (T7 extraction lane).
- `model-facing.json` entry for the rigged attire path (Claude's facing-audit lane).
- Camera-bounds portrait framing (separate lane — fighters render small at screen edges).
- If the sibling cape-jones-repo lane produces a better rigged GLB, swap it in a follow-up PR (additive).
