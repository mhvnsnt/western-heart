# Move Matching System — How Tekken Does It Right

## The Four Things That Must Align

Every move has four sides that must match:

1. **Input** — What button you press and what state you're in. LP1 (Left Punch = Tekken 1), RP2 (Right Punch = Tekken 2), LK3 (Left Kick = Tekken 3), RK4 (Right Kick = Tekken 4). States: standing, crouching, jumping, while rising, while running.

2. **Animation** — What the clip ACTUALLY does, verified by analyzing bone data, not by reading JSON labels. Properties to check:
   - Hip height over time (does it jump? does it crouch?)
   - Limb trajectory (which arm/leg moves? LP1/RP2/LK3/RK4?)
   - Root movement (does it move forward/back? does it stay in place?)
   - Type (strike, throw, block, etc.)

3. **Move List Placement** — Where the move sits in the Create-A-Move List editor, what slot it's assigned to. The editor must show all moves including wrongly mapped ones, so the user can see and fix them by swapping.

4. **Row Matching** — How a move connects to its animation row. This is where bulk JSON matching fails.

## How Tekken Does Row Matching Right

In real Tekken, there is no "matching" step. Each move in the movelist directly references its own animation. King's jab entry says "play animation X" — and animation X IS King's jab. The move and animation are one thing, linked directly. No guessing, no metadata matching.

## How Our Game Got It Wrong

PR #988 matched T7/T8 moves to T3 animation rows by comparing JSON fields (input, class, limb). This is guessing. Example: Pantera's LP1 (jab) was mapped to T3 King row 38 because the JSON said "input 1, strike, left arm." But the actual animation clip for row 38 jumps — it's a jumping jab, not a standing jab. The JSON label said "jab" but the clip does a jump AND a jab. JSON matching cannot detect this.

## The Right Way Going Forward

1. Analyze ACTUAL animation clip data for every row: hip height over time, limb trajectories, root movement.
2. Tag each row with what it ACTUALLY does: jumping/standing/crouching, which limb, what type.
3. When mapping a move to a row, check: does this row's actual properties match this move's input context? Standing slot gets standing animations only. Jumping slot gets jumping animations only.
4. The Create-A-Move List editor shows all four pieces together: input, animation properties, placement, and row. When any don't align, the user can see it and fix it by swapping.
5. Do this one character at a time, starting with Pantera. Verify by playing, not by checking JSON fields.

## Button Names

LP1 = Left Punch = Tekken 1
RP2 = Right Punch = Tekken 2
LK3 = Left Kick = Tekken 3
RK4 = Right Kick = Tekken 4
Use LP1/RP2/LK3/RK4 format in ALL conversation with the user.

## Create-A-Move List — WWE-Style Editor with Custom Combos

### What It Is
Port of WWE's Create-A-Moveset system into Western Heart's creation suite, renamed to Create-A-Move List. Organized in Tekken input style (LP1, RP2, LK3, RK4 + directions).

### Flow
Select character → Create-A-Move List → Edit → Choose character → See ALL moves in a list (including wrongly mapped ones) → Swap moves to correct slots.

### What the Editor Shows
For every move slot:
- Move name (from T7 files)
- Button input (LP1, RP2, LK3, RK4 + direction)
- Exact animation (name/ID from T7 files, not a T3 guess)
- Current mapping status (correct / wrong / approximate / unmapped)

### Custom Combos
Once moves are organized, the editor lets you:
- Extend combos: LP1, RP2 → LP1, RP2, LP1 → LP1, RP2, LP1, RP2
- Shorten combos: Remove hits from long strings
- Build custom combos: Chain any moves together in any order
- Not limited to Tekken's preset strings — create your own

### Data Source Priority
1. WWE 2K22 (most recent, best moveset creator) — when available from Grok's box
2. WWE 2K19 (pull plan exists) — when available
3. Older WWE games already torn down (No Mercy, WMXIX) — start here NOW, do not wait for 2K22
4. T7 files for Tekken moves (kin.mvl and other movelists in private repo)

Do NOT wait for 2K22 to start organizing. Use whatever WWE data is already available, then upgrade to 2K22 when it arrives.

### Button Names
LP1 = Left Punch = Tekken 1
RP2 = Right Punch = Tekken 2
LK3 = Left Kick = Tekken 3
RK4 = Right Kick = Tekken 4

### Context-Appropriate Animation Validation (CORE REQUIREMENT)

The editor MUST enforce that animations match their slot context. This is not optional — it is the core validation that prevents the jumping-jab-in-standing-slot problem.

**Validation Rules:**

- Jumping slots → ONLY jumping animations (jumping LP1, jumping RP2, jumping LK3, jumping RK4)
- Crouching slots → ONLY crouching animations
- Standing slots → ONLY standing animations
- Back/forward/left/down variations → animations matching that direction
- Diagonal inputs (down-forward + RP2, etc.) → animations matching that diagonal direction
- Combination inputs → animations matching the full input sequence

**How Validation Works:**

When you try to assign a move to a slot, the editor checks the animation's properties against the slot's context:
- Animation properties (from clip analysis): jumping/crouching/standing, direction, limb, type
- Slot context (from input): standing/crouching/jumping, direction, button
- If properties match context → assignment allowed
- If properties do NOT match context → assignment BLOCKED or flagged as wrong

User directive (verbatim): "where you can replace the move with the proper animation that goes there not with just like any bullshit animation but like if you're pressing if it's a crouching position that only the crouching animations can get chosen there and such and such"

This means: you cannot put a jumping animation in a standing slot. You cannot put a crouching animation in a jumping slot. The editor validates every assignment against the slot context. No more guessing, no more wrong animations in wrong slots.
