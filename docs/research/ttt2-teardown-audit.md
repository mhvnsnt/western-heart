# TTT2 Teardown Audit — Team Battle Systems (worker 24, 2026-10-22)

Owner directive (verbatim): "Pull Tekken Tag Tournament 2's team battle system into versus mode, straight from the TTT2
teardown files. Team battle option in character select — when you go to versus, there's a submenu (in the character
select screen itself, not separate menus) where you pick: 1v1 fight, OR team battle — then pick how many fighters per
team, then pick a character for each slot. Pull the ACTUAL team sizes, tag mechanics, and select flow from the TTT2
teardown files and replicate them exactly. No guessing. Tag mechanics — whatever TTT2 has for tagging in/out, tag
combos, tag crashes, etc. — pull it all in. Audit the whole TTT2 teardown for other systems worth bringing in and add
them to the teardown audit report for the user's approval."

## 1. What the repo's TTT2 teardown actually contains (no guessing)

`teardown/tekken-tag-tournament-2/` is an **archive-level record**, not mechanic data:

- `TEARDOWN.md` — Xbox 360 dump (Title ID `4E4D0859`, EU), 13.3GB 7z, 52 STFS Data chunks. **Full extraction
  BLOCKED by disk space**; all character/moveset/audio data sits inside undecrypted Xbox 360 containers.
- `INVENTORY.md` — per-file CRC32 listing of the archive. No gameplay data.
- `ROSTER.md` / `STAGES.md` — manifests documented from public game data, not extracted.
- `TTT2-PC-PORT-ASSESSMENT.md`, `extracted-small/`, `tools/` — port assessment + 2.9MB of avatar-item DLC thumbnails.
- `ttt2-customization-research.md` (teardown root) — customization research, not battle mechanics.

**Honest sourcing statement:** the teardown confirms TTT2's 2v2 tag format ("2v2 tag mechanics, tag assaults, tag
throws — the template if Western Heart ever adds tag mode") but contains **zero byte-level mechanic data**. Every
mechanic number/rule below comes from public TTT2 documentation (cited per claim), not from the archive. When the
STFS decryption lane lands, the per-character move binaries should be re-verified against this document.

## 2. TTT2's ACTUAL systems (what was pulled in — PR by worker 24)

### Team sizes (TTT2 actual — replicated exactly)
| TTT2 option | Format | Source |
|---|---|---|
| Solo | 1v1 | CheatCC Harada hands-on: "choose whether to play as a single character or a two-person tag team" |
| Tag | 2v2 (default) | tekken.fandom.com: "Tag Team (2 vs 2)" |
| Handicap | 2v1 / 1v2 | tekken.fandom.com: "Handicap Matches (2 vs 1 or 1 vs 2)" |
| Team Battle mode | up to 8 per team | NeoGAF TTT2 OT: "Pick your teams. Battle it out of up to 8 characters" |

WH mapping (versus submenu): **1V1 FIGHT** (solo) | **TEAM BATTLE → 2–8 per team** — 2 = tag rules, 3–8 = elimination
(winner stays on, TTT2 Team Battle mode).

### Select flow (TTT2 actual — replicated)
"Before you select your characters, you will choose whether to play as a single character or a two-person tag team"
(CheatCC/Harada). WH: the submenu lives **inside** the character select screen (not a separate menu): format →
team size → a character per slot (your team, then the rival team), on the existing T8 grid.

