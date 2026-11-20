# Tekken 6 PSP — Decrypted EBOOT

## EBOOT.DECRYPTED.ELF (4.0MB)
Decrypted from `PSP_GAME/SYSDIR/EBOOT.BIN` using pspc (KIRK engine).

**Method:**
- Tag: 0xD91612F0 (Tekken 6 custom)
- Key from JPCSP KeyVault: `9E20E1CDD788DEC0319B10AFC5B87323`
- Tool: `~/workspace/tools/tekken-decrypt/psp/kirk_engine/pspcipher/pspc`
- Command: `pspc t6_eboot.bin t6_eboot_decrypted.bin`
- Output: Valid ELF (`7f454c46`)

**No PPSSPP live run needed for EBOOT** — direct KIRK decryption works.

## Still encrypted
- `DATA401.IDX` (26KB) — PAC index, CBC-mode encrypted
- 384MB data region — PAC data, encrypted
- `DINF_400.BIN` (120 bytes) — likely contains PAC decryption keys

## Next step
PPSSPP live memory dump (see `../PPSSPP-LIVE-RUN-GUIDE.md`) OR
reverse-engineer the PAC decryption from this ELF's `packdatas_t` code.
