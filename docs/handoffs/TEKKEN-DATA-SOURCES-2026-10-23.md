# Tekken Data Sources — Handoff (2026-10-23)

Where every agent pulls Tekken data from. Use these sources, don't re-derive.

**Exact commands, repo URLs, pinned commits and the chunked Steam pull:** `docs/team/TEKKEN-DATA-SOURCES.md`.

## Tekken 8 full movesets — Kaiutzi21 public repo
- **What:** Complete T8 movelists. PR #859 merged 2026-10-23.
- **Landed:** Lee (2,319 moves → Purple Rain), Law (→ Buffalo Bill), King (→ Pantera),
  Armor King (→ Yukihyo), Paul (→ Gyou).
- **Source:** https://github.com/Kaiutzi21/Tekken8Movesets (CC BY-NC 4.0, private use only), in `teardown/community/tekken8/movesets/kaiutzi21/`. Upstream also has Bryan, Clive, Fahkumram, Heihachi, Jin, Lars, Miary Zo, Raven, Shaheen, Steve, Yoshimitsu and Unknown, which are not pulled yet. Bob and Alisa are not in T8.
- **Note:** Movesets only — no animations, stages, or models. Those come from T7 Steam files.

## Tekken 7 frame data — RBNorway
- **Source:** https://github.com/pbruvoll/rbnTekkenFrameData (no license, private reference), in `teardown/community/tekken7/framedata/rbnorway/csv/`.
- **What:** Per-character frame data for the full T7 roster.
- **Landed:** Bob (→ Burger), Alisa (→ Cape Jones), plus full roster.
- **Use for:** Hit feel numbers — startup, active, recovery, damage. Crew work from
  these files, never ask the user to tune numbers.

## Tekken 7 full files — Steam (user's account)
- **Method:** `tools/depot-pull/depot-pull.sh` — DepotDownloader, pak-only pulls.
  NEVER download a full game; pull per-file and delete raws after extraction.
- **Status:** Grok has T7 downloaded (~20GB) on Grok's box (`/workspace/tools/depotdl`, Steam login token saved there; other machines need the owner's own sign-in, and credentials are never committed), unpacking
  one file at a time (Alisa, Lee, Bob first), saving to GitHub, deleting raws after.
- **Note:** T7 `.uasset`/`.umap` files have per-asset encryption (the decrypter is on Grok's box at `/workspace/tools/extract-t7/t7_decrypt.py`), which contradicts the "no encryption" line in PR #858.
- **Provides:** Animations, stages, models, HUD, announcer — everything the public
  repos don't have.

## Tekken 7 HUD + announcer
- Grok located the HUD and announcer call files. Browser pull once disk frees up. Spriters Resource and Sounds Resource are behind Cloudflare, so curl gets a 403; URLs are in `docs/tech/COMMUNITY-SOURCES.md` #3–6.

## WWE 2K games — Steam (user's account)
- **Status:** Ownership list being written to `docs/tech/STEAM-LIBRARY.md`.
- **Split:** Muse pulls WWE 2K on the VM (disk space available) → `teardown/wwe2k/`.
  Grok takes remaining titles after T7 unpack frees disk.
- **Pull:** models, movesets, animations, creation-suite files.

## Rules for all agents
- Tekken source priority: T5 → T6 → T7 → TTT2 first. T3 is FALLBACK ONLY.
- Owner order pt128u: pull from T8 first, with T7 as backup. Every T3 use gets logged.
- Log every source (`docs/tech/COMMUNITY-SOURCES.md` + `SOURCE_COMMIT.txt`). No hand-made content. Private repos only. Run gitleaks before every push.
- Moveset Source Law is code (`game/data/moveset-library/claimed-map.json`).
- Tekken names stay in technical files, NEVER in canon/bios.
- Verify by playing. Proof or it didn't happen.
