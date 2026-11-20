// WWE 2K22 Create-A-Moveset slot grid for the Western Heart editor.
// Source of truth: the research lane caw-slots.json (see
// docs/research/wwe-2k22-caw-editor.md for sources and the honesty note).
// Slot counts are integers ONLY where a public source states them;
// every other group carries slot_count: null.
// REDACTION (this lane, per the no-famous-names rule): the source guide's
// examples_from_source recommendation lists are NOT shipped here, because
// several entries are famous wrestler signature moves. Structure only.
// Button names: LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2,
// LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.
export const WWE2K22_CAW_SLOTS = {
  "categories": [
    {
      "id": "standing",
      "source_urls": [
        "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
      ],
      "status": "confirmed",
      "subcategories": [
        {
          "id": "standing.light_attack",
          "name": "Light Attack",
          "slot_count": null,
          "slot_count_status": "unknown",
          "wh_input_proposed": "LP1",
          "wwe_input": "Square / X"
        },
        {
          "id": "standing.heavy_attack",
          "name": "Heavy Attack",
          "slot_count": null,
          "slot_count_status": "unknown",
          "wh_input_proposed": "RP2",
          "wwe_input": "X / A"
        },
        {
          "id": "standing.light_grapple",
          "name": "Light Grapple",
          "slot_count": null,
          "slot_count_status": "unknown-as-category; see explicit grapple grid below for the confirmed 10-slot count",
          "wh_input_proposed": "LP1+LK3 + direction",
          "wwe_input": "Grab + Light + stick direction"
        },
        {
          "id": "standing.heavy_grapple",
          "name": "Heavy Grapple",
          "slot_count": null,
          "slot_count_status": "unknown-as-category; see explicit grapple grid below for the confirmed 10-slot count",
          "wh_input_proposed": "RP2+RK4 + direction",
          "wwe_input": "Grab + Heavy + stick direction"
        },
        {
          "id": "standing.running",
          "name": "Running",
          "slot_count": null,
          "slot_count_status": "unknown",
          "wh_input_proposed": "f,f+LP1 / f,f+RP2 (proposed; running state is a position flag in WH, not a Tekken input)",
          "wwe_input": "Run (L2/LT) + Light/Heavy/Grab"
        }
      ],
      "wwe_category": "Standing"
    },
    {
      "id": "ground",
      "source_urls": [
        "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
      ],
      "status": "confirmed",
      "subcategories": [
        {
          "id": "ground.supine",
          "name": "Supine",
          "opponent_state": "face up",
          "slot_count": null,
          "slot_count_status": "unknown"
        },
        {
          "id": "ground.prone",
          "name": "Prone",
          "note": "Prone submissions (e.g. Cloverleaf Breaker) cross-reference holds.submission; do not duplicate the move.",
          "opponent_state": "face down",
          "slot_count": null,
          "slot_count_status": "unknown"
        },
        {
          "id": "ground.kneeling",
          "name": "Kneeling",
          "opponent_state": "kneeling",
          "slot_count": null,
          "slot_count_status": "unknown"
        },
        {
          "id": "ground.seated",
          "name": "Seated",
          "opponent_state": "seated",
          "slot_count": null,
          "slot_count_status": "unknown"
        }
      ],
      "wwe_category": "Ground"
    },
    {
      "id": "corner",
      "source_urls": [
        "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
      ],
      "status": "confirmed",
      "subcategories": [
        {
          "id": "corner.leaning",
          "name": "Leaning",
          "opponent_state": "leaning on turnbuckle, facing out",
          "slot_count": null,
          "slot_count_status": "unknown"
        },
        {
          "id": "corner.top_rope",
          "name": "Top Rope",
          "opponent_state": "seated on top turnbuckle",
          "slot_count": null,
          "slot_count_status": "unknown"
        },
        {
          "id": "corner.seated",
          "name": "Seated",
          "opponent_state": "seated on mat leaning on turnbuckle",
          "slot_count": null,
          "slot_count_status": "unknown"
        },
        {
          "id": "corner.tree_of_woe",
          "name": "Tree of Woe",
          "opponent_state": "hung upside down on turnbuckle",
          "slot_count": null,
          "slot_count_status": "unknown"
        }
      ],
      "wwe_category": "Corner"
    },
    {
      "id": "rope",
      "source_urls": [
        "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
      ],
      "status": "confirmed",
      "subcategories": [
        {
          "id": "rope.leaning",
          "name": "Leaning",
          "opponent_state": "leaning/draped on ropes",
          "slot_count": null,
          "slot_count_status": "unknown"
        },
        {
          "id": "rope.middle_rope",
          "name": "Middle Rope",
          "note": "Middle-rope attacks are distinct from top-rope attacks (tap R1/RB, do not sprint).",
          "opponent_state": "attacker on middle turnbuckle",
          "slot_count": null,
          "slot_count_status": "unknown"
        }
      ],
      "wwe_category": "Rope"
    },
    {
      "id": "irish_whip",
      "source_urls": [
        "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
      ],
      "status": "confirmed",
      "subcategories": [
        {
          "id": "irish_whip.rebound",
          "name": "Rebound Attack",
          "slot_count": null,
          "slot_count_status": "unknown"
        },
        {
          "id": "irish_whip.pull_back",
          "name": "Pull-Back Attack",
          "slot_count": null,
          "slot_count_status": "unknown"
        }
      ],
      "wwe_category": "Irish Whip"
    },
    {
      "id": "holds",
      "source_urls": [
        "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
      ],
      "status": "confirmed",
      "subcategories": [
        {
          "id": "holds.submission",
          "name": "Submission",
          "note": "No source states a pool restriction for this group; do not invent one.",
          "slot_count": null,
          "slot_count_status": "unknown"
        }
      ],
      "wwe_category": "Holds"
    },
    {
      "id": "finisher",
      "source_urls": [
        "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
      ],
      "status": "confirmed",
      "subcategories": [
        {
          "gate": "Finisher meter",
          "id": "finisher.in_ring",
          "name": "In-Ring",
          "slot_count": null,
          "slot_count_status": "unknown; do not equate with finishers_stored_max=3"
        },
        {
          "gate": "Finisher meter",
          "id": "finisher.ringside",
          "name": "Ringside",
          "slot_count": null,
          "slot_count_status": "unknown"
        },
        {
          "gate": "Finisher meter",
          "id": "finisher.tag_team",
          "name": "Tag Team",
          "slot_count": null,
          "slot_count_status": "unknown"
        }
      ],
      "wwe_category": "Finisher"
    },
    {
      "id": "signature",
      "note": "No Tag Team signature subcategory is listed in the source; do not copy finisher.tag_team here.",
      "source_urls": [
        "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
      ],
      "status": "confirmed",
      "subcategories": [
        {
          "gate": "3 Special Stock",
          "id": "signature.in_ring",
          "name": "In-Ring",
          "slot_count": null,
          "slot_count_status": "unknown"
        },
        {
          "gate": "3 Special Stock",
          "id": "signature.ringside",
          "name": "Ringside",
          "slot_count": null,
          "slot_count_status": "unknown"
        }
      ],
      "wwe_category": "Signature"
    }
  ],
  "combos": {
    "chains": [
      "towards",
      "away",
      "neutral"
    ],
    "customisable_in_editor": true,
    "ender_types": [
      "light",
      "heavy",
      "grapple"
    ],
    "max_length": 4,
    "min_length": 2,
    "must_start": "light",
    "notes": [
      "Combo Enders can include moves not normally available from Standing, such as certain Running Attacks.",
      "Some chains turn the opponent around, opening rear-facing Heavy/Grab options."
    ],
    "per_chain_count": null,
    "per_chain_count_status": "unknown; do not assume 10/10/10",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players",
      "https://realsport101.com/article/wwe-2k22-combos-guide-how-to-light-heavy-grapple-controls",
      "https://www.thesmackdownhotel.com/news/wwe2k24/wwe-2k24-controls-scheme-full-guide-for-ps5-ps4-xbox"
    ],
    "status": "confirmed",
    "total_most": 30,
    "total_powerhouse_3hit": 18
  },
  "explicit_slots_confirmed": [
    {
      "direction": "none",
      "group": "standing_grapple_front",
      "id": "standing_grapple_front.light.neutral",
      "kind": "grapple",
      "source_urls": [
        "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
      ],
      "status": "confirmed",
      "stick": "neutral",
      "strength": "light",
      "wh_display_input": "LP1+LK3",
      "wh_input": "LP1+LK3",
      "wwe_input": "Grab + Light, no stick direction"
    },
    {
      "direction": "u",
      "group": "standing_grapple_front",
      "id": "standing_grapple_front.light.up",
      "kind": "grapple",
      "source_urls": [
        "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
      ],
      "status": "confirmed",
      "stick": "up",
      "strength": "light",
      "wh_display_input": "u+LP1+LK3",
      "wh_input": "u+LP1+LK3",
      "wwe_input": "Grab + Light + Up"
    },
    {
      "direction": "d",
      "group": "standing_grapple_front",
      "id": "standing_grapple_front.light.down",
      "kind": "grapple",
      "source_urls": [
        "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
      ],
      "status": "confirmed",
      "stick": "down",
      "strength": "light",
      "wh_display_input": "d+LP1+LK3",
      "wh_input": "d+LP1+LK3",
      "wwe_input": "Grab + Light + Down"
    },
    {
      "direction": "b",
      "group": "standing_grapple_front",
      "id": "standing_grapple_front.light.left",
      "kind": "grapple",
      "source_urls": [
        "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
      ],
      "status": "confirmed",
      "stick": "left",
      "strength": "light",
      "translation": "proposed",
      "wh_display_input": "b+LP1+LK3",
      "wh_input": "b+LP1+LK3",
      "wwe_input": "Grab + Light + Left"
    },
    {
      "direction": "f",
      "group": "standing_grapple_front",
      "id": "standing_grapple_front.light.right",
      "kind": "grapple",
      "source_urls": [
        "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
      ],
      "status": "confirmed",
      "stick": "right",
      "strength": "light",
      "translation": "proposed",
      "wh_display_input": "f+LP1+LK3",
      "wh_input": "f+LP1+LK3",
      "wwe_input": "Grab + Light + Right"
    },
    {
      "direction": "none",
      "group": "standing_grapple_front",
      "id": "standing_grapple_front.heavy.neutral",
      "kind": "grapple",
      "source_urls": [
        "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
      ],
      "status": "confirmed",
      "stick": "neutral",
      "strength": "heavy",
      "wh_display_input": "RP2+RK4",
      "wh_input": "RP2+RK4",
      "wwe_input": "Grab + Heavy, no stick direction"
    },
    {
      "direction": "u",
      "group": "standing_grapple_front",
      "id": "standing_grapple_front.heavy.up",
      "kind": "grapple",
      "source_urls": [
        "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
      ],
      "status": "confirmed",
      "stick": "up",
      "strength": "heavy",
      "wh_display_input": "u+RP2+RK4",
      "wh_input": "u+RP2+RK4",
      "wwe_input": "Grab + Heavy + Up"
    },
    {
      "direction": "d",
      "group": "standing_grapple_front",
      "id": "standing_grapple_front.heavy.down",
      "kind": "grapple",
      "source_urls": [
        "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
      ],
      "status": "confirmed",
      "stick": "down",
      "strength": "heavy",
      "wh_display_input": "d+RP2+RK4",
      "wh_input": "d+RP2+RK4",
      "wwe_input": "Grab + Heavy + Down"
    },
    {
      "direction": "b",
      "group": "standing_grapple_front",
      "id": "standing_grapple_front.heavy.left",
      "kind": "grapple",
      "source_urls": [
        "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
      ],
      "status": "confirmed",
      "stick": "left",
      "strength": "heavy",
      "translation": "proposed",
      "wh_display_input": "b+RP2+RK4",
      "wh_input": "b+RP2+RK4",
      "wwe_input": "Grab + Heavy + Left"
    },
    {
      "direction": "f",
      "group": "standing_grapple_front",
      "id": "standing_grapple_front.heavy.right",
      "kind": "grapple",
      "source_urls": [
        "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
      ],
      "status": "confirmed",
      "stick": "right",
      "strength": "heavy",
      "translation": "proposed",
      "wh_display_input": "f+RP2+RK4",
      "wh_input": "f+RP2+RK4",
      "wwe_input": "Grab + Heavy + Right"
    }
  ],
  "game": "WWE 2K22",
  "global_limits": {
    "caw_slots": {
      "source_urls": [
        "http://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-2k20-creation-suite-comparison-how-much-has-changed"
      ],
      "status": "confirmed",
      "value": 100
    },
    "finishers_stored_max": {
      "note": "Stored count, NOT a finisher-slot count.",
      "source_urls": [
        "https://realsport101.com/article/wwe-2k22-how-to-fill-special-finisher-meter-faster-signature-payback"
      ],
      "status": "confirmed",
      "value": 3
    },
    "payback_max": {
      "source_urls": [
        "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-what-happened-to-abilities-skills-omg-moments"
      ],
      "status": "confirmed",
      "value": 1
    },
    "special_stock_max": {
      "source_urls": [
        "https://realsport101.com/article/wwe-2k22-how-to-fill-special-finisher-meter-faster-signature-payback"
      ],
      "status": "confirmed",
      "value": 3
    },
    "total_moves_bracket": {
      "source_urls": [
        "http://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-2k20-creation-suite-comparison-how-much-has-changed"
      ],
      "status": "confirmed",
      "value": "3000+"
    }
  },
  "honesty": "Every group carries status + source_urls. slot_count is an integer ONLY where a public source states it; otherwise null with slot_count_status explaining why. Never treat a null as zero and never fill it from the Pro Game Guides top-5 recommendation lists.",
  "payback": {
    "id": "payback",
    "kind": "payback",
    "note": "Ability slot, not a move slot, in 2K22 structure.",
    "slot_count": 1,
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-what-happened-to-abilities-skills-omg-moments"
    ],
    "status": "confirmed",
    "wwe_input": "R2+Triangle / RT+Y when prompted"
  },
  "schema": "wwe2k22-caw-slots/v1"
};

