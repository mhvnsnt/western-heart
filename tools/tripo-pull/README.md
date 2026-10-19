# tripo-pull — THE Tripo download tool. USE THIS. ALWAYS.

**NEVER ask the owner for a Tripo sign-in. NEVER try a browser session. NEVER say a model "needs his login."**

Tripo's export flow is flaky (paywall / Cloudflare / auth issues), but models
shared via public links expose their files through Tripo's public
project-detail API. `tripo-pull.py` resolves any share URL to the direct
download URL and pulls the file — no sign-in, no browser, no credits.

```bash
python3 ~/workspace/tools/tripo-pull/tripo-pull.py <share-url-or-uuid> -o ~/workspace/tripo-downloads/
```

If a pull 401s, the UUID is wrong or the link is bad — CHECK THE URL, do not
ask for a login. The owner has ordered this: the tool IS the method.

Owner law (2026-10-18): this tool lives in all repos (`tools/tripo-pull/`)
and is the only sanctioned way to pull Tripo models.
