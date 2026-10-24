# WESTERN HEART — Voice Mapping (teardown placeholders)

Owner directive (2026-10-22, Track 1): *"Pull voice lines from the teardown
files and map them to our characters — King's voice lines for Pantera, and so
on for every character. Match by character personality, canon, and style —
not just the moveset source. If another game's voice fits a character better,
use that. This is TEMPORARY — eventually every character gets their own
proprietary voice."*

**Everything here is TEMPORARY.** Two tiers of placeholder:

| Tier | What it is | Status in manifests |
|------|-----------|---------------------|
| **A — owned teardown audio** | Real voice bytes from the owner's OWN Eastern Mind teardown (`teardown/eastern-mind/.../sounds/`). 10 fighters. Copyright-clean (owner's game). | `status: "teardown"` — plays through the voice bus NOW; the voice-clone pipeline replaces with proprietary voice later |
| B — mapped, subtitle-only | No audio bytes shipped (owner law: no copyrighted game audio in the public repo). Manifest carries the mapping + transcribed-style placeholder LINES; the engine shows subtitles only. | `status: "placeholder"`, `file: null` |

Clip content for tier A is **unverified by ear** (never presented as final);
subtitle `text` is canon-flavored and each clip's `note` says so. The voice
session transcribes/verifies before anything is called final.

## The mapping (character → voice source → why it fits)

### Tier A — real audio (owner's Eastern Mind teardown)

| WH fighter | Teardown source | Why it fits |
|---|---|---|
| BYOU | `R_BYOU` incarnation voice | Direct soul-name match — the Eastern Mind voice of the BYOU soul |
| TOU | `R_TOH` incarnation voice | Direct soul-name match — TOU soul |
| SHA | `R_SHA` incarnation voice | Direct soul-name match — SHA soul |
| KAI | `R_KAI` incarnation voice | Direct soul-name match — KAI soul |
| RETSU | `R_LETS` / `R_LETSB` incarnation voices | Direct soul-name match — RETSU soul |
| ZEN | `R_ZEN` / `R_ZEN2` incarnation voices | Direct soul-name match — ZEN soul |
| GYOU | `R_GYOU` / `R_GYOU2` incarnation voices | Direct soul-name match — GYOU soul |
| DEMONIO | `R_JIN` incarnation voice | JIN-soul voice → the Jin-Kazama-based demon soul (name + base + demonic nature) |
| PANTERA | `F_KING` stage voices (9 clips) | The user's example mapping: King's lines for Pantera — Eastern Mind's KING character → the King-moveset panther wrestler |
| ARMOR KING | `L_KING` stage voices (5 clips) | Eastern Mind's KING voice from the Tree of Life → the dark chained king |

(RIN has no Eastern Mind voice file — he maps to Jin Kazama below.)

### Tier B — mapped, subtitle-only (personality/canon/style first)

| WH fighter | Source game | Source character | Why it fits (personality, not just moveset) |
|---|---|---|---|
| RIN | Tekken | Jin Kazama | Same base + the same cold Mishima discipline |
| PHANTOM | Tekken | Yoshimitsu | The mechanical ghost-samurai voice IS Phantom's nature |
| DIABLO | Tekken | Heihachi Mishima | Domineering warlord voice for a devil-soul boss |
| SKULL | Tekken | Bryan Fury | Unhinged rage IS the Punisher Soul |
| SAM-UR-A1 | Tekken | Jack-7 | Flat machine voice for a mech designation |
| SAKU RA | Tekken | Ling Xiaoyu | Playful idol energy IS Saku Ra |
| ZUI | Tekken | Steve Fox | Cocky boxer patter for a drunken showman |
| KINPO | Tekken | Asuka Kazama | Spunky Kazama-girl for a SHA splinter |
| WATERFALL | Tekken | Josie Rizal | Josie's tearful fighter IS "grief of nine" |
| KING TYRANT | Tekken | Eddy Gordo | Brazilian showman rhythm for a showman king |
| BURGER | Tekken | Bob Richards | Jolly food-obsessed brawler IS Burger |
| AWA POP | Tekken | Lucky Chloe | Bubbly idol menace fits "Bubbles" better than Nina's ice — personality over base |
| SCIMITAR | Tekken | Shaheen | Disciplined soldier for a desert blade |
| PURPLE RAIN | Tekken | Lee Chaolan | Lee's "Excellent!" showman IS Purple Rain |
| NIGHTWOLF | Tekken | Julia Chang | Grounded resolve for a storm-shadow guardian |
| DIO | Street Fighter | Akuma | Apocalyptic demon voice IS Dio |
| CYBORG X | Tekken | Alisa Bosconovitch | Polite killer-robot for a GYOU splinter |
| MICHIKO | Tekken | Katarina Alves | Sassy Brazilian striker IS the Savate Queen |
| STAR | Tekken | Christie Monteiro | Bright capoeira rhythm for a KAI splinter |
| TORCH | Tekken | Anna Williams | Purring assassin for a fire assassin |
| BRUNO | Tekken | Miguel | Hot-blooded Spaniard for a matador |
| N3GΔTIV0 | Tekken | Negan | Sadistic drawl IS a bounty hunter |
| THOR | Tekken | Ganryu | Boastful god-voice over sumo reads as Thor |
| YUKIHYŌ | Tekken | Armor King | Silent-growl ninja for a snow leopard |
| SLICE | Tekken | Dragunov | Cold silent agent IS Slice's cover |
| DOC FRANK | Tekken | Dr. Bosconovitch | Apologetic inventor voice IS Doc Frank |
| KEVIN | Tekken | Baek Doo San | Disciplined TKD master voice |
| MARIPOSA | Tekken | Zafina | Enigmatic seer voice IS Mariposa |
| DXMMII | Tekken | Mokujin | Playful party voice for a patchwork DJ |
| ZANGIEF | Street Fighter | Zangief | The Red Cyclone's wrestling roars |
| CHARGER | Street Fighter | Blanka | Feral beast voice IS an ice monster |
| VEGA | Street Fighter | Vega | Narcissistic Spaniard IS the Claw |
| IORI | KOF | Iori Yagami | Brooding flame voice IS Iori |
| KRONOS | Street Fighter | Zangief | Titanic wrestling voice, aged into a titan (grappler archetype fit) |
| DEATHFANG | KOF | Iori Yagami | Anguished flame voice for a chained prisoner |
| RYUJI | KOF | Ryuji Yamazaki | Sadistic laugh IS the Wicked Heretic |
| KORESHI | Tekken | Raven | Stoic shadow-operative for a shadow ninja |
| RAVE | Tekken | Kazuya Mishima | Cold theatrical menace fits a painted dark trickster better than Lei's clowning — personality over base |

