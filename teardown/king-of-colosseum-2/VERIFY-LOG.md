# LANE E — KoC2 — VERIFY LOG (evidence labels)

Every source carries exactly one label per the repo evidence-label law.

## FETCH-VERIFIED (bytes fetched this run, size + hash recorded)

1. archive.org metadata for `ps2-isos-and-translations`
   - URL: https://archive.org/metadata/ps2-isos-and-translations
   - Saved: `ia-metadata.json` (workdir)
   - Confirms: `King of Colosseum II (Japan).7z`, 1,738,818,479 bytes,
     md5 `319396fd807341fa4b6586f2f67f1eeb`,
     sha1 `6706da7f2b0395777f6682576ee65a96781502c1`
   - Also lists KoC1 discs (Noah x Zero-One 3,519,098,811 B;
     Shin Nippon x Zen Nippon x Pancrase 2,272,091,892 B) — NOT pulled.

2. `King of Colosseum II (Japan).7z` — downloaded 2026-11-19
   (curl, resumable, ~1.2 MB/s, ~30 min). Hash-verified: md5 +
   sha1 match archive.org metadata exactly; sha256
   `54b2ee70df965de71ef33a9445dbe906630c4d5a5d0893b303325745e65ce372`.

3. `King of Colosseum II (Japan).iso` — extracted from the 7z
   (7zip 23.01), 4,593,778,688 B, sha256
   `7daa1f8c950272f24e9888d26338645fdbac1974da8dbf43b30c0042ceed0511`.

4. All 49,214 extracted files — sha256 in `extract/MANIFEST-*.txt`
   (per archive) and the combined `FILES-SHA256.txt` staged for
   western-heart. Counts verified per archive: KC2FIRE.001
   16,017/16,017; KC2FIRE.000 7,519/7,519; KC2FIRE.MVS 16,660/16,660;
   KC2FIRE.AFS 9,003/9,003 (after the dedup-bug fix — see WORKLOG);
   MODULES.BIN 15/15. HELLO.FOR / GOOD.BYE / LAST.DAY verified
   entirely zeros by full streaming scan (padding, nothing extracted).

5. LZSS crack verification: files 15972/15973/15975 of KC2FIRE.001
   decode to exactly their catalogued sizes and reproduce the known
   TIM2 header byte-for-byte; all 20,182 compressed files across
   .000/.001 decode to exactly their catalogued sizes (1,492 needed
   the zero-extension fix for truncated (0,0)-match runs — all
   recovered).

6. AFS header order: `data/afs-ids.json` (9,003 entries from file
   02031) matches `extract/kc2fireafs/index.csv` order exactly
   (verified by script).

## SEARCH-VERIFIED (page text seen, no bytes pulled — never ranked as pullable)

3. Jerrold Ng, "King of Colosseum II — Move List and Guide" v1.0,
   10 Oct 2004 — Neoseeker mirror
   https://www.neoseeker.com/king-of-colosseum-ii/faqs/87809-a.html
   (8,834 lines; systems sections A–L + movelist format read via
   browser.open 2026-11-19). GameFAQs original:
   https://gamefaqs.gamespot.com/ps2/921208-king-of-colosseum-ii/faqs/32818
   - NOTE: raw-text fetch via curl failed (Neoseeker JS-gated shell page,
     25,941 B, no FAQ content; GameFAQs curl returned nothing). FAQ text
     was read through the browser tool only. Do NOT commit FAQ text
     verbatim to any repo (third-party copyrighted text).

4. GameSpot import review, "King of Colosseum II Review"
   https://www.gamespot.com/reviews/king-of-colosseum-ii-review/1900-6116996/
   (search snippet seen 2026-11-19).

5. CAGEMATCH wrestling-games list, sorted by rating
   https://www.cagematch.net/?id=77&sortby=colRating&sorttype=DESC
   (search snippet seen 2026-11-19): KoC2 #4, 9.64, 24 votes, 09.09.2004.
   VPW2 #1 (9.75) — Lane D's game.

6. ResHax thread "King of Colosseum 2 TIM2 Compression", topic 18443
   https://reshax.com/topic/18443-king-of-colosseum-2-tim2-compression/
   (full thread text read via browser.open 2026-11-19). Attachments NOT
   fetched (403, login-gated — see BROWSER-QUEUE.md).

7. KoC2 modding community FAQ
   https://sites.google.com/view/kingofcolosseum2/faq
   (search snippet seen 2026-11-19; direct open redirected to Google
   sign-in — see BROWSER-QUEUE.md).

8. bordersdown.net forum review thread, 31 Oct 2004
   https://bordersdown.net/forum/gaming/first-play/13068-king-of-colosseum-2
   (search snippet seen 2026-11-19).

9. Facebook/Instagram community posts (PlayStation Chavy reel 2026-07-18,
   Lucha Joe post 2026-08-27, @brian_fuller17 cover photo 2026-03-27) —
   sentiment/community confirmation only (search snippets).

## BROWSER-GATED (needs live browser / human-gated access)

- ResHax attachments (KoC2.zip decompression script, COCK2COMPRESSION.py,
  File1_mdl.zip sample model) — 403 without login. See BROWSER-QUEUE.md.
- KoC2 modding Discord + Google Drive (texture packs, English menu mod,
  save files) — DM Pejiseven for access. See BROWSER-QUEUE.md.
- CDRomance / romsfun / romspure KoC2 pages — alternate ISO sources, not
  needed (archive.org copy downloading).

## UNVERIFIED

- None outstanding. (GameFAQs raw-text curl: no file returned — recorded
  under item 3, not a source failure; the FAQ was read via browser.open.)
