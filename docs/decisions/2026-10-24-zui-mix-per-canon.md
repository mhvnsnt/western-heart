# ZUI MIX PER CANON — Steve Fox base + Lei Wulong drunken fist + WH originals (2026-10-24)

## Owner directive (verbatim intent, 2026-10-24)

Zui's moveset is a MIX per canon — Steve Fox base PLUS Lei Wulong drunken fist moves
PLUS other moves mixed in per canon. Zui KEEPS his hands-up drunken stagger stance
(do NOT change it). Sharing, not transfer: Lei's drunken fist moves go to Zui TOO;
Rave KEEPS his full Lei moveset. Nothing is removed from Rave.

## Canon reading (what canon actually says)

- **ZUI — The Drunken Soul, vessel of BYOU.** "Steve Fox's pure boxing, drowned in sake."
  Ex-monk of the Central Mountain, hedonist philosopher, "the straight line is a lie,
  everything stumbles, so stumble *beautifully*." Sake bottle never leaves his hand.
  Supernatural sway. Owner-locked: "Drunken master ex-monk hedonist. Sagat-meets-
  Chinese-mountain-monk visual. Sake bottle prop, supernatural sway, sketchbook tattoos.
  Name from 醉 (zuì), 醉拳 (zuìquán) = drunken fist. Steve Fox base."
- **STEVE FOX — The Boxer Soul, same vessel, same BYOU soul, before the monastery.**
  "Zui *is* Steve — the same vessel, the same BYOU soul, before the monastery and the
  bottle. The sway was footwork first. The dodge was a slip-roll before it was a stumble."
- **Lei → BYOU (T3 conversion record, CANON.md):** "Lei→soul BYOU (vessel name pending
  the owner's Lei naming decision)." The Lei connection to BYOU is canon; the drunken
  group is the part of Lei that Zui uses.
- **No third Tekken style is named for Zui anywhere in canon.** The "other moves mixed
  in" resolve to 2 WH-original canon moves (sake bottle + stumble philosophy — see below),
  NOT to a third Tekken fighter. No third fighter was invented.

## Mix counts (keys in `game/assets/movesets/zui.json`, 654 total, 0 deleted, 0 added)

| Group | Keys | Unique inputs | Source |
|---|---:|---:|---|
| Steve Fox T7 base (`mix_group: steve-base`) | 345 | 280 | Tekken 7, TheBigTuna MOD damage where matchable (see below) |
| Lei Wulong drunken (`mix_group: lei-drunken`) | 40 | 39 | Tekken 6 / TTT2 drunken fist, shared via Rave's Lei set |
| WH original canon (`mix_group: wh-original`) | 4 keys / 2 moves | 4 | Western Heart (canon original) |
| Legacy T3 Jin proxy (`mix_group: legacy-t3-proxy`) | 139 | — | Tekken 3 Jin proxy, preserved verbatim, NOT part of the canon mix |
| T8 variant layer (`mix_group: t8-variant-not-in-mix`) | 126 | — | Pre-existing T8-sourced entries, NOT counted, NOT touched (see gaps) |

Every mix entry (389) carries `source_fighter`, `source_game`, `mix_group`, and
`input_display` (LP1/RP2/LK3/RK4 rendering of its Tekken input). Files keep Tekken
numbers in `input` and show LP1/RP2/LK3/RK4 alongside in `input_display`, per the
button-names directive (LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2,
LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4).

## Lei drunken table (40 — all 35 DRU-input moves + 5 drunken transitions)

DRU = Drunken Master Walk stance. All DRU-input moves are stance-gated
(`stance: DRU, stance_gate: true`) and were already present in Zui's file from the
2026-10-21 import; this PR labels them, renames the 20 `RAVE DRU …` names to
`ZUI DRU …`, and corrects their source game. Anim refs keep their historical
`rave_…` slugs untouched (renaming a ref could break animation lookup).

