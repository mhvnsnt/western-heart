# Western Heart — Moveset Editor Research (WWE 2K + MDickie)

Owner-directed 2026-10-18 ~19:52 CDT. Researched via public web (search + page text; no live browser).

**The owner's law (verbatim, goes in every brief):** "the moveset editor must work like the real games — NO drag-and-drop anywhere. Phone-first: TAP a move slot, SCROLL the move library, TAP the move to assign it. WWE 2K's editor UX is the editor model; Tekken is the fighting; MDickie's games are the phone-first reference."

---

## 1. WWE 2K — Create-A-Moveset (the editor model)

**Entry flow (WWE 2K24, verified across guides):**
1. Main menu → **Creations** tab → **Move-Set**
2. Pick the superstar — tabs split roster superstars from the **Custom Superstar** tab
3. **Moves** → category (e.g. **Finisher**) → position/environment (e.g. **In-Ring**)
4. **Select an empty slot** → **select any move from the list** → assigned
5. Slot modifiers exist separate from moves: hover an assigned finisher slot + RT/R2 turns it into a **Super Finisher** (2K24)

**The library is organized by positional category.** Every move in the game is reachable through Create-A-Moveset, filed under the position it belongs to: standing strikes, grapples by position and strength (front/back, weak/strong, light/heavy/signature/power/quick grapple slots), submissions, ground attacks/grapples, back attacks, corner/turnbuckle, top rope, running, apron/ringside, plus signature/finisher slots per position. The slot name and the move name are separate first-class things — the game's CPU-logic menu lists slot names in one column and move names in another.

**Assignment is always slot-first, never drag-and-drop:** highlight the slot → browse the list for that category → confirm. There is no drag-and-drop anywhere in the flow — on console or PC.

**Related editor behaviors worth copying:**
- Heavy-combo finishers are swappable per combo string from the same editor — the end of every combo string is just another slot.
- Fighting style is picked inside Create-A-Moveset (2K16: Aerialist / Brawler / Giant / Powerhouse / Showboat / Striker / Technician) alongside personality sliders — the editor assigns identity, not just moves.
- Slot eligibility is strict: a move only appears in the list for slots whose category it belongs to.

---

## 2. MDickie — the phone-first reference (Wrestling Revolution 3D / Super City lineage)

MDickie's games are built tap-first from the ground up, and the editor grammar is exactly the owner's pattern.

**Menu controls (from the game's own manual text):**
- "Touch either side of a value or box to browse its contents left or right." — every slot browses its library by tapping the slot's edges. No picker dialog, no drag.
- "When selecting characters, touching their slot once will display their stats and touching again will proceed to access them." — **tap-once-to-inspect, tap-again-to-enter.** This is the owner's slot → library → assign pattern in MDickie's own words.
- Hold over a character slot to pick it up and move it (roster slots only — moving, not assigning).
- Back arrow / ESC exits any screen; tap the chosen line of text to confirm.

**Editor structure:** tabbed pages (shoulder triggers / taps move between tabs), each tab a full screen of options — one tap deep, no nested fiddly menus. Rotate the model by swiping it directly.

**Moves get their own pages in the editor** (MDickie's dev blog, Wrestling MPire CE era): "in the case of moves, a couple of whole new pages! Two separate ones are required now (one for standing moves and one for ground moves)... with much more room to display the options clearly." Moves are a named list — "The name you give it will appear in the editor to help people select it."

**Live preview in the editor** (same source): "the chance to preview certain animations... you can now see every type of attack played out to help you decide." Selecting a move shows it — the ancestor of our two-fighter live preview.

---

## 3. The synthesis — what Western Heart builds

| Source | What we take |
|---|---|
| **WWE 2K** | The editor model: slot-first flow, library organized by positional category, strict slot eligibility, no drag-and-drop anywhere |
| **MDickie** | The phone-first grammar: tap slot → browse by tapping/scrolling → tap to assign; tap-once-inspect / tap-again-enter; one-tap-deep tabbed pages |
| **Tekken** | The fighting: the library's Tekken slot group (jab strings, while-rising, crouch dash, throws, rage, stances) is the playstyle everything runs on |

**Interaction law (owner, verbatim):** TAP a move slot → SCROLL the move library → TAP the move to assign it. NO drag-and-drop anywhere. Phone-first.

**WRESTLING-MOVES FEDERATION RULE (owner 2026-10-18):** wrestling moves are welcome in the library — grapples, slams, submissions, dives, all of it — but EVERY wrestling move gets REWIRED to Tekken inputs and Tekken playstyle. The move's animation and identity come from wrestling; its input, frame data, cancel rules, and combo behavior are Tekken. This is the same principle already in the spec: "Categories stay intact (change a punch's animation, it's still a punch with punch properties)" — the slot owns the properties, the move owns the animation.

---

## Sources

- WWE 2K24 Super Finisher assignment flow — https://nintendosmash.com/wwe-2k24-how-to-assign-a-super-finisher-to-a-custom-superstar/
- WWE 2K26 moves list / Create-A-Moveset overview — https://irnpost.com/wwe-2k26-the-ultimate-guide-tips-tricks/
- WWE 2K24 heavy-combo finisher swapping — https://achievers.amway.com/wwe-2k24-heavy-combos-why-your-timing-is-probably-off-and-how-to-fix-it-20hv
- WWE 2K16 Creation Suite details (fighting styles, personality sliders) — http://www.thesmackdownhotel.com/news/wwe2k16/wwe-2k16-full-creation-suite-details-custom-arenas-create-a-superstar-and-all-creation-modes
- WWE 2K CPU-logic slot/move columns — https://steamcommunity.com/sharedfiles/filedetails/?id=2518292334
- Classic moveset category layout — https://www.supercheats.com/playstation2/walkthroughs/-walkthrough04.txt
- MDickie menu controls (touch either side to browse; tap slot once/twice) — https://appfelstrudel.com/id/542665773/wrestling-revolution.html and http://www.mdickie.com/guides/wr3d_controls.htm
- MDickie dev blog: moves pages in the editor + animation preview — http://www.mdickie.com/prev_wm2008ce_beta.htm and http://mdickie.com/code_wm2008_moves.htm
- MDickie editor costuming/tabs — https://www.scribd.com/document/432549820/pdf
