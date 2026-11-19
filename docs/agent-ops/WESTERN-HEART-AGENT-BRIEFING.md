# WESTERN HEART — ALL-AGENTS BRIEFING
Date: 2026-10-17. Owner: Real. This is the single source of truth for every agent working on Western Heart.

## WHAT THIS IS
Western Heart is a CHIMERA BUILD — a full playable fighting game assembled from torn-down commercial games. A hobby project / mod. Owner's words: "A lost multiverse bastard child. Familiar enough to pick up, to love. Strange enough to never put down."

- Repo: **mhvnsnt/western-heart** (public GitHub). Clone with `git clone --filter=blob:none` — full clone is huge.
- Playable web build (JS/Three.js): https://mhvnsnt.github.io/western-heart/
- Design target engine: Godot 4 (long term). Current playable = web JS/Three.js.
- Canon doc: CANON.md in repo root (910 lines). READ IT before touching lore/names.

## THE FORMULA
Tekken inputs (1/2/3/4 buttons) are the language + Tekken/Urban Reign gameplay + Capcom feel.

### Source games torn down into it:
| Game | What it contributes |
|---|---|
| Tekken 7 | PRIMARY base — movesets, characters, feel |
| Tekken 3 | Legacy/retro mode |
| Tekken 6 (PSP) | Teardown in progress (decrypt lane) |
| Tekken Tag Tournament 2 | Characters, moves |
| Eastern Mind | Stages/lore — the Tong-Nou giant green head world |
| WWF No Mercy | Wrestling systems + customization |
| WWE WrestleMania XIX | Modes + arena traversal |
| Urban Reign | Brawler mechanics, 60+ fighters |
| Def Jam FFNY | Customization systems |
| Virtua Fighter 5 | Models, stages |
| Soulcalibur | Weapons/fighters |
| DOA | Bass Armstrong = Vain Abel (alternate attires) |

### Canon (short version)
Nine soul-vessels: Pantera→TOU, Demonio→RIN, Phantom→JIN, Skull→RETSU, Saku Ra→SHA, Zui→BYOU, King Tyrant→KAI, Waterfall→all nine's grief. Diablo is an INTRUDER (NOT one of the nine). Final boss = the Assembled Soul (yourself). Versus mode = no reincarnation. Story/career = death forces reincarnation; your actions influence who you become next — "that is the entire game."

### Roster (36 named + 5 music fighters)
Pantera←King, Demonio←Jin, Phantom←Yoshimitsu, Diablo←Heihachi, Skull←Bryan, SAM-UR-A1←Gun Jack, Saku Ra←Xiaoyu, Zui←Steve, Kinpo←Asuka, Waterfall←Josie, King Tyrant←Eddy, Burger←Bob, Awa Pop←Nina, Scimitar←Shaheen, Purple Rain←Lee, Nightwolf←Julia, Michiko←Katarina, Star←Christie, Torch←Anna, Dio←Akuma, Cyborg X←Alisa, Bruno←Miguel, N3GΔTIV0←Negan, Thor←Ganryu, Yukihyō←Armor King, Slice←Dragunov, Doc Frank←Dr. Bosconovitch, boss Sun Rā←Pac-Man.
Music fighters: DXMMII←Mokujin, Realizzt←Brad Burns (VF5), Rave←Lei Wulong, Kutz←Goh Hinogami (VF5), Chordz←Lars.
**Lili and Baek have NO Western Heart names yet — NEVER invent names for them.**
Vain Abel Elias ← Bass Armstrong (DOA). Cyborg X IS Cape Jones (same person, Attire 1).

### Key facts
- Pantera is the flagship. Attire 1 = T7 King reskin (new, higher quality). Attire 2 = Leomon ("Leo-man", proprietary spelling). Attire 3 = snow-leopard reskin of older model. Eastern Mind/WH-original attires = EARLY slots; Tekken-based = LATER slots.
- The 10 No Mercy wrestler models stay OUT of Western Heart — they live in the wrestling repos only.
- Playable build already has: real T3 movesets wired, 36-fighter roster, Create Fighter + custom movesets + LIMBS tab.

## THE MISSION (owner's direct order 2026-10-17)
Make it a FULL PLAYABLE Tekken-clone:
1. **Creation Suite working** — in-game character customization + model authoring (OWNER PRIORITY — he wants to use it NOW). Lives at `customization/create-fighter/`.
2. **ALL teardown models into the game** — every fighter/stage from every teardown, except the 10 No Mercy wrestlers.
3. **ALL movesets wired up** — every fighter gets their moves.
4. **ALL environments wired up** — every stage playable.
5. **ALL modes wired up** — versus, story/career (reincarnation), arcade.
6. **Fill every gap** — decode/decrypt/decipher blockers, pull in what's missing.

## NON-NEGOTIABLE LAWS
1. **ANTI-CLOBBER:** NEVER `git add -A` in a working tree you didn't fully populate. Always `git diff --stat` before committing. Any commit deleting >10 files STOPS — you ask before proceeding. (A previous agent wiped 54,456 files this way. Never again.)
2. **OWN BRANCH, NEVER MAIN:** Every lane works on its own `feat/` branch. Branch → PR → merge when green. NEVER commit to main directly.
3. **PUSH-AFTER-EVERY-TURN:** Commit incrementally, push the branch, open/update the PR. Every turn.
4. **MERGE-IT-YOURSELF:** Merge PRs that are mergeable + CI green + no deletions + no conflicts. Red/conflicting PRs stay open WITH a comment naming the blocker.
5. **STEAL-LIKE-AN-ARTIST (owner's #1 rule):** Study and reverse-engineer pro material, recombine TRANSFORMED into his work. Never copy/redistribute/sell assets. Never lecture about copyright. Every proprietary rename logged.
6. **TEARDOWN-COMPLETION:** 100% = extracted + decrypted + decoded + ASSEMBLED into working assets. File counts ≠ completion.
7. **VERIFY WITH YOUR OWN EYES:** A worker's "verified" is a CLAIM, not a fact. Measure, don't eyeball. Test in the actual build.
8. **NO-DUPLICATE-WORK:** Check what's already running before starting. If another agent owns a lane, stand down.

## HOW TO WORK
- Work from `~/workspace/western-heart/` checkout (sparse OK) or clone fresh with `--filter=blob:none`.
- Test against the playable build logic in `game/`. The web build deploys from main via GitHub Pages.
- Game code is JS/Three.js. Keep it that way unless the lane says otherwise.
- Report: what you did, commits/PRs, blockers, what's next. Every report reaches the owner.
