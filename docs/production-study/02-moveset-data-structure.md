# Moveset Data Structure — What a "Move" Actually Is

**Source:** tekkenmods-docs, Tekken 8 moveset structure documentation.
This is the professional data model for fighting game moves.

## The Core Definition

> **Animation** = data about the body's movement.
> **Move** = animation + hitbox + hurtbox + active frames + hit conditions + cancels.

Anything involving animation is a "Move": attacks, throws, intros, win poses,
taunts, Rage Arts, reactions, even stage transitions.

## Move Components

- **Move Name/Key** + **Animation Name/Key** (the animation is referenced, not embedded)
- **Hit level:** High / Mid / Low / Unblockable
- **Hurtbox / Vulnerability** (where the character CAN be hit during the move)
- **Hitbox values** (where the move HITS; non-attacks omit this)
- **Cancels:** what the move can transition into, with input sequences + requirements
- **Hit Conditions:** what happens on hit — reactions, pushback, with requirements
- **Extra Move Properties:** frame-timed triggers (projectiles, throw cameras, dialogue, effects)
- **Move Start/End Properties:** setup and cleanup
- **Voice clips** (Folder ID + Voice ID references)

## Why This Matters for Western Heart

1. **Moves are DATA, not code.** The executable doesn't contain fighting logic
   per move — it reads move data files. This matches what the Tekken 3 teardown
   found: 1.2MB executable, 37MB asset archive. Western Heart's engine reads
   move data the same way.

2. **Animation is separate from the move.** The same animation can back multiple
   moves (different hitboxes, different cancels). This is how we retarget No
   Mercy/WrestleMania XIX wrestling animations onto Tekken 7 models — the
   animation is just data referenced by the move.

3. **Every move needs, minimum:** animation reference, hit level, hurtbox,
   active frames, hit conditions. That's the shipping checklist per move.

4. **Throws are moves too** — with throw-camera and throw-extradata properties.
   The wrestling-game grappling system plugs in HERE: a suplex is a Move with
   a throw property, a two-character animation, and a throw camera.
