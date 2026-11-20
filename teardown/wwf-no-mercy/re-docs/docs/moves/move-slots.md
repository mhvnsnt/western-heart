# Move Slots

## Overview

A **move slot** is a named input combination available to every wrestler, organized by position and context. Every wrestler has the same set of slots — what differs between wrestlers is which move from the move database is assigned to each slot.

The full slot system is organized into the following categories:

| Category | Description |
|---|---|
| Grappling | Front and back grapples, weak and strong, plus finisher slots |
| Standing | Strikes, running attacks, counter attacks, and movement |
| Ground | Submissions and strikes against downed opponents |
| Turnbuckle | Corner grapples, tree-of-woe attacks, and flying attacks |
| Ringside | Attacks and grapples at the ropes and to the outside |
| Apron | Attacks and grapples from the ring apron |
| Irish Whip | Follow-up moves after whipping an opponent into the ropes |
| Taunt | Standing, ducking, corner, turnbuckle, celebration, and entryway taunts |
| Double-Team | Co-op grapples and flying attacks with a partner |

---

## Slot Counts Quick Reference

| Position | Grapple Type | Move Slots | Finisher Slot |
|---|---|---|---|
| Front | Weak Grapple | 8 | — |
| Front | Strong Grapple | 8 | 1 |
| Back | Weak Grapple | 4 | — |
| Back | Strong Grapple | 4 | 1 |
| Front Turnbuckle | Weak Grapple | 2 | — |
| Front Turnbuckle | Strong Grapple | 2 | 1 |
| Back Turnbuckle | Weak Grapple | 2 | — |
| Back Turnbuckle | Strong Grapple | 2 | 1 |

---

## Input → Slot Mapping

### Grappling

#### Front Weak Grapple (Tap A)
**Opponent State**: Standing facing player  
**Setup**: Tap A in front of standing opponent

| Input | Move Slot |
|---|---|
| A | Front Weak Grapple Slot 1 |
| ←/→ + A | Front Weak Grapple Slot 2 |
| ↑ + A | Front Weak Grapple Slot 3 |
| ↓ + A | Front Weak Grapple Slot 4 |
| B | Front Weak Grapple Slot 5 |
| ←/→ + B | Front Weak Grapple Slot 6 |
| ↑ + B | Front Weak Grapple Slot 7 |
| ↓ + B | Front Weak Grapple Slot 8 |

#### Front Strong Grapple (Hold A)
**Opponent State**: Standing facing player  
**Setup**: Hold A in front of standing opponent

| Input | Move Slot |
|---|---|
| A | Front Strong Grapple Slot 1 |
| ←/→ + A | Front Strong Grapple Slot 2 |
| ↑ + A | Front Strong Grapple Slot 3 |
| ↓ + A | Front Strong Grapple Slot 4 |
| B | Front Strong Grapple Slot 5 |
| ←/→ + B | Front Strong Grapple Slot 6 |
| ↑ + B | Front Strong Grapple Slot 7 |
| ↓ + B | Front Strong Grapple Slot 8 |
| Control Stick | Front Finisher Slot |

#### Back Weak Grapple (Tap A)
**Opponent State**: Standing facing away  
**Setup**: Tap A when behind a standing opponent

| Input | Move Slot |
|---|---|
| A | Back Weak Grapple Slot 1 |
| ←/→/↑/↓ + A | Back Weak Grapple Slot 2 |
| B | Back Weak Grapple Slot 3 |
| ←/→/↑/↓ + B | Back Weak Grapple Slot 4 |

#### Back Strong Grapple (Hold A)
**Opponent State**: Standing facing away  
**Setup**: Hold A when behind a standing opponent

| Input | Move Slot |
|---|---|
| A | Back Strong Grapple Slot 1 |
| ←/→/↑/↓ + A | Back Strong Grapple Slot 2 |
| B | Back Strong Grapple Slot 3 |
| ←/→/↑/↓ + B | Back Strong Grapple Slot 4 |
| Control Stick | Back Finisher Slot |

#### Reversals
**Opponent State**: Initiating a grapple

| Move Slot |
|---|
| Back Weak Grapple Counter Slot |
| Back Strong Grapple Counter Slot |

---

### Standing

#### Weak Arm Strike
**Opponent State**: Standing facing player or away  
**Setup**: Standing close to opponent

| Input | Move Slot |
|---|---|
| Tap B | Weak Arm Strike Slot 1 |
| ←/→/↑/↓ + Tap B | Weak Arm Strike Slot 2 |

