# Fight UI popups fixed to match Tekken exactly (2026-10-24)

## Owner complaint (2026-10-24 19:29 CDT)

Words keep popping up on the screen while fighting — wall break, soul
something, rage — and they obscure the whole fight screen. They should
only happen the way Tekken does it, in the times Tekken does it, and
only then. Tekken does not put big text across the fight mid-exchange.
This breaks fight immersion. The user had already stated this as the UI
immersion law (2026-10-23: never big "WALL BREAK" / "TIME BREAK" style
text across the screen during fights); the law was still being broken
by 18 mid-fight banner call sites.

## What was actually wrong (measured, not guessed)

Every mid-fight system wrote to the same DOM element, `#round-banner`,
styled by `.banner` in `game/styles.css`:

- `position: fixed; inset: 0` — a fullscreen overlay
- `font-size: clamp(40px, 14vw, 120px)` — up to 120px type
- shown 1400ms per call, centered over the fight

A second element, `#surge-name` (`.surge-name`: fixed, top 22%,
up to 52px, 1600ms), did the same for Soul Surge. So a rage activation,
a wall break, a Soul Urge activation, and a soul-system trigger could
each blank out the fight with giant text mid-exchange.

## How Tekken actually does it (evidence)

- **Rage (T7):** "indicated by a red aura around the character and red
  glowing lifebar." No center-screen text. Sources: Steam Community
  T7 Character Overview guide; Twinfinite "How to Do a Rage Attack";
  Polygon T7 location-test report; Tekkenpedia Rage / Rage Drive
  ("highlighted by a blue aura for the attack's duration, and there is
  a distinct sound effect when the Rage Drive successfully hits").
- **Rage Art (T7):** a cinematic armored super. The cinematic itself is
  the announcement; no "RAGE ART" text is described anywhere.
- **Heat (T8, = WH Soul Urge):** "visualized by blue flames emanating
  from the fighter and a fast-depleting gauge under the health bar"
  (GameRant); "covered with a Blue flame" + "blue bar located just below
  your character's health bar" that "changes to purple" (NerdStash,
  Esports.gg, CharlieIntel, RealSport101). No big "HEAT" text.
- **Wall / floor / balcony breaks (T6/T7):** described purely as stage
  mechanics — the wall shatters, the opponent stays prone, the combo
  continues, damage scales 10% down (Wavu Wiki "Stage break"; Tekken
  Wiki "Wall Break"). No on-screen break text is described anywhere.
- **What Tekken DOES show big:** round boundaries only — ROUND 1/2/3,
  READY, FIGHT, K.O., TIME UP, PERFECT, DOUBLE K.O. Those are the only
  times big center text is Tekken-exact.

Rule applied: **big center text only at round/mode boundaries, never
mid-exchange. Mid-fight states show via aura, health-bar tag/gauge,
screen flash, sound, and the move cinematic itself — exactly as Tekken
does.**

## Removed (18 mid-fight call sites, 8 files, deletions only)

