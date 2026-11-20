# Western Heart — Character Select Redesign (Lane I, Round 2)

Owner order 2026-10-18: kill the embarrassing select screen (vertical-scroll card
grid repeating the same 2-3 renders with no names) and rebuild it Tekken 8-style.
This doc is written BEFORE any code, per the owner correction, and cites exactly
which game each design element comes from (T8 vs TTT2 vs T6 vs owner spec).

## 1. Sources

### Tekken 8 (T8)
- CNT select screen: organized **horizontally** — 8 characters top row, 8 bottom
  row; character icons **small relative to everything else**, "room for a good
  amount of expansion" (eventhubs.com, 2023-07-21,
  https://www.eventhubs.com/news/2023/jul/21/tekken-8-character-select-screen/).
- Fighters **"perform little personal acts"** while waiting: "Xiaoyu lightly
  brushes her bangs with her fingers as she waits to be picked, while Lili
  stands still, holding her cat and petting it" (same article).
- Customization: each fighter has **ten slots**; "Customized content can be
  saved to multiple slots for each individual character. **Select your favourite
  slot in the Character Select** and take on the battle."
  (tk8.tekken-official.jp/en/mode/customize.php).
- Menus are **3D real-time**: "what you see is exactly what you get in the
  match. No weird lighting shifts between the menu and the stage" (diffsense.com
  customization guide). → Our select runs the same GLBs as the fight.
- Final-game select chrome (P1/P2 cursors, big animated model of the highlighted
  fighter, stats block, bottom hints bar, "?" random slot): per the owner's
  screenshots + coordinator brief. Could not be verified by text fetch; the
  stats trio (Fighting Style / Nationality / Height-Weight) is verified from the
  classic series: "Fighting Style: Mishima style Karate, Height/Weight: 181cm/76kg"
  (Tekken 1 PSX manual, regvault.org) and "Fighting style: Capoeira, Nationality:
  Brazilian" (T6 character reveal, worthplaying.com, 2009-03-13).

### Tekken Tag Tournament 2 (TTT2)
- Each player picks a **team of two fighters**; can also play solo; Unlimited
  adds 2v2 / 1v2 / 1v1 ratio select (gamesdb.launchbox-app.com; rocketchainsaw.com.au).