#### Weak Leg Strike
**Opponent State**: Standing facing player or away  
**Setup**: Standing less-close to opponent

| Input | Move Slot |
|---|---|
| Tap B | Weak Leg Strike Slot 1 |
| ←/→/↑/↓ + Tap B | Weak Leg Strike Slot 2 |

#### Strong Strike
**Opponent State**: Standing facing player or away  
**Setup**: Stand near opponent

| Input | Move Slot |
|---|---|
| Hold B | Strong Strike Slot 1 |
| ←/→/↑/↓ + Hold B | Strong Strike Slot 2 |
| A + B | Strong Strike Slot 3 |

#### Ducking Attack
**Setup**: Hold R when getting up

| Input | Move Slot |
|---|---|
| B | Ducking Attack Slot |

#### Counter Punch
**Opponent State**: Throwing a punch  
**Setup**: Time the button press exactly

| Input | Move Slot |
|---|---|
| R | Counter Punch Slot |
| R (with Special) | Special Counter Punch Slot |

#### Counter Kick

| Input | Move Slot |
|---|---|
| A | Counter Kick Slot 1 |
| B | Counter Kick Slot 2 |

#### Walking

| Input | Move Slot |
|---|---|
| ←/→/↑/↓ | Walking Style Slot |

#### Running Attack
**Opponent State**: Standing  
**Setup**: Press C-Down to run, then press attack buttons

| Input | Move Slot |
|---|---|
| Run + B | Weak Running Attack Slot 1 |
| Run + A + B | Weak Running Attack Slot 2 |
| ←/→/↑/↓ + Run + B | Strong Running Attack Slot 1 |
| ←/→/↑/↓ + Run + A + B | Strong Running Attack Slot 2 |

#### Running Grapple
**Opponent State**: Standing  
**Setup**: Press C-Down to run, then press A when close

| Input | Move Slot |
|---|---|
| Run + A (to front of opponent) | Running Front Grapple Slot |
| Run + A (to back of opponent) | Running Back Grapple Slot |

#### Running Ground Attack
**Opponent State**: On mat (facing up, down, or sitting)  
**Setup**: Press C-Down to run, then press B when near downed opponent

| Input | Move Slot |
|---|---|
| Run + B (opponent facing up) | Facing-Up Running Ground Attack Slot |
| Run + B (opponent facing down) | Facing-Down Running Ground Attack Slot |
| Run + B (opponent sitting up) | Sitting-Up Running Ground Attack Slot |
| Run + B (opponent sitting down) | Sitting-Down Running Ground Attack Slot |

#### Evasion
**Setup**: Press C-Down to run, then press R

| Input | Move Slot |
|---|---|
| Run + R | Evasion Slot |

---

### Ground

#### Upper Body Submission
**Setup**: Stand near opponent's head and press A

| Input | Opponent State | Move Slot |
|---|---|---|
| A | Facing up | Facing-Up Upper Body Submission Slot |
| A | Facing down | Facing-Down Upper Body Submission Slot |
| A | Sitting up | Sitting-Up Upper Body Submission Slot |
| A | Sitting down | Sitting-Down Upper Body Submission Slot |
| A (with Special) | Facing up | Facing-Up Upper Body Finisher Slot |
| A (with Special) | Facing down | Facing-Down Upper Body Finisher Slot |

#### Lower Body Submission
**Setup**: Stand near opponent's feet and press A

| Input | Opponent State | Move Slot |
|---|---|---|
| A | Facing up | Facing-Up Lower Body Submission Slot |
| A | Facing down | Facing-Down Lower Body Submission Slot |
| A (with Special) | Facing up | Facing-Up Lower Body Finisher Slot |
| A (with Special) | Facing down | Facing-Down Lower Body Finisher Slot |

#### Ground Attack
**Setup**: Stand near any part of the opponent and press B

| Input | Opponent State | Move Slot |
|---|---|---|
| B | Facing up | Facing-Up Ground Attack Slot |
| B | Facing down | Facing-Down Ground Attack Slot |
| B | Sitting up | Sitting-Up Ground Attack Slot |
| B | Sitting down | Sitting-Down Ground Attack Slot |

---

### Turnbuckle

#### Turnbuckle Attack
**Opponent State**: Standing in corner with back to turnbuckle  
**Setup**: Stand in front of opponent

