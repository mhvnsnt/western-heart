# Western Heart — Work log (timestamps CT)

- 2026-10-14 16:10 Grok Bot (QA lane): claimed in agent-ops CLAIMS.md (`grok/wh-playtest-qa`). Sparse clone `/workspace/wh-qa` (`--depth 1 --filter=blob:limit=2m`), Godot 4.3 already on box. Disk 4.6 GB free, RAM ~5 GB.
- 16:15 Imported lab/game headless; read main.gd / fighter.gd / move_table.gd / ai.gd. King jab row 35 has active_first 18; grab and heavy share row 230.
- 16:20 Wrote `lab/game/tests/qa_playtest.gd` (scripted P1 via InputMap, dummy P2, per-frame CSV). Headless run: 12 scenarios, 30 s.
- 16:22 xvfb + opengl3 capture: 280 PNG → mp4. Copied 7 key frames + mp4 + csv to `docs/qa/2026-10-14/`.
- 16:25 Wrote PLAYTEST-METHOD.md, QA-FINDINGS.md (13 bugs, prioritized), HOW-TO-CONTINUE.md. No engine scripts edited (Repo Co Dev holds the Lab playtest/fix claim).
