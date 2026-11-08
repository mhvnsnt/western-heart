# Devil Within — Story Script (from the Tekken 5 disc files)

**Source:** Internet Archive item `slus-210.59.-tekken-5` (md5 `5bce17ccabacea46d621d195c4600ebb`,
sha1 `97ca517151229bc1c6a58396ccf470f91676f047`). US Tekken 5 (SLUS-210.59).
**Status:** PARTIAL — the four movies inside TK5DATA1 are recovered, identified and transcribed
below; the Devil Within intro/ending themselves are NOT among them (see §5). They are
inside TK5DATA0, whose record payloads are still locked (codec unknown — §6).
**Canon note (read first):** this document transcribes TEKKEN 5's own story. Its hero IS
Jin Kazama there, and his name WILL appear below — that is correct for a source
transcription. In OUR game (Western Heart) there is NO Jin Kazama at all: the ONLY Jin is
the soul JIN (the Blade Soul), pickable as Phantom; the devil in our game is DIABLO, our
own character. Nothing transcribed here is our game's story.

## 1. Where the script lives (measured)

- The disc is FLAT: 10 files, no subdirectories, no .PSS files, no text/script files
  (`iso_head.bin`, 2,097,152 B — ISO 9660 volume, 1,972,644 sectors).
- TK5DATA2.BIN (244,426,640 B) — the DW decode's archive — holds motion (gym), stage map
  objects (moj_stg) and sound containers (snd_*). Its 498-name manifest holds NO text
  files. The script was never there.
- SLUS_210.59 (689,304 B) — the main executable. Strings sweep (`story-work/
  slus_strings_ascii.txt`, 1,389 strings): Sony SDK messages, MPEG-decoder library
  (libipu/libsceMpeg — FMV playback is done by the main executable), character name
  tables. NO dialogue sentences, NO story text, NO `item_force` / `RankingMode` / gauge
  strings. UTF-16LE/BE sweeps: nothing. **The in-game story text is NOT in the ELF.**
- TK5DATA3_code.bin (2,719,159 B decompressed code blob) — strings sweep
  (`story-work/tk5data3_code_strings.txt`, 10,028 strings): "STORY BATTLE", "FINAL STAGE",
  "STAGE %3d", "moviemanager" / "tcb_movie_manager_t", "RankingMode", character full
  names (Jin Kazama, Heihachi Mishima, Kazuya Mishima, Wang Jinrei, Devil Jin, Jinpachi
  Mishima), stage-name formats. NO dialogue sentences. **The story text is NOT in the
  code blob either — it lives ONLY in the FMVs themselves** (spoken, with English
  subtitles burned into the video).
- TK5DATA1.BIN (1,297,731,584 B) — PS2 LUT archive. Table in the code blob at
  TABLESTART 0x0027B5B0, 1,571 entries × 8 bytes (sector u32 × 0x800, size u32;
  0xFFFFFFFF = empty). Sector cipher: LCG keystream (`key = key*5+3` mod 2^32, 512 u32
  words = 2048 bytes, XOR per 2048-byte block; seed = entry index; cipher is its own
  inverse) — `teardown/tekken5/tools/romd_extract.py:decrypt_sector_data_fast`.
  Validated: entry 148 decrypts to `TK5RESU1`, checksum table CK1 at code offset
  0x27E838 matches (word_sum 0xedc1f397).

## 2. The four movies in TK5DATA1 (complete census)

LUT movie scan (all 1,571 entries, first 2048 bytes each, raw + decrypted, MPEG pack
`0x000001BA` / sequence `0x000001B3` / system `0x000001BB`): **exactly 4 movie entries**.
Entries 400–1570: 0 candidates (scan3, 2026-11-08). Entries 0–400: only idx 1–4.
All four are raw MPEG-2 video elementary streams (NO pack headers, NO multiplexed
audio — video only; the audio track for each movie is a separate, not-yet-found file).
640×448, 4:3, 29.97 fps, Main profile, yuv420p. Converted with ffmpeg 8.1.2
(mpegvideo → libx264 CRF 23) to `dw-cutscenes/`.