| Input | Move Slot |
|---|---|
| B | Turnbuckle Attack Slot 1 |
| ←/→/↑/↓ + B | Turnbuckle Attack Slot 2 |
| Run + B | Running Turnbuckle Attack Slot 1 |
| Run + A + B | Running Turnbuckle Attack Slot 2 |

#### Corner Counter
**Opponent State**: Standing/running after Irish-whipping player towards turnbuckle  
**Setup**: While being Irish-whipped into turnbuckle

| Input | Move Slot |
|---|---|
| Rapidly tapping A/B/L/R | Corner Counter Slot |

#### Tree-of-Woe Attack
**Opponent State**: Hanging upside down in tree-of-woe position  
**Setup**: Irish-whip opponent into corner, initiate grapple, press L button

| Input | Move Slot |
|---|---|
| B | Tree-of-Woe Attack Slot 1 |
| ←/→/↑/↓ + B | Tree-of-Woe Attack Slot 2 |
| Run + B | Running Tree-of-Woe Attack Slot |

#### Front Turnbuckle Weak Grapple (Tap A)
**Opponent State**: Standing in corner with back to turnbuckle  
**Setup**: Initiate weak grapple to opponent in corner

| Input | Move Slot |
|---|---|
| A | Front Turnbuckle Weak Grapple Slot 1 |
| B | Front Turnbuckle Weak Grapple Slot 2 |

#### Front Turnbuckle Strong Grapple (Hold A)
**Opponent State**: Standing in corner with back to turnbuckle  
**Setup**: Initiate strong grapple to opponent in corner

| Input | Move Slot |
|---|---|
| A | Front Turnbuckle Strong Grapple Slot 1 |
| B | Front Turnbuckle Strong Grapple Slot 2 |
| Control Stick (with Special) | Front Turnbuckle Finisher Slot |

#### Back Turnbuckle Weak Grapple
**Opponent State**: Standing in corner facing turnbuckle  
**Setup**: Initiate weak grapple to opponent in corner, press C-Left to turn them around, then A to back-grapple

| Input | Move Slot |
|---|---|
| A | Back Turnbuckle Weak Grapple Slot 1 |
| B | Back Turnbuckle Weak Grapple Slot 2 |

#### Back Turnbuckle Strong Grapple
**Opponent State**: Standing in corner facing turnbuckle  
**Setup**: Initiate strong grapple to opponent in corner, press C-Left to turn them around, then A to back-grapple

| Input | Move Slot |
|---|---|
| A | Back Turnbuckle Strong Grapple Slot 1 |
| B | Back Turnbuckle Strong Grapple Slot 2 |
| Control Stick (with Special) | Back Turnbuckle Finisher Slot |

#### Counter Grapple to Flying Attack
**Opponent State**: On top rope, facing player or away  
**Setup**: Press A as opponent prepares to fly

| Input | Opponent State | Move Slot |
|---|---|---|
| A | Opponent facing player | Front Flying Counter Grapple Slot |
| A | Opponent facing away | Back Flying Counter Grapple Slot |

#### Flying Attack
**Setup**: D-Pad plus run (C-Down) into turnbuckle, release C-Down to jump off

| Input | Opponent State | Move Slot |
|---|---|---|
| Release C-Down | Standing in ring | Standing Opponent Flying Attack Slot |
| Release C-Down | Standing outside ring | Standing Opponent Flying Attack to Outside Slot |
| Release C-Down (with Special) | Standing in or outside ring | Standing Opponent Flying Finisher Slot |
| Release C-Down | Laying down in ring | Laying Opponent Flying Attack Slot |
| Release C-Down | Laying down outside ring | Laying Opponent Flying Attack to Outside Slot |
| Release C-Down (with Special) | Laying down in or outside ring | Laying Opponent Flying Finisher Slot |
| A | Laying down inside ring near corner | Attack from Second Rope Slot |

#### Corner Taunt
**Setup**: Stand in corner pressing D-Pad towards turnbuckle plus Control Stick

| Input | Move Slot |
|---|---|
| Control Stick | Corner Taunt Slot |

#### Turnbuckle Taunt
**Setup**: From top turnbuckle, before releasing C-Down

| Input | Move Slot |
|---|---|
| Control Stick | Top Turnbuckle Taunt Slot |

---

### Ringside

#### Grapple to Apron
**Opponent State**: Standing on apron  
**Setup**: From inside ring

| Input | Move Slot |
|---|---|
| A or B (weak grapple) | Weak Grapple to Apron Slot |
| A or B (strong grapple) | Strong Grapple to Apron Slot |
| Control Stick (strong grapple) | Special Grapple to Apron Slot |

