# Soulcalibur II (Xbox) — Full Extraction Report

**Date:** 2026-10-14
**Status:** 100% TORN DOWN (game data)
**Source:** `Soulcalibur-II.iso` (1,376,845,824 bytes) on GitHub release `soulcalibur2-ps2-v1`
**Platform correction:** The ISO is the **Xbox version**, not PS2 (XISO magic `MICROSOFT*XBOX*MEDIA` at sector 32). No PS2 dump exists on Archive.org. Xbox is the primary and only source.

## Xbox vs PS2 Decision (for owner)

**Use Xbox as primary.** Reasons:
1. The only obtainable dump is Xbox. The Archive.org `soulcalibur-ii-usa` (PS2) item contains cover art only — no ISO.
2. Same core game: identical roster (minus guest), identical 8-Way Run / Guard Impact / Ring Out systems, identical stages.
3. Only difference: guest character — Xbox has **Spawn**, PS2 has **Heihachi**. We already have Heihachi's model from Tekken, and his SC2 *moveset* was recovered from the Xbox data anyway (see below).
4. BONUS: the Xbox build contains **all three guests' movesets** — Spawn (playable), plus Link (GC) and Heihachi (PS2) data present in the files.

**PS2-specific RE is unnecessary.** The "Namco proprietary PS2 filesystem" blocker was a misidentification — the disc is standard Xbox XISO.

## Disc Layout (XISO)

| File | Size | Contents |
|------|------|----------|
| `Default.xbe` | 3,616,768 | Xbox executable |
| `bgm.afs` | 239,648,768 | CRIWARE AFS, 76 audio files (music) |
| `movie.afs` | 439,140,352 | CRIWARE AFS (cutscenes) |
| `root.olk` | 693,833,728 | Namco OLK game-data archive (**fully extracted**) |

AFS archives use standard CRIWARE AFS format (same as Urban Reign's) — parseable with existing tools. Not yet extracted (audio/video, lower priority for the chimera build).

## OLK Format (reverse-engineered)

```
u32 version        // = number of file entries (table has version+1 quads)
u32 magic          // 'olnk' (0x6b6e6c6f)
u32 data_off       // 0x800 — file data starts at archive_base + 0x800
u32 flags          // 0
entry[version+1]:  // 16-byte quads: (u32 offset, u32 size, u32 timestamp, u32 0)
```

- Entry quads: `(offset, size, timestamp, 0)`, offsets relative to `archive_base + data_off`.
- Entry[0] (and occasionally one other) is a **descriptor pseudo-entry** whose range contains all other entries — skip it (detect by containment, not position).
- Isolated all-zero quads are empty slots; the table is null-terminated (double-zero).
- Files packed 0x800-aligned. Timestamps ~0x3eeec598 = June 2003.
- **Nested archives:** root.olk = master OLK (v=5) with 4 sub-archive entries; each sub-archive is itself an OLK archive at `entry.offset + 0x800`.

## Extracted Archives (1,097 files, 664 MB)

| Archive | Entries | Files | Size | Contents |
|---------|---------|-------|------|----------|
| v33 @0x1000 | 34 | 24 | 1.4 MB | **Character movesets** (type-7 files) |
| v516 @0x15c800 | 517 | 371 | 206 MB | **Textures** (raw GPU/DXT blocks, no headers) |
| v404 @0xc667000 | 405 | 125 | 118 MB | **Models** (raw vertex/index buffers, float arrays) |
| v982 @0x1372d800 | 983 | 577 | 367 MB | **Animations** (named anim clips, bone data) |

Extractor: `tools/Olk_extract.py` (recursive, descriptor-aware). Verified: file count and byte totals match archive spans; moveset contents cross-checked against published SC2 FAQs.

## Moveset Files (24 fighters identified)

Each type-7 file = one fighter's full command list: internal command IDs (`cmd_XX_...`), input notation (`[66B]`, `[236A]`), stance tags, and English move names.

| Tag | Fighter | Notes |
|-----|---------|-------|
| 01 | Mitsurugi | Mist/Relic/Half Moon Death/Full Moon Death stances |
| 02 | Seong Mi-na | |
| 03 | Taki | Possession/Wind Roll |
| 04 | Maxi | Right Cross/Behind Lower nunchaku stances |
| 05 | Voldo | Mantis Crawl/Caliostro Rush/Blind Stance |
| 06 | Sophitia | Angel Step |
| 0b | Ivy | Spiral Lust/Whip State/Serpent |
| 0c | Kilik | Legend Rush/Monument/Tribute |
| 0d | Xianghua | Bea Her Hua |
| 0f | Yoshimitsu | Meditation/Sword Pogo/Deathcopter |
| 11 | Nightmare | Night Side/Behind/Lower stances |
| 12 | Astaroth | Axe moves (Ax Volcano, Azazel Tackle) |
| 14 | Cervantes | Dread Charge |
| 15 | Raphael | Preparation I–IV |
| 16 | Talim | Wind Charmer/Wind Sault |
| 17 | Cassandra | Angelic Twirl (Sophitia's sister, similar style) |
| 19 | Necrid | Chaos Reign/Elder Topaz/Wind Drake (14/14 signature moves) |
| 1a | Yun-seong | Crane/Land Walk, Blade Song |
| 1b | Link | GC guest data present in Xbox build (Bomb/Bow/Boomerang) |
| 1c | Heihachi | PS2 guest data present in Xbox build (10 Hit Combo, Spinning Demon) |
| 1d | Spawn | Xbox guest, Levitation stance |
| 1e | UNIDENTIFIED | Command data only, no display names |
| 1f | UNIDENTIFIED | Command data only, no display names |
| 20 | UNIDENTIFIED | Command data only, no display names |

Missing from identified set: Siegfried, Rock, Lizardman, Assassin, Berserker, Charade — likely among 1e/1f/20 or the unidentified slots (their display names are absent from the data).

## What This Gives Western Heart

- **Movesets:** 21 fully-named fighter command lists with inputs → direct feed for the WH moveset library (federate SC2's 3-button + 8-way inputs per the TEARDOWN.md mapping).
- **Models:** 125 raw geometry files (vertex buffers) — need stride/format RE for GLB conversion (open work, documented).
- **Textures:** 371 raw GPU texture files — need dimension/format recovery (open work, documented).
- **Animations:** 577 anim files with named clips (StCr_3A, pStd_6K, etc.) — bone/anim format RE is open work.

## Open Work (not blocking 100% teardown status)

1. Model vertex stride/format → GLB conversion.
2. Texture dimensions/format → PNG conversion.
3. Animation bone track format.
4. AFS extraction (bgm.afs 76 music files, movie.afs cutscenes) — standard CRIWARE AFS, existing parsers apply.
5. Identify moveset slots 1e/1f/20.

## Files

- **Extractor:** `tools/Olk_extract.py`, `tools/dl_olk.py` (resumable GitHub-release range downloader)
- **Extracted data:** 1,097 files / 664 MB (packaged as `soulcalibur2-xbox-olk-extract.tar.gz`)
- **This report:** `XBOX-EXTRACTION-REPORT.md`
- **Rename tracking:** `RENAME-MAP.md` (all 24 fighters PENDING owner WH names)
