# Character Creation Suite Sharing Mechanics — Research Report
**Researched 2026-10-22** (index sources; Fire Pro Workshop tag counts verified live)

## Summary

- **Fire Pro Wrestling World** has the strongest creation-sharing ecosystem: Steam Workshop with ~57k wrestler items (verified live), faceted tags, one-click subscribe, collections, auto-updating versions, and an informal remix culture ("feel free to reupload"). No slot limits. PC-only.
- **WWE 2K** has the most structured in-house hub ("Community Creations"): upload slots (80; 200 in 2K26), download caps (100), title/description/hashtags, ratings, Most Downloaded charts, web-based image uploader, moderation with strikes/bans. Cross-platform sharing exists but **2K25 split the pool by console generation** — a cautionary tale. Downloaded CAWs can be edited and re-uploaded, but there's no attribution chain.
- **Soulcalibur VI** has the weakest official pipeline: sharing exists but only as a *random* pull from a shared pool with **no search or direct download** — a famous anti-pattern.
- **Tekken 7/8** has deep per-part customization with **zero official sharing** (local saves only); PC modding is the de facto channel.
- **MK11/Injustice 2, Xenoverse 2, UFC**: no creation-to-creation sharing at all — customizations are either visible-but-not-transferable (MK11 online) or entirely local (UFC removed sharing after legal trouble with EA MMA).
- **No game does true two-way iterative collaboration** (A builds → B edits → sends back → A continues). The closest approximations: Fire Pro's Workshop auto-update + comment-requested tweaks, WWE 2K's download-edit-reupload, and Soulcalibur's random pool.

---

## 1. WWE 2K series (2K22/2K23/2K24/2K25) — Creation Suite & Community Creations

