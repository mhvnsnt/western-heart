# RE Battle Plan: Geo-Mod 2.0 Schemas + Nioh 2 Character Codes (2026-10-23)

**Owner directive (verbatim):** *"Find her way around that whole license code issue like bro it's a game that I own and we can reverse engineer the code and everything"*

**Note:** Full worker doc was lost to /tmp clearing. Key points reconstructed from worker summary below.

---

## A. Geo-Mod 2.0 schemas (RFG Re-Mars-tered, Steam app 667720)

**File layout:** `.vpp_pc` top-level archives → nested `.str2_pc` → `.peg_pc` textures, zone files, `.xtbl` tables.

**Tools (use existing, don't hand-roll):**
- **Gibbed.Volition** (open-source, proven on Volition pack family, ships in FactionFiles mod manager as `gibbed.volition.dll`) for pack extraction
- `strings`/`grep` triage on `.xtbl` tables (strength stats likely designer-tuned there)
- **RSL** (script loader, rsl.readthedocs.io) to damage specific layers in-game as ground truth for layer grouping

**Shard table RE:** Use the saintsrowmods.com Saints Row 3 mesh-format decode thread as Rosetta Stone (same Volition engine family). Hunt for trailing "destruction" chunk in building meshes: shard count, per-shard AABB, material index, break force, layer id.

**Validation:** Render shard AABBs — if they tile the building silhouette, the parse is correct. Correlate break forces against `.xtbl` material rows to fit the strength formula.

**Deliverable:** `geomod2.py` parser + rendered test vectors → PRIVATE repo.

## B. Nioh 2 character codes

**Known shape:** `S-` prefix on PC, two space-separated segments totaling ~13 chars (e.g. `icVfiL is8f3&i`). Custom alphabet (not base64; contains `?`, `%`, `=`). 13 chars ≈ 78 bits ≈ 10-byte blob.

**Differential RE procedure:**
1. Generate baseline codes
2. Sweep every slider min/mid/max, diff code positions → build position↔parameter map
3. Break obfuscation: custom alphabet → XOR key via known-plaintext on default character → checksum position via flip-and-reject test
4. Segment-swap test for independence
5. Cross-validate decoded bytes against unobfuscated save-file appearance struct
6. Build encoder/decoder; in-game round-trip screenshots as proof

**Shortcut:** Codes are shared publicly by the community — collect 20+ public codes and differential-analyze without needing game files.

**Deliverable:** encoder/decoder + byte maps → PRIVATE repo.

---

## Private vs public

**Private** (`mhvnsnt/game-reverse-engineering`): struct layouts, alphabets, XOR keys, byte maps, parsers, test vectors.
**Public** (`mhvnsnt/western-heart`): generic techniques only — differential sweep procedure, XOR detection via difference analysis, geometry-render validation.
