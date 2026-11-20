# Soulcalibur II (Xbox) — hand/arm reference (weapon grips)

Source: teardown/soulcalibur-2/XBOX-EXTRACTION-REPORT.md; release
soulcalibur2-xbox-extract-v1.

## Findings

- 577 named animation files extracted (StCr_3A, pStd_6K, etc.) at v982
  @0x1372d800 — the animation bone data EXISTS but the bone-track format RE is
  open work.
- Character map covers the full roster incl. Yoshimitsu (CHARACTER-MAP.md).

## Takeaway

- No weapon-grip hand poses extractable today — this is the single most relevant
  future source for Scimitar's blade-fused-arm grip poses (weapon fighter,
  full anim set extracted, format decode pending).
- Next step: decode the SC2 animation bone-track format from the extracted
  anim files, then sample grip frames per weapon type.
