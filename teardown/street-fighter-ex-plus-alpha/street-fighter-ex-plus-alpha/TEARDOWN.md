# TEARDOWN — Street Fighter EX Plus Alpha (PS1)

**Game:** Street Fighter EX Plus Alpha | **Dev:** Arika / Capcom (1997) | **Platform:** PlayStation (PS1)
**Disc ID:** SLUS_005.48 | **Volume label:** `SFEXPLUSALPHA`
**Source:** Archive.org `street-fighter-ex-plus-alpha.-7z` → `Street Fighter EX Plus Alpha.bin`
**Image:** 528,049,872 bytes, raw 2352-byte Mode-2 sectors (verified complete, byte-exact vs archive.org metadata)
**Teardown date:** 2026-10-14 | **Lane:** wh-sf-100 | **Status:** 100% pulled, filesystem extracted, move data documented

> Owner SF directive: SF-based characters keep SF movesets BUT play like Tekken.
> SF is research-only for things that don't replace Tekken play style.
> This teardown targets **moveset data** (commands, move names, per-character move tables).

---

## 1. Disc layout

| Path | Contents | Size |
|---|---|---|
| `SLUS_005.48` | Main executable (MIPS). Contains character name table + 165 move names | 768 KB |
| `SYSTEM.CNF` | Boot config | — |
| `PL/P00.PAC` … `P19.PAC` | Per-character model packs (26 slots, hex 00–19). Each = 44-entry offset table: TMD model chunks + TIM textures + animation data | ~300 KB each, 7.7 MB total |
| `OVL/PL00_1.OVL` … `PL19_1.OVL` | Per-character **move-data overlay set 1** | 18–45 KB each |
| `OVL2/PL00_2.OVL` … `PL19_2.OVL` | Per-character **move-data overlay set 2** | same sizes as set 1 |
| `OVL3/` | Game overlays: `BONUS.OVL`, `END.OVL`, `MC_I.OVL`, `MC_M.OVL`, `MOV.OVL`, `OPTS.OVL`, `QUES.PAC` | 252 KB |
| `STG/S00T.PAC` … `S07T.PAC` | Stage packs set 1 (8 stages) | 2.5 MB |
| `STG2/S00D.PAC` … `S07D.PAC` | Stage packs set 2 (8 stages) | 1.7 MB |
| `TMD/` | Loose stage/effect models: `GAMEN.LMD`, `HAPA.LMD`, `VEGADAMA.LMD`, `FDEMO.PAC` | 104 KB |
| `TIM/` | UI textures (titles, logos, fonts) | 1.3 MB |
| `TEX/` | `EFFT.PAC`, `OPTION.PAC` (effect/option textures) | 272 KB |
| `SEL2/` | Character-select screen textures | 1.2 MB |
| `SND/` | `GLOBAL.PAC`, `GOVER.PAC`, `DEMO.PAC`, `P00S.PAC`… (voice/SFX packs per char) | 3.1 MB |
| `TES/` | Test/debug textures | — |
| `MUS/MUS0.XA` … `MUS3.XA` | CD-XA music (4 tracks) | 227 MB — **deferred (disk)** |
| `MOV/` | FMV `.STR` files (per-character endings + intro) | ~90 MB — **deferred (disk)** |
| `SANPUN.NUL` | Padding | — |

Full listing: `iso-file-listing.txt` (247 entries).

## 2. Character system — 26 slots

Each fighter = `PL/Pxx.PAC` (models/textures/anims) + `OVL/PLxx_1.OVL` + `OVL2/PLxx_2.OVL` (move data).
Slot IDs are hex `00`–`19` (26 slots).

### 2a. Character name table (from `SLUS_005.48`, offset ~705572, in order)

`SAKURA, DHALSIM, BETA, GAMMA, AKUMA, GOUKI, ZANGIEF, CHUN-LI, KEN, RYU, GARUDA, M.BISON, VEGA, GUILE, C.JACK, ALLEN, SKULLO, BLAIR, PULLUM, D.DARK, DARUN, HOKUTO, KAIRI`

Notes:
- `BETA`/`GAMMA` = Cycloid-β / Cycloid-γ (hidden copy-characters; confirmed by `Beta Shinku-Tatsumaki`, `Gamma Skullo Crasher`… move names in the same binary).
- `GOUKI` = Akuma's Japanese name (second Akuma entry — boss/alt variant).
- `SAKURA` appears in the name table and as `SAKURA MANKAI` (offset 703116). Identity unconfirmed — documented verbatim; P-slot mapping pending select-screen data cross-check.
- Sagat/Balrog name strings not found in the executable's ASCII tables (may be referenced by ID only); roster cross-check pending.

### 2b. Complete move-name list (165 names, `SLUS_005.48`)

