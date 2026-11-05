# PIPELINE LAW — Western Heart (owner-ordered 2026-11-05)

This law forces Muse and every agent to finish the game piece-by-piece under
owner rules. It does not replace `AGENTS.md`; it adds the adoption / combat /
character / template / first-play rails for the OpenKumite + FightingEngine
pull-in and the WWE-style moveset-template layer.

Authorized by owner messages **t369u / t372u / t373u / t374u / t375u**
(MoneyManBusch / Marquis).

## 0. Non-negotiables (repeat from AGENTS.md)

- No guessing. No donor clip as "the real move". No procedural-as-real.
- Pantera = **exact King Tekken 7** (motbin 0x64, clipmap). Never switched /
  mixed / swapped animations. Never T3 King presented as T7 King.
- Prefer CloudAgent / automated landings; hand-tool only when necessary.
- Merge commits only; never force-push; never unexplained deletions.
- Do not touch Muse #1096 / `tools/auto_rig` unless Muse asks.
- Keep WH visual identity (WWE branding was stripped from rings/belts/announce
  table). We want the **template mechanic** and teardown animation/moveset
  data — **not** WWE logos on screen.

## 1. What we pull in (and what we do not)

### OpenKumite v0.1.2 (MIT) — https://github.com/openkumite/openkumite

Pull **engine systems and packaging ideas** only. Never vendor the Rust crate
tree, converted disc game data, or OK's APK contents into WH.

| OpenKumite area | WH adoption |
|---|---|
| `kumite_sim` 60 Hz | Keep `frame-step.js` / combat tick at 60 Hz. |
| Hit vs push separation | Keep `hitbox.js` capsules ≠ fighter push cylinders. F4 / `?hitboxes=1`. |
| `web/` PWA | `game/manifest.webmanifest` + `game/sw.js` (shell only). |
| `packaging/android` | Later recipe modeled on OK's no-Gradle NativeActivity — WH's own binary. |

### FightingEngine (「3D MUGEN」) — public combat rules only

Follow / cite: https://fightingengine.com/ · https://hanmincho.com/my-own-3d-fighting-game.html · Discord https://discord.com/invite/kMjN2rqyFu · Reddit https://www.reddit.com/r/Tekken/comments/1xnqt6d/this_guy_actually_built_a_3d_mugen_fightingengine/ · Tag Battle https://www.youtube.com/watch?v=Lko4SWLXVEU (@min2hound).

**EMBARGO (t371u / t373u):** FE GitHub + playable builds stay **private until
2026-12-25**. Do **not** hunt for a leaked repo. Public site rules + Tag Battle
video only.

Public rules WH may implement now: hit≠push · frame adv / high-mid-low /
reaction branches · air catch-height blend `visual = clip + (catch - clipStart) * 0.758`
→ `game/js/air-reaction-blend.js` · camera stay-readable at edges / occlusion
ideas (FE public devlog) → `fightCameraDolly` in `fight-camera-math.js`.

### Tag Battle demo characters — NEVER WH canon / roster

Hwoarang · Jin Kazama · Yugo the Wolf (Bloody Roar) · Siegfried Schtauffen
(Soulcalibur) are FE **importer demos only**. Never add to the WH roster.
Never treat as WH canon.

## 2. TEMPLATE LAYER (WWE-style copy-moveset) — t374u / t375u

Pattern: WWE Creator's "copy moveset" templates. Import **character data,
complete animation banks, and moveset datasets** from every teardown game
involved (Tekken 7 and other banks already in WH / GRE, WWE games the owner
has teardown for, Steam library sources and code the owner has access to —
see `docs/tech/STEAM-LIBRARY.md`). Then:

1. **Rename** each imported dataset to a **GENERIC TEMPLATE** id that *hints*
   who/what it is (never a franchise display name on the WH roster).
2. **Attach** that template to the owner's own Western Heart models / created
   characters.
