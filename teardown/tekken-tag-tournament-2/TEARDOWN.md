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

### Selective extraction (DONE 2026-10-13)
All 13 sub-10MB files extracted with 7-Zip (selective `7z e`, ~3MB total — disk-safe):
- **12 files in `00009000/`** (98KB–340KB): identified via `file` as **Xbox 360 LIVE packages, content type "Avatar Item"** — Xbox Live avatar-item DLC bundles (each embeds PNG thumbnail data: IHDR/IDAT chunks visible). 1996-epoch mtimes. These are dashboard avatar cosmetics, **not game metadata**.
- **`392CFF5C9DB17CCAEBC3`** (45,056 bytes): Xbox 360 LIVE package (media ID 5D762D06) — the STFS container descriptor for the main Data0000–Data0051 content package.
- **Result: no plaintext game metadata, no character portraits, no roster/stage manifests, no configs at the package level.** All game content (fighters, stages, movesets, audio, textures) is inside the STFS Data chunks and requires Xbox 360 decryption tooling. Extracted copies kept at [`extracted-small/`](extracted-small/) (2.9MB).

---

## 2026-10-23 — Surgical extraction pipeline (Law/Lars priority lane)

**Directive:** T3 is fallback-only — all pulls from T5/T6/T7/TTT2. Law and
Lars extract FIRST (their modern movesets/animations unblock the Buffalo
Bill / Chordz pull lane); then the full 59-fighter roster, stages, audio.

**Built:** `tools/surgical/` — stream-extracts 7z members from release
`ttt2-7z-v1` over HTTP Range **without** downloading the 13.36GB archive
(VM egress is proxy-throttled to ~0.1 MB/s sustained; full pull ≈ 38h).
The 7z is one LZMA folder (lc=3,lp=0,pb=2,8MB dict), 72 data files in
header order: 7 STFS blobs (0–6) → 12 title-update files (7–18) → GoD
descriptor (19) → Data0000–Data0051 (20–71).

**Verified 2026-10-23:**
- 7z end-header parsed over HTTP Range (1,970 bytes fetched): 80 entries,
  byte-matching INVENTORY.md.
- Member 19 (GoD descriptor, 45,056 bytes) stream-extracted and
  **byte-identical** to the `extracted-small/` copy (sha256 match).
- `GodPackage` (title ID `0x4E4D0859` parses) + `StfsPackage` readers
  sourced from `dfdx047/ZarManager` (`fetch_zarmanager.py`; not vendored —
  upstream license unverified).
- Member 0 (155MB STFS blob) stream-decoding in progress.

**Runbook:** [`EXTRACTION-RUNBOOK.md`](EXTRACTION-RUNBOOK.md) — step-by-step
through the XDVDFS listing (`Data0000`, header index 20, ~4.9GB stream
prefix = the long pole, run under `nohup`) to Law/Lars carving.

---

## What's Blocked and Why

- **Safe storage: DONE 2026-10-23.** Release `ttt2-7z-v1` holds all 27
  assets (26 × 500MB parts + loose-files tar, 13.5GB). The local 7z is
  fully reproducible from the release; per-part deletion after extraction
  is sanctioned.
- **Disk: circumvented.** The surgical pipeline (`tools/surgical/`) never
  holds the full archive + extracted payload simultaneously — members
  stream-decode straight from the release parts over HTTP Range.
- **Network (new, 2026-10-23):** VM egress proxy throttles sustained
  downloads to ~0.1 MB/s. Full 13.36GB pull ≈ 38h; `Data0000` (key to the
  XDVDFS listing) needs a ~4.9GB stream prefix ≈ 14h — run as a background
  `nohup` job. Per-member prefix costs: `tools/surgical/README.md`.
- **Xbox 360 tooling: WIRED 2026-10-23.** `GodPackage`/`StfsPackage`
  (dfdx047/ZarManager) + `tools/xdvdfs_reader.py` + `tools/god_surgical.py`
  cover GoD/STFS/XDVDFS. Remaining: Namco X360 model/moveset format docs
  (same family as Tekken 6 console).
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

1. ~~Finish GitHub Release upload~~ — DONE 2026-10-23 (`ttt2-7z-v1`, 27 assets)
2. ~~Wire Xbox 360 STFS decryption tooling~~ — DONE 2026-10-23 (surgical pipeline)
3. Extract `Data0000` (background `nohup`, ~14h at throttled egress) → XDVDFS listing
4. **Law + Lars first:** carve their character bundles (models, move-list binaries, animations, stances, win poses) → new GitHub Release for binaries >50MB + manifests in `roster/`
5. Continue: full 59-fighter roster → stages (stg00–stg48) → XMA audio banks
6. Document the Namco X360 model format alongside the Tekken 6 findings
