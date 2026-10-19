# TRIPO 3D MODEL ATTACHMENT REGISTRY

Canonical living registry — owner law 2026-10-18. This file exists so nobody
ever reports a character as model-less when it already has a Tripo 3D model
attached. UPDATE IT every time a Tripo model is pulled and attached.

## The law (owner 2026-10-18, verbatim intent)

- Tripo 3D models are the **MAIN / DEFAULT attires** — proprietary to his universe.
- Fixed teardown / foreign-skeleton / older in-game models become **alternate
  attires (slots 2/3/4+)** behind the Tripo default.
- **EXCEPTION — PANTERA:** his in-game reskinned model is Attire 1 (default)
  because he did the reskin first; his Tripo model is Attire 2.
- When a Tripo model is attached, record it HERE immediately: source link,
  local path, slot order, render status, AI-transform flag.

## Resolved names (canon — do not invent new ones)

| Owner said | Canon resolution | Source |
|---|---|---|
| Steve Fox became ___ | **ZUI** (Steve Fox base) | CANON.md "ZUI — The Drunken Soul" |
| "Steve Fox became Zooey" | **NOT FOUND** — "Zooey" appears 0 times in ROSTER.md, CANON.md, kitbash files. OPEN QUESTION: new name or misremember? Flagged, not invented. | — |
| Nina became ___ | **AWA POP** (Nina Williams base, owner-locked) | CANON.md "AWA POP — The Bubble Soul" |
| Nina's sister | **TORCH** (Anna Williams base) | CANON.md "TORCH — The Flame Soul" |
| Kiko Tanaka became ___ | **RAVE** (in Western Heart; "Kiko in others") — "Kiko is rave in this game and Kiko in others, Rave is his Raver personality from our canon" | Owner 2026-10-19 |

## Per-character Tripo attachments

Legend: ✅ attached · ❌ no Tripo on record · ⚠️ needs owner link/pull · 👁️ render exists · 🎨 needs generative-AI transform into proprietary Eastern Mind/Western Heart version

