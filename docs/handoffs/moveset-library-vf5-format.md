# Moveset Library ↔ VF5 extraction — format contract

**To:** worker 45 (VF5 motion + moveset extraction)
**From:** worker 47 (moveset library system), 2026-10-22
**Note:** read-only alignment — not editing your lane's files. When your bank lands, the four pre-assembled Ashlane fighters resolve their base kits automatically.

## What the library expects

One JSON bank file, e.g. `game/data/moveset-library/banks/vf5.json`:

```json
{
  "bank": "vf5",
  "game": "virtua_fighter_5",
  "count": 1234,
  "moves": [ { /* entry per schema below */ } ]
}
```

Entry fields (full schema: `game/data/moveset-library/schema.json`):

| Field | Required | Format |
|---|---|---|
| `id` | yes | `vf5:<fighter>:<slug>` — fighter lowercase (`jeffry`, `wolf`, `el-blaze`, `lei-fei`), slug kebab-case from the VF movelist name, e.g. `vf5:el-blaze:hammerhead-kick` |
| `name` | yes | VF movelist name as-is |
| `name_status` | yes | `"VF5 movelist name"` (or `"auto-label — …"` if you synthesize one) |
| `source` | yes | `"vf5"` |
| `source_game_label` | yes | e.g. `"Virtua Fighter 5 (teardown extraction)"` |
| `source_character` | yes | display name, e.g. `"El Blaze"` |
| `anim_ref` | yes | `vf5:<fighter>:<slug>` (same as id) — later points at your motion clips |
| `type` | yes | one of `strike/grapple/throw/hold/aerial/counter/transition/stance/taunt/special` (see `axes.json`) |
| `position` | yes | one of `standing/crouching/grounded/back-turned/sidestep-left/sidestep-right/jumping/running/airborne/corner/apron/mounted` |
| `orientation` | yes | `forward/backward/left/right/up/down` |
| `input` | yes (null ok) | **Tekken notation** — federation rule: VF inputs converted (`P→1/2`, `K→3/4`, numpad `6→f` etc.; see `docs/movesets/MOVESET-SCHEMA.md` "Input mapping rule (federation)"). null if not yet mapped — assembly assigns slots |
| `input_slots` | yes | `[input]` or `[]` |
| `frames` | yes | `{startup, active, recovery, total}` in frames @60fps (null where unknown) |
| `damage` | yes | WH 100HP scale (null ok if unknown — flag estimated) |
| `damage_raw` | no | VF raw damage |
| `hit_level` | yes (null ok) | `high/mid/low/special-mid/throw/unblockable` |
| `properties` | yes | `[]` or axis vocab (`launch`, `knockdown`, `throw`, `counter-hit`, … — see `axes.json`) |
| `wh` | yes | `{knock, soulGain, heavy}` — defaults fine |
| `provenance` | yes | `{note, estimated[]}` — list every estimated field |

## Characters needed first (locked Ashlane mappings)

`jeffry` (Bannon), `wolf` (El Toro de Oro), `el-blaze` (Pablo), `lei-fei` (NPC Finxsse).

The four manifests in `game/data/movesets/` declare `"base": {"bank": "vf5", "character": "<name>", "status": "pending-bank"}`. The assembler (`game/js/moveset-library.js`) picks up every `vf5:<character>:*` entry automatically once the bank file exists — no manifest changes needed on your side. If your fighter slugs differ from the four names above, tell me and I'll update the manifests (my lane).

## Ingest hook

`tools/moveset-library/ingest.mjs` builds all banks reproducibly. If you want your extraction to feed it directly, add an `ingestVf5()` function following the existing pattern and register the bank in the `banks` array + `pending_banks` in the index builder. Or just drop `banks/vf5.json` in place — the loader reads the index registry, so either way works.
