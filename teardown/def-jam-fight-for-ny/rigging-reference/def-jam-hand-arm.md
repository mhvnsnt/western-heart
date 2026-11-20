# Def Jam Fight For NY (EA Chicago / AKI lineage) — hand/arm reference

Source: teardown/def-jam-fight-for-ny/ANIMATION-FINDINGS.md.

## Findings

- ASSETS/AKI_CFG.XML ships on disc with `<hands_animation>` toggle — the AKI
  grappling core (with its hand-animation layer) survived the EA Chicago rewrite.
- Character models: shared skeleton convention across all 78 fighters
  (all .o rigs ~5KB — same bone count, different proportions via the mesh).
- Animation: per-bone tracks in .orl files (12-21KB) after the `10 fb` header —
  bone map / track count / time base = open work.
- BASE00.VIV (2MB): base skeleton + shared animations.

## Takeaway

- FFNY confirms the design pattern the task wants: a shared hand-animation layer
  on top of a shared skeleton — but the bone map is not yet decoded, so no
  finger-bone names or joint angles are extractable today.
- 676 named moves in MOTION/MAIN_ALL.DAT (WAZA magic) — grapple move names for
  future hand-pose authoring.
