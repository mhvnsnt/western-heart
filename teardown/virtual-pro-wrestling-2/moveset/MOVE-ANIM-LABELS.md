# VPW2 move-animation labels (734 unlabeled anims)

`move_anim_labels.json` (this directory) assigns names, categories, and menu
items to the 734 move anims that `move_anim_map.json` leaves unlabeled.
Produced by `../tools/label_move_anims.py`, which is deterministic from the
in-repo data — re-run it to regenerate.

## Result

| Outcome | Count |
|---|---|
| Named (move name + category + P1/P2 note) | 208 |
| Categorized (category, no name) | 318 |
| Menu item known (P1 of an unnamed move) | 84 (1 of these also has a category, counted above) |
| Ambiguous (bounded between two categories) | 125 |
| Unresolved | 0 |
| **Total unlabeled** | **734** |

526/734 (71.7%) have a category; 208/734 (28.3%) have a name. Every
assignment carries a `method` and `confidence` tag; nothing is presented as
certain unless it is derived from the game's own tables.

## How the labels were derived

**The 326-signature-move JSON** (`vpw2-moveset-summary.json`, Lane D) was
the key to the P1/P2/Block structure: signature moves come as consecutive
AnimIDs — P1 (attacker), P2 (receiver), Block — sharing one Toki1 damage
window (134/134 consecutive pairs in the signature data). The map's `note`
field (P1/P2) plus `move_number` confirmed the grouping.

**Verified structural facts** (each checked against all labeled anims):

- Moves come in P1/P2 pairs sharing a Toki1 damage window.
- **Block is a single anim** (71/72 labeled cases), note P2, exactly 1 AnimID
  after the base pair; no move has more than one Block. (The one exception is
  a 2-anim Block pair for a grapple, One Leg Headbutt.)
- **Multi-anim moves** (grapples/submissions) are strictly consecutive P1/P2
  pairs in canonical order: Base, Loop (or Pin Loop), Finish Normal,
  Finish Submit / Pinfall / Special / Mask Rip, Finish Breakup, Reversal.
  Base+Loop present ⇒ Finish Normal is always at base+4,5 (0 exceptions
  across all labeled multi-anim moves).
- **Combo Strike order:** Base, Block, [single (0,0)-window anim],
  Finish Combo, Push Reversal.
- **File 0x0061 P1s are never components:** an anim reachable from the
  edit-mode move list (via file 0x278) is a move's P1, so it can never be a
  P2, Block, or Finish component. This vetoed 8 early mislabels.

**Rules** (in precedence order; see the script for exact conditions):

1. `menu-item-p1` (84, certain) — anim is a file-0x0061 P1; records its menu
   item and damage. Category only when the item's category is known from
   labeled anims (1 of the 84: a Back Grapple move).
2. `within-family-finish-submit` (50, high) — unlabeled pair between a
   move's Finish Normal and Finish Breakup pairs. Checked: none of these
   families has a Pin Loop / Finish Pinfall component, so "Finish Submit"
   (not "Finish Pinfall") is the right name.
3. `multi-anim-completion` (24, high) — trailing Finish Submit/Breakup pairs
   after a verified Base/Loop/Finish-Normal positional pattern. No Reversal
   extension (unbounded, too risky).
4. `trailing-block` / `within-family-block` (10, high) — single anim with the
   move's damage window directly after its base pair, when the move has no
   Block yet.
5. `trailing-push-reversal` (124, medium) — pair with the move's damage
   window directly after its Finish Combo pair, all in Combo Strike. The
   name rests on a single labeled exemplar (Hashimoto Middle Kick (Left)
   Push Reversal, the only labeled Push Reversal, sitting in exactly this
   position); the position + window match is systematic (62 pairs), the
   name is the inference. Marked medium confidence.
6. `within-family-gap` (21, category-only) — ≤2-anim gaps between consecutive
   components of one move, window matching the family.
7. `category-bracket` (296, medium/low) — nearest categorized anim on both
   sides agrees. "Low" when the bracket is >10 anims away.
8. `category-bracket-ambiguous` (125, low) — nearest categorized anims on
   the two sides disagree; both bounds + nearest menu-item P1s recorded.

## What is still unnamed, and why

- **Menu item 68 — 47 anims (3603–3649), all P1s, no names.** A whole
  47-move category with no labeled anim. Damage profile is strike-like
  (mean 4.4, range 2–8; grapples average 21–32), and it sits between Sitting
  Strike and Mounted Face Up Grapple anims. Hypothesis: a mounted-strike
  category; the name is not in any in-repo source.
- **Items 113/123/124 — 47 anims (4670–4716).** 12 P1s in groups of 8 anims
  sharing one damage window each; damage 2–6. Not taunts (all 47 have damage
  windows) and not submissions (submissions have (0,0) windows). Unknown
  strike category; the 8-anim grouping is unexplained.
- **Items 22/23/82/83 — 18 anims (3426–3445).** 6 P1s, all (0,0) damage
  windows, wedged between Downed Head and Sitting Head Submission blocks.
  Hypothesis: a submission category (the Downed Arm slot is the missing
  piece of the head/arms/legs grid), but the name is not evidenced.
- **Items 57/58 (anims 2592/2593), 55 (2851), 95 (3680), 122 (4812),
  25/29/35/41/42/44/45/46/70** — single-move menu items with no names.
  Anim 4812 is almost certainly an In Corner Taunt (identical Toki1 to the
  Austin/HBK taunts at 4810/4811); the rest are unknown.
- **(0,0)-window runs** (e.g. 79–86, 272–275, 2416–2425, 4526–4535) —
  non-damaging anims (dodges, misses, whiffs, reversal attempts?) with no
  labeled exemplar to name them from.
- **Weak/Strong Running Strike 2-runs** (22 anims) — pairs wedged between
  the two interleaved running-strike categories; no damage-window match to
  either neighbor.

Naming the remaining 526 needs a source this lane does not have: the game's
Japanese move-name text (ROM text tables, not yet located) or the English
fan-translation patch's move list. The labels JSON records everything the
in-repo evidence supports and marks the rest honestly unlabeled.

## Menu-item → category map (all 133 items)

Derived from file 0x0061 groups → file 0x278 AnimIDs → labeled categories.
Every item with labeled anims maps to exactly one category (the apparent
mixing was anim 0, the "no move" placeholder, present in every group).
108/133 items have a known category; 25 do not (19 with anims, 6 empty).
The full map is reproducible from the script's `item_cats` computation; the
unknown items are 0, 12, 13, 19, 22, 23, 25, 29, 35, 41, 42, 44, 45, 46, 55,
57, 58, 68, 70, 75, 82, 83, 95, 113, 120, 122, 123, 124 (0/12/13/19/75/120
have no anims at all).
