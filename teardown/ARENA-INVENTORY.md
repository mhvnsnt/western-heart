# Western Heart — Cross-Game Arena Inventory

**Owner directive (seq 80731):** full arena list across all teardown games.
Index as of 2026-10-14. Counts are documented-vs-extracted; see per-game docs for detail.

| Game | Arenas/Stages | Status | Doc / Location |
|---|---|---|---|
| Tekken 7 | 34 stages | Stage ID table mapped; geometry pending full game (47GB never acquired) | `teardown/tekken7/` |
| Tekken 3 | stage list in docs | Teardown 100%; stage geometry in TMD records | `teardown/tekken3/docs/` |
| Tekken 6 (PSP) | encrypted | Pending PPSSPP live-dump or MIPS RE (`PPSSPP-LIVE-RUN-GUIDE.md` ready) | `teardown/tekken6/` |
| Tekken Tag Tournament 2 | 29 battle stages documented | From public game data (Tekkenpedia/TekkenMods/OST); archive chunks opaque | `teardown/tekken-tag-tournament-2/STAGES.md` |
| Urban Reign | 7 stage PPKs (back alleys, bars, rooftops, Chinatown, junkyards + 2) | PPKs extracted (34MB); inner Namco geometry not yet decoded | `teardown/urban-reign/` |
| Virtua Fighter 5 (PS3) | 18 arenas, 38 farcs | EXTRACTED — geometry+textures on release `vf5-ps3-v1` | `teardown/virtua-fighter-5/stages/README.md` |
| WWF No Mercy | arenas documented | Teardown 100% | `teardown/wwf-no-mercy/arenas/ARENAS.md` |
| WWE WrestleMania XIX | arena universe mapped | Teardown ~80% | `teardown/wmxix/ARENA-UNIVERSE-MAP.md`, `arenas/ARENA-FORMAT.md` |
| Soulcalibur II (PS2) | filesystem 60% | Needs owner decision: Xbox vs PS2 as primary | `teardown/soulcalibur-2/` |
| Soulcalibur VI | mechanics docs | Binaries not acquired (50GB+) | `teardown/soulcalibur-6/` |
| Dead or Alive 6 | mechanics docs | Binaries not acquired (32GB+) | `teardown/dead-or-alive-6/` |
| Dead or Alive 4 | 7.3GB ISO chunked | Reassemble + extract sequenced after TTT2 (disk) | checkpoint `doa4-teardown.json` |
| Street Fighter V | 34 stages (planned) | Not pulled — FitGirl 26.7GB → TeraBox pipeline documented | `teardown/street-fighter-5/SFV-PULL-PLAN.md` |
| Def Jam: Fight for NY | venues TBD | ISO sourced, pull pending | `teardown/def-jam-fight-for-ny/` |
| Eastern Mind | five lands (lore) | Game on release `eastern-mind-v1`; extraction pending | — |

## Western Heart stage mapping (per CHIMERA-ARCHITECTURE.md build order §6)
Stages come from **7 Eastern Mind lands skinned over WMXIX arenas**. The playable
`game/` build's first stage is **SHRINE OF THE BLADE** (`prototype/stages/shrine.json`).
Federated arena mechanics (ring-outs, wall game, destructibles) ride on top of Tekken's base.
