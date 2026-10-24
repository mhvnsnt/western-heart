# Soulcalibur II (PS2) — Teardown

**Version:** Soulcalibur II (PS2, NTSC)
**Source:** Archive.org `soulcalibur-ii` → `Soulcalibur-II.iso`
**Size:** 1,376,845,824 bytes (1.38 GB)
**Status:** Downloaded and verified. Secured to GitHub Release `soulcalibur2-ps2-v1`.
**Date:** 2026-10-13

## Stepdown History
Per owner directive (SCVI 50GB+ → SCV → SCIV → SCIII → SCII):
- **SCVI (2018):** 50GB+, not on Archive.org, cannot fit. Mechanics documented separately.
- **SCV (2012):** ~8-10GB, no standalone dump on Archive.org. Cannot fit in 8GB free.
- **SCIV (2008):** ~8GB, no standalone dump on Archive.org. Cannot fit.
- **SCIII (2005):** 1.85GB zip found (`soul-calibur-iii`), but nested multi-part solid RAR is unextractable (hangs all unrar versions). Abandoned.
- **SCII (2002):** 1.38GB ISO acquired. **SELECTED.**

## Disc Format
- Valid ISO9660 PVD magic (`CD001` at sector 16) but PVD fields are zeroed (minimal/fake header)
- Actual filesystem is **Namco proprietary PS2 format**, not standard ISO9660
- Contains verified strings: "SOULCALIBUR", "NAMCO", "Memory Card (PS2)"
- Full filesystem reverse-engineering is ongoing work

## Roster (25 fighters)
Mitsurugi, Seong Mi-na, Taki, Maxi, Astaroth, Ivy, Sophitia, Siegfried,
Nightmare, Voldo, Cervantes, Xianghua, Yoshimitsu, Rock, Lizardman,
Talim, Raphael, Yun-seong, Link (GC) / Heihachi (PS2) / Spawn (Xbox),
Assassin, Berserker, Charade, Necrid

**Note:** This PS2 version includes **Heihachi Mishima** as the guest character
(Tekken crossover — we already have his model).

## Combat Mechanics (for federation)
Documented from game knowledge for the chimera build:

### Core Systems
- **8-Way Run:** Hold any direction to run in that direction. Foundation of SC movement.
- **Guard:** Hold back or G button. Chip damage on block.
- **Guard Impact (GI):** Forward + Guard = parry. Repels attacks, creates advantage.
- **Weapon clash:** Simultaneous attacks can clash, negating both.
- **Ring Out:** Knock opponent out of the arena for instant win.
- **Soul Charge:** (Introduced in later games, refined here) Power-up state.

### Input Style
- **3 attack buttons:** Horizontal (A), Vertical (B), Kick (K)
- **Guard button** (G)
- **Directions:** 8-way + neutral
- **Throws:** A+G or B+G

### What Federates to Western Heart
| SCII System | Western Heart Layer |
|-------------|---------------------|
| 8-Way Run | Arena-mode movement (Tekken sidestep for duels) |
| Guard Impact | Skill parry (mapped to Tekken input) |
| Weapon ranges | Extended hitbox system |
| Ring Out | Arena kill condition |
| 3-button attacks | Mapped to Tekken 1/2/3/4 limb system |

### What Stays Tekken
- 4-button limb inputs (1/2/3/4)
- f/b/u/d notation
- Juggle system
- While-rising, crouch dash, stances

## Files
- **ISO:** GitHub Release `soulcalibur2-ps2-v1` (1.38GB)
- **Local:** `~/workspace/game-reverse-engineering/soulcalibur/Soulcalibur-II.iso` (deleted after upload verification per NO-DELETE-BEFORE-SAFE-STORAGE LAW)

## Next Steps
1. PS2 filesystem reverse-engineering (Namco proprietary format)
2. Character model extraction
3. Stage extraction
4. Animation extraction
5. UI/menu extraction
