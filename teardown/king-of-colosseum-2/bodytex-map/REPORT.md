# KoC2 Body Texture Mapping — REPORT

**Status: CRACKED and content-verified.** Deliverable: [`mapping.json`](mapping.json) (all 155 manifest wrestlers, variant 0, plus the slot table and TBP0 map).

## The formula

```
file = base[slot] + count[slot] * part_id + sub
```

`part_id` = the appearance part id from the roster DB (= u16 at table-2010 record offset +4). `sub` = index within the part's file group. R/L pairs (knee/elbow/hand) are one file each, interleaved: R = base_R + 2·id, L = base_L + 2·id (the "count 2" is the interleave stride).

| slot | category | base | count | sub → content (dims) |
|------|----------|------|-------|----------------------|
| 2 | chest | 9854 | 4 | 0 torso front 128×128 · 1 torso back 128×128 · 2 R upper arm 64×64 · 3 L upper arm 64×64 |
| 3 | waist | 11300 | 3 | 0 hips 128×128 · 1 R thigh 128×64 · 2 L thigh 128×64 |
| 4 | feet | 13007 | 3 | 0 R foot 128×128 · 1 L foot 128×128 · 2 heels 64×64 |
| 5 | r_knee | 12491 | 2 | 0 R shin 128×64 |
| 6 | l_knee | 12492 | 2 | 0 L shin 128×64 |
| 7 | r_elbow | 10794 | 2 | 0 R forearm 64×64 |
| 8 | l_elbow | 10795 | 2 | 0 L forearm 64×64 |
| 9 | r_hand | 10898 | 2 | 0 R hand+fingers 64×64 |
| 10 | l_hand | 10899 | 2 | 0 L hand+fingers 64×64 |
| 0 | face | 5136 | 1 | (already solved by parent) |
| 11 | entrance_gear_type | 13412 | 6 | entrance gear, out of scope for in-ring renders |

16 files per wrestler = exactly the 16 distinct TBP0s in a body .mdl. Block accounting is exact: chest 234×4 = 9854–10789 (elbows start 10794), waist 397×3 = 11300–12490 (knees start 12491), knees 258×2 = 12491–13006, feet 135×3 = 13007–13411 (slot 11 starts 13412), elbows 52×2 = 10794–10897, hands 201×2 = 10898–11299 (waist starts 11300).

## ELF evidence (SLPM_656.02)

