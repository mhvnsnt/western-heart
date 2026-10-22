# Owner Directives — M.Dogg's standing orders for Western Heart

Living document. Updated every time the owner sets a directive. Newest first.

## 2026-10-22

- **ANTI-CLOBBER LAW (permanent — written in blood after PR #579).** On
  2026-10-22 PR #579 committed stale full-file copies (base from Oct 17),
  wiping 427 lines of `game/js/assets.js`, 113 of `game/js/main.js`, 32 of
  `game/js/game.js`, 25 of `index.html`, 316 of `WORKLOG.md` — Torch broke
  live. Root cause: agents working from stale clones committing whole files.
  Never again. Four rules, no exceptions:
  1. **Sync to latest main BEFORE starting any file work, and again BEFORE
     committing.** A base more than a few hours old gets re-synced.
  2. **Surgical edits only** — never write a whole file when a targeted edit
     will do. Fresh sync + surgical edits; never commit stale full-file
     copies.
  3. **Any diff deleting >20 lines must be intentional and called out** in
     the PR body (`## Reverts` section naming each file, or the
     `owner-approved-revert` label).
  4. **If your base is more than a few hours old, re-sync.**
  Enforced by machinery, not memory: the `clobber-guard` CI check blocks any
  PR whose version lacks lines main added after the PR's base;
  `tools/clobber-check/clobber_check.py` runs the same check locally before
  pushing; the `git_merge.py` merge helper refuses to merge such PRs.
- **Everything goes in the repo.** Every conversation — everything the owner
  says, everything the assistant says, all research — is saved into the repo
  every time: `docs/owner-directives.md`, `docs/research/`, `docs/decisions/`.
  Never wait to be asked.
- **Division of labor.** Owner does surgical hand-tooling (the parts AI
  struggles with — faster than 20 back-and-forths). Crew does automatic
  pulling, wiring, industry-standard open-source stack. Crew gets surgical
  only when asked. Owner wants to feel like a real game dev (Tekken studio /
  2K studio) doing non-code work: art direction, animation review, tuning,
  playtesting. No interest in learning to code.
- **Collaboration loop.** Crew ships a piece → it goes live on
  https://mhvnsnt.github.io/western-heart/ → owner reviews and hand-tweaks →
  crew runs industry-standard automation → shows result → repeat. All inside
  the customization suite, which is improved as a deliverable each round.
- **Round trip.** Suite gets a save/export button → owner tweaks, downloads a
  patch file, sends it in chat → crew validates and applies via PR. Suite can
  also load crew-staged tweak kits.
- **Tag-team community creations.** The owner + crew build like WWE Community
  Creations but two-way: two people in different places working on the same
  character, both involved — the feature WWE lacks.
- **Merge after every pass.** Clean merges into main, no clobbering either
  side (via `tools/git-merge/git_merge.py`).
- **No-stubs rule.** If it's in the repo, it's wired up and working. Audit
  regularly; stubs get finished or removed.
- **Tekken base first.** Full skinning pipeline (bind pose, heat-map skinning,
  rigging, boning) for every character/GLB. Perfect the Tekken base (skeletons,
  models, moves, customization) so everything built on top works.
- **Game feel.** Feels like Tekken, with extra physics — partial ragdoll
  inspired by Gang Beasts / Human Fall Flat / Mortal Kombat Royal Rumble.
  NOT fully ragdoll.
- **WWE 2K26.** Pull animations, code, physics — NOT models.
- **Tripo auto-intake.** New Tripo models get rigged ASAP to their character
  rig. First live intake: Torch Attire 3 "Bald eagle."
- **Torch Attire 3 is the reference piece.** Full jiggle set (breasts, belly,
  hips/ass, thighs, camel-toe); repaint painted-on clothing as skin with
  pores; full anatomy (areolas, clitoris, labia) from Scarlett/Madeline
  reference models; proof must include motion capture, not just stills. Once
  perfected here, the system rolls out to other models.
- **Character select rule.** Attires ladder into their fighter; an attire is
  NOT its own selectable model unless the owner explicitly said so
  (e.g. Yoshimitsu ladders into Phantom's attires).
- **Asset sourcing.** Ripped/ported models (Tekken extracts, SmutBase ports)
  are raw material — transform heavily into the Western Heart universe's own
  characters. Owner made this call; legal caution was given and acknowledged.
- **Master roadmap.** All movesets from Tekken teardowns + canon moves;
  Tekken-like character creation and select screens; 100% teardown of all
  Tekken games (then other games' teardowns); the game feels like all Tekken
  games combined + our own stuff on top, then turned proprietary.
- **Hardened Mind Within mode.** Tekken "Devil Within"-style mode; each
  character selectable with their own storyline; wave/tournament feel like
  Mortal Kombat Royal Rumble in places. All fighters rigged and working for
  it and all other modes.
- **No full game downloads.** Use `tools/depot-pull/` — pull only needed
  files piece by piece. Disk rules are mandatory for all agents.

## 2026-10-21

- All fixes by AI agents, no hand-tooling by the owner (later refined — owner
  now does surgical hand-tweaks in the loop).
- Model-quality round: fix Pantera weights, Doc Frank feet, root-cause the
  "backwards decrypt" in the pipeline (not per-model tweaks), Doc Frank
  attires Tripo-first ordering.
- `git_merge.py` saved to `tools/git-merge/` via PR #495 for merging clean
  green PRs without the GitHub merge API.

## DISPLAY ORDER LAW (2026-10-22, permanent)

Tripo 3D models show FIRST and foremost for every fighter; Tekken attires/models ladder BEHIND as back-slot attire choices.

**SOLE EXCEPTION: Pantera.** His Attire 1 is a King reskin, but the user already customized it, so it may show first/up front. He is the ONLY exception; every other fighter's Tekken reskins go later in the ladder. No future pass shall "fix" Pantera's attire order.

## IDENTITY CANON + DEDUP LAW (2026-10-22, permanent)

- **Rave = Kiko Tanaka = Ghost: ALL THE SAME PERSON.** One select entry only
  ('rave'). Never split into separate fighters.
- **Mary Posa goes OVER Zafina.** One entry (MARIPOSA — repo canon name; see
  below); Zafina is never a separate fighter. Zafina's Tekken in-game model
  ladders BEHIND Mariposa's custom attires as a back-slot attire choice.
- **Phantom is the select entry.** Yoshimitsu ladders into Phantom's attires
  as choices, never a separate slot.
- **Doc Frank = Bosco** (Tekken's Doctor Bosconovitch). One entry ('docfrank').
- **Charger = the proprietary Blanka replacement.** Blanka holds no select
  slot; his moves/identity live under Charger.
- **Dedup law** (owner verbatim 2026-10-22): "all of the character slots need
  to be fixed to where it's no duplicates showing it's no duplicate images
  showing and no duplicate fighters only duplicates will be like the ladders
  of the attires of you know the Tekken characters coming later after the
  proprietary characters in the attire list" — no duplicate fighters, no
  duplicate card images; the ONLY allowed repetition is attire ladders, with
  Tekken characters as later attire choices behind their proprietary fighter.
- Display-order note: Mariposa's Slot 1 default is the Butterfly Default
  (owner 2026-10-19 exception to the Tripo-first law — pipeline-built
  Tekken-wire custom, same standing as Pantera's Attire 1).

### Open naming questions (owner to decide — do NOT guess)
- Repo canon name is **MARIPOSA** (butterfly-themed; owner-approved across
  PRs/renders). "Mary Posa" appears nowhere in-repo, reads as voice-typed
  "mariposa". Kept as MARIPOSA pending owner confirm.
- 'ryuji' (RYUJI) vs 'ryuji-rock' (RYUJI ROCK hybrid): two slots, distinct
  concepts — needs owner call on whether they merge.
- 'armor-king' holds a slot under its Tekken name (WH rename pending owner pick).
- 'zangief' / 'vega' / 'iori' are working names; WH names pending owner pick.
- Kevin's Tripo (kevin-tripo) is not in the repo yet — his select default
  stays the Baek model until it lands.
