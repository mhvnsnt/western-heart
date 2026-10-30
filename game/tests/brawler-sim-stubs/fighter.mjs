/* Headless Fighter stub for the brawler sim test.
 * Same public surface the real Fighter exposes to BrawlerGame
 * (brawler-mode fields + combat methods), with simple deterministic
 * combat math so a bot can actually play the descent. */
export function setArenaLimit(v) { globalThis.__arenaLimit = v; }
export function bankIdFor(id) { return null; }

export class Fighter {
  constructor(charData, startX, facing, isPlayer) {
    this.char = charData; this.isPlayer = !!isPlayer; this.facing = facing;
    this.brawler = false; this.yaw = 0;
    this.stats = Object.assign(
      { speed: 2.8, jump: 7.2, power: 1.1, defense: 1.05 }, charData.stats || {});
    this.dmgMul = charData.dmgMul || 1;
    this.maxHp = charData.maxHp || 100; this.hp = this.maxHp;
    this.meter = 0; this.maxMeter = 100;
    this.vx = 0; this.vy = 0; this.vz = 0; this.onGround = true;
    this.state = 'idle'; this._attackPhase = 'none';
    this.attack = null; this.attackName = null;
    this.hasHit = false; this.dead = false; this.combo = 0;
    this.surgeForm = false;
    this.tekken = { fighterId: charData.id, noteDirection() {} };
    this.root = {
      position: { x: startX, y: 0, z: 0,
        set(x, y, z) { this.x = x; this.y = y; this.z = z; } },
      scale: { x: 1, y: 1, z: 1,
        multiplyScalar(s) { this.x *= s; this.y *= s; this.z *= s; },
        setScalar(s) { this.x = this.y = this.z = s; } },
    };
    this.lockT = 0; this.lockMove = null; this.lockVictim = null; this.lockPartner = null;
    this._atkT = 0; this._block = false; this._sceneRef = null;
  }
  canAct() { return !this.dead && (this.state === 'idle' || this.state === 'walk'); }
  tryAttack(act) {
    if (!this.canAct()) return false;
    this.state = 'attack'; this._attackPhase = 'active'; this._atkT = 0; this.hasHit = false;
    this.attackName = act;
    const heavy = act === '3' || act === '4' || act === 'kick';
    const dmg = (act === 'surge' ? 18 : heavy ? 14 : 9) * this.dmgMul;
    this.attack = { damage: dmg, knock: heavy ? 4 : 2.2, soulGain: act === 'surge' ? 0 : 8,
      isGrab: act.includes('+'), tekkenInput: act };
    return true;
  }
  getHitbox() {
    if (this.state !== 'attack' || this.hasHit || this._atkT > 0.3) return null;
    return { x: this.root.position.x + Math.sin(this.yaw) * 1.2, y: 1.2,
             z: this.root.position.z + Math.cos(this.yaw) * 1.2, r: 1.0, move: this.attack };
  }
  getHurtboxes() {
    if (this.dead) return [];
    return [{ x: this.root.position.x, y: 1.1, z: this.root.position.z, r: 0.6 }];
  }
  canBeHitBy() { return !this.dead; }
  receiveHit(move, attacker) {
    if (this.dead) return 'dodge';
    this._atkT = 0;
    if (this._block) { this.hp = Math.max(0, this.hp - move.damage * 0.12); return 'block'; }
    const pw = (attacker && attacker.stats ? attacker.stats.power : 1);
    this.hp = Math.max(0, this.hp - move.damage * pw);
    this.meter = Math.min(this.maxMeter, this.meter + 6);
    if (this.hp <= 0) { this.dead = true; this.state = 'ko'; return 'ko'; }
    this.state = 'hitstun'; return 'hit';
  }
  registerHit() {
    this.hasHit = true;
    this.meter = Math.min(this.maxMeter, this.meter + (this.attack ? this.attack.soulGain : 8));
  }
  registerCombo() { this.combo++; return this.combo; }
  tryBlock(on) { this._block = on; if (on) this.state = 'block'; else if (this.state === 'block') this.state = 'idle'; }
  isBlocking() { return this._block; }
  tryDodge() { if (this.canAct()) { this.state = 'dodge'; this._atkT = 0; return true; } return false; }
  tryThrowBreak() { return false; }
  startThrowLock(m, a) { this.state = 'thrown'; this.lockT = 0.3; this.lockMove = m; this.lockPartner = a; }
  startThrowing(v) { this.state = 'throwing'; this.lockT = 0.3; this.lockVictim = v; this.lockMove = this.attack; }
  completeThrow() {
    const v = this.lockVictim; this.state = 'idle'; this.lockT = 0;
    if (v && v !== this) { v.state = 'idle'; return v.receiveHit(this.lockMove || { damage: 20, knock: 5 }, this); }
    return null;
  }
  canTransform() { return false; }
  tryTransform() { return false; }
  startSurgeForm() {
    if (this.surgeForm || this.meter < this.maxMeter) return false;
    this.surgeForm = true;
    this.stats = Object.assign({}, this.stats, { power: this.stats.power * 1.45 });
    return true;
  }
  endSurgeForm() { this.surgeForm = false; }
  addMeter(v) { this.meter = Math.min(this.maxMeter, this.meter + v); }
  setStick() {}
  victory() { this.state = 'victory'; }
  _bindT3() {}
  update(dt) {
    this._atkT += dt;
    if (this.lockT > 0) this.lockT -= dt; // throw-break window ticks down
    if (this.state === 'attack' && this._atkT > 0.45) { this.state = 'idle'; this._attackPhase = 'none'; this.attack = null; }
    if (this.state === 'dodge' && this._atkT > 0.34) { this.state = 'idle'; }
    if (this.state === 'hitstun' && this._atkT > 0.3) { this.state = 'idle'; }
    this.root.position.x += this.vx * dt;
    this.root.position.z += this.vz * dt;
    if (this.state !== 'walk') { this.vx *= Math.pow(0.0001, dt); this.vz *= Math.pow(0.0001, dt); }
    const sp = Math.hypot(this.vx, this.vz);
    if (sp > 0.4 && this.state === 'idle') this.state = 'walk';
    if (sp <= 0.4 && this.state === 'walk') this.state = 'idle';
  }
}
