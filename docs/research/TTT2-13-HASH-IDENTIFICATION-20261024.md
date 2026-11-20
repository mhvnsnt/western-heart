# TTT2 13 hash files — IDENTIFIED (2026-10-24, Lane E)

Source set: `teardown/tekken-tag-tournament-2/extracted-small/` — 13 files,
2,957,312 bytes total. All 13 start with the `LIVE` magic of an Xbox 360
STFS (Secure Transacted File System) package, Microsoft-signed (Free60
STFS format: LIVE = delivered over Xbox Live; header fields at 0x340
HeaderSize, 0x344 Content Type, 0x348 Metadata Version, 0x360 Title ID).

Verified header facts, identical across the set unless noted:
- Title ID 0x4E4D0859 at 0x360 = Tekken Tag Tournament 2 (Xbox 360).
  Title name field (UTF-16BE, 0x1691) reads `Tekken TAG Tournament 2`.
- Thumbnail PNG at exactly 0x171A (5914) and title-thumbnail PNG at
  exactly 0x571A (22298) — the Free60 STFS thumbnail offsets. The two
  PNGs are byte-identical inside each file (same SHA, same length =
  the thumbnail-size field at 0x1712).
- Display name is UTF-16BE at 0x411; description at 0xD11; publisher
  `Microsoft` at 0x1611. The display name is what identifies each item.

## Identification table (file → identity + evidence)

| File | Content type | Display name (0x411, UTF-16BE) | Identity |
|---|---|---|---|
| 000005440E4582E3C2F571D64E4D0859 (98,304 B) | 0x9000 Avatar Item | Heihachi Hair Helmet | Xbox 360 Avatar Item: Heihachi hair helmet |
| 00000544954CA233C1F109A04E4D0859 (147,456 B) | 0x9000 Avatar Item | Armor King Helmet | Xbox 360 Avatar Item: Armor King helmet |
| 0000075CC0497211C7FC19A94E4D0859 (229,376 B) | 0x9000 Avatar Item | Heihachi Costume | Xbox 360 Avatar Item: Heihachi costume |
| 00000AB838491231C58A9B294E4D0859 (245,760 B) | 0x9000 Avatar Item | Lars Costume | Xbox 360 Avatar Item: Lars costume |
| 00000AB8A8404242C5D571B84E4D0859 (237,568 B) | 0x9000 Avatar Item | Lili Costume | Xbox 360 Avatar Item: Lili costume |
| 00000AB8C144E211C7C0A9CC4E4D0859 (241,664 B) | 0x9000 Avatar Item | Kazuya Costume | Xbox 360 Avatar Item: Kazuya costume |
| 00000FFC09406211C1456F0A4E4D0859 (315,392 B) | 0x9000 Avatar Item | Yoshimitsu Costume | Xbox 360 Avatar Item: Yoshimitsu costume |
| 00000FFC554FD211CBEB87024E4D0859 (315,392 B) | 0x9000 Avatar Item | Raven Costume | Xbox 360 Avatar Item: Raven costume |
| 00000FFCA94D9272C21DD0644E4D0859 (339,968 B) | 0x9000 Avatar Item | Alisa Costume | Xbox 360 Avatar Item: Alisa costume |
| 00000FFCBC49B2A1C193AE4E4E4D0859 (319,488 B) | 0x9000 Avatar Item | Armor King Costume | Xbox 360 Avatar Item: Armor King costume |
| 00001000434E3243C8DCDAF44E4D0859 (262,144 B) | 0x9000 Avatar Item | Devil Jin Wings Animation | Xbox 360 Avatar Item: Devil Jin wings animation |
| 00001000FE438273C4A8BBFF4E4D0859 (159,744 B) | 0x9000 Avatar Item | Lei Wulong Fighting Animation | Xbox 360 Avatar Item: Lei Wulong fighting animation |
| 392CFF5C9DB17CCAEBC3 (45,056 B) | 0x7000 Game on Demand | TEKKEN TAG 2 | Xbox 360 Game on Demand installed-game header stub only (description: "This is an installed game. To play, insert the original game disc."). No game data blocks present; its two PNGs are the same 64x64 thumbnail twice. |

Each Avatar Item also carries a third PNG (128x128) in its data blocks —
the item preview image. Full per-file SHA-256, PNG offsets/lengths and
descriptions are in the GPU job E1 manifest output that ships with this
lane (tools/gpu-lane-e/, job E1).

## Consequence — read this before using the set

- NONE of the 13 is Jun. NONE is character motion, moveset, model, or
  stage data. The Jun search inside this set is CLOSED with a negative
  result, proven by the header display names above — not by absence of
  a match in a guess list.
- These are Xbox dashboard cosmetics (avatar costumes/helmets/animations).
  They have NO fight wiring value and must NOT be wired as fighters,
  costumes, or animations in Western Heart. Their only legitimate WH use
  is as a costume-reference note (which avatar item exists for which
  fighter), and even that stays in technical docs, never in canon text.
- TTT2 character data (Jun included) does NOT live in this set. It lives
  in the game proper and is reached by the Kiloutre CEMU route (see the
  Jun section of the lane report / GPU job E2 delegation note).
- Raw files stay in the PRIVATE game-reverse-engineering repo only.
  This doc carries names, header fields, and hashes — no game binaries.

## Method note (GPU)

Identification was done by CPU header analysis on this lane's VM and is
packaged as GPU job E1 (tools/gpu-lane-e/gpu-job-e1-ttt2-13.py) for
re-verification on the coordinator's Kaggle/Colab lane: manifest mode
(Kaggle-safe, no raw binaries) and files mode (private-repo copy only).
CPU baselines: files mode 1.985 s for 2,957,312 bytes; manifest mode
0.154 s end-to-end median (6 runs). GPU wall time and speedup are
recorded by the job on its run — speedup is measured, never claimed here.
