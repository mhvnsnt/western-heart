# Bass → Vain Abel wiring + Input-to-Move Fidelity Law as conversion standard
Date: 2026-10-22. Worker 59. Owner clarification ~17:16 CDT.

## Owner instruction (verbatim quote)
"We gotta do it in a Tekken input style type of way. And play style."

## What it means (three hard rules from the owner)
1. **DOA inputs → Tekken inputs:** P/K/G + directions become 1/2/3/4 + directions.
   No DOA input scheme survives — everything gets Tekken notation.
2. **Tekken feel, not DOA feel:** Bass's animations get used, but timing, hit
   properties, frame data, and combo structure follow Tekken conventions.
   A Vain Abel player should feel like they're playing Tekken, not DOA with a
   Tekken skin.
3. **Input-to-move fidelity:** press 1, left punch comes out, every time. Each move
   gets a specific, predictable Tekken input. No random mapping.

Applies to EVERY DOA fighter converted, not just Bass. Tekken is the grammar.
This is now the conversion standard for the moveset library ingest
(`tools/moveset-library-w59/ingest-doa4-kof.mjs` must enforce it).

## What was built
`game/assets/movesets/vainabel.json` v8 — full Bass Armstrong (DOA4) kit wired to
Vain Abel, replacing the 69-entry placeholder (52 moves + 10 strings + 7 specials
triangulated from DOA2/DOA5/DOA6 docs).

- **200 entries:** 147 moves + 38 strings + 15 specials
- **Source:** all 111 named entries from the DOA4 Bass command list
  (deadoralive.fandom.com), each with its exact DOA input recorded in
  `doa_move`/`doa_input`; 19 unique legacy entries merged from the placeholder;
  Tekken-grammar additions: Rage Art, Rage Drive, win poses, ring intro, stance.
- **Notation:** F+P throws → 1+3 / 2+4 / directional (f+1+3, qcf+1+3, hcf+1+3…);
  F+G holds → Tekken reversal slots (b+1+2, f+1+2, d/b+1+2…); strings use
  Tekken chaining (PPP → 1,2,1).
- **Frame data:** Tekken conventions @60fps (i10 jab 0.167s, throws i12 0.2s,
  launchers i15–18). Damage on Tekken scale (jab 7, signature throws 45–55).
  Bass archetype preserved: slowest striker, hardest grappler.
- **Situational variants** (wall/back/air/ground/throw-combo follow-ups) share a
  Tekken input with a `~variant` key suffix and a note naming the situation —
  same convention as the DOA4 federation files. Context-dependent, never random.
- **Generator:** `~/workspace/w59/staging/gen-vainabel.mjs` (compact data tables →
  schema-v2 JSON). Re-runnable; validated (all string refs resolve, all fields present).

## Template status
Bass → Vain Abel is the TEMPLATE for every DOA fighter → WH character wiring.
The per-fighter federation files (`doa4-*.json`, `kof3d-*.json`) already follow
the same law; the ingest script carries it into the library.
