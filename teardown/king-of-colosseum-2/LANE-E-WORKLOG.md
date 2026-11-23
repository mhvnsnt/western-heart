# LANE E — King of Colosseum 2 — WORKLOG

Owner: Mars (mhvnsnt). Lane owner-agent: Muse subagent, 2026-11-19.
Branch (Bannon): `muse/owner-koc2` (off main, head 8075e7d). Branch (western-heart): `muse/koc2`.
Workdir: `~/workspace/grok-declined-items/lane-koc2/`.

## 2026-11-19

- 09:31 EST — Lane start. Read Bannon AGENTS.md (anti-clobber laws,
  NO-SPARSE-COMMIT, evidence-label law, present-references rule),
  HANDOFF_OWNER_REQUESTED_SOURCE_INTEGRATION.md,
  ~/workspace/wrestling-full-pull/other-games/INVENTORY.md,
  western-heart TERABOX-MANIFEST.md + AGENTS.md, northstar deep dives
  (ULTRAVIOLENCE, NECKBREAKER).
- Checked for prior KoC2 work: NONE in western-heart teardown dirs, Bannon
  docs, or wrestling-full-pull (grep over *.md/*.txt: zero hits; the only
  "colosseum" hits are the word inside legacy BANNON_v150.html builds).
  TeraBox manifest has no KoC2 entry (Def Jam + SFV are PLANNED-only).
- Sourcing: archive.org item `ps2-isos-and-translations` holds
  `King of Colosseum II (Japan).7z`, 1,738,818,479 bytes,
  md5 319396fd807341fa4b6586f2f67f1eeb,
  sha1 6706da7f2b0395777f6682576ee65a96781502c1
  (metadata fetched via archive.org/metadata API — FETCH-VERIFIED).
  Download started 09:31 EST via curl (resumable), ~1.25 MB/s, ~23 min ETA.
- Research (all SEARCH-VERIFIED unless noted): Jerrold Ng's FAQ/Movelist
  v1.0 (GameFAQs/Neoseeker, 10 Oct 2004) read in full for systems sections
  A–L + movelist format + samples; GameSpot import review; Cagematch list
  (KoC2 #4 by rating, 9.64, 24 votes, 09.09.2004, PS2 — brief's claim
  confirmed); ResHax thread "King of Colosseum 2 TIM2 Compression"
  (topic 18443, skstylez/Rabatini, Oct 2025–May 2026): archive is
  KC2FIRE.001, files are LZSS-compressed .comp, decompress to .mdl models
  and TIM2 textures; decompression works, byte-exact compression is the
  open problem (textures solved Oct 2025, models still open May 2026).
  Brienj (XHP Creations) made a KOC2 TIM2 tool in 2013.
- Modding community found: sites.google.com/view/kingofcolosseum2 (English
  menu-texture mod, PCSX2 texture replacement, Discord run by Pejiseven,
  Google Drive texture packs + save files, Ligerbusa music-mod tutorial).
  Game ID SLPM-65602. Drive/Discord access is human-gated (DM Pejiseven) —
  BROWSER-QUEUE.md.
- Showcase refs already on disk: ~/workspace/showcase/vpw2-koc2/
  koc2-nakamura-tanahashi.jpg, koc2-nagata-corino.jpg.
- Installed p7zip-full (7zip 23.01) via apt for the .7z extraction.
  Gitleaks v8.21.2 already present at ~/workspace/bin/gitleaks.
- Drafted + staged (not yet pushed): Bannon `docs/koc2/` (README,
  grappling spec, crowd spec) + `assets/moves/koc2-moveset-slots.json`
  (271 slots, 34 categories — count verified by script) +
  `assets/moves/koc2-systems.json` (26 styles, 40 counter styles, 20 COM
  Logic tables, 19 titles — counts verified). Data home follows the
  full-pull lane's convention (`assets/moves/<game>-*.json`, verified on
  Bannon main via GitHub API: `assets/moves/` exists, no top-level
  `data/`). Western-heart staging: `teardown/king-of-colosseum-2/`
  (TEARDOWN.md skeleton, research/KOC2-RESEARCH.md, tools/tim2_decode.py,
  tools/kc2fire_inspect.py).
- Verified via GitHub API (call-read-tool): Bannon main head is
  8075e7d225e3d31712016cfcf7cf32d0280238b4 (matches brief).
- Download at 812 MB / 1,659 MB (~49%) as of ~09:50 EST, ~1.2 MB/s,
  ~12 min left.
- Download complete ~10:00 EST: 7z hash-verified (md5 + sha1 match
  archive.org metadata exactly; sha256
  54b2ee70df965de71ef33a9445dbe906630c4d5a5d0893b303325745e65ce372).
  7z contained CDRomance.url (provenance: packed from a CDRomance
  download) + the ISO (4,593,778,688 B; sha256
  7daa1f8c950272f24e9888d26338645fdbac1974da8dbf43b30c0042ceed0511).
  ISO layout: SLPM_656.02 ELF (3,048,408 B), MODULES.BIN (15 files),
  IOPRP300.IMG, DATA/KC2FIRE.DIR manifest, KC2FIRE.AFS (1.87 GB, 9,003
  files), KC2FIRE.MVS (16,660 files, raw), KC2FIRE.000 (7,519 files),
  KC2FIRE.001 (16,017 files), HELLO.FOR / GOOD.BYE / LAST.DAY (all
  entirely zeros — disc padding, verified by full scan).
- Spike container format reverse-engineered + validated: 8-byte header
  (0x800, count), count x 16-byte entries (offset/stored/decomp/flags;
  bit 16 = LZSS), zero padding to the next 2048-byte boundary, then
  packed file data (offsets relative to the padded data start;
  data_start + sum(stored) == file size exactly on all four archives).
  tools/kc2_extract.py written + index CSVs generated for all four.
- **LZSS CRACKED 2026-11-19** (tools/koc2_lzss.py): flag byte LSB-first,
  bit 1 = literal, bit 0 = match (b1, b2): offset =
  (b1 | ((b2 & 0x0F) << 8)) - 1 (absolute, 1-based, 4096 ring buffer,
  zero-filled, write pos starts at 0), length = (b2 >> 4) + 2 (2..17).
  Solved from known plaintext: compressed TIM2 files 15972/15973 decode
  to exactly their catalogued sizes and reproduce the known TIM2 header
  byte-for-byte; 15975 also decodes to a valid TIM2. Stored streams are
  zero-padded to 2048-byte boundaries; decoder stops at decomp_size.
  (Two bugs found + fixed in the fast path: pos wrap at 4096, and a
  stored offset of 0 meaning ring position 4095, not -1.)
- TIM2 findings: KoC2 TIM2s put the picture header at 0x80 (not 0x10)
  with header_size 0x80; pict_format byte reads 0x01 on plainly 8-bit
  indexed files — tim2_decode.py now scans for the header and derives
  the mode from image_size/(w*h). Raw TIM2 files 15974/16008 are
  128x128 8-bit indexed (256-color 32-bit CLUT). The image data is
  stored 4-way byte-interleaved (4 streams = 4 quadrants of the
  128x128 image); the CLUT is in file order but the palette is dark
  and colors render speckled — texture decode is PARTIALLY solved
  (layout + header cracked, color mapping still open; file 15974 may
  be a tiled/noisy texture by design — needs more samples).
- AFS format confirmed + tools/kc2_afs.py written (mmap-based): standard
  AFS, name table at EOF (48-byte records, 32-byte names). KC2FIRE.AFS
  = 9,003 files, ALL named: 9,000 .adx audio + 3 .sfd videos
  (movtop.sfd, KC2Opening.sfd, KachinukiOP.sfd). Total 1.86 GB.
- Full extraction LAUNCHED (background): .001 + .000 + .MVS + MODULES
  via kc2_extract.py (decompressing inline, ~1.7 MB/s, ~8 min ETA);
  AFS via kc2_afs.py (copy-only). Logs in extract/extract-*.log.
- Full extraction COMPLETE: all 5 archives, 49,214 files (verified by
  counts: .001 16,017/16,017, .000 7,519/7,519, .MVS 16,660/16,660,
  AFS 9,003/9,003, MODULES 15/15). First container pass had 1,492
  files short by 2–76 bytes (the truncated (0,0)-match LZSS quirk);
  retry with the zero-extension fix recovered all 1,492.
- **AFS dedup bug found + fixed**: the first kc2_afs.py dedup kept
  only 2 copies of any repeated name — KoC2's name table genuinely
  repeats names (on0232.adx x158, oc0234.adx x156, all distinct
  offsets/sizes), so 321 files were lost. Fixed the counter to live
  on the original name, added a disk_name column to index.csv,
  re-extracted the AFS clean (9,003 files on disk, verified).
- Data tables parsed (all from KC2FIRE.000): file 02010 master string
  table (25 categories, 4,021 strings; roster 429 entries / 363
  distinct wrestlers) -> data/koc2-strings.json; file 01454 music
  table (483 slots, 240 titles) -> data/koc2-music.json; file 02030
  commentary script (8,983 lines + 20 ADX refs) ->
  data/koc2-commentary.json; file 02031 AFS file-ID header (9,003
  #defines; order verified identical to the AFS index) ->
  data/afs-ids.json; files 02893–02900 threshold tables (44 blocks) ->
  data/threshold-tables.json; files 02401–02402 grade grids (16 x 5x5)
  -> data/grade-grids.json; 273 ACW camera scripts + 11 text tables
  -> data/acw/ (284 files). Parsers: tools/koc2_strings.py,
  tools/koc2_text.py, tools/koc2_tables.py.
- Threshold/grade parsers fixed: blocks/grids are NOT separated by
  blank lines — threshold blocks split on the score resetting to 90
  (8 rows each), grade grids split every 5 rows.
- Formats mapped: IECS sound banks (Vers/Head/Vagi/Smpl chunks, ~759+
  in .000); .mdl section structure (18 sections in file 0, types
  0/1/2/4, VIF/GIF DMA payload — geometry layout still open);
  MVS motion files (16,660, packed, layout open); ELF internal names
  (WrestlerData, MoveBase, MotionBase, BasicMotion, ExtraMotion,
  lpMatchmaker*, lpSurvival*).
- TEARDOWN.md filled in completely (provenance, ISO layout, Spike
  container format, LZSS format + crack story, format table, pull
  inventory, open items). Bannon staging updated: README (extraction
  complete), grappling spec §9 + crowd spec §7 checklists filled with
  real values, assets/moves/koc2-roster.json (363 wrestlers) +
  assets/moves/koc2-text-data.json (real counts).
- sha256 manifests generated for all extracted files
  (extract/MANIFEST-*.txt; combined FILES-SHA256.txt staged in
  western-heart). AFS manifest regenerated after the dedup fix.
- Gitleaks clean on both staging dirs (v8.21.2, no leaks).
- PUSHED + VERIFIED LIVE (GitHub API, get_file_contents):
  - western-heart `muse/koc2` (3 commits): 3d5fa7fd (TEARDOWN,
    research, tools, parsed data, ACW scripts — 300 files),
    bc2230be (indexes, 5 files), 2dc2f314 (FILES-SHA256.txt).
    NOTE: the first attempt (all 306 files, 9.7 MB) failed HTTP 413
    (request body too large); the 6.7 MB manifest+indexes push also
    413'd. Split into 2.1 MB / 2.3 MB / 4.4 MB pushes, all passed.
    A `__pycache__` dir also had to be removed from staging first
    (push-files is text-only; .pyc is not UTF-8).
  - Bannon `muse/owner-koc2` (1 commit): 38635405 (docs/koc2/ +
    assets/moves/koc2-*.json — 7 files).
  - No merges, no PRs (coordinator integrates). No deletions anywhere.

## Status

- [x] Research systems (clutch, powerball, audience ranking, moveset slots,
      COM Logic AI, CAW/Edit, modes, match rules, shoot mounts)
- [x] Source ISO (archive.org, hash-verified) + extract 7z -> ISO
- [x] Spike container format reverse-engineered; LZSS variant cracked
      (koc2_lzss.py, verified on all 20,182 compressed files); AFS format
      confirmed (kc2_afs.py, 9,003 named files; dedup bug fixed)
- [x] Full extraction complete (all 5 archives, 49,214 files, manifests)
- [x] Classify extracted files; parse data tables (strings, music,
      commentary, AFS IDs, thresholds, grades, ACW scripts)
- [x] TEARDOWN.md filled in; Bannon specs + data updated with real values
- [x] Push extracted data + tools to western-heart muse/koc2 (3 commits,
      verified live)
- [x] Wire specs + data to Bannon muse/owner-koc2 (1 commit, verified live)

## Lane complete 2026-11-19 — see final report to the parent.
