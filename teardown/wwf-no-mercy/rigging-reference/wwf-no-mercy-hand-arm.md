# WWF No Mercy (AKI engine, N64) — hand/arm reference

Source: teardown/wwf-no-mercy/AKI-TEKKEN3-RETARGET.md + tools/anim_extract.py.

## Rig: 19 x 1-DOF hinge joints, NO fingers

- The AKI animation format decodes to 19 PivotRotation joints (s8 rotation +
  12-bit pivot XZ). s8 rotation value == degrees (measured pelvis -39..121 deg).
- Joint list includes UpperRightArm/UpperLeftArm -> LowerRightArm/LowerLeftArm.
- **No finger or hand-detail joints.** Hands are mitten geometry; grapple hand
  shapes are baked into the move choreography at the wrist.
- Retarget to Tekken: AKI Upper+Lower arm average onto the Tekken shoulder/elbow
  joints (see AKI-TEKKEN3-RETARGET.md mapping table).

## Takeaway

- Same class as Tekken 3: wrist-only hand posing, no finger articulation.
- The ~1,360-clip AKI animation library is the grapple choreography source, not
  a hand-rig source.
