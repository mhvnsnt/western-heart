# King of Colosseum II — Research Summary

**Game:** King of Colosseum II (キング オブ コロシアム II) · **Dev/publisher:** Spike ·
**Platform:** PlayStation 2, Japan-only · **Released:** 9 September 2004 ·
**Game ID:** SLPM-65602 · **Genre:** 3D pro-wrestling sim

**Lane:** E (KoC2) · **Date:** 2026-11-19 · **Owner priority:** TOP 2, with
Virtual Pro Wrestling 2 (Lane D). **Status:** research complete; ISO sourced
from archive.org; extraction in progress (see TEARDOWN.md in this dir once
landed).

All mechanics below are summarized in our own words from the cited sources.
No third-party text is copied verbatim into this repo. The one full public
systems document is Jerrold Ng's FAQ/Movelist v1.0 (10 Oct 2004); it is a
*reference*, not repo content.

## Why it matters

CAGEMATCH rates KoC2 **#4 of all wrestling games, 9.64/10 (24 votes)** —
behind only Virtual Pro Wrestling 2 (9.75), Total Extreme Wrestling 2013
(9.71) and Fire Pro Wrestling Returns (9.70), and ahead of SmackDown! Here
Comes The Pain (9.53). Players call it "as close to a perfect 3D wrestling
game as we have gotten" and "essentially a 3D version of Fire Pro wrestling"
(CAGEMATCH user ratings, 2015–2026). It is the game Mars was talking about:
the 3D Fire Pro successor, and the heart of the Bannon program alongside VPW2.

What makes it the heart:

1. **The deepest grappling system on PS2.** A timing-based "clutch" system
   with 6 front + 6 back grapple types, each holding 7 executable moves —
   84 grapple slots before strikes, ground, corner, aerial, apron, tag and
   shoot-mount moves. Moves run "into the thousands, perhaps the most for
   any wrestling game" (FAQ).
2. **A crowd-psychology system that judges the match.** Every match ends
   with an Audience Ranking percentage. The crowd hates one-sided beatings,
   rewards variety, match length, proper escalation (weak → strong), style
   fidelity, and near-falls. In Survival Road the ranking decides your
   rewards. This is the same idea as Neckbreaker's Crowd Momentum and
   Lane C's crowd-momentum work (P8) — from the match-quality side rather
   than the performance-feedback side.
3. **A roster of ~200 real wrestlers** across NJPW, AJPW, NOAH, ZERO-1 and
   WJ (World Japan), each with signature moves, up to 4 costume sets, and
   unlockable legends (young versions, retired greats) bought in the Secret
   Shop. Unlockables include non-wrestlers (e.g. Mike Tyson, per CAGEMATCH
   reviewers).
4. **A full promoter mode (Match Maker)** and a complete create-a-wrestler
   system with point-budgeted skills, 26 wrestling styles, 40 counter
   styles, and a percentage-based AI behavior editor (COM Logic) — a
   complete, editable AI spec shipped in the game.

## The grappling system (the clutch system)

- **Initiate:** hold R1 + one of six buttons (Square, Cross, Circle,
  Triangle, Square+Cross, Triangle+Circle) = six clutch types from the
  front; six more from the back. Not every wrestler has a distinct clutch
  in every slot.
- **Execute:** after the clutch locks, press a second button at the right
  moment (Square, Cross, Circle, Triangle, R1, or a Powerball pair) to
  perform the move. Each clutch has its own timing window; button-mashing
  fails. Missing the timing means reversal or a broken grapple.
- **Escalation is enforced:** big moves attempted early in a match are
  automatically countered. The game makes you work weak → strong, like a
  real Japanese match: strikes and weak grapples, then submissions and
  stronger grapples, then big impact moves, finishers and close kickouts.
