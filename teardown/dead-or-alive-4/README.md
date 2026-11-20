# Dead or Alive 4 — Teardown

**Status:** ISO acquired and verified. Full extraction in progress.

## ISO Status
- **Source:** GitHub Release `doa4-iso-v1` (mhvnsnt/western-heart), 30 parts
- **Size:** 7,834,892,288 bytes (7.8GB) — VERIFIED
- **Format:** Xbox 360 XGD (XEX2 found at offset 0x3f23000)
- **Local:** `~/workspace/doa4-bass/doa4.iso` (assembly complete 2026-10-16)

## Extraction Blocker
`extract-xiso` v2.7.1 only supports original Xbox (Xbox 1) ISOs. DOA4 is Xbox 360 (XGD format). Need Xbox 360 XGD extraction tool. See `DOA4-ISO-STATUS.md` for details.

## Bass Armstrong (PRIORITY #1)
Owner's direct order: Bass is the base body for **Vain Abel Elias** (the Kane-based character).

### Model
- **File:** `models/bass-armstrong/DOA5_Bass_Armstrong_Costume_1.zip` (20MB)
- **Source:** DOA5 (GTAinside port, verified real model data)
- **Format:** DFF/TXD (RenderWare) + PNG textures
- **Variants:** 4 (Bandana on/off × Glasses on/off)
- **Note:** DOA6 Bass model not found publicly. DOA4 ISO extraction will provide authentic DOA4 Bass when tooling is available.

### Moveset
- **File:** `movesets/bass-armstrong/BASS-MOVELIST.md` (278 lines)
- **Content:** Complete movelist reference — strikes, throws, holds, strings, specials with inputs and damage
- **Key moves:** Bass Lariat, Reverse Power Bomb, Bass Bomb, Powerslam, Manhattan Driver, Buffalo Rampage (Power Blow)
- **Note:** Chokeslam and Tombstone to be grafted on (not in Bass's native moveset)

### Vain Abel Integration
- **Default attire:** Owner's Tripo model (Vain Abel)
- **Alt attires 1-4:** Bass variants (to be reskinned in black/purple)
- **WH Canon:** Mortal lost soul (one of the twelve, not of the nine). Trial: being purified of the monster.
- See `~/memory/people/kane.md` for full character bible.

## Directory Structure
```
teardown/dead-or-alive-4/
├── README.md (this file)
├── DOA4-ISO-STATUS.md (ISO verification + extraction blocker)
├── models/
│   └── bass-armstrong/
│       └── DOA5_Bass_Armstrong_Costume_1.zip
├── movesets/
│   └── bass-armstrong/
│       └── BASS-MOVELIST.md
├── stages/ (pending ISO extraction)
├── audio/ (pending ISO extraction)
└── ui/ (pending ISO extraction)
```

## Next Steps
1. Acquire/build Xbox 360 XGD extraction tool
2. Extract all character models from DOA4 ISO
3. Extract all movesets from DOA4 ISO
4. Extract stages, audio, UI
5. Wire DOA4 costume customization into WH Create Fighter
