# Versus setup rebuild — proof (2026-10-23, PR #832)

Rebuilt from Tekken 7's GAME OPTION <VS GAME> (arcade operators manual).
Branch: worker-submenus/versus-setup.

## Screenshots (all viewed)
- `00-menu.png` — T8 main menu, VERSUS rail item.
- `01-versus-submenu.png` — VERSUS submenu: 1V1 VERSUS + TEAM BATTLE cards.
- `02-vssetup.png` — VERSUS SETUP screen: FIGHT COUNT 1-5, ROUND TIME
  30/40/60/90/99/∞, GUARD DAMAGE ON/OFF, STAGE SELECT/RANDOM (defaults
  2 / 60s / ON / SELECT).
- `03-vssetup-allset.png` — every option tapped (5 / ∞ / OFF / RANDOM).
- `04-versus-fight.png` — fight reached through the setup flow.

## Menu harness (verify.js vssetup): 7/7 PASS
- Main menu visible; versus submenu opens with 2 cards.
- Setup screen opens with 4 option rows.
- EVERY option tapped; localStorage `wh_rules_v1` asserted =
  {"roundsVs":5,"roundTime":0,"guardDamage":false,"stageMode":"random"}.
- All tap targets measured >= 48px (0 violations).
- Back returns to the menu with the VERSUS submenu still open.

## Fight integration (verify-fight.js): 10/10 PASS
- Versus flow (setup → choose fighters → P1/P2 picks) captured the
  fight opts: {mode:'versus', roundsToWin:3, roundTime:30,
  guardDamage:false, stage:'nm-lobby', skipStage:true} — the setup
  rules reach the match; STAGE=RANDOM skips the arena screen.
- HUD: `setRounds({p1:2,p2:1}, 3)` builds 3 pips with 2 lit;
  `setTimer(Infinity)` renders '∞'; `setTimer(30)` renders '30'.

## Static checks
- `node --check` clean on all 8 touched JS files.
- gitleaks: no leaks found.
- Change set: 8 files modified + 3 new source files + this proof dir
  + 1 decision log; 0 deletions.
