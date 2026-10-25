# How Tekken games + all our games wire their soundtracks — and what Western Heart adopts

Owner directive 2026-10-24 20:33 CDT (verbatim intent): "Why are those up
in the background music and menu music rotation and in the places in the
arenas that they're going to be in the rotation for and later they'll be
maybe used for like background music for cut scenes and stuff but go ahead
and uh get all that done find more music and then find out how the Tekken
games and all their actual games use and wire up their soundtracks and
music."

This doc is the research deliverable for that directive. It is also the
wiring record for this PR: every pool assignment, every adopted pattern
with the exact code/library change that carries it, and every pattern
left as reference-only with the reason. Nothing here is guessed: game
claims cite the community/teardown sources below; WH claims are verified
against `game/data/music-library.json` + `game/js/music.js` on main at
`b509f179` plus this PR's diff, and against the main-tree file list
(14 committed music files — see §7 for committed-vs-pending status).

Standing rules applied: Tekken/WWE names are technical-only (this doc,
moveset docs, wiring specs) and never appear in canon writing; all WH
fighters are adults; buttons are LP1/RP2/LK3/RK4 in user-facing text.

## 1. Rotation wiring shipped by this PR

Engine (PR #1030, merged `8579c6df`): rotation pools, stage-tagged
first then rest of battle pool, sequential advance persisted per
stage/mode, menu pools by mode, pending entries never picked,
`playFinalRound()` match-point variant swap, `playSequence()` ordered
sequences, victory jingle → results theme chaining. This PR EXTENDS
that engine; it does not re-do it, and it does not touch the audio
lane's Jukebox engine read of `wh_jukebox_v1`, the announcer wiring,
or the Cape entries (audio lane, open PR #1058 / #1037 rebase).

### 1a. Engine changes (`game/js/music.js`, surgical, 3 hunks)

1. **Stage-theme rule** in `_poolFor`: a track with NO mode tags but a
   stage tag joins ONLY that stage's battle pool, tagged-first. This
   is load-bearing for the Cape pools: the 8 Cape tracks (audio lane)
   carry `stages: ['cape-jones-arena']` and `modes: []`, so under the
   pre-existing filter (`modes` includes `'battle'`) the battle pool
   would NEVER pick them — the Cape pool would silently not exist.
   With this rule it resolves. Menu pools are untouched: a stage theme
   never enters a menu pool, and with no stage given it joins nothing,
   so it can never leak into other stages' pools.
2. **`playCutscene(name)`** hook: thin alias over `playSequence()`.
   Story lanes call `music.playCutscene('<sequence>')` for ordered
   cutscene BGM; when the sequence ends, battle rotation resumes on
   the last battle stage (existing `_playSequenceNext` behavior).
   Full cutscene scoring is NOT built here — sequences are data in
   `library.sequences`, one named sequence per story scene.
3. Header comment documents both rules for the next lane.

### 1b. Stage pools (battle rotation) — every playable stage id

Pool order = stage-tagged tracks in library order, then the rest of
the battle pool in library order. "Live" = the file is committed on
main today (14 files); "pending" tracks are in the pool by id but
resolve to the procedural fallback until their bytes land — the game
never goes silent, but a pending track is never claimed as playing.

| Stage id | Pool opens with (tagged-first) | Pool size | Live anchor tracks |
|---|---|---|---|
| `shrine` | battle-volatile, nos-t07, nos-t24 | 32 | 7 committed battle tracks |
| `palace-of-dreaming` | battle-cannery, nos-t04, nos-t05, nos-t08 | 32 | 7 committed battle tracks |
| `helix-palace` | battle-implosion, nos-t12, nos-t13, nos-t16 | 32 | 7 committed battle tracks |
| `tree-of-life` | battle-five-armies, nos-t01, nos-t25 | 32 | 7 committed battle tracks |
| `sunra` | battle-five-armies, nos-t14, nos-t15 | 32 | 7 committed battle tracks |
| `phantom-marketplace` | battle-hitman, nos-t03, nos-t11, nos-t21 | 32 | 7 committed battle tracks |
| `octagonal-shrine` | battle-mechanolith, nos-t09, nos-t10, nos-t17 | 32 | 7 committed battle tracks |
| `plains-of-chi-u` | nos-t06, nos-t22, nos-t23 (no prior stage theme) | 32 | 7 committed battle tracks |
| `tong-nou` | tong-nou-theme, nos-t02, nos-t18, nos-t19, nos-t20 | 32 | 7 committed battle tracks |
| `t7-mishima-dojo` | (T7 slots pending-download, excluded) then rest of battle pool | 32 | 7 committed battle tracks |
| `cape-jones-arena` (house) | see §2 | 40 here / 48 merged | 7 committed battle tracks |
| `cape-jones-halloween-beach` (beach) | see §2 | 40 here / 48 merged | 7 committed battle tracks |

Nosferatu stage tags are mood-matched, one stage per track:
dark/aggressive → helix-palace + phantom-marketplace; calm/tense home
and inn → palace-of-dreaming; castle night → octagonal-shrine;
journey/road → plains-of-chi-u; mystical/dark → tong-nou; vigil and
castle-negative → shrine; epic opening + triumphant finale →
tree-of-life; household → sunra. The original stage theme still opens
each pool (library order puts it first) — the Tekken rule that a
stage's own theme opens, with rotation behind it.

### 1c. Menu pools (mode rotation) — menu must never go silent

| Mode | Pool (library order) | Live today |
|---|---|---|
| `title` | tong-nou-theme, title-meditation, nos-t01 (pending-commit) | tong-nou-theme, title-meditation |
| `select` | select-exhilarate, nos-t04, nos-t08 (pending-commit), t7-select (pending-download, excluded) | select-exhilarate |
| `versus` | tong-nou-esoteric, nos-t09, nos-t11 (pending-commit) | tong-nou-esoteric |
| `results` | ending-theme, nos-t25 (pending-commit) | ending-theme |
| `online` | menu-deliberate | menu-deliberate |
| `credits` | transmigration-ending, nos-t01, nos-t25 (pending-commit) | transmigration-ending |
| `victory` (jingle) | victory-fanfare, nos-t25 (pending-commit) | victory-fanfare |

Two orphan fixes ship here: `title-meditation` had `modes: []`
(committed file, unreachable by any pool) → now `['title']`;
`menu-deliberate` had `modes: []` → now `['online']`. Before this
fix the online pool contained ONLY the pending-download T7 slot, so
online menus played the procedural fallback exclusively. After it,
online has a real committed track. Verified by
`test/music-pools-wiring.test.mjs`: every mode pool and every stage
pool contains ≥1 track whose file exists in the checkout.

### 1d. Cutscene BGM hook (wired now, scoring later)

- `sequences.cutscene-example = ['title-meditation',
  'tong-nou-esoteric', 'transmigration-ending']` — all three files
  committed, so the example works TODAY (not pending on any download).
  Arc: calm open → mystical/dark middle → calm/epic close.
- Story lanes call `music.playCutscene('ep01-cutscene-<scene>')` with
  their own named sequence added to `library.sequences`; cutscene
  sequences draw from the same battle/menu pools' committed tracks
  (never from pending-download slots — the sequence builder filters
  to available tracks), and battle rotation resumes on `_lastStage`
  when the sequence ends.
- The existing `ep01-fight` sequence (9 Nosferatu tracks) is the
  fight-arc pattern; cutscene sequences are its story-scene sibling,
  not a replacement.

## 2. TWO Cape Jones arenas — both pools, Ghost Surf Rock FIRST

Coordinator clarification (standing directives 2026-10-24 20:35 +
20:38 CDT): there are TWO Cape arenas, not one.

1. **Cape Jones Arena / Ghost Surf Rock arena = his HOUSE, home
   turf.** Stage tag on main via the audio lane: `cape-jones-arena`.
   (Repo spec `stages/cape-house/STAGE-SPEC.md` describes the house
   variants living-room / cape-bedroom / front-yard; it is spec-only
   and not yet wired into stage select — the tag above is the music
   side's contract, not a stage-select claim.)
2. **Malakor-style Halloween beach = SECOND Cape show arena**,
   show-based, distinct from the house arena: Halloween beach,
   Malakor dark fantasy, Scooby-Doo spooky-fun vibe (not grimdark),
   DARK PURPLE lean-colored heavy/thick/dirty sky, Ghost Surf Rock
   rotation. Stage tag proposed by this PR:
   `cape-jones-halloween-beach`. This id does NOT exist in any stage
   file yet — the dedicated Cape-arenas lane (PR #1061 pipeline)
   owns the arena build, and the coordinator must confirm the beach
   stage id with that lane before it is treated as final.

Both pools, by design:

- Ghost Surf Rock (`cape-jones-ghost-surf-rock`, Loyalty Freak Music,
  04:07, CC0 1.0, album WITCHY, BATTY, SPOOKY, HALLOWEEN IN
  SEPTEMBER !!) FIRST, then interchange tracks rotating around it.
  Vibe lock: surf rock + spooky + witchy + batty + Halloween,
  spooky-surf-fun, never generic dark/epic, never grim horror.
- Interchange tracks: the 8 Cape tracks from the audio lane
  (Ghost Surf Rock + A ghost Waltz + Hello Regan ! + A really dark
  alley + The graveyard + The Old Witch Place + The Witch Are Going
  Magical + Sweat Time !) PLUS the 8 new tracks in this PR (§5).
- Mechanism: stage-tagged-first in library order. Ghost Surf Rock is
  first among Cape-tagged tracks in the audio lane's block, and this
  PR's new block is appended AFTER it — so in the merged library
  both Cape pools open Ghost Surf Rock → A ghost Waltz → … →
  interchange → rest of battle pool.

**Merge-order dependency the coordinator must enforce:** the Cape-8
block must precede this PR's new-8 block in the `tracks` array, or
the beach/house pools would open with an interchange track instead
of Ghost Surf Rock. Likewise, the beach pool opens with Ghost Surf
Rock ONLY once the arena/audio lane adds the
`cape-jones-halloween-beach` tag to all 8 Cape tracks; until then
the beach pool's tagged section is this PR's 8 new tracks (still
Cape vibe, but NOT Ghost-first). The new test logs this as a NOTE,
not a failure, until that tag lands — it is a coordination gap,
recorded here, not hidden.

## 3. How Tekken games wire their soundtracks (researched, sourced)

### T7 — the reference implementation

- **One BGM per stage + Final Round variant.** Most T7 stages ship
  two mixes: a Round 1 mix and a Final Round mix that swaps in at
  match point (deciding round). The swap is a restart into the
  variant, not a seamless layer crossfade — the community Jukebox
  Tool documents that "music doesn't restart when the fight goes
  into the final round" is impossible with its replacement method,
  i.e. the stock game restarts into the variant. Some stages are
  exceptions: Geometric Plane ("The Motion") is documented as the
  only T7 stage with a single theme that "does not change at match
  point". Island Paradise changes music both at Final Round AND on
  its balcony-break stage transition (Poolside remix → Beach remix).
  Sources: Tekken Wiki "Tekken Tunes"; Tekken Wiki "Geometric
  Plane"; TV Tropes "AwesomeMusic/Tekken" (Final Round mixes);
  Nexus Mods "Tekken 7 Jukebox Tool" FAQ.
- **Menu/select/versus/results themes are separate slots**, not
  stage tracks: main menu ("New World Order" in the T7-era lineage),
  character select ("Blood, Sweat, and Fists"), online lobby
  ("Kodama Starship") — these are the 5 pending slots already in
  the WH library (§6).
- **Jukebox (Tekken Tunes, renamed Jukebox in T7).** First in Tekken
  Tag Tournament as a listener; since TTT2 the player can REPLACE
  stage/menu BGM with any track in the game, and buy music packs
  from T1–T6. In T7 the player has access to music from all previous
  Tekken games including Tekken Revolution, can set stage AND menu
  BGM to any track, and can save playlists with different sets.
  Platform catch: T7 Jukebox shipped ONLY on PlayStation 4.
  Source: Tekken Wiki "Tekken Tunes"; ONE Esports T8 Jukebox
  reporting (Harada confirmation).
- **Music keeps playing across rounds** and only changes on
  screen/stage change or at match point — the rule WH's engine
  already follows (no per-round restart except the Final Round
  variant swap).
- **Modding wire-up (PC):** the T7 Jukebox Tool maps one BGM per
  stage (Round 1 + Final Round slots), generates a `Jukebox_P.pak`
  into `TekkenGame/Content/Paks/~mods`. BGM mods are "perfectly
  looped" replacements per stage slot. This is the file-level model
  WH mirrors with `file` + `loopStart`/`loopEnd` + `finalRound`.

### T3 / T5 / T6 / TTT2 / T8

- **T3:** arcade-original stage/character themes — the era's model
  is character-home-stage themes (e.g. Jin's theme = his Tiger Dojo
  Tokyo stage theme; Hwoarang's theme = Taekwondo Dojo). Character
  select has its own attract/select medley. No jukebox; music is
  fixed per stage/character. Source: Smash Wiki "List of Music
  (Tekken series)" (arcade rips + stage mapping).
- **T5 (+ Dark Resurrection):** one theme per stage (Burning Temple
  "Red Hot Fist", Moonlit Wilderness, Poolside, Snow Castle, Heaven's
  Gate "Into Nirvana"), separate opening movie theme
  ("RESURRECTION"), per-character endings with their own ending
  themes (the OST's Disc 2 is largely character endings). T5:DR
  adds a stage-music player in Theatre mode (Panda/Kuma dance
  beside it — a jukebox ancestor). T6 is the ONLY post-TTT game
  WITHOUT a jukebox mode.
- **TTT2:** full Tekken Tunes replacement system + purchasable
  era packs (T1, T2, T3, TTT, T4, T5, T6 separately or together) +
  PS3 personal-library tracks. This is the first true "assign any
  track to any stage" system.
- **T8:** Jukebox returns on ALL platforms (not PS-only), same
  replace-stage/menu-music model across the full back catalog.
  WH's Jukebox lane (audio lane, `wh_jukebox_v1` read in the engine)
  is the WH equivalent; this PR deliberately does not duplicate it.

### Other owned games in scope

- **WWE 2K (2K22/2K23/2K26):** a licensed soundtrack doubles as
  menu music AND entrance music — the same playlist serves both
  slots, and the in-game jukebox lets players enable/disable
  individual tracks (2K26: 16-song curated soundtrack, per-track
  toggles in Options → audio/jukebox; soundtrack songs are
  selectable as entrance themes in Create-an-Entrance). 2K26 has
  NO built-in custom-music import; PC players swap entrance audio
  by replacing existing audio files with mod tools (Sound Factory
  / Discovery Audio Editor class tools). Pattern for WH: one
  library, two slot types (menu + moment), per-track toggles.
  Sources: Operation Sports 2K26 soundtrack list; Attack of the
  Fanboy 2K22 custom entrance guide; GamerBlurb 2K26 custom music.
- **Yakuza / Like a Dragon:** music is wired by SITUATION and by
  CHARACTER, not just by place — each playable character has their
  own random-encounter battle theme (Yakuza 4: Akiyama "Speed Star",
  Saejima "Massive Fire", Tanimura "Infinite Handcuffs", Kiryu "The
  Myth"); chase scenes, boss fights, and long mob fights each get
  their own cues; and the series' famous karaoke/jukebox system
  (Survive Bar jukebox, karaoke minigame with per-character songs,
  DLC karaoke sets) is a second, player-facing music collection
  that lives alongside the score. Pattern for WH: situation tags
  (chase/boss/mob ≈ round/final-round/KO) + a player-facing
  collection (WH Jukebox) are separate systems sharing one library.
  Sources: TV Tropes "Like a Dragon" AwesomeMusic; PlayStation
  Store Yakuza: Like a Dragon Karaoke Set.
- **Gang Beasts / Fire Pro Wrestling:** no verified music-system
  detail was found in this research pass (search returned only
  generic soundtrack praise, no wiring description). Recorded as a
  GAP, not invented: these two stay reference-only until a
  teardown or manual source is verified. Do not cite a Gang
  Beasts/Fire Pro music rule from this doc.

## 4. Adopted vs reference-only

| Pattern (source) | WH status | Carried by |
|---|---|---|
| Stage BGM pools, stage theme opens, rotation behind it (T7 Jukebox + WH #1030) | ADOPTED + extended | `music.js` rotation + §1b tags |
| Final Round variant swap at match point (T7) | ADOPTED (already in engine) | `playFinalRound()` + `finalRound` field; T7 dojo pair is the live example once bytes land |
| Music persists across rounds, changes on screen/stage change (T7) | ADOPTED | engine transport (no per-round restart) |
| Separate title/select/versus/results/credits/online slots (all Tekken) | ADOPTED | mode pools §1c |
| Stage theme with no mode tag joins its stage pool only (WH rule for Cape) | ADOPTED (new) | `_poolFor` stage-theme rule §1a |
| Ordered sequence BGM for story/cutscene scenes, battle resumes after (WH ep01-fight pattern) | ADOPTED (new hook) | `playCutscene()` + `cutscene-example` §1d |
| Victory jingle → results theme chaining (WH #1030) | ADOPTED (already in engine) | `_afterVictory` chaining |
| Crossfade on every switch, no hard cuts (WH engine) | ADOPTED (already in engine) | `_playTrack` 1600 ms crossfade |
| Intensity lift: lowpass + gain ramp as fight heats up (Tekken final-round/low-HP lift, generalized) | ADOPTED (already in engine) | `setIntensity()` 0.55 → 0.85 final round → 1.0 under 25% HP |
| Voice ducking under announcer (~8 dB) | ADOPTED (already in engine; announcer lane owns events) | `duck()` via `voice.onSpeech` |
| Jukebox: any track assignable to any stage/menu, saved playlists (TTT2/T7/T8) | ADOPTED by the AUDIO lane, not this PR | `wh_jukebox_v1` read (PR #1058); this PR does not duplicate it |
| One library serving menu + moment slots with per-track toggles (WWE 2K) | ADOPTED in principle; toggles are a future UI item | library `modes`/`stages` tags; per-track toggle UI NOT built here |
| Situation + character themes (Yakuza) | PARTIAL: situation via intensity/final-round; character themes NOT built (no character-theme audio exists) | `setIntensity` call sites; character-theme slots are a future lane, not claimed |
| Perfectly-looped per-slot replacement files (T7 Jukebox Tool mods) | ADOPTED as file convention | `file` + `loopStart`/`loopEnd` (Nosferatu loop points from the GPU cut job) |
| T6 "no jukebox" / T3 fixed-per-stage model | REFERENCE-ONLY (WH has rotation + jukebox; fixed-per-stage would regress it) | — |
| Guest-character stage themes withheld from Jukebox for copyright (T7 trivia) | REFERENCE-ONLY (WH equivalent: pending slots are never picked) | pending exclusion rule |
| Karaoke minigame / bar jukebox as a playable mode (Yakuza) | REFERENCE-ONLY (WH Jukebox is a listener/assigner, not a rhythm mode) | — |
| Personal music library import (TTT2 PS3) | REFERENCE-ONLY (no user-file import in WH) | — |

## 5. MORE MUSIC — whole list, per-track license verified

Rule applied throughout: Loyalty Freak is NOT uniformly CC0 by
assumption — every track below marked CC0 was verified on its own
FMA page (or an FMA license statement for that track). Tracks whose
individual page was not verified are marked as such and are NOT
added as library entries.

### 5a. WITCHY, BATTY, SPOOKY, HALLOWEEN IN SEPTEMBER !! (13 tracks, full album)

Album page states the songs are CC0 1.0 with "check individual
tracks". All 13 are now individually accounted for:

| # | Track | Dur. | License (per-track) | WH status |
|---|---|---|---|---|
| 1 | Monster Parade | 01:50 | CC0 1.0 (FMA page) | NEW in this PR → Cape pools, pending-file |
| 2 | A ghost Waltz | 01:36 | CC0 1.0 | Audio lane Cape 8 (PR #1058) |
| 3 | Love song by a ghost duet | 02:35 | CC0 1.0 (FMA page) | NEW in this PR → Cape pools, pending-file |
| 4 | Hello Regan ! | 07:07 | CC0 1.0 | Audio lane Cape 8 |
| 5 | We all gonna die !! | 00:32 | Album-level CC0 only, individual page NOT verified; 32 s — stinger-length, not a battle track | NOT added; candidate for a future victory/stinger slot only, after per-track check |
| 6 | The graveyard | 03:40 | CC0 1.0 | Audio lane Cape 8 |
| 7 | A really dark alley | 04:16 | CC0 1.0 | Audio lane Cape 8 |
| 8 | The Swamp | 03:16 | CC0 1.0 (FMA page) | NEW in this PR → Cape pools, pending-file |
| 9 | Hello Michael ! | 04:00 | CC0 1.0 (FMA page) | NEW in this PR → Cape pools, pending-file |
| 10 | The Witch Are Going Magical | 02:09 | CC0 1.0 | Audio lane Cape 8 |
| 11 | The Old Witch Place | 01:36 | CC0 1.0 | Audio lane Cape 8 |
| 12 | Halloween Ghost Party | 02:46 | CC0 1.0 (FMA page) | NEW in this PR → Cape pools, pending-file |
| 13 | Ghost Surf Rock | 04:07 | CC0 1.0 | THEME — Cape pools first track (audio lane) |

### 5b. ROLLER DISCO DANCE DANCE (8 tracks, full album)

Album page: CC0 1.0, check individual tracks. Genres Disco / Rock /
Dance / Surf — surf energy fits the Cape pools (Sweat Time !
precedent: a ROLLER track already sits in the Cape 8).

| # | Track | Dur. | License (per-track) | WH status |
|---|---|---|---|---|
| 1 | Roller Fever | 02:25 | Album-level CC0 only, individual page NOT verified | NOT added; manifest candidate after per-track check |
| 2 | Dance Robot ACTIVATE | 02:39 | Album-level CC0 only, individual page NOT verified | NOT added; manifest candidate after per-track check |
| 3 | I'M ON FIRE | 03:04 | CC0 1.0 (FMA page) | NEW in this PR → Cape pools, pending-file |
| 4 | Can't Stop My Feet ! | 03:05 | Album-level CC0 only, individual page NOT verified | NOT added; manifest candidate after per-track check |
| 5 | Grab A Partner | 03:11 | CC0 1.0 (FMA page) | NEW in this PR → Cape pools, pending-file |
| 6 | Take A Break | 02:05 | CC0 1.0 (FMA page) | NEW in this PR → Cape pools, pending-file |
| 7 | Sweat Time ! | 02:07 | CC0 1.0 | Audio lane Cape 8 |
| 8 | Last Energy For The Day | 02:26 | Album-level CC0 only, individual page NOT verified | NOT added; manifest candidate after per-track check |

### 5c. Other no-copyright sources (scouted, not added this PR)

- **Kevin MacLeod / incompetech (CC BY 4.0, attribution
  required):** the 9 MacLeod tracks already in the library are the
  proven path — new MacLeod battle/menu picks must be chosen from
  incompetech pages with the CC BY credit line copied into the
  track's `credit` field, exactly like the existing entries. No new
  MacLeod track is named here because none was verified on its own
  page in this pass; naming one without that check would repeat
  the guessed-URL failure mode.
- **Rrrrrose circle Best-Of (CC0 compilation, 300 albums / 8
  hours):** Komiku battle themes, Monplaisir, Soft and Furious and
  others appear in the CC0 Best-Of, but per-track FMA verification
  was not completed for any of them in this pass — they are a
  scouting list for the next music lane, NOT additions.
- **HoliznaCC0 (FMA, CC0):** Halloween/ambient CC0 tracks surfaced
  alongside the Loyalty Freak verification (same Halloween lists);
  same rule — per-track check before any entry.

### 5d. Download manifest (browser lane — files NOT downloaded by this lane)

FMA page URLs are HTML pages, not audio files, so no `remote` URL
is set on these entries (the engine would waste a fetch trying to
decode a page). The page URL lives in each track's `source` field.
Download each track from its FMA page and commit to
`game/assets/music/` with EXACTLY these filenames (the library
already references them; no code change once they land):

- `cape-jones-monster-parade.mp3` ← Monster Parade FMA page
- `cape-jones-ghost-duet.mp3` ← Love song by a ghost duet FMA page
- `cape-jones-swamp.mp3` ← The Swamp FMA page
- `cape-jones-hello-michael.mp3` ← Hello Michael ! FMA page
- `cape-jones-ghost-party.mp3` ← Halloween Ghost Party FMA page
- `cape-jones-im-on-fire.mp3` ← I'M ON FIRE FMA page
- `cape-jones-grab-partner.mp3` ← Grab A Partner FMA page
- `cape-jones-take-break.mp3` ← Take A Break FMA page
- (Audio lane, separate manifest) the 8 Cape MP3s + 25 Nosferatu
  MP3s + 5 Tekken slot files (§6).

Full URLs for the 8 new pages are in each new track's `source`
field in `game/data/music-library.json` and in the worklog
manifest — copy them verbatim from there, never retype from memory.

## 6. Tekken 7 OST slots — wiring ready, bytes pending (browser lane)

The 5 pending-download slots stay `file: null, status:
'pending-download'` — their file fields are set ONLY once the bytes
are downloaded and committed. Proposed filenames (to be set at that
moment, no other library change needed):

| Slot id | Track | Proposed filename |
|---|---|---|
| `t7-dojo-1st` | Mishima Dojo — Round 1 (T7) | `assets/music/t7-mishima-dojo-round1.mp3` |
| `t7-dojo-final` | Mishima Dojo — Final Round (T7) | `assets/music/t7-mishima-dojo-final.mp3` |
| `t7-title` | New World Order (T7 main menu) | `assets/music/t7-new-world-order.mp3` |
| `t7-select` | Blood, Sweat, and Fists (T7 character select) | `assets/music/t7-blood-sweat-fists.mp3` |
| `t7-online` | Kodama Starship (T7 online menu) | `assets/music/t7-kodama-starship.mp3` |

Verified source path: the user's owned Tekken 7 files (Steam app
389730, account on file) via the T7 extraction runbook
(`docs/team/TEKKEN-DATA-SOURCES.md`), or TekkenMods BGM mods / the
T7 Jukebox Tool Default Music Pack as the community route — the
browser lane verifies which route yields clean Round 1 / Final
Round pairs before committing. Until then the engine skips all 5
slots and every pool still has live tracks (§1b/§1c). The
`finalRound` link (`t7-dojo-1st` → `t7-dojo-final`) is already in
the library and already tested by the existing rotation test.

## 7. Committed-vs-pending status (honest, per pool)

Main tree at `b509f179` holds 14 music files: the 9 MacLeod MP3s
(title/select/battle ×6/victory/menu), the 4 owner-original OGGs
(Tong-Nou theme + esoteric, transmigration ending, ending theme),
and nothing else. Therefore:

- **COMMITTED (live today):** all 14 above. Every stage pool and
  every menu pool contains ≥1 of them — verified by test, not
  claimed.
- **PENDING-COMMIT (music-commit lane, branch exists, not merged):**
  25 Nosferatu MP3s (`nosferatu-t01…t25`). In pools by id; resolve
  to procedural fallback until merged + deployed.
- **PENDING-FILE (audio lane PR #1058, open):** 8 Cape MP3s.
- **PENDING-FILE (this PR):** 8 new MP3s (§5d).
- **PENDING-DOWNLOAD (browser lane):** 5 Tekken slots (§6) — never
  picked, never counted live.
- **Nosferatu license flag (unchanged by this PR):** the 25 Nos
  tracks carry `license: unknown-uncredited` — the VHS synth
  score's copyright status is UNKNOWN and must NOT be labeled
  public domain; use-basis decision pending. This PR wires their
  stage pools but does not resolve that flag, and no new track in
  this PR inherits it (all 8 new tracks are individually verified
  CC0 1.0).

## 8. GPU jobs prepared (not run by this lane — see tools/)

This lane has no GPU on its VM (`nvidia-smi` absent) and no live
browser, so no GPU job is claimed as run. Two job packages ship in
`tools/music/` for the coordinator's Kaggle (T4 x2 notebook) /
Colab session — switch, never stop; session stays open, jobs queue
continuously:

1. **`tools/music/gpu-new-tracks.py`** — audio batch: normalize
   the 8 new tracks to −14 LUFS, detect loop points, encode MP3.
   Same proof discipline as the Nosferatu cut job: nvidia-smi +
   torch.cuda check + CUDA matmul proof, input size, output,
   wall time, AND CPU-baseline time. Measured CPU baseline on this
   VM (not a batch, a single-track timing): ffmpeg loudnorm on one
   113 s Nosferatu track took 9.65 s → scaled estimate for the 8
   new tracks (~1367 s total audio) ≈ 117 s of loudnorm CPU. The
   GPU run must record its own measured times; the 117 s is a
   scaled estimate from a measured single track, labeled as such.
2. **`tools/music/gpu-research-embeddings.py`** — research job
   (coordinator note: research rides the GPU too): embed the
   community-docs corpus (Tekken Wiki / wavu / modding guides /
   WH music docs) + track metadata with a sentence-transformer on
   CUDA, rank every candidate track against stage/mode vibe
   descriptors (spooky/surf/battle/menu/calm/epic), and classify
   new candidates by vibe/mode fit. CPU baseline measured on this
   VM: a stdlib TF-IDF cosine run over 2 research docs × 3 queries
   took 0.001 s — the lexical floor. The GPU job's value at corpus
   scale is semantic ranking quality + batch throughput, and its
   run must record nvidia-smi + torch.cuda proof, corpus size,
   output rankings, wall time, and the CPU-embedding baseline time
   for the same corpus. No report from that run may say "GPU not
   needed", and no CPU-only audio batch is authorized.

## 9. Live play verification (owed — parent browser delegation)

Tests are NOT playtest. The coordinator's browser lane must play
the live build after merge + deploy, phone portrait mode, human
navigation (screenshot, look, scroll, then tap — never jump via
selectors):

1. Title screen: theme plays, advance through menu → title pool
   rotates (quit to title, re-enter, track changes).
2. Select screen: select theme plays, rotates on re-entry.
3. Stage select → fight on `shrine`: stage pool opens with the
   stage theme, advances per fight (rematch = next pool track).
4. Final round: match-point swap audible where a variant exists
   (T7 dojo after bytes land; otherwise intensity lift audible).
5. Victory → results: jingle plays once, results theme chains
   after it, no gap of silence.
6. Cape pools (after #1058 + this PR + arena ids): fight on BOTH
   Cape arenas — Ghost Surf Rock opens both, interchange rotates.
7. No silence anywhere: menus, versus, online lobby, results,
   credits — if any screen is silent, that is a failure, not a
   fallback success (procedural fallback counts as sound, silence
   does not).

## Sources (verbatim URLs from search results)

- https://tekken.fandom.com/wiki/Tekken_Tunes
- https://tekken.fandom.com/wiki/Geometric_Plane
- https://TVtropes.org/pmwiki/pmwiki.php/AwesomeMusic/Tekken
- https://www.nexusmods.com/tekken7/mods/47/
- https://www.oneesports.gg/tekken/tekken-8-jukebox-mode/
- https://gamajuegos.com/all-important-jukebox-mode-returns-in-tekken-8-with-tracks-from-every-previous-game/
- https://supersmashbros.fandom.com/wiki/List_of_Music_(Tekken_series)
- https://www.operationsports.com/wwe-2k26-soundtrack-list/
- https://attackofthefanboy.com/guides/wwe-2k22-how-to-use-custom-entrance-music/
- https://gamerblurb.com/articles/wwe-2k26-how-to-add-custom-music
- https://tvtropes.org/pmwiki/pmwiki.php/AwesomeMusic/LikeADragon
- https://store.playstation.com/en-us/product/UP0177-PPSA02383_00-DLCYLADEU0000004/
- https://freemusicarchive.org/music/Loyalty_Freak_Music/WITCHY_BATTY_SPOOKY_HALLOWEEN_IN_SEPTEMBER_/
- http://freemusicarchive.org/music/Loyalty_Freak_Music/ROLLER_DISCO_DANCE_DANCE/
- https://chezmonplaisir.bandcamp.com/album/witchy-batty-spooky-halloween-in-september?action=buy
- https://chezmonplaisir.bandcamp.com/album/roller-disco-dance-dance
