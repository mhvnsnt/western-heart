# UI citation re-point: `gre:tekken7/ui/flash/` → pakchunk0 (2026-10-24)

## Problem

`game/ui_sources.json` cited `gre:tekken7/ui/flash/SW_UI_*.png` for
11 files. That directory does not exist. Every one of the 11 citations
was unverified.

## Method (verified, not assumed)

1. Fetched `teardown/tekken7-steam/pakchunk0/manifest.json` from PR
   #863's branch `feat/t7-steam-extraction` (head `43b2ce0a`, DRAFT:
   "T7 Steam extraction #1: pakchunk0 meshes, textures, UI").
   The manifest has 200 meshes + 622 textures, of which 153 sit under
   `textures/UI_common/flash/`.
2. Checked each of the 11 cited files against the manifest AND against
   the actual checked-in files on the #863 branch
   (`teardown/tekken7-steam/pakchunk0/textures/UI_common/flash/<dir>/`).
   A citation was re-pointed ONLY if both checks passed.
3. Searched the whole repo (code search) for the 4 failures, to rule
   out another in-repo home.

## Verified: 7 re-pointed

All 7 exist in the manifest AND as checked-in files on #863:

| File | New citation (prefix `teardown/tekken7-steam/pakchunk0/`) |
|---|---|
| `SW_UI_MainMenu/Base_OnlineMenu.png` | `textures/UI_common/flash/SW_UI_MainMenu/Base_OnlineMenu.png` |
| `SW_UI_Result_Lightning/Result_Lightning_02.png` | `textures/UI_common/flash/SW_UI_Result_Lightning/Result_Lightning_02.png` |
| `SW_UI_CharacterSelect/SlotRed_OnGradient.png` | `textures/UI_common/flash/SW_UI_CharacterSelect/SlotRed_OnGradient.png` |
| `SW_UI_CharacterSelect/SlotBlue_OnGradient.png` | `textures/UI_common/flash/SW_UI_CharacterSelect/SlotBlue_OnGradient.png` |
| `SW_UI_CharacterSelect/Rep_CS_CH_PANEL_00.png` | `textures/UI_common/flash/SW_UI_CharacterSelect/Rep_CS_CH_PANEL_00.png` |
| `SW_UI_StageSelect/InfoRed_Base.png` | `textures/UI_common/flash/SW_UI_StageSelect/InfoRed_Base.png` |
| `SW_UI_StageSelect/RedPanel_Base.png` | `textures/UI_common/flash/SW_UI_StageSelect/RedPanel_Base.png` |

These went into `game/ui_sources.json` for `screen-menu` (1),
`screen-result` (1), `screen-select` (3), `screen-stage` (2).
The #863 branch's checked-in flash dirs are exactly 7:
CharacterSelect, HUD_Gauge, MainMenu, Makuai, Result_Lightning,
Result_RankPromotion, StageSelect — no other flash dirs exist there.

## NOT verified: 4 kept and flagged (not re-pointed)

| File | Evidence |
|---|---|
| `SW_UI_PauseMenu_Replay/Cursor_Sub.png` | Absent from pakchunk0 manifest; no `SW_UI_PauseMenu_Replay` dir on #863; zero code-search hits repo-wide |
| `SW_UI_PauseMenu_Replay/NavigationBar_Waku.png` | Same |
| `SW_UI_ControllerSetup/PanelBase1.png` | Absent from manifest; no `SW_UI_ControllerSetup` dir on #863; zero hits repo-wide |
| `SW_UI_StoryMode_Option/Win_3line.png` | Absent from manifest; no `SW_UI_StoryMode_Option` dir on #863; zero hits repo-wide |

Their old `gre:tekken7/ui/flash/` citations are kept verbatim in
`screen-menu` and flagged in its note. They were NOT re-pointed to
pakchunk0 — that path does not contain them, and re-pointing would
repeat the original error with a new path. Follow-up: extract a later
pakchunk (these UI groups may live in pakchunk1+) or verify the
private game-reverse-engineering tree. Until then they are flagged,
not silently fixed.

Untouched by this re-point: the `gre:teardown/tekken7-steam/tkdata/
list/SW_UI_*.bin` citations in `screen-menu` (different asset class,
not part of this check) and all `teardown/tekken7-steam-ui/
T7-UI-LAYOUT.md` citations.

## Merge dependency (read before merging)

The 7 re-pointed paths live on #863's branch, not on main. They
resolve on main when #863 merges. The screens carrying them
(`screen-menu`, `screen-result`, `screen-select`, `screen-stage`)
are NOT touched by this lane's PR (their sections are unedited, and
`game/js/main.js` is not a ui-sources UI glob), so
`tools/ui-sources/check.py` does not validate those sources at this
PR's head — no new CI failure from the re-point. After #863 lands,
the same check passes them. Merge order: #863 first if the
coordinator wants the citations resolving immediately; otherwise
this PR first is also safe (citations pending #863, stated here).

## Stale doc flagged (extraction lane's, not this lane's)

`teardown/tekken7/ui/UI-EXTRACTION-STATUS.md` still says T7 was
"never acquired" and extraction is "BLOCKED". That is superseded by
PR #863's actual extraction and by the user's T7 Steam ownership
(2026-10-23). This lane did not rewrite it (extraction lane owns
that doc); it is flagged here so it is not cited as current status.
