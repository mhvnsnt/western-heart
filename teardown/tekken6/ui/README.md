# Tekken 6 — UI Assets (BLOCKED: Encrypted)

## Status

Tekken 6 PSP's game data (including all UI assets, character portraits,
menu art, and customization assets) is locked behind PSP `~PSP` encryption.

## What's Encrypted

- `USRDIR/DATA401.IDX` (25KB) — File index, encrypted
- `USRDIR/DINF_400.BIN` (120 bytes) — Data info, encrypted
- All game data referenced by the index (models, textures, UI, audio)

## Decryption Path

See `../TEARDOWN.md` for the PPSSPP decrypt recipe:
1. Boot the ISO in PPSSPP with "Dump Decrypted EBOOT.BIN on game boot"
2. PPSSPP emulates PSP KIRK crypto, decrypts `~PSP` tagged files
3. Extract decrypted data, then pull UI assets

## What's Available (Unencrypted)

- `../videos/` — All 46 PMF cinematics (on Release `tekken6-endings-v1`)
- `PSP_GAME/ICON0.PNG`, `PIC1.PNG` — PSP system icons (fetchable via range-request)

## For the Chimera Build

Once decrypted, priority UI extractions:
- Character select portraits (all 40 fighters)
- Customization menu assets
- Versus screen art
- Stage select art
- HUD elements
