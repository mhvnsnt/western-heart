# WWE 2K14 DLCs — Catalog (PS3, USA)

Pulled 2026-10-14 from Archive.org `wwe-2-k-14-dlcs` → `WWE 2K14 DLCS.zip`
(44,660,178 bytes, byte-verified against metadata API).
Title ID: NPUB31343 (WWE 2K14 US, publisher UP1001 = 2K Sports).

## Packs (12)

| Pack | Content ID | PKG size |
|------|-----------|----------|
| Kevin Nash Exclusive Character | UP1001-NPUB31343_00-WWE2K14KEVINNASH | 3,719,536 |
| Legends Pack | UP1001-NPUB31343_00-WWE2K14LEGENDSPK | 3,719,536 |
| Season Pass (stub) | UP1001-NPUB31343_00-WWE2K14SEASONPAS | 3,719,840 |
| Online Pass (stub) | UP1001-NPUB31343_00-WWE2K14ONLINEPAS | 3,720,032 |
| Scott Hall Exclusive Character | UP1001-NPUB31343_00-WWE2K14SCOTTHALL | 3,719,536 |
| Superstars and Moves Pack | UP1001-NPUB31343_00-WWE2K14SUPERSTAR | 3,719,536 |
| The Giant | UP1001-NPUB31343_00-WWE2K14THEGIANT1 | 3,719,536 |
| Ultimate Warrior | UP1001-NPUB31343_00-WWE2K14ULWARRIOR | 3,720,032 |
| Undertaker Pack | UP1001-NPUB31343_00-WWE2K14UNDERTAKE | 3,720,032 |
| Summer Rae | UP1001-NPUB31343_00-WWE2K14SUMMERRAE | 3,719,536 |
| n.W.o Pack | UP1001-NPUB31343_00-WWE2K14NWOPACK01 | 3,719,536 |
| Virgil | UP1001-NPUB31343_00-WWE2K14VIRGILDLC | 3,719,536 |

Each pack = 1 `.pkg` (PS3 package, encrypted) + 1 `.rap` (license file, preserved in-pack).

## Key finding: these are unlock stubs

All 12 PKGs are ~3.7MB and nearly identical in size. WWE 2K14 shipped its DLC wrestlers
**on the game disc** — these PKGs are license/unlock packages, not full character data.
Standalone value is limited WITHOUT the full WWE 2K14 game (PS3/Xbox 360, ~8GB),
which was NOT found as a verified full dump on Archive.org (see CATALOG.md addendum).

## Status

- File contents are PS3-encrypted (PKG revision 0x8000 header, `\x7FPKG` magic confirmed).
- RAP licenses preserved alongside each PKG — a future PS3-toolchain lane
  (ps3tools/RPCS3 pkg install) can decrypt and extract if the full game is acquired.
- NOT deleted per NEVER-DELETE-GAME-FILES. Staged for TeraBox browser lane.

## Contents unlocked (for the character inventory / rename map)

Kevin Nash, Scott Hall, Virgil, n.W.o stable, Ultimate Warrior, Summer Rae,
"The Giant", Undertaker (alternate), Legends pack wrestlers, Superstars pack
(Fandango, Big E Langston, Brie Bella, Nikki Bella era) + new moves.
WH proprietary names: PENDING OWNER (see RENAME-MAP.md).