Saved verbatim in `move-names.txt`. Highlights per fighter:
- **Ryu/Ken/Akuma:** Hado-Ken, Shoryu-Ken, Tatsumaki-Sempu-Kyaku, Shinku-Hado-Ken, Shinku-Tatsumaki, Shoryu-Reppa, Shinryu-Ken; Akuma: Shungoku-Satsu, Messatsu-Gou-Hado, Messatsu-Gou-Shoryu, Tenma-Gou-Zankuu, Zankuu-Hado-Ken, Asyura-Senku
- **Garuda:** Kyouja-Renbu, Shinki-Hatsudo, Mouryo-Kasen, Maryu-Rekko, Jinki-Hatsudo, Kiensyo, Kienbu, Gouga, Raiga, Shuga, Jazan, Kizan
- **Doctrine Dark:** Dark Shackle, Dark Hold, Dark Spark, Dark Wire, Death Trump, Explosive
- **Darun Mister (wrestler):** Super Darun Bomb, Indra Bridge, Power Indra Bridge, Brahma Bomb, Darun Catch, Ganjis DDT, Dusk Lariat, Final Atomic Buster (Lv3)
- **Skullomania:** Skullo Crasher, Super Skullo Crasher, Skullo Dream, Skullo Slider, Super Skullo Slider, Skullo Dive, Skullo Head, Skullo Face Slam, Skullo Dash, Skullo Back Flip
- **Cracker Jack (baseball boxer):** Homerun Hero, Batting Hero, Crazy Jack, Soccer Ball Kick, Final Punch, Dash Straight, Dash Upper
- **Allen Snider:** Justice Fist, Rising Dragon, Soul Force, Triple Break, Fire Force
- **Blair:** Killing Blade, Lightning Knee, Shoot Upper, Spin Side Shoot, Sliding Arrow, Mirage Combo Kick
- **Pullum:** Drill Purrus, Dance Wind, Femina Wind, Purim Kick, Ten'el Kick, Praec Larum, Res Arcana
- **Guile:** Sonic Boom, Flash Kick, Double Flash Kick, Opening Gambit
- **M.Bison:** Psycho Crusher, Scissors Kick, Head Stomp, Skull Diver, Psycho Cannon, Knee Press Nightmare, Spinning Back Knuckle
- **Chun-Li:** Lightning-Kick, Spinning Air Kick, Hienshu, Kiko-Sho, Senretsu-Kyaku, Ryusei-Raku
- **Zangief:** Spinning Pile Driver, Double Lariat, Quick Double Lariat, Russian Suplex, Flying Body Attack
- **Hokuto/Kairi:** Syougekiha, Shinku-Geki, Shinkyaku-Geki, Kiren-Eki, Kyakuhougi, Ryobu, Ryusui, Gokyakuko

### 2c. Move-data overlay format (`OVL/PLxx_1.OVL`)

- MIPS overlay; opens with a pointer table of 32-bit PS1 RAM addresses (`0x8004xxxx`).
- Per-character move tables: command → animation/frame-data/damage references.
- Full binary decode of the table format is open work; raw overlays for all 26 slots are committed under `data/OVL/` and `data/OVL2/`.

### 2d. Model-pack format (`PL/Pxx.PAC`)

- 44-entry little-endian offset table, then 44 chunks (TMD model parts, TIM textures, animation data).
- Per-character packs committed as GitHub release `sf-ex-plus-alpha-data-v1` (PL + STG tarballs) — see TeraBox staging.

## 3. Stages

8 stages × 2 packs: `STG/S00T–S07T.PAC` + `STG2/S00D–S07D.PAC`. Loose models in `TMD/` (`GAMEN.LMD`, `HAPA.LMD`, `VEGADAMA.LMD`). Stage-name mapping pending texture cross-check.

## 4. What goes to Western Heart (per SF directive)

- ✅ Move names + command research → `moveset-library/` reference (SF movesets, Tekken-style inputs — research only)
- ✅ Per-character move-data overlays → raw data for frame-data research
- ✅ Character model packs → likeness/geometry reference
- ❌ Do NOT port SF engine systems, input parser, or combo system — Tekken play style stays

## 5. Storage

- **Game archive (TeraBox):** `Street Fighter EX Plus Alpha.7z` — 263,912,228 bytes (browser task staged in `terabox-staging/BROWSER-TASKS.md`)
- **Extracted .bin (local):** `game-reverse-engineering/street-fighter-3d-games/extracted/ex-plus-alpha/Street Fighter EX Plus Alpha.bin` — 528,049,872 bytes (NEVER auto-delete per game-file law)
- **Repo:** this dir + GitHub release `sf-ex-plus-alpha-data-v1` (model/stage packs)

## 6. Open work

1. Decode `OVL` move-table binary format → per-move frame data / damage / command inputs.
2. Map P-slot hex IDs → character names (select-screen `SEL2` cross-check).
3. Confirm `SAKURA` entry identity.
4. Extract XA music + FMV when disk allows (deferred, not blocking).