| LUT idx | sector | size (B) | duration | identity |
|---|---|---|---|---|
| 1 | 15 | 61,009,920 | 68.47 s | Tekken 5 MAIN INTRO (English) |
| 2 | 29,805 | 60,954,624 | ~68 s | Tekken 5 MAIN INTRO (duplicate) |
| 3 | 59,568 | 212,115,456 | 301.90 s | Tekken 5 ARCADE ATTRACT / promo movie (Japanese text) |
| 4 | 163,140 | 212,060,160 | 301.30 s | Tekken 5 ARCADE ATTRACT / promo movie (English text) |

- idx 1 vs 2: near-identical sizes (differ 55,296 B); idx 3 vs 4: near-identical sizes
  (differ 55,296 B) and identical first-32 decrypted bytes (`3f740eba` at offset 16).
  Each pair is the same movie in two variants (language/region).
- Decode note: the source MPEG-2 streams carry damaged sections (ffmpeg reports
  "ac-tex damaged", "Missing picture start code", "slice below image" — most in the
  202 MB streams). The videos are watchable and identifiable; some frames have
  blocky glitch patches. Whether the damage is in the disc image or the decrypt is
  UNMEASURED.
- The other large LUT entries (idx 32–64, 5–10 MB) are NOT movies: decrypted heads
  show a 32-byte per-file header starting `[var] 50 53 46` ("PSF") followed by
  high-entropy data (entropy 7.99 bits/byte) — compressed blobs (NLZ/LZ, not
  zlib/lzma/bz2 — all fail). Most plausibly music/sound data, NOT dialogue audio
  (no AC3 syncs, no [TAG] section). UNMEASURED — identification owed.

## 3. Tekken 5 main intro — full transcription (LUT idx 1, 68.47 s)

**Source:** TK5DATA1 LUT entry 1 (sector 15, 61,009,920 B), decrypted with the
sector cipher (seed 1), converted to `dw-cutscenes/lut1_intro.mp4` (H.264,
640x448, 29.97 fps). LUT entry 2 is a near-identical duplicate (60,954,624 B).
**Method:** watched all the way through at 1 frame per second (68 frames);
every on-screen text line is quoted word for word with its timestamp. The
movie is video-only (no audio stream in the entry), so there is no spoken
dialogue to transcribe — the story is told visually plus the one narrated
subtitle line below. Character identifications are from the visuals; the one
name card is quoted as shown.

### On-screen text (word for word — the whole of it)

- ~4–8 s: `namco presents`
- ~47–49 s: `Heihachi Mishima...` (white text; fades in over a close-up of a man
  in dark sunglasses, scarred face, fire reflected in his lenses)
- ~50–51 s: `...is dead.` (red text)
- ~56–68 s: the title logo `TEKKEN 5` (Japanese `鉄拳5` above it)

That is the intro's entire text. The line reads in full: **"Heihachi
Mishima... ...is dead."**

### Beat-by-beat story summary (in order)

- 0–3 s: inside a dark ruined temple — broken pillars, debris falling, the
  camera rising through a shattered ceiling.
- 4–8 s: "namco presents" over the ruined roof; the full moon shows through
  the hole in the roof.
- 9–11 s: a ship at sea in a storm, rain and heavy waves.
- 12–14 s: dust and smoke clearing in a hall; armed soldiers standing in rows.
- 15 s: a body lying in water in the rain.
- 16–19 s: close-up of an older man with white spiky hair in the rain, stern
  face (Heihachi).
- 20–23 s: fighting — a robotic figure, a shirtless scarred man, an armored
  fighter trading blows.
- 24–28 s: the white-haired man from behind (black vest with a circular emblem
  on the back) walking into a dark hall; he faces a bald man; two men fight.
- 29 s: a figure falling in a dark hall.
- 30–31 s: a swallow in flight, close-up (red throat, white belly).
- 32 s: a city skyline with a tall tower.
- 33–34 s: a young woman in a school uniform on a rooftop, city behind her
  (Asuka).
