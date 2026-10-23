# Urban Reign — hand/arm reference

Source: teardown/urban-reign/ (PPK-FORMAT.md, VGS-FORMAT.md, motion/*.gyu).

## Findings

- PPK geometry carries bone index data (0xae00 sections; byte sequences at
  0x017d) and identity-quaternion bind poses (0x0660) — the skeleton exists but
  the bone map (names, hierarchy) is NOT yet decoded.
- Motion files (general_30frame.gyu, general_normal.gyu, general_weapon.gyu,
  gyuindex.bin) are in the repo; the .gyu bone-track format is not yet decoded.
- Weapon motions exist (general_weapon.gyu) — the future source for
  weapon-grip hand poses once the bone map is decoded.

## Takeaway

- No hand/finger bone names extractable today. Urban Reign is a FUTURE source
  for grappling hand/arm poses (its whole design is grappling), pending bone-map
  decode of the PPK/gyu formats.
