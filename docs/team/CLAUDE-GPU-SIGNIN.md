# Claude GPU + Sign-In Handoff

**For: Claude Code (AI collaborator on Western Heart). This file is your sign-in map.**
**No passwords, tokens, keys, or codes are in this file — by design. You sign in yourself, with your own browser, using the accounts below. Never ask the user for a password, token, or code, and never ask them to set up "environment secrets" for you. If a sign-in needs a browser step, do it in the browser like DoggByte does.**

## The one rule for every sign-in

**Always use GitHub sign-in OR Google / Gmail sign-in (tap-to-sign-in). Never ask for an email/password first, never send a secure-entry password card first.** If a site genuinely offers NO GitHub/Google SSO after a thorough check (login page + sign-up flow), report that exact finding — do not silently fall back to password entry.

## Accounts (use these, sign in yourself)

- **GitHub: mhvnsnt** — GitHub OAuth. Used for: the western-heart repo, Netlify (via GitHub OAuth), GitHub Pages fallback.
- **Google / Gmail: fmmg.mars@gmail.com (username marsfmmg)** — Sign in with Google. Used for: Kaggle, Google Colab. No new sign-in or phone verification needed (account shows phone verified, 9-day streak, 42 notebooks, 14 datasets at last check).

## Kaggle GPU (primary GPU — already set up, session pattern)

- **Notebook:** https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
- **Accelerator:** GPU T4 x2 (Settings → Accelerator). P100 is NOT offered; options are None, GPU T4 x2, TPU v5e-8.
- **Quota:** 30 hrs/week GPU. Session counts while open — close it when idle, or hand it to the next job, never leave it burning quota for nothing.
- **Verified GPU proof (from a real run):** Driver 580.178.04, CUDA 13.0, 2x Tesla T4, torch 2.11.0+cu128, `torch.cuda.is_available()` True, CUDA matmul 4096x4096 in 0.083s.
- **Every GPU job must prove GPU first:** `nvidia-smi` + `torch.cuda.is_available()` True in the job output. A script that needs GPU must FAIL LOUDLY with no CUDA device — a CPU run must never silently pass as a GPU run. Record nvidia-smi output + wall time + output files for every job.
- **Pipeline, not one-offs:** jobs queue continuously — when one GPU job finishes, the next starts. Download outputs (MP3s, models, renders, manifests, verification files) and commit the real outputs to the repo via PR. Never claim a GPU job ran until real output + metrics exist.
- **Jobs already proven / queued:** Nosferatu 25-track cut (DONE — 25 tracks, 218.6s, zero errors); T3 animation batch classifier (all 22 bank packs, King row 38 must classify jumping); UniRig auto-rig (Cape Jones body); Real-ESRGAN texture batch; Blender EEVEE-GPU card renders; cuDF batch validation; Gang Beasts dump mining (stage inputs first).

## Google Colab (second GPU — backup / overflow)

- Signed in with the same Google account (fmmg.mars@gmail.com). New test notebook + GPU runtime option verified working (Tesla T4, 15GB GPU memory, driver 580.82.07, CUDA 13.0 at last check).
- Use Colab as backup/overflow when Kaggle quota runs low — don't stop, switch GPUs.

## Other sign-ins DoggByte already has working (same SSO rule)

- **Netlify (playable build host):** GitHub OAuth for mhvnsnt. Project western-heart, site **endearing-scone-b3d816**, URL **https://endearing-scone-b3d816.netlify.app/** — the game is at the site ROOT, NOT /game/ (publish dir = "game"). Production branch = gh-pages, no build command. Auto-deploys on gh-pages pushes.
- **Free Music Archive (FMA):** email/password ONLY — login and register pages were checked thoroughly, NO Google/GitHub SSO exists there. The owner's FMA account is verified and signed in via the browser's saved login. If you need FMA downloads, use the browser's saved-login flow — do NOT ask the user for the password, do NOT create a new account, do NOT re-register.
- **Steam:** website login only (saved login authorizes the Steam website, NOT depot downloads). DepotDownloader anonymous pull for Tekken 7 (app 389730) was denied. Do NOT solicit Steam credentials.

## Repo rules (you work in mhvnsnt/western-heart — follow these or your work gets reverted)

- **Feature branch + PR, NEVER push to main directly, NEVER force-push.**
- **Anti-clobber:** sync to latest main BEFORE starting file work and again BEFORE committing. Surgical edits only — never write a whole file when a targeted edit will do. Any diff deleting >20 lines must be intentional and called out in the PR body.
- **Merge clean green PRs only**, via the Git Data API 3-way merge tool (the merge REST endpoint 404s with the PAT, SSH is blocked). Never merge while CI checks are pending.
- **Instruction-gate PR body — EXACT headings:** `## Owner instruction (verbatim quote)`, `## Method the owner specified`, `## Method actually used`, `## Deviations (none / list, each with owner approval link)`, `## Proof (paths to files, frames, test output)`, `## Self-check: I verified the result against the literal instruction`. Gotchas: backticked strings must be FILE PATHS; when Deviations = none, "Method actually used" must normalize IDENTICALLY to "Method the owner specified"; self-check needs `- [x]`; deviations = exactly "None." when none. Never fabricate an approval link — if a deviation has no owner approval, leave it as pending and say so.
- **Deploy path:** merge to main → sync main→gh-pages → Netlify auto-deploys. Manual gh-pages deploys use the Git Data API from the LAST WORKING gh-pages tree, batches ~50 files. NEVER copy main's raw tree to gh-pages.
- **Verify by playing:** every fix/feature gets verified by actually playing the live build (phone portrait mode, like the owner on their phone — screenshot, look, scroll, THEN tap what's visible, never jump via selectors). Never claim "fixed" until it is on main, deployed, and played.
- **Team channel:** GitHub issue #866, prefix `[Muse]` / your own prefix. The GitHub comments API defaults to 30/page — always use `?per_page=100` or you silently miss the newest comments.
- **Button names in ALL conversation with the user:** LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4. The user sees LP/RP/LK/RK on screen, NOT 1/2/3/4.
- **Do the work right, not fast.** Map each move to its EXACT animation from the actual Tekken files, never a class-correct stand-in. A jumping punch is NOT a jab. Never call something "fixed" when it is only "less broken." Never guess — if the file doesn't contain it, it's UNMAPPED, never invented.
- **Ownership (user's word suffices, never demand proof):** the user OWNS the games and files used here and paid for them. Full owned-game files are the authoritative source for extraction + wiring into OUR game (Western Heart). We never supply/redistribute the original games for people to play — we build our own game from the files. WH ships with NO famous names + proprietary canon names.

## What to do first with this file

1. Sign in to Kaggle with Google (fmmg.mars@gmail.com) in your browser, open the notebook above, confirm GPU T4 x2, run `!nvidia-smi` + a `torch.cuda.is_available()` check.
2. Pick up the next queued GPU job (see "Jobs already proven / queued" above) or the next open item on issue #866.
3. Report GPU proof + outputs + PR link back through the user (you coordinate through the user, not around them).
