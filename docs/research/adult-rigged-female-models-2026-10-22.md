# Adult Rigged Female 3D Base Models — Research Report
**Date:** 2026-10-22 · **Purpose:** Find licensable, fully-rigged, anatomically-detailed adult female base models a game dev can turn into proprietary characters for an M-rated 3D fighting game (Three.js pipeline; FBX/GLB preferred).

## Summary
- **Best legal + quality fit:** Daz 3D Genesis 9 Female pipeline (figure + Anatomical Elements + curvy character morphs such as Raw Bettsie), with per-product **Interactive Licenses** (~$50/item on the current Daz store). Full anatomy, full rig + facial morphs/visemes, FBX export via free Daz Studio. This matches the dev's existing "Scarlett/Madeline" quality bar.
- **Best non-Daz turnkey base:** CGTrader **"Nude Bikini Girl Ashley"** ($59.95) — Epic skeleton, 52 ARKit facial blendshapes, modular bikini + hair, FBX, standard royalty-free game license.
- **Best anatomy-first option:** itch.io **PRIMAL BONE "[UE5] Metahuman Nude Female"** ($44.99, "Commercial use allowed") — full genital mesh + morphs + physics; UE5-only project (FBX export required, physics won't transfer to Three.js); body is average-build, not curvy.
- **SmutBase (user's existing source): assessed separately below — not viable as a licensable source.** The catalog is overwhelmingly ports/rips of commercial games and Daz characters; nothing there carries a commercial-game license by default, the site now requires login (SSO) behind bot protection, and formats are Source-engine-centric (.mdl), a poor Three.js fit.

## Ranked shortlist

### 1. Daz 3D — Genesis 9 Female (+ Female Anatomical Elements)
- **URL:** https://www.daz3d.com/ (figure ships with free Daz Studio; anatomy via pro bundles / characters)
- **Price:** Figure itself effectively free with Daz Studio; **Interactive License $50.00 per product** (confirmed on current store pages, e.g. Raw Bettsie / Cheyenne 9 — "Optional License Add-Ons: Interactive License $50.00; no discounts apply to License Add-Ons"). Budget one $50 license **per item used** (figure, anatomical elements, each character morph, hair, clothing).
- **License:** Daz EULA + per-product Interactive License = may embed meshes in an **original** commercial game. Does NOT permit: reselling/redistributing raw Daz assets, or using them in mods of existing games.
- **Rig:** Full Genesis rig — body skeleton, articulated fingers/toes, facial bones + hundreds of expression/viseme morphs. Jiggle via dForce (Daz Studio only; bake or re-implement springs for Three.js).
- **Anatomy:** 5/5 — full genitalia/areola detail **only with the "Female Anatomical Elements" add-on** (included in most adult Named Character Pro Bundles; not all characters include genital textures).
- **Formats:** .DUF native; **FBX export via Daz Studio** (free). Hair/clothing are separate meshes (removable).
- **Caveat:** Facial morphs don't round-trip cleanly to Three.js blendshapes without extra work (bridges/scripts exist).
- **Verdict:** The legally soundest route and the dev's existing quality bar — buy the figure + anatomy + curvy morphs + per-item Interactive Licenses.

### 2. "Raw Bettsie for Genesis 9" (RawArt, Daz 3D store) — curvy Daz character
- **URL:** https://www.daz3d.com/raw-bettsie-for-genesis-9
- **Price:** $21.99 + Interactive License $50.00.
- **License:** Same Daz terms as #1.
- **Rig:** Genesis 9 rig (as #1).
- **Anatomy:** 5/5 — explicitly "beautiful curvy toon woman" and includes "One Full Skin Mat with Female Anatomical Elements."
- **Formats:** DUF; FBX via Daz Studio. Separate head/body morph dials (easy blending into original characters).
- **Verdict:** A concrete curvy, anatomically-complete Daz base with the interactive license available — purpose-built for the dev's "more base models" goal.

### 3. "Nude Bikini Girl Ashley" by Xandra (F2) — CGTrader
- **URL:** https://www.cgtrader.com/3d-models/character/woman/nude-bikini-girl-ashley-game-character
- **Price:** **$59.95** (rating 4.5/5 from 33 ratings). License: CGTrader standard royalty-free — commercial game use allowed; reselling/redistributing the raw 3D files is not.
- **Rig:** Rigged to **Epic Skeleton** (UE humanoid — retarget/animation-pack compatible), **52 ARKit blendshapes** (full facial), one hairstyle mesh, modular bikini parts, color/makeup customization. No dedicated jiggle bones (springs can be added).
- **Anatomy:** 4/5 — listed as "nude / naked / uncensored"; exact genital sculpt detail not verifiable from listing text (read 2026-10-22 via page fetch).
- **Formats:** UE 4.25–5 project, Blender 2.93+, **FBX**, textures zip. (Unity version listed as coming soon.)
- **Verdict:** Strongest non-Daz turnkey base: real skeleton, real facial rig, FBX, modular clothing/hair, game-friendly license.

### 4. "[UE5] Metahuman Nude Female – Genitals, Morphs & Physics Ready" by PRIMAL BONE — itch.io
- **URL:** https://primalbone.itch.io/metahuman-nude-female
- **Price:** **$44.99**. License: listing states **"Commercial use allowed."**
- **Rig:** MetaHuman skeleton; genital model as separate skeletal mesh with **physics asset**; morph targets (closed→open states); buttock/thigh secondary-motion physics.
- **Anatomy:** 5/5 — fully detailed female genitals + PBR textures.
- **Formats:** **UE5 project only — no native FBX/GLB download.** FBX export from UE5 is possible, but Chaos physics assets will NOT transfer to Three.js (jiggle must be re-implemented, e.g. spring bones).
- **Caveats:** Genitals are aligned to the **standard (average-build) MetaHuman body** — not the curvy/exaggerated proportions requested. (Epic's MetaHuman EULA as of UE 5.6 explicitly allows use outside Unreal Engine as "Non-Engine Products," so the engine concern is resolved; the format/physics concern is not.)
- **Verdict:** Best pure-anatomy asset with an explicit commercial-use grant; budget engineering time for UE5→FBX export and rebuilding soft-body physics for Three.js.

### 5. "Fantasy Girl Rigged" — CGTrader (adult-gated listing)
- **URL:** https://www.cgtrader.com/3d-models/character/fantasy-character/fantasy-girl-rigged
- **Price:** not captured (listing fetch 2026-10-22 returned description only).
- **License:** CGTrader standard royalty-free (game use OK; no raw redistribution).
- **Rig:** Excellent on paper — intuitive FK/IK arms & legs, upper/lower arm/leg twist, **3-level finger controls**, torso FK/IK + twist, **15 blendshapes**, breath control, full eye/eyelid controls, foot controls.
- **Anatomy:** level unverified (adult-gated; description references detailed body/inside-mouth maps but no explicit genital statement).
- **Formats:** Maya 2018/V-Ray native; **FBX = geometry only** — the advanced rig will NOT survive an FBX export to Three.js. Only viable if the dev re-rigs from the geometry.
- **Verdict:** Great sculpt + control rig for a Maya-based pipeline, but the FBX limitation makes it a weak Three.js base; verify price and anatomy before considering.

### 6. "Sexy Female character — animated and rigged UE4 compatible" — CGTrader
- **URL:** https://www.cgtrader.com/3d-models/character/woman/sexy-female-character-animated-and-rigged-ue4-compatible
- **Price:** **$14.99**. License: CGTrader standard royalty-free.
- **Rig:** UE4-compatible rigged + animated (index data only; bone/facial detail unverified).
- **Anatomy:** unverified — listing title implies nudity ("Sexy Female"), no explicit anatomical-detail statement found.
- **Formats:** FBX (CGTrader-verified file).
- **Verdict:** Cheap UE4-skeleton option, but anatomy and facial-rig claims need verification against the live listing before purchase.

### 7. "Naked Girl1 Animations Pack" — CGTrader
- **URL:** https://www.cgtrader.com/3d-models/character/woman/naked-girl1-animations-pack
- **Price:** **$15.00** (rating 3.6/5 from 68 ratings). License: CGTrader standard royalty-free.
- **Rig:** Rigged + animation pack, low-poly, VR/AR-tagged (index data only; facial/jiggle detail unverified).
- **Anatomy:** unverified beyond "Naked" in the title.
- **Formats:** FBX (CGTrader-verified file).
- **Verdict:** Budget animated base; verify anatomy detail and rig completeness on the live page before committing.

### 8. "Male and Female base Human Characters — lowpoly — optional nsfw" — CGTrader
- **URL:** https://www.cgtrader.com/3d-models/character/other/game-ready-optimized-realistic-modern-humans-optional-nsfw
- **Price:** **$3.99**. License: CGTrader standard royalty-free.
- **Rig:** Body + face rig "with as few bones as possible" (twist/knee bones included), manual vertex skinning. No jiggle bones.
- **Anatomy:** Optional NSFW "private parts" included (keep underwear on to hide). Realistic idealized proportions — **not curvy/exaggerated**.
- **Formats:** (formats list not captured; CGTrader 3D-model page).
- **Verdict:** Cheapest legitimate game-ready base with an NSFW option, but it misses the curvy brief and the minimal bone count limits fighting-game animation quality. Backup option only.

## Borderline / do-not-use

### A. "Adventure Character Sarah (Pack 2)" by David Grette — ArtStation ($89) — BORDERLINE (anatomy-limited)
- **URL:** https://www.artstation.com/marketplace/p/m7Yv8/adventure-character-sarah-from-pack-2-game-ready-3d-character-for-unreal-unity
- Superb tech: Epic-skeleton-compatible, **52 calibrated facial blendshapes** (Live Link Face), corrective muscle blendshapes, adjustable chest/hip sizing, modular clothing/hair, hair/cloth/body physics, FBX (full + optimized), UE5 + Unity projects ("uncensored"). **But:** "The characters have a full body **and underwear**" — no explicit genitalia modeled. Anatomy 2/5. Fails the full-anatomy requirement, though the body itself is a strong base mesh.

### B. "Queen Marika The Eternal" by RyanReos — RenderHub ($18.60) — DO NOT USE for this goal
- **URL:** https://www.renderhub.com/ryanreos/queen-marika-the-eternal-game-ready (read live 2026-10-22)
- Technically superb: Auto Rig Pro + MustardUI rig, modular FBX (Full Nude / Half Nude / Full Clothes), "Full vagina and nipples modeled," 190k tris, 2K/4K PBR.
- **Disqualified:** License is **"Extended Use License (IP Restricted)" with an Editorial-Use-Only restriction** — it is Elden Ring fan art (FromSoftware IP). It cannot be turned into a proprietary commercial game character. Included as the canonical example of why provenance matters.

## SmutBase assessment (per follow-up request)
- **What/where:** SmutBase is the NSFW sister site of SFMLab/Open3DLab (same admin/Patreon), hosting free adult SFM/GMod-style models. The old domain **smutbase.net is dead** (connection timeout, confirmed 2026-10-22); traffic data shows the live domain is now **smutba.se**. The live site sits behind **Anubis bot protection** and now **requires SSO login** (archived homepage redirects to `/sso-client/?next=%2F`) — it could not be browsed without an account, which is out of bounds for this research.
- **Catalog composition:** Overwhelmingly **ports/rips** — models extracted from commercial games (Overwatch, Dead or Alive, etc.), Daz 3D characters, and other artists' work, uploaded by "porters" for SFM/GMod fan-animation use. Model pages carry "ported by X" credit chains; per-model licenses are typically personal/fan-use only. A minority are original characters (OCs), but even those are shared without commercial-game grants as a rule.
- **The user's "Scarlett" and "Madeline":** consistent with unauthorized SFM ports of Daz-style characters (cf. the Daz 3D product "HH Scarlett for G9" by Herschel Hoffmeyer — a SmutBase "Scarlett" is most plausibly a port of a Daz or game character, not an original). Exact provenance couldn't be verified behind the login wall.
- **Legal reality:**
  - *Ripped game/Daz assets:* cannot be turned into proprietary commercial game characters — game EULAs forbid asset extraction, and Daz's EULA forbids redistribution. Commercial use = copyright infringement exposure.
  - *Original characters by SmutBase authors:* usable **only** if the author explicitly grants commercial-game rights, which is rare on SmutBase; each model would require direct per-author clearance. Default assumption: **not licensed** for commercial game use.
- **Pipeline fit:** Formats are Source-engine-centric (**.mdl**); some uploads include .blend sources, but FBX/GLB is not standard — poor fit for a Three.js pipeline.
- **Ranking:** No SmutBase model is recommended for the commercial goal. Ranked below every licensable option above; treat SmutBase as reference-only (posing/animation reference), not as a source of shippable base meshes.

## Licensing reality check
**Which license types actually allow turning a purchased model into a proprietary game character:**
| License | Modify into proprietary character? | Ship in commercial game? | Gotchas |
|---|---|---|---|
| CGTrader / ArtStation / RenderHub **standard royalty-free** | ✅ Yes (intended use) | ✅ Yes | ❌ May NOT resell/redistribute the raw 3D files or a competing 3D asset; seller must warrant the work is original (rips do appear — check) |
| **Daz 3D + Interactive License** (per product, ~$50) | ✅ Yes, in original games | ✅ Yes | Every mesh/texture needs its own license (figure + anatomical elements + morphs + hair + clothing adds up); ❌ no use in mods of existing games; ❌ no raw redistribution; facial morphs need extra work to reach Three.js |
| Sketchfab **CC-BY** (free downloads) | ✅ Yes | ✅ Yes | Attribution required (credit the author in the game credits) |
| Sketchfab **CC0** | ✅ Yes | ✅ Yes | None — cleanest free option, but rare for quality adult rigged models |
| Sketchfab **CC-BY-NC** | ❌ No commercial use | ❌ | Free for hobby only |
| Sketchfab **CC-BY-ND** | ❌ No derivatives | — | Useless as a base mesh |
| Sketchfab **Store purchase** | ✅ Yes | ✅ Yes | Royalty-free; no standalone redistribution (same as CGTrader) |
| itch.io per-product terms (e.g. PRIMAL BONE "Commercial use allowed") | ✅ Yes | ✅ Yes | Read the page; engine-specific formats/physics may not transfer |
| **SmutBase / ripped game assets** | ❌ | ❌ | No license chain; infringement exposure regardless of how much you modify the mesh |

**Key gotchas:**
1. "Royalty-free" ≠ "do anything" — it almost always excludes reselling the raw model or stockpiling it into a competing 3D product. Embedding a *modified* character in *your* game is the permitted core use.
2. Daz's Interactive License is **per content item**, not per character or per game — a single fighter built from figure + anatomy + morph + hair + outfit can need 5+ licenses (~$250 at current $50 pricing, more for PA products).
3. "Uncensored" on a listing (e.g., David Grette packs) often means nipples/underwear-level, not full genital anatomy — verify before buying.
4. Physics/jiggle almost never transfers: UE Chaos physics, Daz dForce, and Maya setups stay in their host apps; budget spring-bone re-implementation in Three.js.
5. FBX "geometry only" exports (e.g., CGTrader "Fantasy Girl") lose advanced rigs — confirm the *rigged* format, not just the mesh format.

## Could not verify
- Exact genital-sculpt detail on Ashley (#3), Fantasy Girl (#5), Sexy Female character (#6), Naked Girl1 (#7) — listing text doesn't specify; needs preview-image inspection or purchase.
- "Fantasy Girl Rigged" price (listing fetch returned description only).
- SmutBase model pages / per-model terms (SSO login wall + Anubis bot protection; no sign-in permitted).
- Current Genesis 9 base-figure Interactive License price (character pages show $50; base-figure pricing historically higher).
- Whether Ashley's proportions meet the "exaggerated curvy" bar (stylized "pretty/cute" marketing; preview images needed).

## Sources
- Daz 3D forums — Interactive License explained (index, read 2026-10-22): https://www.daz3d.com/forums/discussion/320496/question-about-license-and-commercial-usage / https://www.daz3d.com/forums/discussion/208551/interactive-license
- Daz store — Raw Bettsie for Genesis 9 ($21.99 + Interactive License $50.00): https://www.daz3d.com/raw-bettsie-for-genesis-9
- Daz store — Cheyenne 9 ($49.99 + Interactive License $50.00): https://www.daz3d.com/cheyenne-9
- CGTrader — Nude Bikini Girl Ashley ($59.95, 4.5★/33): https://www.cgtrader.com/3d-models/character/woman/nude-bikini-girl-ashley-game-character (page fetched 2026-10-22)
- CGTrader — Fantasy Girl Rigged: https://www.cgtrader.com/3d-models/character/fantasy-character/fantasy-girl-rigged
- CGTrader — Sexy Female character UE4 ($14.99): https://www.cgtrader.com/3d-models/character/woman/sexy-female-character-animated-and-rigged-ue4-compatible
- CGTrader — Naked Girl1 Animations Pack ($15.00): https://www.cgtrader.com/3d-models/character/woman/naked-girl1-animations-pack
- CGTrader — Modern Humans optional NSFW ($3.99): https://www.cgtrader.com/3d-models/character/other/game-ready-optimized-realistic-modern-humans-optional-nsfw
- CGTrader license/terms (index, read 2026-10-22): https://www.cgtrader.com/pages/terms-and-conditions
- itch.io — PRIMAL BONE [UE5] Metahuman Nude Female ($44.99, "Commercial use allowed"): https://primalbone.itch.io/metahuman-nude-female (+ comments page on genital/clothing handling)
- ArtStation — David Grette Adventure Character Sarah ($89.00): https://www.artstation.com/marketplace/p/m7Yv8/adventure-character-sarah-from-pack-2-game-ready-3d-character-for-unreal-unity (page fetched 2026-10-22)
- RenderHub — Queen Marika The Eternal, RyanReos ($18.60, IP-Restricted Editorial license): https://www.renderhub.com/ryanreos/queen-marika-the-eternal-game-ready (page read live 2026-10-22)
- Epic MetaHuman license — UE 5.6+ allows non-UE use (index, read 2026-10-22): https://www.metahuman.com/license, https://www.cgchannel.com/2025/06/you-can-now-sell-metahumans-or-use-them-in-unity-or-godot/
- Sketchfab licensing (index, read 2026-10-22): https://sketchfab.com/blogs/community/an-introduction-to-creative-commons-licenses/, https://www.licenseorg.com/guide/3d-assets/sketchfab
- SmutBase: smutbase.net unreachable (ERR_TIMED_OUT, research browser, 2026-10-22); smutba.se live domain per traffic data (Semrush), behind Anubis bot-check + SSO login; SFMLab/SmutBase admin Patreon: https://www.patreon.com/sfmlab/about
