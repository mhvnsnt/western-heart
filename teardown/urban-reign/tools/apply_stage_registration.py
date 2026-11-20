#!/usr/bin/env python3
"""Apply the UR stage registration to game/js/stages.js (follow-on 5).
Reads the measured color means from /var/tmp/ur-census/stage_export_report.json
and inserts: buildURStage (after buildNoMercy), the URBAN_REIGN defs block
(before the SUN RA def), 'urstage' in BUILDERS, 'URBAN REIGN' in STAGE_TIERS,
and a header-comment line. No other file is touched.
panoTint is #ffffff when the decoded vertex colors are real (nonwhite frac
> 0.5); otherwise the measured mean hex (flat tint over white verts).
"""
import json, sys
from pathlib import Path

REPO = Path("/var/tmp/wh-ur-stages")
STAGES = REPO / "game/js/stages.js"
REPORT = json.loads(Path("/var/tmp/ur-census/stage_export_report.json").read_text())

src = STAGES.read_text()

# 1. buildURStage after buildNoMercy (before the T7 GLB comment)
builder = '''
/* ---- URBAN REIGN: real decoded stage geometry (Lane 4 follow-ons) ----
   The 6 decodable stage PPKs (003/004/028/029/030/031) export their stage
   VMD through the Redux Editor's meshes.load to OBJ (game/assets/stages/ur/).
   Units are metres (world space) — NO scale, unlike the T3 (0.015) and
   No Mercy (0.012) shells. Vertex colors are the VMD's decoded colors;
   textures are NOT wired yet (no map — the follow-up adds the decoded
   texture atlas). stage020's VMD fails read_mesh in-VM and is NOT
   registered. See UR-STAGE-MISSION-DECODE.md. */
async function buildURStage(g, def, api) {
  const { updaters, skyTex, fog } = buildBase(g, def, api);
  try {
    const geo = await fetchStageOBJ(def.obj);
    const mat = new THREE.MeshBasicMaterial({
      vertexColors: !!geo.getAttribute('color'),
      color: _hex(def.panoTint),
      side: THREE.DoubleSide, fog: true,
    });
    const shell = new THREE.Mesh(geo, mat);
    g.add(shell);
  } catch (e) {
    console.warn(`[WH] stage ${def.id}: UR shell failed (${e.message}), palette backdrop only`);
  }
  const edge = new THREE.Mesh(new THREE.TorusGeometry(8.9, 0.08, 10, 48),
    new THREE.MeshBasicMaterial({ color: _hex(def.lighting.sun[0]) }));
  edge.rotation.x = Math.PI / 2; edge.position.y = 0.02; edge.userData.nearClip = true; g.add(edge);
  return { updaters, skyTex, fog };
}

'''
anchor = "/* ---- TEKKEN 7 GLB stage (Mishima Dojo): untextured rip, normals rebuilt ---- */"
assert src.count(anchor) == 1, "T7 GLB anchor not unique"
src = src.replace(anchor, builder + anchor, 1)

# 2. UR defs block before the SUN RA def
rows = []
for tag in ("stage003", "stage004", "stage028", "stage029", "stage030", "stage031"):
    r = REPORT[tag]
    tint = "#ffffff" if r["color_frac_nonwhite"] > 0.5 else r["color_mean_hex"]
    rows.append(f"  ['{tag}', 'UR Arena {tag[5:]}', {r['vertices']}, {r['triangles']}, '{tint}', '{r['color_mean_hex']}'],")
