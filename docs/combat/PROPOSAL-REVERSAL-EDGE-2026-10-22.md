# PROPOSAL — Reversal Edge, Tekken-ified (NOT YET APPROVED)

**Status:** MAYBE per user 2026-10-22 — proposal first, no implementation.
**This is a design proposal only. Nothing below is implemented.**
**Teardown source:** `teardown/soulcalibur-6/docs/SCVI-MECHANICS.md` (§5),
community frame data (Frame Calibur / Dustloop via SuperCombo Wiki).

---

## 1. What Reversal Edge actually is (SCVI, community-documented)

- **6-frame startup universal parry**, holdable to extend the window. Parries
  high/mid/low — but NOT break attacks or unblockables.
- On a successful parry → an RE attack. If it lands → **slow-motion RPS
  minigame**: each player picks one of A attack / B attack / K attack / Guard /
  Step. Triangle roughly A > K > B > A; Guard vs B restarts the clash;
  correct step dodges for big damage, wrong step eats the hit.
- **Round 2:** same option or G-vs-B continues the clash. The initiator gets
  massive advantage (B does 100% guard damage, all options become lethal,
  initiator wins ties).
- **Charged RE** (held to max): becomes a +8-on-block break attack with big
  chip and meter.
- RE is the **fastest soul-gauge builder** in SCVI — the comeback mechanic
  doubles as the meter engine.
- Design intent: a momentum-breaker — the losing player forces a mind-game
  reset. Narratively SC frames it as a clash of wills.

## 2. Why it might be wrong for Western Heart (honest section)

The user said "Tekken doesn't use those for a reason." The reasons, applied
to RE:

1. **Pacing.** RE stops the fight for a minigame. WH's feel priority is flow —
   Tekken-like exchanges with extra physics. A slow-mo RPS break every time
   someone is losing is the opposite of flow.
2. **It flattens skill.** The RPS minigame is close to 50/50 with initiator
   edge. Turning a losing position into a coin flip devalues the neutral game
   that got you there.
3. **WH already has a comeback mechanic.** Soul Surge (100 souls, 18-damage
   cinematic super) is the WH comeback button. RE would be a second one
   competing for the same emotional slot.
4. **Button budget.** SC has a spare shoulder button. WH's inputs are spoken
   for (limbs, block, surge, dodge, transform, V-System).

This proposal exists because the *fantasy* — two souls colliding, time
dilating — maps beautifully onto WH's trial narrative (the self as final
boss). If that fantasy is worth the costs, here's the Tekken-ified version.

## 3. The Tekken-ified proposal

### Input — no new button
**b + block-tap** (hold back, tap the block button — the "turn defense into a
clash" gesture). Cost: **50 souls** (½ bar — mirrors SCVI Resist Impact's
½-soul-gauge cost, and makes RE a resource decision, not a panic button).
6f startup, holdable up to 20f, parries high/mid/low; loses to throws,
unblockables, and break attacks, exactly like SCVI.

### The clash — Tekken limbs, not A/B/K
On a successful parry the screen desaturates, time dilates to ~0.3× for the
pick window, banner: **SOUL CLASH «name TBD»**. Both players pick simultaneously:

| Pick | Input | Beats |
|---|---|---|
| Fang (punch) | 1 | Claw (kick) |
| Claw (kick) | 4 | Edge (heavy) |
| Edge (heavy) | 2 | Fang (punch) |
| Guard | block | — (restarts clash, defender takes chip) |
| Step | u/d tap | dodges a *correctly-read* limb for a launch; wrong read eats the hit |

(Names «TBD» — the limb triangle is 1 > 4 > 2 > 1 so Tekken players read it
instantly. Guard-vs-heavy restarts; initiator wins ties and gets round-2
lethal properties, per SCVI.)

The winner gets a **full combo starter** (launch, not a cutscene). The loser
eats it. Total break in flow: ~2.5 seconds, then the fight resumes at full
speed.

### Tekken-ification mitigations (the "for a reason" answers)
1. **Costs 50 souls** — not free, not spammable; it competes with Soul Surge
   and (now) V-Trigger for the same meter. Resource tension, not a panic button.
2. **Loses cleanly to throws.** Throw the RE startup or the clash stance and
   it's over — grapplers stay relevant, and there's a universal answer that
   isn't "guess the RPS."
3. **The RE attack is sidesteppable.** The parry doesn't guarantee the clash —
   the follow-up attack can be stepped or blocked like any Tekken move.
4. **Once per round per player.** It stays a *moment*, never a strategy.
5. **No meter gain from RE.** SCVI's fastest-meter-builder property is cut —
   WH's meter economy doesn't need a second engine.

## 4. How it would feel

You're losing. The opponent is pressing. You spend half your souls, hold
back, tap block — the world goes quiet and slow, and for three seconds the
fight isn't about frames anymore, it's about *souls*. You read their Fang
with your Edge. Time snaps back. They're launched. The crowd (in your head)
goes wild. Then it's Tekken again.

In story mode, the trial's final boss uses it too — the one fight where the
game *tells* you the self is the final boss is the fight where your own
mechanic gets turned on you.

## 5. Story-mode-only variant (fallback proposal)

If full versus-mode RE is too much: restrict the clash to story/boss fights
as a scripted *soul-clash* beat (Heart-and-Mind-Within campaigns). Versus
keeps its flow; the fantasy lives where the narrative justifies it. This is
the proposer's recommended scope if the user is on the fence.

## 6. Open questions for the user

1. Full versus implementation, story-only variant, or skip entirely?
2. Is the "SOUL CLASH" fantasy worth a ~2.5s pacing break, given Soul Surge
   already owns the comeback slot?
3. Name: «TBD with user» — candidates in the V-System doc's naming appendix
   style (Nine-Souls-flavored), but this one needs its own pick.

## 7. Implementation sketch (only if approved)

- `fighter.js`: `tryReversalEdge()` (b+block-tap edge, 50-soul cost, 6f
  startup, holdable parry window); clash state machine on both fighters;
  `game.js`: slow-mo timescale hook (same mechanism as V-Shift's — build
  V-Shift first and RE reuses it); limb-triangle resolution table;
  once-per-round flags; `main.js`: desaturate + banner presentation.
- Estimated: ~250 lines + tests. Reuses the V-System slow-mo path.
