# Western Heart — Character Customization & Moveset UI Design Spec
Owner-directed 2026-10-13. This is the UI/UX blueprint for the two creation systems.

## CREATE FIGHTER (Character Customization)

**Base:** Tekken 7's character customization (most recent Tekken we have). WWE creation suite layered in.

**Menu name:** "Create Fighter"

**What it does:**
- Edit existing fighters
- Edit their attires
- Create a new fighter from scratch (built on the WMXIX default custom character base)

**Preview window (the core of the experience):**
- Full 3D preview of the character WHILE you're customizing them
- Zoom in/out on the character
- Rotate the character (orbit)
- Words, HUDs, and menu selections overlay the preview window — but positioned so they DON'T cover the character
- Clean, readable layout like WWE and Tekken games — you always see what you're working on

**Flow:** Create Fighter → pick base (default or existing fighter) → customize (attire pieces, faces, hair, body parts, accessories, skin, colors) → preview updates live → save

## MOVESET (Moveset Customization)

**Base:** WWE-style moveset library (No Mercy / WMXIX layout). Tekken striking system layered in.

**Menu name:** "Moveset"

**What it does:**
- Edit a fighter's moveset — every button input, combo, grapple, taunt
- Assign any animation to any input slot
- Categories stay intact (change a punch's animation, it's still a punch with punch properties)

**Preview window (the core of the experience):**
- Big full preview window showing YOUR fighter in a ring/arena
- When you hover over or select a move, the fighter PERFORMS it live
- A second fighter (dummy/opponent) in the ring — you see how they REACT to the move
- Just like WWE games: you're in the moveset menu, you pick a grapple, you watch your fighter do it to the other fighter and see the reaction
- Test the moveset, build the moveset — all from this screen
- HUD and selections overlay but DON'T cover the preview — you see the animations happening

**Visual layout:** Based on the most recent WWE moveset menus and creation screens. Familiar to anyone who's customized a moveset in a WWE game.

**Interaction (phone-first — owner's law 2026-10-18):** NO drag-and-drop anywhere. The whole editor is three taps:
1. **TAP a move slot** — the slot highlights, the move library opens filtered to that slot's category (WWE 2K slot-first flow; MDickie tap-once-to-inspect)
2. **SCROLL the move library** — browse by positional category (WWE 2K's category organization); every entry tap-previews live on both fighters; edge-tap browse a la MDickie on short lists
3. **TAP the move to assign it** — tap-once previews, tap-again (or the confirm) assigns (MDickie tap-again-to-enter). Assigned move plays live on both fighters so you see the impact immediately

Slot modifiers (e.g. Super Finisher style upgrades) live on the slot, not the move — WWE 2K model. Tabs stay one tap deep, MDickie-style; the preview window is never covered.

**Flow:** Moveset → pick fighter → TAP input slot (button/combo/grapple/taunt) → SCROLL move library by category → TAP move to preview live on both fighters → TAP again to assign → test → save

**Wrestling-moves federation rule (owner 2026-10-18):** wrestling moves are welcome in the library — grapples, slams, submissions, dives, all of it — but EVERY wrestling move gets REWIRED to Tekken inputs and Tekken playstyle. The move's animation and identity come from wrestling; its input, frame data, cancel rules, and combo behavior are Tekken. The slot owns the properties, the move owns the animation.

## Design Principles
1. **Preview is king.** Every customization action shows live in the preview window. No blind editing.
2. **Nothing covers the character.** Menus and HUDs frame the preview, never block it.
3. **Two fighters in moveset preview.** You don't just see YOUR move — you see the IMPACT on the opponent.
4. **WWE familiarity.** Anyone who's used a WWE creation suite should feel at home immediately.
5. **Tekken depth.** The striking system has Tekken's granularity (jab strings, while-rising, crouch dash, etc.)
