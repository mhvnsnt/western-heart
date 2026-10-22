# PLAYER IDENTITY + ACCESSIBILITY + SIDE GAMES — CANON MAPPING
Worker 35 · 2026-10-22 · for OWNER APPROVAL — nothing below is locked.

Every system: teardown pull → WH canon mapping → approval status.
Code: `game/js/identity.js` (profile core), `game/js/wh-boot.js` (game wiring),
`game/identity.html` (hub), `game/settings.html` (accessibility),
`game/side-games.html` (hub + 2 playable prototypes),
`game/css/identity.css`, `game/css/colorblind.css`.

---

## 1. PLAYER TITLES — ⏳ PROPOSED, needs approval

**Teardown pull:** Tekken 7's unlockable player titles, shown on player info and the
versus screen, earned through play (not bought). Tekken's rank titles double as
identity (Brawler → Warrior → … → Tekken God).

**WH mapping:** titles are carved by the shrine into the soul's incarnation record
(canon: the shrine keeps a face/portrait/voice record per soul — titles are the
record's marginalia). Trial-flavored, Nine-Soul flavored, rank-ladder flavored.

**Proposed list** (unlock in parens):
| Title | Trial |
|---|---|
| Lost Soul | default — the rank ladder's entry tier |
| Trial-Walker | clear arcade |
| Wood-Bearer / Fire-Bearer / Earth-Bearer / Metal-Bearer / Water-Bearer | claim each elemental force (manual unlock, wired to story/mode worker) |
| Reborn | die 10 times — "Death is not failure. It is the mechanism." |
| Unbroken | 5-win streak |
| Untouched | a perfect victory |
| Haggler of the Marketplace | trade with the Trader |
| Purified | win through the Soul Surge |
| The Eyeballs' Favorite | spend 10,000 currency under the Eyeball Mountains |
| Soul-Friend | 25 battles |
| Tong-Nou's Witness | 100 battles |
| Whole | reach the apex rank (manual) |

**Approval needed:** the list, the flavor text, and whether elemental-bearer titles
should be per-fighter or per-player.

---

## 2. CUSTOMIZABLE PLAYER CARDS — ⏳ PROPOSED, needs approval

**Teardown pull:** SFV Fighter Profile — name, title, comment, favorite character,
stats, customizable background; TTT2's player-card presentation.

**WH mapping:** the card IS the shrine's incarnation record made visible — the face
the soul wore when the head first dreamed it. Customization:
- **Elemental frames** (Wood/Fire/Earth/Metal/Water/Prism) — the land that claims you,
  each with its alchemical sigil (🜃🜂🜔🜄🜏 — owner-approved for identity use).
- **Pattern backs** drawn from Japanese tradition + the art bible: Seigaiha waves,
  Asanoha hemp, Shippo treasures, Soul Mandala (psychedelic Buddhist/Hindu),
  Ichimatsu check.
- Name, title, motto ("Fight. Die. Return."), soul-bound favorite fighter, live
  stats (wins / battles / best streak / max combo).
- The card paints onto P1's versus HUD nameplate in-game (wh-boot.js).

**Approval needed:** frame/pattern sets, and whether cards should show the fighter's
portrait render (needs the portrait pipeline) vs. the current sacred-geometry backs.

---

## 3. IN-GAME CURRENCY — ⏳⏳ NAME IS A CREATIVE CALL, DO NOT LOCK

**Teardown pull:** Tekken 7 Fight Money — earned EVERY battle, win or lose; spent on
customization; the "G" economy with 5,000,000G / 10,000,000G lifetime achievements.
Our economy mirrors it: win = 120 + 20/streak + bonuses (Perfect +150, Surge win +80);
loss = 40. One constant renames everything (`CURRENCY_NAME` in identity.js).

**WH mapping — three options with lore justification:**

- **Option A — "Soul Shards" (recommended).** Every fight chips a fragment off the
  loser's soul; the shrine sweeps them up and pays out. Fits the Nine-Soul cosmology
  directly — currency as literal soul-matter. Losing still pays because even the
  broken-off pieces are real.
- **Option B — "Trader's Coin".** The Phantom Marketplace's scrip. The Trader pays
  fight purses the way a promoter pays a card — and King Tyrant already believes the
  trial is a promotion with a payday. "Nothing here is real, but the prices are."
- **Option C — "Death Tithe".** The shrine's due. Death is the mechanism, and every
  death pays the tithe; the Reincarnation runs on it. Darker, more theologically WH.

**Approval needed:** the NAME. Shipped default is Option A, one-line rename.

---

## 4. TREASURE BOXES / LOOT — ⏳ NAME IS A CREATIVE CALL, DO NOT LOCK

**Teardown pull:** Tekken 7 Treasure Battle — 1–3 chests per victory; bonus chest for
Perfect / Great / Double-KO; rarities Bronze&Ruby (very frequent) < Silver&Emerald
(frequent) < Gold (rare) < Rainbow (very rare); Special Matches drop Gold/Rainbow;
chest-only items never appear in the shop.

**WH mapping — three name options:**
- **Option A — "Soul Caches" (recommended, shipped).** Where fallen fighters fell,
  their shed soul-matter pools and hardens. Cracking one open is grave-robbing with
  the shrine's blessing.
- **Option B — "Shrine Offerings" (お供え).** Offerings left at the Octagonal Shrine
  by souls grateful to be reborn — the shrine shares them back out. Festival flavor.
- **Option C — "Trader's Stashes".** The Trader skims every deal; his stashes leak
  back into the world. Marketplace flavor.

Rarity ladder (Tekken's precious-material ladder, WH-flavored):
Clay (very frequent) → Stone → Jade → Gold (rare) → Prism (very rare).
Contents: currency + 35% bonus pull from the chest-only pool (titles, Prism frame,
Mandala/Shippo patterns) — mirroring Tekken's chest-only items.
Drops are awarded automatically on the match-result screen (wh-boot.js observer —
no edits to main.js/game.js needed).

**Approval needed:** the NAME and the rarity ladder.

---

## 5. BUTTON REMAPPING — ✅ WIRED

**Teardown pull:** Tekken-standard remapping (every action rebindable; modern fighters
all ship this).

**WH mapping:** none needed — pure utility. Constraints honored: the **virtual joystick
is never touched** (owner-approved); face buttons (LP/RP/LK/RK), legacy P/K, throw,
surge, block, dodge, and movement keys are all remappable. Touch buttons (.act-btn
cluster) are reassignable per-button; applied by the boot script before the input
manager binds.

**Implementation:** `input.js` `_remapCode()` translates physical keys to canonical
action codes before dispatch (defaults preserved when no remap); keyup made
remap-aware so held keys (block) release correctly; conflict clearing (one key, one
action); `RESET TO TEKKEN DEFAULTS`.

**Known limitation:** simultaneous opposite-direction holds use the remapped physical
codes — correct in all tested cases; exotic double-remaps fall back safely.

---

## 6. COLORBLIND OPTIONS — ✅ WIRED

**Teardown pull:** modern fighters (SF6/GGST) — player-pickable P1/P2 and UI colors
instead of hardcoded red/green.

**WH mapping:** none needed — pure accessibility. Five presets via
`<html data-cb>` overriding the HUD's CSS variables:
Standard / Deutan (blue vs orange) / Protan (blue vs yellow) / Tritan (vermillion vs
teal) / High-contrast mono. Covers HP bars, Nine-Soul meter segments, round pips,
P1/P2 tags, combo popup. Applies instantly on every page and in-fight.

---

## 7. DIFFICULTY ASSISTS — ✅ WIRED (input layer) / ⏳ COMBAT HOOK SPECIFIED

**Teardown pull:** SF6 Modern controls (one-button specials, auto-combos) and Dynamic
(AI-assisted inputs). Philosophy: execution help, never playing the game for you.

**WH mapping:** assists are framed as the Trial meeting the soul where it is —
"the Trial respects effort, not purity." Titles still count with assists on.

| Assist | State |
|---|---|
| Auto-combo (mash LP → 1-2-1 string) | ✅ wired via input queue |
| One-button special (Surge at 7+ souls on S) | ✅ wired via input queue |
| Throw-break assist (any limb = correct break while prompt shows; timing still yours) | ✅ wired via input queue |
| Damage dealt 50–150% | ⏳ stored live in `window.WHAssistDamage`; combat hook specified below |
| Damage taken 50–150% | ⏳ same |

**Combat hook for the combat worker** (4 lines, at game.js's two hit-resolution
sites — the `dealt` computations near the `hpBefore` reads):
```js
// after: const dealt = Math.max(0, hpBefore - def.hp);
const w = window.WHAssistDamage;
const dealtAdj = w ? dealt * w.dealtFor(attackerIsPlayer) * w.takenFor(defenderIsPlayer) : dealt;
```
`attackerIsPlayer`/`defenderIsPlayer` are whichever side flags game.js already
tracks at those sites. Damage numbers stay honest — the multiplier object is live,
so the settings page changes apply mid-session.

**Approval needed:** assist philosophy — are damage sliders "honest help" or too
much? Should they scale CPU damage too, or player-only?

---

## 8. SIDE GAMES — ⏳⏳ ALL CONCEPTS NEED APPROVAL (user: go deep, mythology-first)

**Teardown pull:** Tekken Bowl / Tekken Ball — physics party games with fighting-game
characters, winnings feeding the main economy.

**WH direction (owner-locked):** NOT generic bowling. Games native to the mythological
world — festival games (matsuri), spirit trials, yokai pastimes — mainly Japanese,
mixed with world mythologies per the NORTH STAR ("the universe digests world
mythologies"). Each concept: myth root + WH identity + how it plays + home.

### 🎮 PLAYABLE PROTOTYPES (in `game/side-games.html` now)
1. **Soul-Fruit Harvest** — Tree of Life (Wood). *Myth root:* tamaire, the festival
   ball-toss. *WH:* the Tree "holds glowing souls like fruit" (canon) — toss
   spirit-orbs back into the branches; every orb returned guides a soul home.
   Physics arcs, 10 orbs, 45s, shard payouts.
2. **The Trader's Chō-han** — Phantom Marketplace. *Myth root:* chō-han bakuchi dice
   gambling. *WH:* the Trader runs the table; bet shards on even/odd; the house
   takes 5%. "Nothing here is real, but the prices are."

### THE FIVE LANDS
3. **Daruma Drop — Stack of the Nine** (Octagonal Shrine, Earth). *Root:* daruma
   otoshi. Nine soul-blocks etched 凛病闘沙海刃烈禅行; hammer blocks out — TOU's
   block enrages the tower, ZEN's steadies it. Rigid-body sway, purify the stack.
4. **Koi-Scooping of the Dreaming** (Palace of Dreaming, Water). *Root:* kingyo-sukui.
   Scoop spirit-koi (each a dream someone is having) with a tearing paper poi; the
   pool tilts because the palace won't stay still. Prism-koi jackpots.
5. **Oni Hunt** (Plains of Chi-U, Fire). *Root:* setsubun mamemaki ("Oni wa soto!
   Fuku wa uchi!"). Pelt intruder-oni effigies (Diablo, unbound RETSU) with
   fortune-beans; perfect volleys shout FUKU WA UCHI.
6. **Hyakumonogatari — One Hundred Soul Tales** (Helix Palace, Metal). *Root:* Edo
   kaidankai. 100 candles, one trial-vignette per tale; at zero candles something
   from the Destruction room arrives. Rarest cache in the game.

### MARKETPLACE & TRIAL
7. **Eyeball Auction** (Phantom Marketplace). *Root:* world-market haggling + the
   Eyeball Mountains audience (canon — King Tyrant plays to them). Blind-bid on
   sealed caches against AI souls with tells; the mountains rumble luck.
8. **The Nine Trials** (Octagonal Shrine). *Root:* the Trial, bite-sized; Shugendō
   ordeals. One 60–90s trial per soul, each a parable of its nature (ZEN scores by
   NOT moving; GYOU by never stopping; JIN one-hit duels…). Medals, leaderboards.
9. **Scimitar's Ledger** (Phantom Marketplace). *Root:* hanafuda/kabufuda gambling
   halls. The Trader's vizier deals a matching game from his ledger of the
   merchant's weaknesses; final table is Scimitar himself, and he cheats the way
   the marketplace cheats.

### FESTIVAL & SOULS
10. **Kagome Circle** (Octagonal Shrine festival). *Root:* kagome kagome. Eight souls
    in the eight-sided circle, one caged; rhythm + guessing; the last caged faces
    Phantom's Fiend-laugh.
11. **Soul Karuta** (Octagonal Shrine festival). *Root:* uta-garuta. 100 cards of
    soul kanji and fighter verses, read by the shrine; slap the match before your
    rival. Phantom reads in three voices at high difficulty.
12. **Kemari of the Nine** (Tree of Life festival). *Root:* Heian kemari. Circle
    keepie-uppie with a soul-orb — dropping it is a small death. Each soul kicks
    with its nature (TOU smashes, ZEN barely touches).

**Suggested first full builds** (pending approval): Daruma Drop (simple physics,
strong kanji identity) and Oni Hunt (projectile scoring reuses fight input).

**Approval needed:** which concepts ship, names, rules, homes — everything.

---

## FILES (no deletions; 2 surgical edits, rest new)
- `game/js/identity.js` — NEW: profile core (titles/cards/currency/loot/remap/CB/assists)
- `game/js/wh-boot.js` — NEW: boot wiring (CB class, touch remap, result observer, HUD nameplate)
- `game/identity.html` — NEW: player hub
- `game/settings.html` — NEW: accessibility page
- `game/side-games.html` — NEW: hub + 2 playable prototypes + 10 concept cards
- `game/css/identity.css` — NEW: shared page styles + card preview
- `game/css/colorblind.css` — NEW: HUD palettes
- `game/index.html` — MODIFIED (surgical): 3 menu links, colorblind.css, identity+boot scripts
- `game/js/input.js` — MODIFIED (surgical): `_remapCode`, remap-aware keyup, assist hooks in `_push`
- `docs/identity/IDENTITY-CANON-MAPPING.md` — NEW: this file
- `docs/workflows/2026-10-22-player-identity-accessibility-sidegames.md` — NEW: work log
