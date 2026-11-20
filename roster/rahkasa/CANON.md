# CHATUR — CANON

### CHATUR — The Bridge Soul

**Category.** Spirit fighter. Not one of the nine souls. An Oversoul — a spirit wearing a body the way other fighters wear attires. GYOU-touched.

**Backstory.** She was a temple dancer at the Octagonal Shrine Par-fang, at the foot of the Central Mountain — the Source, the still point of the head. She danced the old dances, the ones that ask the body to say what the mouth can't. When her dying came, she refused it.

In the Western Heart, death is not failure — it is the mechanism. The soul loses, dies, and is reborn before the next round, choosing a new face. This is the Reincarnation, and every fighter knows it. Chatur is the one who said no. When her turn came, she did not take a new face. She kept dancing. The dance kept her.

What came back was not the dancer. It was the dance, wearing her — an Oversoul with four arms. Two are hers, the ones she was born with. Two are the spirit realm's, reaching through her into the living trial. That is what a bridge is: a place where one side reaches through to the other and holds.

She anchors the spirit realm the way the shrine anchors the head — still, central, load-bearing. The dead pass over her on their way to their new faces. She does not pass. She holds.

**GYOU-touched.** Gyou is motion itself and cannot stop moving. He did not teach her — he recognized her. The mark he left: she cannot stop either. Her dance has no ending, only continuations.

**Trained by Megami.** Before the refusal, before the four arms — Megami, the temple guardian, trained her. Grief in motion taught the dancer who would not stop. Megami guards a sealed door. Chatur became one.

**Personality.** Stillness inside motion. She sways even when she is standing still — a temple-dancer's idle, the four arms resting in mudra positions. Speaks rarely, and when she does it lands like a bell struck once. No cruelty in her. No mercy either — bridges don't choose who crosses.

**Fighting philosophy.** *"Stopping is dying. I already did that once."*

**Relationships.**
- **MEGAMI:** Trained her, back when she had two arms and a name the shrine stones still remember. Megami guards a sealed door; Chatur became a door. They do not speak of it.
- **GYOU:** Motion itself. He marked her the way weather marks stone — without asking, without malice. She dances; he moves; neither stops.
- **ZEN:** His spirit floats behind his body. Hers IS the body. They are the same sentence written backwards. He watches her the way you watch a mirror that moves first.
- **POND:** The swamp boundary watcher. Chatur is the bridge; Pond watches the banks. Old friends — the kind who don't need to talk.
- **DOROWANI:** She was there when Pond's egg hatched. She doesn't say what she saw. He barks his Japanese words at her and she answers in mudras.
- **BIRODO:** The Velvet Room is neutral ground; a bridge is neutral ground too. Birodo keeps a table for her. Neutral recognizes neutral.
- **The Trader:** At the Phantom Marketplace, under the Eyeball Mountains. Crossings have tolls, and the Trader collects. *All transactions are final. Nothing here is real, but the prices are.*

**Element.** Earth — the Octagonal Shrine, the Source. The bridge anchors at the center of the head. Her fights live there even when the arena doesn't.

**Body / Mind / Soul.** BODY: the four-armed spirit body — two arms the dancer's, two the spirit realm's reaching through. MIND: the dance — she thinks in rhythm, in mudras; language arrives late and leaves early. SOUL: an Oversoul, vesseled by none of the nine. No shrine stone names her. The dead know her by the sway.

**Why she thinks she's here.** She thinks the trial is a dance that never ends, and she is finally in the right room. She is not wrong.

**Being purified of:** The refusal. She refused death; the trial is teaching her that stopping isn't dying — it's the part of the dance where you breathe. She hasn't learned it yet. She may never. The trial keeps her anyway. Bridges don't get to leave.

**Signature detail.** Her shadow has only two arms — the shape of the dancer she was, before the spirit realm lent her the other two. Fighters who notice it stop watching her arms and start watching her shadow. It doesn't help.

**Voice.** Sparse, imagistic, Japanese-influenced. Short lines, long silences. *"Mata ne."* / *"The bridge holds."* / *"Dance."*

---

## Technical (non-canon — crew plumbing only)

- **Model (SmutBase intake 2026-10-22):** Attire 1: `roster/rahkasa/attires/attire1/model.glb` (3.7 MB). Single mesh (`ReVAmped_body_base_female_standard`), unrigged static — no skins. Source `.blend` (`roster/rahkasa/intake/RahkasaV1.1.blend`): body (`OBRahkasaBody`), hair (`OBRahkasaHair`), rigs (`OBRahkasaRIG`, `OBRahkasaRIG_Deform`), IK/rig widgets (`OBWGT*`).
- **Four arms verified:** rig bone inspection of the decompressed `.blend` shows four forearm chains per side (`forearm.L/.001/.002/.003`, same on R) — the extra arm pairs are real geometry, not a texture trick.
- **Moveset:** True Ogre's Tekken 3 kit — `game/assets/movesets/chatur.json` (52 moves, 7 strings, 5 specials, 2 stances), translated from `teardown/tekken3/movesets/moveset_ogre.json` (bank `divmot14_ogre.bin`, 330 rows) via `game/assets/movesets/t3-ogre.json`. Canon specials layered on top: FOURFOLD MUDRA, OVERSOUL SURGE, GYOU'S MARK, REFUSED TO DIE, BRIDGE OF ARMS. Tekken inputs (1/2/3/4 + directions), 1:1 input-to-move fidelity per the owner's feel law.
- **Ogre replaced:** Ogre is REPLACED by Chatur (owner 2026-10-22). Ogre stays in the repo as Tekken reference only (`t3-ogre.json`, teardown bank) — never as a WH fighter.
- **Rig lane:** k-NN auto-rig from donor is the planned path (unrigged static, like the other SmutBase intakes).

*Bio written 2026-10-23, canon-grounded (Tong-Nou, Nine Souls, Five Lands, Trial, Trader). Adults only. No Tekken names in canon — moveset source lives in the technical section only.*