- **Fatigue is Fire Pro-like:** wrestlers visibly get winded; stamina
  governs reversal success (fresh = reverses easily, gassed = can't) and
  how much energy each action costs. Breathing (L1) restores stamina.
- **Reversals** are timing-based and blend into the move animation; there
  are distinct reversal families per grapple position, each opening
  different follow-ups. Strike defense: R2 blocks/swipes; a perfectly
  timed R2 counters (punches: two counter types; kicks: catch into a
  dragon-screw clutch).
- **Ground game:** six ground-attack sets (opponent face up/down × near
  head/side/feet); pins live in the "by the side" sets. Drag, flip, and
  pick-up into a clutch from the ground. Downed players can roll, crouch
  on getting up to avoid grapples, and mash out of pins.
- **Corners:** corner strikes, running corner strikes, corner grapples
  (4 strengths), tree-of-woe setup, and at least one corner-to-corner
  special (Marufuji's dropkick, Powerball).
- **Aerial:** top-rope moves (climb speed varies by wrestler; some can't
  climb; lightweights can run up) and climbing moves (no perch needed).
  Some aerials need the opponent in the right position/orientation.
- **Apron/outside:** hammer throws can send opponents to the apron or out
  of the ring; apron grapples, slingshot moves, apron dives, running
  attacks to the outside.
- **Tag:** tag out (L1 at partner), call partner (Select, ~once per couple
  of minutes), front/back double teams (both press Square), corner double
  teams (cost a Powerball).
- **Headlock / full nelson:** from the Triangle clutch, R2 puts the
  opponent in a headlock (drag anywhere, then strike) or, from the back,
  a full nelson (holds him open for the tag partner).
- **Shoot fighting:** separate rules (KO/submission only, no ring exit in
  Vale Tudo) with four mounts (Guard, Full, Back, Clutch) and "instant
  submissions" — lethal holds only available from mounts, only when the
  opponent is very weak, instant tap-out on lock-on.
- **Match rules:** Puroresu, Vale Tudo (rounds, KO/sub only), Ultimate
  Crush (NJPW shoot rules, 3×5-min rounds), U-Style (UWF rules, 15 min,
  TKO counter — 5 prolonged knockdowns loses), American (everyone can
  power up by taunting, finishers do far more damage), MUGA (American +
  hardcore traits), Free (mix and match).

## The Powerball system (finishers as a scarce resource)

- Each wrestler starts with **1–4 Powerballs** (weaker wrestlers fewer;
  CAW can buy 0–5 with edit points). All are available at the start; none
  regenerate during the match.
- Powerball moves (mapped to Square+Cross or Triangle+Circle) do much more
  damage, connect more easily, and Powerball submissions make the opponent
  tap sooner and restrict rope escapes. Many moves are "Powerball only."
- **One regain per match**, only after spending all Powerballs: kick out
  at 2.9 while nearly out of energy, fight out of a Powerball submission
  while nearly empty, kick out of a Powerball move ending in a pin, or
  catch/reverse a Powerball strike — then taunt within 30 seconds of game
  time. The regain is earned by surviving something huge, then playing to
  the crowd. This is a crowd-psychology mechanic wearing a resource skin.

## The crowd-psychology system (Audience Ranking)

A percentage shown at the end of every match: how much the crowd
appreciated the match. In Survival Road it decides what you are rewarded;
elsewhere it is the score for "did you put on a good match." The known
factors, from the FAQ's tips (player-observed, not datamined):

1. **Parity.** Crowds hate one-sided beatings. The closer both wrestlers'
   stamina at the end, the better. You must let the opponent get offense in.
2. **Variety.** Repeating the same move or clutch hurts. Work all over:
   corners, outside, different attack types.
3. **Length.** Longer is better if it isn't one-sided or repetitive;
   20+ game minutes scores well. High-stamina top-tier wrestlers have the
   best shot at great matches.
4. **Escalation.** Start weak, build to strong — the same rule the
   reversal system enforces mechanically.
5. **Style fidelity.** Technical wrestlers should work pins/submissions,
   juniors aerials, hardcore types blood and weapons.
6. **Near-falls.** Lots of pinfalls; 2.999 kickouts are a crowd favorite.
   You can manually break your own pin (Cross) to set them up, and time
   kickouts to 2.999.
7. **Crowd Favor.** A match option skews the crowd toward a federation or
   a fighting style. Booking the wrong style for the crowd tanks the
   rating (e.g. a shoot-fighting crowd watching a wrestling match).
8. **Match Maker ties in:** each show has attendance + average-rating
   targets; booking good cards against rising targets is the mode's
   progression. Computer-controlled matches usually rate poorly — you are
   expected to play the matches you book.

Design note for Bannon: KoC2's ranking is *retrospective* (judged at the
end), while Neckbreaker's Crowd Momentum is *live* (energy rises/falls
during the match and feeds back into performance). Bannon wants both:
KoC2's match-quality judgment as the scoring brain, Neckbreaker's live
momentum as the in-match feedback. See Bannon `docs/koc2/` wiring specs.

