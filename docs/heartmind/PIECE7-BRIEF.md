# PIECE 7 — Redux 29 as template donors (QUEUED LAST — ISO dependency SATISFIED, still waits for Pieces 1–4)

**Source:** Jay's order 2026-11-08 ~12:11 — all the Urban Reign stuff the Tekken brawler mode doesn't have, into HeartMind. Coordinator task add, 2026-11-08 ~12:12. Updated 2026-11-08 ~12:13 with the ISO landing.
**Sequencing:** LAST. The ISO dependency is now SATISFIED (see below) — but the piece still waits for Pieces 1–4 to complete (same fight code — do not run in parallel with Pieces 1, 2 or 4). Spawn when Pieces 1–4 have all reported.
**Same rules as Pieces 1–4:** fresh clone of main (`fcaa8b1d` — verify HEAD after cloning; no sparse checkouts; no /tmp clones), small verifiable commits, repo tests green (zero new failures), one PR, no merge, proof watched in motion.

## ISO LANDED (dependency satisfied, 2026-11-08 ~12:12)

The ISO agent completed: all 8 parts downloaded + size-verified, assembled `~/workspace/urban-reign-redux/iso/urban-reign-usa.iso` (4,140,924,928 B exactly), SHA-256 `c22209eefcdc4275a75dc3656b4abf5807940155236916271e19455d302a8ec2` — matches the author's source disc exactly. **50/50 fighter files extracted** (84,536,860 B, `extracted/fighters/` under `~/workspace/urban-reign-redux/`, per-file SHA-256s in `REDUX-0.5-COMPLETION-MANIFEST.json`), 0 uncovered gap ranges, all 29 models + 29 packages parse clean with the author's roster-lib.

Two corrections recorded in `INVENTORY.md` + `URMOD-EXTRACTION-FOLLOWON.md` §10 (do NOT use the old values):
- (a) `74E78599` is the PCSX2 *game* CRC, NOT the whole-ISO CRC32 (measured whole-ISO CRC32 `87803691`; SLUS_212.09 `58F4F090`).
- (b) The manifest copies field is `[output_offset, source_offset, length]`, NOT `[src, dst, length]` as `extract_a.py`'s docstring says.

## THE BLOCKER — solve FIRST, before any ingest

The 50 files are extracted but NOT wired: the author's `vmd_mesh.read_mesh` still FAILS on these guest VMDs, so no mesh → no GLB → nothing to wire. No hand-written replacement. **Your first job is to solve the guest-VMD read** — the Editor's roster-lib tooling, a third reader, or the Windows Editor route — and report the exact failure + what would unblock it if it can't. **Do NOT claim the 29 donors are ingested until a guest VMD actually parses to a mesh.**

## Job (once the VMD read is solved)

Ingest the 29 Redux fighters' movesets into the template library as donors under the plain working label "Redux guests" in code (the PROPOSED category name "Strays of the Trial" stays OUT of UI until Jay calls it — call #7). They keep their own names as template names; they are NOT WH canon fighters, never join the story. Devil Jin + Jin are donor data only, never characters (canon law). 5 portrait-only Tekken faces (Bruce, Dragunov, Eddy, Feng, Marduk) have no fighter file — no templates from them, report as such.

**Grounding:** Redux roster is 29 fighters (roster 23 + 6 stock-slot — corrected from 25; Lane 2 deliverable `~/workspace/urban-reign-redux/URMOD-EXTRACTION-FOLLOWON.md`). The 8 fighter files already extracted + SHA-verified are the pattern for the other 50 (Kiryu model + package; Asuka, CJ, Hwoarang, King, Paul, Vergence packages).

## Still owed (NOT this piece, for the record)

- The full output-disc build died on disk quota again during the copies phase (the agent deleted its own partial at once; nothing of Jay's touched) — the output-disc SHA check (`cc2312c1…`) is still owed, retryable when quota is genuinely free.
- Movesets/banks still need a built disc or the all-in-one (Drive retry cron ~7:18 PM CST tonight).

## Guardrails (same as Pieces 1–4)

- CANON LAWS (Jay): there is NO Jin Kazama in our game at all — the ONLY Jin is the soul JIN (the Blade Soul), pickable as Phantom. "Devil" may appear ONLY in OUR own way and language, NEVER in the Devil Within way. Pantera is male (he/him); every other fighter by name only, no guessed pronouns.
- STANDING RULE (Jay 2026-11-08): top-level industry-standard way, from their source and code — not hand-tooled, not homebrewed, fully wired up, landed in the repo, from research, never guessing. Our own code is thin glue only.
- No commercial game code/models/art/audio/logos/dialogue copied into the game, even privately — measure and rebuild in our own code.
- If the ingest hits a real blocker, stop at the blocker, write the exact blocker + what would unblock it, and report — do not hand-build a workaround and call it the fix.
- Update `HEARTMIND-COMPLETION.md` (C6 row) with measured evidence if the score moves.
- Proof: live, phone-size, video — proof under `~/workspace/western-heart-audit/proof-ur-all/`, NOT /tmp.
- DISK: VM quota freed 2026-11-08 ~11:27 but the edge moves — the output-disc build just died on quota again, so treat quota as FRAGILE: on EDQUOT stop, delete ONLY own partials, report exact error + bytes written, never touch `~/workspace/video-mocap` or `browser_downloads` (Jay's files, never delete).
- Workdir for the clone: `~/workspace/redux-donors/repo` (fresh single-branch clone of main, HEAD verified `fcaa8b1d`). Branch: `redux-donors`.
