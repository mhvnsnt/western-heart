# Chain throws + the T7 1,2,1,2+4 copies (2026-10-29)

## Chain throws (Tekken multi-part throws)
Stage rows such as AB1.1,1+2 (King's Arm Breaker chain) used to be swept as stance moves, so they never ran inside the throw they belong to. They are real now:
- game/js/movesets.js: throwStageTag reads the stage from the throw's name. "Arm Breaker (AB1)" gives AB1. A T7 throw with no code, such as "Arm Breaker", gives ARM_BREAKER. throwStageKeys lists that stage's rows.
- game/js/fighter.js: buttons pressed during throwing or throwExec go to the stage (_throwChainPress). When the presses fully match a row, that row is queued; a partial match keeps listening, and chord presses count as one input. When the current part ends, _startThrowChain starts the queued row on the same victim, with its own throw clip and damage.
- test/e2e/moveset-sweep.page.js: a stage row is entered during its parent throw, one level at a time. For example, AB2b.3,4,3+4,1+2 runs CD.1+3, then AB1.2,4,2+4 inside it, then 3,4,3+4,1+2 inside that.

Results (sweep-pantera-chainthrow.json compared row by row with sweep-pantera-motion.json): pantera 698 -> 718, with 21 rows fixed:
- The full Arm Breaker chain: AB1.*, AB2b.*, AB2c.*, ARM_BREAKER.*
- SHH1.*, SHH2c.*, STANDING_HEEL_HOLD.*, HEAD_JAMMER.*, COBRA_CLUTCH.*, COBRA_TWIST.*
- The four T7 copies 1,2,1,2+4~t7.king, .2, .3, .4

One row went from pass to fail. PILE_DRIVER.1+2,1+2 only passed before because the old sweep fired it as a stance move. It now runs inside its parent, qcf+1~t7.king, and that parent does not fire yet. The parent's input is the same as n,d,d/f,f+1, which wins. This conflict already existed and is a separate fix.

Other fighters with chain rows (sweep-*-chainthrow.json):
- armor-king: SLEEPER.* and NECK_DROP.* pass. SUPLEX.d,d,d+1+2 does not, because the stick steps are not read as stage input yet.
- awapop and t3-nina: BACKHAND_SLAP.* and CRAB_HOLD.* pass. SHOULDER_THROUGH_BUSTER.2,1,3 does not, because its parent is a string throw.
- kinpo: NANIWA_ULTIMATE_TACKLE.* passes.

## T7 copies of 1,2,1,2+4 (pantera.json)
Cause: the copies' grab came out while the opponent was still 2.0 to 2.2 m away, pushed back by hits 1 to 3, and the default reach is 1.7. The base row connects through its clip geometry. The animation row was not the cause: copying every data field except the slot did not fix it.
Fix, on the four copies only:
- reach 2.3, so the string's last hit reaches through its own pushback. In T7 this hit is guaranteed once the string connects.
- anim_t3 row 280 and row 279 changed to 127, the same clip the base row uses. The match label now records that.
All four now reach throwExec with the victim clip.
