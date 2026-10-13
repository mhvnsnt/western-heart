# Fighter Data Template

Each fighter is defined in a JSON file: `prototype/fighters/{id}.json`.

## Required Fields

```json
{
  "id": "fighter-id",
  "name": "DISPLAY NAME",
  "baseModel": "Tekken 7 character name (e.g. King)",
  "soul": "Which of the nine souls (Rin/Byou/Tou/Sha/Kai/Jin/Retsu/Zen/Gyou)",
  "style": "Fighting style description",
  "colors": {
    "primary": "#hex",
    "secondary": "#hex",
    "accent": "#hex"
  },
  "stats": {
    "speed": 4.6,
    "jump": 7.4,
    "power": 1.0,
    "defense": 1.0,
    "weight": 1.0
  },
  "bodyScale": 1.0,
  "model": "path/to/model.glb",
  "textures": "path/to/texture/dir/",
  "moveset": "path/to/moveset.json",
  "soulSurge": {
    "name": "Surge name",
    "effect": "Visual/mechanical description",
    "color": "#hex"
  },
  "attires": [
    { "id": "default", "name": "Default", "textures": "path/" },
    { "id": "alt1", "name": "Alt costume", "textures": "path/" }
  ]
}
```

## Stat Ranges

- **speed:** 3.5 (slow) – 6.0 (fast). Affects walk speed and dash.
- **jump:** 6.0 (low) – 8.5 (high). Affects jump height.
- **power:** 0.8 – 1.4. Damage multiplier.
- **defense:** 0.8 – 1.3. Damage reduction divisor.
- **weight:** 0.9 – 1.3. Affects knockback received and throw resistance.
- **bodyScale:** 0.9 – 1.15. Visual size multiplier.

## Archetypes

| Archetype | Speed | Power | Defense | Example |
|---|---|---|---|---|
| Balanced | 4.6 | 1.0 | 1.0 | Demonio |
| Rushdown | 5.5 | 0.9 | 0.9 | Saku Ra |
| Grappler | 4.0 | 1.3 | 1.2 | Pantera |
| Zoner | 4.2 | 1.1 | 0.95 | Phantom |
| Trickster | 5.0 | 0.85 | 0.9 | Zui |
