# SC6 (SoulCalibur VI, Steam app 544750) pull — progress

Started: 2026-11-06 ~17:41 CST (owner order: "Get the soul caliber binaries")
Lane: subagent 80586e3b. Route: DepotDownloader, same as T7 full pull.

## Environment facts (verified)
- DepotDownloader: ~/workspace/_steam-pull/tool/dd/DepotDownloader
- Steam account: vil3m, remembered login (login key in IsolatedStorage under
  HOME=~/workspace/_steam-pull/ddhome). T7 pull used:
  `DepotDownloader -app 389730 -depot 389731 -manifest <id> -dir <dir> -filelist <f> -username vil3m -remember-password`
  with NO_PROXY extended for steamserver.net,steamcontent.com,akamaihd.net,steamstatic.com
- T7 store pattern: waves via filelist-waveN.txt -> store_wave_v3.py + resume_store.sh
  -> GRE releases t7-depot389731-waveN-20261031, SHA256SUMS + manifest json per wave.
- Disk at start: /home 110G used / 39G free (df); quota wall ~118G -> stage small, store+verify+clear per wave.
- Other lanes in progress (DO NOT DISTURB): CF Pages build of WH (proc running, cf-wh-clone).

## OWNERSHIP VERDICT (2026-11-06 ~17:45 CST): NOT OWNED
- Probe: DepotDownloader -app 544750 -manifest-only, remembered login (vil3m).
  Login WORKED (85 licenses — same count as the T7 pull). AppInfo for 544750 fetched.
  DD output: "App 544750 (SOULCALIBUR VI) is not available from this account."
  Full log: probe-manifest-only.log in this dir.
- Per task step 3: STOPPED before any purchase. No pull attempted.

## Price facts (checked 2026-11-06 23:43 UTC, live Steam page fetch)
- Steam base game: $59.99 list; NO discount visible on the live page right now
  (the 90%-off $5.99 Steam deal tracker pages showed 2 days ago appears rotated off).
- Steam Deluxe Edition (base + Season Pass 1): $14.39 (84% off $89.99),
  SPECIAL PROMOTION ends November 10 — live on the page now.
- Authorized Steam-key resellers (CheapShark feed, Oct 27): GameBillet $5.26,
  Gamesplanet $5.30, Humble Store $5.99, IndieGala $5.99 for the base game.
- The teardown only needs the BASE game: its main Windows depot carries the
  exe + data archives incl. guard/stamina system data. Deluxe/SP1 only adds
  DLC-character depots.

## Existing SC holdings inventory
- GRE teardown/soulcalibur-6/: DOES NOT EXIST (contents API 404; GRE root tree
  has no soulcalibur path under teardown/). GRE root `soulcalibur/` = MODEL-HUNT
  docs only (community fan-model cataloging, Oct 2026). The SCVI research docs
  actually live in WESTERN-HEART teardown/soulcalibur-6/: TEARDOWN.md (5,276 B)
  + docs/SCVI-MECHANICS.md (11,330 B). Docs only, no binaries.
- No SCVI binaries in any GRE release (release list, 200 checked: zero
  soul/calibur/sc6 hits).
- WH: no soulcalibur teardown dir; SC mentions are docs/research only.
- Local disk: agent-ops top100-staging/wave-15/soulcalibur-vi.md = dev-interview
  research writeup (not game data). wh-ttt2/teardown/soulcalibur-2 + ghidra-projects/
  soulcalibur2 + gre-p9r/soulcalibur (MODEL-HUNT docs, 111M) are SoulCalibur II /
  earlier-title material, NOT SCVI.

## Steps
- [x] Ownership probe: DD -app 544750 -manifest-only (remembered login) -> NOT OWNED
- [x] Inventory existing SC holdings (GRE + WH) -> docs/research only, zero binaries
- [x] Price/route facts gathered (live Steam page 2026-11-06 23:43 UTC)
- [ ] BLOCKED ON OWNERSHIP: pull waves -> store -> verify (runs the moment the
      account owns app 544750; route + tooling proven and staged)
- [x] Final report (to parent, 2026-11-06)

## Disk state
Nothing pulled, nothing staged beyond this dir (PROGRESS.md + probe log +
empty DD depot dir). No local clears needed; nothing logged to disk-cleanup-log.
Other lanes untouched (CF build left alone).