| File | Removed | Tekken-exact replacement (already in code, kept) |
|---|---|---|
| `game/js/rage.js` | `ui.banner('RAGE')` on rage activation | red aura (`setRageAura`) + small `RAGE` health-bar tag (`ui.setRage`, 11px pulsing) + `audio.rage()` cue |
| `game/js/rage.js` | `ui.banner('RAGE ART')` on rage-art hit | `rageArtFlash()` + hitstop + arena shake + slow-mo cinematic |
| `game/js/soulurge.js` | `ui.banner('SOUL URGE')` on activation | urge aura (`setUrgeAura`) + Urge gauge under health bar (`ui.setUrge`, `updateUrge`) + `audio.urge()` cue |
| `game/js/soulurge.js` | `ui.banner('URGE SMASH')` on connect | hitstop + shake + `rageArtFlash()` |
| `game/js/soul-systems.js` | `NINE-SOUL RELEASE` banner on release | super effects + spirit visuals; no text (Tekken supers show no text) |
| `game/js/soul-systems.js` | `REIHOU` banner on reihou | spirit flare (`_spiritFlare`, `setAuraFlare`) + foe rage purge |
| `game/js/soul-systems.js` | `SOUL RELEASE READY` banner on meter fill | meter-ready indicator (`ui.setSoulReady`) |
| `game/js/stagebreaks.js` | `WALL BREAK` / `FLOOR BREAK` / `BALCONY BREAK` banners | wall/floor shatter visuals + debris + shake + hitstop + bounds extension + audio |
| `game/js/finisher.js` | `FINISHER — <name>` banner on KESSHOU | finisher cinematic beats + x-ray flashes + poses (cinematic is the announcement) |
| `game/js/main.js` | `V-TRIGGER` / `V-REVERSAL` / `V-SHIFT BREAK` / `V-SKILL PARRY` banners (all `«name TBD»`) | `surgeFlash()` color flash per system (vShift already used flash-only — the correct pattern) |
| `game/js/game.js` | `surgeName()` on player + AI Soul Surge activation | `surgeFlash()` + `audio.soulSurge()` |
| `game/js/spirit-actions.js` | `魂 ACTION` banner on Spirit Action | context-finisher cinematic clip + damage (clip is the announcement) |

`banner()` itself and `surgeName()` stay defined: `banner()` is still
used by the legitimate round-boundary calls, and `surgeName()` stays
defined so any un-audited caller cannot break (both known mid-fight
call sites were removed).

## Kept (Tekken-time or small/functional, not obscuring)

- Round boundaries: `ROUND n`, `FIGHT!`, `K.O.`, `DOUBLE K.O.`
  (`game/js/game.js`) — Tekken-exact times.
- Round-end verdict: `TRIAL'S SEAL` (`game/js/soul-systems.js`,
  fires only in `onRoundEnd`) — round-end time, like K.O.
- Mode boundaries (fire between fights/waves/bouts, never
  mid-exchange): arcade `FIGHT n — foe`, survival `WAVE n`,
  `WAVE CLEARED`, tournament `VS`, ranked `RANK BATTLE`,
  Heart-and-Mind `STAGE · ECHO n/N`, `ECHO DOWN`, `STAGE CLEARED`,
  Episodes chapter labels (`game/js/modes.js`,
  `game/js/heartmind.js`, `game/js/episodes.js`,
  `game/js/ranks.js`).
- Small/functional HUD (never fullscreen): combo counter
  (`#combo-pop`, small, left side), throw-break prompt
  (`#throw-prompt`, small pill, gameplay-critical), rage tag,
  urge gauge, Nine-Soul Meter label, `RESET — DUMMY RESTORED`
  (training-mode dummy reset, not a live fight).
- Cutscene tool `WHLabels.banner()` (`game/js/labels3d.js`, 3D title
  cards) — cutscene use only, no fight call sites found; untouched.

## Audit scope

Every `game/js` file that references the fight UI object or is
fight-UI-adjacent was fetched from main and grepped for `banner` /
`surgeName` (~45 files, including all of `game/js/game.js`,
`fighter.js`, `main.js`, `rage.js`, `soulurge.js`,
`soul-systems.js`, `stagebreaks.js`, `finisher.js`,
`spirit-actions.js`, `modes.js`, `heartmind.js`, `episodes.js`,
`online.js`, `tournament-ui.js`, `versus-setup.js`,
`select-screen.js`, `menus.js`). Pure data/rigging/physics/material
files do not import the UI object and cannot call `ui.banner`.

## Proprietary names for Tekken systems (from repo files + docs)

LOCKED (user-approved, use these, never the Tekken name):

