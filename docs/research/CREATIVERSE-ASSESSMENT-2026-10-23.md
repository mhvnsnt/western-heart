# Creativerse — Assessment for Western Heart

**Date:** 2026-10-23
**Status:** PUBLIC-SOURCE RESEARCH ONLY. **No Steam file pull was performed and none was possible** — Creativerse is a proprietary, copyrighted game (see §6) with no publicly available open assets, SDK, or modding support. No game files were downloaded, no file contents were inspected, and no claims below are based on any file pull. Every substantive claim is cited to a public URL.

**Owner instruction (verbatim):** *"Creativerse: whatever it can add idk what it is"*

---

## Section 0: What Creativerse IS (context — you said you don't know)

**[RESEARCHED]** Creativerse is a **voxel sandbox game** (Minecraft-like: everything is built from 3D cubes/blocks) developed by **Playful Corp**, on Steam at **app ID 280790**. It launched in Early Access, fully released on **May 8, 2017**, and after ~8 years of development shipped as **"Creativerse: The Definitive Edition"** on November 15, 2022 — which changed it from free-to-play to **pay-once-play-forever ($24.99)**.
- Official store description: https://store.steampowered.com/app/280790?l=dutch&curator_clanid=27037355 ("best-rated sandbox adventure/building games on Steam")
- F2P → Definitive Edition pivot explained by the devs: https://store.steampowered.com/news/app/280790/view/3648508800838071143
- MMOHuts reporting the pivot, $24.99 B2P launch: https://mmohuts.com/news/creativerse-leaving-f2p-buy-play-model/

**Correction to the task brief:** the brief said "free-to-play," but it is **no longer F2P** — it has been buy-to-play since November 2022.

The pitch: an enormous reactive voxel world with adventure/RPG-lite systems (mining, crafting, hunting, cooking, farming, quest badges), plus "next-gen sandbox building" — blueprints, wired machines, fully rotatable and paintable blocks, and a Creator Mode with infinite items. The official FAQ lists the pillars: beautiful sandbox, next-level tools, "built for sharing": https://creativersegame.com/faq.html

---

## 1. The building system