### What you can create
- **Create-A-Superstar:** body morphing (deepened in 2K26: "mix and match body parts"), face sculpting, face scans via the image uploader, hair (two-tone blending added in 2K26), attire parts, tattoos/body paint, colors/textures; per-attire customization. 2K26 doubled slots to **200 CAS slots / 2,000 image slots** (https://newsroom-uk.2k.com/news/players-creativity-takes-centre-stage-as-wwer-2k26-universe-and-community-creations-details-revealed-in-ringside-report-narrated-by-bayley — index).
- **Create-An-Arena** (LED barricades, aprons, announce tables, ring parts), **Create-A-Championship**, **Create-A-Show**, **Create-A-Moveset**, **Create-A-Video/Sign** (2K24 signs held by crowd NPCs), image/logo uploads.
- **Image uploader:** web flow at wwe.2k.com — link 2K account to platform account, upload 512×512 PNGs (face scans, logos), download in-game via Image Manager (Incoming/Local) (https://www.gamepur.com/guides/how-to-upload-custom-images-and-renders-in-wwe-2k23 — index).

### Sharing mechanics (the core loop)
- **Upload flow:** finishing a CAW auto-prompts "upload?"; or later via Online → Community Creations → Uploads → pick an empty slot → select creation → add title, description, hashtags. Requires 2K account + internet.
- **What's transferred:** a server-side creation record including the full parameter set plus embedded custom images (face scans/logos uploaded through the image pipeline).
- **Download/browser flow:** Online → Community Creations → Downloads → tabs for Superstar, Image, Arena, Championship, Shows, Moveset, MITB. Filters by name, creator, overall rating; sort by Most Downloaded / Most Upvoted. (https://frondtech.com/how-to-upload-a-wrestler-in-wwe-2k23/, https://www.gamepur.com/guides/how-to-download-and-upload-created-wrestlers-caws-in-wwe-2k23 — index)
- **Limits (2K23):** upload up to **80** superstars; download up to **100** wrestlers/attires. 2K26: 200 CAS slots, 2,000 images.
- **Ratings:** upvotes/star ratings, public download counts, Most Downloaded / Most Upvoted leaderboards.
- **Versioning:** none observed. Updating = delete and re-upload as a new item (downloaders keep the stale copy).
- **Remix:** downloaded superstars *can* be edited locally and re-uploaded (2K25 patch notes explicitly mention "the ability to remove custom renders when editing a downloaded superstar" — https://frontend.gist.ly/youtube-summarizer/wwe-2k25-patch-107-update-new-content-fixes-revealed — index). No attribution to the original creator; no fork graph.
- **Cross-platform:** 2K23 had cross-platform Community Creations. **2K25 removed cross-generation sharing**: PS4/Xbox One/PC share one pool; PS5/Xbox Series X|S share another; Switch 2 has its own isolated pool with **no image uploader and no cross-platform creations** (https://www.thesmackdownhotel.com/news/wwe2k25/wwe-2k25-cross-gen-and-cross-platform-community-creations-explained, https://gamingbolt.com/wwe-2k25-on-nintendo-switch-2-lacks-cross-platform-community-creations-image-uploader-support — index). Fragmenting the pool was widely criticized — keep one canonical format.
- **Moderation:** in-game flag/report system; 2K enforces ToS with strikes (24h → 2-week → permanent bans). In 2K24 the creator "WhatsTheStatus" (1.7M downloads) was permanently banned with no warning over intergender-modded uploads (https://hopzone.eu/forums/topic/20855- — index). The flagging system is leaky: explicit images reached Most Downloaded pages in 2K24 despite reports (https://www.gamespot.com/articles/wwe-2k24-feature-has-players-uploading-porn-to-the-game/1100-6521806/ — index).

### Collaboration
No true send-back-and-forth feature. Closest: download → edit locally → re-upload (unattributed); creator followings where fans request tweaks via social media and creators re-upload.

---

## 2. Tekken 7 / Tekken 8 — Customization (no official sharing)

### What you can customize
- Per-character: hairstyle, upper/lower body, shoes, glasses, accessories; per-part **color, size, and position** of accessories; multiple save slots per character selectable at character select (https://tk8.tekken-official.jp/en/mode/customize.php — index, official). Avatar customization (Fight Lounge), Player customization (titles, plates, gauges). Items unlocked with Fight Money or DLC packs.

### Sharing mechanics
- **None officially.** Customizations live in local save data; no upload, browser, or download feature exists. There is no A→B transfer path in either game.
- De facto channel: **PC mods** (NexusMods) — modders package outfits as .pak drop-ins. PC-only, unofficial, no curation, risk of malware (https://aaltoinmobiliaria.performlead.com/26019087/tekken-8-mods-unlocking-new-dimensions-of-gameplay/ — index).
- Opponents see your customization in online matches, but cannot acquire it.

### Collaboration
None. Lesson: a deep editor without an export/share path leaves the community to hack around it.

---

## 3. Soulcalibur VI — Character Creation (weakest official sharing)

### What you can create
- Choose **race** (human, lizardman, etc.) → body morphs → face → equipment (main-cast pieces + generic parts), stickers, colors; weapon = a main-cast fighter's "Soul" (including guest Geralt). ~**100 creation slots** (Gamescom 2018 via https://www.eventhubs.com/news/2018/aug/22/more-details-about-soul-calibur-6s-character-creator-and-roster-reportedly-emerge-gamescom-along-our-first-look-customized-designs/ — index). Created characters are usable in ranked and online matches.

### Sharing mechanics (the anti-pattern to avoid)
- **No search, no gallery, no direct download.** The shipped system: Creation → Original Character Creation → **Customize pulls one random character** from the shared pool; if you like it, save it locally (https://www.siliconera.com/soulcalibur-vi-creation-suite-works-best-when-you-try-to-stick-to-the-spirit-of-a-character/ — index).
- Pre-release Steam FAQ claimed friend-list-based downloads; the shipped game replaced that with the random pool (note the discrepancy; the random-pool behavior is confirmed by multiple post-release sources).
- Downloaded creations using DLC parts you don't own: usable, but **not editable**.
- Community sharing therefore moved off-platform: Reddit/Discord screenshot threads (https://thegunzone.com/how-to-look-at-other-created-characters-soul-caliber-6/ — index).

### Collaboration
None. This is the clearest example of "sharing" that fails: a pool with no search, attribution, or targeting kills iterative improvement.

---

## 4. Fire Pro Wrestling World — the gold standard of sharing ecosystems

### What you can create
- **Wrestler Edit:** appearance (hundreds of faces/costumes, pixel-art parts), size/weight/build, stats, full moveset assembled from 1,000+ moves, and **CPU logic/AI parameters** — you script how the wrestler behaves (taunts, dives, dirty tactics). Commonly 4 attires per wrestler. Reviewers note these are the same tools the developers used (https://www.merchandiseandmemories.com/the-grappling-gamer-fire-pro-1 — index).
- Custom rings, mat logos, aprons, referees, championship belts.
- **Move Craft DLC:** create/share custom moves. **Parts Craft DLC:** export part data, edit in external image software, share as custom edit parts — essentially a dev-tool pipeline; wrestlers using custom parts can't be used in online matches (https://store.steampowered.com/app/1120550/Fire_Pro_Wrestling_World__Parts_Craft/ — index).

### Sharing mechanics (verified live 2026-10-22 at https://steamcommunity.com/app/564230/workshop/)
- **Upload:** in-game Workshop uploader; item goes live with title, description, screenshots, tags.
- **Download:** one-click **Subscribe** (in-game or browser). Subscribed wrestlers auto-download into a "Retired" group; player organizes them via Team Edit (https://www.resetera.com/threads/fire-pro-wrestling-world-ot-fire-pro-wrestling-returns.429/index.php?pages/faq/ — index).
- **Scale (verified live):** "Pro Wrestler" tag 56,976 items; "Pro Wrestling Style" 56,786; "Move Craft" 48,926; Male 56,762 / Female 13,966; rich faceted tags (America/Japan/Mexico, Heavy/Junior, body-part tags like Face 15,472 / Layer 35,434, move-position tags).
- **No slot limits** — limited only by disk space (vs. WWE 2K's hard caps).
- **Search/discovery:** name search, sort by Most Subscribed, tag facets, follow top creators, third-party mirror firepro-w.com.
- **Versioning:** Steam Workshop auto-updates subscribers when a creator pushes a new version; creators document iterations in descriptions ("EDIT 2: I finished the moveset!") — e.g. the "Wrestlers Assemble!" collection (https://steamcommunity.com/sharedfiles/filedetails/?id=1093146476 — index).
- **Collections:** curated bundles (whole promotions, with rings) subscribed in one click — e.g. creators like Avenger3 split collections by WWE/AEW (Steam discussion "Who makes the best collections?", https://steamcommunity.com/app/564230/discussions/0/1638661595059984450/?l=greek — index).
- **Ratings:** favorites/star ratings, comments, subscriber counts.
- **Remix/fork:** informal but thriving — descriptions credit sources ("4 costumes (Credit to Dale for them)", "moves & logic taken from FPR", "**feel free to reupload it!**"). No formal fork graph or attribution tracking.
- **Platform restriction:** Workshop sharing is Steam/PC-only; no console workshop equivalent.

### Collaboration
No in-tool send-back-and-forth. Closest approximation: creator posts v1 → users comment requesting tweaks → creator updates the item (subscribers auto-receive it) → another user downloads, edits, re-uploads with credit. The **auto-update subscription** is the key mechanic: the "shared thing" is a live document, not a one-time file.

---

## 5. Others (brief)

- **Mortal Kombat 11:** gear is cosmetic-only; "augments" modify gameplay. Custom variations are *visible* online but there is **no trading or sharing** of gear/variations between players (interview with tech producer Trevor Traub — https://na.alienwarearena.com/ucf/show/1979230/boards/gaming-news/News/mortal-kombat-11-gear-is-purely-cosmetic-but-gameplay-can-be-altered-with-augments — index). **Injustice 2:** gear had stats (disabled in competitive), RNG Mother Boxes; also no player-to-player sharing.
- **Dragon Ball Xenoverse 2:** deep CaC (5 races, appearance, mentor moves, QQ Bangs, Super Souls) but **zero creation sharing** between players — others see your CaC in multiplayer but can't copy it (https://gamefaqs.gamespot.com/boards/437193-dragon-ball-xenoverse-2/80389234 — index).
- **EA UFC (UFC 4 and earlier):** created fighters **cannot be shared** — EA removed the feature after EA MMA's fighter sharing "got EA into a bit of trouble" (licensing/legal). A useful negative precedent: sharing real-person-likeness creations carries legal risk (https://www.game-over.com/content/2014/06/ea-sports-ufc/, https://worthplaying.com/article/2014/8/28/reviews/93352-ps4-review-ea-sports-ufc/ — index).

---

## STEAL THESE IDEAS — ranked for a web-based indie fighting game
*Target loop: AI builds a base → player hand-tweaks in browser → exports a patch file → AI applies it to the repo → repeat.*

1. **Deterministic creation formula as the shareable unit** (Fire Pro's implicit model, old CAW "formulas"). Store every fighter as a compact, human/AI-diffable JSON "recipe" (part IDs + colors + move IDs + logic params). The patch file *is* the creation — tiny, version-controllable, repo-friendly. This maps 1:1 onto your export-patch loop.
2. **Subscription with auto-update versioning** (Fire Pro/Steam Workshop). Creations are live documents: when the AI or a player pushes v2 of a fighter, subscribers get it automatically with a changelog. In your loop: the repo tracks formula versions; the browser shows "AI updated this fighter — review diff."
3. **Fork/remix chains with attribution** (formalize Fire Pro's "credit to Dale / feel free to reupload"). Every tweak creates a child revision linked to its parent; original creators get credit/notifications. Your loop already is a fork chain (AI base → player patch → AI applies) — make the chain visible and browsable.
4. **Faceted tag search** (Fire Pro's 56k-item workshop: style, weight class, gender, body-part, move-position tags). Give every creation structured tags so the AI can query the library ("find me a junior heavyweight striker with a top-rope finisher") and players can filter the gallery.
5. **Popularity signals as ranking + training data** (WWE 2K's Most Downloaded/Most Upvoted; Fire Pro's Most Subscribed). Use download/favorite counts to rank the gallery *and* as preference data for the AI when it generates bases.
6. **Collections = one-click roster bundles** (Fire Pro Workshop Collections). Let players/AI publish and subscribe to themed packs ("8-fighter tournament roster") as a single patch — perfect for the AI to generate a whole balanced roster in one shot.
7. **In-browser live preview before import** (WWE 2K's rendered thumbnails, taken further). A shareable URL that renders the fighter in 3D instantly — no install — so anyone can inspect before applying the patch. Your web-based setup makes this cheap.
8. **Draft moderation pipeline** (WWE 2K's flag/report + strike system; UFC/EA MMA's legal lesson). UGC needs: upload ToS, one-click flagging, review queue, and caution with real-person likenesses (the EA MMA precedent is exactly your legal risk if players recreate real wrestlers).
9. **Cross-platform single canonical pool** (the 2K25 anti-lesson). 2K25 split pools by console generation and the community hated it. Keep ONE platform-agnostic formula format so browser, repo, and any future client share everything.
10. **Editable-on-download by default** (WWE 2K lets you edit downloaded CAWs; Soulcalibur locks DLC-gated parts). Default to "download = you can tweak and re-share (as a fork)"; reserve locking only for genuinely proprietary parts. This is what turns a gallery into a collaboration graph.

## Could not verify
- Whether WWE 2K has any in-game "formula code" export (text codes) in recent titles — older titles' formula sharing happened on fan sites, not in-game; no in-game formula-code system found in 2K22–2K25 sources.
- Soulcalibur VI's exact pre-release vs post-release sharing behavior conflict: pre-release Steam FAQ said friend-based downloads; shipped game uses the random pool. The random pool is the confirmed shipped behavior.
- Whether Fire Pro Workshop items' "auto-update" pushes mid-session or on restart (Steam client behavior; not confirmed in sources).
- UFC 5's current sharing state (series precedent through UFC 4 is no sharing; UFC 5 not specifically checked).
- Tekken 8's Fight Lounge avatar data: whether avatars have any transfer path — no evidence of one found.

## Sources
- Live (verified 2026-10-22): https://steamcommunity.com/app/564230/workshop/ — Fire Pro Wrestling World Steam Workshop tag/item counts.
- Index (read 2026-10-22):
  - https://www.gamepur.com/guides/how-to-download-and-upload-created-wrestlers-caws-in-wwe-2k23
  - https://www.gamepur.com/guides/how-to-upload-custom-images-and-renders-in-wwe-2k23
  - https://frondtech.com/how-to-upload-a-wrestler-in-wwe-2k23/
  - https://www.thesmackdownhotel.com/news/wwe2k25/wwe-2k25-cross-gen-and-cross-platform-community-creations-explained
  - https://newsroom-uk.2k.com/news/players-creativity-takes-centre-stage-as-wwer-2k26-universe-and-community-creations-details-revealed-in-ringside-report-narrated-by-bayley
  - https://frontend.gist.ly/youtube-summarizer/wwe-2k25-patch-107-update-new-content-fixes-revealed
  - https://www.gamespot.com/articles/wwe-2k24-feature-has-players-uploading-porn-to-the-game/1100-6521806/
  - https://hopzone.eu/forums/topic/20855-%E2%80%98there-was-no-warning%E2%80%99-2k-faces-community-backlash-after-banning-leading-wwe-2k24-creator/
  - https://gamingbolt.com/wwe-2k25-on-nintendo-switch-2-lacks-cross-platform-community-creations-image-uploader-support
  - https://tk8.tekken-official.jp/en/mode/customize.php (official)
  - https://aaltoinmobiliaria.performlead.com/26019087/tekken-8-mods-unlocking-new-dimensions-of-gameplay/
  - https://www.siliconera.com/soulcalibur-vi-creation-suite-works-best-when-you-try-to-stick-to-the-spirit-of-a-character/
  - https://www.eventhubs.com/news/2018/aug/22/more-details-about-soul-calibur-6s-character-creator-and-roster-reportedly-emerge-gamescom-along-our-first-look-customized-designs/
  - https://thegunzone.com/how-to-look-at-other-created-characters-soul-caliber-6/
  - https://www.resetera.com/threads/fire-pro-wrestling-world-ot-fire-pro-wrestling-returns.429/index.php?pages/faq/
  - https://steamcommunity.com/sharedfiles/filedetails/?id=1093146476
  - https://steamcommunity.com/app/564230/discussions/0/1638661595059984450/?l=greek
  - https://store.steampowered.com/app/1120550/Fire_Pro_Wrestling_World__Parts_Craft/
  - https://www.merchandiseandmemories.com/the-grappling-gamer-fire-pro-1
  - https://na.alienwarearena.com/ucf/show/1979230/boards/gaming-news/News/mortal-kombat-11-gear-is-purely-cosmetic-but-gameplay-can-be-altered-with-augments
  - https://gamefaqs.gamespot.com/boards/437193-dragon-ball-xenoverse-2/80389234
  - https://www.game-over.com/content/2014/06/ea-sports-ufc/
  - https://worthplaying.com/article/2014/8/28/93352-ps4-review-ea-sports-ufc/