#### Counter Grapple from Apron
**Opponent State**: Grappling player in ring from ring apron  
**Setup**: Being grappled by opponent from apron

| Input | Move Slot |
|---|---|
| Rapidly tapping A and B | Counter Grapple from Apron Slot |

#### Rope Inside Attack
**Opponent State**: Laying on mat  
**Setup**: Standing between downed opponent and ring ropes

| Input | Move Slot |
|---|---|
| D-Pad + A | Rope Inside Attack Slot |

#### Flying Attack to Outside
**Opponent State**: Outside of ring

| Input | Setup | Move Slot |
|---|---|---|
| D-Pad + A | Standing inside ring up against ropes | Flying Attack to Outside Slot |
| A | Inside ring running towards ropes | Running Diving Attack Slot 1 |
| D-Pad + A | Inside ring running towards ropes | Running Diving Attack Slot 2 |

#### Running Diving Taunt
**Opponent State**: Outside of ring  
**Setup**: Inside ring running towards ring ropes

| Input | Move Slot |
|---|---|
| Control Stick | Running Diving Taunt Slot |

#### Rebound Flying Attack
**Opponent State**: Standing  
**Setup**: Inside ring running towards ring ropes

| Input | Move Slot |
|---|---|
| A | Rebound Flying Attack Slot |

---

### Apron

#### Apron Strike
**Setup**: Standing on ring apron

| Input | Opponent State | Move Slot |
|---|---|---|
| B | Standing inside ring | Apron Strike to Inside Slot |
| B | Standing outside ring | Apron Strike to Outside Slot |

#### Grapple from Apron
**Setup**: Standing on ring apron

| Input | Opponent State | Move Slot |
|---|---|---|
| A or B (weak grapple) | Standing inside ring near ropes | Weak Grapple from Apron Slot |
| A or B (strong grapple) | Standing inside ring near ropes | Strong Grapple from Apron Slot |
| Control Stick (strong grapple) | Standing inside ring near ropes | Finisher from Apron Slot |

#### Counter Grapple from Apron
**Opponent State**: Grappling player on apron while standing inside ring  
**Setup**: Being grappled by opponent while standing on ring apron

| Input | Move Slot |
|---|---|
| Rapidly tapping A and B | Counter Grapple from Apron Slot |

#### Flying Attack from Apron
**Setup**: Standing or running on ring apron

| Input | Opponent State | Move Slot |
|---|---|---|
| D-Pad + A | Outside of ring | Flying Attack from Apron Slot |
| A (running) | Outside of ring | Running Flying Attack from Apron Slot |

#### Flying Attack to Ring
**Setup**: Standing on ring apron

| Input | Opponent State | Move Slot |
|---|---|---|
| A | Standing inside ring | Flying Attack to Ring (Standing) Slot |
| A | Laying inside ring | Flying Attack to Ring (Laying) Slot |
| A (with Special) | Standing or laying inside ring | Flying Attack to Ring (Special) Slot |

#### Apron Taunt
**Setup**: Standing on ring apron

| Input | Move Slot |
|---|---|
| Control Stick | Apron Taunt Slot |

---

### Irish Whip

#### Irish Whip Attack
**Opponent State**: Running towards player

| Input | Move Slot |
|---|---|
| B | Irish Whip Attack Slot |

#### Irish Whip Grapple (from Weak Grapple)
**Opponent State**: Irish-whipped from weak grapple, running towards player

| Input | Move Slot |
|---|---|
| Tap A | Weak Irish-Whip Grapple Slot 1 |
| Hold A | Weak Irish-Whip Grapple Slot 2 |

#### Irish Whip Grapple (from Strong Grapple)
**Opponent State**: Irish-whipped from strong grapple, running towards player

| Input | Move Slot |
|---|---|
| Tap A | Strong Irish-Whip Grapple Slot 1 |
| Hold A | Strong Irish-Whip Grapple Slot 2 |
| Control Stick | Irish-Whip Finisher Slot |

---

### Taunt

#### Standing Taunt

| Input | Move Slot |
|---|---|
| Control Stick Up | Standing Taunt Slot 1 |
| Control Stick Left | Standing Taunt Slot 2 |
| Control Stick Right | Standing Taunt Slot 3 |

#### Special Taunt
**Setup**: Standing, has Special

