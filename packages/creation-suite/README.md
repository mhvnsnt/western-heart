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
