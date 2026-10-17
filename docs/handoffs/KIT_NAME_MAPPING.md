# Kit name mapping (canonical)

Owner decision, verbatim (2026-10-14):

> "Leave it alone, as long as all agents know what I'm talking about no matter what I call it."

**The rule:** every term in the table below names the SAME method. Nothing was
consolidated. Do **not** rename, merge, or "fix" the naming anywhere — including
the older `tracks/entrance-kit/` directory in money-machine-hq. Agents resolve
his wording to the method and paths below; they do not correct him.

## The terms → the one method

| What the owner says | What it is |
|---|---|
| entrance kit | The character entrance/promo/cutscene video production method |
| promo kit | same method |
| cutscene kit | same method |
| cutscenes kit | same method |
| promo and cutscenes kit | same method |
| promo-cinematic-kit | same method |
| promo pack kit | same method |
| entrance video method | same method |

The method: rig repair → animation → ring/arena + lighting → titantron name
plate/cards → beat-grid edit (every cut on the beat grid) → music → post →
proof. Full definition:
`docs/production-bible/ENTRANCE_VIDEO_METHOD.md` (Bannon; canonical copies also
in money-machine-hq, TRIPPEDD and God Molecule per that file's header).

## Canonical paths (verified 2026-10-15)

- **money-machine-hq `tracks/promo-cinematic-kit/`** — source of truth for the
  code (per ENTRANCE_VIDEO_METHOD.md): pipeline (`make kit`), shot-list
  templates, `tools/rerender_shot.py`, samples (`el-toro-de-oro`).
- **money-machine-hq `tracks/entrance-kit/`** — the older name for the same
  kit in the same repo. It exists. Do not rename it.
- **Bannon `docs/production-bible/ENTRANCE_VIDEO_METHOD.md`** — the production
  bible for the method.
- **Bannon `docs/promo/PROMO_PACK_KIT.md`** — the promo pack kit doc.
- **Bannon `tools/promo-pack-kit/`** — beat grid, 12 defect gates
  (`promo_gates.py`), side-by-side proof (`sbs_proof.py`), shot checklist.
- **Bannon `docs/PROMO-CINEMATIC-KIT.md`** — the promo-cinematic-kit doc.
- **Bannon `docs/UNIVERSAL_VIDEO_PRODUCTION_KIT.md`** — the universal video
  production kit doc.
- **western-heart `docs/agent-handoff/PRODUCERBOT_WORKFLOW.md` §8 ("Entrance
  videos")** — the entrance-video entry point for agents working in
  western-heart.

Reference pointer for Bannon readers:
`docs/production-bible/KIT_NAMES.md` points here (this file).

## The per-character entrance kits (where they actually live)

- Reported done 2026-10-08 (130 claimed). Verified 2026-10-15 via GitHub code
  search across the owner's repos: **ZERO hits for `entrance-kits`** — they
  never landed in any repo.
- They **do** exist locally: `~/workspace/bannon-video-pipe/entrance-kits/`
  (verified 2026-10-15): **32 ashlane + 63 bannon + 29 brutal-fist + 8
  concrete-dragon = 132 directories, 2.8 MB**. Convention (per that folder's
  README.md): one directory per character, `<Game>/<CharacterName>/`,
  containing a `<CHARACTER>_CHARACTER_CARD.md` built on the
  `stickup/STICKUP_CHARACTER_CARD.md` structure (billing block, bio, gimmick,
  gear, taunts, finishers, entrance music notes, height scale, video notes,
  50-second storyboard, script, beats, theme/environment, 15s mobile cut note).
- Follow-up still open: a lane needs to get these into a repo. Until then the
  local copy is the only copy. (If you check and they are not there, log
  MISSING honestly — do not claim they are.)

## What this is not

- `tools/rig_repair/` (Bannon, PR #77) is the weight-paint rig-repair pipeline
  — a different lane that feeds this method's model step, not the kit itself.
- "STICK UP" (no hyphen) is the owner's spelling rule for the character; the
  kit names above are the production method, not the character.

## History

- 2026-10-14: owner made the naming call quoted at the top; folded into the
  universal rig-pipeline coordinator brief (this doc is that brief's
  deliverable).
