# Urban Reign Texture Work — WORKLOG

**Task:** Texture all 49 Urban Reign characters (owner order 2026-10-19 ~02:49 CDT: "Get them all textured.")
**Lane:** a4f50eeb (texture), coordinating with 35e1f1b2 (render/geometry).

## Findings

### Where character textures live
- Character textures are **NOT in the repo in decoded form**. They are embedded in the char PPKs (`teardown/urban-reign/ppks/chars/char001–072.ppk`) in **Namco's proprietary inline format**.
- **No TIM2 signatures** in char001.ppk (scanned full file, 0 hits).
- **VGS decoded PNGs are UI screens only** (`teardown/urban-reign/vgs/decoded/` — title, menus, test stages). NOT character textures. (VGS-FORMAT.md documents the UI screen container.)
- **AFS map has no texture archives** — searched 2,431 DVD000 entries for tex/chara/skin/face/cloth: zero texture archives. Only `data/kageTest/vgs/*` test files.
- **dvd000-contents.txt**: zero hits for tex/tim2/tm2.

### PPK chunk probe (char001.ppk, 776,960 bytes)
Unparsed "non-float content" chunks tested for image-like structure:
| Chunk | Offset | Size | Entropy | H-autocorr | Verdict |
|---|---|---|---|---|---|
| 0x8001 | 0x2971 | 16,143 | 5.80 | 0.331 | Structured binary (vertical stripe pattern when rendered as 128x128 — tables/indices, NOT an image) |
| 0xae00 | 0x17d | 2,258 | 2.08 | 0.070 | Low-entropy structured data |
| 0x865 | 0x8001 | 2,935 | 6.18 | 0.315 | Structured binary |
| 0xa800 | 0xbcd | 7,588 | 3.79 | 0.399 | Mostly zeros, sparse data |

Rendered as raw grayscale: no recognizable image content. Texture pixel data is either compressed, swizzled beyond trivial detection, or in chunks not yet identified. **Full PPK texture-chunk decode remains open RE work** (multi-day, per PPK-FORMAT.md).

### UVs are real
`char001_uv.obj`: 3,576 vt entries (matches vertex count), u in [-0.99, 1.00], v in [-0.00, 2.01]. UV mapping exists — only the pixel data is missing.

### External texture source found
- **urban-reign-redux** (Jasonafex, community mod): v0.4 includes **"167 matching replacement textures"** in PCSX2 format (dumped PNGs — the actual in-game textures as rendered).
- Google Drive: https://drive.google.com/file/d/127deHyx4wlYcyniWvTe1pl8oEXROJMxh/view (1.75GB ZIP: ISO + textures + patches).
- **urban-reign-recomp** (thiagordsfx): static recompilation project — deep RE of the game's rendering, but intercepts textures at render time (no file-format decode docs for textures).

### Plan
1. Download Redux 0.4 pack → extract the 167 PCSX2 texture PNGs.
2. Identify character textures by visual inspection (own-eyes).
3. Map textures to the 49 characters (via UV layout + visual matching).
4. Build textured GLBs (embed PNGs, wire existing UVs).
5. Render textured front T-pose views, own-eyes verify each.
6. Land via git-data API: textured models + renders, branch → PR → merge.

## Status
- [x] Repo survey complete (no decoded character textures anywhere)
- [x] PPK chunk probe complete (no trivially-decodable texture data)
- [x] External source identified (Redux 167-texture pack)
- [ ] Redux pack downloading (1.75GB, in progress)
- [ ] Texture identification + character mapping
- [ ] Textured GLB builds (49)
- [ ] Textured renders + own-eyes verification
- [ ] PR → merge

## Update: Redux pack blocked, PPK texture format not cracked

**Redux 0.4 texture pack (Google Drive):** Rate-limited — "Too many users have viewed or downloaded this file recently." Cannot download via curl or gdown. The 167 PCSX2 replacement textures remain the best-known source of real character textures, but require browser access or waiting for the rate limit to clear (up to 24h).

**PPK texture RE:** Probed char001.ppk thoroughly:
- No TIM2 signatures (0 hits in 776,960 bytes)
- No texture/material name strings (8054 printable runs are binary garbage)
- Unparsed chunks rendered as raw images show structured binary data, not images
- Autocorrelation 0.07–0.40 (too low for raw pixel data)
- Textures are referenced by ID, not name; pixel data is in unknown Namco inline format

**Conclusion:** Real character textures cannot be extracted with current tooling. Two paths forward:
1. **Redux pack** (167 real PCSX2 textures) — retry download when Drive rate limit clears, or via browser lane
2. **PPK texture format RE** — multi-day binary RE to decode Namco's inline texture chunks (docs mark this "open work")

**NOT done:** Faking textures. No procedural/generated textures were created — the owner asked for the real game textures, and shipping fake ones would violate the honest-flags standard.