## Roster structure

- **Federations:** NJPW, NOAH, AJPW, ZERO-1, WJ (World Japan), plus FREE
  and Template heads in edit mode.
- **Per wrestler:** profile (fed, name/short+long, nickname, weight class:
  Light Heavyweight / Heavyweight / Super Heavyweight / Free, home
  country from a 40-country list, size SS/S/M/L/LL — size drives how
  easily he is lifted, weight/height, birthday, wrestle style, defensive
  style, counter style, 2 voice sets, favorite color for streamers,
  popularity Low/Medium/High — how much the crowd cheers him).
- **Costume sets:** up to 4 per wrestler; each set can carry a different
  moveset (e.g. Kensuke Sasaki). Extra costumes/movesets are unlockables.
- **Templates:** Secret Shop sells wrestler *templates* (renamed/recolored
  to dodge likeness issues); the player rebuilds the real wrestler from
  the template in Edit mode (profile/appearance/skill/parameter/moves/
  COM Logic all loadable from the template). This is how the game ships
  ~200 wrestlers without ~200 full edit slots.
- **Wrestle styles (26):** Orthodox, Technical, Wrestling, Ground, Power,
  Strong Shooter, American, Highspot, All Around, Genius, Revolution,
  Junior, Luchador, Heel, Mysterious, Shooter, Fighter, Grappler, Striker,
  Free Fighter, Stacie (Gracie), Panther, Giant, Vicious, King's Road,
  Beast (Bob Sapp style). Style affects animations and move compatibility:
  a move with low compatibility to your style is easier to counter/avoid.
- **Counter styles (40):** the same 26 plus 14 wrestler-unique types
  (Iizuka, Kido, Hase, Ogawa, Kawada, Asako, Marufuji, Low-Ki, Ka Shin,
  Tanaka, Misawa, Akiyama, Kobashi, Nakamura).

## Edit mode (create-a-wrestler) — data model

Six sub-menus, all point-budgeted (edit points bought in the Secret Shop):

- **PROFILE** — as above.
- **APPEARANCE (normal):** head (sorted by fed; hundreds of heads),
  standing pose, body shape, height, costume type (9: tights, karate gi,
  long pants, T-shirt+pants, tucked long pants, tucked pants w/ belt,
  track suits, boxer shorts, corporate suit), glasses, chest (5: bare,
  bare w/ tattoos, T-shirts, body suits/shirts, T-shirts w/ logos), elbows
  L/R, gloves L/R, lower body (5 tight lengths), knees L/R, boots. Every
  part recolorable; the game "suggests" the real wrestler's colors.
- **APPEARANCE (entrance):** entrance mask, entrance costume (capes,
  shoulder pads), costume design, glasses, title belts worn to the ring,
  held items (barbed wire to katanas), announce type, entrance theme
  (large music library; "(C)" tracks have crowd chants), announce name,
  ring announce.
- **SKILL (point costs):** Powerballs 0–5 (0/10/15/20/25/30 pts);
  Critical type (None / Finisher only / Suplexes / Power moves / Technical
  / Striking / Submissions — criticals are instant KOs); Recovery,
  Recovery (bleeding), Breathing, Breathing (bleeding), Awareness,
  Awareness (bleeding) — each Weak/Medium/Strong; Neck/Arm/Waist/Leg
  strength — Low/Medium/Strong/Injured; Movement speed; Climbing
  (cannot / normal / quick / run-up); Mode skills; Skill package (3
  sub-skills, preset or custom).
