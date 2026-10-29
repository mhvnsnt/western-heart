# Rank system — teardown research → Western Heart implementation

Worker 30, 2026-10-22. Sources: Tekken 7 rank ladder + points formula (sdtekken IC-card
FAQ, esports.gg rank guide, upcomer rank list), TTT2/T5 arcade rank conventions,
WH canon (CANON.md: Nine Souls, Tong-Nou).

## What Tekken does (teardown facts)

**Two ranks per player** (esports.gg): "Players in Tekken 7 receive two different ranks.
The first is for offline play... the second is for ranked play." We mirror this exactly:
separate OFFLINE and ONLINE tracks.

**Per-character ranks** (T7): each character carries its own rank, not the account. We do
per-character ranks on both tracks (`wh_ranks.offline.<charId>`).

**The ladder** (upcomer list, 47 ranks in T7): Beginner → 9th–1st Kyu → 1st–3rd Dan →
Initiate/Mentor/Expert/Grand Master → Brawler/Marauder/Fighter/Vanguard → Warrior/
Vindicator/Juggernaut/Usurper → Vanquisher/Destroyer/Savior/Overlord → Genbu/Byakko/
Seiryu/Suzaku → Mighty/Revered/Divine/Eternal Ruler → Fujin/Raijin/Yaksa/Ryujin →
Emperor/Tekken King → Tekken God → True Tekken God → Tekken God Prime → Tekken God Omega.
Note the shape: real martial-arts grades at the bottom, themed words mid, Japanese
mythology (Genbu/Byakko/Seiryu/Suzaku, Fujin/Raijin/Yaksa/Ryujin) high, invented god-tiers
at the top — **added over time** (Tekken God → True → Prime → Omega came in patches).
That is exactly the user's formula: "real terms bottom → real mythology mid → WH
cosmology top", with top tiers invented going forward. Our ladder follows the same
curve: Lost Soul → 9th–1st Kyu → 1st–3rd Dan → Brawler→Warlord → Kappa→Fudo Myoo →
Four Heavenly Kings → Genbu→Suzaku → Fujin→Ryujin → Nine Souls → Whole → Purified →
S: Assembled → Super S: Tong-Nou → Master God of the Universe → 52–53 RESERVED.

**Points** (sdtekken suggested formula, T5DR era; T7 keeps the shape): vs same rank = full
points; vs higher = less risk and less reward; vs lower = less reward, harsher loss.
"Beating players with the exact same rank as you yields the most points" (esports.gg).
Our `rules.points`: baseWin 100 / baseLoss 70, ±25% per tier of difference capped at 3
tiers, 0.5x floor — the same curve, data-tunable.

**Promotion/demotion** (esports.gg): a visible meter; "when the bar is nearly full, players
earn a Promotion Match that they must win to rank up... Conversely, the meter will also
let players know when they are on the brink of a Demotion Match. Losing one is the same
as ranking down." We implement the bar + promotion/demotion as best-of-N *series*
(Tekken's single "chance" generalized — the user asked for promotion/demotion series).
1st Dan is hardcapped at zero in Tekken ("You cannot be demoted from 1st Dan to 1st
Kyu") — we generalize: bottom tier can't demote + fresh-promotion protection matches
(no instant yo-yo; Tekken fills half your bar on rank-up — our `promoteStartFrac`).

**Offline ranks** come from arcade/treasure-style CPU fights ("Promotional matches happen
after a few victories in a row" — mull-overthing). Our RANK BATTLE mode is exactly that:
arcade-style CPU ladder feeding the offline track.

## What we built

- `game/data/ranks.json` — the entire ladder + all rules as DATA. 53 tiers, 12 sections,
  reserved placeholders at 52–53. The user edits names/sections/rules here; the engine
  never hardcodes a name. Stable `id` slugs per tier so mid-ladder inserts don't break
  saved data.
- `game/js/ranks.js` — engine: points, upset scaling, placement bouts, promotion/demotion
  series, protection, top-held counter (drives future reserved-tier invention), per-track
  leaderboards, RankBattleController (offline ladder mode), Rank Hub UI (both tracks +
  full ladder view), CSS injected at runtime.
- Online track: same math, separate ladder. Local versus feeds it until netplay ranked
  lands (`game/netplay/` is prototype-only today); the hook is `recordResult({track:
  'online', ...})` + `getLeaderboard('online')`.

## Verification

`node test/ranks.test.mjs` — 38 assertions, all passing: table shape (53 tiers, reserved
flags, section bars/series), placement → promo series → promotion → protection →
demotion series → demotion, upset scaling, track separation, leaderboard, top-held,
mid-table tier insertion with zero code changes.
