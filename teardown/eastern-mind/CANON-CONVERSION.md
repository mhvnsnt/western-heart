# EASTERN MIND — CANON CONVERSION LOG

The Eastern Mind lane's source of truth for the Full Wiring + Canon Conversion order
(owner, 2026-10-20 ~08:06 CDT). Every inventoried group in
`teardown/eastern-mind/WIRING-INVENTORY.md` is accounted here:
source material → the Western Heart canon it became → where it landed.
Anything unmapped or ambiguous is flagged, never silently filled.

**Method.** Inventory and counts come from the `main` git tree (GitHub git-trees API,
recursive, `truncated: false`): **5,707 files (blobs)** under `teardown/eastern-mind/`,
420,423,503 bytes — 5,321 PNG bitmaps, 233 WAV audio, 49 `.pal` + 48 `.bin` palette files,
31 text files, 24 MP4 videos, 1 Markdown document. Wiring evidence was read directly from
`CANON.md`, `game/js/stages.js`, `game/js/modes.js`, `game/js/assets.js`,
`game/js/audio.js`, and `game/js/main.js` on `main` at `fa4f3757341160f03aebb3d18e0f52d7b29e9020`.

## Totals

| Measure | Files |
|---|---:|
| Inventoried | 5,707 |
| WIRED before this PR (canon and/or game data at category/system level) | 3,817 |
| Newly WIRED by this PR (WIRED-PENDING-MERGE until it lands) | 762 |
| NOT WIRED — flagged archival (transcript-promo) | 1,128 |
| Converted to authored WH canon in `CANON.md` §8 by this PR (prologue-ending + soundtrack + palettes) | 762 |

## Category conversions

