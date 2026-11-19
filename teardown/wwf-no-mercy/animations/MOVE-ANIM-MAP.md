# WWF No Mercy → Bannon: Move-to-Animation Map

**Date:** 2026-11-19 · **Game:** WWF No Mercy (N64, 2000), NTSC-U Rev-A (1.1)
**Purpose:** wire the four Bannon characters' signature moves to real No Mercy
animation clips (file IDs, AnimIDs, clip files, frame counts, P1/P2).

**Bank status:** the animation bank was re-extracted with the W3c-corrected
decode (PR #1755, merged 2026-11-19). All frame counts in this doc were
verified against the new manifest: all 57 table rows match exactly.

## How the mapping was derived (audit trail)

### Sources (in order of authority)

1. **AKI-Club/VPWStudio** (public GitHub repo) — `MenuItems_Moves.cs` defines the
   move-menu entry: each move carries `AnimID` = animation file ID **− 0x3322**
   ("animation ID (-3322)", 3322 hex), plus `RepeatAnimID`, `MasterMoveID`,
   `MoveLink`, `DamageInfo`, `PreviewPos`. `DefaultGameData.cs`
   (NoMercy_NTSC_U_11) gives the constants: `FirstAnimationFileID = 0x2DD9`,
   `FirstMoveAnimationID = 0x3322`, `MoveAnimationFileID = 0x01F0` (the move
   menu data lives in ROM file 0x1F0), `MoveDamageFileID = 0x01EF`. VPWStudio
   is the *parser*, not the data — the move names come from the sources below.
2. **western-heart `moveset-library/movesets/mat-kings-move-database.json`**
   (2.3 MB, built 2026-10-20) — programmatic join of `animations/manifest.json`
   + `tools/NoMercy-FileTableDB.txt` labels + re-docs power tables: all **4,409
   move clips** with `file_id`, `anim_id`, `source_label` (`[Category] Name
   P1/P2`), `category`, power/slot data where known. This is the move table.
3. **western-heart `teardown/wwf-no-mercy/tools/NoMercy-FileTableDB.txt`** —
   the raw AKI-Club community file-label DB (19,462 ROM files). Every label used
   here was cross-checked against the raw lines (e.g. `37EE=AkiAnimation;[Front
   Special Grapple] Stone Cold Stunner P1`).
4. **`work/manifest-old.json`** — the animation-bank manifest (5,762 clips).
   Frame counts in this doc are derived from it via the correction below.
5. **Moveset corroboration (public sources)** — *WWF No Mercy Official Prima
   Guide* (Prima, 2000; archive.org full text), Tetzcatlipoca's *WWF No Mercy
   FAQ* v2.1 (GameFAQs, complete numbered movesets for Rock/HHH/Austin/
   Undertaker/Kane/Mankind/Jericho/Angle/Benoit), Ed Butler's *FAQ/Move List*
   v1.9 (numbered movesets for Al Snow/Albert/Andre/Bossman/Bradshaw/Bulldog/
   Buh Buh Ray/Bull Buchanan), SPOON's *Moves Guide* (power/attack-point data).
   These pin down *which numbered variant* each wrestler actually uses
   (e.g. Austin's Lou Thesz Press is the Knuckle variant; Angle's German is
   the German Suplex Pin; Shamrock's Ankle Lock is the face-down Special).
6. **western-heart docs** — `teardown/wwf-no-mercy/docs/ANIMATION-ISOLATION.md`
   (§1, §6: AnimID linkage, bank ranges), `docs/anim/AKI-BAKE-ROCK-2026-10-21.md`
   (W3b Finding 1: the extraction-window correction; W3c true frame counts for
   the 11 Rock clips), `teardown/wwf-no-mercy/animations/FORMAT.md`.

### Validation

- **6/6 known-good Rock clips match exactly** in the move table (name, AnimID,
  file ID): Rock Bottom 0x4D8/0x37FA, People's Elbow grounded 0xB1B/0x3E3D,
  People's Elbow running 0xD91/0x40B3, Rock Spinebuster 0x75D/0x3A7F, Rock
  Stomp 0xC30/0x3F52, Rock Spinning DDT 0xE4B/0x416D. The other 5 Rock clips
  in `aki-rock-v3/` resolve to taunts (Entry Way / In The Ring / Taunt 01–03),
  as expected.
- **Frame-count correction validated 11/11.** The `.npy` bank in the repo still
  holds the pre-W3c shifted decode: repo clip `fid` = game file `fid + 0x19`
  (W3b Finding 1), so the manifest's raw `nframes` for non-Rock clips is the
  *wrong file's* length. True frames for game file `fid` =
  `manifest-old[fid − 0x19].nframes`. Tested against the 11 W3c-verified Rock
  frame counts: **11/11 match** (e.g. Rock Bottom: manifest-old[0x37E1] = 70 =
  true). All frame counts below use this correction; confirmed against the
  re-extracted bank (PR #1755): all 57 table rows match the new manifest
  exactly (AnimID + frame count).
- **Move-table structure.** A move usually has a **P1** clip (attacker) and a
  **P2** clip (victim), adjacent AnimIDs. Submissions/pins add phase clips:
  initial, `(Repeat)` loop, `(Release)`, `(Win)`, `(Break Up)`. `(Reversal N)`
  clips are the move performed *in reverse* (roles swapped). Some move families
  have **no dedicated P2** — running attacks and Irish-whip grapples use a
  generic victim reaction from the unlabeled system range (see § "No dedicated
  P2" below). Strikes with no P1/P2 suffix are single-performer clips.

### Key facts

- File IDs are **1-based, game-exact**: FileTable @ ROM `0x16C31D8`,
  FirstFile `0x1BD150`. System anims `0x2DD9–0x3321` (1,353 clips); move anims
  `0x3322–0x4473` (4,434 clips). `AnimID = file_id − 0x3322`.
- **Rhino and Rob Van Dam are NOT in No Mercy** (both debuted in WWF in 2001).
  Their moves map to shared/generic clips in the game's pool, or to the nearest
  equivalent where the move doesn't exist at all (Rolling Thunder, Van
  Daminator). Angle (id 3) and Austin (id 4) ARE in the game, so their
  signature moves are exact named matches.
- Clip files are named `anim_XXXX.npy` where `XXXX` is the hex file ID, in
  `teardown/wwf-no-mercy/animations/clips/`. The bank was re-extracted with
  the W3c-corrected decode in PR #1755 (merged 2026-11-19), so the `.npy`
  files now hold game-exact motion.

## Confidence key

- **HIGH** — exact named match in the move table, corroborated by moveset
  sources where applicable.
- **MEDIUM** — right move family; the specific numbered variant is the best
  pick on the available evidence but its visuals are not yet confirmed (needs
  the re-extracted bank / a watch-through).
- **LOW** — the move does not exist in No Mercy; nearest available equivalent
  only (part of the move, or the kick half without the prop).

## Master mapping table

★ = best pick for that move. Frames are W3c-corrected (see Method).

| Bannon character | Move (Bannon / real) | AnimID hex (dec) | Clip file | Frames | P1/P2 | Notes / confidence |
|---|---|---|---|---|---|---|
| Stone Core (Austin) | ★ Stunner / Stone Cold Stunner | 0x4CC (1228) | anim_37EE.npy | 36 | P1 | Front Special Grapple, front finisher slot. Power S, KO. HIGH |
| Stone Core (Austin) | ★ Stunner / Stone Cold Stunner | 0x4CD (1229) | anim_37EF.npy | 39 | P2 | Victim side. HIGH |
| Stone Core (Austin) | ★ Lou Thesz Press (Knuckle) | 0x764 (1892) | anim_3A86.npy | 26 | P1 | Irish Whip Grapple. Austin's actual variant (Prima + Tetzcatlipoca both list Knuckle, not Pin). HIGH |
| Stone Core (Austin) | Lou Thesz Press Knuckle — Reversal 1 (victim-side candidate) | 0x766 (1894) | anim_3A88.npy | 21 | P2 (Rev 1) | No plain P2 exists; this is the nearest victim-side clip (see § No dedicated P2). MEDIUM |
| Stone Core (Austin) | Lou Thesz Press Pin (alternate) | 0x695 (1685) | anim_39B7.npy | 18 | P1 | The pin variant — not Austin's. No plain P2. MEDIUM |
| Perk Spangled (Angle) | ★ Angle Slam / Olympic Slam | 0x4FA (1274) | anim_381C.npy | 42 | P1 | Front Special Grapple, front finisher slot. Power A, KO. Angle's finisher in-game. HIGH |
| Perk Spangled (Angle) | ★ Angle Slam / Olympic Slam | 0x4FB (1275) | anim_381D.npy | 37 | P2 | Victim side. HIGH |
| Perk Spangled (Angle) | ★ German suplex / German Suplex Pin | 0x588 (1416) | anim_38AA.npy | 22 | P1 | Back Strong Grapple. Angle's actual in-game German (Prima + Tetzcatlipoca). Pin/bridge finish — has Repeat/Release/Win/Break Up phases. HIGH |
| Perk Spangled (Angle) | ★ German suplex / German Suplex Pin | 0x589 (1417) | anim_38AB.npy | 22 | P2 | Victim side. HIGH |
| Perk Spangled (Angle) | German suplex (plain) / German Suplex 01 | 0x550 (1360) | anim_3872.npy | 34 | P1 | Back Strong Grapple. The standard plain German (Al Snow's). Use if Bannon wants a clean throw, not a pin. HIGH |
| Perk Spangled (Angle) | German suplex (plain) / German Suplex 01 | 0x551 (1361) | anim_3873.npy | 28 | P2 | Victim side. HIGH |
| Perk Spangled (Angle) | German suplex / German Suplex 02 | 0x560 (1376) | anim_3882.npy | 32 | P1 | Variant — visuals unconfirmed. MEDIUM |
| Perk Spangled (Angle) | German suplex / German Suplex 02 | 0x561 (1377) | anim_3883.npy | 35 | P2 | Victim side. MEDIUM |
| Perk Spangled (Angle) | German suplex / German Suplex 03 | 0x558 (1368) | anim_387A.npy | 35 | P1 | Variant — visuals unconfirmed. MEDIUM |
| Perk Spangled (Angle) | German suplex / German Suplex 03 | 0x559 (1369) | anim_387B.npy | 35 | P2 | Victim side. MEDIUM |
| Perk Spangled (Angle) | German suplex / German Suplex 04 | 0x55A (1370) | anim_387C.npy | 31 | P1 | Variant — visuals unconfirmed. MEDIUM |
| Perk Spangled (Angle) | German suplex / German Suplex 04 | 0x55B (1371) | anim_387D.npy | 29 | P2 | Victim side. MEDIUM |
| Perk Spangled (Angle) | ★ Rolling Germans / Multiple German Suplex | 0x671 (1649) | anim_3993.npy | 10 | P1 | Back Special Grapple, back finisher slot. Benoit's special in-game; the Repeat clips (1651/1652, 78f) are the looped suplex cycle. HIGH |
| Perk Spangled (Angle) | ★ Rolling Germans / Multiple German Suplex | 0x672 (1650) | anim_3994.npy | 10 | P2 | Victim side. HIGH |
| Perk Spangled (Angle) | ★ Ankle lock / Ankle Lock (Special, face down) | 0xD56 (3414) | anim_4078.npy | 27 | P1 | Special Ground Leg Grapple (Facing Down). Shamrock's signature finisher version in-game (Prima: "Ankle Lock — opponent on mat, face down, near feet"). Has Repeat/Release/Win/Break Up phases. HIGH |
| Perk Spangled (Angle) | ★ Ankle lock / Ankle Lock (Special, face down) | 0xD57 (3415) | anim_4079.npy | 27 | P2 | Victim side. HIGH |
| Perk Spangled (Angle) | Ankle lock / Ankle Lock (Ground, face up) | 0xC8A (3210) | anim_3FAC.npy | 23 | P1 | Ground Leg Grapple (Facing Up). The standard non-special ground ankle lock. HIGH |
| Perk Spangled (Angle) | Ankle lock / Ankle Lock (Ground, face up) | 0xC8B (3211) | anim_3FAD.npy | 23 | P2 | Victim side. HIGH |
| Perk Spangled (Angle) | Ankle lock / Standing Ankle Lock (counter) | 0x92C (2348) | anim_3C4E.npy | 22 | P1 | Special Counter Kick — a kick counter, not a ground hold. Alternate only. MEDIUM |
| Perk Spangled (Angle) | Ankle lock / Standing Ankle Lock (counter) | 0x92D (2349) | anim_3C4F.npy | 22 | P2 | Victim side. MEDIUM |
| Wildebeest (Rhino) | ★ Gore / Spear | 0x898 (2200) | anim_3BBA.npy | 26 | P1 | Running Attack. The game's only spear (Edge's trademark; also Linda McMahon's running attack). The Gore IS a spear. HIGH |
| Wildebeest (Rhino) | Gore / Spear — Reversal 1 (victim-side candidate) | 0x897 (2199) | anim_3BB9.npy | 12 | P2 (Rev 1) | No plain P2 exists; nearest victim-side clip. MEDIUM |
| Wildebeest (Rhino) | ★ Piledriver / Piledriver 01 | 0xBF (191) | anim_33E1.npy | 41 | P1 | Front Weak Grapple B. Power D. Strong-grapple-tier piledriver (Mankind's strong slot; Andre's weak slot). Best pick. HIGH as pick; variant visuals MEDIUM |
| Wildebeest (Rhino) | ★ Piledriver / Piledriver 01 | 0xC0 (192) | anim_33E2.npy | 43 | P2 | Victim side. HIGH as pick |
| Wildebeest (Rhino) | Piledriver / Piledriver 02 | 0xB7 (183) | anim_33D9.npy | 48 | P1 | Power E — the weak-grapple variant (Austin's, Albert's, Al Snow's, Mankind's weak slot). MEDIUM |
| Wildebeest (Rhino) | Piledriver / Piledriver 02 | 0xB8 (184) | anim_33DA.npy | 51 | P2 | Victim side. MEDIUM |
| Wildebeest (Rhino) | Piledriver / Piledriver 03 | 0xBD (189) | anim_33DF.npy | 52 | P1 | Power D (British Bulldog's, Buh Buh Ray's weak slot). MEDIUM |
| Wildebeest (Rhino) | Piledriver / Piledriver 03 | 0xBE (190) | anim_33E0.npy | 54 | P2 | Victim side. MEDIUM |
| Wildebeest (Rhino) | Piledriver / Piledriver 04 | 0xBB (187) | anim_33DD.npy | 58 | P1 | Power D. No default user found in the completed movesets. MEDIUM |
| Wildebeest (Rhino) | Piledriver / Piledriver 04 | 0xBC (188) | anim_33DE.npy | 59 | P2 | Victim side. MEDIUM |
| Wildebeest (Rhino) | ★ Spinebuster / Spinebuster | 0x745 (1861) | anim_3A67.npy | 16 | P1 | Irish Whip Grapple. The generic spinebuster (Bradshaw's Irish-whip strong move). HIGH |
| Wildebeest (Rhino) | Spinebuster — Reversal 1 (victim-side candidate) | 0x744 (1860) | anim_3A66.npy | 25 | P2 (Rev 1) | No plain P2 exists; nearest victim-side clip. MEDIUM |
| Wildebeest (Rhino) | Spinebuster / Faarooq Spinebuster (alternate) | 0x760 (1888) | anim_3A82.npy | 13 | P1 | Farooq's trademark variant — a different, longer-setup spinebuster. No plain P2. MEDIUM |
| O. Godd Damme (RVD) | ★ Frog splash / Frog Splash | 0xDBD (3517) | anim_40DF.npy | 15 | P1 | Strong Flying Attack to Laying Opponent (top rope). Eddie Guerrero's finisher in-game. HIGH |
| O. Godd Damme (RVD) | ★ Frog splash / Frog Splash | 0xDBE (3518) | anim_40E0.npy | 7 | P2 | Victim side (short impact reaction — victim is already down). HIGH |
| O. Godd Damme (RVD) | Frog splash — extra clips (probable miss/landing) | 0xDBF–0xDC1 (3519–3521) | anim_40E1–40E3.npy | 16/12/19 | — | Three unlabeled "Frog Splash" clips after the P1/P2 pair; almost certainly the miss/landing variants (flying attacks follow this pattern). MEDIUM |
| O. Godd Damme (RVD) | ★ Rolling Thunder / Senton Splash 01 (impact half) | 0xD8C (3468) | anim_40AE.npy | 23 | P1 | Running Ground Attack. No "Rolling Thunder" exists in the game; this is the closest: a running senton onto a downed opponent = the impact half of Rolling Thunder. No P2 (running ground attacks are P1-only). MEDIUM |
| O. Godd Damme (RVD) | Rolling Thunder / Senton Splash 02 (alternate) | 0xD86 (3462) | anim_40A8.npy | 22 | P1 | Alternate running senton. MEDIUM |
| O. Godd Damme (RVD) | Rolling Thunder / Senton Splash 03 (alternate) | 0xD92 (3474) | anim_40B4.npy | 28 | P1 | Alternate running senton. MEDIUM |
| O. Godd Damme (RVD) | ★ Van Daminator / Back Spinning Heel Kick (kick half) | 0x835 (2101) | anim_3B57.npy | 25 | — | Strong Striking, single clip (no P1/P2 split). No Van Daminator exists in the game and no chair-assisted kick exists; this is the closest named kick — a spinning heel kick to a standing opponent. The chair prop + victim reaction would have to be composited. LOW–MEDIUM |
| O. Godd Damme (RVD) | Van Daminator / Spinning Wheel Kick 01 (alternate) | 0x7C8 (1992) | anim_3AEA.npy | 17 | P1 | Strong Striking alternate kick, with P2 0x7C9 (1993), anim_3AEB.npy, 7f. MEDIUM |
| O. Godd Damme (RVD) | Van Daminator / Spinning Wheel Kick 03 (alternate) | 0x869 (2153) | anim_3B8B.npy | 33 | P1 | Running Attack alternate kick (delivered on the run, closer to how RVD throws it). MEDIUM |

---

## Per-move notes

### Stone Core (Steve Austin)

**Stunner — exact, HIGH.** `Stone Cold Stunner` is Austin's front-grapple
finisher in the game (Prima + Tetzcatlipoca). Power S, KO-capable, front
finisher slot. Other stunners in the bank, for reference only: `Mac Stunner`
P1 0x4EC (1260, anim_380E, 37f) / P2 0x4ED (1261, anim_380F, 43f);
`Counter Stunner` P1 0x938 (2360, anim_3C5A, 49f) / P2 0x939 (2361, anim_3C5B,
52f) — a counter-kick stunner.

**Lou Thesz Press — Knuckle variant, HIGH for P1.** Two variants exist:
*Knuckle* (press + punches) and *Pin* (press into a pin). Austin's default
moveset uses the **Knuckle** variant in his Irish Whip Grapple—Strong slot
(confirmed in both the Prima guide and Tetzcatlipoca's complete Austin
moveset), so Knuckle P1 0x764 is the pick. Neither variant has a plain P2
clip (see § No dedicated P2). Phase clips for Knuckle: Reversal 1 P1/P2
0x765/0x766 (21f each); Release 0x769/0x76A (23f/26f, no P1/P2 suffix —
first is attacker, second victim, by the bank's pair ordering); Win
0x76B/0x76C (1f each — single-frame poses); Break Up 0x76D/0x76E (26f/19f).
Pin phases: Reversal 1 0x69A/0x69B (17f), Reversal 1 Repeat 0x69C/0x69D
(10f), Release 0x69E/0x69F (13f/14f), Win 0x6A0/0x6A1 (36f/43f), Break Up
0x6A2/0x6A3 (11f each).

### Perk Spangled (Kurt Angle)

**Olympic Slam (= Angle Slam) — exact, HIGH.** The move was called the
Olympic Slam in 2000 (renamed Angle Slam in 2001–02); in No Mercy it is
Angle's front-grapple special, power A, KO-capable.

**German suplex — two best picks depending on use, HIGH.** Angle's actual
in-game German is the **German Suplex Pin** (Back Strong Grapple, both
directions; Prima + Tetzcatlipoca). It ends in a pinning bridge, so it
carries the full pin-phase set: Repeat 0x58A/0x58B (16f), Release
0x58C/0x58D (14f/17f), Win 0x58E/0x58F (16f/15f), Break Up 0x590/0x591
(15f/16f). If Bannon wants a clean throw with no pin attached, use
**German Suplex 01** (Al Snow's back-strong German). German Suplex 02/03/04
are unassigned variants in the completed movesets — their visuals differ in
ways the labels don't capture (bridge vs release vs angle); confirm from the
re-extracted bank before using one over 01. **Multiple German Suplex** is
Benoit's back-grapple special in-game and is the rolling-Germans sequence:
the 10f P1/P2 are the setup, and the 78f Repeat pair (0x673/0x674) is the
looped suplex cycle. Angle's real-life rolling Germans = this clip.

**Ankle lock — Special face-down version, HIGH.** Three Ankle Locks exist:
(1) **Special Ground Leg Grapple (Facing Down)** 0xD56/0xD57 — Ken Shamrock's
signature finisher in-game (Prima, hidden-characters chapter: "Ankle Lock —
opponent on mat, face down, near feet"). This is the finisher-grade hold and
the best pick for Angle's signature submission. Phases: Repeat 0xD58/0xD59
(19f), Release 0xD5A/0xD5B (20f/18f), Win 0xD5C/0xD5D (31f/29f), Break Up
0xD5E/0xD5F (20f/15f). (2) **Ground Leg Grapple (Facing Up)** 0xC8A/0xC8B —
the standard non-special ground ankle lock (opponent face up); phases Repeat
0xC8C/0xC8D (16f), Release 0xC8E/0xC8F (28f/11f), Win 0xC90/0xC91 (51f/46f),
Break Up 0xC92/0xC93 (11f/12f). (3) **Standing Ankle Lock** 0x92C/0x92D — a
Special Counter Kick (counter to a kick), not a ground hold; alternate only.
Note: Angle does *not* have the Ankle Lock in his No Mercy default moveset —
he adopted it in 2001, after the game's release (his in-game submissions are
the Armbar special and Rear Naked Choke). The hold itself is in the game's
move pool, so Bannon can give it to him.

### Wildebeest (Rhino)

**Gore — Spear, HIGH for P1.** No "Gore" exists (Rhino isn't in the game),
but the Gore is a spear and No Mercy has exactly one `Spear` (Running
Attack): P1 0x898. It is Edge's trademark running attack and also appears in
Linda McMahon's running attacks. No plain P2 exists; the nearest victim-side
clip is Spear P2 (Reversal 1) 0x897.

**Piledriver — 01 best pick, MEDIUM on variant visuals.** Four numbered
variants, all Front Weak Grapple B, all with P1/P2 pairs. What the movesets
say about who uses which:
- **01** (power D): Andre's weak slot, **Mankind's strong slot** — the only
  one of the four used in a strong grapple. Best pick for Rhino: strongest
  tier, power-move usage.
- **02** (power E): the weak-grapple variant — Austin's, Albert's, Al Snow's,
  and Mankind's weak slot. Weakest of the four.
- **03** (power D): British Bulldog's and Buh Buh Ray's weak slot.
- **04** (power D): no default user found in the completed movesets
  (Tetzcatlipoca 9 + Ed Butler 8 wrestlers).
The 01–04 numbers are the game's own numbering; what visually distinguishes
them (setup, drop style, landing) is not in any label or FAQ. Confirm from
the re-extracted bank before finalizing. For reference, the Tombstone
Piledriver (Undertaker/Kane finisher, power S, KO, bleed) is P1 0x4F6
(1270, anim_3818, 90f) / P2 0x4F7 (1271, anim_3819, 90f) — not Rhino's move,
listed so it isn't confused with the numbered four.

**Spinebuster — generic, HIGH for P1.** The plain `Spinebuster` (Irish Whip
Grapple) P1 0x745 is Bradshaw's Irish-whip strong move. No plain P2 exists;
nearest victim-side clip is Spinebuster P2 (Reversal 1) 0x744. The
**Faarooq Spinebuster** P1 0x760 is Farooq's trademark variant (a different,
longer-setup spinebuster — his in-game trademark per Tetzcatlipoca); use it
only if Rhino's spinebuster should read as a distinct signature rather than
the generic one. The Rock Spinebuster (0x75D, already known-good) is Rock's
own variant, not Rhino's.

### O. Godd Damme (Rob Van Dam)

**Frog splash (Five-Star Frog Splash) — exact, HIGH.** `Frog Splash` is
Eddie Guerrero's finisher in No Mercy (Strong Flying Attack to Laying
Opponent — a top-rope move): P1 0xDBD / P2 0xDBE. The three following
unlabeled `Frog Splash` clips (0xDBF–0xDC1) follow the flying-attack pattern
of hit-P1 / victim-P2 / miss-and-landing variants; treat as probable
miss/landing clips until the re-extracted bank confirms.

**Rolling Thunder — NO exact match, MEDIUM (impact half only).** Nothing
called Rolling Thunder exists in the game (RVD isn't in it), and no clip
combines a forward roll with a senton. The closest available piece is the
**Senton Splash** family in Running Ground Attack — a running senton onto a
downed opponent, which is the impact half of Rolling Thunder: 01 P1 0xD8C
(best pick — first-listed), 02 P1 0xD86, 03 P1 0xD92. Running ground attacks
have no P2 clips at all (the victim is already down). The forward-roll entry
has no named clip anywhere in the bank (the system range 0x2DD9–0x3321 is
almost entirely unlabeled, so a roll clip may exist there unidentified).
Bannon options: use Senton Splash 01 alone (loses the roll), or composite a
roll from the system bank once it is labeled, or build the roll-in as new
motion. `Rolling Hangover` (0xE06/0xE07, Flying Attack) is a top-rope move,
not Rolling Thunder. `Fire Thunder` / `Blue Thunder Pin` are unrelated
("Thunder" is just the name).

**Van Daminator — NO exact match, LOW–MEDIUM (kick half only).** The move is
a chair held against the opponent's face + a spinning heel kick driving it
in. No Mercy has no chair-assisted kick and no Van Daminator. The closest
named kick is **Back Spinning Heel Kick** 0x835 (Strong Striking, single
clip, no P1/P2 split — a spinning heel kick to a standing opponent).
Alternates: Spinning Wheel Kick 01 P1 0x7C8 (+ P2 0x7C9) and Spinning Wheel
Kick 03 P1 0x869 (Running Attack — delivered on the run, closer to how RVD
throws it). Any Van Daminator in Bannon needs the chair prop and the victim
reaction composited around one of these kicks; no clip in the bank does the
chair part.

## No dedicated P2 — what the game does instead

For **Spear, Spinebuster, Lou Thesz Press (both variants), and all Running
Ground Attacks**, the bank contains no plain victim clip. This is structural,
not a gap in this research: in AKI's engine, running attacks and Irish-whip
grapples play a generic victim reaction (knockdown/fall) drawn from the
system anim range `0x2DD9–0x3321`, which is almost entirely unlabeled in the
FileTableDB (1,307 of 1,353 system clips carry the label `(system)`).
Practical options for Bannon, in order of fidelity:
1. Use the **(Reversal 1) P2** clip listed for each move — it is a real
   victim-side clip of that same move (roles swapped), so the body mechanics
   match even if the entry differs.
2. Use a generic knockdown from the system range once the re-extract/labeling
   pass identifies the fall clips.
3. For the Lou Thesz Press specifically, the **(Release)/(Win)/(Break Up)**
   second clips (0x76A/0x76C/0x76E Knuckle; 0x69F/0x6A1/0x6A3 Pin) are
   victim-side clips of the hold's endings and can stand in for the victim
   during/after the press.

## Sanity check — known-good Rock clips (all confirmed in the move table)

| Move | AnimID | Clip file | Frames (W3c true) |
|---|---|---|---|
| Rock Bottom P1 | 0x4D8 (1240) | anim_37FA.npy | 70 |
| Rock Bottom P2 | 0x4D9 (1241) | anim_37FB.npy | 68 (corrected) |
| People's Elbow (grounded) P1 | 0xB1B (2843) | anim_3E3D.npy | 112 |
| People's Elbow (running) P1 | 0xD91 (3473) | anim_40B3.npy | 39 |
| Rock Spinebuster P1 | 0x75D (1885) | anim_3A7F.npy | 13 |
| Rock Stomp | 0xC30 (3120) | anim_3F52.npy | 20 |
| Rock Spinning DDT P1 | 0xE4B (3659) | anim_416D.npy | 28 |
| Rock — Entry Way Taunt | 0x1089 (4233) | anim_43AB.npy | 102 |
| Rock — In The Ring Taunt | 0x10AD (4269) | anim_43CF.npy | 103 |
| Rock — Taunt 02 | 0x10FB (4347) | anim_441D.npy | 82 |
| Rock — Taunt 01 | 0x1101 (4353) | anim_4423.npy | 17 |
| Rock — Taunt 03 | 0x1102 (4354) | anim_4424.npy | 24 |

## Open items

1. **Variant visuals** — Piledriver 01 vs 02 vs 03 vs 04 and German Suplex 01
   vs 02 vs 03 vs 04 differ in ways no label or FAQ captures. Now that the
   re-extracted (game-exact) bank has landed (PR #1755), watch the P1 clips
   and confirm the picks (01 in both cases) — or swap if another variant
   reads better.
2. **Frame counts** — all non-Rock counts here come from the validated −0x19
   correction (11/11 on the Rock clips). **Confirmed 2026-11-19 against the
   re-extracted bank (PR #1755): all 57 table rows match the new manifest
   exactly (AnimID + frame count).**
3. **Generic victim reactions** — the system range (0x2DD9–0x3321) needs
   labeling to find the fall/knockdown clips the Spear, Spinebuster, Lou
   Thesz Press, and running ground attacks pair with, and to check whether a
   forward-roll clip exists for Rolling Thunder's entry.
4. **Frog Splash extras (0xDBF–0xDC1)** — confirm they are the miss/landing
   variants.
5. **Rhino/RVD roster note** — neither man is in No Mercy, so no
   wrestler-specific clips (taunts, entrances, signatures) exist for them;
   only the shared move pool applies. Their taunts/entrances would need to
   come from generic taunts in the bank or be built new.
