# @mhvnsnt/creation-suite
Shared creation suite (see `docs/creation-suite/DESIGN.md`).
```js
import { makeDNA, applyDNA, attach, suiteMenu } from '@mhvnsnt/creation-suite';
const dna = makeDNA({ bodyType: 'heavy', sliders: { belly: 1.8 } });
const springs = applyDNA(gltf.scene, dna);     // sliders + generated jiggle bones
// each frame, after animation: springs.update(dt)
```
Tests: `node --test test/`. Proof: `proof/harness.html` (serve with three in `./three`, the
package in `./cs`, and the Lab GLBs beside it), screenshot via `proof/shot.cjs`.

> ⚠️ **NON-COMPLIANT UI (owner law, Oct 23, 2026, 2:21 PM CT):** the current menu/UI (`suiteMenu` and related screens) is hand-built and pending a rebuild sourced from Tekken T5/T6/T7/T8/TTT2 and other game teardowns. Do not delete it; every UI change must cite its teardown source. The DNA/slider/jiggle logic is not affected by this note.
