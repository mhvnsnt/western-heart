# voice-changer rig — create-a-fighter real-time VC (2026-10-16)

**Tool:** [w-okada/voice-changer](https://github.com/w-okada/voice-changer) · **MIT** ·
⭐ 21,187 · pushed 2026-09-26.

## Concept
Player creates a fighter → picks (or records) a base voice → the rig converts their live
mic (or pre-recorded taunts) into the character voice in real time via RVC/ONNX models
loaded into voice-changer slots.

## Components
- **GUI:** repo start scripts (`start2.sh`, `start_docker.sh`) — model slot management,
  pitch/formant tuning per fighter.
- **Server:** `server/MMVCServerSIO.py` — socket.io server for game-engine integration.
  The game client streams mic audio in, receives converted character voice out.
- **Models:** any RVC v2 / ONNX VC model per fighter. Train per-character RVC models from
  the Chatterbox-generated roster voices (Chatterbox = owner default character voice —
  RVC models derive from it, never replace it).

## Integration sketch (Western Heart)
1. Roster voice design: Chatterbox zero-shot clone per fighter (existing pipeline).
2. Export 5–10 min of Chatterbox voice per fighter → train RVC model → `.pth` + index.
3. Load fighter RVC models into voice-changer slots (one slot per active fighter).
4. Game client: mic → `MMVCServerSIO` → converted voice → in-game voice chat / taunts.
5. Fallback: no mic → pre-rendered Chatterbox taunts (existing TTS path).

## Notes
- GPU recommended for real-time (T4 fine); CPU possible at higher latency.
- Keep RVC training data to voices we own (Chatterbox generations, owner-recorded lines).
- License: MIT — commercial-safe. (seed-vc was excluded: GPL-3.0.)