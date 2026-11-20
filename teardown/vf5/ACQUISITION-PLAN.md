# VF5 R.E.V.O. World Stage — Acquisition & Teardown Plan

**Lane:** `wh-vf-newest` | **Created:** 2026-10-14 (subagent 03747efc)
**Status:** RESEARCHED — version picked, download BLOCKED (see below)

---

## Version picked

| Field | Value |
|---|---|
| **Game** | Virtua Fighter 5 R.E.V.O. World Stage (PC, Steam) |
| **Steam AppID** | 3112260 |
| **Depot** | 3112261 (`Virtua Fighter 5 R.E.V.O. World Stage`) |
| **Current build** | 24944148 (public, updated 10 Sep 2026; manifest 6891312408572027293, build 22258875 dated 9 Mar 2026) |
| **Download size** | **12.69 GiB** (compressed, per SteamDB) |
| **Installed size** | **27.58 GiB** (1,430 files) |
| **Fighter count** | 19 (same roster as vanilla VF5 teardown + FS additions: Jean Kujo, Taka-Arashi) |
| **Price** | Paid (~$30 on Steam). NOT a free title. |

### Why this version
- **VF6 does not exist as a playable game.** The new VF is officially *Virtua Fighter: Crossroads*, RGG Studio, releasing **2027** (revealed Summer Game Fest 2026). Nothing to pull.
- R.E.V.O. World Stage (PC, Jan 28 2025 base; World Stage update 2025–2026) is the **newest released** VF. PS5/Xbox builds (Oct 30 2025) and Switch 2 (Mar 25 2026) exist but **cannot be decrypted/extracted** on this VM (PS5 PKG keys unavailable; Switch 2 encryption not broken).
- PC build is the only extractable option: Dragon Engine `.par` archives, `.dds` textures, `.adx` audio, `.usm` cinematics.
- Size sanity: 12.69 GB download / 27.58 GB installed — reasonable per owner's "most decent sized" guidance (far smaller than SCVI/DOA6-class pulls).

### What's NEW vs the vanilla VF5 lane (already 100%)
- Rebuilt Dragon Engine character models (4K textures) for all 19 fighters
- **Jean Kujo (Karate) + Taka-Arashi (Sumo)** — FS-era fighters NOT in the vanilla PS3 dump; priority pull
- New/rebalanced movesets (first balance adjustments in 13 years, ver 2.0, Dec 2024)
- New stage themes/models, new soundtrack, revamped UI
- 16-player custom tournament/league data, World Stage single-player mode content

---

## Blockers (BOTH must clear before download)

1. **Purchase required.** App 3112260 is a paid Steam title. Acquisition needs the
   owner's Steam account: buy on Steam via browser lane, then download with SteamCMD
   authenticated (`+login <user>`) or via the Steam client. No public dump exists
   (Archive.org: none; SteamDB depot 3112261 requires ownership).
2. **Disk space.** `/home/hatch` is at **85% (16 GB free)**. The pull needs ~12.7 GB
   download + ~27.6 GB install/extract ≈ **~28 GB peak**. Disk must be stored/moved
   to ≤75% FIRST (disk-space-guardian's save-then-clean cycle; owner law: store to
   TeraBox/GitHub before any cleanup).

---

## Download procedure (once unblocked)

SteamCMD with resume capability — SteamCMD resumes interrupted depot downloads
automatically on retry (manifest-level resume), satisfying RESUME-DON'T-REDOWNLOAD:

```bash
mkdir -p ~/workspace/game-reverse-engineering/vf5-revo/download
cd ~/workspace/game-reverse-engineering/vf5-revo/download
steamcmd +@sSteamCmdForcePlatformType windows \
  +login <steam_user> \
  +app_update 3112260 validate \
  +quit
# On interruption: re-run the SAME command — SteamCMD resumes from manifest state.
```

Checkpoint byte counts after each run: `du -sb` on the download dir into
`vf5-revo-download.log`.

---

## Extraction pipeline (after download)

Key file types per SteamDB depot 3112261 file list (1,430 files):

| Type | Count | Size | Contents | Tool |
|---|---|---|---|---|
| `.par` | 78 | **23.42 GiB** | RGG Dragon Engine archives — models, stages, moveset data | Yakuza/RGG modding tools (parless / RyuModManager / RGG par extractor) |
| `.usm` | 7 | 2.07 GiB | CRI Sofdec cinematics | vgmtoolbox / ffmpeg |
| `.adx` | 804 | 1.53 GiB | CRI ADX audio (BGM/SE/VO) | vgmtoolbox |
| `.dds` | 66 | 93.9 MiB | DirectDraw textures | any DDS reader |
| `.farc` | 52 | 130.8 MiB | Sega archives (legacy containers) | FarcPack / `tools/vf5-extract` |

Steps:
1. Verify depot build ID matches `24944148` (Sep 2026) or later.
2. Extract `.par` archives → per-fighter model dirs (`chara/` naming inside).
3. Extract `.adx` → BGM/VO; `.usm` → cinematics (World Stage story content).
4. Convert/import character models; diff roster vs vanilla lane (priority: Jean, Taka).
5. Extract stages + moveset data (ver 2.0 balance tables).
6. Rename ALL content to WH proprietary universe names → track in `RENAME-MAP.md`.
7. Save: full game + extracted assets → TeraBox; extracted assets + docs → western-heart
   GitHub repo (branch → PR → merge). NEVER auto-delete game files (owner law).

---

## Rename plan

Track old→new names in `~/workspace/game-reverse-engineering/RENAME-MAP.md`.
WH universe names for the new fighters (Jean Kujo, Taka-Arashi, rebalanced variants)
are OWNER-assigned — do not invent names. List models needing names per the
character-inventory rule.