| Character | Tripo | Source | Local path | Slot order | Render | AI transform |
|---|---|---|---|---|---|---|
| PANTERA | ✅ YES — **"Leo man" IS the Tripo model** (owner-confirmed 2026-10-19: "Leo man is the tripo model for that attire slot 2, the one we had in game for so long and the original tripo model and the one we put in the pictures"). No Tripo link on file — recorded as owner-confirmed. | owner-confirmed (no link on file); Leopard King: https://studio.tripo3d.ai/3d-model/094c2f37-1c61-43fb-82ff-7124100a1021 | `roster/pantera/attires/leomon/` (Slot 2 = Leo man Tripo); `roster/pantera/attires/leopard-king/model.glb` (Slot 6 = Leopard King Tripo, "tiger humanoid" by jaywillf69, 23.3MB, static — needs auto-rig) | A1 = in-game T7King reskin (default), A2 = "Leo man" Tripo, A3 = snow leopard, A4 = T7 P2, A5 = Crimson Rage, A6 = Leopard King Tripo | A1/A3/A4/A5 👁️ rendered (`docs/tpose-refs/pantera-t7king/`, `pantera-snow-leopard/`, `pantera-attire4-p2/`, `pantera-crimson-rage/`); A6 👁️ `docs/tpose-refs/pantera-leopard-king/` | A1 done by owner direction; A6 pending auto-rig (PANTERA RIG RULE stands) |
| ZUI | ✅ YES (Attire 1) | Owner Drive file "ZUI (Drunken Monk).glb" (Tripo-generated, tripo_node, 20.7MB) | `roster/zui/attires/attire1/model.glb` | A1 = Drunken Monk Tripo (default) · A2 = rework v2 `attires/attire2/model.glb` · A3+ = other Steve attires (pending) | A1 render unverified — needs T-pose render | 🎨 yes |
| THOR | ✅ YES (main attire) | tripo3d.ai/3d-model/65ff7ad8-c423-46ff-8a46-4582a782c59f | `game/assets/models/thor.glb` | A1 = Tripo (default) · A2 = Tripo "phantom mimic attire oni mask" (c85dc47b-a3b4-41ad-b39c-86ea81b418cd, `roster/thor/attires/attire2/model.glb`) · `thor_alt1.glb` later slot | 👁️ `game/assets/models/renders/thor.png` · `docs/tpose-refs/thor/a2_front.png` | 🎨 yes — also unrigged static per MODEL-STATUS.md (auto-rig before wiring) |
| AWA POP | ✅ YES (Attire 1 + 2) | tripo3d.ai/3d-model/e3d3b06f-0f00-4ca7-87db-872850dbb6a4 ("muscular superhero", owner confirmed = Awa Pop) — PR #215 · A2: tripo3d.ai/3d-model/d71f4210-acff-4009-ba53-3813ea488a91 ("muscular female figure", owner-confirmed = Awa Pop Attire 2) | `roster/awa-pop/awa-pop-attire-1.glb` · `roster/awa-pop/attires/attire2/model.glb` | A1 = Tripo (default) · A2 = Tripo "muscular female figure" | 👁️ `docs/tpose-refs/awa-pop/a2_front.png` (A1 render still pending) | 🎨 yes |
| WATERFALL | ✅ YES (main attire) | Tripo Studio account pull (tripo-pull, 2026-10-16) | `game/assets/models/waterfall.glb` | A1 = Tripo (default) | 👁️ `game/assets/models/renders/waterfall.png` | 🎨 yes — unrigged static (auto-rig before wiring) |
| SAKU RA | ✅ YES (main attire) | Tripo Studio account pull (tripo-pull, 2026-10-16) | `game/assets/models/saku-ra-main.glb` (existing `saku-ra.glb` kept) | A1 = Tripo (default) · `saku-ra.glb` later slot | 👁️ `game/assets/models/renders/saku-ra-main.png` | 🎨 yes — unrigged static |
| PURPLE RAIN | ✅ YES (main attire) | Tripo Studio account pull (tripo-pull, 2026-10-16) | `game/assets/models/purple-rain-main.glb` (existing `purple-rain.glb` kept) | A1 = Tripo (default) · `purple-rain.glb` later slot | 👁️ `game/assets/models/renders/purple-rain-main.png` | 🎨 yes — unrigged static |
| RAVE (= KIKO TANAKA in Western Heart — owner 2026-10-19) | ✅ YES (main + alt1) | Tripo Studio account pull (tripo-pull, 2026-10-16) | `game/assets/models/kiko-tanaka.glb` (A1 hooded/robed), `kiko-tanaka_alt1.glb` (A2 unrobed, shrouded face — "ghost Tanaka" = Raver personality) | A1 = Tripo hooded (default) · A2 = Tripo unrobed ("ghost Tanaka" — Raver personality) · A3+ = `game/assets/models/rave.glb` (Lei Wulong in-game base) ladders back | 👁️ `renders/kiko-tanaka.png`, `renders/kiko-tanaka_alt1.png` | 🎨 yes — unrigged statics |
| CAPE JONES / CYBORG X | ✅ YES (Attire 1) | Tripo Studio account pull (tripo-pull, 2026-10-16) | `game/assets/models/cape-jones.glb` | A1 = Cape Jones Tripo (default; = Cyborg X Attire 1 per canon) | 👁️ `renders/cape-jones.png` | 🎨 yes — unrigged static |
| SKULL | ✅ YES (Attire 1) | tripo3d.ai/3d-model/d77eb53a-5369-4055-9ee6-b4a46eaf7789 ("human figure 3d model" — skull face paint, skeleton ribcage body paint, digital-camo cargo pants; the Bryan Fury proprietary replacement) | `roster/skull/attires/attire1/model.glb` | A1 = Tripo (default) · A2/A3 reserved customs · A4+ = Bryan Fury in-game attires (`game/assets/models/skull.glb` base) ladder back | 👁️ `docs/tpose-refs/skull/p1_front.png` | 🎨 yes — unrigged static (auto-rig before live-game swap) |
| LILI | ❌ retired name — see **SILVERTONGUE** row (owner 2026-10-18: "never use the old name") | — | `game/assets/models/lili.glb` (base) | base GLB as-is | 👁️ `docs/tpose-refs/lili/` | — |
| ZAFINA | ❌ no Tripo on record | — | `game/assets/models/zafina.glb` (base) | base GLB as-is | 👁️ `docs/tpose-refs/zafina/` | — |
| BAEK / KEVIN | ✅ YES (Attire 1) | tripo3d.ai/3d-model/86d12371-a3f6-4f45-8b8b-4abdd47b881e ("human figure 3d model" by marquiswhitacre — Kevin from the God Molecule show, "just a guy, inside Mars' head") | `roster/baek/attires/attire1/model.glb` | A1 = Kevin Tripo (default, replaces boring Baek model) · A2 = original Baek `game/assets/models/baek.glb` · A3 = "Master's White" reskin (PR #265) | render pending | 🎨 yes — unrigged static (auto-rig before live-game swap) |
| KING TYRANT | ✅ YES (Attires 1–4) | tripo3d.ai/3d-model/22d9d916-71b1-4372-bdce-2d27acf0d18e (A1 "White Tyrant") · 85fb8756-33d1-466a-a0ef-2d4c8f1b65ff (A2 "Tyrant King", crown + ermine cape) · fed0d1d3-ba55-40c4-a0b7-fc78cb4560aa (A3 "Black Snow", red velvet robe, leopard collar) · 3dcb748f-8e96-49dd-a975-3ebf78f414f9 (A4 "Fight Gear", short spiky hair) — all owner's Tripo builds, pulled via tools/tripo-pull/ 2026-10-19 | `roster/king-tyrant/attires/attire1/model.glb` (A1) · `attire2/model.glb` (A2) · `attire3/model.glb` (A3) · `attire4/model.glb` (A4) | A1 = White Tyrant Tripo (default) · A2 = Tyrant King Tripo · A3 = Black Snow Tripo · A4 = Fight Gear Tripo · A5+ = in-game `king-tyrant.glb`, `king-tyrant_alt1.glb` ladder back | 👁️ `docs/tpose-refs/king-tyrant/p1_front.png`, `a2_front.png`, `a3_front.png`, `a4_front.png` (front renders own-eyes verified) | 🎨 yes — unrigged statics (auto-rig before live-game swap; A2 cape + A3 robe are cloth-rig follow-ups) |
| STAR | ✅ YES (Attires 1–3) | tripo3d.ai/3d-model/ea73eeb3-c755-4e9d-b58a-8749add387f4 ("red latex cosplay 3d model" by fluidmovementmusicgroup — Star, the Christie Monteiro equivalent; owner confirmed = her Attire 1, 2026-10-18) | `roster/star/attires/attire1/model.glb` (A1 Red Latex, as-pulled) · `attire2/model.glb` (A2 "After Dark" black-latex colorway — NOT rated-M) · `attire3/model.glb` (A3 "Capoeira Gold" Brazil-green colorway) | A1 = Tripo Red Latex (default) · A2 = After Dark (black-latex colorway) · A3 = Capoeira Gold (colorway) · A4 = in-game `game/assets/models/star.glb` "Classic" (untextured clay — texture pass queued, never a gate) · A5+ reserved for true rated-M versions/models (mature content — separate in-flight lane) per `roster/star/attires/_VARIANT-PIPELINE.md` | 👁️ `docs/tpose-refs/star/p1_front.png` (+ a2/a3/a4 previews own-eyes verified) | 🎨 yes — unrigged statics (auto-rig before live-game swap) |
| SILVERTONGUE | ✅ YES (Attire 1) | tripo3d.ai/3d-model/2e20f9eb-5591-4f73-8d11-980f993c91d6 ("metallic bodysuit 3d model" by eqqq57218, pulled 2026-10-18) | `roster/silvertongue/attires/attire1/model.glb` (23.87MB, 1 mesh/1 primitive/1 material/3 textures, static — needs auto-rig) | A1 = Tripo Metallic Bodysuit (default) · A2 = Spy Debut `roster/silvertongue/attires/spy-debut/` · A3 = Rated-M Nude `roster/silvertongue/attires/attire2/model.glb` (dir name unchanged) · A4 = Noir Gala `roster/lili/attires/noir-gala/` | 👁️ `docs/tpose-refs/silvertongue/p1_front.png` (T-pose front, own-eyes verified 2026-10-19) | 🎨 yes — unrigged static (auto-rig before live-game swap) |
| DXMMII | ❌ no Tripo on record | — | `game/assets/models/dxmmii.glb` (base) | base GLB as-is | check `docs/tpose-refs/` | — |
| PHANTOM | ✅ YES (Attire 1) | tripo3d.ai/3d-model/3ed032a4-8a4d-4111-b852-373ebf0a06aa ("fantasy armored warrior 3d model" by marz6kdabest) | `roster/phantom/attires/attire1/model.glb` (21.96MB, 1,053,849 verts) | A1 = Tripo (default) · existing base GLB (`game/assets/models/phantom.glb`) ladders back | 👁️ `docs/tpose-refs/phantom/p1_front.png` (1024px Cycles, own-eyes verified 2026-10-18) | 🎨 yes — unrigged static (1 mesh/1 primitive/1 material/0 skins, auto-rig before wiring) |
| NIGHTWOLF | ✅ YES (Attire 1) | tripo3d.ai/3d-model/5b0835eb-6c87-4257-899e-0771698d02c6 ("tribal warrior 3d model" by marz6kdabest; tribute to Serena Misae Brown) | `roster/nightwolf/attires/attire1/model.glb` (21.87MB, 1,015,766 verts) | A1 = Tripo (default) · existing base GLB (`game/assets/models/nightwolf.glb`) ladders back | 👁️ `docs/tpose-refs/nightwolf/p1_front.png` (1024px Cycles, own-eyes verified 2026-10-18) | 🎨 yes — unrigged static (1 mesh/1 primitive/1 material/0 skins, auto-rig before wiring) |
| Others (demonio, diablo, n3g4tiv0, sam-ur-a1, kinpo, mariposa, doc-frank, jin, steve-fox→zui) | ❌ no Tripo on record | — | base GLBs in `game/assets/models/` | base GLBs as-is | see `docs/tpose-refs/` | — |

## How to attach a new Tripo model (checklist)

1. Pull via `tools/tripo-pull/` (Forge3D) from the owner's share link — verify valid GLB.
2. Land it at `game/assets/models/<name>.glb` (or `roster/<name>/attires/attire1/model.glb` for slot-structured characters). Never overwrite an existing model — use `-main` suffix if needed.
3. It becomes **Attire 1 (default)** — older in-game models shift to later slots (Pantera exception: Tripo → Attire 2).
4. Add a T-pose render to `docs/tpose-refs/<name>/` (locked orientation method).
5. **Record it in this file** — source link, path, slot order, render status, AI-transform flag.
6. Flag 🎨 — the render goes to the owner for generative-AI transform into the proprietary Eastern Mind/Western Heart version.

## History

- 2026-10-16: tripo-pull recovered waterfall, saku-ra-main, purple-rain-main, kiko-tanaka(+alt1), cape-jones, thor (TRIPO-ATTIRES.md).
- 2026-10-16: Awa Pop Tripo pulled (PR #215, `roster/awa-pop/awa-pop-attire-1.glb`).
- 2026-10-15/16: Zui attires wired (PR #170): A1 Drunken Monk Tripo, A2 rework v2.
- 2026-10-18: registry created per owner order — Tripo = default attire law; Pantera exception; "Zooey" flagged as unresolved; Pantera Tripo marked NOT ON RECORD (needs owner link).
- 2026-10-19: CORRECTION — owner confirmed "Leo man" IS Pantera's original Tripo model (Slot 2); the "NOT ON RECORD" note was wrong. Added Leopard King (Tripo 094c2f37) as Slot 6.
- 2026-10-19: Skull Tripo attached (Attire 1, the Bryan Fury proprietary replacement) — Bryan Fury in-game attires ladder to A4+ per owner slot order.
- 2026-10-19: **KIKO TANAKA = RAVE merged** (owner: "Kiko is rave in this game and Kiko in others, Rave is his Raver personality from our canon" / "the ghost tanaka is Rave"). The unrobed variant is Rave. Rows merged into one RAVE row; the robe pair (`kiko-tanaka.glb`, `kiko-tanaka_alt1.glb`) are RAVE's models; `rave.glb` (Lei Wulong base) ladders back to A3+.
- 2026-10-19: Star Tripo attached (Attires 1–3: Red Latex default, After Dark (black-latex colorway — NOT rated-M, owner correction 2026-10-19), Capoeira Gold colorway; A4 = in-game Classic) — owner: "That's her attire 1 and we will make more and some rated M versions and models of her and some variants and color ways."
