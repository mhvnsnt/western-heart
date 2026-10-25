# Tekken 6 (PSP) — UI Asset Extraction Status

**Updated:** 2026-10-23 (UI sweep)
**Status:** 🔴 BLOCKED — game data AES-encrypted (DATA401); local ISO is a trimmed stub

## Blocker

All Tekken 6 PSP game assets — models, textures, **UI/menu art, character
portraits, customization assets** — live inside `USRDIR/DATA401`
(384MB data region), which is AES-encrypted (entropy 7.99/8.0). Key hunt is
tracked in `../T6-KEYHUNT-REPORT-2026-10-22.md`; decrypt paths (PPSSPP live
dump, MIPS RE of decrypted EBOOT) are in `../TEARDOWN.md`.

## Local ISO is a trimmed stub (verified 2026-10-23)

`~/workspace/t6work/tekken6-psp.iso` (244,022,601 bytes, valid PSP GAME
ISO9660) has **stale directory records**: `DATA401.IDX` (extent 230240),
`DINF_400.BIN` (extent 230192), all `movie/*.pmf`, and `modules/*.prx`
point **beyond end-of-file** (119,151 sectors). Only `PSP_GAME/` shell files,
`SYSDIR/` (EBOOT/BOOT), and `UPDATE/` are actually present. The IDX/index and
the entire data region are not recoverable from this file.

A sibling lane is downloading the **full** `tekken6-psp.iso` from release
`tekken6-psp-v1` (observed 2026-10-23 ~19:32 UTC). Even the full ISO still
needs the DATA401 decrypt breakthrough before any UI comes out.

## Where the UI lives (sourced, not guessed)

- Decrypted EBOOT (`../decrypted/EBOOT.DECRYPTED.ELF`) exports the PAC reader
  symbols: `packdatas_t`, `ReadInfo`, `ktRead`, `openPac` — UI textures load
  through the same DATA401 PAC system as models (per `../TEARDOWN.md`).
- Texture format: TIM2/GIM family, same encryption barrier as models
  (`../TEARDOWN.md`: "Textures — Likely TIM2/GIM format, same encryption barrier").

## Already landed

- `teardown/tekken6/ui/psp_ICON0.png`, `psp_PIC1.png` — PSP system icons
- `teardown/tekken6/videos/` — 46 PMF cinematics (release `tekken6-endings-v1`)

## UI pull list (for when DATA401 decrypts)

Character select portraits (40 fighters), versus screen art, stage select art,
customization menu assets, HUD elements. Phone-scale rule applies: T6 PSP ran
at 480×272 — its UI art is already close to phone-target resolution, which
makes it a strong menu reference once decrypted.
