# Pull Structure — Where Game Files Go and How They Get Wired

**Created:** 2026-10-23 | **Coordinator:** pull-wiring lane
**User directive:** "pull all the creation stuff and all the stuff I mentioned
from the WWE games and put it into the repo and wire it up best way possible.
Same with all the other games I mentioned pull in files from them into the
repo wire them up in the best place possible in the best way possible"

---

## The Golden Rule: Private vs Public

**western-heart is a PUBLIC repo.** Raw commercial game files NEVER go here.

| Goes to PRIVATE repo | Goes to PUBLIC (western-heart) |
|---------------------|-------------------------------|
| Raw models (.glb, .fbx from games) | Our proprietary wiring code |
| Raw textures | Catalog JSONs (our format) |
| Raw animations (game formats) | Converted animation banks (our format) |
| Proprietary file formats | Research docs and technique briefs |
| Anything extracted 1:1 from a game | Anything we built/transformed |

**The test:** if you extracted it and didn't transform it, it's private.
If you built it, converted it to our format, or wrote it from research,
it can go public.

---

## Teardown Directory Map

### Existing (wrestling/fighting)

| Dir | Game | Status |
|-----|------|--------|
| `teardown/wmxix/` | WrestleMania XIX (GC) | Full teardown, caw-parts cataloged |
| `teardown/wwf-no-mercy/` | WWF No Mercy (N64) | Full teardown |
| `teardown/wwe-wrestlemania-xix/` | WM XIX | Teardown docs |
| `teardown/wwe-2k/` | WWE 2K (shared docs) | Docs hub |
| `teardown/def-jam-fight-for-ny/` | Def Jam FFNY | Teardown in progress |

### New (2026-10-23 pull wave)

| Dir | Game | App ID | Owned | Priority pull |
|-----|------|--------|-------|---------------|
| `teardown/wwe2k19/` | WWE 2K19 | 846350 | YES | Animations, CAW parts |
| `teardown/wwe2k20/` | WWE 2K20 | 1015500 | YES | Animations, rigs, CAW, customization |
| `teardown/wwe2k22/` | WWE 2K22 | 1255630 | YES | Animations, rigs, customization, creation suite, community creations |
| `teardown/firepro/` | Fire Pro Wrestling World | 564230 | YES | CPU sim, creation depth, AI logic |
| `teardown/wrestling-empire/` | Wrestling Empire | 1620340 | YES | Wrestling systems, world-building |
| `teardown/yakuza-kiwami/` | Yakuza Kiwami | 834530 | YES | Beat-em-up combat, world design |
| `teardown/gang-beasts/` | Gang Beasts | 285900 | YES | Physics technique |
| `teardown/nioh/` | Nioh: Complete Edition | 485510 | YES | Character depth, mythology structure |

All owned on Steam (vil3m), confirmed 2026-10-23.

---

## Wiring Map: Pull → System

### Creation Suite (`packages/creation-suite/`)

| Source | What | How it wires |
|--------|------|--------------|
| WWE 2K22 CAW parts | Parts library | Per-source catalog → `src/catalogs.js` (`source_game: "wwe2k22"`) |
| WWE 2K20 CAW parts | Parts library | Same, `source_game: "wwe2k20"` |
| WWE 2K19 CAW parts | Parts library | Same, `source_game: "wwe2k19"` |
| WMXIX caw-parts | Parts library | Already cataloged (files.tsv) |
| 2K22 customization structure | Slots, categories | `src/slotmap.js`, `src/layering.js`, `src/menu.js` |
| Fire Pro creation depth | Parametric depth | Expand `src/morphs.js`, `src/dna.js` |
| Nioh character depth | Stats/builds | New: progression layer |

### Animation System (`game/assets/anim/`)

| Source | What | How it wires |
|--------|------|--------------|
| WWE 2K22 animations | Wrestling moves | Convert → animation bank format |
| WWE 2K20 animations | Wrestling moves | Same |
| T7 animations (Grok) | Fight moves | Already in progress (PR #863) |

Show/fight lock applies to ALL: tag every clip `"anim_set": "FIGHT"` or `"SHOW"`.

### AI / Simulation (`game/js/`)

| Source | What | How it wires |
|--------|------|--------------|
| Fire Pro CPU sim | Watch mode | New: `game/js/simulation.js` |
| Fire Pro AI logic | Fighter behavior | `game/js/ai/` (behavior programming) |

### Physics (`game/js/`)

| Source | What | How it wires |
|--------|------|--------------|
| Gang Beasts technique | Partial-ragdoll blend | `game/js/softbody.js`, `game/js/physics.js` |
| (existing) Jolt soft-body | Muscle/jiggle | Already merged (PR #846) |

### Story Mode (Heart and Mind Within)

| Source | What | How it wires |
|--------|------|--------------|
| Yakuza Kiwami combat | 3D brawling | Story mode combat design |
| Wrestling Empire world | World-building | Story mode structure |
| Yakuza world design | Dense spaces | Arena pipeline |

### Canon Building (docs only, never lore)

| Source | What | How it wires |
|--------|------|--------------|
| Nioh mythology structure | Systematization method | Methodology docs for Eastern Mind canon |

**Canon comes from CANON.md ONLY. Never copy lore from any game.**

---

## Pull Pipeline: Extraction → Wiring

```
1. EXTRACT (Steam via DepotDownloader)
   └── Raw files → PRIVATE repo
         │
2. CONVERT (our tools)
   └── Our format → PUBLIC repo (teardown/<game>/)
         │
3. CATALOG (per-source)
   └── catalog JSON → packages/creation-suite or game/assets
         │
4. WIRE (into systems)
   └── Code changes → feature branch → PR → 6/6 green → merge
```

## Coordination

| Lane | Does | Contact |
|------|------|---------|
| Grok | T7 Steam extraction, T8 select | Issue #866 |
| Top-5 coordinator | Research all 5 games | Issue #866 |
| Pull-wiring (this doc) | Receiving end, structure, wiring | Issue #866 |
| WWE DepotDownloader | Needs Steam auth | Blocked — see #866 |

## Steam App IDs (quick ref)

```
WWE 2K19: 846350          WWE 2K20: 1015500         WWE 2K22: 1255630
Fire Pro: 564230          Wrestling Empire: 1620340  Yakuza Kiwami: 834530
Gang Beasts: 285900       Nioh CE: 485510            Tekken 7: 389730
```

## Status

- [x] Structure created (this PR)
- [ ] WWE 2K19/2K20/2K22 extracted (blocked: Steam auth)
- [ ] Fire Pro systems documented (top-5 coordinator)
- [ ] Yakuza/Gang Beasts/Nioh/WE documented (top-5 coordinator)
- [ ] T7 extraction (Grok, in progress)
- [ ] First wiring PRs (pending pulls)
