# Owner-model-first audit (2026-10-23)

Owner order pt213u: every fighter's own model is ATTIRE 1 (select card, 3D hero render, fights). Source-game ports, reskins and retextures are laddered back, never deleted. Enforced by `test/owner-model-first.test.mjs` against `game/data/owner-models.json`.

## Swapped in this PR

| Fighter | New attire 1 (owner) | Laddered back |
|---|---|---|
| negativo | negativo-attire1 (Tripo, red eyes), then negativo-attire2 | n3g4tiv0 (Negan/Tekken reskin) |
| dio | dio-attire1 (Tripo, jade god) | dio (Akuma source port) |
| bruno | bruno-attire2 (Tripo, rigged) then bruno-attire1 (Tripo, unrigged) | bruno (Miguel source port) |
| yukihyo | yukihyo-attire1..3 (Tripo) — un-hides him (legacy attire was quarantined) | yukihyo (Armor King T8 port), armor-king entries |
| awapop | awa-pop-attire2 (Tripo) | awa-pop (Nina-style port) |

Fight path: `randomEnemy` and explicit enemy ids now go through `resolveFighterAttire`, so CPU opponents also wear attire 1 instead of the raw roster key (affected kingtyrant, nightwolf, michiko, star, baek whose raw keys point at legacy GLBs).

## Already owner-first (no change)

- **zen**: zen-attire1
- **demonio**: demonio-a1
- **phantom**: phantom
- **diablo**: diablo
- **skull**: skull, skull-tripo
- **samura1**: sam-ur-a1
- **sakura**: saku-ra
- **zui**: zui-attire1
- **kinpo**: kinpo, kinpo-attire2
- **waterfall**: waterfall, waterfall-attire1
- **kingtyrant**: king-tyrant-attire1, king-tyrant-attire2, king-tyrant-attire3, king-tyrant-attire4
- **burger**: burger
- **awapop**: awa-pop-attire2
- **purplerain**: purple-rain
- **nightwolf**: nightwolf-attire1
- **dio**: dio-attire1
- **cyborgx**: cape-jones
- **michiko**: michiko-attire1, michiko-attire2
- **star**: star-attire1
- **torch**: torch-tripo-a1, torch-tripo-a2
- **bruno**: bruno-attire2, bruno-attire1
- **negativo**: negativo-attire1, negativo-attire2
- **thor**: thor, thor-attire2
- **yukihyo**: yukihyo-attire1, yukihyo-attire2, yukihyo-attire3
- **slice**: slice-attire1
- **docfrank**: doc-frank-big, doc-frank-wowomomo, doc-frank-wowomomo-big, doc-frank-hood, doc-frank-hood-big, doc-frank-frankenstein, doc-frank-frankenstein-big, doc-frank-a1
- **baek-master-white**: kevin-tripo
- **mariposa-monarch**: mariposa-butterfly-default, mariposa
- **dxmmii-patchwork**: dxmmii-tripo
- **charger**: charger
- **dorowani**: dorowani
- **kronos**: kronos
- **deathfang**: deathfang
- **ryuji**: ryuji-rock
- **koreshi**: koreshi, koreshi-attire1
- **rave**: kiko-tanaka
- **buffalo-bill**: buffalo-bill
- **vainabel**: vainabel-attire1
- **cainelias**: cain-elias
- **chordz**: chordz

## Exempt / flagged

- **pantera** — exempt per roster/TRIPO-REGISTRY.md marker. CONFLICT: the marker says "EXCEPTION — PANTERA (SUPERSEDED 2026-10-21)", attires.js already leads with his Tripo, but roster-full.js model is still "pantera". Left untouched pending owner decision.
- **scimitar** — no owner model wired; still legacy scimitar-rigged.glb (a scimitar-a1 auto-rig proof exists).
- **ryusan** — uses roster/mina-ashido/attires/attire1/model-rerig.glb; needs owner review.
- **awapop** — slot-1 Tripo roster/awa-pop/awa-pop-attire-1.glb is not on main (only in old history/deploy commits); attire2 Tripo leads.
- Pending (no model): rin, byou, tou, sha, kai, retsu, gyou. Hidden (no usable attire): chatur, pond, tobi, megami, menajerii.

## Gates

All new defaults are material-status ok. Portraits regenerated: all five captured in stance (no T-pose), manifest models match attire 1. Rig proofs: docs/proof/2026-10-23/auto-rig-*. Select proofs (390x844): docs/proof/2026-10-23/owner-model-first/.