| Move | Input | LP1/RP2/LK3/RK4 | Damage raw | TTT2 status |
|---|---|---|---|---|
| Drunken Master Walk | `f+3+4` | `f+LK3+RK4` | none | Name/input confirmed |
| ZUI DRU (2),2 | `DRU (2),2` | `DRU (RP2),RP2` | 20 [24] | Name/input confirmed |
| ZUI DRU (3),(2),4 | `DRU (3),(2),4` | `DRU (LK3),(RP2),RK4` | 18 [21] | Name/input confirmed |
| ZUI DRU (3),1+2 | `DRU (3),1+2` | `DRU (LK3),LP1+RP2` | 15 [18] | NEEDS-SOURCE-CHECK |
| Drunken Fox Combination (chain) | `DRU (3),2` | `DRU (LK3),RP2` | 20 [24] | Name/input confirmed |
| ZUI DRU (3),2,4 | `DRU (3),2,4` | `DRU (LK3),RP2,RK4` | 20 [24], 12 | Name/input confirmed |
| Drunken Tiger Lash | `DRU 1` | `DRU LP1` | 25 [30] | Name/input confirmed |
| ZUI DRU 1+2 | `DRU 1+2` | `DRU LP1+RP2` | none | Name/input confirmed |
| Tiger Sip (chain) | `DRU 1+2,1+2` | `DRU LP1+RP2,LP1+RP2` | none | Name/input confirmed |
| Tiger Sip | `DRU 1+2,1+2,1+2` | `DRU LP1+RP2,LP1+RP2,LP1+RP2` | none | Name/input confirmed |
| Out of Control | `DRU 1+3` | `DRU LP1+LK3` | 33 | Name/input confirmed |
| ZUI DRU 1,F | `DRU 1,F` | `DRU LP1,F` | 25 [30] | Name/input confirmed |
| ZUI DRU 2 | `DRU 2` | `DRU RP2` | 12 [14] | Name/input confirmed |
| Drunken Rapid Fists | `DRU 2,2` | `DRU RP2,RP2` | 12 [14], 20 | Damage differs — file kept |
| ZUI DRU 2,2,F | `DRU 2,2,F` | `DRU RP2,RP2,F` | 12 [14], 20 | Name/input confirmed |
| ZUI DRU 2,B | `DRU 2,B` | `DRU RP2,B` | 12 [14] | Name/input confirmed |
| ZUI DRU 2,F | `DRU 2,F` | `DRU RP2,F` | 12 [14] | Name/input confirmed |
| ZUI DRU 3 | `DRU 3` | `DRU LK3` | 10 [12] | Damage differs — file kept |
| Staggering Slide | `DRU 3+4` | `DRU LK3+RK4` | 23 [27] | Damage differs — file kept |
| Drunken Fox Rotation | `DRU 3,1+2` | `DRU LK3,LP1+RP2` | 10 [12], 15 | NEEDS-SOURCE-CHECK |
| ZUI DRU 3,1+2,D | `DRU 3,1+2,D` | `DRU LK3,LP1+RP2,D` | 10 [12], 15 | Name/input confirmed |
| Drunken Fox Combination (chain) | `DRU 3,2` | `DRU LK3,RP2` | 13 [15], 20 | Name/input confirmed |
| Drunken Fox Combination | `DRU 3,2,4` | `DRU LK3,RP2,RK4` | 13 [15], 20, 12 | Damage differs — file kept |
| ZUI DRU 3,2,4,B | `DRU 3,2,4,B` | `DRU LK3,RP2,RK4,B` | 13 [15], 20, 12 | Name/input confirmed |
| ZUI DRU 3,2,4,F | `DRU 3,2,4,F` | `DRU LK3,RP2,RK4,F` | 13 [15], 20, 12 | Name/input confirmed |
| ZUI DRU 3,2,F | `DRU 3,2,F` | `DRU LK3,RP2,F` | 13 [15], 20 | Name/input confirmed |
| ZUI DRU 3,F | `DRU 3,F` | `DRU LK3,F` | 13 [15] | Name/input confirmed |
| Drunken Tiger Kick | `DRU 4` | `DRU RK4` | 17 [20] | Name/input confirmed |
| ZUI DRU 4,F | `DRU 4,F` | `DRU RK4,F` | 17 [20] | Name/input confirmed |
| ZUI DRU b | `DRU b` | `DRU b` | none | Name/input confirmed |
| Spinning Headbutt | `DRU b+1+2` | `DRU b+LP1+RP2` | 25 [30] | Name/input confirmed |
| ZUI DRU f | `DRU f` | `DRU f` | none | Name/input confirmed |
| ZUI DRU f,b | `DRU f,b` | `DRU f,b` | none | Name/input confirmed |
| Drunken Stupor | `DRU u/b+1+2` | `DRU u/b+LP1+RP2` | none | Name/input confirmed |
| Drunken Fake to Jab | `DRU u/b+1+2,1` | `DRU u/b+LP1+RP2,LP1` | 25 [30] | Name/input confirmed |
| Drunken Fall | `DRU u/f+1+2` | `DRU u/f+LP1+RP2` | 21 [25] | Name/input confirmed |
| Startled Drunk | `FCD or SLD 1+2` | `FCD or SLD LP1+RP2` | none | Name/input confirmed |
| Startled Drunk | `KND or PLD 1+2` | `KND or PLD LP1+RP2` | none | Name/input confirmed |
| Phoenix Illusion to Drunken Master Walk | `PHX 1+2` | `PHX LP1+RP2` | none | Name/input confirmed |
| Phoenix Drunken Tiger Stumble | `PHX 1,D` | `PHX LP1,D` | 24 [28] | Damage differs — file kept |

