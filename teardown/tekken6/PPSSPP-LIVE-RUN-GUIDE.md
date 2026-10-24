# Tekken 6 PSP — PPSSPP Live Decrypt Run Guide

## Status
- ✅ EBOOT.BIN already decrypted via pspc (KIRK) — saved as `decrypted/EBOOT.DECRYPTED.ELF`
- ✅ PPSSPP v1.20.4 installed at `~/workspace/tools/ppsspp/PPSSPP.AppImage`
- ✅ ISO at `~/workspace/game-reverse-engineering/tekken6/tekken6-psp.iso` (816MB)
- ⏳ DATA401.IDX + 384MB data region still encrypted — needs live run OR IDX key recovery

## Why a live run is needed
The 384MB game data (models, textures) is encrypted. The decryption happens at runtime
via the game's PAC system (`openPac`, `ReadInfo`, `ktRead`). PPSSPP can dump decrypted
memory/files during emulation.

## Exact steps for browser task with display

### 1. Launch PPSSPP
```bash
~/workspace/tools/ppsspp/PPSSPP.AppImage
```
(If FUSE fails, extract first: `./PPSSPP.AppImage --appimage-extract` then run `squashfs-root/AppRun`)

### 2. Load the ISO
- File → Load → navigate to `~/workspace/game-reverse-engineering/tekken6/tekken6-psp.iso`
- OR drag the ISO onto the PPSSPP window

### 3. Enable decrypted EBOOT dump (optional — already done via pspc)
- Settings → Tools → Developer Tools → check "Dump Decrypted EBOOT.BIN on game boot"
- This outputs to PPSSPP's memstick folder

### 4. Dump game data from memory
The critical step: as the game loads PAC data, decrypted content exists in RAM.
- Settings → Tools → Developer Tools → "Dump frames" won't help here
- Instead: use PPSSPP's debugger (Settings → Tools → Developer Tools → check "Show debugger on load")
- In debugger: Memory view → search for GMO magic (`GMO\0`) or TIM2 (`TIM2`)
- Right-click → dump memory region to file

### 5. Alternative: GE debugger texture dump
- While game is running: Debugger → GE Debugger → Textures tab
- Dump all loaded textures (these are decrypted in VRAM)

## What we need from the live run
1. Decrypted DATA401.IDX structure (to map the 384MB data region)
2. GMO model files dumped from RAM
3. Any decryption keys visible in memory

## Files ready
- ISO: `~/workspace/game-reverse-engineering/tekken6/tekken6-psp.iso`
- Decrypted EBOOT: `~/workspace/game-reverse-engineering/tekken6/decrypted/EBOOT.DECRYPTED.ELF`
- Encrypted IDX: `~/workspace/game-reverse-engineering/tekken6/extracted/DATA401.IDX`
- pspc decrypter: `~/workspace/tools/tekken-decrypt/psp/kirk_engine/pspcipher/pspc`
