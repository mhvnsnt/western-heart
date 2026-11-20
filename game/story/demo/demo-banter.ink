// WH Story System demo — Track 7 (2026-10-23).
// Demo-only narrative for the cinematic director / inkjs wiring test.
// Canon-safe: uses only established canon terms (the Trial, the Nine
// Souls, Tong-Nou). A spirit guide speaks before a Heart-and-Mind-
// Within wave; branches on the wanderer's choice. Compiled with
// inkjs 2.4.0 (MIT): ink-full.mjs -> demo-banter.ink.json.
// Writer tool: Inky (https://github.com/inkle/inky).

VAR wave = 1
VAR hp = 100

-> start

=== start ===
GUIDE: Another echo rises, wanderer. The Trial keeps what it catches.
GUIDE: Wave {wave} of the descent. Your ember burns at {hp} percent.
+ [Steel yourself] -> steel
+ [Ask what the echo wants] -> ask
+ [Descend in silence] -> silent

=== steel ===
GUIDE: Good. Stillness does not compete — but it does not kneel either.
~ wave = wave + 1
-> wave_gate

=== ask ===
GUIDE: What every echo wants: the piece of you that you threw away.
GUIDE: Take it back, or become it. Those are the only doors here.
~ wave = wave + 1
-> wave_gate

=== silent ===
GUIDE: ...The quiet ones descend fastest. Mind the dark.
~ wave = wave + 1
-> wave_gate

=== wave_gate ===
{ wave > 3:
    GUIDE: Three waves down. The warden stirs. This is where the Trial stops being polite.
    -> END
- else:
    GUIDE: Wave {wave}. Keep your ember lit.
    -> END
}
