# SFIV teardown status

Checked live 2026-11-20. Owner order (Nov 20 ~19:27 EST): pull the
already-torn-down/decomped fan/mod work instead of buying the games.

## SFIV — Street Fighter IV

| Item | Status |
|---|---|
| Complete extracted moveset/animation/model pack | NONE FOUND anywhere searched |
| Extraction toolchain (bac/bcm parser) | PULLED — `tools/sf4tools/` (Dantarion, MIT) |
| Decomp / static-recomp port | RECORDED — `sf4-nx.md` (`jvankooo/sf4-nx`, GPL-3.0, working v0.1.0); framework only, not vendored |
| archive.org teardown/decomp | NONE — 40 software items checked; all raw game images/builds/prototypes/fixes/MUGEN |
| Models Resource | No SFIV vanilla roster pack; USFIV page has 2 assets total (Adon + 1 stage) |
| WH bank converter for bac/bcm | NOT BUILT — next step |

## USFIV — Ultra Street Fighter IV

Same engine, same formats, same toolchain as SFIV — covered by this
directory. No separate USFIV teardown exists; the only USFIV-specific
extraction found is a single Adon fighter model (DAE, 14.21 MB) on the
Models Resource, no animations, not pulled. USFIV status is recorded
separately in `../ultra-street-fighter-4/`.

## SFxT — Street Fighter X Tekken

Same bac/bcm/emo formats as SFIV (ShiroiKaze ripped the Xbox 360 disc
with SF4 tools in 2012, full DLC cast with rigs + animations) — but no
surviving downloadable pack was found; only EventHubs images, single
MMD rips, and sound rips remain. No SFxT recomp project exists (a
"SFxT RECOMP" logo image on Facebook, Oct 11 2026, has no repo/code).
SFxT status is recorded separately in `../street-fighter-x-tekken/`.

## Still missing (exact gap)

1. **Extracted moveset data.** Nobody publishes a complete SFIV/SFxT/USFIV
   moveset dump. To get one, run `tools/sf4tools/` against real game files
   (SF4 PC install or the owner's Xbox 360 disc files) and dump bac/bcm →
   JSON. That run has not happened yet.
2. **WH bank converter.** bac/bcm JSON → WH moveset bank. Not built.
   The SF EX `PL/*.PAC` clips have the same gap (no WH bank converter,
   P00X index → names not established).
3. **Animations/models.** `.emo`/`.emz` extraction needs piecemontee's
   SF4 Asset Explorer (SourceForge mercurial source, v0.38 binary on
   mediafire) — not vendored here; no GitHub mirror found.