- **PARAMETER (offense/defense pairs):** Punch, Kick, Suplex, Submission,
  Stretch, Power/Instant Power/Arm Power (offense), Technique, Roughneck,
  Shootfighting; defense adds Flying, Crushing, Lariat.
- **MOVES:** 271 slots in 34 categories (see
  `assets/moves/koc2-moveset-slots.json` in Bannon for the full machine-readable
  list): standing strikes, running attacks, running counters, corner
  attacks, 12 clutch-type slots (6 front + 6 back) × 7 moves each,
  counter back clutch, ground (face up/down × head/side/feet), lifting,
  seated, kneeling, all-fours, aerial (top rope + climbing), dives to
  outside, apron attacks/grapples, counters (incl. kick-catch → dragon
  screw), double teams, taunts (4, right stick), entrance (walk, stage
  taunt, mid-point taunt, ring entry, idle, intro taunt), win animation.
  Up to **4 specialty moves** (lock on easier, +damage) and **1 finisher**
  (much more damage, renamable). A move set as specialty/finisher applies
  everywhere it appears in the list. Voice clips attach per move.
- **COM LOGIC:** percentage-based AI behavior tables — see below.
- **Quick Save/Load:** memory-card slots; clones (same wrestler, different
  costume/moveset/profile) cost extra slots.

## COM Logic — the shipped AI spec

20 behavior tables; each row is a situation (what the opponent is doing ×
opponent injury level: Light / Medium / High / Near Defeat) with
percentage chances across a set of actions. The tables: opponent standing;
opponent groggy (front/back); front grapple; back grapple; back-capture
counter; hammer throw (destination + after-rebound); opponent in corner;
downed opponent (face up/down, seated, kneeling, all fours); opponent near
corner; opponent near ropes; opponent outside; apron maneuvers; taunt set 1
(by opponent state); taunt set 2 (after specialty/finisher); mount
maneuvers (4 mounts); guarding (punches/kicks); counter mount; finisher
taunts; one untranslated table; other tendencies (breathing, dragging to
middle, escaping outside, weapon use — Often/Little). A wrestler with bad
COM Logic loses despite great stats — the AI is data, and it is editable.
This is the closest thing in any wrestling game to a published AI design
doc, and Bannon's AI should be built on this shape.

## Modes

- **Exhibition:** 1v1, tag, battle royal (3 targets), 5v5 elimination;
  match rules as listed above; Crowd Favor option.
- **Survival Road:** gauntlet; audience ranking decides rewards; Secret
  Shop sells templates, edit points, costumes, secrets (numbered, e.g.
  Secret 001 = Tatsumi Fujinami, 003 = young Chono, 005 = Seiji Sakaguchi).
  Five roads (NJPW/NOAH/AJPW/ZERO-1/WJ) + MMA and Legends roads unlockable;
  difficulties Easy/Normal/Hard + Super Hard/Master unlockable. Points
  earned per match = f(audience ranking, difficulty). 5–10 matches per
  road; Easy cannot finish (game over after 3 matches). The Secret Shop
  holds 165 secrets: 30 existing wrestlers (50–500 pts: young Chono,
  Super Generation Misawa/Kobashi/Taue/Kikuchi, NBM/Back-Promotion Mutoh,
  Great Muta at 500), 75 wrestler samples (20–100 pts: Brock Lesnar,
  Ric Flair, Bill Goldberg, Bob Sapp, Hulk Hogan, Andre the Giant,
  Bruiser Brody, Stan Hansen, Vader, Tiger Mask I/IV, Great Sasuke,
  Hayabusa, Atsushi Onita, Dynamite Kid, the Steiners, Hawk & Animal),
  42 MMA samples (20–100 pts: Mike Tyson, Fedor Emelianenko, Mirko Cro
  Cop, Rickson/Royce Gracie, Bas Rutten, Ken Shamrock, Dan Severn,
  Quinton Jackson, Mark Hunt, Kazushi Sakuraba, Minoru Suzuki), and 18
  etc. (13 extra rings — K-1, PRIDE FC, RINGS, UWFi, Michinoku Pro,
  Osaka Pro, Toryumon, DEEP, Wrestle-1, Indy, 1990s/1980s AJPW, Heisei
  Era — plus Super Hard/Master difficulty, MMA/Legend roads, and repeat
  +50 edit points up to 400).
