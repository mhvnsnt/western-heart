# Western Heart Moveset JSON Schema — v2 (moveset-editor contract)

**Owner rule:** WWE = the editor UX. Tekken = the content and the fighting.
**Owner rule:** wrestling-game moves may enter the library, but every one is wired
to Tekken inputs (1/2/3/4), Tekken notation, Tekken moveset structure.

This document is the data contract between **Lane F (moveset data)** and
**Lane H (moveset editor, r2/creation-suite)**. The editor reads
`game/assets/movesets/{fighter_id}.json` directly — field names below are the
agreement. Additive changes only; never rename/remove a v1 field.

## Top-level fields

| Field | Type | Notes |
|---|---|---|
| `fighter` | string | fighter id, matches filename |
| `display` | string | display name |
| `tekken_base` | string | Tekken/DOA/etc. character this moveset is built from |
| `proxy` | bool | **honest flag** — true while riding another bank's data |
| `proxy_note` | string\|null | why it's a proxy, in plain words |
| `schema_version` | int | 2 = editor-contract fields present |
| `moves` | object | notation → move entry (see below) |
| `strings` | array | multi-hit strings with component hits |
| `specials` | array | motion-input specials the input buffer resolves |
| `frame_convention` | string | how frames/damage were derived — honest provenance |
| `{game}_source` | string | per-game provenance: `t3_source`, `ttt2_source`, `t6_source`, `doa_source`, `ur_source`, `nomercy_source`, ... |

## Per-move fields

| Field | Type | Notes |
|---|---|---|
| `name` | string | move name, human readable |
| `input` | string | Tekken notation: `1`, `d/f+2`, `1,2`, `qcf+2`, `1+3` ... |
| `input_slots` | string[] | **(v2, editor)** Tekken input slots this move can occupy in the editor. First entry = canonical slot. Strings also list component inputs. |
| `move_class` | string | **(v2, editor)** `strike` \| `throw` \| `string` \| `special` — editor filter buckets |
| `anim_ref` | string | **(v2, editor)** preview-animation clip reference for live preview. Format `game:character:row-or-slug`, e.g. `t3:king:row:44`, `doa:bass:palm-jab` |
| `damage` | number | WH-scale damage (WH 100HP) |
| `startup` / `active` / `recovery` | number | seconds at 60fps |
| `limb` | string | `armL` `armR` `legL` `legR` |
| `heavy` | bool | heavy attack flag |
| `knock` | number | knockback tuning |
| `soulGain` | number | WH soul-meter tuning |
| `throw` / `isGrab` / `unblockable` | bool | throw flags where applicable |
| `{game}_source`, `{game}_row`, `{game}_command`, `{game}_move`, `{game}_input`, `{game}_damage` | — | per-game provenance, e.g. `t3_source`/`t3_row`/`t3_command`, `doa_move`/`doa_input`/`doa_damage` |
| `note` | string | honesty note where data is estimated |

## anim_ref registry

- `t3:{bank}:row:{n}` — Tekken 3 decoded motion bank row (`teardown/tekken3/movesets/`)
- `ttt2:{char}:row:{n}` — Tekken Tag Tournament 2 (when extraction lands)
- `t6:{char}:row:{n}` — Tekken 6 PSP (when decrypt6 lane lands DATA401)
- `doa:{char}:{slug}` — Dead or Alive movelist entry (BASS-MOVELIST.md et al.)
- `ur:{char}:{slug}` — Urban Reign (when PPK binary RE lands)
- `nomercy:{wrestler}:{slug}` — WWF No Mercy teardown clips
- `wh:{fighter}:{slug}` — Western Heart original / fallback

## Input mapping rule (federation)

Every non-Tekken move is mapped to Tekken limb inputs on ingest:
DOA `P`→`1`/`2`, `K`→`3`/`4`, `T`→`1+3`/`2+4`, numpad dirs→Tekken dirs
(`6`→`f`, `4`→`b`, `2`→`d`, `8`→`u`, `3`→`d/f`, `1`→`d/b`, `9`→`u/f`, `7`→`u/b`,
`236`→`qcf`, `214`→`qcb`, `41236`→`hcf`, `63214`→`hcb`, `66`→`f,f`).
No wrestling control schemes ever reach the player — Tekken inputs are the language.
