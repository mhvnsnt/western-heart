# TempleOS → Shrine体系 — pull, inventory, and wiring (2026-10-24)

Owner directive (2026-10-24 20:01 CDT): find what of TempleOS is free
and open source, incorporate it into the Heart and Mind Within mode
and into Eastern Mind, and make its own mode in the for-fun section —
NOT called TempleOS, called "Shrine" + the kanji for OS — fully
incorporated, wired up, and made canon to the universe 100%.

Owner correction (2026-10-24 20:01 CDT): NOT "trying" — "shrine, like
a shrine, and then the kanji for OS".

Owner confirmation (2026-10-24 20:04 CDT): "The kanji for system is
good." — 体系 (taikei = system) is LOCKED as the kanji for OS.
**The in-game name is Shrine体系.** No further naming questions.

## 1. Source: public domain, no license block

- TempleOS, by Terry A. Davis: 64-bit, ring-0-only, single address
  space, non-networked, public domain, open source, written in
  HolyC (a C/C++-influenced dialect that is also the shell).
  Over 100,000 lines. Last release 5.03 (November 20, 2017).
- Repo inventoried via the GitHub API 2026-10-24:
  github.com/cia-foundation/TempleOS. Full ISO is ~16.5 MB.
- Public-domain status means there is no license to clear and no
  copyleft to work around. Attribution is kept in technical
  files (this doc, code header comments) and NEVER appears in
  canon writing or in-game text — the same law as Tekken names
  (technical files only, never in-universe writing).

## 2. Repo inventory (GitHub API, 2026-10-24)

Top level: `0000Boot`, `Adam`, `Apps`, `Compiler`, `Demo`, `Doc`,
`Downloads`, `Kernel`, `Linux`, `Misc`, plus `Home*.HC`,
`PersonalMenu.DD`, `ReadMe.TXT`, `StartOS.HC`.

`Apps/` (user programs): Budget, GrModels, KeepAway, Logic,
Psalmody (hymn/music programs), Span, Strut, TimeClock,
Titanium, ToTheFront, Vocabulary, X-Caliber.

`Demo/Games/` (bundled games — the adaptation pool):
BattleLines, BigGuns, BlackDiamond (downhill skiing dodge,
SkiFree-like: reach the bottom dodging trees, rocks, wild
dogs), BomberGolf (bomb 10 tanks from above), CastleFrankenstein,
CharDemo, CircleTrace, Collision, Digits, DunGen, ElephantWalk,
FlapBat (Flappy-like: eat bugs to 100%), FlatTops (carrier
strategy: launch fighters, sink enemy carriers), Halogen,
MassSpring, Maze, RainDrops, RawHide, Rocket, RocketScience,
Squirt, Stadium, Talons, TheDead, TicTacToe, TreeCheckers,
Varoom (arcade racing: stay on track, fastest lap), Wenceslas,
Whap, Zing, ZoneOut.

`Demo/Snd/` (sound toys): ASCIIOrgan, MorseCode, OhGreat,
WaterFowl.

`Demo/` also holds: DolDoc (document format), Graphics demos,
Lectures, MultiCore, Snd, Templates, and HolyC demos
(Carry, ClassMeta, CompileDemo, DateTime, DbgDemo, Define,
Directives, Exceptions, ExtChars, GlblVars, KeyBitMap,
LastClass, MagicPairs, MemDemo, MsgLoop, NullCase, OnceDemo,
ParenWarn, PhoneNumWords, Print, Progress, Prompt,
PullDownMenu, RadixSort, RandDemo, RegistryDemo, SortFileDemo,
Spy, StkGrow, SubIntAccess, SubSwitch, SuggestSpelling,
TimeIns, WordSearch, and more).

Notable single programs (from public documentation):
AfterEgypt — travel to a burning bush and use a "high-speed
stopwatch" oracle that generates pseudorandom text (Davis
likened it to a Ouija board / glossolalia). Flight simulator,
compiler, kernel, sprite editor (16-color VGA), tracker-style
music editor, Oracle (random scripture-word generator).

## 3. What was adapted into Western Heart (this PR)

