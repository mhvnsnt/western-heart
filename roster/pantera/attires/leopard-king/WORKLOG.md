# WORKLOG — Pantera Attire 6 "Leopard King" + Slot-2 Tripo correction (2026-10-19)

## Owner instructions (verbatim, 2026-10-19 ~01:22 CDT)

1. "Leo man is the tripo model for that attire slot 2, the one we had in game for so long and the original tripo model and the one we put in the pictures."
2. "I have an attire 6 coming for Pantera now from tripo https://studio.tripo3d.ai/3d-model/094c2f37-1c61-43fb-82ff-7124100a1021 (Pantera Leapord King attire)"

## What was done

1. **CORRECTION — Slot 2 is the Tripo model.** The owner confirmed "Leo man" IS
   Pantera's original Tripo model (in-game for so long, the one in the pictures).
   The TRIPO-REGISTRY.md "NOT ON RECORD" note was wrong and has been corrected:
   - `roster/TRIPO-REGISTRY.md` — PANTERA row now reads attached (Slot 2 =
     "Leo man" Tripo, owner-confirmed; no Tripo link on file — recorded as
     owner-confirmed, no link invented). Slot 6 (Leopard King) added.
   - `roster/ROSTER-GAPS-2026-10-19.md` — Pantera removed from the Q1 "No Tripo
     on record" table (was row 21, in error); added to the "Tripo-attached and
     done" list with a dated correction note.
   - `roster/pantera/attires/ATTIRE-SLOTS.md` — Slot 2 row corrected: "THIS IS
     THE TRIPO MODEL (owner-confirmed 2026-10-19)". The old note claiming a
     future Tripo pull would take the slot was wrong and is gone.
2. **WIRED ATTIRE 6 "LEOPARD KING"** — `roster/pantera/attires/leopard-king/model.glb`
   (Tripo 094c2f37, "tiger humanoid" by jaywillf69, 23.3MB, 1 mesh / 3 textures,
   meshopt-compressed static — the COMPRESSED original, matching the Kevin/Star/
   King-Tyrant/Skull pattern). Model: snow-leopard head with fangs bared, spotted
   white/black rosette tights, spotted tail with dark tip, big spotted paw gloves,
   spotted boots with black trim. Wired as-is per NO-GATE law.
3. **SLOT MAP** — ATTIRE-SLOTS.md Slot 6 = "Pantera — Leopard King" (Tripo).
   Full map now: A1 = in-game T7King reskin (default), A2 = "Leo man" Tripo,
   A3 = snow leopard, A4 = T7 P2, A5 = Crimson Rage, A6 = Leopard King Tripo.
4. **RENDER** — locked-standard FRONT view at
   `docs/tpose-refs/pantera-leopard-king/p1_front.png` (ortho, white bg,
   ortho_scale 1.12x span per docs/RENDER-ORIENTATION.md). 2048px OOM-killed the
   VM (rc=137) and 1024px died silently under memory contention — shipped at
   512px, the proven recipe. Viewed with my own eyes before wiring — TRUE front:
   snow-leopard head, fangs bared, rosette tights, tail with dark tip, paw gloves.

## What was NOT done (by owner law / lane rules)

- Live-game default (`game/js/assets.js`) NOT swapped — the Leopard King GLB is
  an unrigged static; the playable swap rides with the auto-rig pass
  (Kevin/Star/King-Tyrant/Skull pattern).
- No rig, texture, or geometry changes — PANTERA RIG RULE stands (zero
  facial/mouth rig, ever).
- No invented Tripo link for Leo man — recorded as owner-confirmed, link pending
  only if one turns up on file (none found).

## Deviations

- Render at 512px instead of the 2048px convention (VM OOM-killed 2048; 1024
  died silently under contention; precedent: Attire 5 shipped 1024px for the
  same reason).
- The only fix beyond the literal ask was correcting the two docs that repeated
  the registry error (TRIPO-REGISTRY.md is the source of truth; ROSTER-GAPS and
  ATTIRE-SLOTS.md carried the same wrong note).
