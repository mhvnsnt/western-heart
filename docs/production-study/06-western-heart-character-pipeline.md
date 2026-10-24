# Western Heart Character Pipeline — Concept to Shipped Fighter

**How a professional fighting game studio documents a character from concept to
shipped fighter — applied to Western Heart.**

Synthesized from: Tekken 7/8 production structure (tekkenmods-docs), Riot's
character design method (Alex Jaffe, Project L), the pro move-data model.

## The Pipeline — 7 Stages

### Stage 1: IDENTITY
**Owner names the fighter.** One at a time, like the roster was built.
- Western Heart name + source fighter (e.g., Pantera ← King)
- The "real character" statement: who is this fighter REALLY? (Riot method:
  the source character is the abstraction; we design the real one)
- Design space claim: what territory does this fighter own that no other
  fighter touches? (Pantera owns panther-wrestler; SAM-∪R-Λ1 owns mech)
- Output: `roster/[code]/IDENTITY.md`

### Stage 2: DESIGN DOC
**Go wide, then lock.** (Riot: 10 one-paragraph kits, pick the winner.)
- Fighting style essence in one paragraph
- Signature mechanic/move — the ONE thing that defines them
- Gameplan: what does this fighter WANT to do in a match?
- Visual direction: base attire + alternates
- Output: `roster/[code]/DESIGN.md`
- Owner approves before any modeling starts.

### Stage 3: MODEL
**Chimera-build the base.** (Tekken naming conventions apply.)
- Base model: Tekken 7 skeletal mesh (default) or Tekken 3 (legacy mode)
- File naming: `[PREFIX]_CH_[code]_[part]_[variant]` (e.g., `SK_CH_ptr_bdu_P1`)
- Character ID assigned from the master table (permanent, never reused)
- Reskin per the design doc — real extracted textures recombined, never hand-made
- Output: model files in `assets/characters/[code]/`

### Stage 4: RIG
**Skeleton + physics.**
- SKT skeleton structure, PA physics asset
- Tekken 3 lesson: 27 rigid parts, no skinning (legacy). Tekken 7: full skeletal.
- Hitbox/hurtbox PROXY shapes defined here (separate from visual mesh —
  Tekken lesson: hitboxes ≠ visuals)
- Output: `SKT_CH_[code]`, `PA_CH_[code]`

### Stage 5: MOVESET
**Moves are data.** (Pro move model: animation + hitbox + hurtbox + hit
conditions + cancels.)
- Per-move checklist: animation ref, hit level (H/M/L/U), hurtbox, active
  frames, hit conditions, cancels
- Signature move built + playtested FIRST (Riot: prototype the core)
- Wrestling-mode moves use the throw property structure (suplex = Move +
  throw camera + two-character animation)
- Full movelist per fighter, documented in `roster/[code]/MOVESET.md`
- Output: move data files in `assets/characters/[code]/moves/`

### Stage 6: CUSTOMIZATION
**WWE-style attire system.** (Tekken CS/CCI/CI + No Mercy creation suite.)
- CS (Character Set): the fighter's customization data
- CCI slots: which body regions are swappable (head, torso, arms, legs, etc.)
- CI items: each alternate attire piece as a separate item
- EI: weapon/prop attachments
- P1 default + alternates per the design doc
- Output: `assets/characters/[code]/customization/`

### Stage 7: SHIP GATE
**Verify before claiming.**
- Likeness check: does the fighter look like the design doc?
- Moveset check: every move has all required data (no missing hitboxes)
- No-cannibalization check: does any other fighter own this design space?
- Playtest: does the signature mechanic have "juice"?
- Owner sees the fighter before it ships. No exceptions.

## Directory Layout (per fighter)

```
roster/[code]/
  IDENTITY.md      # Stage 1: name, source, real-character statement
  DESIGN.md        # Stage 2: style, signature, gameplan, visual direction
  MOVESET.md       # Stage 5: full documented movelist
assets/characters/[code]/
  SK_CH_[code]_bdu_P1.*    # Stage 3: base model
  SKT_CH_[code].*          # Stage 4: skeleton
  PA_CH_[code].*           # Stage 4: physics
  moves/                   # Stage 5: move data files
  customization/           # Stage 6: CS/CCI/CI/EI
```

## Naming Convention (adopted from Tekken)

`[PREFIX]_CH_[code]_[part]_[variant]_[map]`
- Example: `T_CH_ptr_bdu_P1_black_D` = texture, character, Pantera, body,
  Player-1 attire, black variant, diffuse map.

## Roster Status

7 of 51 named: Pantera (KIN/2), Demonio (JIN/6), Phantom (YOS/3), Diablo
(HEI/8), Skull (BRY/7), SAM-∪R-Λ1 (JAC/11), Saku Ra (XIA/5). 44 to go —
owner names them one at a time.