- **Match Maker:** run a fed (NJPW/NOAH/AJPW/ZERO-1/WJ, each with a mentor:
  Chono, Misawa, Mutoh, Hashimoto). Book cards against attendance +
  average-rating targets; mentor advice; roster grows as targets rise.
- **Title Match:** 19 titles with default holders and full real-world
  title histories (IWGP Heavyweight/NWF/IWGP Tag/IWGP Jr/IWGP Jr Tag/U-30;
  GHC Heavyweight/Tag/Jr/Jr Tag; Triple Crown/AJPW Tag/AJPW Jr/All Asia
  Tag; NWA World/NWA IC Tag/NWA Jr; WMG Heavyweight/Tag).
- **Series:** leagues (2–32 entrants, single or split blocks) and
  tournaments (4/8/16/32, 1-day with accumulating fatigue vs series with
  fresh wrestlers), real named events or create-your-own.
- **Dojo:** training (tutorial in Japanese).
- **Edit:** original wrestler, default wrestler edit, create-a-fed,
  create-a-belt, etc.

## File formats / modding state (community knowledge)

- **Archive:** `KC2FIRE.001` — the main game archive. Files inside are
  individually compressed (`.comp`) and decompress to `.mdl` (models) and
  TIM2 (textures), among others.
- **Compression:** a custom LZSS variant. Decompression is solved and
  works (community scripts exist); byte-exact *compression* is the open
  problem — solved for TIM2 textures (Oct 2025), still open for models
  (May 2026, unresolved in the ResHax thread).
- **Textures:** TIM2 (standard PS2 format). PCSX2 texture dumping /
  replacement works; the modding community ships English menu textures,
  wrestler/ring/UI texture packs, and a save file (Discord + Google Drive,
  run by Pejiseven — human-gated access).
- **Models:** `.mdl` — community members are working on .mdl → OBJ
  conversion (head models attempted; not yet clean).
- **Video:** PSS (MPEG-2 + ADPCM); community PSS muxer work in progress
  (ps2str.exe from the PS2 SDK muxes correctly).
- **Music:** community video tutorial exists for music modding (Ligerbusa).
- **Earlier work:** Brienj (Brien L. Johnson, XHP Creations) made a KOC2
  Tool (2013) for TIM2 texture thumbnails in Windows Explorer.
- **Save files:** PS2 save tools (PS2 Save Builder, mymc) work; community
  save file unlocks content for texture-pack users.

## Sources (evidence labels)

- FETCH-VERIFIED: archive.org metadata for `ps2-isos-and-translations`
  (KoC2 7z: 1,738,818,479 B, md5 319396fd807341fa4b6586f2f67f1eeb,
  sha1 6706da7f2b0395777f6682576ee65a96781502c1); the 7z itself
  (downloading 2026-11-19, hash-checked on completion — see TEARDOWN.md).
- SEARCH-VERIFIED: Jerrold Ng FAQ/Movelist v1.0 (Neoseeker mirror; systems
  sections read 2026-11-19); GameSpot import review; CAGEMATCH games list
  (rating-sorted) + KoC2 ratings page; ResHax topic 18443 (full thread);
  KoC2 modding FAQ (sites.google.com/view/kingofcolosseum2/faq);
  bordersdown.net review thread (31 Oct 2004).
- BROWSER-GATED: ResHax attachments (decompression/compression scripts,
  sample model); modding Discord + Google Drive. See lane BROWSER-QUEUE.md.

## What is NOT in this repo

- The ISO / 7z (never committed — workdir only).
- The FAQ text verbatim (third-party copyrighted text; summarized here).
- Real wrestlers' names as Bannon roster entries (KoC2's roster is
  reference data for systems/moves; Bannon's roster is its own).
