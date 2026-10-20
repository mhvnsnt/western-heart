# Development Conversation Record — 2026-10-20 (Morning)

Source: the "original Western Heart convo" chat, owner (Real) + main agent.
All times America/Chicago (CDT), 2026-10-20. Owner quotes are VERBATIM voice
transcripts — his exact words are the law of this project, so they are recorded
exactly as spoken, typos and all. Sections marked HONEST-STATUS are the
assistant's verified status reports, not owner directives.

---

## ⭐ THE ACCEPTANCE BAR (owner, 2026-10-20 ~08:08 CDT)

**The game must actually FEEL like playing a Tekken game. Right now it does
not.** That is the bar everything in this record is measured against. Wiring
counts, teardown percentages, and PR numbers do not substitute for it. The
proprietary/authorship pass comes AFTER this bar is met, not before.

Owner's words: "it actually starts to feel like I'm playing a Tekken game
because right now it doesn't".

---

## 1. Context — where things stood when this conversation started

- Tekken 5 ISO recovery completed 2026-10-20 ~04:54 CDT after a cleanup lane
  deleted the local copy on 2026-10-19: re-downloaded from archive.org,
  MD5-verified byte-perfect, mirrored to GitHub release `tekken5-iso-v1`
  (mhvnsnt/game-reverse-engineering, 9 parts + SHA256SUMS). The "93%" figure
  in the original incident report was a bad denominator; the deleted file was
  in all likelihood already 100% complete.
- Prior Tekken 5 RE already in hand: TK5DATA3.BIN entry table mapped,
  obfuscation keystream partially recovered (PR #17 merged,
  game-reverse-engineering main e36621d). Resume point: the loader /
  deobfuscator in SLUS_210.59.ELF.
- The three orders below were given back to back between 07:46 and 08:08 CDT.

## 2. The Tekken 5 order (07:46 CDT)

Owner, verbatim:

> "Okay, it's Teardown decoding decryption and extraction time. For Tekken 5,
> get it done fully 100% all the characters all the move sets all the
> character customization and creation suite all of the devil within mode all
> of the cut scenes story mode all of the animations every single piece of it
> tore down and wired up into our game and I'm reverse engineered with
> Ghidra and MCP and goddamn try and get this understanding all the agents
> and everything working on this understanding real game production and
> development states and like the the stages and like the the phases and
> steps that they take and like the things the actual things and files and
> code they have like 100% so they can actually see what it's like to be like
> someone like Tekken or Street Fighter or like someone building a real
> fighting game not guessing and bullshitting a fucking bullshit prototype
> like how AI does but like how real people build a game. Like with your real
> eyes hands and thoughts and like actually being intentional with all the
> fucking steps through the phase towards a goal not just randomly
> bullshitting hodgepodge of prototype"

What this orders:

- Tekken 5 (PS2, SLUS_210.59) to a FULL 100% teardown per the
  TEARDOWN-COMPLETION LAW: extracted, decrypted, decoded, AND assembled.
  Every character, every moveset, all animations, customization / creation
  data, the complete Devil Within mode, cutscenes and story mode, stages,
  audio. Wired into Western Heart.
- Method: Ghidra + MCP and the full RE toolchain. NO hand-tooling, no
  prototype guessing.
- The production documentation is a deliverable in its own right: how the
  game is REALLY built (disc layout, archives, modules, data pipeline, the
  phases development moves through), written into the repos so the whole
  team learns real fighting-game production.

Dispatched ~07:47 CDT: Tekken 5 teardown coordinator lane (fan-out:
deobfuscation, archives, characters, animation/movesets, Devil Within,
story/audio, stages, customization, production docs, WH wiring).
Checkpoint: `agent-ops/checkpoints/tekken5-teardown.json`.

## 3. The completion sweep order (07:49 CDT)

Owner, verbatim:

> "Yeah and get all of that done and all the games in our tear down list and
> everything all the modes every single piece every single file from all the
> tear down games 100% wired up starting with the one that's closest to 100%
> while you do that decryption and tear down and decoding of Tekken 5"

Dispatched ~07:50 CDT: teardown completion sweep coordinator, working the
remaining games closest-to-100% first, in parallel with Tekken 5:

1. Urban Reign (~95%)
2. Tekken 6 PSP (~90%)
3. DOA4 (completion claim to be verified first)
4. Def Jam: Fight for NY (ISO ~31.5% downloaded)
5. Soulcalibur II (~60%)
6. Street Fighter EX trilogy
7. Tekken Tag Tournament 2 (disk-gated restart)