- 35 s: a burning, ruined street, debris falling.
- 36 s: a shirtless man with a scarred chest looking up (Kazuya).
- 37 s: a bald man with red glowing eyes, stern.
- 38 s: a robotic/masked face with a fan-like blade and red eyes.
- 39 s: the white-haired man (Heihachi) close-up, angry.
- 40–43 s: a massive explosion — a huge fireball, debris flying.
- 44–47 s: close-up of a man in dark sunglasses, scarred face, fire reflected
  in the lenses; the `Heihachi Mishima...` name card fades in over this shot.
- 48–51 s: the text completes — `Heihachi Mishima...` then `...is dead.`
- 52–55 s: a horned, demonic figure rising out of the burning temple.
- 56–68 s: the TEKKEN 5 logo held over the flames, then fade to black.

### What this sets up (story, not speculation)

The intro announces Heihachi Mishima's death and shows a demonic figure
rising from the burning temple — the premise Devil Within continues (Jin
going into the G Corp lab / the ruins). The swallow, the rooftop woman
(Asuka), the scarred shirtless man (Kazuya) and the red-eyed bald man are
shown but not named in this movie.

## 4. Tekken 5 arcade attract movie — story summary (LUT idx 3/4, 301.9 s)

NOT a story cutscene — a 5-minute arcade demo reel. Observed beats (15 s
contact sheet, idx 3 Japanese / idx 4 English — same shots):
"The wait is over..." → "namco presents" → TEKKEN logo in fire → character
select cards (ASUKA KAZAMA, FENG WEI, ...) → "Please Select Characters" →
gameplay footage → rank ladder (RANK 3 / RANK 2 / RANK 1) + "TEKKEN 5 - Data
Card" (arcade card system) → "Fighter Information" → "Earn different colored
outfits!" (idx 4) / "Defeat other fighters to raise your rank" → end card
"TEKKEN OFFICIAL www.tekken-official.jp" (idx 4). No Devil Within content.
No dialogue to transcribe (on-screen promo text only, listed above).

## 5. The Devil Within cutscenes — NOT FOUND YET (status + where they must be)

- The DW intro and DW ending are NOT in TK5DATA1 (complete LUT census: only the
  4 movies above). They are NOT in TK5DATA2 (motion/stages/sound only), NOT in
  SLUS (no story text), NOT in the code blob (no dialogue), NOT in TK5DATA3/5
  (code archive — TK5DATA5 is the same extent as TK5DATA3, listed twice).
- They must be inside TK5DATA0.BIN (2,072,586,240 B) — the only unsearched big
  archive. The 20 character-ending movies are missing from the LUT too, so they
  are presumably also in TK5DATA0.
- The in-game DW story text (mission briefings, etc.) is likewise not in any
  searched file — if it exists as text, it is in TK5DATA0; otherwise it lives
  only as the FMVs' burned-in subtitles + spoken audio.

## 6. TK5DATA0 structure (measured) + the blocker

- 18,432-byte records (2,072,586,240 / 18,432 = 112,445 records). Record header
  (32 bytes): [0:4] type (0/1), [4:8] = 8, [8:12] = 0x442b, [12:16] = 0xda,
  [16:20] per-record hash, [20:24] / [24:28] / [28:32] = file-level constants.
- Records group into FILES by constant (a,b,c) = header fields [20:24],
  [24:28], [28:32], where b = c//5 and a = c//25 (same number in three units;
  increments 78,125 or 156,250 per file — 78,125 = 5^7). 65 runs in the
  downloaded region; the biggest: rec 0–8890 (156.3 MB), rec 9037–17921
  (156.2 MB), then files of 64.8 / 48.3 / 45.6 / 44.5 / 43.9 / 41.3 MB, etc.
  A 68 s movie at ~5 Mbps ≈ 43 MB; a 302 s movie ≈ 190 MB — the file sizes
  fit movies, but that is a SIZE match only, NOT an identification.