**[RESEARCHED]**
- **Blocks, not meshes:** everything is voxel-based. The game has **400+ unique blocks and items** (official FAQ), going far beyond plain cubes — slopes, slabs, stair blocks, corner blocks, columns, doors, windows, tables, chairs, ladders, plus furniture/decor items. Source: https://creativerse.fandom.com/wiki/Features
- **Rotation + painting:** every block is **fully rotatable and paintable** — a February 2020 update (R65) lets players color nearly every block/object/liquid with up to two colors. Source: https://creativerse.fandom.com/wiki/Mods
- **Wired machines (their "redstone"):** a 2017 "Machines" update added **switches, wiring, electricity, logic gates, sensors, math blocks, and wireless circuitry** so players can engineer animated/interactive builds. Source: https://www.gameskinny.com/opinion/creativerse-goes-proand-they-are-killing-it-with-the-new-features/
- **Arc Signs:** in-world billboard blocks that display words, game icons, and even **custom images via "rich text"** — used by players to make flat paintings, posters, patterns, and NPC images on walls. Source: https://creativerse.fandom.com/wiki/Mods
- **Land claims:** areas can be claimed to protect builds, doors can be locked with number codes. Source: https://creativerse.fandom.com/wiki/Features
- **No mods allowed** (during the F2P era at least — the wiki states mods are not permitted since optional store sales had to earn the devs' income). Source: https://creativerse.fandom.com/wiki/Features
- **[AWAITS FILE PULL]:** nothing. There are no public voxel-building SDK/teardown files from Creativerse to pull. Its building code and block asset libraries are proprietary and were never released. General voxel techniques (greedy meshing, chunking) are documented in open literature — e.g. 0fps articles and Mikola Lysenko's meshing writeups — if the crew ever needs voxel tech, but it would come from open sources, not from this game.

---

## 2. Blueprints + Steam Workshop (the community sharing pipeline)

**[RESEARCHED]** This is the most complete finding and the most transferable piece.
- **Blueprints** are the core UGC unit: players build a structure, then craft a **Capture Block / capture stone** (in several sizes) to "photograph" the build into a portable blueprint with **step-by-step building instructions** and a 3D preview. Source: https://creativerse.fandom.com/wiki/Blueprint
- **Publishing is in-game:** a Blueprint can be published **directly to the Steam Workshop** (`steamcommunity.com/app/280790/workshop/`) from inside the game — pick tags, title, description, screenshots, video links; visibility options (private / friends / public). Sources: https://creativerse.fandom.com/wiki/Blueprint and https://creativerse.fandom.com/wiki/Capture_Blocks
- **Scale:** the wiki reports **over 27,000 player-created workshop objects** already published. Source: https://creativerse.fandom.com/wiki/Mods
- **Consumption model:** other players **subscribe** to download blueprints for free; the blueprint does NOT build itself — the player must still gather/craft the materials ("burst fill" speeds placement), with optional paid "building kits." Source: https://creativerse.fandom.com/wiki/Features
- The **"Blueprint Revolution" update** (the one that opened the tools to players) explicitly pitched it as: *"Steam Workshop support for player blueprints… craft capture stones to capture small, medium, and large blueprints… publish blueprints directly to the Steam workshop from within the game."* Source: https://store.steampowered.com/news/posts/?feed=steam_community_announcements&appids=280790&enddate=1501786047
- **[AWAITS FILE PULL]:** nothing — the blueprint format is proprietary; the pipeline *design* (capture → tag → publish → subscribe → preview) is the pullable lesson, not code.

---

## 3. "Adventures" — shareable player-made mini-games

**[RESEARCHED]** A separate, higher-level UGC system: **Adventures** are shareable instances of player worlds where players author **mini-games/quests** — custom checkpoints, dialogues, creature spawning, block manipulation (disappearing/reappearing walls, rollercoasters, labyrinths, timed devices, number puzzles), then publish them for others to play. The wiki FAQ calls it a *"publishable adventure system"* that puts player creations *"at the fingertips of millions of players."* Source: https://creativerse.fandom.com/wiki/FAQ and https://creativerse.fandom.com/wiki/Mods
- **[AWAITS FILE PULL]:** nothing pullable; design pattern only.

---

## 4. The F2P content pipeline — a cautionary data point

**[RESEARCHED]** Creativerse's monetization is worth noting precisely because it **failed as F2P**:
- F2P-era revenue came from store-exclusive blocks/objects/skins, costumes (purely cosmetic — defense came from craftable armor), coins, and DLC. Source: https://creativerse.fandom.com/wiki/Features
- In the devs' own pivot letter: *"Despite this, outside of one exception Creativerse has never been profitable. Its year over year costs always exceeded what it brought in… That one exception? It was during the first 15 months of early access, when the game was not yet free to play."* They concluded: *"Creativerse's business model just worked better as a pay-once game."* Source: https://mmohuts.com/news/creativerse-leaving-f2p-buy-play-model/
- The Definitive Edition removed Playful-hosted servers entirely — players host their own worlds — and added 300+ new blocks/items. Source: https://store.steampowered.com/news/app/280790/view/3648508800838071143
- **[AWAITS FILE PULL]:** nothing; this is business-model research, not game assets.

---

## 5. Honest value assessment for Western Heart

Be straight: **Creativerse is a block-building sandbox; WH is a Tekken-style fighting game. There is almost no direct asset or technique transfer.** What follows is the honest ledger:

### What's actually useful (the real finds)

1. **The Blueprint → Workshop pipeline is the best public reference design for WH's creation-suite community features.** The owner wants a WWE 2K-style creation suite with **community creations** sharing. Creativerse's loop is a clean model to study and adapt: **capture** (select a creation in-game) → **tag + title + describe** → **publish from inside the game** (no external upload tool) → **3D preview + screenshots/video** → **subscribe to download** → **ratings/tags for discovery**. Creativerse proved it at scale: 27,000+ community objects. WH's "share my custom fighter/attire/moveset" flow can borrow the UX shape directly.
2. **Adventures = the design pattern for shareable "Just Fun" modes.** The owner authorized "Just Fun" side games drawn from Japanese/world mythologies (festival games, spirit trials, yokai pastimes — concepts need user approval). Creativerse's Adventures system — player-authored quests/mini-games with checkpoints, dialogues, and triggers, published for others to play — is the reference architecture if WH ever wants **shareable custom scenarios** in those modes.
3. **Wired machines / logic gates = inspiration for interactive arena elements.** Timed devices, triggered lights/doors, disappearing floor parts — that's the vocabulary for arena interactivity (a stage whose lighting rigs fire on a KO, destructible/animated set pieces beyond the Geo-Mod destruction pulls). Low priority, but real.
4. **The F2P cautionary tale:** if WH ever considers selling creation-suite content, Creativerse's own post-mortem says F2P-with-cosmetics couldn't sustain a UGC sandbox and they pivoted to buy-once. Given the owner's "maximize FREE resources" stance, the takeaway is: community sharing works as a **retention** feature, not a monetization one.

### What's NOT useful — stated plainly

- **Voxel building techniques for arenas: no.** The arena directive is explicit — kill the "blocky minecraft roblox 3js prototype" look, upgrade quality toward real video-game visuals. Voxel aesthetics are literally the thing the owner is trying to escape. Nothing in Creativerse's rendering/voxel pipeline serves the T7 teardown-based arena upgrade path.
- **Combat/animation/character tech: none.** It's a first-person voxel builder; it has no fighting-game animation, skeleton, or input tech of any relevance to the Tekken-style moveset work.
- **No file pull exists to do.** Creativerse never released an SDK, asset pack, or modding tools (mods were explicitly disallowed). The user never asked for a pull and didn't claim ownership — and under the game-ownership rule, a pull requires the user's authorization for that game, which was not given. Everything usable here is **design knowledge from public docs**, which is already fully captured above.

**Bottom line:** Creativerse adds one thing to WH — **the UGC sharing pipeline playbook** (blueprint capture → in-game Workshop publishing → adventure sharing). Everything else is "not our genre." File under `docs/research/` as a design reference for the creation suite's community features, not as an asset source.
