# Cross-up proof (390x844 touch, headless Chromium, Burger vs Purple Rain, Tree of Life)
P1 at x=-0.8, P2 at x=0.7, P1 jumps holding forward. Samples every 70 ms: [p1.x, p1.y, p2.x, p1.facing].

Before (live main): P1 is held off at a 1.45 gap the whole jump and never passes over; facing stays +1.
[[-0.78,0.6,0.67,1],[-0.78,0.98,0.67,1],[-0.76,1.14,0.69,1],[-0.62,1.08,0.83,1],[-0.48,0.8,0.97,1],[-0.34,0.3,1.11,1],[-0.2,0,1.25,1],...,["end",0.78,2.23,1,-1]]

After (this branch): P1 passes over P2 at the top of the jump, lands on the far side, and both facings flip.
[[-0.52,0.6,0.42,1],[-0.24,0.98,0.14,1],[0.04,1.14,-0.14,-1],[0.32,1.08,-0.42,-1],[0.6,0.8,-0.49,-1],[0.88,0.3,-0.49,-1],[1.16,0,-0.49,-1],...,["end",3.4,-0.49,-1,1]]