- Unrevealed characters sit behind **"?" boxes** on the select screen
  (TTT PS2 manual, archive.org: "Until then they are hidden behind question
  marks on the Character Select Screen").
- WH is 1v1, so TTT2 contributes the **two-cursor flow** (P1 cursor + P2 cursor
  over the icon field) and the "?" convention — not the pair layout.

### Tekken 6 (T6)
- Random **"?" slots at both ends of the portrait row**, plus extra "?" boxes
  for upcoming characters (neogaf.com Tekken 6 thread, 2009).
- Attire select, classic rule: "press a **punch** button to get one outfit or
  press a **kick** button to get the other" (Tekken 1 PSX manual, regvault.org);
  T6: "Some special costumes are already there, just **press left punch** button
  when selecting character" (answers.com).

### Owner spec (2026-10-18, verbatim in spirit)
- Top ~75–80% = the FIGHTERS' ZONE, **bisected**: P1's full 3D render BIG on the
  left, P2's BIG on the right; renders live in the BACKGROUND of the zone.
- Bottom ~20% = a **contained strip** of small character cards (faces, portraits,
  character art).
- Hundreds of characters coming: the **ONLY** thing allowed to scroll vertically
  is the card strip, and it scrolls **within its own box** — never flooding or
  stretching the whole screen.
- Tap/hover a card → that fighter's full 3D render appears on YOUR side.
- Name + fighting style + stats show for the selected fighters.
- **Attire switching ON the select screen**, Tekken-style.
- Mobile-first: tap to select.
- Owner correction (same day): the big zone is **LIVE ANIMATED 3D MODELS (our
  GLBs)** doing select-screen idles — "A still image in the big zone = hand-tooled
  slop, he WILL reject it." Attire flips on the big P1/P2 model LIVE. Classic
  Tekken = punch selects outfit 1, kick selects outfit 2; Tekken 8 = per-character
  slots chosen right on the select screen.

## 2. Layout (owner spec is the boss)

```
┌──────────────────────────────────────────────────────┐
│ FIGHTERS ZONE (~78%)                                 │
│  ┌───────────────┐  ┌───────────────┐                 │
│  │ P1 3D (live)  │  │ P2 3D (live)  │  renders as the │
│  │ big, left     │  │ big, right    │  background     │
│  │ name/style/   │  │ name/style/   │                 │
│  │ stats + attire│  │ stats + attire│                 │
│  └───────────────┘  └───────────────┘                 │
│  hints bar (Confirm · Back · Attire · Random)        │
├──────────────────────────────────────────────────────┤
│ CARD STRIP (~20%, own internal scroll, contained)    │
│  [card][card][card][card]...[?]                      │
└──────────────────────────────────────────────────────┘
```

- The page itself NEVER scrolls (`overflow: hidden` on the screen). The card
  strip has a fixed height (~20–22% of viewport) and `overflow-y: auto` —
  contained, per spec.
- P1 side is interactive (this device). P2 side mirrors for versus preview;
  P2 defaults to a CPU pick (random non-P1 fighter, like the old `P2 = ROSTER[(i+6)%len]`).
- Mobile 390×844: zone stacks the same bisected halves side-by-side (they're
  narrow but T8 does the same); cards stay thumb-sized; tap targets ≥ 44px.

## 3. Big zone — live 3D, never a still image

- One three.js canvas behind the zone (two viewports, P1 left / P2 right), using
  `game/vendor/three.module.js` + GLTFLoader + meshopt decoder (same stack as
  `game/js/assets.js` — "same GLBs + lighting as the fight", owner correction §4).
- **Every fighter shows a real 3D model, live.** Model map (honest status):
  - Playable-gate GLBs (Mixamo rig, embedded clips where present): PANTERA
    (`pantera.glb` + attire slots below), ZUI (`steve-fox.glb`), DEMONIO
    (`demonio.glb`, has Idle/Run/TPose/Walk clips), CYBORG X (`cyborg-x.glb`,
    41 MB textured build, PR #230).
  - Other loadable GLBs (valid glTF, wrong/mini scale or foreign skeleton —
    fine for a menu, they only need to LOOK right): diablo, phantom, skull,
    saku-ra, sam-ur-a1, kinpo, king-tyrant, nightwolf, purple-rain, waterfall,
    awa-pop (×40 scale fix — 2.5 cm miniatures), thor, cape-jones, mariposa
    (Tripo statics ~1 m), doc-frank, mariposa (T7 base), phantom-t8, kinpo-t8 (foreign
    skeletons). See MODEL-STATUS.md for the audit.
  - Fighters with NO GLB in the repo (BURGER, SCIMITAR, MICHIKO, STAR, TORCH,
    DIO, BRUNO): the fighter's card art (`docs/qa/roster-cards/card_<id>.png`)
    on a 3D card plane that floats/rotates gently in the 3D scene with real
    lighting, labeled MODEL PENDING. It is still live WebGL — never a DOM `<img>`.
- **Idle animation policy ("little personal acts", T8):** play the GLB's own
  idle clip when it has one (demonio Idle; pantera pose clips); otherwise a
  neutral breathing loop (subtle scale/rotation sway on the root). TRUE
  per-fighter personality mocap (Xiaoyu's bang-brush, Lili's cat) does NOT exist
  in our assets — the per-fighter idle *types* below are approximated from canon
  souls and stated as such in the PR; no claim of real mocap idles.
  - PANTERA (prowling showman): slow prowl sway. ZUI (drunken soul): loose
    drunken weave. DEMONIO (demon soul): menacing breath, ember pulse.
    SAKU RA (idol): bouncy idol sway. CYBORG X (trapped soul): mechanical
    twitch. Others: neutral breathing until their clips land.
- Attire switcher sits under each big model: slot chips (1/2/3…).
  PANTERA: 1 = P1 Original (t7king reskin, `docs/tpose-refs/pantera-t7king/`),
  2 = Leo man (`roster/pantera/attires/leomon/`), 3 = Snow Leopard
  (`roster/pantera/attires/snow-leopard/`) — per ATTIRE-SLOTS.md (owner
  2026-10-17). CYBORG X: 1 = cape-jones.glb (canon main attire). Later slots =
  Tekken-based attires per the slot-ordering law. Swapping reloads the GLB in
  the same viewport — the model flips LIVE, T8-style.
- Keyboard parity with classic Tekken: on a highlighted card, **Punch key =
  confirm with attire slot 1, Kick key = confirm with attire slot 2**
  (T1 PSX manual rule). Touch/mouse: tap card = preview on your side; tap the
  big model or CONFIRM = lock in.

## 4. Card strip (the ONLY scroll)

- Small cards using `docs/qa/roster-cards/card_<fighter>.png` — 21 real cards, one
  per fighter (no repeats, no shared renders). Every card carries a DISTINCT
  NAME LABEL — the no-names embarrassment dies here (owner spec, first fix).
  NOTE (build finding): `card_pantera.png` and `card_zui.png` are 0 bytes on
  origin/main — those two cards fall back to the real bust portraits
  (`portraits/pantera_bust.png`, `portraits/zui_a1wip_bust.png`).
- "?" random card at the end (T6 convention) + locked "?" cards for fighters
  with no model yet (TTT2 "?"-box convention, labeled MODEL PENDING).
- Tap = preview on P1 side; tap again (or CONFIRM) = lock. Hover (desktop) =
  preview. P2 cursor: tap a card with the P2 toggle active, or long-press to
  assign to P2 (mobile-first: a small P1/P2 side toggle above the strip).
- The strip scrolls internally (`overflow-y: auto`, fixed height); page never
  scrolls. Hundreds of cards later: same box, virtualized if needed.

## 5. Stats panel (T8/T6 convention, our canon)

Under each big model: NAME (kanji accent) · SOUL (canon) · FIGHTING STYLE =
Tekken base body (e.g. "King", "Steve") · ORIGIN = "parts unknown" (canon rule).
Height/weight show only where the model audit measured them (MODEL-STATUS.md);
never invented.

## 6. Hints bar (T8 bottom-hints convention)

Bottom of the fighters zone: `TAP: preview · CONFIRM: fight · ATTIRE: 1/2/3 ·
?: random · ESC: back`. Desktop adds `PUNCH: attire 1 · KICK: attire 2`.

## 7. Files

- `game/ui-wh/cards.html` — select screen shell (kept standalone-playable).
- `game/ui-wh/cards.js` — select logic (3D zone, strip, attire, postMessage).
- `game/ui-wh/cards.css` — select styles (75–80/20 split, contained strip).
- `game/ui-wh/index.html` — MINIMAL HOOK: the `#select` section becomes a
  mount point for the rebuilt screen (old grid removed — see §8).
- `game/ui-wh/ui.js` — MINIMAL HOOK: old `renderSelect()` grid deleted;
  select screen delegates to cards.js; `startVs()` / postMessage protocol
  (`{type:'fight',p1,p2}`, `{type:'fighters'…}`) UNCHANGED so
  `game/js/ui-wh-bridge.js` keeps working untouched.
- Old roster-cards promo page (`cards.html#<id>`, `#strip`) is RETIRED — its
  content (repeated renders, no names) is exactly what the owner flagged.
  (Said explicitly per anti-clobber rule 4; details in the PR.)

## 8. What dies (anti-clobber rule 4 — said explicitly)

1. The old `#select` vertical-scroll card grid in `game/ui-wh/index.html`
   (`.sel-side` × 2 + `#sel-grid`) and its renderer `renderSelect()` in
   `game/ui-wh/ui.js` plus the `.select` grid styles in `game/ui-wh/ui.css`.
   Reason: owner-flagged embarrassment — repeated 2–3 renders, no names,
   page-level vertical scroll.
2. The `cards.html#<id>` single-card and `cards.html#strip` promo-strip modes
   in `cards.js` (same file becomes the select screen). Reason: same repeated-
   render problem; superseded by the contained card strip with distinct labels.

## 9. Honest rebuild statement (for the PR)

No real Tekken menu/UI files exist in our teardowns (see UI-ASSET-INVENTORY.md)
— the select screen is REBUILT to match Tekken 8's layout and behavior per the
owner's spec, using OUR assets: our GLBs, our card art, Oswald (bundled font),
the owner's menu-wallpaper art. Nothing here is ripped Tekken UI; the layout
lineage (T8 bisected 3D zone, T8 hints bar, T6 "?" random, TTT2 two-cursor flow)
is documented in §1.

## 10. Playtest gate

Local http.server + headless Chromium (Playwright skill) at 390×844 and
1280×800. Screenshots: initial, P1 select, P2 select, attire switch, scrolled
card strip (containment proof). Every screenshot viewed with own eyes before
merge. Merge only when green + mergeable + no-deletion-guard clean.

## 11. Build findings (added during implementation)

- **CSS collision:** `game/ui-wh/ui.css` has a mode-select `.cards
  { position: absolute; ... }` rule that leaked onto the strip's
  `.whsel-strip .cards` grid (my CSS never set `position`), lifting the grid
  out of the strip and defeating the contained scroll. Fixed with an explicit
  `position: static` guard in cards.css. Class-name audit: `.k` (same kanji
  intent) and `.nm` (higher-specificity local rules win) are harmless.
- **Load timing:** big GLBs (54-texture fighters) need 5–10s to parse/upload
  under SwiftShader; the old fighter now stays visible until the new GLB is
  ready (no empty stage mid-swap), plus a curated idle prefetch
  (`?noprefetch=1` / `<4GB RAM` opt-outs).
- **cape-jones.glb is 1.9M triangles** (node-verified parse: valid, 0 NaN).
  It renders on real GPUs; the VM's SwiftShader software renderer cannot
  composite it (GPU process dies, canvas goes blank). The CYBORG X select UI
  (chips, stats, cursor) is verified; its 3D swap is verified by code path,
  not by pixels, in this environment.
- **QA hooks** (kept, harmless): `window.__WH_SELECT_READY` (first frame),
  `window.__WH_SELECT_DBG()` (per-side 3D state), `window.__WH_SELECT_FREEZE(v)`
  (pause rAF for screenshots under software rendering).
