# Deploy split decision — 2026-10-26

Owner decision, 2026-10-26 ~19:10 CDT (tapped option in disc-cleaner chat):
split hosting is approved — **Pages shell + GLBs on Cloudflare R2**.

## What it replaces

The pending "what gets cut" question. Nothing is cut from the game,
only from the deploy: the game stays whole; the deploy set is split
between the Pages shell and R2-hosted GLBs.

## Context

- Deploy set is 5,969 MB vs the 1 GB GitHub Pages limit.
- Live site is frozen on the Oct 24 build until the split lands.

## Owner-only items

- Cloudflare R2 signup is owner-only (card rules).
- itch.io account/payout setup is still owner-only (separate item).

## Status

- Decision recorded here 2026-10-26. R2 signup and the split-deploy
  wiring are still to do; nothing about the game itself changes.
