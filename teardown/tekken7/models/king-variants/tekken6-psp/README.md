# King outfits — Tekken 6 (PSP)

## Status: BLOCKED — not extractable (documented 2026-10-13)
King's T6 outfits (P1/P2/P3/Suit/Beast per Tekken Wiki customization research) live in
the PSP ISO at `~/workspace/game-reverse-engineering/tekken6/tekken6-psp.iso` (816MB,
PR #14 merged to western-heart main), but character models/textures could NOT be
extracted: the model archives sit behind PSP encryption in EBOOT.BIN with encrypted
index files (`extracted/DINF_400.BIN`, `extracted/DATA401.IDX`).
Future path: PPSSPP decryption -> Namco archive RE -> GMO extraction (multi-day task).

What the T6 lane DID recover (in the ISO):
- `ending_kin.pmf` — King II story ending cinematic (H.264 480x272)
- Roster slot 20 `kin` = King II confirmed
- Customization system documented (the template for Western Heart customization)

## Free T6 King substitutes (model data, other sources)
- Pedro-Croft T6 King 2P XPS — DeviantArt, login-gated (see ../deviantart/README.md)
- wakind King (wrestler) TK6 — DeviantArt, login-gated (see ../deviantart/README.md)
- DavidChikardi T5 King (1p,2p) — PS2-era predecessor geometry (see ../deviantart/README.md)