table = "\n".join(rows)
defs = f'''
/* ---------------- URBAN REIGN ARENAS (Lane 4 follow-ons, 2026-11-08) ----
   6 real arena shells from teardown/urban-reign/stages/ (stage003/004/028/
   029/030/031.ppk), decoded with the Redux Editor's meshes.load and exported
   to game/assets/stages/ur/stageNNN.obj (vertices + UVs + decoded vertex
   colors, metres). stage020.ppk is NOT here: its only VMD fails read_mesh
   (command-walk reads past EOF) in every in-VM reader — the named route is
   the Editor on Windows. Names are PROPOSED labels (the PPK ids) — Jay
   names these arenas; the measured source place per arena is in
   UR-STAGE-MISSION-DECODE.md, NOT in the game strings (UR stage names stay
   in the teardown). Textures are not wired yet (vertex colors only). */
const URBAN_REIGN = [
  // ppk, PROPOSED label, verts, tris, panoTint, measured mean vertex color
{table}
];
for (const [ppk, label, verts, tris, tint, meanHex] of URBAN_REIGN) {{
  STAGES.push({{
    id: `ur-${{ppk}}`,
    name: label,
    tier: 'URBAN REIGN',
    universe: 'Urban Reign (legacy)',
    element: 'Retro',
    description: `Real Urban Reign arena — decoded stage geometry (${{verts}} verts, ${{tris}} tris) from ${{ppk}}.ppk. PROPOSED name — Jay names this arena. Vertex colors only; textures not wired yet.`,
    dims: {{ width: 16.8, depth: 6.0, wallDistance: 8.4 }},
    spawns: {{ p1: -3.5, p2: 3.5 }},
    lighting: {{
      sky: [[0.0, '#0a0a18'], [0.55, '#1a2a3a'], [0.85, '#7ab0d0'], [1.0, '#0a0a18']],
      fog: ['#0a0a18', 22, 80],
      hemi: ['#8a8aa8', '#1a1420', 1.5],
      sun: ['#ffe0c0', 2.2, [-10, 8, 5]],
      rim: ['#ffe0c0', 0.6, [8, 6, -7]],
      fill: ['#ffe0c0', 0.8, [0, 4, 10]],
    }},
    floor: {{ kind: 'stone', tint: '#5a5a5a', repeat: 26, platformTint: '#5a5a5a', platformRepeat: 6 }},
    swatch: [meanHex, '#ffe0c0'],
    builder: 'urstage',
    obj: `assets/stages/ur/${{ppk}}.obj`,
    panoTint: tint,
    hidePlatform: true, // the decoded stage carries its own floor at y=0
  }});
}}

'''
anchor2 = "/* ---- SUN RĀ — THE STARING SKY (boss stage; Kevin's home base) ---- */"
assert src.count(anchor2) == 1, "SUN RA anchor not unique"
src = src.replace(anchor2, defs + anchor2, 1)

# 3. BUILDERS map
old_builders = "  sunra: buildSunRa, nomercy: buildNoMercy, t7glb: buildT7Glb,"
assert src.count(old_builders) == 1
src = src.replace(old_builders, old_builders + "\n  urstage: buildURStage,", 1)

# 4. STAGE_TIERS
old_tiers = "export const STAGE_TIERS = ['CANON LANDS', 'CAPE JONES', 'TEKKEN RETRO', 'WWF NO MERCY', 'WRESTLING', 'BOSS STAGES'];"
assert src.count(old_tiers) == 1
src = src.replace(old_tiers,
    "export const STAGE_TIERS = ['CANON LANDS', 'CAPE JONES', 'TEKKEN RETRO', 'WWF NO MERCY', 'WRESTLING', 'URBAN REIGN', 'BOSS STAGES'];", 1)

# 5. header comment
old_head = "   • Every stage: collision bounds (wallDistance), spawn points,\n     lighting rig, floor, backdrop. Builders return an update hook\n     for animated elements (flicker, drift, ripple)."
assert src.count(old_head) == 1
src = src.replace(old_head, old_head +
    "\n   • + 6 Urban Reign arenas from REAL decoded stage PPKs (Lane 4\n     follow-ons): game/assets/stages/ur/stageNNN.obj, builder 'urstage',\n     tier 'URBAN REIGN'. stage020 NOT registered (VMD undecodable in-VM).", 1)

STAGES.write_text(src)
print("stages.js updated; new lines:", len(src.splitlines()))
for tag in ("stage003", "stage004", "stage028", "stage029", "stage030", "stage031"):
    r = REPORT[tag]
    print(f"  {tag}: tint={'#ffffff' if r['color_frac_nonwhite'] > 0.5 else r['color_mean_hex']} mean={r['color_mean_hex']} nonwhite={r['color_frac_nonwhite']}")
