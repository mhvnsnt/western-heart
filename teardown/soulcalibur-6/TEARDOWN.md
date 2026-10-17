# Soulcalibur VI — Teardown

**Game #8 for the Western Heart chimera build.** Owner-directed 2026-10-13.

## Source

| Item | Details |
|------|---------|
| **Title** | Soulcalibur VI (2018) — most recent mainline SC |
| **Developer** | Project Soul / Bandai Namco |
| **Engine** | Unreal Engine 4 |
| **Platform target** | PC/Steam (preferred for extraction) |
| **Size** | ~32GB installed |
| **Status** | **NOT YET ACQUIRED** (2026-10-13) |

### Why not yet pulled

1. **Not on Archive.org** — SCVI is a 2018 commercial title still sold on Steam. No free
   dump exists on IA (verified via advancedsearch 2026-10-13; only videos/trailers found).
2. **Disk** — VM at 93% (7.8GB free). A 32GB game cannot land here.
3. **Steam Workshop assets ARE available** — see below. These cover the character models.

### Pull strategy (when disk/owner allows)

- **Option A:** Owner purchases SCVI on Steam → SteamCMD backup → transfer .pak files.
  UE4 .paks extract with standard tools (FModel supports SCVI — it's UE 4.x).
- **Option B:** Steam Workshop collections (FREE, no game needed):
  - Shadow Master SC2 collection: 16 chars × 2-4 costumes (Source .mdl → Crowbar → Blender)
  - Rolandz SCIV collection: 32 ragdolls + 16 weapons
  - Standalone: Nightmare SCIV SFM, Shura SCIV, Taki Soul Edge
- **Option C:** rigmodels (5 direct): Cassandra, Amy, Seong Mi-na, Xianghua, Hwang (SC3)
- **Option D:** rolance DeviantArt SCVI XPS gallery (12 items, incl. 2B)

Full model-hunt catalog: `~/workspace/game-reverse-engineering/models/soulcalibur-hunt/HUNT-RESULTS.md`

## Roster (SCVI base + DLC)

| # | Fighter | Weapon | Style | Notes |
|---|---------|--------|-------|-------|
| 1 | Mitsurugi | Katana | Samurai | Series poster boy |
| 2 | Sophitia | Sword + Shield | Greek | — |
| 3 | Siegfried | Zweihander | Knight | — |
| 4 | Nightmare | Soul Edge (zweihander) | Azure Knight | Boss material |
| 5 | Kilik | Staff | — | — |
| 6 | Xianghua | Jian | Chinese sword | — |
| 7 | Maxi | Nunchaku | — | — |
| 8 | Ivy | Snake sword | Aristocrat | Transforming weapon |
| 9 | Yoshimitsu | Katana | Ninja | ← already have as Phantom's base |
| 10 | Astaroth | Great axe | Golem | — |
| 11 | Taki | Dual kodachi | Ninja | Pairs with ninja crew |
| 12 | Voldo | Dual katars | Blind contortionist | Unique |
| 13 | Cervantes | Dual swords + pistol | Undead pirate | — |
| 14 | Seong Mi-na | Naginata | Korean | — |
| 15 | Talim | Dual tonfa | Wind priestess | — |
| 16 | Raphael | Rapier | French fencer | — |
| 17 | Zasalamel | Scythe | Immortal | Fits soul trial |
| 18 | Tira | Ring blade | Split personality | Jolly/Gloomy stances |
| 19 | Grøh | Dual swords | New (SCVI) | — |
| 20 | Azwel | Gauntlets | New (SCVI) | Boss |
| 21 | Geralt | Steel + silver swords | Guest (Witcher) | — |
| 22 | 2B | Virtuous Contract | Guest (Nier) | DLC |
| 23 | Haohmaru | Katana | Guest (SamSho) | DLC |
| 24 | Hwang | Katana | Korean | DLC |
| 25 | Cassandra | Sword + Shield | Greek | DLC |
| 26 | Amy | Rapier | French | DLC |
| 27 | Hilde | Sword + spear | German knight | DLC |
| 28 | Setsuka | Iai katana | Japanese | DLC |
| 29 | Inferno | Soul Edge | Flame demon | Final boss |

## File Formats (UE4 — documented, not yet extracted)

| Format | Description | Tool |
|--------|-------------|------|
| `.pak` | UE4 package archives | FModel / repak / QuickBMS |
| `.uasset` | UE4 assets (meshes, anims, textures) | FModel (has SCVI profile) |
| `.umap` | UE4 maps (stages) | FModel |

SCVI runs UE 4.x — the same toolchain already pulled for Tekken 7
(`~/workspace/tools/tekken-decrypt/`: FModel, repak, aluigi QuickBMS) applies directly.

## What SCVI Contributes (Federation)

Full mechanics reference: **[docs/SCVI-MECHANICS.md](docs/SCVI-MECHANICS.md)**

Priority systems for the chimera build:
1. **8-way run** → arena-mode movement
2. **Guard stamina / crush** → universal defense resource
3. **Guard Impact** → skill parry (+28/+16/+8)
4. **Reversal Edge** → comeback / soul-clash
5. **Soul Charge** → soul-vessel power state
6. **Lethal Hit** → conditional combo starters
7. **Ring-out** → arena kill condition
8. **Weapon ranges** → weapon-fighter move properties

**Tekken stays the input base** (4-button limbs, f+2 notation, hold-back block for duels).

## Directory Layout (this teardown)

```
teardown/soulcalibur-6/
├── TEARDOWN.md          # this file
├── docs/
│   └── SCVI-MECHANICS.md  # full combat mechanics federation reference
├── models/              # (pending game acquisition)
├── stages/              # (pending game acquisition)
├── animations/          # (pending game acquisition)
├── audio/               # (pending game acquisition)
└── ui/                  # (pending game acquisition)
```

## Open Items

- [ ] Acquire SCVI (owner Steam purchase → SteamCMD, or disk space for Workshop bulk)
- [ ] Extract .pak contents via FModel
- [ ] Character models → western-heart/teardown/soulcalibur-6/models/
- [ ] Stage .umap files → stages/
- [ ] UI/menus → ui/
- [ ] Cross-reference with soulcalibur-hunt model catalog

---
*Teardown scaffold: 2026-10-13. Mechanics documented from community sources.
Game binary pending acquisition.*