Shared sources are deliberate and documented (Zangief → zangief + kronos;
Iori → iori + deathfang; Armor King → armor-king [tier A audio] + yukihyo
[mapped]). Different lines per fighter; the clone pipeline splits them
into fully proprietary voices anyway.

## Announcer (owner-approved 2026-10-22)

`game/data/voices/announcer.json` — Tekken-style calls: Round 1/2/3,
Final Round, Fight!, K.O., Double K.O., Perfect!, Time Up, Draw, You Win.
**Subtitle-only placeholder**: the mapping is "Tekken series announcer" but
NO Tekken audio bytes ship in the public repo (owner law: no copyrighted
game files). Wired triggers in `game/js/game.js`: `_startRound` (round +
final-round calls), the FIGHT! beat, `_endRound` (K.O. / Perfect! / Time Up
/ Double K.O. with the loser's KO cry, the winner's win line, and a delayed
taunt beat).

**Local-build extraction path** (not in the repo): a Tekken announcer can be
dropped in later as `game/assets/voices/announcer/<trigger>-<NN>.ogg` with
`status` flipped from `"placeholder"` — zero code changes. The Urban Reign
teardown shows the reference architecture: per-stage `bgNN_01.adx` BGM +
per-character `v_*` voice ADX (`teardown/urban-reign/sound/ok_adx/ADX-INVENTORY.csv`).

## Trigger map (where teardown games fire voice → where we fire it)

| Teardown convention | WH trigger | Wired in |
|---|---|---|
| Round intro | `announce('round-N' / 'final-round')` | `game.js` `_startRound` |
| "FIGHT!" | `announce('fight')` | `game.js` `_startRound` beat |
| KO / Perfect / Time Up | `announce('ko'/'perfect'/'time-up')` + loser `play(id,'ko')` | `game.js` `_endRound` |
| Win pose | `play(winner,'win')` + delayed `play(winner,'taunt')` | `game.js` `_endRound` |
| Select confirm | `play(id,'select')` | `main.js` `confirmSelection` |
| Hit reactions | throttled `play(def,'hit')` (heavy/counter, ≤1/1.1 s per fighter) | `game.js` hit resolution |
| Intro interactions | `playLine` per beat | `intro-interactions.js` (existing) |
| Cutscenes | `playCue` | cutscene timeline (existing) |

## Sound bank: the 229 Eastern Mind sounds (owner 2026-10-22)

The full extraction ships as `game/data/sound-bank.json` +
`game/assets/sounds/*.ogg` (every sound OGG'd, categorized
`voice`/`prologue`/`stage`, durations inventoried, `mappedTo` marks the
clips already wired into the voice manifests above). Play any of them
with `voice.playSound(bankId)` — the prologue D_* narration, SHARED
stingers, and stage beds are cutscene/UI candidates; wire per use, no
engine changes needed.

## Deferred: crowd reactions (owner decision 2026-10-22)

**SKIP for now — do not build.** Tekken has little of it, and our stages
have no crowds. When crowds are added to stages, crowd reactions ship WITH
the crowd system (per-stage crowd beds + reaction stingers, most likely as
`game/assets/crowd/<stage>/` driven by a future crowd module). This doc is
the bookmark.

## Replacement path (voice-clone pipeline)

Worker 13's pipeline (`tools/character-voice/voice-clone/`,
contract `docs/VOICE-CLONING-PIPELINE.md`) replaces these placeholders:
write a voice spec per fighter, generate, review via direct download links,
`--deposit` writes `game/assets/voices/<fighter>/` and flips `status` to
`"final"`. Tier A `"teardown"` clips are replaced the same way. The
`direction` + `why` fields in every manifest are the brief the voice
sessions read.
