# Tekken Teardown Completion Plan — 2026-10-22

**Worker:** Tekken Teardown Completion Lane (parallel worker)
**Owner directive:** "Get Tekken 5, Tekken 6, and Tekken Tag 2 all complete to 100%"
**Date:** 2026-10-22

---

## Executive Summary

| Game | Before | After (this pass) | Blocker |
|------|--------|-------------------|---------|
| Tekken 5 (PS2) | 0% (never acquired) | **Acquisition documented** | Disk (3.76GB ISO) |
| TTT2 (X360) | 15% (docs only) | **Extraction plan ready** | Disk (12.6GB + 27GB peak) |
| Tekken 6 (PSP) | 30% (models encrypted) | **No change** (deep RE in progress) | DATA401 decrypt |
| Tekken 7 (PC) | 40% (King-focused) | **Law/Lars sourcing mapped** | No free rips found |

**Critical constraint:** Disk at 99% (1.6GB free). All large downloads blocked until cleanup completes.

---

## 1. Tekken 5 (PS2) — Priority #1

### Acquisition (DONE)
- **Release:** [tekken5-ps2-v1](https://github.com/mhvnsnt/western-heart/releases/tag/tekken5-ps2-v1)
- **Source:** Internet Archive `slus-210.59.-tekken-5`
- **File:** `SLUS_210.59.Tekken 5.ISO` (3.76 GB)
- **URL:** https://archive.org/download/slus-210.59.-tekken-5/SLUS_210.59.Tekken%205.ISO
- **Region:** USA (SLUS-21059)
- **Verified:** 2026-10-22

### Why T5 Matters
1. **Devil Within source** — owner's story-mode blueprint (Heart and Mind Within)
2. **Missing entirely** from teardown holdings
3. **32-fighter roster** with classic movesets
4. Jin Kazama's Devil Within campaign = template for per-character story mode

### Extraction Plan (when disk allows)
1. Download ISO from IA to staging
2. Extract with PS2 ISO tools (Apache3, or 7z for ISO9660)
3. Identify model format (T5 uses Namco's PS2-era formats)
4. Extract: models → movesets → stages → audio → Devil Within data
5. Devil Within: full level/map extraction (priority for story mode)
6. Upload large files to release, wire small files to repo

### T5 Roster (32 fighters)
Jin Kazama, Kazuya Mishima, Heihachi Mishima, Paul Phoenix, Marshall Law,
King, Nina Williams, Yoshimitsu, Hwoarang, Ling Xiaoyu, Bryan Fury,
Christie Monteiro, Craig Marduk, Steve Fox, Jack-5, Kuma, Panda, Lee Chaolan,
Lei Wulong, Wang Jinrei, Anna Williams, Baek Doo San, Bruce Irvin,
Ganryu, Julia Chang, Mokujin, Roger Jr., Asuka Kazama (new), Feng Wei (new),
Raven (new), Jinpachi Mishima (boss, new)

---

## 2. Tekken Tag Tournament 2 (X360) — Priority #2

### Status (unchanged)
- **Release:** `ttt2-7z-v1` (27 assets, 12.6 GB total)
- **Docs:** INVENTORY.md, ROSTER.md (59 fighters), STAGES.md (29 stages), TEARDOWN.md
- **Format:** Xbox 360 STFS (Title ID 4E4D0859)
- **Tools:** `teardown/tekken-tag-tournament-2/tools/` (god_surgical.py, stfs_blobs.py, xdvdfs_reader.py)

### Blocker
- **Disk:** 12.6GB download + 27GB extraction peak. Currently 1.6GB free.
- **Cannot proceed** until disk cleanup completes.

### Selective Extraction Plan (disk-efficient)
Instead of full extraction, target specific characters:
1. Download chunks to external storage (not local disk)
2. Extract STFS → parse Data chunks for character boundaries
3. **Priority extractions:** Marshall Law, Lars Alexandersson
4. Upload extracted character packs to new release `ttt2-chars-v1`
5. Delete local copies immediately after upload

### TTT2 Roster (59 fighters)
All T6 roster + Jun Kazama, Michelle Chang, Kunimitsu, Ogre, True Ogre,
Angel, Jinpachi Mishima, Forest Law, Prototype Jack, Alex, Tiger Jackson,
Violet, Jaycee, Sebastian, Slim Bob, Combot, Unknown, Miharu Hirano,
Dr. Bosconovitch (Wii U)

---

## 3. Tekken 6 (PSP) — Priority #3

### Status (unchanged — deep RE in progress by decrypt lane)
- **What's done:** EBOOT decrypted, sector cipher fully reversed, K1/K2 extraction solved
- **What's blocked:** Bulk DATA401 transform (384MB encrypted data region)
- **Docs:** `teardown/tekken6/docs/` (SECTOR-CIPHER-REVERSED.md, K1K2-CALL-SITE-ANALYSIS.md, etc.)
- **Tools:** `teardown/tekken6/tools/` (sector_cipher.py, k1k2_extract.py)

### Path Forward
1. **Option A (RE):** Continue static analysis of decrypted EBOOT for DATA401 key derivation
2. **Option B (PPSSPP):** Live memory dump via PPSSPP (needs browser task with display)
3. **Recommendation:** Option B is faster if browser resources available

### T6 Roster (40 fighters)
All T5 roster + Lars Alexandersson (new), Alisa Bosconovitch (new),
Zafina (new), Miguel Caballero Rojo (new), Leo Kliesen (new), Bob Richards (new)

---

## 4. Tekken 7 (PC) — Priority #4

### Status
- **What's done:** King-focused extraction (40%), T8 King variants
- **What's missing:** Full 51GB game, most character models

### Marshall Law + Lars Sourcing (2026-10-22 research)
**Result:** No free T7 rips found for Law or Lars (confirmed via web search).
- RigModels.com: requires login, no specific Law/Lars hits
- SFMLab: has Shaheen, Miguel, Akuma, Alisa — but NOT Law or Lars
- DeviantArt: Paul only via XPS, no Law/Lars
- Archive.org: no T7 Law/Lars model rips

**Sourcing options (ranked):**
1. **TTT2 extraction** (has both) — blocked on disk
2. **T6 PSP** (has both) — blocked on decrypt
3. **T5 PS2** (has Law, not Lars — Lars debuted in T6) — blocked on disk
4. **SFMLab/DeviantArt** (needs browser download task)
5. **T7 full purchase** (owner authorized up to $10, needs owner action)

### Recommended: TTT2 selective extraction for Law + Lars
Both characters are in TTT2 with full models, movesets, and animations.
Single extraction run gets both.

---

## 5. Marshall Law + Lars — Specific Extraction Plan

### Marshall Law
- **Available in:** T5 (PS2), T6 (PSP), TTT2 (X360), T7 (PC)
- **T3 moveset:** Already in repo (`teardown/tekken3/movesets/moveset_law.json`)
- **Best source:** TTT2 (most complete: model + moveset + customization)
- **Fallback:** T5 PS2 (simpler format, smaller download)

### Lars Alexandersson
- **Available in:** T6 (PSP), TTT2 (X360), T7 (PC)
- **NOT in T5** (debuted in T6)
- **Best source:** TTT2 (full model + moveset)
- **Fallback:** T6 PSP (if decrypt completes first)

### Extraction Steps (when disk allows)
1. Download TTT2 chunks (12.6GB) to staging
2. Extract 7z → STFS parse → locate character data
3. Extract Law + Lars: models, textures, movesets, animations, voices
4. Convert to GLB + JSON moveset format
5. Upload to `ttt2-chars-v1` release
6. Wire into `roster/` and `moveset-library/`
7. Clean local files

---

## 6. Disk Space Action Plan

**Current:** 99% full (1.6GB free of 100GB)

**Space hogs:**
- `~/workspace/fix2/` — 29GB (old working copy)
- `~/workspace/fix/` — 18GB (old working copy)
- `~/workspace/audit/` — 3.8GB (old working copy)
- `~/workspace/tripo-staging/` — 271MB (coordinator archiving to repo)

**Recommendation:**
- Coordinator is archiving tripo-staging → repo → clean (user authorized)
- fix/fix2/audit are old clones — **need user authorization before deletion**
- Once tripo-staging is clean: ~2GB free (enough for T5 ISO staging)
- TTT2 needs 40GB+ peak — requires fix/fix2 cleanup (user decision)

---

## 7. What Was Delivered This Pass

1. ✅ **T5 acquisition documented** — IA source verified, GitHub release created
2. ✅ **TTT2 extraction plan** — selective approach documented
3. ✅ **T6 status confirmed** — decrypt lane still working, no action needed
4. ✅ **T7 Law/Lars sourcing** — researched, no free rips, TTT2 is best path
5. ✅ **Disk assessment** — space hogs identified, cleanup recommendations
6. ✅ **This document** — comprehensive plan for coordinator/owner review

## 8. Next Actions (for coordinator)

1. Complete tripo-staging → repo archival (free ~2GB)
2. Ask user about fix/fix2/audit deletion (free ~50GB)
3. Download T5 ISO → extract → Devil Within priority
4. TTT2 selective extraction (Law + Lars first)
5. Continue T6 decrypt (separate lane)
6. T7 Law/Lars via browser task (SFMLab/DeviantArt) as fallback

---

*Generated by Tekken Teardown Completion Lane, 2026-10-22*
*All large files to GitHub Releases, never local disk.*
*No clobbering. PRs only. Never push to main.*
