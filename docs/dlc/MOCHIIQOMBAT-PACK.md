# MOCHIIQOMBAT PACK: post-100% DLC plan

**Status:** plan, 2026-10-29. Owner approved writing it (t329u). Nothing here is built yet.
Tiers: **OWNER** = owner words; **CANON** = in a repo (cited by path); **PROPOSAL** = planned here, owner to keep or cut.

## 0. What it is (OWNER)

The owner's framing (t326u, verbatim): "we're making Pokkén Tournament almost, just Western Heart / Immortal Qombat meets Mochiichao".

The Mochiiqombat Pack, as the owner specified it, adds the Pokkén Tournament roster's movesets and animations and puts Mochiichao models on top of the Pokémon models' rigs and animations. The new fighters join the WH roster, and each Pokémon's moves map to the matching Mochiichao's moveset.

- **Gate:** the pack unlocks only after the **base game is at 100%**. It is a post-completion DLC and not part of the base roster count (ROSTER.md and docs/ROSTER-COUNT-CANON-2026-10-21.md stay unchanged).
- **Story hook (CANON link):** in Mochiichao canon, R4's tournament is Sun Rā's Immortal Qombat, and Sun Rā is its secret true host (Mochiichao docs/canon/WESTERN-HEART-IN-MOCHIICHAO.md, t326u/t328u, PR #121 in that repo). In WH, Sun Rā **is** 不死クォンバット (CANON.md §7 SUN RĀ). PROPOSAL: the pack's mode is Sun Rā's pocket realm, with Mochiichao fighters pulled in under his stare. Naming law holds: everyone says 不死クォンバット and only Sun Rā says "Immortal Qombat".
- **Chao-Ranger tie (Mochiichao canon, t330u/t331u):** Pantera, Yukihyō, Sun Rā, Demonio and (late) Diablo are both Mochiichao and Rangers. PROPOSAL: in this pack they can appear in Mochiichao form, as alternates of their WH selves.

## 1. Roster mapping approach (PROPOSALS)

**Rule:** each Pokkén Tournament DX fighter maps to a Mochiichao candidate on **(1) body plan** first, because the rig and animations must fit, and **(2) type/element** second. The candidates come from the Mochiichao dex (mhvnsnt/Mochiichao-Diamond-Version-2d-fresh-start, show/production/mochichao-design/SPECIES-DATA-R*.md) or from Chao-Rangers already transplanted there. **Every row is a PROPOSAL.** The owner picks.

| Pokkén DX fighter | Body plan / type | Mochiichao candidate (PROPOSAL) | Note |
|---|---|---|---|
| Lucario | biped canine aura fighter / Fighting-Steel | Pantera (big-cat Chao-Ranger; Leo-man form) or Fenrirune (rune-wolf A8) | body plan fits; Pantera has WH canon moves |
| Blaziken | biped avian kicker / Fire-Fighting | Diablaze (imp ladder A4) | Fire biped |
| Charizard | winged dragon / Fire-Flying | Halberdrake (A2) or Sun Rā (Mythical Flame, t328u) | Sun Rā is the owner's call |
| Machamp | four-arm biped grappler | Excavarm / Magmole (A6) | grappler body |
| Gardevoir | slender biped psychic | Twinvow (A9) | |
| Weavile | small biped clawed / Dark-Ice | Frosfang (A8) or Yukihyō (snow-leopard form) | |
| Suicune | quadruped / Water | Rainokapi (C2-6) or Tuskicorn (C2-10) | quadruped rig |
| Gengar | squat biped ghost | Spindevil (B7) | |
| Braixen | biped fox caster / Fire | Cinderewe (B3) | check body plan |
| Chandelure | floating ghost | a spirit-class R4 species (SPECIES-DATA-R4-SMALL-AND-SPIRIT.md) | floater rig |
| Sceptile | biped reptile with blade arms / Grass | Verdilance (A3) | |
| Garchomp | land-shark biped dragon | Slashfoss (C2-5) | |
| Mewtwo / Shadow Mewtwo | humanoid psychic legendary | Goddgachuu (rarest; Diablo owns one, t324u) | owner call; Shadow form = Diablo's |
| Empoleon | biped penguin / Water-Steel | Helmbeak (C2-7) | |
| Darkrai | floating humanoid / Dark | Demonio (Chao-Ranger, winged form) or none | owner call |
| Croagunk | small biped frog / Poison-Fighting | Clearibbit (C2-11) | |
| Aegislash | living sword-shield | Bastihound (A1) or an R4 toy-battle species | unusual rig |
| Scizor | biped insect with pincers | an R4 toy-battle species (SPECIES-DATA-R4-TOYBATTLE.md) | |
| Decidueye | biped owl archer | Thouswings (A7) | |
| Blastoise | heavy biped turtle with cannons | Atollossus (A5) | |
| Pikachu / Pikachu Libre | small biped mascot | the Mochiichao mascot species (owner call) | Libre = luchador attire |

The roster list is the Pokkén Tournament DX roster as published. Verify it against the source data in §2 before any build. Support Pokémon are out of scope unless the owner adds them.

## 2. Data sources (order of preference)

1. **The user's own repos first:** the WH teardown/moveset library (moveset-library/, teardown/, docs/movesets/), the Mochiichao repo's species sheets and models, and any Pokkén material in the private assets repo. As of 2026-10-29 WH main has no Pokkén data; search the private repo next.
2. **The Pokkén Tournament (DX) modding community:** published file-format notes, model/animation extraction tooling and frame-data wikis. Use them for reference and for the owner's own legally obtained copy only. Log each tool and source in docs/CREDITS.md before use.
3. **Frame data / move lists** from community wikis, used only to check move names, inputs and frame timings.

**Raw assets stay private:** extracted models, rigs and animations live only in the private assets repo and load at runtime only when globalThis.__WH_PRIVATE_ASSETS is present (docs/rules/COMPLETE-WIRING-LAW.md rule 4; docs/tech/CREATION-SUITE.md). The public repo holds only manifests, mapping tables and code.

## 3. Retarget pipeline (PROPOSAL, reusing WH pipelines)

1. **Extract** the Pokkén fighter rig + animation set (private) and log provenance.
2. **Normalise** using the fixes already found in docs/RETARGET-MOVEDECODE-RESEARCH-2026.md: Z-up vs Y-up, animation channels on the wrong nodes, scene placements baked into clips, hard L/R skin-weight tearing.
3. **Skin the Mochiichao model onto the Pokémon skeleton** ("model on top of the rig"): fit the mesh to the Pokkén bind pose, auto-weight, then hand-fix seams. Follow docs/MODEL_IMPORT_AUTORIG.md, docs/HAND-RIG-STANDARD-2026-10-22.md and docs/FACE-RIG-STANDARD-2026-10-22.md.
4. **Play the original clips unchanged** on that skeleton. No cross-skeleton retarget is needed when the body plan matches, which is why body plan leads the mapping in §1.
5. **Proof:** per fighter, render idle + 5 signature moves at 390x844 and at desktop size into docs/proof/mochiiqombat/, with an orientation check (docs/RENDER-ORIENTATION.md).

## 4. Moveset alignment rules

- **One move = its own animation**, per docs/MOVE-MATCHING-SYSTEM.md. No bulk JSON row-matching (the PR #988 failure).
- Map **each Pokémon move to the matching Mochiichao move** by (1) the same function in the Mochiichao learnset, then (2) element/type, then (3) shape (strike / projectile / grab / counter). Keep one mapping table per fighter. Any unmatched move is flagged, never guessed (docs/RULES_NO_GUESSING.md).
- **Inputs:** translate Pokkén's phases (Field / Duel) and its buttons onto WH's LP1/RP2/LK3/RK4 slots. The translation table goes in the pack spec and needs owner sign-off.
- **Counter triangle** (normal > grab > counter > normal): PROPOSAL to keep it as a pack-only rule layer, with no change to base-game combat.
- Mochiichao creatures only cry, they don't talk (Mochiichao canon). Use voice slots for cries.

## 5. How it plugs into WH systems

- **Moveset editor** (docs/MOVESET_EDITOR_SPEC.md): pack fighters appear on the MOVE-SET screen like any fighter. The library browser is filtered to pack clips plus compatible base clips, and wrongly mapped moves stay visible so they can be fixed.
- **Sweeps:** every pack fighter goes through the same batch passes as the base roster (batch-rig sweep, docs/MOVESET-COVERAGE.md, docs/MOVESET-STUB-AUDIT-2026-10-22.md, fighter completeness audit) before release.
- **Roster/select:** a separate MOCHIIQOMBAT tab on the select grid, hidden until 100%. Base roster counts and canon names stay untouched; names go through tools/canon.
- **Per-character isolation** (docs/PER-CHARACTER-ISOLATION.md): pack fighters live in their own folders; no edits to base fighters.

## 6. Gate

- Unlock = base game at 100% (all completion flags). PROPOSAL: Sun Rā's eyes open over the title screen when it unlocks.
- Build order: only after the base game ships at 100%. This doc reserves the plan; no build work is scheduled.

## 7. Open questions for the owner

1. Approve or replace each §1 mapping. Who takes the Pikachu slot? Is Mewtwo → Goddgachuu acceptable, given its rarity?
2. Which Pokkén source copy and tools are approved for extraction?
3. Keep Pokkén's Field/Duel phases and counter triangle, or play pure WH rules?
4. Support Pokémon: in or out?
5. Do the Chao-Rangers' Mochiichao forms join the pack as alternates?
