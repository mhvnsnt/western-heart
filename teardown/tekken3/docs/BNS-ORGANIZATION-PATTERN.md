# Tekken 3 BNS Organization Pattern — Character Models & Textures

## The Pattern (verified with King)

### Character Model Records
- BNS IDs: `71 + (name_index × 8)` for P1, `+4` for P2
- Example: PAUL(idx 0)→71/75, LAW(idx 1)→79/83, LEI(idx 2)→87/91, **KING(idx 3)→95/99**

### Name Table Order (from SLUS_004.02 @ 0x129ac)
```
0: PAUL       → BNS 71/75
1: LAW        → BNS 79/83
2: LEI        → BNS 87/91
3: KING       → BNS 95/99  ← the real King
4: YOSHIMITSU → BNS 103/107
5: NINA       → BNS 111/115
6: HWOARANG   → BNS 119/123
7: XIAOYU     → BNS 127/131
8: EDDY       → BNS 135/139
9: TIGER      → BNS 143/147
10: JIN       → BNS 151/155
11: JULIA     → BNS 159/163
12: KUMA      → BNS 167/171
13: PANDA     → BNS 175/179
14: BRYAN     → BNS 183/187
15: HEIHACHI  → BNS 191/195
16: OGRE      → BNS 199/203
17: MOKUJIN   → BNS 207/211
18: GUN JACK  → BNS 215/219
19: GON       → BNS 223/227
20: ANNA      → BNS 231/235
```

### Texture Blocks
- Each character's textures are stored in the **~445KB gap AFTER their P1 model record**, before their P2 record
- King (BNS 95): 59 textures (TIM IDs 6213–6271) in gap 11183336–11689984
- Paul (BNS 71): 59 textures in gap after his model
- Pattern holds for all characters

### ⚠️ CORRECTION: Earlier Misidentification
A previous worker identified BNS 87 as King. **BNS 87 is actually LEI** (index 2).
The "King" model rendered earlier (king_full_front.png) is actually Lei Wulong.
The real King is BNS 95. His textures (jaguar spots, blue pants, jaguar mask)
confirm this unambiguously.

### King's Texture Set (BNS 95, TIMs 6213–6271)
- **Jaguar mask:** spotted fur texture, jaguar face with open mouth
- **Blue pants/tights:** dark blue fabric textures
- **Purple trunks:** with gold design
- **Gold boots:** yellow/gold boot textures
- **Skin:** chest, arms, hands (wrestler physique)
- **Effects:** gold energy sprites (King's moves)

Location: `~/workspace/game-reverse-engineering/tekken3/renders/king/textures/real_king/`

### How to Find Any Character's Textures
1. Look up character index in name table (SLUS_004.02 @ 0x129ac)
2. BNS P1 ID = 71 + (index × 8)
3. Get P1 model offset + size from model-inventory.json
4. Textures are TIMs in the gap between P1 end and P2 start
5. Extract with palette from tim-inventory.json CLUT data

## Motion Banks (divmot) — verified 2026-10-12
- BNS IDs 280–300 = divmot types 0–20 (ID 279 = divmot99 common bank). ID 283 = type 3 = **King** (confirmed via n0madic ai.md hooks table; header byte 0x01 == 3).
- BNS table offsets are SECTOR numbers: byte_offset = table_offset × 2048 into TEKKEN3.BNS.
- Extracted: `animations/divmot03_king.bin` (403,732 bytes, 652 move rows).
