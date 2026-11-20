/* ============================================================
   WESTERN HEART — Soul Relay (tag throws / tag crash / tag assault)
   Teardown source: Tekken Tag Tournament 2 — tag-team systems.
   TTT2 behavior, faithfully ported:
     • RAW TAG (5): point fighter tags out; partner leaps in. Long,
       punishable animation — never free.
     • TAG ASSAULT: during your own combo, on a launcher/bound-eligible
       hit, press 5 — the partner jumps in and continues the juggle with
       their assault string. Combo scaling keeps applying.
     • TAG CRASH: while being launched/juggled, press 5 — the partner
       crashes in and TAKES the rest of the combo for you. The damage the
       partner absorbs becomes RED (recoverable) health on the partner.
     • TAG THROW: command throws flagged tagThrow:true, executed with 5 —
       both partners perform a tandem throw for big damage.
     • RED HEALTH: the tagged-out partner regenerates the red portion of
       their bar over RED_REGEN_S.
   Coordination: worker 24's TTT2 team-battle lane owns the 2v2 match
   structure. This module is the MECHANICS layer it should call — do not
   reimplement tag state machines elsewhere; extend TagRelay.
   WH canon mapping (PROPOSED — needs owner approval):
     "SOUL RELAY" — partners are soul-fragments of one being relaying
     vessels mid-trial. Canon precedent: SHA's three-way split
     (Saku Ra / Kinpo / Awa Pop — "when one is hurt, the other two feel
     the grain shift") and KAI's two moods (King Tyrant / Star).
     Proposed mechanical names: Relay Assault / Relay Crash / Relay Throw.
   ============================================================ */

export const TAG_INPUT = '5';
export const RED_REGEN_S = 12;        // seconds to regen full red bar
export const RAW_TAG_VULN_S = 0.9;    // raw tag punishable window
export const TAG_ASSAULT_WINDOW_S = 0.5; // after a launcher-eligible hit
export const TAG_CRASH_WINDOW_S = 0.6;  // while being launched

/* A team of two fighters on one side. fighterA starts on point. */
export class TagTeam {
  constructor(fighterA, fighterB) {
    this.point = fighterA;      // active fighter
    this.standby = fighterB;    // tagged-out fighter
    this.red = new Map();       // fighter -> red (recoverable) hp
    this.red.set(fighterA, 0); this.red.set(fighterB, 0);
    this.relayStats = { assaults: 0, crashes: 0, throws: 0, rawTags: 0 };
  }
  swap() { const t = this.point; this.point = this.standby; this.standby = t; }
  addRed(fighter, amount) {
    this.red.set(fighter, Math.min(fighter.maxHp || 100, (this.red.get(fighter) || 0) + amount));
  }
  regenRed(dt) {
    for (const [f, r] of this.red) {
      if (f === this.point || r <= 0) continue;
      const rate = (f.maxHp || 100) / RED_REGEN_S;
      this.red.set(f, Math.max(0, r - rate * dt));
    }
  }
}

/* The tag mechanics controller — one per side (p1 team, p2 team). */
export class TagRelay {
  constructor(team, foeTeam) {
    this.team = team;
    this.foe = foeTeam;
    this.assaultWindow = 0;  // counts down after launcher-eligible hit
    this.crashWindow = 0;    // counts down while point is launched
    this.taggingOut = 0;     // raw-tag vulnerability timer
  }

  update(dt, events = {}) {
    if (this.assaultWindow > 0) this.assaultWindow = Math.max(0, this.assaultWindow - dt);
    if (this.crashWindow > 0) this.crashWindow = Math.max(0, this.crashWindow - dt);
    if (this.taggingOut > 0) this.taggingOut = Math.max(0, this.taggingOut - dt);
    // events from the combat resolver:
    if (events.launcherHit) this.assaultWindow = TAG_ASSAULT_WINDOW_S;
    if (events.pointLaunched) this.crashWindow = TAG_CRASH_WINDOW_S;
    this.team.regenRed(dt);
  }

  /* Press 5. ctx: { comboActive, beingJuggled, throwMove }. Returns the
     tag action taken (or null). Pure decision logic — unit-testable. */
  pressTag(ctx = {}) {
    const { comboActive = false, beingJuggled = false, throwMove = null } = ctx;
    if (this.taggingOut > 0) return null; // already tagging
    if (throwMove && throwMove.tagThrow) {
      this._doSwap();
      this.team.relayStats.throws++;
      return { type: 'tag-throw', move: throwMove, incoming: this.team.point };
    }
    if (comboActive && this.assaultWindow > 0) {
      this._doSwap();
      this.team.relayStats.assaults++;
      this.assaultWindow = 0;
      return { type: 'tag-assault', incoming: this.team.point };
    }
    if (beingJuggled && this.crashWindow > 0) {
      // partner crashes in and absorbs the rest as RED health
      const saved = this.team.point;
      const partner = this.team.standby;
      this._doSwap();
      this.team.relayStats.crashes++;
      this.crashWindow = 0;
      return { type: 'tag-crash', saved, incoming: partner, absorbsAsRed: true };
    }
    // raw tag — punishable
    this._doSwap();
    this.taggingOut = RAW_TAG_VULN_S;
    this.team.relayStats.rawTags++;
    return { type: 'raw-tag', incoming: this.team.point, vulnerable: true };
  }

  _doSwap() {
    // outgoing point keeps a red-health marker of damage taken this stint
    this.team.swap();
  }

  /* Route damage to red health when a tag-crash partner absorbs a combo. */
  absorbAsRed(fighter, amount) { this.team.addRed(fighter, amount); }

  get point() { return this.team.point; }
  get standby() { return this.team.standby; }
}

/* Frame the relay for versus UI: "SOUL RELAY" team names. */
export function relayTeamName(ids) { return ids.map(id => String(id).toUpperCase()).join(' ✦ '); }