- Bytes [32:64] of each record are IDENTICAL within a file and DIFFERENT across
  files (a per-file 32-byte header/key repeated in every record of that file).
  One file's [32:64] appears shifted by 4 bytes in another file's first record
  (rec 25752) — the record-header length may vary, or the [32:64] block is a
  window into a longer stream. UNMEASURED.
- Record payload [64:] entropy 7.988 bits/byte (random-looking = compressed or
  encrypted). Record headers are PLAINTEXT (the [4:16] pattern repeats
  identically every 9 sectors), so TK5DATA0 is NOT sector-ciphered like
  TK5DATA1.
- FAILED to open record 0's payload: zlib / gzip / lzma / bz2 (all fail);
  NLZ-SC3 (`decNLZ1.unpack_sc3game`) and `tk5psp_dec.decompress_blob` (same
  LZSS flag-byte scheme) fail — "invalid backref" / "bytearray index out of
  range"; sector cipher with 11 seed hypotheses (0, 1, 0x442b, 0xda, header
  fields, 8, 9, 18432) yields 0 MPEG magics and chance-level ASCII.
- The sibling DW-numbers agent is working the same TK5DATA0 decompressor
  (its probes 1–8, `tools-Tekken5_Tools/` vendored; latest: record diffs,
  relaxed census, decompressor tests). The DW movies CANNOT be extracted until
  that codec is cracked — that is the exact next step, with the exact tool
  (Tekken5_Tools `decNLZ1.py` / `tk5psp_dec`, or the retail generic LUT
  overlay) and the exact blocker (record-payload codec unknown).
- TK5DATA0 local download: 95/198 chunks (first 950 MB) on disk; the run
  survey covered the whole sparse file (records past ~65,424 read as zeros —
  not yet downloaded). The sibling's fetches died on disk quota; resume from
  its `.ranges.json` state files when quota allows.

## 7. In-game story text (SLUS + code blob) — what WAS found

- NO dialogue sentences exist in SLUS_210.59 or the code blob. The only
  story-adjacent strings: "STORY BATTLE", "FINAL STAGE", "STAGE %3d",
  "moviemanager", "RankingMode", "RankingMob", "SplashStage", character full
  names, stage-name formats (`stage_%02d`, `stage_final_2`, `stage_name_*`),
  UI `name_*` labels. Full lists: `story-work/slus_strings_ascii.txt`
  (1,389 strings) and `story-work/tk5data3_code_strings.txt` (10,028 strings).
- DW story facts already established from the DECODED files (not the script):
  5 stages (G Corp lab → medical wing / child's bedroom → ruins → spaceship →
  deeper); bosses in order: Modified Gun Jack, Heihachi clones, True Ogre,
  Soul Sphere (no body — confirmed absence), Monstrous Ogre; enemies: G Corp
  soldiers, JACK variants, mutants Adam/Eve/Duke/Regal/Jill; brawler
  (punch/kick/block/jump), Devil Gene meter → transform (black feathers, wings,
  laser) draining health, gems heal + give Force, ranks S/A/B/C, 40 devil
  symbols hidden, stage select + difficulty unlock. The files give structure +
  cast, NOT the cutscene script.

## 8. UNMEASURED (exact reasons)

- DW intro + DW ending movies: inside TK5DATA0; record-payload codec unknown
  (§6). No location (record range) can be named until a payload is opened.
- Character-ending movies (20): same blocker as the DW movies.
- FMV audio tracks (dialogue/music for all 4 found movies): the movie entries
  are video-only; no audio stream found in TK5DATA1. Possibly in TK5DATA0
  (same blocker) or in the `snd_*` P3Dp containers (391 clips, 297.6 s total —
  decoded, but clip↔movie mapping not done).
- Whether the "PSF" LUT entries (idx 32–64) are music, and what they contain:
  compressed blobs, codec unknown (same NLZ family as TK5DATA0 — possibly the
  same unlock).
- The damaged MPEG sections in the 4 converted movies: disc-image damage vs
  decrypt error — UNMEASURED (would need a second source or a checksum).
