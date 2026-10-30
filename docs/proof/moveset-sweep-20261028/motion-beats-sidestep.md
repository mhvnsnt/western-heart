# Motion in progress beats sidestep (2026-10-29)

Root cause: in pantera's 6-step f,n,b,d/b,d,f+1, the d step was released before f went down (a key-by-key roll). input.js read that as a u/d tap returning to neutral and queued a sidestep, which ate the button.

Fix (game/js/input.js): a u/d tap now waits a 3-frame grace (SS_GRACE_MS = 50 ms). If a horizontal arrives inside it, the tap was a motion step and no sidestep fires. Otherwise the sidestep fires when the grace ends. Unit coverage: test/input-timing.test.mjs (touch d tap still sidesteps after the grace; d then f inside it gives no sidestep).

Sweep (sweep-pantera-motion.json, compared row by row with sweep-pantera-variants.json):
- pantera 696 -> 698: fixed f,n,b,d/b,d,f+1 and f,n,b,d/b,d,f+1~t3.king, 0 regressions.
- ryuji 135 -> 135 and ryuji-rock 136 -> 136, 0 regressions. jin_soul 785 -> 785 (pass count).
- Unit tests 116/116.
