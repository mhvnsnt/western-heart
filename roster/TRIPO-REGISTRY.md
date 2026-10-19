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

## Per-character Tripo attachments

Legend: ✅ attached · ❌ no Tripo on record · ⚠️ needs owner link/pull · 👁️ render exists · 🎨 needs generative-AI transform into proprietary Eastern Mind/Western Heart version

| Character | Tripo | Source | Local path | Slot order | Render | AI transform |
|---|---|---|---|---|---|---|
| PANTERA | ⚠️ **NOT ON RECORD** — no Pantera Tripo GLB found in repo; Slot 2 is currently "Leo man" per ATTIRE-SLOTS.md. If the owner has the Tripo link, pull it and it slots at Attire 2 per the exception. | — | — | A1 = in-game snow-leopard reskin (default), A2 = "Leo man", A3 = older classic; Tripo → A2 when pulled | A1 👁️ rendered (`docs/tpose-refs/pantera-t7king/`, `pantera-snow-leopard/`) | A1 done by owner direction |
| ZUI | ✅ YES (Attire 1) | Owner Drive file "ZUI (Drunken Monk).glb" (Tripo-generated, tripo_node, 20.7MB) | `roster/zui/attires/attire1/model.glb` | A1 = Drunken Monk Tripo (default) · A2 = rework v2 `attires/attire2/model.glb` · A3+ = other Steve attires (pending) | A1 render unverified — needs T-pose render | 🎨 yes |
| THOR | ✅ YES (main attire) | tripo3d.ai/3d-model/65ff7ad8-c423-46ff-8a46-4582a782c59f | `game/assets/models/thor.glb` | A1 = Tripo (default) · `thor_alt1.glb` later slot | 👁️ `game/assets/models/renders/thor.png` | 🎨 yes — also unrigged static per MODEL-STATUS.md (auto-rig before wiring) |
| AWA POP | ✅ YES (Attire 1) | tripo3d.ai/3d-model/e3d3b06f-0f00-4ca7-87db-872850dbb6a4 ("muscular superhero", owner confirmed = Awa Pop) — PR #215 | `roster/awa-pop/awa-pop-attire-1.glb` | A1 = Tripo (default) | ❌ no render — needs T-pose render | 🎨 yes |
| WATERFALL | ✅ YES (main attire) | Tripo Studio account pull (tripo-pull, 2026-10-16) | `game/assets/models/waterfall.glb` | A1 = Tripo (default) | 👁️ `game/assets/models/renders/waterfall.png` | 🎨 yes — unrigged static (auto-rig before wiring) |
| SAKU RA | ✅ YES (main attire) | Tripo Studio account pull (tripo-pull, 2026-10-16) | `game/assets/models/saku-ra-main.glb` (existing `saku-ra.glb` kept) | A1 = Tripo (default) · `saku-ra.glb` later slot | 👁️ `game/assets/models/renders/saku-ra-main.png` | 🎨 yes — unrigged static |
| PURPLE RAIN | ✅ YES (main attire) | Tripo Studio account pull (tripo-pull, 2026-10-16) | `game/assets/models/purple-rain-main.glb` (existing `purple-rain.glb` kept) | A1 = Tripo (default) · `purple-rain.glb` later slot | 👁️ `game/assets/models/renders/purple-rain-main.png` | 🎨 yes — unrigged static |
| KIKO TANAKA | ✅ YES (main + alt1) | Tripo Studio account pull (tripo-pull, 2026-10-16) | `game/assets/models/kiko-tanaka.glb` (A1 hooded/robed), `kiko-tanaka_alt1.glb` (A2 unrobed, shrouded face) | A1 = Tripo hooded (default) · A2 = Tripo unrobed | 👁️ `renders/kiko-tanaka.png`, `renders/kiko-tanaka_alt1.png` | 🎨 yes — unrigged statics |
| CAPE JONES / CYBORG X | ✅ YES (Attire 1) | Tripo Studio account pull (tripo-pull, 2026-10-16) | `game/assets/models/cape-jones.glb` | A1 = Cape Jones Tripo (default; = Cyborg X Attire 1 per canon) | 👁️ `renders/cape-jones.png` | 🎨 yes — unrigged static |
| KING TYRANT | ✅ YES (Attire 1) | tripo3d.ai/3d-model/22d9d916-71b1-4372-bdce-2d27acf0d18e ("wrestling figure 3d model", owner-sent 2026-10-19) | `roster/king-tyrant/attires/attire1/model.glb` | A1 = Tripo "White Tyrant" (default) · A2 = Red Trunks (reserved, owner target) · A3 = KING crown+ermine cape (reserved, owner target) · A4 = red velvet robe + leopard collar (reserved, owner target) · A5+ = in-game `king-tyrant.glb` / `king-tyrant_alt1.glb` | 👁️ `docs/tpose-refs/king-tyrant/p1_front.png` | 🎨 yes — unrigged static (auto-rig before playable wiring) |
| LILI | ❌ no Tripo on record | — | `game/assets/models/lili.glb` (base) | base GLB as-is | 👁️ `docs/tpose-refs/lili/` | — |
| ZAFINA | ❌ no Tripo on record | — | `game/assets/models/zafina.glb` (base) | base GLB as-is | 👁️ `docs/tpose-refs/zafina/` | — |
| BAEK | ❌ no Tripo on record | — | `game/assets/models/baek.glb` (base) | base GLB as-is | 👁️ `docs/tpose-refs/baek/` | — |
| DXMMII | ❌ no Tripo on record | — | `game/assets/models/dxmmii.glb` (base) | base GLB as-is | check `docs/tpose-refs/` | — |
| RAVE | ❌ no Tripo on record | — | `game/assets/models/rave.glb` (base) | base GLB as-is | per tpose sweep | — |
| Others (demonio, diablo, n3g4tiv0, nightwolf, phantom, skull, sam-ur-a1, kinpo, mariposa, doc-frank, jin, steve-fox→zui) | ❌ no Tripo on record | — | base GLBs in `game/assets/models/` | base GLBs as-is | see `docs/tpose-refs/` | — |

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