Completeness check: Zui's DRU set equals Rave's DRU set (35 DRU-input moves, identical
inputs) and Byou's DRU set (same `lei_*` ids, `DRU.` vs `DRU ` spelling only).
No DRU move was missing, so no Lei move was added — this PR is labeling +
correction, not a new import. The one exception is flagged, not added:
`byou.json`-only `lei_rbn_021` (`DRU.2,F+4`, rbnorway row) is absent from Rave's set
and from the TTT2 Drunken Master Walk section — NEEDS-SOURCE-CHECK, not wired.

## WH-original canon moves (the "other moves mixed in")

| Move | Input | LP1/RP2/LK3/RK4 | Anim ref | Canon basis |
|---|---|---|---|---|
| Bottle's Honest Truth [WH SIGNATURE] | `1+2` (also placeholder key `S`) | LP1+RP2 | `wh:zui:sig:bottles-honest-truth` | "The sake bottle never leaves his hand. The bottle was more honest than the monastery." |
| Beautiful Stumble [WH SIGNATURE] | `d+4` (also placeholder key `D+K`) | d+RK4 | `wh:zui:sig:beautiful-stumble` | "The straight line is a lie. Everything stumbles — so stumble beautifully. Sway-dodge into low kick." |

Both already existed in the file with real Tekken inputs (`1+2`, `d+4`); this PR
labels them `wh-original`. NEEDS-INPUT count for the whole mix: **0** — every mix
move already had a Tekken input; nothing was invented.

## Stance confirmation (corrected, not replaced)

- `stances.default` was `BOX` (Steve boxing). Per the owner directive it is now `DRU`.
  This is metadata only: the file itself records that the fighter state machine has no
  stance flag yet (data-level gates), and no game code reads `stances.default`.
- The DRU stance entry itself is UNCHANGED except its `source` label (corrected from
  "Lei Wulong T7 (via rave.json T7 import)" to "Lei Wulong (Tekken 6 / TTT2 drunken
  fist, shared via rave.json Lei set; Lei has no T7 data)") and one appended sentence
  noting DRU as the default. Entry move `f+3+4` (Drunken Master Walk), exit `DRU b`,
  and all 40 DRU stance-list moves are unchanged. Steve boxing (`BOX`) remains a
  listed stance, not the default. No NEEDS-STANCE-SPEC: the spec exists and is intact.

## Collision resolutions (within Zui's moveset)

- **The only Steve ↔ Lei shared canonical input is `f+3+4`.** Canonical key `f+3+4`
  = Lei Drunken Master Walk (`lei_290`). Steve Peekaboo (`steve_198`) is preserved
  under key `f+3+4_r198` AND inside the `f+3+4` entry's nested `t7` dict — Peekaboo
  is NOT lost, and the pre-existing PKB note documents that `,F` transition strings
  enter Peekaboo in play. No Steve base move and no Lei move was silently overwritten.