| Input | Move Slot |
|---|---|
| Control Stick | Special Taunt Slot |

#### Ducking Taunt

| Input | Move Slot |
|---|---|
| Control Stick Down | Ducking Taunt Slot |

#### Celebration Taunt
**Setup**: Win match

| Trigger | Move Slot |
|---|---|
| Automatic | Celebration Taunt Slot |

#### Entry Way Taunt
**Setup**: Player's character making way to ring

| Trigger | Move Slot |
|---|---|
| Automatic | Entry Way Taunt Slot |

---

### Double-Team

#### Standing Double-Team Grapple
**Opponent State**: Standing  
**Setup**: Player and another character grapple opponent simultaneously

| Input | Position | Move Slot |
|---|---|---|
| A | Front | Front Double-Team Grapple Slot |
| A | Back | Back Double-Team Grapple Slot |
| A | Sandwich | Sandwich Double-Team Grapple Slot |

#### Running Double-Team Grapple
**Opponent State**: Running towards player and another opponent

| Input | Move Slot |
|---|---|
| A | Running Double-Team Grapple Slot |

#### Double-Team Flying Attack
**Opponent State**: Held up on the shoulders of an opponent  
**Setup**: Grapple and C-Up to hold opponent on shoulders, then execute flying attack

| Setup | Move Slot |
|---|---|
| From top rope into ring | Double-Team Flying Attack (Top Rope) Slot |
| From top rope to outside | Double-Team Flying Attack (Top Rope to Outside) Slot |
| From apron | Double-Team Flying Attack (Apron) Slot |

---

## JSON Reference

The following JSON represents the complete slot structure as used by the engine. This mirrors the tables above and serves as a preview of `data/schemas/move-slots.json`.

```json
{
  "grappling": {
    "frontGrapple": {
      "frontWeakGrapple": {
        "opponentState": "Standing facing player",
        "setup": "Tap A in front of standing opponent",
        "slots": {
          "A": "frontWeakGrappleSlot1",
          "leftRight+A": "frontWeakGrappleSlot2",
          "up+A": "frontWeakGrappleSlot3",
          "down+A": "frontWeakGrappleSlot4",
          "B": "frontWeakGrappleSlot5",
          "leftRight+B": "frontWeakGrappleSlot6",
          "up+B": "frontWeakGrappleSlot7",
          "down+B": "frontWeakGrappleSlot8"
        }
      },
      "frontStrongGrapple": {
        "opponentState": "Standing facing player",
        "setup": "Hold A in front of standing opponent",
        "slots": {
          "A": "frontStrongGrappleSlot1",
          "leftRight+A": "frontStrongGrappleSlot2",
          "up+A": "frontStrongGrappleSlot3",
          "down+A": "frontStrongGrappleSlot4",
          "B": "frontStrongGrappleSlot5",
          "leftRight+B": "frontStrongGrappleSlot6",
          "up+B": "frontStrongGrappleSlot7",
          "down+B": "frontStrongGrappleSlot8",
          "controlStick": "frontFinisherSlot"
        }
      }
    },
    "backGrapple": {
      "backWeakGrapple": {
        "opponentState": "Standing facing away",
        "setup": "Tap A when behind a standing opponent",
        "slots": {
          "A": "backWeakGrappleSlot1",
          "anyDirection+A": "backWeakGrappleSlot2",
          "B": "backWeakGrappleSlot3",
          "anyDirection+B": "backWeakGrappleSlot4"
        }
      },
      "backStrongGrapple": {
        "opponentState": "Standing facing away",
        "setup": "Hold A when behind a standing opponent",
        "slots": {
          "A": "backStrongGrappleSlot1",
          "anyDirection+A": "backStrongGrappleSlot2",
          "B": "backStrongGrappleSlot3",
          "anyDirection+B": "backStrongGrappleSlot4",
          "controlStick": "backFinisherSlot"
        }
      }
    },
    "reversals": {
      "slots": [
        "backWeakGrappleCounterSlot",
        "backStrongGrappleCounterSlot"
      ]
    }
  }
}
```

> The full JSON for all categories follows the same pattern. See `data/schemas/move-slots.json` for the complete schema.

---

## Related

- `data/moves/move-database.md` — Master list of all moves eligible for each slot
- `data/schemas/move-slots.json` — JSON schema for the slot system structure
- `docs/mechanics/GRAPPLING-SYSTEM.md` — Explanation of how the grappling system works
- `assets/characters/{character}/moves.json` — Per-character move assignments
