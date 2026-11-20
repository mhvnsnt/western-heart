# SCIMITAR — Dressing Spec (for the Creation Suite lane)

**Character:** SCIMITAR (base: Shaheen, Tekken 7 SFMLab rip)
**Design lock:** Prince of Persia (2003 PS2) × Scar (The Lion King) × Jafar (Aladdin)
**Base mesh:** `game/assets/models/scimitar.glb` — wired 2026-10-18 per NO-GATE LAW.
Base mesh state (honest): Y-up, 1.8m, front=-Z (pantera convention), 29.5k verts,
1 material, **untextured, unrigged (no skeleton)**. Rig + textures are follow-up.

## Why this spec exists

Per the NUDE/BASE MODEL CLOTHING LAW, the base mesh wired in as-is. No suitable
3D clothing pieces for Scimitar exist in the parts library yet (34 parts as of
2026-10-18: eyes, decals, logos, tights textures, masks, gauntlets, jackets, boots,
hair — all character-specific to Pantera / Silvertongue / Cape Jones builds).
So the Creation Suite lane must build the following pieces.

## Required 3D clothing / accessory pieces

Build in the locked design direction (PoP PS2 × Scar × Jafar):

1. **Desert-warrior wrapped cloth torso garb** — PoP 2003 PS2 traveler style, weathered cloth wraps over the torso.
2. **Leather bracers** — both forearms, worn traveler leather.
3. **Sash belt** — waist, cloth sash with knot.
4. **Sand-worn boots** — agile acrobat's boots, weathered.
5. **Layered robes, deep-crimson + black** — Jafar silhouette, tall and cobra-like, with **gold geometric desert embroidery**.
6. **High flared collar / half-face veil** — shadows the lower face (Jafar).
7. **Serpent motif forearm coil** — a serpent coiled around one forearm (Jafar).
8. **Curved scimitar, jeweled hilt** — hip-mounted signature weapon.
9. **Black-tipped claw gauntlets** — Scar presence, lean regal menace.
10. **Scar-over-eye + amber/gold eyes** — thin scar down over one eye (texture/decal work ok).

## Texture work needed on the base mesh

- Full skin/clothing textures (base mesh is currently 1 flat beige material).
- Beard (Shaheen's bearded face — verify against the SFMLab source).
- Dark mane-like hair swept back (Scar).

## Rig needed

- Auto-rig to the WH/Mixamo skeleton (Hips/Spine1/Spine2/Head/hands/feet) — the base mesh has no skeleton. (Follows the auto-rig wave pattern, PR #264.)

## Wire-in history

- 2026-10-18 (lane C, PR #266): T7→Mixamo conversion proven on Shaheen; only the nude MDL imported — held per the old defect framing.
- 2026-10-18 (PR #268, open): base mesh wired as `game/assets/models/scimitar.glb` (768KB, Z-up, untextured, unrigged) per NO-GATE LAW. Proof render flagged: looked like a side view (facing heuristic wrong).
- 2026-10-18 (this PR): orientation corrected to Y-up / front=-Z (pantera convention, verified numerically: nose protrusion toward -Z; own-eyes verified upright humanoid T-pose, front render). Registered in `game/js/assets.js` MODEL_URLS; roster `model` field switched from `steve-fox` fallback to `scimitar`.