| Source material | Files | WH canon it became | Where it landed | Status |
|---|---:|---|---|---|
| `stage-4-tree-of-life/` (L_* — Ming-ken, Wood/Life) | 505 | Tree of Life, Land of Life; ladder step 1; Wood force (reach extends) | `CANON.md` §1, §5, §8; `game/js/stages.js` def `tree-of-life`; `game/js/modes.js` `STORY_STAGES` 1 + `FORCES.wood`; registry `game/assets/stages/eastern-mind/stages.json` | WIRED (pre-existing) |
| `stage-1-plains-of-chi-u/` (F_* — Shi-chieng, Fire/Time) | 518 | Plains of Chi-U, Land of Time; Fire Tower of Time; ladder step 2; Fire force (chip through guard) | `CANON.md` §1, §5, §8; `game/js/stages.js` def `plains-of-chi-u`; `game/js/modes.js` `STORY_STAGES` 2 + `FORCES.fire`; registry (this PR) | WIRED (pre-existing) |
| `stage-6-octagonal-shrine-par-fang/` (E_* — Tong-nou, Earth/Source) | 223 | Octagonal Shrine Par-fang, Central Mountain; ladder steps 3 + 7 (final ascent, Assembled Soul); Earth force (defense solidifies) | `CANON.md` §1, §5, §8; `game/js/stages.js` defs `octagonal-shrine`, `shrine`, `tong-nou`; `game/js/modes.js` `STORY_STAGES` 3 + 7 + `FORCES.earth`; registry (this PR) | WIRED (pre-existing) |
| `stage-2-helix-palace/` (G_* — Yui-wang, Metal/Desire) | 1,282 | Helix Palace, Land of Desire; five rooms (Greed, Appetite, Immortality, Sexual Desire, Destruction); ladder step 4; Metal force (regeneration); Burger's curse, Scimitar's Greed, Purple Rain's reflection, Skull's Destruction room | `CANON.md` §1, §5, §6, §8; `game/js/stages.js` def `helix-palace`; `game/js/modes.js` `STORY_STAGES` 4 + `FORCES.metal`; registry (this PR) | WIRED (pre-existing) |
| `stage-3-palace-of-dreaming/` (W_* — Mon-chien, Water/Dreaming) | 676 | Palace of Dreaming, Land of Dreaming; ladder step 5; Water force (movement quickens); Waterfall's and Bruno's element home | `CANON.md` §1, §5, §8; `game/js/stages.js` def `palace-of-dreaming`; `game/js/modes.js` `STORY_STAGES` 5 + `FORCES.water`; registry (this PR) | WIRED (pre-existing) |
| `stage-5-phantom-marketplace/` (D_MARKET, D_MERCHA) | 100 | Phantom Marketplace under the Eyeball Mountains; the Trader; ladder step 6 (trade a force); Trader's Mimic mode | `CANON.md` §1, §5, §8; `game/js/stages.js` def `phantom-marketplace`; `game/js/modes.js` `STORY_STAGES` 6, `TRADER_CFG`, Trader screens; registry (this PR) | WIRED (pre-existing) |
| `incarnation-system/` (R_* — the nine incarnations) | 512 | The soul-vessel framework: nine souls (RIN, BYOU, TOU, SHA, KAI, JIN, RETSU, ZEN, GYOU), their vessels and splinters; death → reincarnation with actions influencing the next vessel; Versus = no reincarnation, Story = reincarnation | `CANON.md` §1 (Death), §2–§4 (vessels, the nine, Soul Surge), §8 (The Two Laws of Death, The Incarnations — distinction made explicit in prose by this PR); `ROSTER.md`; `game/js/modes.js` (`chooseReincarnation`, `VESSEL_AFFINITY`, `reincarnationReason`, `styleProfile`, Diablo 3-death gate, `buildAssembledSoul`) | WIRED (pre-existing); canon prose extended by this PR |
| `prologue-ending/` (D_* prologue/ending, CHARA, PORT, PROF, MAIN, SHARED) | 661 | **The Threshold** — the Face, the Book, the Mirror, the Sea, the Rock, the sumi-e dark, and the Ending: the country a soul passes before its first fight and after its final absorption | `CANON.md` §8 (The Threshold) — **new in this PR**; registry `systems[prologue-ending]` (this PR) | CONVERTED by this PR (was NOT WIRED) |
| `soundtrack/` (CD tracks + ending theme) | 4 | The Music of the Head-World: head-world theme, transmigration/ending theme, esoteric mix, ending theme | `CANON.md` §8 (The Music of the Head-World) — **new in this PR**; registry `audio` (this PR) | CONVERTED by this PR (was NOT WIRED); engine audio consumption still open — see Flags |
| `palettes/` (global CLUT + per-file/per-character palettes) | 97 | Colour Is Law: one shared head-world palette; per-soul/per-face palettes inside it; claimed lands' colours "settle" as the healing chart | `CANON.md` §8 (Colour Is Law) — **new in this PR**; registry `palettes` (this PR); skin palettes already described per soul in `ROSTER.md` | CONVERTED by this PR (was NOT WIRED); texture-pipeline consumption still open — see Flags |
| `transcript-promo/` (AUTODEMO, promo + Sato-works videos) | 1,128 | — none — | Retained as source archive under `teardown/eastern-mind/transcript-promo/`; listed in registry `archive` (this PR) | **FLAGGED — NOT WIRED** (archival promo/transcript material; no canon or game consumer by design) |
| `TEARDOWN.md` | 1 | Teardown record itself (extraction method, format notes, stage mapping) | `teardown/eastern-mind/TEARDOWN.md` | WIRED |

## System conversions (cross-category)

| Source system | WH canon / game system | Where it landed |
|---|---|---|
| Five elemental forces scattered across five lands | The Trial ladder in generating-cycle order; claiming a force permanently changes the fighter (Wood reach, Fire chip, Earth defense, Metal regeneration, Water speed); forces can be traded, never unclaimed | `CANON.md` §5 + §8; `game/js/modes.js` `FORCES`, `applyForces`, `STORY_STAGES` |
| Incarnation / transmigration (R_*) | Reincarnation: death in Story returns the soul in a new vessel scored from its actions (aggression, grapple, defense, trickery, surge); the old vessel is never re-offered; Diablo (intruder, not one of the nine) is gated behind 3+ deaths | `CANON.md` §1, §8; `game/js/modes.js` reincarnation block |
| Face assembly (eyes / noses / mouths; D_FACE, CHARA, PORT) | The returning soul assembles its new face in pieces; the face changes the fighter | `CANON.md` §1, §8 (The Two Laws of Death, The Threshold) |
| The marketplace merchant (D_MERCHA) | The Trader: buys and sells elemental forces; mimicry fighting style; Trader's Mimic mode; Scimitar as the Trader's vizier | `CANON.md` §5, §6, §8; `game/js/modes.js` Trader block + `traderFoe` |
| The assembled final encounter (E_LAST) | The Assembled Soul: composite of all nine styles including the player's; victory is absorption, not destruction | `CANON.md` §5, §8; `game/js/modes.js` `buildAssembledSoul` |
| Soul fragments (the nine) | The Nine-Soul Meter / Soul Surge: channel one of the other eight souls for ten seconds; in Story, the Surge Gauntlet runs nine fights under nine souls | `CANON.md` §4, §8; `game/js/modes.js` Soul Surge Gauntlet |
| Per-land Kings (F_KING, G_KING, W_KING, L_KING area groups) | Each land keeps a King — a resident power a soul must settle with to claim the land's force | `CANON.md` §8 (The Shape of the Head) — **new in this PR** |
| Inter-land tunnels (F_TONNEL, G_TONNEL, W_TONNEL, L_TONNEL area groups) | The tunnels: passages in the head's own flesh joining the lands; why the trial can be a ladder | `CANON.md` §8 (The Shape of the Head) — **new in this PR** |

