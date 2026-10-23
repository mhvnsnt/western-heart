# Tekken Data Sources — Handoff (2026-10-23)

Where every agent pulls Tekken data from. Use these sources, don't re-derive.

## Tekken 8 full movesets — Kaiutzi21 public repo
- **What:** Complete T8 movelists. PR #859 merged 2026-10-23.
- **Landed:** Lee (2,319 moves → Purple Rain), Law (→ Buffalo Bill), King (→ Pantera),
  Armor King (→ Yukihyo), Paul (→ Gyou).
- **Note:** Movesets only — no animations, stages, or models. Those come from T7 Steam files.

## Tekken 7 frame data — RBNorway
- **What:** Per-character frame data for the full T7 roster.
- **Landed:** Bob (→ Burger), Alisa (→ Cape Jones), plus full roster.
- **Use for:** Hit feel numbers — startup, active, recovery, damage. Crew work from
  these files, never ask the user to tune numbers.

## Tekken 7 full files — Steam (user's account)
- **Method:** `tools/depot-pull/depot-pull.sh` — DepotDownloader, pak-only pulls.
  NEVER download a full game; pull per-file and delete raws after extraction.
- **Status:** Grok has T7 fully downloaded (~20GB) on the user's machine, unpacking
  one file at a time (Alisa, Lee, Bob first), saving to GitHub, deleting raws after.
- **Provides:** Animations, stages, models, HUD, announcer — everything the public
  repos don't have.

## Tekken 7 HUD + announcer
- Grok located the HUD and announcer call files. Browser pull once disk frees up.

## WWE 2K games — Steam (user's account)
- **Status:** Ownership list being written to `docs/tech/STEAM-LIBRARY.md`.
- **Split:** Muse pulls WWE 2K on the VM (disk space available) → `teardown/wwe2k/`.
  Grok takes remaining titles after T7 unpack frees disk.
- **Pull:** models, movesets, animations, creation-suite files.

## Rules for all agents
- Tekken source priority: T5 → T6 → T7 → TTT2 first. T3 is FALLBACK ONLY.
- Moveset Source Law is code (`game/data/moveset-library/claimed-map.json`).
- Tekken names stay in technical files, NEVER in canon/bios.
- Verify by playing. Proof or it didn't happen.
