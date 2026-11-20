# Tekken Arena Decryption — Status

**Owner ask (seq 80794):** Tekken arenas still encrypted.

## Tekken 6 (PSP)
- EBOOT.BIN decrypted via KIRK (PR #56); `DATA401` decrypt is the open item
- Two paths ready: `teardown/tekken6/PPSSPP-LIVE-RUN-GUIDE.md` (live dump, needs
  browser task with display) or MIPS reverse-engineering
- Arenas unlock with DATA401

## Tekken 7 (PC/UE4)
- Stage ID table mapped (34 stages); asset prefixes catalogued (SK/SKT/SM/BP/PA/CS/CCI/CI/T)
- **Blocked on the full 47GB game** — never acquired (VM disk too small; TeraBox
  Premium is the candidate landing zone — see `TERABOX-MANIFEST.md` and
  `TEKKEN78-ACQUISITION-PLAN.md`)

## Tekken 8
- Same blocker as Tekken 7 (full game never acquired)

## What this unblocks
`teardown/ARENA-INVENTORY.md` rows for T6/T7/T8 flip from "encrypted/pending"
to extracted once the game data lands.
