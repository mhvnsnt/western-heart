# Tekken Character Production Structure

**Source:** tekkenmods-docs (community reverse-engineering of Tekken 7/8),
on disk at `~/workspace/game-reverse-engineering/tekken7/tekkenmods-docs/`.
This is how Bandai Namco actually organizes character production data.

## Character ID Table

Every fighter has a numeric ID and a 3-letter abbreviation. Tekken 7: IDs 0–56,
51 playable. Example: `2 = KIN = King`, `6 = JIN = Jin`, `3 = YOS = Yoshimitsu`.

**Lesson for Western Heart:** every fighter gets a permanent numeric ID + short
code at the START of production. All files, docs, and data reference the code,
never just the name. (Names change; IDs don't.)

## Asset Naming Convention

File prefixes (from the developers' own naming):
| Prefix | Asset Type | Example use |
|--------|-----------|-------------|
| SK | Skeletal Mesh | Character body model |
| SKT | Skeleton | Rig structure |
| SM | Static Mesh | Props, non-deforming objects |
| BP | Blueprint | Behavior/visual scripting |
| PA | Physics Asset | Physics properties |
| CS | Character Set | Customization/appearance data |
| CCI | Customize Character Item | Clothing/accessory slot reference |
| CI | Character Item | Specific equippable item |
| EI | Extra Item (Sets) | Weapons/props (Negan's bat, Noctis' sword) |
| ECI / ACI | Effect / Aura Item | Visual effects attached to character |
| M / MI | Master Shader / Material Instance | Rendering materials |
| T | Texture | Diffuse, normal, etc. |

**Full filename breakdown** — `T_CH_kaz_bdu_1P_wind_coat_D`:
- `T` = texture
- `CH` = character asset
- `kaz` = Kazuya (character code)
- `bdu_1P_wind_coat` = the item (Player 1 wind coat)
- `D` = diffuse map

**Lesson for Western Heart:** adopt this naming scheme verbatim. Every asset is
self-describing: `T_CH_pantera_bdu_P1_black_D` tells you everything — texture,
character asset, Pantera, Player-1 attire, black variant, diffuse map. No
guessing, no README needed to identify a file.

## File Locations

- Character assets: `TekkenGame\Content\Characters`
- Stages: `TekkenGame\Content\Maps`

**Lesson:** one canonical directory per domain. Characters live in ONE place.
No scattered folders.

## Customization System

Tekken 7's customization is a DATA system, not a modeling task:
- `CS` (Character Set) = the customization/appearance data per fighter
- `CCI` (Customize Character Item) = a slot reference (e.g., "upper body slot 3")
- `CI` (Character Item) = the specific equippable item
- `EI` (Extra Item) = weapon/prop attachments

Attires are SWAPPED, not remodeled. The base body stays; items attach to slots.

**Lesson for Western Heart:** this is exactly the WWE-style attire system the
owner wants. Base model + item slots + swappable items. No Mercy taught us the
DESIGN of a creation suite; Tekken 7 shows the FILE STRUCTURE that ships it.

## Stage Structure

Stages use level-streaming suffixes — each concern is a separate file:
`debug`, `demo`, `edit` (editor map), `effect` (particles), `geom` (geometry),
`light`, `lightstatic` (baked), `mob` (crowds), `reload` (destructibles),
`sound`, `switch`, `WB` (wall brushes).

**Lesson:** separate concerns into separate files from day one. A stage is not
one file — it's a folder of concerns. Same for characters.