- Base table at vaddr **0x32FC08** (file offset 0x230c08): slot → base. Slot 0 = 5136 (face — confirms the parent's formula), 2 = 9854, 3 = 11300, 4 = 13007, 5 = 12491, 6 = 12492, 7 = 10794, 8 = 10795, 9 = 10898, 10 = 10899, 11 = 13412, 12–18 = 15968–16006.
- Count table at **0x32FC58**: slot → count/stride: 2:4, 3:3, 4:3, 5–10:2, 11:6, 12–18:1.
- **0x107ea8(slot, part_id)** returns `base[slot] + part_id` (delay-slot `addu` at 0x107ecc verified by hexdump). It also computes `mult(part_id, count)` — but the product is dead: the LO result is never read (no `mflo` anywhere near 0x107000–0x109000; word 0x00a32818 hand-decoded as MULT). See "open puzzle" below.
- **0x106d78** returns `5·a0 + 65·a1 + a2`; **0x106d98** returns `2·(…)+5564` (body file formula); **0x106e68** returns `2·(…)+7254`.
- Driver **0x10d7c0** (match path; sole caller 0x10a020) copies the 0x70-byte appearance struct to `0x3fcd70 + index·0x70`, calls body loader 0x106dc0, face loader 0x106cc0, costume loader 0x106e98, the 0x106fb8 accessories loop (slots 0–13), and 0x107f40/0x108010/0x1080b0 for slots 2–18.
- **0x107f40 / 0x107ed0 / 0x108010 / 0x1080b0** call 0x107ea8, store the result at struct+0x200+slot·4, and load that ONE file via **0x28b178(2, dest, index, 0)** (verified by full disassembly; entry = file table + index·16).
- **0x106fb8** accessories: files from `14018 + 65·slot + 5·body_type + body_size` are small **.mdl model** files (verified: file 14020 starts with VIFcode bytes, 1792 bytes, tim2.py fails on them), not textures — out of scope.
- Patch site **0x294058(model, tex0_64)**: sets ALL packets' TEX0 to one value. Patch site **0x294218(model, s1, s2)**: REBASES TBP0/CBP per packet (`new = old − 0x1a40 + 0x28e438() + s1`); if s2==1 writes word 9 = 0x302E4000, if s2==2 writes 0x303E4000. So .mdl TBP0s are RELATIVE to a per-model VRAM base (0x1a40); the same numeric TBP0 in a face vs a body file is NOT the same texture.
- Slot → appearance category (from driver $s1 offsets + rosterdb.py APPEAR table; $s1 = variant+0xc0): 0 face (+0xc6), 2 chest (+0xd6), 3 waist (+0xf4), 4 feet (+0x106), 5 r_knee (+0xfa), 6 l_knee (+0x100), 7 r_elbow (+0xdc), 8 l_elbow (+0xe2), 9 r_hand (+0xe8), 10 l_hand (+0xee), 11 entrance_gear_type (+0x114). Belt (+0x128) → slots 15/17; options (+0x129) → slot 16.

## Section → texture (body .mdl; TBP0 = word4 & 0x3FFF)

Verified identical across body files 5568 (Nakamura), 5664 (Liger), 5906 (Saito, special_gear 2) — 40 sections, same TBP0s. Front/back confirmed by packet-normal analysis (KoC2 coords, −z = front): TBP0 0x1bb4 packets avg normal z = −1.00 (FRONT), 0x1bf8 = +1.00 (BACK).

| TBP0 | part / sub | sections | body part |
|------|-----------|----------|-----------|
| 0x1a44 | waist 0 | 3, 7 | hips |
| 0x1a88 | waist 2 | 4 | L thigh |
| 0x1b28 | waist 1 | 8 | R thigh |
| 0x1aac | l_knee | 5 | L shin |
| 0x1b4c | r_knee | 9 | R shin |
| 0x1ad0 | feet 1 | 6 | L foot |
| 0x1b70 | feet 0 | 10 | R foot |
| 0x1b14 | feet 2 | 6, 10 | heels (both feet; packets normal +z, rearmost) |
| 0x1bb4 | chest 0 | 11, 12, 13, 26 (+39*) | torso front |
| 0x1bf8 | chest 1 | 11, 12, 13, 26 (+39*) | torso back |
| 0x1c3c | chest 3 | 14 | L upper arm |
| 0x1c78 | chest 2 | 27 | R upper arm |
| 0x1c50 | l_elbow | 15 | L forearm |
| 0x1c8c | r_elbow | 28 | R forearm |
| 0x1c64 | l_hand | 16–25 | L hand+fingers |
| 0x1ca0 | r_hand | 29–38 | R hand+fingers |

\* Sec 39 (neck) uses 0x1bb4 (front) on 5568/5906 but 0x1bf8 (back) on 5664 — read it from each body .mdl.

## Verification evidence (all decoded with kactusken tim2.py and eye-checked)

**Nakamura** (chest 73, waist 226, knees 154, feet 57, hands 186, elbows 0): 10146–10149 bare torso front/back + skin details ✓; 11978–11980 gray/silver long tights ✓; 12799/12800 matching gray knee pattern, L/R mirrors ✓; 13178–13180 orange laced shoes ✓; 11270/11271 skin with red stripe (wristband) ✓; 10794/10795 plain skin ✓.

**Liger** (chest 42, waist 75, elbows 7): 10022/10023 red/white suit with horned mask emblem + gold medallion, front/back ✓; 10024/10025 red suit shoulder/sleeve panels ✓; 11525–11527 red/white/silver tights with black/gold waistband ✓; 10808/10809 red/white suit elbow textures ✓.

**Others**: chest 0 → 9854 bare torso ✓; 7 "Liger Paint" → 9882 black tiger-stripe paint ✓; 12 "Dislocation Taping" → 9902 torso with shoulder bandage ✓; 13 "Jamal Tank Top" → 9906 "EKIMO 3" shirt ✓; 14 "Torn One-Shoulder" → 9910/9911 white singlet ✓; 16 → 9919 torso + black "BEAR" trunks ✓; 158 "Kotaro T-Shirt" → 10487 "BIG MOUTH LOUD" shirt ✓; 18 "Plain Tank Top" → 9926–9929 black singlet + skin details ✓; 44 "Long-Sleeve Shirt" details → 10032/10033 white fabric ✓; waist 283 "Kashin Spats" → 12149 black "OGRE OGRE" waistband ✓; knee 77 "All Japan Jersey" → 12645/12646 red with black-white side stripe ✓; feet 19 "Kensuke Shoes 2" → 13064 black laced shoe ✓; elbow 1 "Elbow Pad" → 10796/10797 black pad band with skin above/below ✓; elbow 9 "Long-Sleeve Shirt" → 10812/10813 white fabric ✓.

**Killed hypotheses**: 9900+table-2010-row (already dead per parent; re-confirmed: face rows 380/97/167 are Bone Cry/Sano/Ishikari, not Liger/Mutoh/Muta); plain base+id (leaves 706 chest-block and 785 waist-block files unexplained; 10146 is beyond the plain chest range); companion-file map (dead per parent); sequential VRAM packing (dead per parent).

**Size-pattern confirmation**: chest block shows AACC size pattern (128×128, 128×128, 64×64, 64×64) repeating over 9854–10090; waist ABB (128×128, 128×64, 128×64); feet AAC. Index.csv decomp sizes: 17664 = 128×128, 9472 = 128×64, 5376 = 64×64.

**Flip tests**: waist subs (11526 vs 11527) and knee pair (12799 vs 12800) are exact mirrors ✓; feet subs (13178 vs 13179) and hand pair (11270 vs 11271) are NOT mirrors (genuinely different L/R designs). Generic skin detail files share sha256 052b569e… (9856, 9860, 9928, 10148 identical).

## Flagged ambiguities (NOT verified — check on the first color render)

1. **Within-group L/R** (waist subs 1/2, feet subs 0/1, chest subs 2/3): encoded R-first, following the R-before-L file convention (R slot bases are lower than L: R knee 12491 < L knee 12492, etc.). TBP0 order is the opposite (L before R), but the knee case proves file order and TBP0 order are independent. UV analysis shows L and R sections map the same anatomical landmarks to the same u (front-center → u=0.5 on both thighs), so symmetric designs are safe either way; only asymmetric details would read mirrored. If wrong, swap subs 1↔2 (waist), 0↔1 (feet), 2↔3 (chest details).
2. **Upper-arm vs forearm** (chest details vs elbow textures): encoded chest-details → upper arms, elbows → forearms, by elimination + outfit pairing: wrestlers pair matching chest and elbow parts (Liger suit 42/7, Chairman suit 155/51, Tenta tattoo 84/19), tank-top wearers have bare elbows (their chest details are generic skin), and Liger's chest details are shoulder/sleeve-cap shaped while the elbow pad is a band. The long-sleeve check (chest 44 details vs elbow 9) was inconclusive (both plain white fabric). If the first render shows sleeves on the wrong segment, swap.

## Open puzzle (does NOT block rendering)

0x107ea8 returns base+id, but the on-disk layout is base+id·count. The game provably loads the right textures (content-verified layout), so some later stage must expand the stored base+id into the group (e.g., a reader of struct+0x200[slot] computing base + (stored−base)·count) — that reader was NOT found. The mult in 0x107ea8 is dead code (possibly a leftover). The renderer uses the file layout directly and does not need the runtime path.

## Table 2010 structure (for reference)

25 groups, 4021 records, 32-byte records: +0 u32 string offset, +4 u16 = part id, +6 u16 = group index, +28 u32 = index within group. Groups: 0 face (429), 6 chest (234, rows 473–706), 7 r_elbow (52), 8 l_elbow (52), 9 r_hand (207), 10 l_hand (207), 11 waist (406), 12 r_knee (258), 13 l_knee (258), 14 feet (137). Row ≠ start+id for costume parts (records not sorted by id); rosterdb `part()` looks up by +4 == key.
