VAR souls = 0
VAR trial_done = false

You stand at a crossroads between the Five Lands. A trader waits by the road, and the Trial gate hums ahead.

* [Speak to the Trader]
    The Trader smiles. "Every road has a price, traveler. But the first lesson is free: the road is the trial, walked down, not crossed."
    ~ souls = souls + 1
    -> crossroads
* [Enter the Trial gate]
    The gate opens. Nine lights flicker — one burns brighter.
    ~ souls = souls + 3
    ~ trial_done = true
    -> ending
* [Walk the road in silence]
    The road winds on. Colour shifts with each step, as if the land itself is deciding.
    -> crossroads

= crossroads
{souls >= 1: The Trader nods at your growing light.}
You return to the crossroads. The descent has five rooms: the Threshold, the Gallery of Masks, the Drowning Room, the Furnace, and the Still Point.
* [Enter the Trial gate] -> ending
* [Keep walking] -> crossroads

= ending
{trial_done:
    The Trial seals behind you. Souls gathered: {souls}. At the Still Point waits your shadow self — yourself, unmasked.
- else:
    You descend unsealed. The dark keeps what it catches, and it is waiting.
}
Named. Faced. Put down. Purification is not becoming someone else. It is meeting yourself and staying.
-> END