## Area-level conversion table

Every named area group in the stage, incarnation, and prologue groups. File counts include
bitmaps, sounds, and text in that area group; the per-file checklist is
`teardown/eastern-mind/WIRING-INVENTORY.md` and per-area byte counts are in
`game/assets/stages/eastern-mind/stages.json`.

| Source area | Files | WH canon it became |
|---|---:|---|
| `stage-4-tree-of-life` area `L_FIELD` | 55 | Tree of Life — CANON §1/§5/§8; stage tree-of-life |
| `stage-4-tree-of-life` area `L_FOREST` | 160 | Tree of Life — CANON §1/§5/§8; stage tree-of-life |
| `stage-4-tree-of-life` area `L_INNER` | 41 | Tree of Life — CANON §1/§5/§8; stage tree-of-life |
| `stage-4-tree-of-life` area `L_KING` | 67 | Tree of Life — CANON §1/§5/§8; stage tree-of-life |
| `stage-4-tree-of-life` area `L_OGRE` | 43 | Tree of Life — CANON §1/§5/§8; stage tree-of-life |
| `stage-4-tree-of-life` area `L_TONNEL` | 42 | Tree of Life — CANON §1/§5/§8; stage tree-of-life |
| `stage-4-tree-of-life` area `L_WOOD` | 78 | Tree of Life — CANON §1/§5/§8; stage tree-of-life |
| `stage-4-tree-of-life` area `L_WTOR` | 19 | Tree of Life — CANON §1/§5/§8; stage tree-of-life |
| `stage-1-plains-of-chi-u` area `F_FIELD` | 151 | Plains of Chi-U — CANON §1/§5/§8; stage plains-of-chi-u |
| `stage-1-plains-of-chi-u` area `F_KING` | 148 | Plains of Chi-U — CANON §1/§5/§8; stage plains-of-chi-u |
| `stage-1-plains-of-chi-u` area `F_TONNEL` | 69 | Plains of Chi-U — CANON §1/§5/§8; stage plains-of-chi-u |
| `stage-1-plains-of-chi-u` area `F_TOWER1` | 36 | Plains of Chi-U — CANON §1/§5/§8; stage plains-of-chi-u |
| `stage-1-plains-of-chi-u` area `F_TOWER2` | 80 | Plains of Chi-U — CANON §1/§5/§8; stage plains-of-chi-u |
| `stage-1-plains-of-chi-u` area `F_TOWER3` | 34 | Plains of Chi-U — CANON §1/§5/§8; stage plains-of-chi-u |
| `stage-6-octagonal-shrine-par-fang` area `E_LAST` | 27 | Octagonal Shrine Par-fang — CANON §1/§5/§8; stages octagonal-shrine/shrine |
| `stage-6-octagonal-shrine-par-fang` area `E_MOUNT` | 35 | Octagonal Shrine Par-fang — CANON §1/§5/§8; stages octagonal-shrine/shrine |
| `stage-6-octagonal-shrine-par-fang` area `E_RM1` | 51 | Octagonal Shrine Par-fang — CANON §1/§5/§8; stages octagonal-shrine/shrine |
| `stage-6-octagonal-shrine-par-fang` area `E_RM2` | 58 | Octagonal Shrine Par-fang — CANON §1/§5/§8; stages octagonal-shrine/shrine |
| `stage-6-octagonal-shrine-par-fang` area `E_STAIRS` | 52 | Octagonal Shrine Par-fang — CANON §1/§5/§8; stages octagonal-shrine/shrine |
| `stage-2-helix-palace` area `G_BOULDE` | 52 | Helix Palace — CANON §1/§5/§6/§8; stage helix-palace |
| `stage-2-helix-palace` area `G_CASTLE` | 53 | Helix Palace — CANON §1/§5/§6/§8; stage helix-palace |
| `stage-2-helix-palace` area `G_CHIFA1` | 19 | Helix Palace — CANON §1/§5/§6/§8; stage helix-palace |
| `stage-2-helix-palace` area `G_CHIFA2` | 142 | Helix Palace — CANON §1/§5/§6/§8; stage helix-palace |
| `stage-2-helix-palace` area `G_ENTRAN` | 28 | Helix Palace — CANON §1/§5/§6/§8; stage helix-palace |
| `stage-2-helix-palace` area `G_FLOWER` | 54 | Helix Palace — CANON §1/§5/§6/§8; stage helix-palace |
| `stage-2-helix-palace` area `G_KING` | 109 | Helix Palace — CANON §1/§5/§6/§8; stage helix-palace |
| `stage-2-helix-palace` area `G_NONFAI` | 43 | Helix Palace — CANON §1/§5/§6/§8; stage helix-palace |
| `stage-2-helix-palace` area `G_PALACE` | 56 | Helix Palace — CANON §1/§5/§6/§8; stage helix-palace |
| `stage-2-helix-palace` area `G_PALM` | 12 | Helix Palace — CANON §1/§5/§6/§8; stage helix-palace |
| `stage-2-helix-palace` area `G_PURYAO` | 46 | Helix Palace — CANON §1/§5/§6/§8; stage helix-palace |
| `stage-2-helix-palace` area `G_RMBUD` | 33 | Helix Palace — CANON §1/§5/§6/§8; stage helix-palace |
| `stage-2-helix-palace` area `G_RMSHA` | 37 | Helix Palace — CANON §1/§5/§6/§8; stage helix-palace |
| `stage-2-helix-palace` area `G_ROOF` | 47 | Helix Palace — CANON §1/§5/§6/§8; stage helix-palace |
| `stage-2-helix-palace` area `G_SHOWMI` | 116 | Helix Palace — CANON §1/§5/§6/§8; stage helix-palace |
| `stage-2-helix-palace` area `G_SSAVER` | 317 | Helix Palace — CANON §1/§5/§6/§8; stage helix-palace |
| `stage-2-helix-palace` area `G_TONGSI` | 55 | Helix Palace — CANON §1/§5/§6/§8; stage helix-palace |
| `stage-2-helix-palace` area `G_TONNEL` | 63 | Helix Palace — CANON §1/§5/§6/§8; stage helix-palace |
| `stage-3-palace-of-dreaming` area `W_AUN` | 56 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_KING` | 121 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_LAKE1` | 34 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_LAKE2` | 26 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_PALAC1` | 64 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_PALAC2` | 19 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_RM1` | 24 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_RM2` | 37 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_RM3` | 11 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_RM4` | 6 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_RM5` | 6 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_RM6` | 6 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_RM7` | 6 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_RMAUN` | 18 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_RMDUMP` | 15 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_RMEYE` | 10 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_RMILL` | 18 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_RMKAI` | 26 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_RMMAGA` | 42 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_RMMAP` | 8 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_RMMIN` | 13 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_RMSHA` | 13 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_RMYUI` | 17 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-3-palace-of-dreaming` area `W_TONNEL` | 70 | Palace of Dreaming — CANON §1/§5/§8; stage palace-of-dreaming |
| `stage-5-phantom-marketplace` area `D_MARKET` | 19 | Phantom Marketplace — CANON §1/§5/§8; stage phantom-marketplace |
| `stage-5-phantom-marketplace` area `D_MERCHA` | 81 | Phantom Marketplace — CANON §1/§5/§8; stage phantom-marketplace |
| `incarnation-system` area `R_BYOU` | 25 | Incarnation System — CANON §1/§4/§8; modes.js reincarnation |
| `incarnation-system` area `R_GYOU` | 22 | Incarnation System — CANON §1/§4/§8; modes.js reincarnation |
| `incarnation-system` area `R_GYOU2` | 39 | Incarnation System — CANON §1/§4/§8; modes.js reincarnation |
| `incarnation-system` area `R_JIN` | 46 | Incarnation System — CANON §1/§4/§8; modes.js reincarnation |
| `incarnation-system` area `R_KAI` | 26 | Incarnation System — CANON §1/§4/§8; modes.js reincarnation |
| `incarnation-system` area `R_LETS` | 22 | Incarnation System — CANON §1/§4/§8; modes.js reincarnation |
| `incarnation-system` area `R_LETSA` | 15 | Incarnation System — CANON §1/§4/§8; modes.js reincarnation |
| `incarnation-system` area `R_LETSB` | 32 | Incarnation System — CANON §1/§4/§8; modes.js reincarnation |
| `incarnation-system` area `R_RTOG` | 138 | Incarnation System — CANON §1/§4/§8; modes.js reincarnation |
| `incarnation-system` area `R_SHA` | 26 | Incarnation System — CANON §1/§4/§8; modes.js reincarnation |
| `incarnation-system` area `R_SYSTEM` | 41 | Incarnation System — CANON §1/§4/§8; modes.js reincarnation |
| `incarnation-system` area `R_TOH` | 25 | Incarnation System — CANON §1/§4/§8; modes.js reincarnation |
| `incarnation-system` area `R_ZEN` | 21 | Incarnation System — CANON §1/§4/§8; modes.js reincarnation |
| `incarnation-system` area `R_ZEN2` | 34 | Incarnation System — CANON §1/§4/§8; modes.js reincarnation |
| `prologue-ending` area `CHARA` | 21 | The Threshold — CANON §8 (new) |
| `prologue-ending` area `DAMMY` | 2 | The Threshold — CANON §8 (new) |
| `prologue-ending` area `D_BOOK` | 88 | The Threshold — CANON §8 (new) |
| `prologue-ending` area `D_ENDING` | 10 | The Threshold — CANON §8 (new) |
| `prologue-ending` area `D_FACE` | 112 | The Threshold — CANON §8 (new) |
| `prologue-ending` area `D_LOGO` | 58 | The Threshold — CANON §8 (new) |
| `prologue-ending` area `D_MIRROR` | 40 | The Threshold — CANON §8 (new) |
| `prologue-ending` area `D_ROCK` | 39 | The Threshold — CANON §8 (new) |
| `prologue-ending` area `D_SEA` | 59 | The Threshold — CANON §8 (new) |
| `prologue-ending` area `D_SUMIE` | 48 | The Threshold — CANON §8 (new) |
| `prologue-ending` area `MAIN` | 26 | The Threshold — CANON §8 (new) |
| `prologue-ending` area `PORT` | 26 | The Threshold — CANON §8 (new) |
| `prologue-ending` area `PROF` | 17 | The Threshold — CANON §8 (new) |
| `prologue-ending` area `SHARED` | 111 | The Threshold — CANON §8 (new) |

## CANON.md additions in this PR

One append-only addition: `CANON.md` §8 "THE HEAD-WORLD, AS THE TRIAL FOUND IT", containing
The Shape of the Head (tunnels, per-land Kings), The Two Laws of Death (Versus vs Story
made explicit in canon prose; face assembly; Diablo's third-death gate), The Lands As
Places (all six stage groups as lived places), The Threshold (prologue-ending conversion),
The Incarnations (incarnation-system records), Colour Is Law (palettes), The Music of the
Head-World (soundtrack), and Soul Progression (forces, surge-as-memory, grief-as-progression).
No settled canon was rewritten, moved, or deleted. Mariposa was not touched (see Flags).

## Flags — unmapped, ambiguous, or not wired

1. **transcript-promo (1,128 files) — NOT WIRED, accounted-elsewhere (source archive).**
   AUTODEMO bitmaps (1,115) plus promo and Sato-works videos are promotional/transcript
   material, not world, system, or character material. No canon conversion was attempted;
   converting advertising material into game canon would invent canon. Retained and
   inventoried; decision to mine it for anything further is the owner's.
2. **Asset-level engine consumption — NOT WIRED for all 5,707 files.** No game code loads
   any file from `teardown/eastern-mind/` individually (verified by reading
   `game/js/assets.js`, `game/js/audio.js`, `game/js/main.js`, `game/js/stages.js`,
   `game/js/modes.js` on main). The six stage builders in `game/js/stages.js` are
   procedural and carry the lands' identities without sampling the extracted bitmaps;
   `game/js/audio.js` never references the soundtrack. Wiring the actual bitmaps as stage
   textures, the face bitmaps into the reincarnation screen, and the soundtrack into the
   audio system is the concrete follow-up — it touches `game/js/` engine code, which this
   lane was instructed not to rewrite. The registry added by this PR
   (`game/assets/stages/eastern-mind/stages.json`) is the map that follow-up consumes.
3. **Ambiguous area codes — converted at land level only, not interpreted individually:**
   `G_SSAVER` (317 files, the single largest area group — screensaver material by code),
   `G_CHIFA1`/`G_CHIFA2`, `G_NONFAI`, `G_PURYAO`, `G_SHOWMI`, `G_TONGSI`, `L_WTOR`,
   `W_AUN`/`W_RMAUN`, `W_RMMAGA`, `W_RMDUMP`, `W_RMILL`, `R_RTOG` (138 files),
   `R_LETS`/`R_LETSA`/`R_LETSB`, `R_TOH` (read as TOU by soul-name pattern only),
   `prologue-ending` `DAMMY` (2 files, dummy material by code), `MAIN`, `SHARED`, `PROF`.
   These are accounted inside their land/system conversions above; no individual canon
   meaning was invented for a code this lane could not verify.
4. **MARIPOSA — standing open question, not resolved by this lane.** The coordinator's
   brief states `CANON.md` carries two `### MARIPOSA` headers (Sealed Soul vs Butterfly
   Soul). On `main` at the commit above, this lane found exactly **one** MARIPOSA header
   (`### MARIPOSA — The Sealed Soul`, §7) and no Butterfly Soul header. Nothing in this PR
   touches Mariposa. Flagged for the coordinator/owner: either the duplicate was already
   resolved by another lane, or it lives on an unmerged branch.