export const WWE2K22_EDITOR_ROWS = [
  {
    "direction": "none",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_front.light.neutral",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "confirmed",
    "translation": "proposed",
    "wh_buttons": [
      "LP1",
      "LK3"
    ],
    "wh_display_input": "LP1+LK3",
    "wh_input": "LP1+LK3",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Light, no stick direction",
    "wwe_subcategory": "Light Grapple"
  },
  {
    "direction": "u",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_front.light.up",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "confirmed",
    "translation": "proposed",
    "wh_buttons": [
      "LP1",
      "LK3"
    ],
    "wh_display_input": "u+LP1+LK3",
    "wh_input": "u+LP1+LK3",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Light + Up",
    "wwe_subcategory": "Light Grapple"
  },
  {
    "direction": "d",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_front.light.down",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "confirmed",
    "translation": "proposed",
    "wh_buttons": [
      "LP1",
      "LK3"
    ],
    "wh_display_input": "d+LP1+LK3",
    "wh_input": "d+LP1+LK3",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Light + Down",
    "wwe_subcategory": "Light Grapple"
  },
  {
    "direction": "b",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_front.light.left",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "confirmed",
    "translation": "proposed",
    "wh_buttons": [
      "LP1",
      "LK3"
    ],
    "wh_display_input": "b+LP1+LK3",
    "wh_input": "b+LP1+LK3",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Light + Left",
    "wwe_subcategory": "Light Grapple"
  },
  {
    "direction": "f",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_front.light.right",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "confirmed",
    "translation": "proposed",
    "wh_buttons": [
      "LP1",
      "LK3"
    ],
    "wh_display_input": "f+LP1+LK3",
    "wh_input": "f+LP1+LK3",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Light + Right",
    "wwe_subcategory": "Light Grapple"
  },
  {
    "direction": "none",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_front.heavy.neutral",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "confirmed",
    "translation": "proposed",
    "wh_buttons": [
      "RP2",
      "RK4"
    ],
    "wh_display_input": "RP2+RK4",
    "wh_input": "RP2+RK4",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Heavy, no stick direction",
    "wwe_subcategory": "Heavy Grapple"
  },
  {
    "direction": "u",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_front.heavy.up",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "confirmed",
    "translation": "proposed",
    "wh_buttons": [
      "RP2",
      "RK4"
    ],
    "wh_display_input": "u+RP2+RK4",
    "wh_input": "u+RP2+RK4",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Heavy + Up",
    "wwe_subcategory": "Heavy Grapple"
  },
  {
    "direction": "d",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_front.heavy.down",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "confirmed",
    "translation": "proposed",
    "wh_buttons": [
      "RP2",
      "RK4"
    ],
    "wh_display_input": "d+RP2+RK4",
    "wh_input": "d+RP2+RK4",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Heavy + Down",
    "wwe_subcategory": "Heavy Grapple"
  },
  {
    "direction": "b",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_front.heavy.left",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "confirmed",
    "translation": "proposed",
    "wh_buttons": [
      "RP2",
      "RK4"
    ],
    "wh_display_input": "b+RP2+RK4",
    "wh_input": "b+RP2+RK4",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Heavy + Left",
    "wwe_subcategory": "Heavy Grapple"
  },
  {
    "direction": "f",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_front.heavy.right",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "confirmed",
    "translation": "proposed",
    "wh_buttons": [
      "RP2",
      "RK4"
    ],
    "wh_display_input": "f+RP2+RK4",
    "wh_input": "f+RP2+RK4",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Heavy + Right",
    "wwe_subcategory": "Heavy Grapple"
  },
  {
    "direction": "none",
    "kind": "payback",
    "move_id": null,
    "slot_count": 1,
    "slot_id": "payback",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-what-happened-to-abilities-skills-omg-moments"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Payback",
    "wwe_input": "R2+Triangle / RT+Y when prompted",
    "wwe_subcategory": "Payback"
  },
  {
    "combo_rules": {
      "max_length": 4,
      "min_length": 2,
      "must_start": "light",
      "per_chain_count": null,
      "total_most": 30,
      "total_powerhouse_3hit": 18
    },
    "direction": "none",
    "kind": "combo",
    "move_id": null,
    "slot_id": "combos.towards",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players",
      "https://realsport101.com/article/wwe-2k22-combos-guide-how-to-light-heavy-grapple-controls",
      "https://www.thesmackdownhotel.com/news/wwe2k24/wwe-2k24-controls-scheme-full-guide-for-ps5-ps4-xbox"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Combos",
    "wwe_input": "Light Attack first, then Light/Heavy/Grab",
    "wwe_subcategory": "towards"
  },
  {
    "combo_rules": {
      "max_length": 4,
      "min_length": 2,
      "must_start": "light",
      "per_chain_count": null,
      "total_most": 30,
      "total_powerhouse_3hit": 18
    },
    "direction": "none",
    "kind": "combo",
    "move_id": null,
    "slot_id": "combos.away",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players",
      "https://realsport101.com/article/wwe-2k22-combos-guide-how-to-light-heavy-grapple-controls",
      "https://www.thesmackdownhotel.com/news/wwe2k24/wwe-2k24-controls-scheme-full-guide-for-ps5-ps4-xbox"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Combos",
    "wwe_input": "Light Attack first, then Light/Heavy/Grab",
    "wwe_subcategory": "away"
  },
  {
    "combo_rules": {
      "max_length": 4,
      "min_length": 2,
      "must_start": "light",
      "per_chain_count": null,
      "total_most": 30,
      "total_powerhouse_3hit": 18
    },
    "direction": "none",
    "kind": "combo",
    "move_id": null,
    "slot_id": "combos.neutral",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players",
      "https://realsport101.com/article/wwe-2k22-combos-guide-how-to-light-heavy-grapple-controls",
      "https://www.thesmackdownhotel.com/news/wwe2k24/wwe-2k24-controls-scheme-full-guide-for-ps5-ps4-xbox"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Combos",
    "wwe_input": "Light Attack first, then Light/Heavy/Grab",
    "wwe_subcategory": "neutral"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "standing.light_attack",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": "LP1",
    "wh_input": "LP1",
    "wwe_category": "Standing",
    "wwe_input": "Square / X",
    "wwe_subcategory": "Light Attack"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "standing.heavy_attack",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": "RP2",
    "wh_input": "RP2",
    "wwe_category": "Standing",
    "wwe_input": "X / A",
    "wwe_subcategory": "Heavy Attack"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown-as-category; see explicit grapple grid below for the confirmed 10-slot count",
    "slot_id": "standing.light_grapple",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": "LP1+LK3 + direction",
    "wh_input": "LP1+LK3 + direction",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Light + stick direction",
    "wwe_subcategory": "Light Grapple"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown-as-category; see explicit grapple grid below for the confirmed 10-slot count",
    "slot_id": "standing.heavy_grapple",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": "RP2+RK4 + direction",
    "wh_input": "RP2+RK4 + direction",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Heavy + stick direction",
    "wwe_subcategory": "Heavy Grapple"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "standing.running",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": "f,f+LP1 / f,f+RP2 (proposed; running state is a position flag in WH, not a Tekken input)",
    "wh_input": "f,f+LP1 / f,f+RP2 (proposed; running state is a position flag in WH, not a Tekken input)",
    "wwe_category": "Standing",
    "wwe_input": "Run (L2/LT) + Light/Heavy/Grab",
    "wwe_subcategory": "Running"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "ground.supine",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Ground",
    "wwe_input": null,
    "wwe_subcategory": "Supine"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "ground.prone",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Ground",
    "wwe_input": null,
    "wwe_subcategory": "Prone"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "ground.kneeling",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Ground",
    "wwe_input": null,
    "wwe_subcategory": "Kneeling"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "ground.seated",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Ground",
    "wwe_input": null,
    "wwe_subcategory": "Seated"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "corner.leaning",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Corner",
    "wwe_input": null,
    "wwe_subcategory": "Leaning"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "corner.top_rope",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Corner",
    "wwe_input": null,
    "wwe_subcategory": "Top Rope"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "corner.seated",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Corner",
    "wwe_input": null,
    "wwe_subcategory": "Seated"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "corner.tree_of_woe",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Corner",
    "wwe_input": null,
    "wwe_subcategory": "Tree of Woe"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "rope.leaning",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Rope",
    "wwe_input": null,
    "wwe_subcategory": "Leaning"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "rope.middle_rope",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Rope",
    "wwe_input": null,
    "wwe_subcategory": "Middle Rope"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "irish_whip.rebound",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Irish Whip",
    "wwe_input": null,
    "wwe_subcategory": "Rebound Attack"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "irish_whip.pull_back",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Irish Whip",
    "wwe_input": null,
    "wwe_subcategory": "Pull-Back Attack"
  },
  {
    "direction": "none",
    "kind": "submission",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "holds.submission",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Holds",
    "wwe_input": null,
    "wwe_subcategory": "Submission"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown; do not equate with finishers_stored_max=3",
    "slot_id": "finisher.in_ring",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Finisher",
    "wwe_input": null,
    "wwe_subcategory": "In-Ring"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "finisher.ringside",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Finisher",
    "wwe_input": null,
    "wwe_subcategory": "Ringside"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "finisher.tag_team",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Finisher",
    "wwe_input": null,
    "wwe_subcategory": "Tag Team"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "signature.in_ring",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Signature",
    "wwe_input": null,
    "wwe_subcategory": "In-Ring"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "slot_count": null,
    "slot_count_status": "unknown",
    "slot_id": "signature.ringside",
    "source_urls": [
      "https://progameguides.com/wwe/best-movesets-for-caws-in-wwe-2k22/"
    ],
    "status": "confirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Signature",
    "wwe_input": null,
    "wwe_subcategory": "Ringside"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "note": "Top turnbuckle attack vs standing opponent.",
    "nullable": false,
    "slot_id": "diving.top_rope.vs_standing",
    "source_urls": [
      "https://realsport101.com/wwe2k/wwe-2k22-how-to-do-springboard-moves-dive-outside-ringside-running/",
      "https://gamerjournalist.com/wwe-2k22-springboard-dives/",
      "https://www.gamepur.com/guides/how-to-do-a-middle-rope-diving-attack-in-wwe-2k22"
    ],
    "status": "gameplay-confirmed, editor-tab-unconfirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Diving / Springboard / Apron",
    "wwe_input": null,
    "wwe_subcategory": "diving.top_rope.vs_standing"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "note": "Top turnbuckle attack vs downed opponent (face up supine / face down).",
    "nullable": false,
    "slot_id": "diving.top_rope.vs_downed",
    "source_urls": [
      "https://realsport101.com/wwe2k/wwe-2k22-how-to-do-springboard-moves-dive-outside-ringside-running/",
      "https://gamerjournalist.com/wwe-2k22-springboard-dives/",
      "https://www.gamepur.com/guides/how-to-do-a-middle-rope-diving-attack-in-wwe-2k22"
    ],
    "status": "gameplay-confirmed, editor-tab-unconfirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Diving / Springboard / Apron",
    "wwe_input": null,
    "wwe_subcategory": "diving.top_rope.vs_downed"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "note": "Middle turnbuckle; tap R1/RB, then Light/Heavy. Distinct from top rope.",
    "nullable": false,
    "slot_id": "diving.middle_rope",
    "source_urls": [
      "https://realsport101.com/wwe2k/wwe-2k22-how-to-do-springboard-moves-dive-outside-ringside-running/",
      "https://gamerjournalist.com/wwe-2k22-springboard-dives/",
      "https://www.gamepur.com/guides/how-to-do-a-middle-rope-diving-attack-in-wwe-2k22"
    ],
    "status": "gameplay-confirmed, editor-tab-unconfirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Diving / Springboard / Apron",
    "wwe_input": null,
    "wwe_subcategory": "diving.middle_rope"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "note": "None is a valid choice for every springboard position.",
    "nullable": true,
    "slot_id": "springboard.ropes",
    "source_urls": [
      "https://realsport101.com/wwe2k/wwe-2k22-how-to-do-springboard-moves-dive-outside-ringside-running/",
      "https://gamerjournalist.com/wwe-2k22-springboard-dives/",
      "https://www.gamepur.com/guides/how-to-do-a-middle-rope-diving-attack-in-wwe-2k22"
    ],
    "status": "gameplay-confirmed, editor-tab-unconfirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Diving / Springboard / Apron",
    "wwe_input": null,
    "wwe_subcategory": "springboard.ropes"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "note": "",
    "nullable": true,
    "slot_id": "springboard.corner",
    "source_urls": [
      "https://realsport101.com/wwe2k/wwe-2k22-how-to-do-springboard-moves-dive-outside-ringside-running/",
      "https://gamerjournalist.com/wwe-2k22-springboard-dives/",
      "https://www.gamepur.com/guides/how-to-do-a-middle-rope-diving-attack-in-wwe-2k22"
    ],
    "status": "gameplay-confirmed, editor-tab-unconfirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Diving / Springboard / Apron",
    "wwe_input": null,
    "wwe_subcategory": "springboard.corner"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "note": "Apron into the ring.",
    "nullable": true,
    "slot_id": "springboard.apron_in",
    "source_urls": [
      "https://realsport101.com/wwe2k/wwe-2k22-how-to-do-springboard-moves-dive-outside-ringside-running/",
      "https://gamerjournalist.com/wwe-2k22-springboard-dives/",
      "https://www.gamepur.com/guides/how-to-do-a-middle-rope-diving-attack-in-wwe-2k22"
    ],
    "status": "gameplay-confirmed, editor-tab-unconfirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Diving / Springboard / Apron",
    "wwe_input": null,
    "wwe_subcategory": "springboard.apron_in"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "note": "Apron to ringside; needs an extra LB/L1 press.",
    "nullable": true,
    "slot_id": "springboard.apron_out",
    "source_urls": [
      "https://realsport101.com/wwe2k/wwe-2k22-how-to-do-springboard-moves-dive-outside-ringside-running/",
      "https://gamerjournalist.com/wwe-2k22-springboard-dives/",
      "https://www.gamepur.com/guides/how-to-do-a-middle-rope-diving-attack-in-wwe-2k22"
    ],
    "status": "gameplay-confirmed, editor-tab-unconfirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Diving / Springboard / Apron",
    "wwe_input": null,
    "wwe_subcategory": "springboard.apron_out"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "note": "Running springboard to ringside; timing-based.",
    "nullable": true,
    "slot_id": "springboard.running",
    "source_urls": [
      "https://realsport101.com/wwe2k/wwe-2k22-how-to-do-springboard-moves-dive-outside-ringside-running/",
      "https://gamerjournalist.com/wwe-2k22-springboard-dives/",
      "https://www.gamepur.com/guides/how-to-do-a-middle-rope-diving-attack-in-wwe-2k22"
    ],
    "status": "gameplay-confirmed, editor-tab-unconfirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Diving / Springboard / Apron",
    "wwe_input": null,
    "wwe_subcategory": "springboard.running"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "note": "Attacker on apron vs opponent in-ring / at ringside. Editor-tab placement unconfirmed.",
    "nullable": false,
    "slot_id": "apron.attacks",
    "source_urls": [
      "https://realsport101.com/wwe2k/wwe-2k22-how-to-do-springboard-moves-dive-outside-ringside-running/",
      "https://gamerjournalist.com/wwe-2k22-springboard-dives/",
      "https://www.gamepur.com/guides/how-to-do-a-middle-rope-diving-attack-in-wwe-2k22"
    ],
    "status": "gameplay-confirmed, editor-tab-unconfirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Diving / Springboard / Apron",
    "wwe_input": null,
    "wwe_subcategory": "apron.attacks"
  },
  {
    "direction": "none",
    "kind": "position",
    "move_id": null,
    "note": "Running dive to ringside.",
    "nullable": false,
    "slot_id": "diving.outside_running",
    "source_urls": [
      "https://realsport101.com/wwe2k/wwe-2k22-how-to-do-springboard-moves-dive-outside-ringside-running/",
      "https://gamerjournalist.com/wwe-2k22-springboard-dives/",
      "https://www.gamepur.com/guides/how-to-do-a-middle-rope-diving-attack-in-wwe-2k22"
    ],
    "status": "gameplay-confirmed, editor-tab-unconfirmed",
    "wh_buttons": [],
    "wh_display_input": null,
    "wh_input": null,
    "wwe_category": "Diving / Springboard / Apron",
    "wwe_input": null,
    "wwe_subcategory": "diving.outside_running"
  },
  {
    "direction": "none",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_behind.light.neutral",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "inferred-mirror, unconfirmed",
    "wh_buttons": [
      "LP1",
      "LK3"
    ],
    "wh_display_input": "LP1+LK3",
    "wh_input": "LP1+LK3",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Light, no stick direction (behind, via reposition)",
    "wwe_subcategory": "Behind Grapple (inferred)"
  },
  {
    "direction": "u",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_behind.light.up",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "inferred-mirror, unconfirmed",
    "wh_buttons": [
      "LP1",
      "LK3"
    ],
    "wh_display_input": "u+LP1+LK3",
    "wh_input": "u+LP1+LK3",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Light + Up (behind, via reposition)",
    "wwe_subcategory": "Behind Grapple (inferred)"
  },
  {
    "direction": "d",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_behind.light.down",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "inferred-mirror, unconfirmed",
    "wh_buttons": [
      "LP1",
      "LK3"
    ],
    "wh_display_input": "d+LP1+LK3",
    "wh_input": "d+LP1+LK3",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Light + Down (behind, via reposition)",
    "wwe_subcategory": "Behind Grapple (inferred)"
  },
  {
    "direction": "b",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_behind.light.left",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "inferred-mirror, unconfirmed",
    "wh_buttons": [
      "LP1",
      "LK3"
    ],
    "wh_display_input": "b+LP1+LK3",
    "wh_input": "b+LP1+LK3",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Light + Left (behind, via reposition)",
    "wwe_subcategory": "Behind Grapple (inferred)"
  },
  {
    "direction": "f",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_behind.light.right",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "inferred-mirror, unconfirmed",
    "wh_buttons": [
      "LP1",
      "LK3"
    ],
    "wh_display_input": "f+LP1+LK3",
    "wh_input": "f+LP1+LK3",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Light + Right (behind, via reposition)",
    "wwe_subcategory": "Behind Grapple (inferred)"
  },
  {
    "direction": "none",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_behind.heavy.neutral",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "inferred-mirror, unconfirmed",
    "wh_buttons": [
      "RP2",
      "RK4"
    ],
    "wh_display_input": "RP2+RK4",
    "wh_input": "RP2+RK4",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Heavy, no stick direction (behind, via reposition)",
    "wwe_subcategory": "Behind Grapple (inferred)"
  },
  {
    "direction": "u",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_behind.heavy.up",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "inferred-mirror, unconfirmed",
    "wh_buttons": [
      "RP2",
      "RK4"
    ],
    "wh_display_input": "u+RP2+RK4",
    "wh_input": "u+RP2+RK4",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Heavy + Up (behind, via reposition)",
    "wwe_subcategory": "Behind Grapple (inferred)"
  },
  {
    "direction": "d",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_behind.heavy.down",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "inferred-mirror, unconfirmed",
    "wh_buttons": [
      "RP2",
      "RK4"
    ],
    "wh_display_input": "d+RP2+RK4",
    "wh_input": "d+RP2+RK4",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Heavy + Down (behind, via reposition)",
    "wwe_subcategory": "Behind Grapple (inferred)"
  },
  {
    "direction": "b",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_behind.heavy.left",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "inferred-mirror, unconfirmed",
    "wh_buttons": [
      "RP2",
      "RK4"
    ],
    "wh_display_input": "b+RP2+RK4",
    "wh_input": "b+RP2+RK4",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Heavy + Left (behind, via reposition)",
    "wwe_subcategory": "Behind Grapple (inferred)"
  },
  {
    "direction": "f",
    "kind": "grapple",
    "move_id": null,
    "slot_id": "standing_grapple_behind.heavy.right",
    "source_urls": [
      "https://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-controls-tips-and-tricks-for-beginner-players"
    ],
    "status": "inferred-mirror, unconfirmed",
    "wh_buttons": [
      "RP2",
      "RK4"
    ],
    "wh_display_input": "f+RP2+RK4",
    "wh_input": "f+RP2+RK4",
    "wwe_category": "Standing",
    "wwe_input": "Grab + Heavy + Right (behind, via reposition)",
    "wwe_subcategory": "Behind Grapple (inferred)"
  }
];
