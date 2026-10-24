# Model intake laws: NO-GATE + clothing + M-rating (owner laws, 2026-10-18)

Applies to every agent working Western Heart and every repo that feeds it. These three laws govern how models enter the game. They override any quality-gate, modesty-gate, or completeness-gate instinct.

## 1. NO-GATE LAW (owner 2026-10-18, verbatim)

> "nothing gates a model from making it into the game — models wire in as-is, missing textures/meshes/UVs get corrected and put on the character, customization dresses them. Nothing watered down, nothing held back."

1. **No model is ever held back for being incomplete.** Missing textures, missing meshes, broken UVs, no rig, wrong orientation — none of these block wire-in. They get fixed and put on the character as follow-up work.
2. **Wire in as-is, then correct.** The base mesh lands in `game/assets/models/` and gets registered in `game/js/assets.js` MODEL_URLS first. Texture passes, re-rigs, UV fixes, and clothing come after — tracked as follow-up, never as blockers.
3. **"Have" vs "wired" are separate states.** A model we pulled (on a release, on disk) is HAVE. A model registered in the asset pipeline is WIRED. Never conflate them; never lose a HAVE because it isn't WIRED yet. (See the model inventory for the registry.)
4. **Nothing watered down, nothing held back.** Do not "clean up" a model by removing what makes it distinctive. Do not delay wire-in waiting for a better source.

## 2. NUDE/BASE MODEL CLOTHING LAW (owner 2026-10-18, verbatim)

> "any models that come in with no clothes, we just gotta find clothing and accessories to put on them because we're pulling in a system for that anyway."

1. **Never hold a model for missing clothes.** A nude or unclothed base mesh wires in like any other model (NO-GATE LAW applies).
2. **The customization/clothing system dresses it.** Clothing and accessories come from the parts library (`customization/parts/`, `PARTS-REGISTRY.json`) and the Creation Suite flagship lane — full attire swaps, full model/mesh customization, textures, meshes, UV fixes.
3. **If no suitable clothing pieces exist yet:** wire the base mesh anyway, then document exactly which pieces the Creation Suite lane must build (per-character dressing spec in `docs/attire/`), and say so in the PR. The missing pieces are a build list, not a blocker.
4. **Base meshes are first-class.** A clean base body is the foundation the clothing system needs — treat it as an asset, not a defect.

## 3. M-RATING LAW (owner 2026-10-18)

Western Heart targets **RATED M**. The long-term bar is Mortal Kombat-level visceral: bone breaks, fatalities, x-ray attacks.

1. **Never hold a model back for nudity or partial nudity.** Nudity is not a defect and not a gate — per the NO-GATE LAW, the model wires in.
2. **Nothing watered down while building.** Do not censor, cover, or "safe-ify" models during development because of discomfort with adult themes. The game is going to adult themes; build toward that.
3. **The M-rating is the destination, not a blocker.** Visceral systems (breaks, fatalities, x-ray) come when the base game is down. Until then: build the base, don't get caught up on the adult themes — but never gate on them either.
