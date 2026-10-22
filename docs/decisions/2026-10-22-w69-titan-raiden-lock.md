# Decision: Titan -> Raiden / Big Bear (Fatal Fury: Wild Ambition) lock (worker 69, 2026-10-22)

## Owner instruction (verbatim quote)
"Priority extractions: Raiden/Big Bear moveset (for Titan)."

## Lock
- **Titan -> Raiden / Big Bear (Fatal Fury: Wild Ambition)** — recorded in
  `moveset-library/movesets/CLAIMED-MAP.json` under new locked section
  `ffwa_federation`, source file `federation/kof3d/ffwa-raiden.json`.
- Titan is on the Ashlane 28-list; this is his first moveset-source lock.

## Why Wild Ambition (not MI2)
Worker 59 verified via fandom: Raiden is NOT playable in KOF: Maximum
Impact 2 (cameo only, as Clark's Another Outfit Variation E). His only 3D
playable appearance is Fatal Fury: Wild Ambition (Hyper Neo Geo 64, 1999;
PS1 port, 2000). The PS1 port is the practical source (no public HNG64
extraction toolchain).

## Acquisition (this lane)
- IA item `fatal-fury-wild-ambition-usa_202503`: `Fatal Fury - Wild Ambition
  (USA).chd`, 448,135,229 bytes, md5 `557b9d20a2d0b9682ac089cbda13a51e` —
  VERIFIED match.
- Extracted with `chdman extractcd` -> 694MB `.bin`; `bchunk` -> 604MB
  ISO9660 (`SLUS-01001`, SNK, 1999).
- Disc contents: `GAME.DAT` (91.6MB, character/stage data), `MENU.BIN`,
  `SLUS_010.01` (executable), `STR/` (videos), `DUMMY.DAT`.

## GAME.DAT forensics (so far)
- 91,615,232 bytes. Header u32 = 542, followed by 542x8-byte entries —
  candidate file table, but (offset,size) pairing is ambiguous (tiny sizes
  under the naive reading); data at candidate offsets is high-entropy
  (compressed/encrypted).
- Full-file scan: 3,631 zlib signatures, 17,266 TIM texture signatures —
  the archive holds zlib-compressed chunks and PS1 TIM textures.
- No `RAIDEN`/`BEAR` plaintext strings (only coincidental `JOE`/`RYO` hits).
- Full binary RE (table format + decompression + TMD models) is queued;
  the moveset below is doc-sourced from the verified FAQ.

## Moveset delivered
`moveset-library/movesets/federation/kof3d/ffwa-raiden.json` — 17 moves from
the Wild Ambition FAQ/Walkthrough (Sephiroth808, vFinal 2014-05-20):
10 throws (incl. unblockable 360s: Thunder Death Driver, Bersek Trident,
Circle Hurricane super) + 7 strikes (DokuGiri poison-mist dizzy, Giant Bomb,
Thor's Hammer super). Tekken-notation inputs per the conversion standard
(P/K/S -> 1/2/3/4/1+2-family; throws -> 1+3/2+4-family command throws).

## Iori (Deathfang) 3D upgrade — same commit
`kof3d-iori.json` 20 -> 36 moves: 12 MI-series stylish strings (SM13-24,
Yumebiki/Agatsuki routes, unblockable Hikirigine enders) + Hikirigine throw
+ Ura 311 Shiki Saku Tsumagushi + Ge-Shiki Kui/Agatsuki, from
snk.fandom.com. Exact MI2 in-game button sequences flagged for verification
against the MI2 ISO (full 1.9GB IA dump downloading; the earlier 731MB file
was a trimmed dump with truncated PLAYER.AFS).