Already at 100% and untouched by the sweep: Tekken 3, WWF No Mercy,
Eastern Mind. VF5 is extraction-complete (conversion blocked on tooling,
document only). SFV is not acquired (list only).

## 4. The program is 8 games + the research mandate (07:59 CDT)

Owner, verbatim:

> "Okay, that list of one, two, three, four, five, six and seven and then
> you'll have to add number eight taking five onto there and um yeah all of
> those start doing those from the one that's closest to 100% down and get
> them all tore down fully descripted fully decoded fully deciphered use
> Ghidra and MCP wherever needed and any other industry standard things we
> need for reverse engineering tear down and camera builds of games do heavy
> research and pull in and wire up everything into the repo that we need and
> get all that done efficiently optimized and um the highest quality
> possible"

The TEARDOWN PROGRAM, final form:

1. Urban Reign
2. Tekken 6 PSP
3. DOA4
4. Def Jam: Fight for NY
5. Soulcalibur II
6. Street Fighter EX trilogy
7. Tekken Tag Tournament 2
8. Tekken 5 (keeps its own parallel coordinator from section 2; the sweep
   does not duplicate it)

Plus, for all 8: fully decrypted, decoded, deciphered; Ghidra + MCP + any
industry-standard RE tools needed; HEAVY RESEARCH first, pull in and wire up
everything needed into the repos; efficient, optimized, highest quality
possible. The update was sent to both coordinators the same hour.

## 5. The wiring question + the honest status (08:01–08:03 CDT)

Owner, verbatim:

> "is 100% of taking three no mercy Wrestlemania 19 and Eastern Mind already
> 100% wired up in every way using all of their files and turning them into
> proprietary Eastern Mind Western Heart files and the whole thing that we're
> doing how we're doing like this branch off of the canon and story of
> Tonio's Eastern Mind that's completely like fine because that's a really
> old game isn't it like nobody's going to come after me for that using their
> characters using their influence using the eastern mind influence I know
> everything else is more likely for them to come after me but that's getting
> really um edited and really customized and made really proprietary to me
> but that eastern mind stuff is the stuff I'm least worried about them
> coming after me for but I still want to know because we're using their
> stuff the most exact while we're changing most of the other stuff and
> files from the other games like to proprietary names and stuff like that."

### HONEST-STATUS NOTE — the answer given (assistant, 08:03 CDT)

- The four teardowns (Tekken 3, No Mercy, WrestleMania XIX, Eastern Mind)
  are 100% torn down and their teardown folders sit in western-heart on
  main, verified that morning: `teardown/tekken3/`, `teardown/wwf-no-mercy/`,
  `teardown/wmxix/`, `teardown/eastern-mind/`.
- The big systems are wired into the playable build: Tekken 3 movesets live,
  No Mercy wrestling + customization systems in, WMXIX modes + arena
  traversal, Eastern Mind world + lore as the game's backbone.
- NOT claimed: "every single file wired in every way." The build is still
  growing into the teardowns (story / reincarnation depth still shallow).
  Assistant's words: "Teardown complete and stored? Yes, verified. Every
  last file driving gameplay? Not yet, and I won't claim it till it's
  audited file by file." That audit is what section 6 ordered.
- On the Eastern Mind question, the honest picture as given: copyright does
  not expire because a work is old; Tong-Nou / Eastern Mind (1995) is still
  protected for decades yet. Old means low attention, not no rights; the
  obscurity makes practical enforcement attention unlikely, but the legal
  weight sits on exactness of use, not age. Transformation toward his own
  expression is what protects the work. Not legal advice; if Western Heart
  goes commercial in a serious way, an IP lawyer read on the Eastern Mind
  layer specifically is the one consult worth paying for.
