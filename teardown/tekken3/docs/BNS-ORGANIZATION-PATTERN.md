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
- NOTE: BNS ID 295 (type 15, Mokujin) has size 0 in this local disc image — divmot15 is absent locally.
- Extracted: `animations/divmot03_king.bin` (403,732 bytes, 652 move rows).

### divmot type → character map (verified 2026-10-13)
Derived from n0madic `docs/research/bns-original-index.md`: each divmotNN sits in the
4th slot of its character's model group (kmd, vh, arc, divmot), cross-checked
against the AI hooks table (`ai.md`: bank 0=Paul, 3=King, 4=Yoshimitsu, 6=Hwoarang,
10=Julia, 13=Heihachi, 14=Ogre, 16=Gun Jack, 19=Gon). Header byte 0x01 of each
extracted bank == its type. Every extracted bank's SHA-256 matches n0madic's
original-disc index exactly.

| Type | Character | Local BNS ID | Extracted file | Size | SHA-256 (n0madic) |
|---:|---|---|---:|---|---|
| 0 | Paul | 280 | divmot00 (not yet extracted) | 313472 | 06f6447a… |
| 1 | Law | 281 | divmot01 (not yet extracted) | 313308 | 14f83938… |
| 2 | Lei | 282 | divmot02 (not yet extracted) | 318524 | bd795779… |
| 3 | King | 283 | divmot03_king.bin | 403732 | 8ae24919… |
| 4 | Yoshimitsu | 284 | divmot04_yoshimitsu.bin | 327920 | f99859bc… |
| 5 | Nina | 285 | divmot05 (not yet extracted) | 333384 | 50430e78… |
| 6 | Hwoarang | 286 | divmot06 (not yet extracted) | 312268 | d0b5b43a… |
| 7 | Xiaoyu | 287 | divmot07_xiaoyu.bin | 326972 | cd558158… |
| 8 | Eddy / Tiger | 288 | divmot08 (not yet extracted) | 336652 | 0383ddb2… |
| 9 | Jin | 289 | divmot09_jin.bin | 328396 | 5ac9fef4… |
| 10 | Julia | 290 | divmot10 (not yet extracted) | 267924 | d4c8ce91… |
| 11 | Kuma / Panda | 291 | divmot11 (not yet extracted) | 285432 | 77804b1f… |
| 12 | Bryan | 292 | divmot12_bryan.bin | 264372 | 07e00019… |
| 13 | Heihachi | 293 | divmot13_heihachi.bin | 268796 | 9567b139… |
| 14 | Ogre / True Ogre | 294 | divmot14 (not yet extracted) | 315396 | f0c14b35… |
| 15 | Mokujin | 295 | — MISSING locally (size 0) | 127368 | 5cead15f… |
| 16 | Gun Jack | 296 | divmot16_gunjack.bin | 316944 | 7f35c9fb… |
| 17 | Anna | 297 | divmot17 (not yet extracted) | 314684 | 16886320… |
| 18 | Dr. Bosconovitch | 298 | divmot18 (not yet extracted) | 332372 | 130ee660… |
| 19 | Gon | 299 | divmot19 (not yet extracted) | 322196 | d28e5e77… |
| 20 | Forest Law | 300 | divmot20 (not yet extracted) | 106948 | 0aaf8799… |
| 99 | Common bank | 279 | divmot99 (not yet extracted) | 240468 | 2a8c754a… |
