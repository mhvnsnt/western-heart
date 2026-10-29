# Tekken 5 (PS2) — UI Asset Extraction Status

**Updated:** 2026-10-23 (UI sweep)
**Status:** 🟡 IN PROGRESS — full ISO download running (sibling lane)

## Acquisition

- **ISO:** `SLUS_210.59.Tekken 5.ISO` — 4,039,974,912 bytes (3.76 GiB), USA SLUS-21059
- **Source:** Internet Archive `slus-210.59.-tekken-5`
  (https://archive.org/download/slus-210.59.-tekken-5/SLUS_210.59.Tekken%205.ISO)
- **Checksums:** md5 `5bce17ccabacea46d621d195c4600ebb`,
  sha1 `97ca517151229bc1c6a58396ccf470f91676f047`
- **Download:** 16-segment parallel fetch via `~/workspace/tekken5-extract/dl_segments.sh`,
  running 2026-10-23 ~20:06 UTC (sibling lane — do not duplicate)
- **Releases:** `tekken5-ps2-v1` (acquisition record), `tekken5-ps2-extract-v1`
  (extraction payloads record)

## Where the UI lives

PS2 Tekken 5 menu art = **TIM2** textures inside the game data files.
`~/workspace/tekken5-extract/t5_survey.py` fingerprints TIM2/VAGp/PSS/ELF —
run it against the joined ISO to inventory every UI texture by offset.

**Already in-game:** `game/assets/ui/` holds 6 TIM2-extracted PNGs
(`tim_0947_off_001E6950.p000.png` etc.) + `title-bg.png` (landed via PR #811,
2026-10-23) — proof the TIM2→PNG path works for T5 menu art.

## UI pull list (once ISO lands)

Title/menu background art, character select portraits (32 fighters),
versus screen art, HUD elements, font glyphs (TIM2), navigation sounds
(VAGp/PS-ADPCM). T5's menus are the closest pre-T7 Tekken feel reference and
the Devil Within mode's UI lives here too.