- Public domain (owner, 08:08 CDT, verbatim): "And I did learn, bro,
  copyright does expire when something gets really old. That's when it's
  called things going public." / "Yeah, public domain yeah I know about
  that". Recorded note: agreed on the principle; the only nuance is the
  timeline (a 1995 work's term runs to roughly the 2090s). The owner is
  settled on his Eastern Mind position; no more lecturing.

## 6. Full wiring + canon conversion order (08:06 CDT)

Owner, verbatim:

> "yeah we need to wire everything from those files and verify a hundred
> percent that everything gets used nothing get overlooked anything that
> needs to be transformed to something that goes into my universe or world
> so we can like get it more authored and copyright to my world we'll do
> that and like like I said animations and movements and stuff no matter how
> authored they are bro you can't really come after anybody for movements no
> matter how close the movements are if we get the animations and movements
> renamed and slightly tweaked not broken or hand tool but just like done in
> high high really high standard high quality industry standard ways then
> we'll be able to make the moves and stuff proprietary to my universe as
> well in a way without altering them too much and same for anything else
> that's proprietary to other people's copyright or games or stuff like that
> we'll start renaming it getting it put over into our universe's canon and
> all of that but the eastern mind stuff like like I said it's such an
> obscure 1995 art game computer game it's not even a franchise thing that
> literally the eastern mind I could literally build a whole universe based
> off of that and use it and talk about it and it'll definitely be looked at
> as an inspiration piece more than um stealing or copyright same with the
> rest of the game and just that fact itself how i'm bringing that in it
> really customizes everything else and makes everything else proprietary to
> me as well"

The order, in substance:

- For the 4 complete teardowns (Tekken 3, No Mercy, WMXIX, Eastern Mind):
  wire EVERYTHING from their files into Western Heart and verify 100% that
  everything is used, nothing overlooked. File-level inventory per game is
  the checklist.
- Transform and rename everything third-party into Western Heart canon so
  it is authored to his world, with rename-map discipline (every rename
  logged). Never invent canon or names; unmapped items get flagged to the
  owner.
- Animations and movements: renamed and slightly tweaked at industry
  standard, NOT broken, NOT hand-tooled, so they become proprietary to his
  universe without being altered much.
- Owner's reasoning, recorded as his: movements cannot really be owned no
  matter how close they are; renamed + slightly tweaked = his. On Eastern
  Mind: an obscure 1995 art game, not a franchise; building a universe on
  it reads as inspiration. (The honest counter-picture given at 08:03 is
  recorded in section 5 and stands as the assistant's note.)

Dispatched ~08:07 CDT: full wiring + canon conversion coordinator (one lane
per game + a separate verification lane). Checkpoint:
`agent-ops/checkpoints/wh-full-wiring-canon.json`.

## 7. Staging plan + the archive order (08:08 CDT)

Owner, verbatim:

> "Yeah you want to probably put all of that in this conversation in like
> usual put everything we talk about and say into the repo into the
> development and production conversations so we can keep track of
> everything we're saying and come back to it and revisit it later on
> because you know that stuff is important like I said right now this is
> just a hobby project until it's perfected but then once it's perfected and
> everything's tore down and wired up completely and fully and it's actually
> starts to feel like I'm playing a Tekken game because right now it doesn't
> then you know then like I said I was going to start making everything more
> proprietary to me in my universe without fucking it up with hand tooling
> but just by adding onto it my own proprietary stuff and my own you know
> stuff uh that relates to Eastern Mon Western Heart"

Two directives in this message:

1. **THE ARCHIVE ORDER (standing):** everything said in this conversation
   goes into the repo's development and production conversation records,
   tracked and revisit-able. This file is that order being carried out.
2. **THE STAGING PLAN:** Western Heart is a hobby project UNTIL perfected.
   The sequence is fixed:
   1. Everything torn down and wired up completely and fully.
   2. The acceptance bar is met: it actually feels like playing a Tekken
      game (see the callout at the top of this record).
   3. ONLY THEN the proprietary pass: make everything more proprietary to
      his universe by ADDING his own authored material on top (Eastern Mind /
      Western Heart related), additively, without hand-tooling damage to
      what works.

## 8. Decisions + lanes dispatched this morning (summary)

| Time (CDT) | Decision / order | Lane |
|---|---|---|
| 07:46 | Tekken 5 full 100% teardown + production docs | T5 teardown coordinator |
| 07:49 | All teardown games to 100%, closest first, T5 in parallel | Completion sweep coordinator |
| 07:59 | Program fixed at 8 games; heavy research + pull-in mandate | Update sent to both coordinators |
| 08:06 | Wire everything from the 4 complete teardowns; canon conversion; movement rename + light industry-standard tweak | Wiring + canon coordinator |
| 08:08 | Archive all dev/production conversation into the repo; staging plan fixed (perfect it, then proprietary pass) | This record |

---

Record kept under the conversation-to-repo order (section 7). Future
development conversations get their own dated files alongside this one in
`docs/dev-conversations/` so the full history stays trackable and
revisit-able.
