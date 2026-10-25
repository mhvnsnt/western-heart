# GPU / Blender lane jobs (Lane 8 — PREPARED, not run)

These jobs need a browser + GPU/Blender machine this lane cannot
operate. They are handed to the coordinator for browser execution.
Nothing in this directory claims a GPU run happened: a job counts
as run only when its report JSON carries real output + metrics.

## Jobs

- `tripo-autorig-job.py` — Tripo open-source auto-rigging +
  animatable generation on a WH model GLB. Needs Kaggle GPU.
- `mblab-blender-job.py` — MB-Lab / MPFB parametric-human
  generation for the creation suite. Needs Blender (installed
  in-notebook on Kaggle GPU, or any Blender-equipped machine).

## Coordinator browser delegation

- Kaggle notebook: https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
- Sign-in: Google tap-to-sign-in ONLY, account
  fmmg.mars@gmail.com (username marsfmmg). Standing sign-in rule
  (2026-10-24): NEVER ask for an email/password, NEVER request a
  secure-entry password card first. If Kaggle genuinely offered no
  Google SSO (it does — Google is the account on file), that exact
  finding would be reported instead of falling back to passwords.
- API keys: Tripo API keys, if ever needed, go via browser /
  Secure Vault. NEVER in chat, NEVER in files (this directory
  contains no keys, and no job here reads a key from a file).

## Done criteria (per job)

Report JSON with real metrics (rig type from
`game/js/rig-compat.js`, mapped/unmapped core roles, vertex
count, GPU used, wall time) AND zero unmapped core roles. A job
that only works on one model is NOT done.
