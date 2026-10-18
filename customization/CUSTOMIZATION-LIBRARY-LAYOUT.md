# Customization Library — Canonical Layout

**Version:** 1.0 — 2026-10-18 (cust-wwe2k-inventory lane)
**Purpose:** the single reference every part lane (Tekken, Def Jam, WWE 2K, open-source,
owner-owned) follows when wiring a new part into `customization/`. No lane invents its own
folder scheme.

## 1. Directory layout (under `customization/`)

| Path | Contents |
|------|----------|
| `eye-library/` | Universal eye texture options (canonical eye home — see `customization/eye-library/`) |
| `decal-library/<character>/` | Character-bound decal PNGs composited into that character's UV maps (e.g. `decal-library/pantera/`) |
| `parts/<source-game>/` | Raw teardown extracts, organized by source game: `wmxix/`, `no-mercy/`, `doa/`, `superhero/`, `tekken/`, `defjam/`, `wwe2k/` (when it lands) |
| `parts/eyes/` | Eye textures pulled into parts form (mirrors `eye-library/` entries) |
| `parts/hair/<style>/` | Hair / beard / eyebrow / facial-hair MESH parts (rigged or with rig notes) |
| `parts/attire/<region>/<style>/` | Clothing pieces. Regions: `upper/`, `lower/`, `full/`, `headwear/`, `handwear/`, `footwear/` |
| `parts/accessories/<type>/<style>/` | Chains, jewelry, belts, glasses, masks. Types: `chains/`, `jewelry/`, `belts/`, `head/`, `other/` |
| `parts/decals/<style>/` | Character-agnostic decal sheets / logos (paint/face-paint/tattoo art) |
| `parts/tattoos/<style>/` | Tattoo sheets (layered, placeable, scalable, rotatable) |
| `parts/templates/` | FULL CHARACTER TEMPLATES — whole-character base models for created fighters to build on |
| `parts/base/` | Base bodies / morph references |
| `wwe2k-caw/` | WWE 2K CAW research, parts catalog, pull plan |
| `tools/` | Extraction/indexing scripts shared across lanes |

`PARTS-INDEX.json` at `parts/` root is the master machine-readable index over everything above.

## 2. Naming conventions

- **Folder ids:** lowercase, dashes, no spaces, no special chars:
  `toon-dread-ponytail`, `chain-gold-bannon`, `eye-yellow-tiger`.
- **Entry ids:** `<type>-<style>-<variant>`:
  `hair-toon-dread-ponytail`, `accessory-chain-bannon-rigged`.
- **Part types:** `eye`, `hair`, `beard`, `eyebrows`, `attire-upper`, `attire-lower`,
  `attire-full`, `headwear`, `handwear`, `footwear`, `accessory`, `decal`, `tattoo`,
  `template`, `body-morph`.
- **File names:** descriptive; keep source naming when it carries meaning
  (`King_Eye_D_yellow_tiger.png`), otherwise `<entry-id>.glb/.png`.
- **License files:** every open-source folder carries its license text:
  `LICENSE-<source>.txt` at the folder root.

## 3. MANIFEST format

Every part folder carries a `MANIFEST.json`. Fields follow the universal pattern set by
`decal-library/pantera/MANIFEST.json` and `eye-library/MANIFEST.json`:

```json
{
  "library": "hair library",
  "source": "Human-readable provenance: author, site, license, owner directive/date",
  "created": "2026-10-18",
  "entries": [
    {
      "id": "hair-toon-dread-ponytail",
      "name": "Toon dread ponytail (tiko479)",
      "type": "hair",
      "files": ["Toon Dread Ponytail.glb", "Dreads Multicolored_Bake1_pbr_diffuse.png"],
      "notes": "Static mesh — must be rigged to the head bone (see universal_format.rigging)"
    }
  ],
  "character_mappings": {
    "pantera": {
      "character": "Pantera (Western Heart roster/pantera, King-based)",
      "bone": "Head",
      "material": "...",
      "notes": "..."
    }
  },
  "universal_format": {
    "description": "...what an entry is and how to drop it onto any character...",
    "placement_fields": {
      "character": "character id",
      "bone": "bone name to attach/rig to",
      "material": "material name (for texture-swap parts)",
      "replaces_texture": "texture name in that character's GLB",
      "rect": "pixel rect to composite into (full replace if omitted)",
      "notes": "free text"
    }
  }
}
```

Rules:
- `entries[].id` is globally unique across the whole library.
- `character_mappings` is how a part becomes UNIVERSAL: one part folder, one entry,
  N character mappings. Add a mapping per character; never duplicate the part files.
- **Variants are never overwritten.** A new variant = a new entry + a new file.
  Old entries stay (options stack, WWE/Tekken-style).

## 4. Texture-swap parts vs mesh parts

- **Texture-swap parts** (eyes, decals, some tattoos): square/rect RGBA PNGs; mapping names
  `replaces_texture` + `material` + `rect`. Follow the eye-library pattern exactly.
- **Mesh parts** (hair, attire, accessories): GLB/glTF (preferred; embedded textures);
  mapping names `bone` (attach/rig target) + fit notes. If a part is not yet rigged,
  the entry `notes` MUST say what rigging it needs (static mesh → rig to head bone, etc.).

## 5. Workflow for new lanes

1. Put files in the right folder per §1 (new source game → `parts/<source-game>/`;
   new reusable style → `parts/<type>/<style>/`).
2. Write `MANIFEST.json` per §3. License text in the folder if open-source.
3. Add entries to `parts/PARTS-INDEX.json` (one record per entry id).
4. Update this doc only if the layout itself changed.
5. Worklog entry in `docs/WORKLOG.md`.