| TempleOS thing | Shrine体系 form | Where |
|---|---|---|
| 640x480 16-color VGA display | 16-color VGA palette, 640px-wide terminal panel, pixelated canvases | game/js/shrine-os.js |
| Single-voice audio | One oscillator at a time, never chords; three hymn patterns | game/js/shrine-os.js |
| HolyC command line | HELP / ORACLE / SPRITE / MUSIC / GAME / SHARDS / CLEAR / EXIT parser | game/js/shrine-os.js |
| Oracle (random words) | Three-word readings drawn ONLY from canon: nine soul kanji, trial inscription, five lands, elements | game/js/shrine-os.js |
| Sprite editor | 16x16 board, 16-color paint, hex serialization | game/js/shrine-os.js |
| Music editor / Psalmody / ASCIIOrgan | Single-voice hymn player (arrival, trial, purified) | game/js/shrine-os.js |
| BlackDiamond (downhill dodge) | Slope descent: dodge rocks/trees down the Central Mountain, score by distance, pays Soul Shards | game/js/shrine-os.js |
| AfterEgypt oracle journey | The stillpoint beat: at stage 5 the shrine terminal reads the descending soul | game/js/heartmind.js |
| Shrine concept (Third Temple) | Octagonal Shrine Par-fang terminal — "shrine" is the canon anchor, not the source name | CANON.md |

What was NOT taken: any scripture content (the Oracle draws
canon words, never Bible words), the burning-bush framing
(no bush in-universe), any religious doctrine, and no HolyC
source code (a browser game cannot run HolyC; this is an
adaptation, not a port — no HolyC is vendored into the repo).

## 4. Forks checked, not used

- ZealOS (modernized: 32-bit VBE, 60fps) — more capable, but
  its improvements erase the 16-color limit that IS the
  shrine look. Not used.
- TinkerOS (255 colors, AHCI/USB) — same reason. Not used.
Both are noted here so a later lane can revisit them for a
different mode; neither is wired anywhere.

## 5. Kanji decision (locked)

- Japanese standard for "operating system" is katakana:
  オペレーティングシステム, abbreviated ＯＳ. There is NO
  single standard kanji for OS.
- Literal kanji alternative: 操作体系 (sousa taikei =
  "operation system"). NOT used — the owner picked the
  shorter form.
- LOCKED (owner 2026-10-24 20:04 CDT): 体系 (taikei =
  "system"). In-game name: **Shrine体系** everywhere —
  side-games block, terminal boot text, story beats, canon.
- If the owner ever wants a different kanji, it is a
  one-word change: the name constant lives in
  game/js/shrine-os.js (SHRINE_OS) and the story segment in
  game/js/heartmind.js (SHRINE_OS_SEGMENT).

## 6. Wiring map (all three, plus tests and docs)

1. Own mode (side games / for-fun): game/side-games.html
   prototype 3 — Shrine体系 terminal, playable on load
   (terminal + oracle + sprite + hymns + slope game).
2. Heart and Mind Within: game/js/heartmind.js —
   SHRINE_OS_SEGMENT + shrineOsBeat(), played at the
   stillpoint stage (stage 5, octagonal-shrine) for every
   fighter, before the shadow-self fight.
3. Eastern Mind canon: CANON.md — Shrine体系 section
   (in-universe only, no source names), anchored to the
   Octagonal Shrine Par-fang, Central Mountain, Earth, the
   trial inscription, and the nine souls.
4. Story-mode doc: docs/modes/HEART-AND-MIND-INSIDE.md —
   stillpoint segment note.
5. Standing directives: docs/owner-directives.md — entry.
6. Tests: test/shrine-os.test.mjs — identity, palette,
   oracle pool, parser, sprite round-trip, single-voice
   patterns, slope physics, story wiring. CI-safe: it only
   reads game/js files (CI's sparse checkout includes
   game/js but NOT side-games.html or CANON.md, so those
   two are verified by blob SHA after commit, not by test).

## 7. GPU note (honest)

No GPU batch job belongs to this lane: the work is
hand-written JavaScript plus docs — no raster assets, no
model conversion, no audio cutting, nothing to batch.
Running a GPU job here would be theater. The GPU lanes
(UniRig rigging, Real-ESRGAN upscaling, Nosferatu cutting,
card pre-renders) run separately and are unaffected.

## 8. Honest gaps (not claimed done)

- Live phone playtest is OWED (this lane has no live
  browser): menu → side games → Shrine体系 → type HELP →
  ORACLE → SPRITE (paint) → MUSIC (play) → GAME (descend,
  crash, shards pay) → EXIT → BOOT; plus a Heart and Mind
  Within run to the stillpoint beat. Do not call the mode
  "verified" until that playtest happens.
- Only ONE mini-game is built (slope descent). Varoom,
  FlapBat, Titanium, FlatTops, BomberGolf, KeepAway and the
  rest are inventoried above for later adaptation, NOT
  claimed as built.
- Hymns are WebAudio beeps, not recorded audio. A
  recorded-hymn pass would be a later audio lane.
