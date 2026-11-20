# Move-set editor (WWE 2K style, merged with Practice) — spec

Owner of the UI: **Repo Co Dev** (it lives in the creation suite). This is the spec + handoff; posted on agent-ops TAG-TEAM.md.

## Flow
1. Tap a fighter on the select grid (or in Create a Fighter) → **MOVE-SET** screen, full roster of slots.
2. Left column: categories (submenus). Middle: slots in that category. Right: move library browser filtered to what fits the slot, with a looping preview.
3. Assign = pick a move from the teardown library. Tekken-style slots also take an **input string** (e.g. `f,f+2`, `d/f+1,2`, `[6 5 4 1 2 6+LP]` motion inputs).
4. **Practice merge**: the editor is a panel over Practice mode. Edit a slot → it is live immediately in the running practice fight. Command list and input display (Tekken-style history column with frame counts) are always on; the dummy can record/playback.
5. Save per attire version (never overwrite): `roster/<id>/movesets/<attire>_vN.json`.

## Categories (from the WWE structure we tore down: `moveset-library/movesets/MOVE-SLOTS.json`)
grappling (front/back weak/strong, reversals) · standing (weak arm/leg, strong, ducking, counter punch/kick, running attack/grapple) · **tekken_striking** (jab strings, crouch dash, while rising, while running, throws, rage, stance transitions) · ground (upper/lower submission, ground attack, running ground attack) · turnbuckle (attack, tree of woe, front/back weak/strong, flying) · ringside_apron · irish_whip · taunt (standing, special, ducking, corner, top turnbuckle, apron, running/diving, celebration) · double_team (standing, running, flying).

## Slot data (grounded in the Tekken teardown)
The Tekken 3 move banks (`teardown/tekken3/movesets/moveset_<char>.json|csv`, e.g. King = 652 moves) give each move: `stream_frames`, `damage`, `attack_class`, `active_first/last`, `hit_freeze`, `stance_slot`, `heading_change`, `air_first/last`, `hold_frame`, and a **cancel list** of `inputs -> target move [frame window]` (e.g. `[6 5 4 1 2 6+LP](30f)->2824[1-255]` = motion input with 30f buffer, cancel window frames 1-255). The editor slot schema mirrors that:
```json
{ "slot": "tekken_striking.jab_strings.1", "input": "1,2,1", "move": "lib:king.t3.row1037",
  "anim": "moveset-library/animations/ANIMATION-INDEX.json#...", "startup": 10, "active": [10,12],
  "damage": 7, "hit": "high", "cancels": [{"input": "2", "to": "slot:...", "window": [12,20]}],
  "source": "teardown/tekken3 King row 1037", "third_party": true }
```
Rules: every move keeps its `source` and `third_party` flag (pre-sale replacement list, same as parts.json). Frame data shown in the command list comes from the bank, not typed by hand. WWE slots use the Lab animation index; Tekken slots use the bank rows + input strings. Validation: input string parses, cancel targets exist, active window inside stream_frames, no duplicate input in one stance.

## Practice integration
- Input display: last 20 inputs with frame gaps; highlight when a slot's input matched.
- Command list: generated from the current move-set file, grouped by the categories above.
- Live test: edit → hot-swap the move table in the running fight; dummy repeats last recording.
- Frame meter: startup/active/recovery bar from the bank fields.

## Handoff
Repo Co Dev builds the UI in the suite. Physics agent: none. Producerbot/Muse: data schema + library export (`moveset-library/movesets/*.json`). Claim on agent-ops before starting.
