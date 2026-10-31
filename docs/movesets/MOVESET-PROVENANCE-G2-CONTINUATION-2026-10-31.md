# Moveset Provenance — G2 Continuation (2026-10-31)

Lane: G2 provenance continuation, owner order 2026-10-31 ("finish flushing
out the guess-grade animations fighter by fighter, then the donor-moveset
replacements, skipping only the fighters waiting on your calls").

This lane re-ran the branchwalk proof sweep over the 36 class 1-W files with
two evidence upgrades the Phase 1 continuation lane did not have:

1. **The decoded T3 condition table** (PR #1370,
   `tools/anim/t3_condition_codes.json`): branch records whose condition is
   a dispatcher jump (`blocked_dispatch`), still undecoded
   (`blocked_unknown`), or a state-family gate the source row's profile
   fails are no longer walk edges.
2. **The extracted T3 common bank** (PR #1379,
   `teardown/tekken3/movesets/moveset_common.json` + extraction doc): the
   walk now runs over character rows and common rows together — `<common>`
   CALL records splice their EXE branch blocks in place, and every target
   slot resolves through the active character bank's move index, per the
   engine (BranchFind / MoveBranchStep).

The proof engine itself is the frozen Phase 1 branchwalk, unmodified; the
upgrades are data-level (a transformed walk graph per bank), exactly the
provpass pattern. Anchor discipline is unchanged: native `t3_row` anchors,
Phase 1 corrected twins (pass 1), lineage anchors (pass 2). Owner Decision
List files served only as read-only pass-2 anchor sources in a separate
configuration; anything they alone prove is HELD, never landed. Class 1-S
files, class 2 mixes, and the 10 Decision List files were not touched.

**DATA-CORRECTED is not play-verified.** Nothing in this document promotes
any mapping to VERIFIED; that gate belongs to play-verify video evidence,
which is owner-gated and not this lane's.

## Headline numbers (all re-parsed by this lane from the files themselves)

- Guess-grade at G2 start: **8,552** across the 36 class 1-W files (the
  Phase 1 continuation lane's remainder, re-verified exactly).
- Newly proven and landed by G2: **4** (kai 2, kingtyrant 2 — all proof C).
- Proven but HELD: **33** (paul bank; sole anchor source is an owner-gated
  file — unchanged from the previous lane, reproduced exactly under the
  G2 walk model; see Held section).
- Proven into the common bank (graph-proven, not landable): **0**.
  Proven but not baked into a rows.pack: **0**.
- Bootstrap re-sweep after landing (eddy group, G2 twins added): delta 0.
- The sibling B2 lane's Tekken 7 cross-decoded conditions had **not**
  landed when this sweep closed (the condition table on main still has
  its single original commit), so the conditional re-run did not trigger.
- Remaining guess-grade after G2: **8,548**, grouped by blocker below.

## Landed

| PR | Merge commit | File | Corrections | Proofs |
|---|---|---|---|---|
| #1393 | `b93bf7443335b1c587ae2fac366c5916eaaa5bef` | kai.json (eddy) | 2 | C×2 |
| #1397 | `646951d92f63ee414f1ecaa4148335bdeb90eb96` | kingtyrant.json (eddy) | 2 | C×2 |

All four are label-only confirms of input `f+2,1` and its `~t7.eddy`
variant at Eddy row 103: the claimed row was already correct, and the walk
becomes unique once the condition table removes a dispatch-blocked
competing branch the old model had to treat as a live candidate. The other
34 files proved nothing new in any pass — including pantera and rin, whose
remaining pools the old engine, re-run as a control on the current files,
also proves nothing on (the transform discards no previously available
proof; verified directly).

## What the new evidence did and did not unlock

The walk model is now complete — conditions and the common bank are both
in — and the blocker census barely moved, which settles where the wall is:

| Blocker | Phase 1 cont. | G2 | Delta |
|---|---:|---:|---:|
| no-anchor | 6,842 | 6,842 | 0 |
| no-branch | 1,270 | 1,285 | +15 |
| ambiguous-branch | 72 | 52 | −20 |
| unparsable-step | 329 | 330 | +1 |
| throw-gate | 18 | 18 | 0 |
| foreign-bank-skipped | 21 | 21 | 0 |
| **proven + landed** | 22 | **4** | — |

Condition filtering converted 20 ambiguous entries: 4 into proofs, 15 into
no-branch (their only paths ran through dispatcher/unknown-condition
edges the engine does not take as input continuations — those paths are
now correctly closed), 1 into unparsable-step. The dominant blocker is
**no-anchor (6,842 = 80% of the remainder)**: the proof standard anchors a
string's first step on a direct T3-native entry (`t3_row`) in the
fighter's own file group, and most first steps simply have no native
entry. That is an anchor-pool limit, not a walk-model limit — it shrinks
only as more direct native mappings land (each landed correction joins
the twin pool) or as new native data is authored from the teardown.
No-anchor entries are counted per file in the table below; the full
per-entry sweep output is preserved in the lane's analysis files.

Buffalo Bill's forestlaw run (a 37th run over the same file): its 21
forestlaw-bank entries remain unprovable (no-branch 13, no-anchor 8);
the file's 305 entries are counted once, under the law bank.

## Held — proven, not landed (owner-gated anchor evidence)

Pass 2 with all lineage sources proves the same **33** paul-bank
corrections as the previous lane (t3-paul 18, tou 15; proofs A and C).
Their sole enabling anchor source is gyou-spirit-body.json's direct
paul-port entries — Owner Decision List item 5 (Paul wiring vs Hwoarang
canon). They land mechanically the moment item 5 is ruled. The G2 walk
model neither adds nor removes any of them (paul's proof paths use no
blocked-condition edges and no common rows).

## Per-file results

Blocker columns are the pass-2 (landable configuration) census per file;
"Remaining" = guess-grade after G2's landings.

| File | Bank | Guess | Landed | Held | Remaining | no-anchor | no-branch | ambiguous | unparsable | throw-gate | foreign |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| aotsuki.json | kuma | 170 | 0 | 0 | 170 | 143 | 19 | 0 | 6 | 2 | 0 |
| awapop.json | nina | 204 | 0 | 0 | 204 | 138 | 50 | 9 | 7 | 0 | 0 |
| buffalo-bill.json | law | 305 | 0 | 0 | 305 | 187 | 83 | 5 | 7 | 2 | 21 |
| demonio-bloodline-ember.json | jin | 232 | 0 | 0 | 232 | 194 | 25 | 0 | 13 | 0 | 0 |
| demonio-human.json | jin | 140 | 0 | 0 | 140 | 113 | 17 | 0 | 10 | 0 | 0 |
| demonio.json | jin | 136 | 0 | 0 | 136 | 109 | 17 | 0 | 10 | 0 | 0 |
| diablo.json | heihachi | 115 | 0 | 0 | 115 | 66 | 26 | 0 | 23 | 0 | 0 |
| doc-frank-frankenstein.json | bosconovitch | 182 | 0 | 0 | 182 | 162 | 12 | 0 | 8 | 0 | 0 |
| doc-frank-hood.json | bosconovitch | 227 | 0 | 0 | 227 | 202 | 15 | 0 | 10 | 0 | 0 |
| doc-frank-machine-shop.json | bosconovitch | 227 | 0 | 0 | 227 | 202 | 15 | 0 | 10 | 0 | 0 |
| doc-frank-wowomomo.json | bosconovitch | 227 | 0 | 0 | 227 | 202 | 15 | 0 | 10 | 0 | 0 |
| gashadokuro.json | kuma | 170 | 0 | 0 | 170 | 143 | 19 | 0 | 6 | 2 | 0 |
| gyou.json | hwoarang | 409 | 0 | 0 | 409 | 345 | 57 | 0 | 7 | 0 | 0 |
| kai.json | eddy | 285 | 2 | 0 | 283 | 212 | 48 | 5 | 18 | 0 | 0 |
| kingtyrant.json | eddy | 200 | 2 | 0 | 198 | 148 | 28 | 5 | 17 | 0 | 0 |
| nightwolf.json | julia | 149 | 0 | 0 | 149 | 89 | 56 | 0 | 4 | 0 | 0 |
| pantera.json | king | 175 | 0 | 0 | 175 | 149 | 12 | 0 | 13 | 1 | 0 |
| phantom.json | yoshimitsu | 268 | 0 | 0 | 268 | 216 | 45 | 0 | 7 | 0 | 0 |
| retsu.json | bryan | 353 | 0 | 0 | 353 | 281 | 64 | 0 | 8 | 0 | 0 |
| rin.json | jin | 211 | 0 | 0 | 211 | 173 | 25 | 0 | 13 | 0 | 0 |
| sakura.json | xiaoyu | 167 | 0 | 0 | 167 | 142 | 22 | 0 | 3 | 0 | 0 |
| samura1.json | gunjack | 192 | 0 | 0 | 192 | 174 | 12 | 0 | 5 | 1 | 0 |
| sha.json | xiaoyu | 167 | 0 | 0 | 167 | 142 | 22 | 0 | 3 | 0 | 0 |
| skull.json | bryan | 225 | 0 | 0 | 225 | 184 | 37 | 0 | 4 | 0 | 0 |
| t3-anna.json | anna | 312 | 0 | 0 | 312 | 252 | 49 | 2 | 8 | 1 | 0 |
| t3-eddy.json | eddy | 280 | 0 | 0 | 280 | 211 | 45 | 5 | 18 | 1 | 0 |
| t3-hwoarang.json | hwoarang | 402 | 0 | 0 | 402 | 345 | 50 | 0 | 7 | 0 | 0 |
| t3-julia.json | julia | 147 | 0 | 0 | 147 | 88 | 54 | 0 | 4 | 1 | 0 |
| t3-kuma.json | kuma | 170 | 0 | 0 | 170 | 143 | 19 | 0 | 6 | 2 | 0 |
| t3-law.json | law | 306 | 0 | 0 | 306 | 199 | 91 | 5 | 9 | 2 | 0 |
| t3-lei.json | lei | 425 | 0 | 0 | 425 | 370 | 41 | 0 | 14 | 0 | 0 |
| t3-nina.json | nina | 311 | 0 | 0 | 311 | 229 | 62 | 12 | 7 | 1 | 0 |
| t3-paul.json | paul | 227 | 0 | 18 | 227 | 189 | 27 | 0 | 10 | 1 | 0 |
| tobi.json | hwoarang | 402 | 0 | 0 | 402 | 345 | 50 | 0 | 7 | 0 | 0 |
| torch.json | anna | 207 | 0 | 0 | 207 | 165 | 29 | 4 | 8 | 1 | 0 |
| tou.json | paul | 227 | 0 | 15 | 227 | 190 | 27 | 0 | 10 | 0 | 0 || **Total** | | **8,552** | **4** | **33** | **8,548** | **6,842** | **1,285** | **52** | **330** | **18** | **21** |

## Donor-moveset replacements

Donor-flagged entries (`donor_fighter`) inside the 36 class 1-W files
exist in only 6 files, and every donor is the same fighter's own base or
sibling form — demonio → demonio-human / demonio-bloodline-ember,
docfrank → the four doc-frank attire files. (The cross-fighter donor
files named in the provenance classification — star and the other
Decision List items — were skipped per the lane brief.) Accounting:

| File | Donor | Already proven | Guess-grade (still unprovable) | No anim_t3 | Other label |
|---|---|---:|---:|---:|---:|
| demonio-bloodline-ember.json | demonio | 9 | 21 | 0 | 0 |
| demonio-human.json | demonio | 193 | 140 | 245 | 3 |
| doc-frank-frankenstein.json | docfrank | 86 | 182 | 149 | 4 |
| doc-frank-hood.json | docfrank | 108 | 227 | 185 | 5 |
| doc-frank-machine-shop.json | docfrank | 108 | 227 | 180 | 5 |
| doc-frank-wowomomo.json | docfrank | 108 | 227 | 185 | 5 |
| **Total** | | **612** | **1,024** | **944** | **22** |

- **Replacements landed by G2: 0.** The 4 G2 proofs fell in kai /
  kingtyrant, which carry no donor entries; every donor-flagged
  guess-grade entry (1,024) sits in the same blocker classes as the rest
  of its file (predominantly no-anchor) and stays byte-identical,
  still flagged.
- The 944 donor entries with **no anim_t3** have no T3 mapping to
  replace — they are merge-fill / WH-original entries whose animation
  does not come from a T3 row; they are named here as out of scope for
  mapping replacement.
- The `donor_fighter` flag itself documents where the move *data* was
  copied from; this lane did not remove flags, only anim mappings are in
  its remit.

## T7 preference — per-fighter attachment flags

Owner preference (2026-10-31): "I would prefer if we attach the T7 move
sets, just because they're more expanded and more recent and updated, to
whoever's in T7." The T3 proofs above stand as the proof layer; this
table flags, per file, whether the fighter's T3 source character is
present in Tekken 7 and what T7 attachment already exists on main, so the
wiring lanes can sequence T7-first. "T7 entries" counts the file's own
`~t7.*` variant entries / `anim_t7` mappings (move-level T7 join data);
"Clip-map" is the anim-level attachment in
`game/assets/anim/t7/clip-maps/`.

| File | T3 source | In T7? | T7 entries | Clip-map on main |
|---|---|---|---:|---|
| aotsuki.json | Kuma | yes | 139 | no |
| awapop.json | Nina | yes | 201 | no |
| buffalo-bill.json | Law (Marshall) | yes | 211 | no |
| demonio.json | Jin | yes | 109 | yes |
| demonio-bloodline-ember.json | Jin | yes | 127 | yes (demonio) |
| demonio-human.json | Jin | yes | 0 | yes (demonio) |
| diablo.json | Heihachi | yes | 96 | yes |
| doc-frank-frankenstein.json | Dr. Bosconovitch | NO | 0 | no |
| doc-frank-hood.json | Dr. Bosconovitch | NO | 0 | no |
| doc-frank-machine-shop.json | Dr. Bosconovitch | NO | 0 | no |
| doc-frank-wowomomo.json | Dr. Bosconovitch | NO | 0 | no |
| gashadokuro.json | Kuma | yes | 139 | no |
| gyou.json | Hwoarang | yes | 242 | no |
| kai.json | Eddy | yes | 177 | no |
| kingtyrant.json | Eddy | yes | 153 | no |
| nightwolf.json | Julia | yes (DLC) | 94 | no |
| pantera.json | King | yes | 118 | yes |
| phantom.json | Yoshimitsu | yes | 177 | yes |
| retsu.json | Bryan | yes | 205 | no |
| rin.json | Jin | yes | 128 | no |
| sakura.json | Xiaoyu | yes | 144 | no |
| samura1.json | Gun Jack (Jack line) | yes (as Jack-7) | 168 | no |
| sha.json | Xiaoyu | yes | 143 | no |
| skull.json | Bryan | yes | 181 | yes |
| t3-anna.json | Anna | yes (DLC) | 219 | no |
| t3-eddy.json | Eddy | yes | 182 | no |
| t3-hwoarang.json | Hwoarang | yes | 243 | no |
| t3-julia.json | Julia | yes (DLC) | 104 | no |
| t3-kuma.json | Kuma | yes | 139 | no |
| t3-law.json | Law (Marshall) | yes | 211 | no |
| t3-lei.json | Lei | yes (DLC) | 210 | no |
| t3-nina.json | Nina | yes | 240 | no |
| t3-paul.json | Paul | yes | 117 | no |
| tobi.json | Hwoarang | yes | 243 | no |
| torch.json | Anna | yes (DLC) | 183 | no |
| tou.json | Paul | yes | 117 | no |
Reading: every swept fighter except the four Dr. Bosconovitch files is
T7-present and already carries move-level T7 join entries; the
anim-level clip-map attachment exists for demonio, diablo, pantera,
phantom and skull and is **still owed for the other 31 files' fighters**.
Dr. Bosconovitch has no T7 counterpart, so the doc-frank files'
end state stays T3.

## Method note — fidelity checks run by this lane

- The paul pass-2 configuration (gyou-spirit-body anchors + twins)
  reproduces the previous lane's run **exactly** (237 anchors; proven A
  17 / C 1; identical blocker census) on the G2-transformed graph —
  the new model changes no previously reachable verdict except through
  the condition/common evidence itself.
- Control: the frozen engine on the *untransformed* king graph over the
  current pantera.json also lands 0, matching the G2 run — the transform
  eats no proofs.
- The transformed jin graph resolves the standing hub's RP branch to
  {row 47, common:60, common:61} — the condition decode doc's own worked
  example — and 34 common rows are reachable within 4 steps of that hub.
