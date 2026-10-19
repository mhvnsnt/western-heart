# Awa Pop Attire 2 + Thor Attire 2 wiring — worklog

## Lane
- Task: wire AWA POP Attire 2 + THOR Attire 2 (Tripo) in mhvnsnt/western-heart.
- Owner standing rule (restated 2026-10-19 ~02:13 CDT): Tripo links from him = pull + wire, no waiting for a separate "word."

## Sources (already pulled locally)
- AWA POP A2: `~/workspace/tripo-downloads/muscular_female_figure_3d_model.glb`
  - Tripo: https://studio.tripo3d.ai/3d-model/d71f4210-acff-4009-ba53-3813ea488a91 ("muscular female figure")
  - sha256: b127900dcb18dbc4f2fc9944181fdcc61686fdc59df0394b8c787502169917b2
  - size: 20,834,332 bytes
- THOR A2 "phantom mimic attire oni mask": `~/workspace/tripo-downloads/demon_costume_3d_model.glb`
  - Tripo: https://studio.tripo3d.ai/3d-model/c85dc47b-a3b4-41ad-b39c-86ea81b418cd ("demon costume")
  - sha256: 296a2a441e5f44acdbee1a82e1694f6aadbcf533cda5267ea4cc29f2472a8615
  - size: 24,147,212 bytes

## Layout
- `roster/awa-pop/attires/attire2/model.glb` (new attires/ subdir; A1 stays at `roster/awa-pop/awa-pop-attire-1.glb`)
- `roster/thor/attires/attire2/model.glb` (new attires/ subdir; A1 stays at `game/assets/models/thor.glb`)
- `docs/tpose-refs/awa-pop/a2_front.png`, `docs/tpose-refs/thor/a2_front.png` (locked-standard front renders)

## Render notes
- First parallel render attempt OOM-killed the Thor render (rc=137, memory contention with two blenders at once). Rerunning one at a time.