3. **Log** the full template ↔ WH-character map in-repo:
   - this law (§2),
   - `docs/handoffs/OPENKUMITE-FIGHTINGENGINE-ADOPTION-2026-11-05.md`,
   - `docs/movesets/MOVESET-TEMPLATE-INVENTORY-2026-11-05.md`,
   - `game/data/moveset-templates/index.json`.

Example: **Pantera** remains Pantera, attached to template
`t7-grappler-jaguar-mask` (King-hinting T7 grappler, exact 0x64).

### Steam / GRE source rules (t375u)

- Owner's Steam-installed games + documented extraction guides in the
  reverse-engineering repo are valid sources for template data and engine
  behavior.
- Prefer existing GRE / WH teardown files. Do **not** re-download huge Steam
  depots in an adoption pass unless a specific small file is already documented
  as missing and required.
- Raw ripped WWE / Tekken / Steam assets stay in the **private**
  `mhvnsnt/game-reverse-engineering` repo. WH ships **WH-named template
  mappings + pointers** to teardown paths — not raw dumps in public paths.
- Never print secrets or Steam credentials.

### Roster naming rule

Do **NOT** put other-franchise display names (Hwoarang, Jin, Yugo, Siegfried,
WWE superstar names, etc.) on the WH roster. Template ids may *hint*
(e.g. `t7-grappler-jaguar-mask`, `wwe2k-powerhouse-brawler`) without being
roster labels.

## 3. Canon boundary

Western Heart is **not** a Tekken 3 clone and **not** a FightingEngine
scrapbook. Systems inspired by OK / FE / WWE-template UX land as WH-owned
code under WH names, wired into the Tekken menu/system structure
(INTEGRATION LAW).

## 4. Pantera = exact King T7

- Clipmap: `docs/proof/t7-clipmap-king-pantera.json` (467 mapped).
- Diagnosis: `docs/movesets/PANTERA-WIRING-DIAGNOSIS-2026-11-03.md`.
- Audit: `docs/movesets/PANTERA-KING-T7-AUDIT-2026-11-05.md`.
- Template: `t7-grappler-jaguar-mask` → `pantera`.
- Fix only with proven King T7 data — never a donor guess.

## 5. FIRST-PLAY / PLAYTEST FIXES (t374u) — priority with Pantera audit

First stuff the player experiences; clean landing for playtest:

| Bug | Approach | Status in adoption PR |
|---|---|---|
| Camera shoved back / blocked by walls at arena edges | Industry FG camera: cap dolly inside shell, widen FOV (FE public occlusion idea). `fightCameraDolly` + `fightCameraCenterX` in `fight-camera-math.js`, wired in `scene.js`. | landed |
| Wall/floor break debris floats (cracked textures) | Real physics: pieces fall, collide, settle via existing `DestructionSystem` + `_debris` gravity. Wall breach dressing chunks now join `_debris`. | landed (wall chunks); Voronoi shards already settled |
| Other first-play glitches | Prefer industry / modding-community / teardown code; no hand-tool unless necessary. Named leftovers in the handoff. | ongoing |

## 6. Piece-by-piece landing order (Muse-forcing)

1. Law + handoff + template inventory.
2. Air-reaction blend + tests + fighter hook.
3. Hit/push debug (F4).
4. Minimal PWA shell.
5. Camera edge clamp + tests.
6. Breakable debris physics for floating chunks.
7. Pantera audit; then one proven King-T7 fix at a time.
8. Attach more WH characters to templates as banks prove out.
9. After PWA proven: Android packaging plan (OK-style).
10. On **2026-12-25**: re-read FE OSS; only then deeper FE imports.

## 7. Claim / ownership

- Lane: #866 — MoneyManBusch prefix on comments and PR titles when claiming.
- Do not steal Muse's #1096 / auto_rig seat.

## 8. Proof required before claiming "done"

- Paths in the PR diff or already on main.
- Pantera moves: clipmap row / motbin id / probe JSON.
- Combat / camera math: `node --test` on the pure module.
- PWA: manifest + sw present; shell list excludes `/assets/` packs.
- Templates: inventory lists every attachment; no franchise roster names.
