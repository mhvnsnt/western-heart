# SF EX stage defs — `game/assets/stages/sf-ex/stages.json`

Data-only pack for the Street Fighter EX PS1 discs (Plus Alpha + EX2 Plus).

- **8 EX+α packs** (`STG/SxxT.PAC` textures + `STG2/SxxD.PAC` geometry, 8 stages) —
  stage *names* are not stored in the SLUS_005.48 ASCII tables, so defs are keyed
  `sfex-s00..s07` with a pending-cross-check note. NO names invented.
- **19 EX2 Plus named stages** — verbatim list from
  arcadequartermaster.com/sfex2p_bosses.html (PHANTOM BOMB, MAHATMA TEMPLE, …).

Wiring: `game/js/stages.js` STAGES array (Lane 4 owns that file — another lane edits
it live; this pack does not touch it). To wire: register each id via the same
pattern as the existing entries (id, name, tier e.g. 'STREET FIGHTER EX'),
pointing the builder at the STG2 geometry once decoded.

Geometry/textures themselves come from the disc ISOs (re-pull lane in progress;
see SF-TEARDOWN-STATUS.md). Music (`MUS/MUS0.XA..MUS3.XA`) and FMVs (`MOV/*.STR`)
were deferred on disk space in the Oct-14 extraction and are NOT in this pack.
