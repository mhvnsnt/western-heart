# PS2 HTTPS Fallback — Cloudflare Quick Tunnel

**Status 2026-11-21 ~08:40 EST: LIVE AND VERIFIED.** Both KoC2 games boot and play
over public HTTPS through the tunnel. No "Secure connection required" gate.

## The link (give this to Mars)

- Tunnel base: https://powerseller-success-requesting-evanescence.trycloudflare.com
- English: https://powerseller-success-requesting-evanescence.trycloudflare.com/play-ps2.html?game=koc2
- Hybrid JP/EN: https://powerseller-success-requesting-evanescence.trycloudflare.com/play-ps2.html?game=koc2hybrid

**FALLBACK ONLY — the URL is ephemeral.** If the tunnel dies or the VM reboots,
the URL changes. The Render static site remains the durable HTTPS path.

## Verification (Puppeteer on the VM, Chrome 157, SwiftShader)

| Game | Boot | State | fps (title) | discReads / bytes | Errors | Gate visible |
|------|------|-------|-------------|-------------------|--------|--------------|
| koc2 (English) | 5s | running | 94 readings, avg 33.9, last [39,39,38,39,38] | 19 / 39,845,888 | [] | NO |
| koc2hybrid | 5s | running | 94 readings, avg 33.5, last [40,39,39,39,39] | 18 / 37,748,736 | [] | NO |

Network: manifest 200, 19–20x HTTP 206 Range fetches to raw.githubusercontent.com,
tunnel page status 200. Title run (prompt dismissed via Up + Circle): both stayed
running, reads rose to 31/29, errors empty. Logo run (koc2, 90s past prompt):
attract FMV playing, 41 reads / 85,983,232 B, errors empty.

Screenshots (eyes-on checked, all in this dir):
- koc2-t30.png — memcard prompt in Japanese (known untranslated string), 38 fps · 63%
- koc2hybrid-t30.png — same prompt in English, 38 fps · 63%
- koc2-title2.png — title background (blue smoke), 29 fps · 48%
- koc2-logo-90s.png — attract FMV, real match footage in the ring, 29 fps · 48%

Speed note: title/attract ~29–39 fps (48–65%) on the VM rig — same class as the
localhost Phase 5 runs. Match speed is still the known ~28% figure from the
original test; phone speed unknown until Mars tests on his phone.

## Caveat — Cloudflare bot filter

My sandbox VM's egress IP gets a plain-text 403 "Your request was blocked" from
Cloudflare's edge on this URL (datacenter IP flagged). The Oracle VM's own IP
gets 200, and all Puppeteer verification passed from there. Mars's phone
(mobile/residential IP) should pass like the VM does — but I could NOT verify
from a phone IP. If he hits a Cloudflare block page, that's the known
trycloudflare bot-filter risk, not the tunnel failing.

## Live state on the VM

- cloudflared 2026.11.1 at /home/ubuntu/bin/cloudflared (official GitHub
  release, downloaded over HTTPS; the release's .sha256 asset 404'd, so no
  checksum verification was possible — version check passed).
- tmux session `ps2-tunnel` (created 2026-11-21 13:22 UTC), process alive,
  log at /home/ubuntu/ps2-tunnel.log.
- Tunnel serves the VM's nginx on http://localhost:80 (COOP/COEP headers
  already in place). Nothing else touched: no nginx/port/ttyd/games.json
  changes, no processes killed.

## Restart (if the tunnel dies — URL WILL CHANGE)

```bash
ssh -o ProxyCommand="nc -X connect -x 198.19.0.1:3128 %h %p" -o IdentitiesOnly=yes -i ~/.ssh/id_ed25519 ubuntu@132.145.194.139
tmux kill-session -t ps2-tunnel   # only if the old session is still there but dead
tmux new-session -d -s ps2-tunnel "/home/ubuntu/bin/cloudflared tunnel --url http://localhost:80 2>&1 | tee /home/ubuntu/ps2-tunnel.log"
sleep 10
grep -o "https://[a-z0-9-]*\.trycloudflare\.com" /home/ubuntu/ps2-tunnel.log | sort -u
```

Check liveness anytime: `tmux ls | grep ps2-tunnel` and
`curl -s -o /dev/null -w "%{http_code}\n" https://<tunnel>/play-ps2.html`
(from the VM — a curl from the sandbox VM will 403 on the bot filter).

## Scripts

- ~/workspace/koc2-disk-decision/tunnel-verify.js (both games, full metrics)
- ~/workspace/koc2-disk-decision/tunnel-title.js (prompt dismiss + title shots)
- ~/workspace/koc2-disk-decision/tunnel-logo.js (koc2 long-wait attract shot)
- Full metrics: tunnel-results.json in this dir. VM copies in /dev/shm/tunnel-test/.
