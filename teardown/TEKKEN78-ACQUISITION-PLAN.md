# Tekken 7 + 8 Full Game — Acquisition Plan (PREPARED ONLY)

**Owner auth (seq 77036–77080):** up to $10 spend authorized. Account creation is
the OWNER's manual step — agents do not create accounts or make purchases.

## Why
Tekken 7 is the primary chimera base (modern models, 51-fighter roster, 34 stages,
customization system) and its 47GB were never acquired. Tekken 8 adds the newest
models/variants (King variants already partially pulled via PR #54/#59).

## Owner steps (his hands)
1. Create/verify the store account(s) for the purchase source he chooses
2. Complete the purchase (≤$10 authorized)
3. Tell the agent the download is ready

## Agent pipeline once the download exists (no VM disk — 47GB won't fit)
1. Download straight to TeraBox Premium (5TB trial, expires 2026-10-20 — renew first)
   via browser chunked upload → `/western-heart/tekken7/` (see `TERABOX-MANIFEST.md`)
2. Pull back in batches that fit disk → extract with UModel/repak/FModel
   (tools already at `teardown/tekken7/tools/`)
3. Models → `teardown/models/tekken7/`; stages → arena inventory; customization
   data → `customization/`; movesets → `moveset-library/`
4. Everything via branch → PR → merge; hashes in `teardown/TEARDOWN-SOURCES.md`

## Notes
- TeraBox Remote Upload is GONE from the website — chunked browser upload is the path.
- Do NOT start this pipeline until the owner confirms the purchase/download.
