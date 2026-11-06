# Broken select cards, saved as the originals (2026-11-06)

Owner 2026-11-06: "you can save the ones the broken ones but you still need to go through and look and actually look
and see which all ones are currently broken ... the ones that are showing default currently need to be the fixed ones
... fix them all per character".

Every one of the 59 roster cards (`game/assets/portraits/<id>.png`) was looked at by eye on 2026-11-06. These are the
cards that were broken at that moment, byte-for-byte as they shipped, kept here before any replacement:

| card | what is wrong on the card | cause found |
|---|---|---|
| diablo | crumpled body, wings fill the frame | rig (audit: CONE FACE), stance pose breaks the mesh |
| waterfall | turned away from the camera | facing / rig (audit: CONE FACE + SEAM CRACKS) |
| burger | torn, spiky mesh | rig (audit: CONE FACE) |
| scimitar | torn shards | wrong model: owner 2026-11-06 "that not the correct scimitar glb model from my tripo imports" |
| dio | back of the head | facing: his front is 180 deg from the card camera in stance |
| cyborgx | camera inside a stretched white cape | rig (audit: CONE FACE) |
| slice | side / back view | facing: his front is 90 deg from the card camera in stance |
| charger | torn shards | rig (audit: CONE FACE) |
| deathfang | back view | facing: front 180 deg from the card camera in stance |
| koreshi | back of the spiked head | facing: front 180 deg from the card camera in stance |
| rave | huge white hood geometry | textures are bucket-served (white on a local tree) + rig (audit: CONE FACE) |
| chatur | untextured (white hair, grey body) | material / texture load |

Suspect on the same pass (kept for comparison): dxmmii-patchwork and bruno (floating hands), dorowani, michiko,
cainelias, tobi.

The seven fighters with no model at all (rin, byou, tou, sha, kai, retsu, gyou) show the shared MODEL PENDING
placeholder; they are tracked in `tools/portraits/KNOWN-PLACEHOLDERS.json` and clear when their models land.

Tool used to find each model's front: `tools/portraits/facing_probe.mjs` (four camera angles around the head, in stance
or `--rest`).