| Tekken system | WH proprietary name | Source |
|---|---|---|
| Heat (T8) | **SOUL URGE** | `docs/owner-directives.md` (NAME LOCKED 2026-10-22); `game/js/soulurge.js` header |
| Heat Bar | Urge gauge | `game/js/soulurge.js` rename table |
| Heat Burst | Urge Burst (2+3) | `game/js/soulurge.js` rename table |
| Heat Engager | Urge Engager | `game/js/soulurge.js` rename table |
| Heat Smash | Urge Smash (2+3 during Urge) | `game/js/soulurge.js` rename table |
| Heat Dash | Urge Dash (1+2 during Urge, 1 pip) | `game/js/soulurge.js` rename table |
| Heat Energy pip | Urge pip | `game/js/soulurge.js` rename table |
| Finisher system | **KESSHOU (結章)** | `docs/design/SOUL-SYSTEMS.md`; `game/js/finisher.js` |
| Super (full meter) | **Nine-Soul Release / Climax (九魂極)** | `docs/design/SOUL-SYSTEMS.md`; `game/js/soul-systems.js` |
| Spirit Release | **Reihou (霊放)** | `docs/design/SOUL-SYSTEMS.md`; `game/js/soul-systems.js` |
| Round-end verdict | **Trial's Seal (試練の封)** | `docs/design/SOUL-SYSTEMS.md`; `game/js/soul-systems.js` |
| Context finisher (during Urge) | **魂 ACTION / Spirit Action** | `game/js/spirit-actions.js` header (canon, owner 2026-10-23) |
| Fight lab mode | **GUNGAKU (軍楽)** | repo docs |
| Chess Kombat side mode | **Go Qombat** | `~/MEMORY.md` (user spelling) |

NEEDS NAME — flagged, NOT invented (user names these):

| Tekken system | Current WH state |
|---|---|
| Rage (WH version) | Code + small health-bar tag still say `RAGE`; no proprietary name in any doc. Rename the tag too when the user picks the name. |
| Rage Art | Code synthesizes `RAGE ART` moves; no proprietary name. |
| Rage Drive | Code synthesizes `RAGE DRIVE` moves; no proprietary name. |
| Power Crush | No proprietary name in docs. |
| Screw / Tailspin / Tornado | No proprietary name in docs. |
| Wall Break / Floor Break / Balcony Break | Mechanics wired (`game/js/stagebreaks.js`); no proprietary names. |
| V-System (V-Trigger / V-Reversal / V-Shift / V-Skill) | Explicitly `«name TBD»` in `game/js/main.js` — flagged, not final. Banners removed; flashes remain. |
| WWE entrance-tool repurpose | Name TBD (`WH_CINEMATIC_TOOLS_WORKING_TITLE` working title only). |
| Stage-intro sweep presentation | Proposed `LAND REVEAL` (minor flag in `game/js/stage-intros.js`). |

Note: `docs/design/SOUL-SYSTEMS.md` said "HUD callout SOUL RELEASE
READY" and one line still said `HEAT`; both fixed in this pass
(meter-ready indicator wording; `SOUL URGE` wording). The Trial's
Seal "decisive verdict seal banner" line stays — that banner is kept
(round-end only).

## Verification

- `node --check` passes on all 8 edited JS files.
- Grep of edited files: zero remaining mid-fight banner/`surgeName`
  call sites; all kept banners and all Tekken-style indicators
  (auras, tags, gauges, flashes, audio cues) still present.
- Diff is deletions only: rage −2 lines, soulurge −2, soul-systems
  0 net (3 inline removals + comment updates), stagebreaks −2 net
  (−3 banners +1 header note), finisher −1, main −4, game −2,
  spirit-actions −1. No logic, damage, timing, or animation changed.
- Playtest owed (parent browser step, post-deploy): on Netlify, play
  a versus fight and trigger rage (≤25% HP), Soul Urge (2+3 burst),
  a wall break, a Soul Surge, and a Spirit Action — confirm no big
  center text appears mid-fight, and that ROUND/FIGHT/K.O. still show
  at round boundaries. GPU screenshot comparison can run in that same
  browser step; no GPU job was applicable to this code-only fix
  (deletions verified by grep + `node --check` in seconds).
