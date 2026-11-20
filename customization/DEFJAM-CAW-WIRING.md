# Def Jam CAW parts — catalog + suite wiring

## Source

`teardown/def-jam-fight-for-ny/` — Def Jam: Fight for NY (PS2) teardown.

| Artifact | Count | State |
|---|---|---|
| `customization/parts/defjam/PARTS-INDEX.json` | 22,360 parts (head 455, upper_body 14,430, lower_body 5,850, accessories 1,625) | PS2 `.o` (EAGL) — indexed, not web-renderable |
| `customization/parts-converted/defjam/CATALOG.json` | 2,624 conversion entries | converted via `customization/tools/convert_defjam_o.py` |
| `customization/parts-converted/defjam/**/*.glb` | 1,218 GLBs (+2,182 PNGs) | **POINTS topology, unproven vertex order** |

Honest state: the 1,218 GLBs are conversion output with POINTS
primitives — NOT clean render-ready meshes. Every Def Jam entry in
the suite ships `geometry_pending: true` until the mesh conversion
pass lands. The suite shows them as "conversion pending", never as
finished parts.

## Wiring (worker 33, fight-lab lane, 2026-10-22)

Coordinated with the WWE parts work (wmxix / no-mercy) — **no
duplication**: Def Jam is a new `defjam` library, ids namespaced
`defjam:…`, and the builder block is additive.

1. **`customization/PARTS-REGISTRY.json`** — new `defjam` entry in
   `libraries` (kind, manifest, note, part_class, path).
2. **`customization/build_suite_catalog.py`** — new source block §5:
   reads `parts-converted/defjam/CATALOG.json`, maps
   `head/upper_body/lower_body/accessories` to suite slots, marks
   `geometry_pending: True`, carries `converted_status`,
   `uv_status`, `topology_status` through.
3. **`customization/creation-suite-ui/data/parts-catalog.json`** —
   regenerated: +2,624 defjam entries (total 7,147), same sort key
   and entry shape as the builder.

## Suite slots

`head → head`, `upper_body → upper_body`, `lower_body → lower_body`,
`accessories → accessory` (T7 spine: 9 / 11 / 12; head has no T7 slot
in the current spine — sorts last, same as the builder produces).

## Rebuilding

Run `python3 customization/build_suite_catalog.py` from the repo root
on a machine with the full tree (this VM's python3 cannot write
files; the committed catalog was produced by the equivalent node
transform in `/tmp/flb/merge-defjam.mjs`).
