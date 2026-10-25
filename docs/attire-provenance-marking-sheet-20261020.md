# ATTIRE-PROVENANCE MARKING SHEET — Western Heart

**Owner order 2026-10-20 ~14:19 CDT · RECOVERY RUN #2 (prior lane d865c39b died ~15:30 CDT without delivering) · built 2026-10-20 (CDT).**

The owner marks the verdicts himself. This sheet is the complete, evidence-grounded inventory — NOT the verdicts.
The two verdict columns ([ ] move to Tripo model / [ ] keep as skin) are HIS to fill. KEVIN A3 Master White is pre-marked PARKED (his verdict).

## Method
- **Repo wiring wins over old notes:** `game/js/attires.js` + `game/js/roster-full.js` + `game/js/assets.js` MODEL_URLS on main (via gh api, 2026-10-20), cross-referenced with `roster/*/ATTIRE-SLOTS.md` + `roster/TRIPO-REGISTRY.md` + the 39-model audit (`~/workspace/wh-pose-survey/inventory.jsonl`).
- **Wire status** verified against the live main tree (59,866 files): wired = game key resolves to an existing file; not wired = file exists in repo but has no game key; broken = path 404s.
- **Provenance values:** Tripo original / source-game retexture (names the source-game character) / source-game model / Tripo reskin-of-source / community rip / unknown — needs evidence. Never guessed.
- **Owner-settled facts baked in:** KEVIN is the fighter (Baek rows folded in; no separate Baek row); PANTERA final order A1 T7King reskin / A2 Leo man Tripo / A3 snow-leopard reskin / A4 Leopard King Tripo / A5 Crimson Rage / A6 T7 P2; MARIPOSA A1 = original Tripo butterfly (eyes on wings), A2 = Monarch reskin (exempt); DEATHFANG 1+2 = owner Tripo originals; CHARGER 1+2 = owner Tripo originals; KRONOS A3 = TimberWolf Suited (Tripo 93e4961f); DXMMII gets NO exemption (Patchwork row unflagged); Phantom = owner-approved portrait (note, not an attire verdict row).

## The sheet

