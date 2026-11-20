# WWE 2K CAW Viewing/Editing Structure — 2026-10-19

**Purpose:** How WWE 2K19 stores, views, and edits created wrestlers — the structural knowledge
needed for the combined creation suite.
**Sources:** `pac/root/createmode*.pac` string tables (extracted), CAW-SUITE-BREAKDOWN.md (2026-10-13),
community modding knowledge, in-game editor structure.

## 1. Where CAW data lives

| Location | Contents | Status |
|----------|----------|--------|
| `pac/root/createmode.pac` (+p10/p20/p30) | Create-mode string tables: 5,581 move names, editor labels | ✅ EXTRACTED |
| `pac/edit/bbtemplate.pac` | Male/female base bodies + morph targets | 🔲 In 51GB pull |
| `pac/edit/default.pac` | Starter heads, bodies, attire | 🔲 In 51GB pull |
| `pac/edit/edit.pac` | Full customization part library | 🔲 In 51GB pull |
| `pac/edit/sample.pac` | Preset samples | 🔲 In 51GB pull |
| `pac/edit/ch/` | Head parts: masks, face accessories | 🔲 In 51GB pull |
| `pac/edit/body/` | Torso / limb meshes | 🔲 In 51GB pull |
| `pac/profile/profile_dat.pac` | Hometown, CAW IDs, slot data | 🔲 In 51GB pull |
| Save data (console/PC) | Created wrestler blobs | 🔲 Research queued |

Reference base models: slot 256 (male default CAW), slot 257 (female default CAW) — used in cutscenes.

## 2. The 8 editors (creation suite structure)

1. **Custom Superstar** — body, face, attire, moveset, entrance, victory, AI
2. **Custom Entrance** — choreography, lighting, pyro, Titantron video
3. **Custom Victory** — separate Face and Heel victory scenes
4. **Custom Moveset** — hundreds of moves across all positions (5,581 in 2K19)
5. **Custom Championship** — belt designer (strap → plate)
6. **Custom Arena** — arena designer
7. **Custom Show** — brand/show creator
8. **Custom Video / MITB** — Titantron editor, briefcase designer

## 3. Custom Superstar — data model

**Personal info:** name, nickname, hometown, gender, crowd reaction (Face/Heel/Tweener),
weight class, fighting style.

**Appearance — Head/Face:**
- Dozens of face morph sliders (jaw width, cheek depth, brow, nose, eyes, mouth, chin, ears)
- Skin tone, eye color, hair styles, facial hair, makeup
- Face paint / masks as layered parts

**Appearance — Body:**
- Body morph sliders (height, weight, muscle definition per region)
- Body hair, skin tone

**Attire — layered system:**
- Ordered layers per body region; each layer: part ID + color/pattern + material
- WWE 2K19 supports up to 8+ attire slots per wrestler (in-ring + entrance variants)
- Naming convention (from X-Packer/modding docs): `000` + model number + attire index;
  in-ring attires end in `2`, entrance attires end in `4` (e.g. `00013602`, `00013604`)

**Moveset:**
- Position-based slots (standing front/back, corner, apron, diving, grounded, etc.)
- Each slot ← one move from the 5,581 library
- AI fields per move: priority, repetition, timing (per Bannon's moveset_schema.json)

**Entrance / Victory:**
- Entrance pac per wrestler (`pac/evt/NNNNN_Name.pac`) — choreography + lighting + pyro
- Victory scenes separate for Face/Heel

**Profile & AI:**
- Fighting style, crowd reaction, AI tendencies

## 4. How the game loads a CAW (pipeline)

1. Read base body template (slot 256/257 morph target set)
2. Apply morph slider values (face + body)
3. Layer attire parts in order (each part: mesh + transform + material override)
4. Apply paint/tattoo decals
5: Load moveset (slot → move ID mapping)
6. Load entrance/victory pacs
7. Apply AI profile

## 5. Gaps (need the 51GB)

- Exact morph slider list + value ranges (in `bbtemplate.pac`)
- Part ID catalog (in `edit.pac`)
- Save-blob format for created wrestlers
- Material/shader parameters per part
