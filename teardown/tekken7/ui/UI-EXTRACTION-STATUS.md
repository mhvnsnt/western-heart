# Tekken 7 — UI Asset Extraction Status

**Updated:** 2026-10-23 (UI sweep)
**Status:** 🔴 BLOCKED — full game never acquired

## Blocker

The 51GB Tekken 7 PC (Steam) game was never acquired. No `.pak` files exist on
the VM, on any western-heart release, or in the repo. Per
`../TEKKEN78-ACQUISITION-PLAN.md`, acquisition waits on the owner confirming
the Steam purchase (console copy is encrypted/unusable; PC is Steam-only).

**Do NOT pull T7 UI from third-party mod sites** — T7 is the one game the owner
does not own yet, so unofficial sources are not authorized.

## Where the UI lives (sourced from tekkenmods-docs, in-repo)

From `tekken7/tekkenmods-docs/files/en/Tekken_7/Basic_Information/Understanding_the_Game_Files/index.md`
(actual modding documentation, not guesses):

| Asset class | Pak-internal path |
|---|---|
| UI assets | `TekkenGame\Content\UI_common` |
| Character assets | `TekkenGame\Content\Characters` |
| Stages | `TekkenGame\Content\Maps` |
| Stage assets | `TekkenGame\Content\Stage` |
| Sound | `TekkenGame\Content\WwiseAudio` |

Pak files on disk: `TekkenGame\Content\Paks` (Steam default:
`...\steamapps\common\TEKKEN 7\TekkenGame\Content\Paks`).

Texture naming: `T_` prefix = Texture (e.g. `T_CH_kaz_bdu_1P_wind_coat_D` —
T=texture, CH=character, kaz=Kazuya, D=diffuse).

## Extraction tools (already in repo)

- `teardown/tekken7/tools/` — FModel + repak pulls (UE4 pak extraction)
- `tekken7/tekkenmods-docs/.../Extracting_Game_Files/quickbms.zip` — QuickBMS +
  UE4 script (`extract-all_4gb_files.bat` → `out/` dir)
- umodel path documented with screenshots in the same guide
  ("For this demonstration, we'll extract a simple UI texture file")

## UI pull list (for when the game lands)

From `UI_common`: button textures/backgrounds, menu background art,
select-screen frames, icon sets, HUD elements. Fonts: UE4 font assets in the
same tree. Navigation sounds: `WwiseAudio` banks.

Mobile rule: prefer large high-contrast button/background textures; T7's UI was
built for TV scale — assets will need downscale/re-layout passes for phone,
but the source art comes from here, not hand-drawn.

## Unblock path

1. Owner confirms Steam purchase/download (per TEKKEN78-ACQUISITION-PLAN.md)
2. Download straight to external storage (47GB won't fit VM disk)
3. Pull back `UI_common` subtree only → extract with umodel/FModel/repak
4. Land in `teardown/tekken7/ui/` via branch + PR; large files to Releases