- **All other duplicate canonical inputs** are (a) T3-proxy vs Steve, where Steve owns
  the canonical key and the proxy is kept under a `_r` key, or (b) chain-variant rows
  (parenthesized continuations of the same string). DRU moves cannot collide with
  standing Steve moves: they are stance-gated.
- Verified by field-level diff vs `origin/main`: the only changed fields outside the
  newly added mix fields are the 20 `RAVE → ZUI` renames and the stance default/source/
  note. Damage, `anim_ref`, `input`, `stance`, and `stance_gate` are identical on all
  654 keys; 0 keys deleted, 0 keys added.

## Steve T7 base + TheBigTuna MOD damage (verification, not a re-import)

- Prior work (PR #1000 method, commit `005061f2`) already wired TheBigTuna MOD damage
  into Zui's Steve entries: nested `t7` dicts get `damage` := first MOD hit,
  `mod_damage` := full per-hit trace iff multi-hit, `mod_source` always; flat entries
  get `mod_damage` + `mod_source` with entry damage untouched; whole-notation matching
  only; ambiguous/unmatched left exactly as-is.
- This PR re-verified that wiring against `TheBigTuna/Tekken-7-Frame-Data`
  `frames-json/t7-steve-1.json` (255 rows): **117/117 agree** where TheBigTuna has
  parseable damage (the 4 apparent disagreements are TheBigTuna rows with empty damage
  `","` / `",,"` for `f+1+2` variants, not real mismatches). 175 Steve entries carry
  MOD sourcing today.
- The remaining 119 Steve entries are unmatchable by the established whole-notation
  rule and were left exactly as-is: 116 notations are absent from TheBigTuna's 255
  Steve rows (stance-transition / `~` / wall / ground variants TheBigTuna phrases
  differently or lacks), 1 is ambiguous (`d/b+3`: TheBigTuna lists both 13 and 12),
  1 has null TheBigTuna damage (`b+1+2`). No MOD value was forced or guessed.

## Lei source correction (the T7-Lei problem, stated plainly)

Lei Wulong is NOT in Tekken 7. The 2026-10-21 import labeled the shared Lei group
"T7" via the t7chicken dataset, and `rave.json` / `byou.json` carry the same label.
That label is wrong as a game attribution even though the move names/inputs match
real Lei drunken fist. This PR corrects it by annotation, not by rewriting history:
`source_game` on all 40 Lei entries now reads "Tekken 6 / Tekken Tag Tournament 2",
each carries a `mix_note` stating the sharing + the correction, and the historical
`t7_import_note` string is left untouched. The TTT2 cross-check used the Tekken Tag
Tournament 2 movelist, During Drunken Master Walk section: all named DRU moves
confirmed on name + input; per-hit damage differs on 5 rows (file value kept
verbatim, listed in the table notes); `Drunken Fox Rotation` (`DRU 3,1+2` and
`DRU (3),1+2`) was NOT found in the TTT2 DRU section and is flagged
NEEDS-SOURCE-CHECK. No T8 data was used for the mix.

## Move List Creator wiring (Zui individually, editor proof only)

- `packages/creation-suite/src/movelist-editor.js`: `fromMovesetFile()` already builds
  Zui's library from `zui.json`, so all 389 mix entries were already readable. This PR
  adds an additive pass-through (`source_fighter`, `source_game`, `mix_group` on each
  library entry) so the editor can display each Zui move's mix source directly, without
  digging into `sourceMove`. Validation logic is untouched.
- Node test (`/tmp/zui_editor_test.mjs`, `node v24.22.1`): library 666 entries
  (654 move keys + 12 non-duplicate specials); steve-base 345, lei-drunken 40,
  wh-original 4; all 40 Lei entries carry `source_fighter: Lei Wulong` and the T6/TTT2
  game; own-slot `computeMappingStatus` = `correct` + allowed for DRU LP1
  (Drunken Tiger Lash), DRU LK3,RP2,RK4 (Drunken Fox Combination), DRU LP1+RP2,
  standing LP1, LP1+RP2 signature, and `f+3+4` (Drunken Master Walk); 0 mix entries
  lack `anim_ref` (none would be `unmapped`). Simulation/editor proof only —
  NOT play-verified, and no play claim is made.
- Known display gap (flagged, not silently fixed): the editor's `toDisplayInput`
  renders `DRU 1` as `DRU 1`, not `DRU LP1`, for space-form stance inputs (its
  dot-form branch handles `DRU.1` only). The file-level `input_display` field does
  render `DRU LP1`. Changing `toDisplayInput` would alter display for every fighter's
  stance inputs and belongs to the sibling Move List Creator lane, not this PR.

## Mixed-style audit — other characters (standing rule: MIX PER CANON)

Method: (1) read CANON.md character entries + Owner-locked base lines; (2) scan every
`game/assets/movesets/*.json` for 2+ distinct Tekken T7 fighter prefixes; (3) check
whether canon names 2+ styles for that character. A file holding two fighters' rows is
NOT automatically a canon mix — transformation forms and unresolved doc conflicts
are reported as such, not rewired.

| Character | Styles / sources in canon | Moveset today | Verdict |
|---|---|---|---|
| **ZUI** | Steve Fox boxing + Lei Wulong drunken fist + WH-original (bottle/stumble) | 345 Steve T7 + 40 Lei drunken + 2 WH-original, all labeled in this PR | **WIRED (this PR)** |
| **RAVE** (Kiko Tanaka / Ghost) | Lei Wulong, full, plus Byou donor rows (see reconciliation note) | 526 Lei T7 rows + ~158 Byou donor rows + 2 Rave sigs (per pattern audit) | NOT a canon-named style mix — but a file-content MIX under the pattern audit's definition (Lei + Byou donor rows, per owner order quoted there). Zui's DRU sharing is one-directional; Rave untouched by this PR |
| **BYOU** (soul file) | Lei Wulong | Full Lei set (524 + 47 rbnorway rows) + DRU group | NOT a mix — the Lei-side file of the same BYOU soul. Untouched by this PR |
| **STEVE FOX** (vessel) | Steve Fox boxing | No separate fighter file; represented by Zui's Steve base (same vessel, same soul, before the monastery) | No action — the duality IS the Zui mix |
| **DEMONIO / DEMONIO-WINGED** | Mishima-style karate only (Jin's frame, "precise, fundamental, the honest style") | Jin rows + Devil Jin rows (demonio 289 + 45; winged 218 + 199) | NOT a mix per canon-style definition — Devil Jin is Jin's devil FORM, not a second fighting style; BUT the pattern audit counts Devil Jin as a second fighter, so Demonio is MIX under that definition. No wiring change either way |
| **GYOU** | CONFLICT: T3 conversion record says Hwoarang→GYOU; user decision 2026-10-23 says Paul Phoenix→Gyou; T3 record also says Paul→TOU | File already holds both: 326 Hwoarang `~t7.hwoarang` variant keys (suffixed, non-colliding) + 86 Paul keys + T3 rows | **NEEDS-CANON-DECISION** — owner must resolve Paul vs Hwoarang. No wiring change by this PR; deleting either set would destroy one side of an unresolved conflict |
| **THE TRADER** (Phantom Marketplace) | Mimicry — "wears the opponent's moveset like a borrowed coat"; ROSTER.md: "Mokujin's mimicry moveset. Copies the opponent's style." | No moveset file | **NEEDS-DATA (systemic)** — mimicry cannot be a fixed mix; needs an opponent-copy system, not a move list |
| **DXMMII** | Mokujin base; "mimic soul", "a copy that became an original" | Mokujin base file | **NEEDS-DATA (systemic)** — same as Trader: mimicry is a system, not a fixed 2-fighter mix |
| All other canon fighters checked | Single Tekken base each in canon (King→Pantera, Armor King→Yukihyo, Akuma→Dio, Shaheen→Scimitar, Lars→Chordz, Zafina→Mary Posa, Bosconovitch→Doc Frank, Yoshimitsu→Phantom, Lee→Purple Rain, Xiaoyu→Saku-ra, Law→Buffalo Bill, Paul→Gyou per 2026-10-23, plus single-base roster) | Single-base files (no 2nd T7 prefix found by scan) | No mix found — no action |

**Standing rule (also appended to `docs/owner-directives.md`): MIX PER CANON.**
When canon says a fighter fights with 2+ styles, the moveset MUST reflect all of them,
each move labeled with its source fighter + source game, collisions resolved by
stance-gating or alternate input (never silent overwrite), and sharing NEVER removes
moves from the donor. When canon does NOT name a mix, a file holding two fighters'
rows is a conflict or a form to report, not a mix to wire. Mimicry (Trader, DXMMII)
is a system, not a move list — flag NEEDS-DATA, don't fake a fixed mix.

## Honest gaps (nothing papered over)

1. **Lei damage values are the imported dataset's, not TTT2's**, on 5 rows (see table
   notes). Overwriting them with TTT2 numbers would be a balance change made without
   frame-data authority for the dataset's own game version; they are kept verbatim
   and flagged.
2. **Drunken Fox Rotation NEEDS-SOURCE-CHECK** (not in the TTT2 DRU section).
3. **Byou-only `lei_rbn_021` NOT added** (single rbnorway row, unverified).
4. **T8 layer untouched and flagged:** 171 Zui entries carry `t8_source` fields and
   the file partitions (priority-ordered) as 126 `t8-variant-not-in-mix` keys. Those
   entries pre-date this PR, are NOT part of the canon mix, and are NOT counted in it.
   Whether canonical-slot T8 entries stay (as alternate-source variants, which the
   editor's `fromMovesetFile` comment explicitly supports) or are purged under the
   no-T8 rule is an owner decision for a separate PR — deleting 126 keys here would
   have been destructive scope creep.
5. **MOD damage incomplete by method, not by neglect:** 119 Steve entries have no
   TheBigTuna MOD value because whole-notation matching cannot match them (see above).
6. **Not play-verified.** Editor/simulation proof only, per task scope. The live
   playable check (hands-up drunken stagger idle, DRU entry from boxing, DRU strings
   in a real fight) is still owed before anyone calls this "done" in game.
7. **Rave untouched:** `git diff --name-only` for this branch shows only
   `game/assets/movesets/zui.json`, `packages/creation-suite/src/movelist-editor.js`,
   and the three docs below. Rave's file was read, never written.

## Files changed (this branch)

- `game/assets/movesets/zui.json` — mix labels, 20 renames, stance default BOX→DRU,
  DRU source correction, `mix_20261024` + `mix_note_20261024` audit objects.
- `packages/creation-suite/src/movelist-editor.js` — additive mix-source pass-through
  in `fromMovesetFile()` (8 lines, validation untouched).
- `docs/decisions/2026-10-24-zui-mix-per-canon.md` — this file.
- `docs/owner-directives.md` — MIX PER CANON standing rule.
- `WORKLOG.md` — entry for this PR.

## Reconciliation with the pattern audit (PR #1021, landed on main during this PR)

`docs/MOVESET-PATTERN-AUDIT-2026-10-24.md` (PR #1021) audits the same roster by a
different definition: MIX = moves from 2+ distinct named fighters present in the
FILE, whatever the decode status. By that definition it counts 6 MIX: Zui, Rave,
Demonio, Gyou, Kronos, Ryuji. This audit counted canon-NAMED fighting styles and
found 1 confirmed fixed mix (Zui). The two audits do not contradict; they answer
different questions, and the rows above now carry both verdicts where they differ:

- Rave: this audit originally called Rave pure Lei from its 526 T7 Lei rows; the
  pattern audit shows ~158 Byou donor rows in the same file (owner order quoted
  there: "U can add leis and byous moves to rave"). Corrected above.
- Demonio: form (this audit) vs second fighter (pattern audit rule 7). Both readings
  are recorded; neither requires a wiring change.
- Gyou: both audits agree it NEEDS an owner decision (Paul declared base vs
  Hwoarang-majority file).
- Zui counts differ by basis only: this PR counts 345 Steve keys (280 unique inputs,
  chain-variant rows included); the pattern audit cites 286/287 T7 Steve rows
  (distinct-row basis). Same file, different counting basis.
- The pattern audit explicitly defers Zui to this lane ("Sibling Zui-mix lane owns
  Zui's Steve + Lei DRU mix and stance system") and flags the same remaining gap
  class this PR flags for animation (DRU clip row-mapping).