5. **ZEN and GYOU remain unvesseled in canon** (`CANON.md` §4) while `game/js/modes.js`
   already carries `zen` and `gyou` vessel-affinity entries and story-ladder pools.
   Canon and code disagree about their availability; this lane did not reconcile them —
   that is an owner canon decision.
6. **Per-file WH names for Eastern Mind assets remain NEEDED** (per `RENAME-MAP.md`:
   stage directories were renamed with owner-assigned stage names; individual asset names
   were left pending owner assignment). This PR does not rename any teardown file.
7. **Teardown gaps carried from `TEARDOWN.md`:** ~7% of BITD chunks unmatched to
   dimension info (pixel data preserved in analysis logs, recoverable); Lingo scripts not
   decompiled; THUM thumbnails not extracted (redundant with full bitmaps). These are
   extraction gaps in the source teardown, recorded here so they are not mistaken for
   wiring gaps.

## Feel / structure gaps (acceptance bar)

Canon and `game/js/modes.js` agree on the systems; the *feel* gaps are about presence:

- **Reincarnation has no face.** The system (§8, modes.js) promises a new face assembled
  from three eyes, three noses, three mouths — and the face bitmaps for exactly that live
  in `prologue-ending/` (`D_FACE`, `CHARA`, `PORT`) and `incarnation-system/`. The current
  reincarnation screen offers new *vessels*, not new faces. Until the face layer ships,
  Story mode's central promise is readable but not visible.
- **The lands do not look like themselves yet.** Stage identity is carried by names,
  descriptions, and procedural builders. The extracted land bitmaps (the actual visual
  soul of each land) are not sampled by any stage, so a fight in the Palace of Dreaming
  does not yet *look* like the Palace of Dreaming's own art.
- **The head-world is silent.** Four soundtrack files carry the world's entire musical
  identity and none of them plays. A Tekken-feeling build needs the theme under the menu
  and the transmigration music over Story endings; both files exist and are registered.
- **Soul progression is invisible between fights.** Forces change stats in code, but no
  canon surface (shrine record, palette shift, surge after-effect) shows a soul its own
  career. §8's Colour Is Law gives the intended diegetic surface — claimed lands' colours
  settle — which no system implements yet.

## Per-character isolation

This lane made **no rig, skeleton, animation, or model edits** — the work is canon,
inventory, and registry data only. No character's files were modified, so no per-character
gating was required and no cross-character bleed is possible from this PR. No deliberate
parallels sharing was performed. The soul-vessel mapping in §8 follows the settled,
per-character assignments already in `CANON.md` §4 and `ROSTER.md` without alteration.
