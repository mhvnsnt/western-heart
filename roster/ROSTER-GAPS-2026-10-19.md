# WESTERN HEART — ROSTER GAPS AUDIT (2026-10-19)

Owner's three questions (2026-10-19 ~00:42 CDT), answered from the actual repo state:
`roster/TRIPO-REGISTRY.md`, `CANON.md`, `ROSTER.md`, `roster/*/ATTIRE-SLOTS.md`,
`game/assets/models/` listing — all read from `origin/main` via the GitHub API on 2026-10-19.

No invented canon. Where a bio is thin or missing, it says so.

---

## Q1 — WHO ELSE NEEDS A TRIPO MODEL?

"No Tripo on record" = no Tripo attachment in `roster/TRIPO-REGISTRY.md` AND no pull
recorded in flight. Characters with pulls already in flight are marked separately.

### No Tripo on record (needs an owner Tripo link / new Tripo build)

**CORRECTION 2026-10-19:** PANTERA was listed here in error and has been removed — the owner confirmed "Leo man" IS his original Tripo model (Slot 2). The "NOT ON RECORD" note in this doc and in TRIPO-REGISTRY.md was wrong; both corrected.

| # | Character | Current model state | Base |
|---|---|---|---|
| 1 | **DEMONIO** | `game/assets/models/demonio.glb` wired (in-game base only) | Jin Kazama |
| 2 | **DIABLO** | `game/assets/models/diablo.glb` wired (in-game base only) | Heihachi Mishima |
| 3 | **SKULL** | `game/assets/models/skull.glb` wired (in-game base only) | Bryan Fury |
| 4 | **SAM-UR-A1** | `game/assets/models/sam-ur-a1.glb` wired (in-game base only) | Gun Jack |
| 5 | **KINPO** | `game/assets/models/kinpo.glb` wired (+ `kinpo-t8`, `kinpo_alt1`); in-game bases only | Asuka Kazama |
| 6 | **BURGER** | **NO GLB WIRED AT ALL** — no `burger.glb` in `game/assets/models/` | Bob Richards (T6) |
| 7 | **SCIMITAR** | `game/assets/models/scimitar.glb` wired (PR #284, Shaheen rip, unrigged static) | Shaheen |
| 8 | **MICHIKO** | `game/assets/models/michiko.glb` wired (fighter hunt) | Katarina Alves |
| 9 | **TORCH** | `game/assets/models/torch.glb` wired (fighter hunt) | Anna Williams |
| 10 | **DIO** | `game/assets/models/dio.glb` wired (fighter hunt) | Akuma (T7) |
| 11 | **BRUNO** | `game/assets/models/bruno.glb` wired (fighter hunt) | Miguel |
| 12 | **N3GΔTIV0** | `game/assets/models/n3g4tiv0.glb` wired | Negan-style base |
| 13 | **DXMMII** | `game/assets/models/dxmmii.glb` wired (in-game base only) | Patchwork build |
| 14 | **RAVE** | `game/assets/models/rave.glb` wired (in-game base only) | Lei Wulong |
| 15 | **DOC FRANK** | `game/assets/models/doc-frank.glb` wired | Dr. Bosconovitch |
| 16 | **JIN** (Kazama) | `game/assets/models/jin.glb` wired (in-game base only) | Jin Kazama |
| 17 | **YUKIHYŌ** | `game/assets/models/yukihyo.glb` wired (fighter hunt) | (fighter-hunt source) |
| 18 | **SLICE** | **NOT WIRED** — Dragunov source is a 509-bone pro control rig (needs dedicated rigging lane) | Dragunov |
| 19 | **CHORDZ** | **NO SOURCE FOUND** — nothing on disk; disk too tight for a full T7 pull | unknown |
| 20 | **VAIN** | Tripo GLB exists locally (`~/workspace/tripo-downloads/`, 19MB, by marz6kdabest) but **NOT wired, NOT recorded** in the registry | Bass Armstrong |

### Pulled already — wiring/rigging in flight (NOT "needs a model")

- **NIGHTWOLF** — Tripo pulled (`nightwolf-tripo.glb`); wiring pending.
- **PHANTOM** — Tripo pulled (`phantom-tripo.glb`); wiring pending.
- **SUN RĀ** — Tripo pulled (`spiky_sun_creature_3d_model.glb`); rig + fight-video lane in flight.
- **KEVIN** (replacing Baek) — Tripo pulled (`kevin-tripo.glb`); PR #278 open.
- **STAR** — Tripo pulled (`red_latex_cosplay_3d_model.glb`); 4-attire build lane in flight.
- **KING TYRANT** — Attires 1/2/3 pulled; wiring lane in flight.
- **SILVERTONGUE** — Tripo pulled (`silvertongue-tripo.glb`); reserved for Slot 1, wiring pending. (Current Slot 1 = "Spy Debut" Creation Suite build.)

### Tripo-attached and done (for reference)

ZUI, THOR, AWA POP, WATERFALL, SAKU RA, PURPLE RAIN, KIKO TANAKA, CAPE JONES/CYBORG X, MARIPOSA (Slot 1 wired), PANTERA (Slot 2 = "Leo man" Tripo, owner-confirmed 2026-10-19; Slot 6 = Leopard King wired 2026-10-19).

---

## Q2 — WHO ELSE NEEDS WESTERN HEART / EASTERN MIND NAMES AND BIOS?

"Done" = proprietary WH/EM name locked + full bio in `CANON.md`. Everyone in The Seven,
The Four, The Twelve, and The New Vessels is done. The gaps:

| # | Character | Name status | Bio status | Notes |
|---|---|---|---|---|
| 1 | **RAVE** | ✅ WH name locked (Rave) | ❌ **NO BIO in CANON.md** | Lei Wulong base; kitbash notes "Great Muta/Keiji Mutoh skin" |
| 2 | **JIN** (Kazama) | ❌ still "Jin Kazama" — **name conflicts with the JIN blade soul**; needs a proprietary name | ❌ **NO BIO in CANON.md** | "Bloodline Soul" (PR #258) — but that entry is missing from current CANON.md (see flag below) |
| 3 | **KEVIN** (replacing Baek) | ✅ WH name locked (Kevin) | ❌ **NO BIO** — canon rewrite lane still needed (God Molecule tie-in: Central Mountain trickster, inside Mars' head, forehead portal) | PR #278 (model swap) open |
| 4 | **DXMMII** | ✅ WH name locked (Dxmmii), pronouns it/its | ❌ **NO BIO in CANON.md** (mentioned once, in Doc Frank's relationships) | "Patchwork DJ" attire owner-approved |
| 5 | **THOR** | ⚠️ "THOR" — unconfirmed as a proprietary name | ❌ **NO BIO in CANON.md** | Tripo attached; needs name lock + bio |
| 6 | **VAIN** | ❌ no WH name on record | ❌ **NO BIO in CANON.md** | Tripo pulled but not wired; Bass Armstrong base |
| 7 | **YUKIHYŌ** | ⚠️ "YUKIHYŌ" — unconfirmed as a proprietary name | ❌ **NO BIO in CANON.md** | Wired via fighter hunt |
| 8 | **SLICE** | ❌ no WH name on record | ❌ **NO BIO in CANON.md** | Dragunov base; rig blocked |
| 9 | **CHORDZ** | ❌ no WH name on record | ❌ **NO BIO in CANON.md** | No source found |

Also pending: **ZEN** (the Still Soul) — soul exists in canon, vessel unvesseled ("refused the trial").

### 🚩 HONEST FLAG — missing canon entries (possible clobber)

PR #258 (merged 2026-10-18) added "7. THE NEW VESSELS" with NINE vessels: Lili, Zafina,
Baek, Jin Kazama, Steve Fox, Dxmmii, Mariposa, Doc Frank, Kiko Tanaka. The CURRENT
`CANON.md` section 7 contains only: Silvertongue (= Lili, renamed), Mariposa (merged),
Doc Frank, Kiko Tanaka, Sun Rā. **The Baek, Jin Kazama, and Dxmmii vessel entries are
absent from the current file.** (Steve Fox → Zui already has canon elsewhere.) They may
have been dropped by the Mariposa-merge PR #277. **Needs verification against git
history and recovery if dropped** — do not re-invent; recover the merged text.

---

## Q3 — WHO HAS A BIO BUT NEEDS A TRIPO MODEL?

For each: bio summary, character look, and style — so the owner can judge what Tripo
model to make/commission. All from `CANON.md`; nothing invented.

### 1. DEMONIO — The Demon Soul (Vessel of RIN)
- **Bio:** Named demon, fights like a saint. The most disciplined soul in the trial — bows before every fight (never to Diablo), follows a code he can't name from a life he can't recall. RIN is the protagonist soul, the baseline every other soul deviates from. Being purified of a guilt he can't name.
- **Look:** Jin Kazama's karate frame — precise, unadorned, dignified. Cold courtesy made flesh; the demon who apologizes to no one.
- **Style:** Mishima-style karate — precise, fundamental, the "honest" style. The shoto archetype: balanced, the baseline.

### 2. DIABLO — The Devil Soul (intruder, not one of the nine)
- **Bio:** Wasn't called — tore through the head-world's membrane and announced himself. Fights like a final boss because he believes he is one. Conquest, charisma, absolute certainty; makes declarations, not trash talk. The trial's sparring partner; being purified of the need to be the final boss.
- **Look:** Heihachi's devastating frame, the boss's body worn like a crown.
- **Style:** Heihachi's Mishima karate — powerful, aggressive, the boss style.

### 3. SKULL — The Punisher Soul (Vessel of RETSU)
- **Bio:** Bryan Fury's brutality worn as vocation — fights because something needs punishing. Wears demon paint like a ritual (Punisher × Finn Balor); nobody has seen him without it. Judgment without mercy, few words. Being purified of the mission — stripped down to pure force.
- **Look:** Bryan's brutal frame, demon face paint (ritual), keep Bryan's pants per owner lock.
- **Style:** Bryan's brutal kickboxing — bone-breaking, no wasted motion, every hit meant to end the fight.

### 4. SAM-UR-A1 — The Mech Soul (built, no soul detected)
- **Bio:** Gun Jack's heavy frame rebuilt as a mech chimera. Designation reads SAMURAI but scans as a model number (SAM-∪R-Λ1). Mechanical courtesy, literal-minded, visibly learning — asks every new fighter "WHAT IS YOUR DESIGNATION?" The shrine stones are silent on him; he has started dreaming. Built by Doc Frank.
- **Look:** Gun Jack's heavy frame + Gundam plating + Transformer joints + Power Ranger color breaks.
- **Style:** Gun Jack's power-robot moveset — heavy, mechanical, devastating.

### 5. KINPO — The Buttercup Soul (splinter of SHA)
- **Bio:** SHA split three ways; Kinpo is the thorn — tougher, blunter, green to Saku Ra's pink. Buttercup to Blossom. Not the sidekick — the other protagonist. Blunt, loyal, allergic to sentiment; secretly visits losers after matches with water. Being purified of the hardness.
- **Look:** Asuka's aggressive frame; Buttercup (green Powerpuff Girl) direction. Name from kinpōge (buttercup flower).
- **Style:** Asuka's aggressive Kazama-ryu — no nonsense, all forward pressure.

### 6. BURGER — The Hunger Soul (claimed by the Appetite Room)
- **Bio:** Bob Richards' impossible body — fat and fast, the punchline that hits back. His hunger is a *curse* laid by the Helix Palace's Appetite room; he eats between rounds, even during the versus screen. Jolly — terrifyingly jolly. Slim Bob (TTT2) is the uncursed attire, not a separate character. Being purified of appetite.
- **Look:** Bob's heavyweight frame; the fat form IS the cursed form.
- **Style:** Fast-twitch heavyweight brawling — impossibly quick for the size.

### 7. SCIMITAR — The Vizier Soul (born in the Phantom Marketplace)
- **Bio:** The Trader's vizier — smiles while the deal closes around you. Scar's scheming × Jafar's hunger for the lamp; doesn't want the katana to become whole, wants it as *leverage*. Regal, sinister; keeps a ledger of every fighter's debts. Marketplace-born, not trial-called — the trial doesn't know what to do with a soul that isn't broken.
- **Look:** Shaheen's soldier frame — precise, coiled; regal sinister vizier.
- **Style:** Shaheen's military precision — disciplined soldier's body, desert warrior's economy.

### 8. MICHIKO — The Outlaw Soul (a lost soul who refuses the ladder)
- **Bio:** Heard the call, came, but won't climb the ladder. Michiko Malandro's fugitive freedom × Tier Harribel's regal composed power — a queen who ran from her throne. Wanders the five lands picking fights, owing nothing. Magnetic, dangerous, free. Being purified of running.
- **Look:** Katarina's frame; outlaw queen — swagger with a crown left behind.
- **Style:** Katarina's savate — confident, powerful legs, all leverage and swagger.

### 9. TORCH — The Flame Soul (a mortal soul, pulled in by sisterhood)
- **Bio:** Awa Pop's sister — followed her through the membrane out of loyalty, not calling. Anna Williams' ruthless elegance; lethality as manners. Not lost — *loyal*, and the trial doesn't know what to do with that. Ruthless, elegant; files her nails during the versus screen. Being purified of living through her sister.
- **Look:** Anna's assassin poise — every gesture lethal, the darker edge to Awa Pop's sweetness.
- **Style:** Anna's assassin precision — lethality as etiquette.

### 10. DIO — The Demon That Is (the trial's failure mode)
- **Bio:** Akuma's Satsui no Hado worn by something the trial cannot name — tore in from *outside the metaphysics*. Not fragmentation but a different physics: destruction as a law of nature. Silence, then violence; no third mode. The shrine stones don't go silent on him — they *crack*. The test the trial gives itself.
- **Look:** Akuma's demonic frame (Tekken 7 version — NOT Kuma the bear; the bear, if ever pulled, is URSA).
- **Style:** The Satsui no Hado — raging demon, dark hadou made flesh.

### 11. BRUNO — The Heartbreak Soul (a mortal soul, drowned in feeling)
- **Bio:** Died of heartbreak — the heart stopped because it couldn't stand another beat of the ache. Miguel's street-brawler fury worn by a beautiful mess: The Weeknd's 3AM despair × Bruno Mars' silk × Boomhauer's mumble × Johnny Bravo's swagger. Moody, smooth, vain. Being purified of heartbreak.
- **Look:** Miguel's brawler frame; leather-jacket heartbreak, pretty-boy armor over the wound.
- **Style:** Miguel's street brawling — raw, emotional, all power punches thrown from the gut.

### 12. N3GΔTIV0 — The Hunter (not a soul, not a vessel — a contractor)
- **Bio:** Zombie bounty hunter across the galaxies — Negan's bat/grin/certainty × Sinestro's fear-as-weapon × Black Flash's unstoppable death. Followed a bounty into the giant green head; saw souls that die and return and thought *zombies*. Charismatic, menacing; carves the kill-count into the bat's handle. Not being purified — he's working.
- **Look:** Negan's brutal frame; barbed-wire bat (well-maintained) as an extension of the arm.
- **Style:** Brutal brawling + fear as a weapon; when he decides you're dead, no Reincarnation saves you.

### 13. DOC FRANK — The Builder (not one of the nine)
- **Bio:** Born Franklin Bauzzkoh → Frank Bozko → DOC FRANK: the universe's Dr. Frankenstein × Dr. Gero — built androids until he turned *himself* into one. Built Cyborg X and SAM-UR-A1. Theatrical mad genius, proud father; takes notes mid-fight on a clipboard, in crayon. The only soul that *chose* its vessel. Being purified of the god complex.
- **Look:** Rebuilt android — every panel a decision he made about himself; reskins change, the clipboard doesn't. Dr. Bosconovitch base.
- **Style:** ⚠️ No signature fighting style documented in canon (honest gap — Bosconovitch-style mad-science brawling implied, not specified).

---

## How this was built

- Read `roster/TRIPO-REGISTRY.md`, `CANON.md` (91KB, 36 character sections), `ROSTER.md`,
  `roster/{mariposa,silvertongue}/ATTIRE-SLOTS.md`, `roster/bonus/BONUS-CHARACTERS.md`,
  and the `game/assets/models/` GLB listing from `origin/main` via the GitHub API, 2026-10-19.
- Tripo "in flight" states cross-checked against the owner's live pull log
  (`~/workspace/tripo-downloads/` manifests + renders).
- Canon coverage checked by section headers + full-text search (BAEK/KEVIN/JIN/DXMMII/RAVE/
  THOR/VAIN/YUKIHYŌ/SLICE/CHORDZ all searched; only Doc Frank, one Jin Kazama mention,
  and one Dxmmii mention found outside the 27 full bios).
- Nothing invented. Gaps and conflicts are flagged, not filled.
