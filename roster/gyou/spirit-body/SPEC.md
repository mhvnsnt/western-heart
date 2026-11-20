# Gyou Spirit Body — Spec (archive lane, future rig/anim work)

**Status:** ARCHIVED ONLY. Unrigged static source; NOT wired into MODEL_URLS.
See `MANIFEST.md` in this folder for byte-verification details.

## Canon (user decision, 2026-10-22)

Gyou is one of the two unvesseled Nine Souls — a selectable **spirit fighter**.
Canon name: **Flame Lord (Flaming Angel)**.

## Spirit-float behavior (future anim lane — do NOT build yet)

- Gyou's spirit floats **behind** his spirit body — same structural setup as Zen's spirit-behind-body rig.
- It moves **more aggressively and sporadically** than Zen's spirit does behind his spirit body.
- Zen = calmer, steadier drift. Gyou = aggressive, erratic, sporadic motion.
- Anim lane must parameterize float "aggression/sporadicness" so Gyou's
  behavior is distinctly more violent than Zen's — different idle/hover
  behavior curves, not a copy of Zen's with different paint.

## Transformation roadmap (future lanes — documented, not built)

- **Various transformations**: Gyou has multiple transformation states.
- **Giant Susanoo form**: a giant Susanoo-style form with **different levels
  and transformations** — a tiered transformation ladder (multiple levels),
  not a single one-off form.
- Susanoo levels stack/escalate; each level is a distinct transformation.

## Lane notes for whoever picks this up

- Archive source lives in `source/` in this folder — byte-identical to the
  Tripo intake, restore point tagged `gyou-spirit-body-original`.
- Rig lane: rig like other Tripo intakes (Blender + GameRig pipeline) when
  scheduled; this model currently has no rig.
- Float-motion lane: read this spec — aggressive/sporadic Gyou float behind
  the spirit body, distinct from Zen's.
- Transformation lane: Susanoo level ladder design belongs to the owner;
  do not invent levels without owner input.
