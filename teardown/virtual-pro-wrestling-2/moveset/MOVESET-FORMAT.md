# VPW2 bit-packed moveset format (CRACKED 2026-11-19)

Reverse-engineered from the VPW2 ROM code (main segment) and verified by
decoding all 98 wrestler movesets + 3 edit-mode movesets: **101/101 decode
with zero invalid indices and zero trailing garbage.**

## The code (ROM addresses, RAM = ROM + 0x7FFFF400)

| Function | RAM | ROM | Role |
|---|---|---|---|
| Moveset encoder | 0x80005578 | 0x6178 | writes bitstream from 292×6B move array |
| Moveset decoder | 0x8000632C | 0x6F2C | reads bitstream into 292×6B move array |
| Bit-writer | 0x80004D60 | 0x5960 | MSB-first bitstream writer |
| Bit-reader | 0x80004F64 | 0x5B64 | MSB-first bitstream reader |
| Params encoder | 0x8000593C | 0x653C | 50-case switch; params format (see below) |
| Params decoder | 0x80006608 | 0x7208 | 50-case switch; params format (see below) |
| Match setup (seg3) | 0x8014CFAC | 0x14775C | in-match copy of the decoder + damage load |

## Tables (all in-repo under `moveset/`)

| File | ROM offset | Content |
|---|---|---|
| `bitpacking_main.bin` | 0x3E530 (268 B) | 134 u16: bit width per menu item (0..132 + terminator 0) |
| `bitpacking_movegroup_wrestling.bin` | 0x3D4E0 (1530 B) | 152 records + FFFF terminator |
| `bitpacking_movegroup_combo.bin` | 0x3DADC (1550 B) | 154 records + FFFF terminator |
| `bitpacking_movegroup_shoot.bin` | 0x3E0EC (1080 B) | 107 records + FFFF terminator |
| `master_movemods.bin` | 0x3E748 (3908 B) | 133 groups of u16 "mod values", FFFF-separated |
| `master_movemods_first_entries.bin` | 0x3E63C (266 B) | 133 u16: first nonzero value per group |
| `master_movemod_pointers.bin` | 0x3F68C (532 B) | 133 u32 RAM pointers into master_movemods |
| style table (ROM 0x3E524, 12 B) | 0x3E524 | 3 u32: movegroup table pointers (wrestling/combo/shoot) |

A movegroup record is 10 bytes: `u16 move_id, u16 item[4]` — the move and
up to 4 menu items (slots) it may be assigned to (0 = unused slot).
Move IDs run 1..287; the decoder zeroes a 292-entry output array.

`bitpacking_main[i] == ceil(log2(count_i))` for all 133 groups, where
`count_i` is the group size in file 0x0061 (`edit_mode_moves.json`) —
verified 133/133. The main table is the bit width of the mod-index field
for menu item i.

## Bitstream layout

MSB-first within each byte; the first bit read is the MSB of the value.
The bitstream is read record by record, in movegroup-table order. For each
record:

```
maxbits = max(bitpacking_main[item] for item in record.items if item != 0)
read (maxbits + 5) bits -> V
mod_index = V & ((1 << maxbits) - 1)      # low maxbits bits
slot      = (V >> maxbits) & 3            # next 2 bits
flags     = (V >> (maxbits + 2)) & 7      # top 3 bits
item      = record.items[slot]
mod_value = MasterMoveMods[item][mod_index]   # u16, multiple of 10 (or 0)
```

Decoded move record (6 bytes, indexed by move_id): `{u16 mod_value,
u8 flag2, u8 flag3, u8 flag4, u8 pad}`. `mod_value == 0` means the slot is
unset for this wrestler.

Bit totals (verified against file sizes):

| Style | Records | Bits | Bytes (ceil) | File size |
|---|---|---|---|---|
| wrestling | 152 | 1406 | 176 | 176 |
| combo | 154 | 1426 | 179 | 180 (+1 zero byte) |
| shoot | 107 | 999 | 125 | 125 or 126 (+1 zero byte) |

File length identifies the style: 176 = wrestling, 180 = combo,
125/126 = shoot. (Style also lives in the params; see below.)

## What the mod value means

The mod value is an index into two parallel u16 tables (raw files 0x0278
and 0x0279, 16160 entries each, decoded in `raw/`):

- `raw/0278.bin[mod_value]` = **AnimID** (0..4812) — the move's animation.
  AnimID maps to `move_anim_map.json` (name, category, file_id, .npy,
  Toki1 windows). File ID = AnimID + 0x2056.
- `raw/0279.bin[mod_value]` = **damage-table index** (0..2301) into file
  0x0277 (`move_damage.json`: damage, spirit gain/drain, attack/defense
  params, head/body/arm/leg/speed damage).

Both tables are sparse: only multiples of 10 (the values MasterMoveMods
can produce) carry data. The seg3 match-setup code (0x8014D308–0x8014D38C)
loads file 0x0277 and 0x0279 and copies the 32-byte damage record per move
— confirming the chain in live game code.

The 3 flag bits feed per-move state bytes in the match struct (seg3
0x8014D38C–0x8014D474): flag2/flag3 set bytes at +0x4ACA/+0x4AC9 to 3 when
set (0 when clear); flag4 ORs 0x8000 into a u32 at +0x4ADC. Exact gameplay
meaning of the flags is still open (likely finisher/signature/unlocked
markers — needs in-match observation).

## Verification

- 98/98 wrestler movesets + 3/3 edit movesets decode with 0 invalid
  indices (every mod_index inside its MasterMoveMods group) and all-zero
  trailing padding bits.
- Spot-check (Misawa, id4 0001, combo): Tiger Driver (Front Strong
  Grapple, dmg 25), Tiger Suplex (Back Strong, dmg 35), Tiger Suplex '85
  (Back Special, dmg 40), Apron Powerbomb (dmg 45) — his real moves.
- 10,572/10,765 decoded move animations resolve to a named move in
  `move_anim_map.json` (98.2%); the rest hit the 734 unlabeled anims.

## Decoded output

- `moveset/decoded_movesets.json` — all 98 wrestlers: per move_id the
  menu item, slot, mod value, flags, AnimID, move name, category, file
  ID, .npy clip, Toki1 windows, and damage record fields.
- `tools/vpw2_moveset.py` — the decoder (run it to re-verify: prints
  `valid: 98/98`).
- `tools/decode_all_movesets.py` — regenerates `decoded_movesets.json`.

## Params files (30 bytes) — PARTIALLY decoded

The params decoder (0x80006608) unpacks the 30-byte file into 50 u16
parameters via a 50-case switch (jump table at RAM 0x8005A800). The
fighting style is among them (seg3 0x8014D1B8 reads style bits from the
wrestler struct at +0x30 to pick the movegroup table). The full 50-param
map is still open — see `tools/vpw2_params.py` (WIP) for the current
state. Moveset decoding does not depend on it (style comes from file
length, cross-checked against the edit-mode files).
