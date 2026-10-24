# Combat QA — Autonomous Testing Harness

**Owner directive (2026-10-23):** "start figuring out what's how you can test something side by side to see what's wrong with our combat right now... so I can stop having to describe everything to you so you can start autonomously seeing what's wrong with it and fixing it."

## What this does

Runs the game headlessly and verifies combat works like Tekken, catching bugs BEFORE the owner playtests:

1. **Input audit** (`input_audit.mjs`) — every fighter, every move: simulate the exact Tekken input, verify the EXACT move fires (not a random fallback)
2. **Combo audit** (`combo_audit.mjs`) — every string: simulate with Tekken timing windows, verify each hit connects in sequence
3. **Animation audit** (`anim_audit.mjs`) — every move's `anim_ref` resolves to a real animation; every throw has attacker AND victim animation data
4. **Hit audit** (`hit_audit.mjs`) — attacks connect at proper range; hitboxes/hurtboxes overlap correctly
5. **Auto-fix** (`autofix.mjs`) — applies clear fixes (wrong mappings, missing refs, timing)

## Usage

```bash
# Run everything
node tools/combat-qa/run_all.mjs

# Run individual audits
node tools/combat-qa/input_audit.mjs [--report out.json]
node tools/combat-qa/combo_audit.mjs [--fighter pantera]
node tools/combat-qa/anim_audit.mjs [--fix]
node tools/combat-qa/hit_audit.mjs
```

## Ground truth

Tekken files are the source of truth:
- `game/assets/movesets/*.json` — movelists with T3/T7/T8 source data
- `game/assets/anim/t3/*/` — T3 animation banks
- Frame data in moveset `t7` blocks

## What "done" means

The owner should NEVER have to report:
- "buttons do random moves" → input audit catches it
- "combos don't work" → combo audit catches it  
- "grapple animations don't play" → anim audit catches it
- "hits don't connect" → hit audit catches it