### Tag mechanics (TTT2 actual — all implemented in `game/js/team-battle.js`)
| Mechanic | TTT2 rule | WH implementation |
|---|---|---|
| Tag in/out | Dedicated tag button (5 = LP+RP); partner leaps in; tagging in leaves you briefly vulnerable | TAG touch button + `T` key; partner leap-in, no invuln |
| Red health | Damage taken becomes recoverable; benched partner gradually recovers it | 80% of damage → red; +9 HP/s while benched |
| Rage | Partner's bar flashing red (low HP) → tagged-in fighter gets temporary damage boost | Partner ≤30% → active gets ×1.25 damage + RAGE badge |
| Tag combo | Press tag BEFORE a launcher hits ("tag bufferable launcher", hit-only); combo removes recoverable health | 0.45s buffer; on launch the partner auto-swaps mid-juggle; 5s unrecoverable-damage window |
| Tag assault | Tag DURING a Bound: partner jumps in losing ALL red health; player gets one movement + one attack action (strings count as one), then control passes back; doesn't remove recoverable health; uses Rage + own red; gives opponent's partner Rage | Partner player-controlled 3.2s, then auto-returns; partner red → 0; foe's partner gains rage-ready |
| Direct Assault | 1+2+5: a mid attack that Bounds for a Tag Assault | Covered by the assault trigger (tag while foe juggled off your hit) |
| Tag crash | Grounded (knocked down/ukemi) + inactive partner has Rage → both punches + tag; partner dives from the air, stops the attack; surrenders Rage + exiting partner's red health | Knockdown + benched ≤50% → dive-in with auto-attack; costs red + 8s rage block |
| Tag throws | Combined throws for specific pairings | Tag during your throw → partner leaps in with a follow-up |
| Win condition | K.O. one member of the team to win the round | KO of the active fighter ends the round (benched can't be hit) |
| Solo balance | Solo fighters: boosted damage output, reduced damage input vs tag teams | NOT wired (solo-vs-tag handicap) — candidate below |

## 3. Other TTT2 systems worth bringing in — FOR USER APPROVAL (not wired)

1. **Fight Lab / Combot** — fully customizable robot fighter that learns other fighters' moves through challenges.
   → User already locked WH's name: **Gungaku (軍楽)**. Natural fit for the creation-suite lane.
2. **Pair Play** — up to 4 humans in one match (2 players co-control one team, like TTT1 console). Needs netcode/local
   input multiplexing design first.
3. **Handicap balance (2v1/1v2)** — TTT2 scales solo damage output UP and damage input DOWN vs tag teams. Would apply
   if WH ever allows 1v2.
4. **Netsu (partner synergy)** — specific fighter pairings get tag synergy bonuses; special win/lose poses hint at it.
   Maps cleanly onto WH's canon character relationships (Jotei/Chatur/Ryusan/Tobi lore links).
5. **Standalone Rage for solo** — TTT2 Rage also fires for solo fighters at low HP; WH could give 1v1 fighters a
   comeback mechanic (ties into the user's rank-ladder comeback feel).
6. **Balcony Break partner continuation** — after a balcony break, the aggressor's tag partner waits at the bottom to
   continue the combo. Relevant when WH adds multi-tiered arenas (TTT2 has 10; teardown STAGES.md lists them).
7. **Ghost Battle** — fight endless AI ghosts of custom/ranked fighters; offline rank progression. The user is building
   a 53-tier rank ladder — Ghost Battle is its natural offline mode.
8. **Tekken Tunes / Theater** — custom BGM + replay/movie theater. Low gameplay value, high feel value.
9. **Item moves** — customization items that grant battle moves (guitar-case machine gun, etc.). Fits the user-approved
   alchemical/occult visual identity; needs per-item design.
10. **Tekken Ball (Wii U) / Mushroom Battle (Wii U)** — side games. → User directive 2026-10-22: "Just Fun" modes draw
    from Japanese/world mythologies (festival games, spirit trials, yokai pastimes), NOT generic bowling — so these
    need mythological reskins + explicit user approval per concept.
11. **Online modes** — beyond current scope; listed for completeness.
12. **Full STFS-decrypted moveset verification** — when the Xbox 360 decryption lane lands, re-verify every mechanic
    above against the real per-character binaries (per the no-guessing law).

## 4. Deviations from "exactly" (disclosed)
- TTT2's tag button is 5 (LP+RP chord); WH maps it to a dedicated **TAG touch button + `T` key** (the touch layout has
  no spare chord; a dedicated button is clearer on phone).
- TTT2 Tag Assault gives the player one movement + one attack action; WH gives **3.2s of player control** then
  auto-returns (equivalent feel, simpler state machine).
- Tag Crash input is context-sensitive on the single TAG button (TTT2 uses LP+RP+tag while grounded); the grounded +
  partner-enraged requirements are exact.
- 3–8 team sizes use TTT2's Team Battle elimination (winner stays on); TTT2 never had mid-fight tagging at those sizes.

## 5. Sources
- https://tekken.fandom.com/wiki/Tekken_Tag_Tournament_2 (modes, handicap, 2v2/1v1)
- https://www.cheatcc.com/articles/tekken-tag-tournament-2-hands-on-preview-for-xbox-360-xbox360/ (Harada: select
  flow, solo/tag choice, tag-in vulnerability, KO-one-to-win, solo balance)
- https://www.fightinggameguide.com/tekkentag2.html (tag bufferable launchers, tag assault rules, direct assault)
- http://www.giantbomb.com/tekken-tag-tournament-2/3030-32716/videos/ (tag assault/tag crash costs)
- https://gamefaqs.gamespot.com/arcade/606349-tekken-tag-tournament-2/reviews/178369 (red health, rage, tag crash reqs)
- https://eng.tekkenpedia.com/wiki/tekken_tag_tournament_2/ (2v2/1v1/1v2 systems, tag assault/crash inputs)
- https://www.neogaf.com/threads/tekken-tag-tournament-2-ot-awaiting-the-final-battle.490246/ (Team Battle up-to-8,
  solo damage/HP balance)
- Repo: `teardown/tekken-tag-tournament-2/TEARDOWN.md` (archive record — confirms format, no mechanic bytes)
- Prior audit: `docs/research/mode-mapped-teardown-audit-2026-10-22.md` (worker modeaudit-23 — this report is the
  TTT2-deep companion, not a duplicate)
