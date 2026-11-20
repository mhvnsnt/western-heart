# Jin Kazama — "Bloodline Ember" reskin library

Jin's **first custom look** (owner 2026-10-18). The Bloodline Soul's devil-gene
variant: dark base, ember-crimson flame motifs, devil-gene flame-tribal chest
marking, ashen skin.

## What's here

| File | What it is |
|---|---|
| `jin-torso-ember.png` | Chest with devil-gene flame marking (replaces `torso`, GLB image 14) |
| `jin-pantsfire-ember.png` | Flame decal, orange→ember crimson (replaces `pantsfire`, GLB image 34) |
| `jin-pants-ember.png` | Deepened black pants, ember warmth in weave (replaces `pants_tm`, GLB image 36) |
| `jin-obi-ember.png` | Obi cords gold→ember crimson (replaces `obi`, GLB image 32) |
| `*-original.png` | Byte-identical originals from `game/assets/models/jin.glb` — restore points |
| `MANIFEST.json` | Parameterized placements, GLB image indices, swap procedure |

## The reskinned model

`roster/jin/attires/bloodline-ember/jin-bloodline-ember.glb` — texture work only,
no rig/geometry changes. T-pose renders (own-eyes verified):
`roster/jin/jin-bloodline-ember-front.jpg`, `roster/jin/jin-bloodline-ember-side.jpg`.

## Eyes

Defaults untouched. The yellow tiger eye (owner's universal "I like" variant)
is a swappable option in `customization/parts/jin-eyes/` — tiger iris
composited onto Jin's native eye texture, drop-in 128x128 for `eye-iris`.
