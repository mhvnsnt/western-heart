# RENAME-MAP — Western Heart Proprietary Universe Rename

**OPERATIONAL DOCUMENT — DELETE WHEN COMPLETE.**
Owner directive 2026-10-14: "rename ALL the files and make it proprietary to our universe."
When every teardown file is renamed and the game hooks up correctly, DELETE this file
so no one knows we renamed stuff. Self-contained; nothing else references it.

**Basis:** "I own all of those games that we did teardown files to." — Owner
**Rule:** Data stays real; names become Western Heart. The game must hook up to
renamed files correctly (not just renamed on disk).

---

## Universe Name Mapping

| Source Game | WH Universe Name | Rationale |
|-------------|------------------|-----------|
| Tekken 3 | `iron-legacy` | The legacy iron-fist tournament |
| Tekken 6 | `iron-storm` | The storm-era tournament |
| Tekken 7 | `iron-prime` | The prime-era tournament |
| Tekken 8 | `iron-apex` | The apex-era tournament |
| Tekken Tag 2 | `iron-tag` | Tag-team tournament |
| Virtua Fighter 5 | `virtual-soul` | Virtual arena fighters |
| Def Jam: Fight for NY | `underground-brawl` | Underground street brawl |
| Urban Reign | `street-reign` | Street reign brawlers |
| Street Fighter (all) | `dragon-strike` | Research only per SF directive |
| WWF No Mercy | `mat-kings` | Kings of the mat |
| WWE WrestleMania XIX | `mat-legends` | Legends of the mat |
| WWE 2K series | `mat-dynasty` | Dynasty-era wrestling |
| Dead or Alive 4/6 | `ninja-heart` | Ninja-heart fighters |
| Soulcalibur II/VI | `soul-blade` | Soul-blade weapons |
| Eastern Mind | `dream-walker` | Dream-walker adventure |

---

## Completed Renames

### 2026-10-14 — T3 Animation Merge (this task)
| OLD | NEW | Status |
|-----|-----|--------|
| `assets/anim/t3/king_on_pantera_leoman/*.json` | `assets/anim/iron-legacy/pantera/*.json` | PENDING |
| `teardown/tekken3/movesets/` | `teardown/iron-legacy/movesets/` | PENDING |
| `teardown/tekken3/animations/` | `teardown/iron-legacy/animations/` | PENDING |
| `lab/tools/t3_motion_bake.py` | `lab/tools/ironlegacy_motion_bake.py` | PENDING |

### Game files wired to renamed sources
| Game File | Sources From (renamed) |
|-----------|------------------------|
| `game/js/t3anims.js` (new) | `assets/anim/iron-legacy/pantera/*.json` (real T3 motion) |
| `game/js/fighter.js` (modified) | Real T3 clips replace procedural combat |
| `game/assets/*_moves.json` | `teardown/iron-legacy/movesets/` (real T3 frame data) |

---

## Still Needed (per game)

### iron-legacy (Tekken 3) — 100% complete ✅
- Nothing missing. 7 fighters, 15 stages, 8,556 textures, 3,247 moves, real anim clips.

### street-reign (Urban Reign) — ~95%
- **Have:** VGS cracked, 509 files, 1,033 audio files, 72 UI screens, 46 motion packs
- **Need:** DCM semantics, inner PPK geometry
- **Blocker:** Format reverse-engineering in progress

### mat-legends (WMXIX) — ~80%
- **Have:** Full extraction, 126 wrestler OBJs, 170 YANM anims, 2,690 CAW parts
- **Need:** ECD identity, base-ID generation, CAW.gci semantics
- **Blocker:** Watchdog lane active, needs Dolphin/browser for CAW.gci

### soul-blade (SCII) — ~60%
- **Have:** Xbox version extracted
- **Need:** PS2 filesystem RE (1.38GB ISO on release)
- **Blocker:** Owner decision: Xbox vs PS2 as primary

### iron-prime (Tekken 7) — ~40%
- **Have:** 5 King variants (T8 base, T8 S2, T3 legacy, T7 1P, Armor King)
- **Need:** Full 51GB game (never acquired)
- **Blocker:** No landing zone; TeraBox could receive via browser

### iron-storm (Tekken 6) — ~30%
- **Have:** 46 videos, ISO structure, 40-fighter roster, decrypted EBOOT
- **Need:** DATA401 models (384MB encrypted)
- **Blocker:** AES key needed; PPSSPP live dump is fastest path

### dream-walker (Eastern Mind) — ~20%
- **Have:** Game safe on release (549MB)
- **Need:** Full extraction (bitmaps, stage art, 3D, audio)

### iron-tag (TTT2) — ~15% → teardown in progress
- **Have:** 26/26 chunks on release `ttt2-7z-v1`, docs (59 fighters, 29 stages), STFS/GoD tooling (zarmanager pure-Python), custom XDVDFS parser (`tools/xdvdfs_reader.py`), surgical GoD pull tool (`tools/god_surgical.py`), STFS blob tool (`tools/stfs_blobs.py`)
- **Need:** 13.3GB reassembly (1/26 chunks, PAUSED for disk emergency — resume at <80%), then surgical extraction: GoD header + DataXXXX on demand → XDVDFS walk → per-fighter model/moveset pull. NO 27GB full extraction needed (surgical approach).
- **Blocker:** Disk emergency 2026-10-15 (was 95%, recovering). TeraBox upload blocked (needs owner sign-in for browser session).
- **Rename plan:** `teardown/tekken-tag-tournament-2/` → `teardown/iron-tag/`; extracted fighter data → `teardown/iron-tag/fighters/<fighter>/`; 59 fighters keep original names as donor refs (per ROSTER.md convention).

### ninja-heart (DOA4) — ~15%
- **Have:** 30/30 chunks on release (7.8GB)
- **Need:** Reassemble + extract
- **Blocker:** Sequenced after TTT2 (disk)

### soul-blade VI / ninja-heart 6 — ~10% each
- **Have:** Mechanics docs only
- **Need:** Game binaries (32GB / 50GB+)
- **Blocker:** Not on Archive.org; need owner source or stepdown

### mat-kings (No Mercy) — 100% complete ✅
### virtual-soul (VF5) — 100% complete ✅

---

## Rename Execution Order

1. ✅ **Phase 1:** iron-legacy (Tekken 3) — files this task touches
2. **Phase 2:** street-reign (Urban Reign) — game uses UR systems
3. **Phase 3:** mat-kings, mat-legends, mat-dynasty (wrestling)
4. **Phase 4:** iron-prime, iron-storm, iron-apex, iron-tag (other Tekken)
5. **Phase 5:** virtual-soul, underground-brawl, dragon-strike, ninja-heart, soul-blade, dream-walker

**Safety rules:**
- `git mv` (preserves history), never manual move
- Update ALL references: code imports, docs, README provenance tables, scripts
- Verify game still boots + fights work after each phase
- One phase per PR; never batch-rename everything at once

---

## Deletion Checklist (when all done)
- [ ] All teardown dirs renamed
- [ ] All references updated (grep for old names returns zero)
- [ ] Game boots, fights load, fighters visible and animating
- [ ] No duplicate downloads (this map prevented re-pulls)
- [ ] DELETE THIS FILE