| Fighter | Attire (slot # + name) | Model file (repo path) | Built on | Wire status | [ ] move to Tripo model | [ ] keep as skin (built-on-Tekken) | Notes |
|---|---|---|---|---|---|---|---|
| RIN | A1 (default) | `game/assets/models/steve-fox.glb` | source-game model (Tekken Steve Fox, teardown extraction) | wired | [ ] | [ ] | shared steve-fox base (tint applied in-game) |
| BYOU | A1 (default) | `game/assets/models/steve-fox.glb` | source-game model (Tekken Steve Fox, teardown extraction) | wired | [ ] | [ ] | shared steve-fox base (tint applied in-game) |
| SHA | A1 (default) | `game/assets/models/steve-fox.glb` | source-game model (Tekken Steve Fox, teardown extraction) | wired | [ ] | [ ] | shared steve-fox base (tint applied in-game) |
| JIN | A1 (default) | `game/assets/models/steve-fox.glb` | source-game model (Tekken Steve Fox, teardown extraction) | wired | [ ] | [ ] | shared steve-fox base (tint applied in-game) |
| ZEN | A1 (default) | `game/assets/models/steve-fox.glb` | source-game model (Tekken Steve Fox, teardown extraction) | wired | [ ] | [ ] | shared steve-fox base (tint applied in-game) |
| TOU | A1 (default) | `game/assets/models/pantera.glb` | source-game retexture (Tekken King lineage — shared PANTERA A1 asset) | wired | [ ] | [ ] | shared pantera base (tint applied in-game) |
| KAI | A1 (default) | `game/assets/models/pantera.glb` | source-game retexture (Tekken King lineage — shared PANTERA A1 asset) | wired | [ ] | [ ] | shared pantera base (tint applied in-game) |
| RETSU | A1 (default) | `game/assets/models/pantera.glb` | source-game retexture (Tekken King lineage — shared PANTERA A1 asset) | wired | [ ] | [ ] | shared pantera base (tint applied in-game) |
| GYOU | A1 (default) | `game/assets/models/pantera.glb` | source-game retexture (Tekken King lineage — shared PANTERA A1 asset) | wired | [ ] | [ ] | shared pantera base (tint applied in-game) |
| GYOU | A2 · Spirit form | `roster/gyou/attires/spirit-form/model.glb` | Tripo original (Tripo 6414fa3b ‘fiery face’) | wired | [ ] | [ ] | unvesseled soul; splinter trapped in Cyborg X per CANON.md |
| PANTERA | A1 · T7King reskin (default) | `game/assets/models/pantera.glb` | source-game retexture (Tekken 7 King reskin per ATTIRE-SLOTS.md) | wired | [ ] | [ ] | exempt — showable, Tripo preferred. Slot-doc names 14.7MB t7king ref copy (docs/tpose-refs/pantera-t7king/); wired file is 7.6MB golden-era build — slot swap owned by dedicated Pantera lane. |
| PANTERA | A2 · Leo man | `roster/pantera/attires/leomon/ — model.glb ABSENT (mane/tail pieces only)` | Tripo original (owner-confirmed original Tripo) | broken (path 404s) | [ ] | [ ] | Leo man Tripo model.glb not in repo — Pantera lane owns. 'The one we had in game for so long.' |
| PANTERA | A3 · Snow Leopard reskin | `roster/pantera/attires/snow-leopard/pantera-snow-leopard.glb` | source-game retexture (T7 King P1 base) | not wired | [ ] | [ ] | exempt — showable, Tripo preferred. |
| PANTERA | A4 · Leopard King | `roster/pantera/attires/leopard-king/model.glb` | Tripo original (Tripo 094c2f37, 23.3MB) | not wired | [ ] | [ ] | static — auto-rig in flight (dedicated Pantera lane, carved out of personality RIG lane). Tail must rig properly. |
| PANTERA | A5 · Crimson Rage | `roster/pantera/attires/crimson-rage/pantera-attire5-crimson.glb` | source-game retexture (Creation Suite custom build on King base, texture-only) | not wired | [ ] | [ ] | exempt — showable, Tripo preferred. |
| PANTERA | A6 · T7 P2 | `roster/pantera/attires/p2-wired/pantera-attire4-p2.glb` | source-game retexture (official T7 Player-2 scheme on S1 base) | not wired | [ ] | [ ] | exempt — showable, Tripo preferred. |
| DEMONIO | BASE | `game/assets/models/demonio.glb` | source-game model (Tekken Jin; family-A canonical rig) | wired | [ ] | [ ] | assets.js: ‘Tekken’s Jin = DEMONIO’; old jin: key removed |
| DEMONIO | A1 · Unwinged demon | `roster/demonio/attires/attire1/model.glb` | Tripo original (Tripo 879b6dae) | wired | [ ] | [ ] | owner 2026-10-19: ‘Attire 1 = Tripo unwinged demon’; game default |
| DEMONIO | A2 · Winged Devil | `roster/demonio/attires/winged-devil/model.glb` | Tripo original | wired | [ ] | [ ] | transform target |
| DEMONIO | A3 · Human | `roster/demonio/attires/human/model.glb` | Tripo original | wired | [ ] | [ ] | transform target |
| DEMONIO | A4 · Bloodline Ember | `roster/demonio/attires/bloodline-ember/demonio-bloodline-ember.glb` | source-game retexture (Tekken Jin base, custom reskin; 49-bone canonical rig) | wired | [ ] | [ ] | reskin-wave custom; NOT exempt |
| PHANTOM | A1 · Phantom | `roster/phantom/attires/attire1/model.glb` | Tripo original (Tripo 3ed032a4) | wired | [ ] | [ ] | owner-approved PORTRAIT (2026-10-20) — note, not an attire verdict row |
| PHANTOM | A2 · T8 | `game/assets/models/phantom-t8.glb` | unknown — needs evidence | wired | [ ] | [ ] | ‘T8’ suggests Tekken-8-era in-game model; no provenance audit found |
| DIABLO | A1 (default) | `game/assets/models/diablo.glb` | unknown — needs evidence | wired | [ ] | [ ] | no provenance audit found |
| SKULL | A1 (default) | `roster/skull/attires/attire1/model.glb` | Tripo original (Tripo d77eb53a, Bryan Fury proprietary replacement) | wired | [ ] | [ ] | A2/A3 reserved customs; A4+ Bryan Fury in-game attires (game/assets/models/skull.glb, RigModels fan rip) ladder back — unwired |
| SAM-UR-A1 | A1 (default) | `roster/sam-ur-a1/attires/attire1/model.glb` | Tripo original (Tripo 7c94ba99, floating-forearm rocket-fist) | wired | [ ] | [ ] | replaces fan-rip placeholder; old fan-rip (game/assets/models/sam-ur-a1.glb) ladders back |
| SAKU RA | A1 (default) | `roster/sakura/attires/attire1/model.glb` | Tripo original (Tripo, Oct-16 pull) | wired | [ ] | [ ] |  |
| SAKU RA | A2 · MAIN | `game/assets/models/saku-ra-main.glb` | Tripo original (same Oct-16 pull, byte-identical per registry) | wired | [ ] | [ ] |  |
| ZUI | A1 (default) | `game/assets/models/steve-fox.glb` | source-game model (Tekken Steve Fox, teardown extraction) | wired | [ ] | [ ] | current game default (shared base) |
| ZUI | A2 · Drunken Monk (Tripo) | `roster/zui/attires/attire1/model.glb` | Tripo original (Tripo cdf894fc, 20.7MB) | not wired | [ ] | [ ] | registry default per Tripo law; playable swap rides with auto-rig pass. attires/attire2 (rework v2) also on disk, unwired. |
| KINPO | A1 (default) | `game/assets/models/kinpo.glb` | unknown — needs evidence | wired | [ ] | [ ] | no provenance audit found |
| KINPO | A2 · T8 | `game/assets/models/kinpo-t8.glb` | unknown — needs evidence | wired | [ ] | [ ] | no provenance audit found |
| WATERFALL | A1 (default) | `roster/waterfall/attires/attire1/model.glb` | Tripo original (Tripo, Oct-16 pull) | wired | [ ] | [ ] |  |
| KING TYRANT | A1 · White Tyrant | `roster/king-tyrant/attires/attire1/model.glb` | Tripo original (Tripo 22d9d916) | not wired | [ ] | [ ] | owner’s Tripo build; playable swap rides with auto-rig pass |
| KING TYRANT | A2 · Tyrant King | `roster/king-tyrant/attires/attire2/model.glb` | Tripo original (Tripo 85fb8756) | not wired | [ ] | [ ] | cape = cloth-rig task (auto-rig wave) |
| KING TYRANT | A3 · Black Snow | `roster/king-tyrant/attires/attire3/model.glb` | Tripo original (Tripo fed0d1d3) | not wired | [ ] | [ ] | robe = cloth-rig task |
| KING TYRANT | A4 · Fight Gear | `roster/king-tyrant/attires/attire4/model.glb` | Tripo original (Tripo 3dcb748f) | not wired | [ ] | [ ] | clean — no cloth blockers |
| KING TYRANT | A5 · in-game | `game/assets/models/king-tyrant.glb` | source-game retexture (RigModels fan rip, Eddy lineage; ladders back per slot-order law) | wired | [ ] | [ ] | current game default only because Tripo attires are unrigged statics |
| BURGER | A1 · Demon Mode | `roster/burger/attires/attire1/model.glb` | Tripo original (owner Tripo pull 2026-10-19) | wired | [ ] | [ ] |  |
| BURGER | A2 · Cursed Human | `roster/burger/attires/attire2/model.glb` | Tripo original (owner Tripo pull 2026-10-19) | wired | [ ] | [ ] |  |
| BURGER | A3 · Feral Hunger | `roster/burger/attires/attire3/model.glb` | Tripo original (owner Tripo pull 2026-10-19) | wired | [ ] | [ ] |  |
| BURGER | A4 · Getting Hungry | `roster/burger/attires/attire4/model.glb` | Tripo original (owner Tripo pull 2026-10-19) | wired | [ ] | [ ] |  |
| BURGER | A5 · Mini Tank | `roster/burger/attires/attire5/model.glb` | Tripo original (owner Tripo pull 2026-10-19) | wired | [ ] | [ ] |  |
| BURGER | A6 · Speed Demon | `roster/burger/attires/attire6/model.glb` | Tripo original (owner Tripo pull 2026-10-19) | wired | [ ] | [ ] | transform-chain target (forms data) |
| BURGER | A7 · The Mouth | `roster/burger/attires/attire7/model.glb` | Tripo original (owner Tripo pull 2026-10-19) | wired | [ ] | [ ] | transform-chain target (forms data) |
| AWA POP | A1 (default) | `game/assets/models/awa-pop.glb` | unknown — needs evidence | wired | [ ] | [ ] | slot doc: live-game default NOT swapped — pre-Tripo in-game build; no provenance audit found |
| AWA POP | A2 · Tripo | `roster/awa-pop/awa-pop-attire-1.glb` | Tripo original (Tripo e3d3b06f, ‘muscular superhero’, PR #215) | not wired | [ ] | [ ] | slot-doc default per Tripo law; playable swap rides with auto-rig pass |
| AWA POP | A3 · Attire 2 (Tripo) | `roster/awa-pop/attires/attire2/model.glb` | Tripo original (Tripo d71f4210, ‘muscular female figure’) | not wired | [ ] | [ ] |  |
| SCIMITAR | A1 (default) | `game/assets/models/scimitar.glb` | source-game model (Shaheen base mesh, NO-GATE wire per assets.js) | wired | [ ] | [ ] | clothing via Creation Suite optional |
| PURPLE RAIN | A1 (default) | `roster/purplerain/attires/attire1/model.glb` | Tripo original (Tripo, Oct-16 pull) | wired | [ ] | [ ] |  |
| PURPLE RAIN | A2 · MAIN | `game/assets/models/purple-rain-main.glb` | Tripo original (same Oct-16 pull, byte-identical per registry) | wired | [ ] | [ ] |  |
| NIGHTWOLF | A1 (default) | `game/assets/models/steve-fox.glb` | source-game model (Tekken Steve Fox — roster-full default model) | wired | [ ] | [ ] | tribute to Serena Misae Brown; Tripo swap pending auto-rig |
| NIGHTWOLF | A2 · Tribal Warrior (Tripo) | `roster/nightwolf/attires/attire1/model.glb` | Tripo original (Tripo 5b0835eb, 21.87MB) | not wired | [ ] | [ ] | slot-doc default per Tripo law; base game/assets/models/nightwolf.glb (wired key, audit pending) ladders back |
| DIO | A1 (default) | `game/assets/models/dio.glb` | community rip (Akuma — Lane C fighter-hunt) | wired | [ ] | [ ] | 174-bone foreign rig; engine cannot animate canonically |
| CYBORG X | A1 (default) | `game/assets/models/cyborg-x.glb` | unknown — needs evidence | wired | [ ] | [ ] | no provenance audit found |
| CYBORG X | A2 · Cape Jones | `game/assets/models/cape-jones.glb` | Tripo original (Tripo, Oct-16 pull) | wired | [ ] | [ ] | canon: Cape Jones = Cyborg X Attire 1 (owner 2026-10-16) |
| MICHIKO | A1 (default) | `game/assets/models/michiko.glb` | community rip (Katarina lineage — Lane C fighter-hunt) | wired | [ ] | [ ] | 33-bone canonical rig |
| STAR | A1 · Red Latex (default) | `roster/star/attires/attire1/model.glb` | Tripo original (Tripo ea73eeb3) | not wired | [ ] | [ ] | owner 2026-10-18: ‘That’s her attire 1’; playable swap rides with auto-rig pass |
| STAR | A2 · After Dark | `roster/star/attires/attire2/model.glb` | Tripo reskin-of-source (Tripo base colorway — black latex; NOT rated-M per owner 2026-10-19) | not wired | [ ] | [ ] |  |
| STAR | A3 · Capoeira Gold | `roster/star/attires/attire3/model.glb` | Tripo reskin-of-source (Tripo base colorway — Brazil green/yellow) | not wired | [ ] | [ ] |  |
| STAR | A4 · Classic | `game/assets/models/star.glb` | community rip (fighter-hunt ‘Classic’; ships untextured clay — texture pass queued, never a gate) | wired | [ ] | [ ] | current game default. Rated-M roadmap (attires/attire5) is a separate in-flight lane — not listed. |
| TORCH | A1 (default) | `game/assets/models/torch.glb` | community rip (Anna lineage — Lane C fighter-hunt) | wired | [ ] | [ ] | 33-bone canonical rig |
| BRUNO | A1 (default) | `game/assets/models/bruno.glb` | community rip (Miguel lineage — Lane C fighter-hunt) | wired | [ ] | [ ] | 142-bone foreign rig |
| N3GΔTIV0 | A1 (default) | `game/assets/models/n3g4tiv0.glb` | unknown — needs evidence | wired | [ ] | [ ] | no provenance audit found |
| THOR | A1 (default) | `roster/thor/attires/attire1/model.glb` | Tripo original (Tripo 65ff7ad8) | wired | [ ] | [ ] |  |
| THOR | A2 · Oni Mask | `roster/thor/attires/attire2/model.glb` | Tripo original (Tripo c85dc47b, ‘phantom mimic oni mask’) | wired | [ ] | [ ] | thor_alt1.glb planned later slot |
| YUKIHYŌ | A1 (default) | `game/assets/models/yukihyo.glb` | unknown — needs evidence | wired | [ ] | [ ] | no provenance audit found; 328-bone canonical-names rig |
| SLICE | A1 (default) | `game/assets/models/steve-fox.glb` | source-game model (Tekken Steve Fox — shared base) | wired | [ ] | [ ] | shared steve-fox base (tint applied in-game) |
| DOC FRANK | A1 · Old Man | `game/assets/models/doc-frank.glb` | source-game model (Tekken Dr. Bosconovitch, teardown extraction) | wired | [ ] | [ ] | 178-bone foreign rig; mid-match transform → A2 |
| DOC FRANK | A2 · Transformed | `roster/doc-frank/attires/attire1/post-transform/model.glb` | Tripo original (Tripo 597c67b3, 20.6MB) | wired | [ ] | [ ] | Roshi-style transform target (2c6cff79 = true target) |
| DOC FRANK | A3 · Wowomomo | `roster/doc-frank/attires/attire2/base/model.glb` | Tripo original (Tripo 84b128d2) | wired | [ ] | [ ] | two-form: transform → A4 |
| DOC FRANK | A4 · Wowomomo XL | `roster/doc-frank/attires/attire2/transformed/model.glb` | Tripo original | wired | [ ] | [ ] |  |
| DOC FRANK | A5 · Hood Scientist | `roster/doc-frank/attires/attire3/base/model.glb` | Tripo original | wired | [ ] | [ ] | two-form: transform → A6 |
| DOC FRANK | A6 · Hood XL | `roster/doc-frank/attires/attire3/transformed/model.glb` | Tripo original | wired | [ ] | [ ] |  |
| DOC FRANK | A7 · Frankenstein | `roster/doc-frank/attires/attire4/base/model.glb` | Tripo original (Tripo 2bea6cac) | wired | [ ] | [ ] | two-form: transform → A8; in attires.js only via MODEL_URLS (attires.js ladder missing this pair — wiring gap flagged) |
| DOC FRANK | A8 · Frankenstein XL | `roster/doc-frank/attires/attire4/transformed/model.glb` | Tripo original (Tripo 690d28a2) | wired | [ ] | [ ] |  |
| DOC FRANK | A9 · Machine Shop | `roster/doc-frank/attires/machine-shop/doc-frank-machine-shop-rigged.glb` | source-game retexture (Bosconovitch retexture, PR #263 reskin) | wired | [ ] | [ ] | texture-transplant onto rigged base |
| KEVIN | A1 · Kevin (Tripo) | `roster/baek/attires/attire1/model.glb` | Tripo original (Tripo 86d12371, 12.1MB — his face) | not wired | [ ] | [ ] | file present in repo (12.1MB static); NO game key yet — auto-rig lane in flight (top priority). Kevin kick proof runs on THIS model. |
| KEVIN | A2 · original Baek | `game/assets/models/baek.glb` | source-game model (RigModels fan rip — Baek) | wired | [ ] | [ ] | former default; now Kevin’s later attire per owner directive |
| KEVIN | A3 · Master White | `roster/baek/attires/master-white/baek-master-white-rigged.glb` | source-game retexture (Baek-model retexture, PR #265) | wired | [ ] | [ ] | PARKED — owner verdict (2026-10-20 ~14:19 CDT): weak attire, unused, never shown as the character. NOT MARKABLE. |
| MARIPOSA | A1 · Butterfly (Tripo) | `game/assets/models/mariposa.glb` | Tripo original (original Tripo butterfly, eyes on wings — Tripo 187bb8a9) | wired | [ ] | [ ] | owner-settled slot 1 (2026-10-20) |
| MARIPOSA | A2 · Monarch | `roster/mariposa/attires/monarch/mariposa-monarch-rigged.glb` | Tripo reskin-of-source (PR #271 texture-transplant on Tripo base) | wired | [ ] | [ ] | exempt — showable. Blue Morpho / Luna Moth (A4/A5) in build, unwired; Zafina in-game models ladder back later. |
| MARIPOSA | A3 · Slot 2 pull | `roster/mariposa/attires/slot2/model.glb` | Tripo original (same Oct-16 pull as A1, byte-identical per registry) | wired | [ ] | [ ] | duplicate of A1’s pull — consolidation candidate |
| DXMMII | A1 (default) | `game/assets/models/dxmmii.glb` | Tripo original (Tripo ca068026, Oct-16 pull; auto-rig wave 2026-10-18) | wired | [ ] | [ ] | the subject of all proofs — never the Patchwork reskin |
| DXMMII | A2 · Blockhead | `roster/dxmmii/attires/attire2/model.glb` | Tripo original (‘block built blockhead crash dummy’, PR #323) | wired | [ ] | [ ] |  |
| DXMMII | A3 · Patchwork DJ | `roster/dxmmii/attires/patchwork-dj/dxmmii-patchwork-rigged.glb` | Tripo reskin-of-source (custom reskin on Tripo base) | wired | [ ] | [ ] | NO exemption — Patchwork reskin row gets no flag |
| ZANGIEF | A1 (default) | `roster/zangief/attires/attire1/model.glb` | community rip (Sketchfab CC-BY johnny136) | wired | [ ] | [ ] |  |
| BLANKA | A1 (default) | `roster/blanka/attires/attire1/model.glb` | community rip (Sketchfab Free Standard allanromanreyes) | wired | [ ] | [ ] | being REPLACED by CHARGER (owner 2026-10-20 ~13:32 CDT) — files stay in repo, fighter entry changes |
| CHARGER | A1 (default) | `roster/charger/attires/attire1/model.glb — PLANNED (pull in ~/workspace/tripo-recovery/charger_attire1/)` | Tripo original (Tripo b91318ce, ‘ice monster’) | not wired | [ ] | [ ] | NEW proprietary fighter = Blanka replacement (owner 2026-10-20 ~13:32); ice + electricity; pull+wire lane in flight |
| CHARGER | A2 | `roster/charger/attires/attire2/model.glb — PLANNED (pull in ~/workspace/tripo-recovery/charger_attire2/)` | Tripo original (Tripo f87e24eb, ‘green spiky creature’) | not wired | [ ] | [ ] | charger.json = Blanka’s 199-move set, ice/electric signature renames |
| VEGA | A1 (default) | `roster/vega/attires/attire1/model.glb` | community rip (Sketchfab CC-BY pierodsoto01) | wired | [ ] | [ ] | 364-bone foreign rig |
| IORI | A1 (default) | `roster/iori/attires/attire1/model.glb` | community rip (Sketchfab CC-BY 0xo) | wired | [ ] | [ ] | 79-bone KOF rig, 61 native clips |
| ARMOR KING | A1 (default) | `roster/armor-king/attires/attire1/model.glb` | community rip (Sketchfab CC-BY theamazingdonovan207) | wired | [ ] | [ ] | unrigged statue |
| KRONOS | A1 (default) | `roster/kronos/attires/attire1/model.glb` | Tripo original (Tripo 6cca2267) | wired | [ ] | [ ] |  |
| KRONOS | A2 · TimberWolf | `roster/kronos/attires/attire2/model.glb` | Tripo original (Tripo 40013fc2, Wolverine-inspired) | wired | [ ] | [ ] |  |
| KRONOS | A3 · TimberWolf Suited | `roster/kronos/attires/attire3/model.glb — NOT ON MAIN (PR #378 open)` | Tripo original (Tripo 93e4961f, 21.5MB) | not wired | [ ] | [ ] | Tripo pull verified in ~/workspace/tripo-recovery/kronos_attire3_timberwolf_suited/. Owner 2026-10-20 ~17:00 REJECTED the yellow-pants recolor variant — use the stock A3 GLB untouched. |
| DEATHFANG | A1 · The Chained Prisoner | `roster/deathfang/attires/attire1/model.glb` | Tripo original (owner 2026-10-20: Tripo originals) | wired | [ ] | [ ] | CONFLICT: 2026-10-19 slot doc called A1 an Iori reskin; owner 2026-10-20 declares Deathfang 1+2 = owner Tripo originals. DEATHFANG lane in flight — re-audit when it lands. |
| DEATHFANG | A2 · Chained Prisoner Werewolf | `roster/deathfang/attires/attire2/model.glb` | Tripo original (owner 2026-10-20: Tripo originals) | broken (path 404s) | [ ] | [ ] | path 404s — werewolf transform follow-up lane; other lane’s Tripo not yet in repo |
| RYUJI | A1 (default) | `game/assets/models/steve-fox.glb` | source-game model (Tekken Steve Fox — shared base) | wired | [ ] | [ ] | shared steve-fox base (tint applied in-game) |
| RYUJI ROCK | A1 (default) | `roster/ryuji-rock/attires/attire1/model.glb` | unknown — needs evidence | broken (path 404s) | [ ] | [ ] | MODEL PENDING by design — no Yamazaki model found; lands the moment the owner sends a Tripo link (see roster/ryuji-rock/attires/attire1/README.md) |
| KORESHI | A1 (default) | `roster/koreshi/attires/attire1/model.glb` | Tripo original (Tripo 034bb96f, owner’s own creation) | wired | [ ] | [ ] |  |

## Totals

- Rows: **101**
- Tripo-original: **53**
- Source-game retextures: **12** (incl. 1 parked)
- Source-game models: **13**
- Community rips: **10**
- Tripo reskin-of-source: **4**
- Unknown — needs evidence: **9**
- Wire: wired **79** · not wired **19** · broken (404) **3**

## Pre-marked by the owner (do not re-mark)

- **KEVIN A3 · Master White — PARKED** (owner verdict 2026-10-20 ~14:19 CDT): weak attire, unused, never shown as the character. Both verdict columns stay blank.
- **Exempt — showable, Tripo preferred (Pantera):** A1 T7King reskin, A3 Snow Leopard reskin, A5 Crimson Rage, A6 T7 P2.
- **Exempt — showable:** MARIPOSA A2 Monarch.
- **No exemption:** DXMMII (all rows, incl. Patchwork reskin).
- **Rejected:** KRONOS A3 yellow-pants recolor variant (owner 2026-10-20 ~17:00 CDT: ‘Man u changed the color of the claws’) — use the stock A3 GLB untouched; no hand-tooled recolor jobs.

## Unknowns (needs evidence — where I looked)

- `game/assets/models/phantom-t8.glb` — ‘T8’ suggests a Tekken-8-era in-game model; looked at MODEL_URLS comment (round-2 auto-rig wave block), slot docs, registry, memory — no audit on record.
- `game/assets/models/diablo.glb` — no slot doc, no registry row, no audit.
- `game/assets/models/kinpo.glb`, `game/assets/models/kinpo-t8.glb` — no slot doc, no audit.
- `game/assets/models/awa-pop.glb` — slot doc says the live-game default was NOT swapped to the Tripo pulls; the wired file’s provenance unaudited (Tripo pulls live unwired at roster/awa-pop/).
- `game/assets/models/cyborg-x.glb` — no slot doc coverage; canon A1 is the Cape Jones Tripo (separate file).
- `game/assets/models/n3g4tiv0.glb` — no provenance audit.
- `game/assets/models/yukihyo.glb` — 328-bone canonical-names rig; no slot doc/audit.
- `roster/ryuji-rock/attires/attire1/model.glb` — 404 by design (MODEL PENDING; owner to send Tripo link).

## Wiring gaps flagged (not verdicts)

- PANTERA A2 Leo man: `roster/pantera/attires/leomon/model.glb` absent from repo (only mane/tail pieces) — owned by the dedicated Pantera lane.
- KEVIN A1: `roster/baek/attires/attire1/model.glb` present (12.1MB) but has NO game key — auto-rig lane in flight.
- DEATHFANG A2 werewolf: path 404s — follow-up lane; other lane’s Tripo not yet in repo.
- KRONOS A3: not on main (PR #378 open, branch `feat/kronos-attire3-timberwolf-suited`).
- CHARGER A1/A2: not in repo at all (lane in flight; pulls in `~/workspace/tripo-recovery/charger_attire1|2/`).
- DOC FRANK A7/A8 (Frankenstein pair): wired via MODEL_URLS keys but missing from attires.js’ doc-frank ladder — ladder gap flagged.

## Back-catalog / ladder-back models (not fighter attires — no owner verdict needed)

| Model key(s) | Repo path | Provenance | Notes |
|---|---|---|---|
| cape-jones | `game/assets/models/cape-jones.glb` | Tripo original (Tripo, Oct-16 pull) | no fighter key uses it; canon = Cyborg X Attire 1 |
| rave / kiko-tanaka | `game/assets/models/rave.glb + kiko-tanaka.glb / kiko-tanaka_alt1.glb` | source-game model (Lei Wulong in-game base) + Tripo x2 | KIKO TANAKA = RAVE merged (owner 2026-10-19) |
| lili | `game/assets/models/lili.glb` | source-game model (unassigned; ‘NO WH name yet’ — retired name, see SILVERTONGUE) | do not assign |
| zafina | `game/assets/models/zafina.glb` | source-game model (T6 Zafina) | Mariposa A6+ ladder-back target |
| skull (base) | `game/assets/models/skull.glb` | source-game retexture (RigModels fan rip, Bryan Fury) | SKULL A4+ ladder-back |
| nightwolf (base) | `game/assets/models/nightwolf.glb` | unknown — needs evidence | NIGHTWOLF A2 ladder-back; audit pending |
| phantom (base) | `game/assets/models/phantom.glb` | unknown — needs evidence | PHANTOM ladder-back per slot doc; not in game/js keys |
| king-tyrant_alt1 | `game/assets/models/king-tyrant_alt1.glb` | source-game retexture (RigModels fan rip, Eddy) | KING TYRANT later slot |
| *-body / *_alt1 / zui_alt1-2 / kinpo_alt1 | `game/assets/models/ (round-2 auto-rig wave re-rigs)` | re-rigged per-fighter variants | playable-gate passing variants; not fighter attires |
| custom (CAW) | `customization/create-fighter/assets/Soldier.glb` | Creation Suite base | Created fighters use this base |

---
Sources: game/js/attires.js, game/js/roster-full.js, game/js/assets.js (main, via gh api 2026-10-20); roster/*/ATTIRE-SLOTS.md; roster/TRIPO-REGISTRY.md; ~/workspace/wh-pose-survey/inventory.jsonl; checkpoint wh-pose-isolation.json (27 notes). No repo edits, no PRs.
