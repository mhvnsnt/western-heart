# TEKKEN TAG TOURNAMENT 2 — Teardown for Western Heart

**Role in Chimera Build:** 59-fighter roster source + tag-team systems. TTT2 is the biggest Tekken roster ever shipped — every fighter is a potential Western Heart reskin base or alt-costume donor.
**Developer:** Namco Bandai (2011 arcade / 2012 console; console built on an upgraded Tekken 6 engine, Namco System 369 in arcade)
**Platform:** Xbox 360 (this dump: EU region, Title ID `4E4D0859`)
**Last updated:** 2026-10-13 (inventory + manifest sweep)

---

## Complete File Inventory (DONE 2026-10-13)

**Archive:** `Tekken Tag Tournament 2.7z` — **13,363,624,393 bytes** (byte-exact vs Archive.org item `tekken-tag-tournament-2_202609`)
**Uncompressed:** 13,452,865,536 bytes (12.53 GiB) — **80 entries: 72 files + 8 dirs** (was: header-only listing of 80 entries)
**Method:** py7zr header read (no decompression); per-file CRC32 captured.
**Full inventory:** [`INVENTORY.md`](INVENTORY.md) — every file, size, CRC32, mtime.

### Disc structure
| Directory | Files | Contents |
|-----------|-------|----------|
| `0000000000000000/4E4D0859/00000002/` | 7 | Title data: 7 blobs — 51MB / 79MB / 80MB / 155MB / 358MB / 1.94GB / 2.03GB (build mtimes 2012-10/11) |
| `0000000000000000/4E4D0859/00009000/` | 12 | Title-update/system files, 98KB–340KB each (~3.1MB total) |
| `4E4D0859/00007000/392CFF5C9DB17CCAEBC3.data/` | 53 | **Data0000–Data0051: 52 × 170,459,136-byte chunks** (~8.86GB, the bulk game content) + 45KB STFS container descriptor |

### Where the game data lives
Character data, stage data, movesets, audio, and textures are all inside the 52 Data chunks + the 7 large `00000002/` blobs — Xbox 360 STFS containers holding Namco's proprietary in-house-engine formats (NOT UE4). **No plaintext manifest exists at package level:** all names/offsets are inside the containers. Character models expect the Tekken 6 console model family (distinct from PSP GMO); audio is XMA banks; movesets are per-character move-list binaries.

### Roster manifest (documented from public game data — NOT in the archive)
**59 playable fighters** on console (60 counting Wii U-exclusive Dr. Bosconovitch): all 41 Tekken 6 fighters + returning favorites (Jun, Michelle, Kunimitsu, Ogre, True Ogre, Angel, Jinpachi, Forest Law, Prototype Jack, Alex, Tiger Jackson, Violet) + newcomers Jaycee, Sebastian, Slim Bob. Devil is Kazuya's transformation stance, not a separate slot. Combot (Fight Lab) is playable in VS. DLC: Kunimitsu/Michelle/Angel/Ogre (pre-order), Alex/P.Jack/Tiger/Forest (console), Miharu/Unknown/Sebastian/Slim Bob (update 1.02, 2012-10-09).
**Full list:** [`ROSTER.md`](ROSTER.md)

### Stage manifest (documented from public game data — NOT in the archive)
**29 battle stages** incl. 10 multi-tiered (Condor Canyon, Dusk After The Rain, Fireworks Over Barcelona, Hall Of Judgement, Moai Excavation, Riverside Promenade, Strategic Space, Tempest, Tropical Rainforest, Winter Palace) + Violet Systems Lab (Fight Lab) + system stages. Internal stage IDs (stg00–stg48) documented in [`STAGES.md`](STAGES.md) for the future extractor.

### Selective extraction (IN PROGRESS 2026-10-13)
The 13 sub-10MB files (12 title-update files + the 45KB STFS descriptor, ~3.1MB total) are being selectively extracted for identification. Character-select portraits, stage thumbnails, and all other game content sit inside the Data chunks and cannot be reached without STFS decryption. Results will be documented here when the extraction lands.

---

## What's Blocked and Why

- **Full extraction BLOCKED by disk space.** Archive (13.3GB) + extracted (13.45GB) = ~27GB needed simultaneously; /home/hatch sits at 90% (11GB free) with an 88% hard ceiling. **Not attempted.**
- **Safe storage: IN PROGRESS (separate lane).** The 13.3GB archive is being uploaded to a western-heart GitHub Release in 500MB chunks (26 chunks; 5/26 verified as of 2026-10-13 ~09:00 EDT). Until the full archive is verified in the Release, **per NO-DELETE-BEFORE-SAFE-STORAGE LAW the local 7z stays.**
- **Xbox 360 package decryption:** the Data0000–Data0051 blobs and the 7 large `00000002/` files are Xbox 360 STFS/container format. Extraction needs Xbox 360 tooling (Velocity/Xbox 360 Content Manager equivalent, or Linux STFS parsers). The tekken-decrypt tool hunt (`~/workspace/tools/tekken-decrypt/`) pulled FModel + repak for Tekken 7 (UE4) — TTT2 is NOT UE4, so a different extractor is needed.
- **Character models inside the blobs:** once extracted, expect Namco proprietary console model format (same family as Tekken 6's, distinct from PSP GMO).

---

## Chimera Build Value

- **59 fighters = the deepest reskin pool** of any chimera source game. Every body type from Kuma/Panda to Slim Bob to Alisa.
- **Tag-team systems:** 2v2 tag mechanics, tag assaults, tag throws — the template if Western Heart ever adds tag mode.
- **~120+ attires:** the largest alt-costume library; P2/customization variants for every base.
- **Fight Lab / Combot:** TTT2's Combot (customizable robot fighter) is a direct reference for a chimera create-a-fighter system.
- **29 stages** incl. multi-tiered arenas — the largest stage pool; breakable-floor arenas are the template for Western Heart stages.

---

## Next Steps

1. Finish GitHub Release upload of the 13.3GB archive (separate lane in progress); verify all 26 chunks, then decide on local 7z retention
2. Wire Xbox 360 STFS decryption tooling (Linux) — the blocker for ALL inner content
3. Extract Data chunks → map internal file structure → pull character models, movesets, stage geometry, audio banks
4. Document the Namco X360 model format alongside the Tekken 6 findings
