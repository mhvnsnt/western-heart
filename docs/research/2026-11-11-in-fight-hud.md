# What a fight shows on screen, and what only practice shows (2026-11-11)

Owner, 2026-11-11: "stop adding stuff into the actual fights and combat that are only for debug and practice type
shit like how much damage a hit is giving popping up big across the screen that's stupid AF to have in normal fights
and even if it did happen in practice u should do it like Tekken not that ugly hand tooled bullshit but straight from
the games source files of tekken".

## Source

The Tekken 7 Steam executable (`TekkenGame-Win64-Shipping.exe`, the same private copy the move pipeline reads;
never committed). Its UI is Scaleform movies under `/Game/UI_common/flash/`, and the exe names every movie and every
movie-clip path it drives. Read with `strings -n 6` (ASCII and UTF-16LE).

## The battle HUD has no hit counter and no damage number

The fight HUD is one movie, `SW_UI_HUD` (`SwfHUD::exec`, plus `SwfHUDGauge` and `CSwfHUDRage`). The clip paths the
exe drives in it:

- life gauges: `GAU_Life_Frame_Area_L_mc` / `_R_mc` (green bar, gradient, damage trail `GAU_Life_eff_damage`)
- round counters: `GAU_Life_Frame_Area_%s_mc.RNDcounter_%s_%1d_mc`
- timer: `TimerArea_mc.Timer_LimitBattle_Number01_mc` (and the infinite-time `..._Mugen_mc`)
- names, rank, title: `Rep_HUD_CH_NAME`, `UserName_Area_L_mc`, `RNK_M_L_mc`, `$playername_L`, `$Rank_L`, `$title_L`
- side gauges (character-specific EX bars) `EX_mc.EX_L_mc...`, and the rage movie `SW_UI_HUD_Rage`
- online only: ping / delay / rollback icons, wins counter, stage count

There is no hit counter, no damage figure and no hit-type text ("counter hit", "clean hit") anywhere in it.

## Hit data is a separate practice movie

`SW_UI_AttackData` (`SwfAttackData::exec`), one panel per side (`AttackData_%s_mc` with `%s` = `L` / `R`), labelled
with practice-mode message ids `prc_573` .. `prc_581`. Its fields, each with a `_Glow` state for the value that just
changed:

| clip | meaning in our panel |
|---|---|
| `Damage_%s_mc` | this hit's damage |
| `ComboDamage_%s_mc` | damage of the current combo |
| `HitCombo_%s_mc` | hits in the current combo |
| `MaxComboDamage_%s_mc` | best combo damage this practice session |
| `TotalDamage_%s_mc` | all damage dealt this practice session |
| `CleanHit_%s_mc` | lamp: the move's clean-hit property (no move data carries it yet, so it stays dark) |
| `CounterHit_%s_mc` | lamp: the hit was a counter hit |
| `WallHit_%s_mc` | lamp: the hit's reaction is a wall splat |
| `Punish_%s_mc` | lamp: the defender was still recovering from an attack that had just been blocked |

Frame data is a third practice movie, `SW_UI_Practice_Frames` (`SwfPracticeFramesWindow::frame_info_exec`).

## What the game does now

- Normal fights (versus, arcade, story, survival, ranked, online): life bars, timer, round pips, names, the meters,
  ROUND / FIGHT / K.O. banners. No hit counter, no damage numbers, no hit-type labels, no rejected-grab or
  rejected-Surge notes, no "break the throw" prompt, no throw-escape text, no control hints, no frame-data line.
- Practice (training and the fight lab): the attack-data panel above, one per side at the screen edge under the
  gauges, persistent, the changed value glowing; the throw-break prompt and throw-escape text as practice aids;
  control hints for 6 s at the start; the frame-data option (Options) draws only here.

Code: `game/js/practice-attack-data.js` (data, practice gate), `ui.attackData` / `ui.attackDataClear` in
`game/js/main.js` (panel), `game/js/game.js` call sites. Test: `test/practice-attack-data.test.mjs`.
Probe (screenshots both modes while hits land, lists every visible overlay): `tools/ui/fight_overlay_probe.mjs`.

## Not done here

The panel's look is ours (small dark readout with gold glow), not the original movie's art: the `.gfx` movies are
inside the game's pak files, which are not in the teardown. The field set, the per-side layout, the glow-on-change
behaviour and the practice-only rule are the game's.
