# STREET FIGHTER EX3 — Teardown for Western Heart

**Role in Chimera Build:** 3D Street Fighter reference (owner 2026-10-13) — the last EX
game (Arika, PS2, 2000). Tag-battle system reference; roster/move-set structure for the
3D-fighter lane alongside Tekken/Virtua Fighter teardowns.
**Federation law:** SF is research-only — SF characters keep SF movesets but play like
Tekken. Nothing here replaces Tekken systems.
**WH universe name:** `dragon-strike` (see `RENAME-MAP.md`).
**Developer:** Arika / Capcom
**Platform:** PlayStation 2
**Disc ID:** SLUS_201.30 (US release) | **Volume:** STREET_FIGHTER_EX3
**Source:** Internet Archive `street-fighter-ex-3-usa_202404` (`Street Fighter EX3 (USA).bin`)
**Pulled/verified:** 2026-10-14 (wh-sf-dj-vf-100 lane)
**Last updated:** 2026-10-14

---

## Acquisition & Verification

- `Street Fighter EX3 (USA).bin` — **701,813,280 bytes, byte-exact vs archive.org metadata**.
  Downloaded with `wget -c` (resume-capable per owner resume law).
- Filesystem: raw 2352-byte sectors, Mode 2. Valid ISO9660 at sector 16 (PVD).
  **12 files parsed programmatically** — classic Arika PS2 layout.
- **Safe storage:** GitHub Release `sf-ex3-v1` — the 701MB `.bin`.
  TeraBox upload pending (browser lane → `/western-heart/games/street-fighter/`).
- Local working copy: `~/workspace/game-reverse-engineering/street-fighter-3d-games/downloads/Street Fighter EX3 (USA).bin`

---

## Disc Layout (12 entries)

| File | Size | Notes |
|---|---|---|
| `SYSTEM.CNF` | 57 B | Boot config |
| `SLUS_201.30` | 5,644,094 B | PS2 executable (EE MIPS) |
| `PS2.DAT` | 604,702,720 B | **Entire game data — single archive. Priority RE target.** |
| `ARIKA.DAT` | 40,960 B | Arika header/config data |
| `IOPRP165.IMG` | 98,901 B | IOP reboot image |
| `IOPCTRL.IRX` / `LIBSD.IRX` / `MCMAN.IRX` / `MCSERV.IRX` / `MTAPMAN.IRX` / `PADMAN.IRX` / `SIO2MAN.IRX` | — | Standard PS2 IOP modules |

---

## What's Next (Stage 3: decrypt/decode)

- [ ] `PS2.DAT` format RE — header/magic identification, file table, compression
- [ ] Extract player models, stages, audio from `PS2.DAT`
- [ ] Roster inventory from decoded data (WH rename → `RENAME-MAP.md`, NEEDED)
- [ ] Move-set data: per-character records (SF movesets w/ Tekken-style inputs — research only)
- [ ] Strings pass on `SLUS_201.30` for roster/move-list confirmation (as done for EX Plus Alpha)

---

## Federation

- Chimera build: `CHIMERA-BUILD.md` — 3D-fighter lane.
- Tag-battle system is EX3's distinctive mechanic — study target for WH tag modes.
