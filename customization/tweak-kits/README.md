# Tweak kits — crew-staged starting points for the suite round trip

A tweak kit is what the crew stages so the user always starts from latest.
The user opens it live in the suite:

`game/customization-harness.html?tweak=<kit-id>&p1=<fighter>&demo=1`

…tweaks the flagged parts with the fix panel, hits **EXPORT TWEAK PATCH**,
and sends the downloaded JSON back in chat. The coordinator applies it with
`tools/customization/import_tweak_patch.py`.

The ONE patch format is specified in `customization/TWEAK-PATCH-SPEC.md`
(versioned `wh-tweak-patch`, self-describing, strictly validated).

## Kit file format (`wh-tweak-kit` v1)

`<kit-id>.json` next to this README:

- `id`, `fighter` (roster id), `attire`, `status` (`staged` / `staged-for-proof` / `applied`), `notes`
- `flagged_parts`: the 8 part groups the crew flagged
  (`head`, `torso`, `upper_arms`, `forearms`, `hands`, `thighs`, `shins`, `feet`)
- `part_map`: per-group bone/mesh name substrings (case-insensitive) used to
  find the part targets on the fighter's model. Omit a group to use the
  panel's built-in Mixamo-style defaults.
- `adjustments`: the crew's starting values per group
  (`rotation_deg`, `flip`, `offset`, `scale`, `note`). Usually all-zero;
  the suite loads these and the user tweaks from there.
- `history`: appended by the importer every time a user patch is applied.

## Applied records

`customization/tweak-kits/<fighter>/applied/<kit>-<timestamp>-<sha>.applied.json`
— the canonical record of every user patch the importer accepted
(patch + sha256 + validation report). The rig/model-fix pipeline reads the
kit's `adjustments` as its input spec; the applied records are the audit trail.

## Staging a new kit

1. Copy an existing kit, change `id`/`fighter`/`notes`/`flagged_parts`/`part_map`.
2. Keep `adjustments` empty (or set the crew's known-good starting values).
3. Commit on a branch, PR, merge — it goes live with the Pages build, and the
   `?tweak=<kit-id>` URL works immediately after.
