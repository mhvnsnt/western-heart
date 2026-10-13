# Western Heart — Chimera Build Architecture
Owner-directed 2026-10-13. This is the foundational design principle.

## The Foundation (never changes)
- **Input style:** Tekken. The 1/2/3/4 limb buttons, f/b/u/d directional notation, strings, stances, while-rising, crouch dash — Tekken's input DNA is the base.
- **Play style:** Tekken + Urban Reign. Open-plane 3D movement, juggle system, wall game from Tekken. Street brawling, weapons, destructible environments, multi-fighter chaos from Urban Reign.
- **Gameplay feel:** Capcom (Street Fighter). The responsiveness, the hit-stop, the special move motion inputs layered where they fit.

## The Federation (built on top)
Every other game contributes MECHANICS, not input schemes:

| Game | What we take |
|------|--------------|
| Tekken 3/6/7/TTT2 | Input foundation, movelists, customization, legacy |
| Urban Reign | Brawl mode, weapons, environments, 60+ fighter archetypes |
| WWF No Mercy | Moveset slot system, CAW parts, AKI grappling |
| WWE WrestleMania XIX | Deeper moveset tree, CAW system, arena traversal |
| Virtua Fighter 5 | Defensive mechanics, throw escapes, weight classes, ring-outs |
| Dead or Alive 6 | Triangle system (strike > throw > hold), counter holds, stun game |
| Soulcalibur VI | 8-way run, guard impact, soul charge, weapon ranges, ring-outs |
| Eastern Mind | World, narrative, visual soul, the five lands |

## The Rule
Tekken's inputs are the language. Every federated mechanic must speak that language.
A DOA counter-hold maps to a Tekken input. A Soulcalibur guard impact has a Tekken notation.
Nothing replaces the foundation — everything plugs into it.

## The Build Order
1. Tekken input core (resolver, move table, properties)
2. Urban Reign brawl layer (multi-fighter, weapons, environments)
3. Federated mechanics, one game at a time (VF defense → DOA triangle → SC movement)
4. Moveset library (176 slots, all animations indexed)
5. Create Fighter (Tekken 7 base + WWE CAW parts)
6. Stages (7 Eastern Mind lands from WMXIX arenas)
7. Roster (28 named + incoming)

## What It Feels Like (owner 2026-10-13)
Western Heart feels like **Tekken with an Eastern Mind Tong-Nou mod** — and all the
federated chimera mechanics built in. Like a **lost multiverse bastard child**:
the Tekken you know, warped through Tong-Nou's dreaming head, carrying DNA from
every fighting game worth stealing from. Familiar enough to pick up, strange
enough to never put down.

## WRESTLER MODEL SEPARATION (owner 2026-10-13)
Wrestling GAMES stay in the federation — their mechanics (moveset slots, CAW parts,
AKI grappling, arena traversal) are Western Heart DNA. But wrestler CHARACTER MODELS
move OUT to a separate game.

- **Western Heart keeps:** everything EXCEPT wrestler models. All mechanics, all
  systems, all non-wrestler characters, all stages, all audio.
- **Wrestler models go to:** `mhvnsnt/wrestling-game` — the standalone wrestling game.
  All 2,826 models from WWF No Mercy + WWE WrestleMania XIX, plus future pulls
  (Def Jam: Fight for NY, WWE 2K-style models from DeviantArt).
- **Why:** art style mismatch. Wrestler models are realistic; Western Heart fighters
  are stylized fighting-game characters. They don't belong in the same roster visually.
- **Exception:** a wrestler model MAY come into Western Heart ONLY with a deep
  reskin to match the WH art style. Default is separation.

WWE animations CAN work in a Tekken-style engine — Def Jam: Fight for NY proved
wrestling/grappling animations work inside a 3D fighter. The animation data stays
federated; the character models live in the wrestling game.

## STREET FIGHTER FEDERATION (owner 2026-10-13)
Owner prefers Tekken over Street Fighter. Tekken is the game; SF is research.

- **SF-based characters keep their SF movesets, attacks, and animations** — the
  cool things SF does differently stay in. A Hadoken-type move can keep its
  quarter-circle / down-forward punch input.
- **But they PLAY like Tekken.** Tekken + Urban Reign is the input style and the
  play style (Urban Reign plays kind of like Tekken — same language). An SF
  character is a Tekken fighter wearing SF moves, not an SF fighter dropped
  into the game.
- **Everything from SF games becomes proprietary to Western Heart:** renamed,
  reskinned, transformed into our universe. Nobody looks at it and says "that's
  literally Street Fighter" — same as the transformation law for everything else.
- **The line:** SF is mined for interesting moves and mechanics. It NEVER
  replaces the Tekken play style. If an SF idea would change how the game plays
  at its core, it doesn't go in — or it gets rebuilt to speak Tekken first.

## TRANSFORMATION LAW (owner 2026-10-13)
100% of every teardown game gets incorporated into Western Heart somehow, somewhere. But nothing stays proprietary to the source — everything gets transformed into Western Heart's own through editing, owner alterations, AI generation/alteration, and whatever we can pull in.

Eastern Mind is the universe bible (50% bible) but nobody should look at it and say "that's literally Tong-Nou." People who know Eastern Mind get the nod. Everyone else just sees our world.
