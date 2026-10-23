/* ============================================================
   WESTERN HEART — ChronoGrapple (joint-constraint grappling lane)

   Track 4 (advanced-systems integration, 2026-10-23): Project Chrono
   evaluation, wired as a grappling subsystem. See research report:
   docs/research/CHRONO-PHYSICS-2026-10-23.md

   WHAT THIS IS — a deterministic, dependency-free (no three.js, no
   WASM, no vendor blob) joint-constraint solver modeled on Project
   Chrono's ChLink architecture, purpose-built for WH's ground game:
     - ChronoBody      — rigid limb segment (ChBody analog)
     - ChronoLink      — joint taxonomy: FIXED / SPHERICAL / REVOLUTE /
                         PRISMATIC / UNIVERSAL (ChLinkLock* analogs)
     - ChronoEngine    — torque / speed / position motor on a joint's
                         free DOF (ChLinkEngine analog)
     - ChronoSpring    — linear/angular spring-damper with RUNTIME-
                         VARIABLE stiffness = the muscle model
                         (ChLinkTSDA / ChLinkRSDA analog)
     - Torque nodes    — per-link getReactionForce()/getReactionTorque()
                         (ChLink::Get_react_force/torque analogs)
     - MuscleStrain    — real-time muscle-strain force calculation per
                         target joint (elbow/shoulder/knee/ankle/neck)
     - SubmissionChain — data-driven multi-step ground-game transitions:
                         armbar / kimura / triangle / rear-naked choke,
                         with dwell bands, escapes, tap-out + bone-snap.

   WHAT THIS IS NOT — not a general physics engine, not a replacement
   for cannon-es (arena props/debris/KO tumble, visuals-only) or Jolt
   (XPBD soft tissue). It fills the gap neither covers: ARTICULATED
   JOINT CONSTRAINTS with torque readout for grappling. Full Chrono
   C++ → WASM remains a documented SPEC path (see research doc).

   DETERMINISM CONTRACT (owner law): combat sim never reads
   nondeterministic physics state. This module IS deterministic game
   logic: fixed substep dt, fixed iteration count, no Math.random, no
   wall clock, no allocation-order dependence. Identical inputs ⇒
   bit-identical outputs (asserted in game/tests/chrono-grapple.test.mjs).
   The joint solver is the AUTHORITY for grappling state — it is never
   "sampled" like a cosmetic sim.

   INTEGRATION CONTRACT (mirrors game/js/softbody.js):
     1. Lazy-load (integration.js block 8): const g = new ChronoGrapple();
     2. On clinch/grapple entry (fight state machine):
          g.startChain('armbar', { attacker, defender });
        Returns immediately; safe to call stepCombat/update before start
        (they no-op while idle — zero cost).
     3. Every COMBAT tick (fixed dt, authoritative):
          const ev = g.stepCombat(fixedDt, { defenderInput });
        ev ∈ {step advanced} | {event:'tap'|'snap'|'escape'} → drive the
        fight state machine (round end, damage, commentary).
     4. Every RENDER frame (cosmetic joint solve for the servo layer):
          g.update(dt);  const targets = g.getServoTargets();
        Feed targets into the PhysicsServo per-limb PD controllers
        (driveScale blend). Null while idle.
     5. On break/disengage: g.reset().

   No top-level imports — unit-testable in node, zero boot cost.
   ============================================================ */

export const CHRONO_GRAPPLE_VERSION = '1.0.0-track4';

/* ---------------- deterministic math (no THREE) ---------------- */
// vec3 = [x,y,z]; quat = [x,y,z,w]; mat3 = 9-array row-major.

function v3add(a, b) { return [a[0]+b[0], a[1]+b[1], a[2]+b[2]]; }
function v3sub(a, b) { return [a[0]-b[0], a[1]-b[1], a[2]-b[2]]; }
function v3scale(a, s) { return [a[0]*s, a[1]*s, a[2]*s]; }
function v3dot(a, b) { return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]; }
function v3cross(a, b) {
  return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
}
function v3len(a) { return Math.sqrt(v3dot(a, a)); }

function qmul(a, b) {
  const [ax,ay,az,aw] = a, [bx,by,bz,bw] = b;
  return [
    aw*bx + ax*bw + ay*bz - az*by,
    aw*by - ax*bz + ay*bw + az*bx,
    aw*bz + ax*by - ay*bx + az*bw,
    aw*bw - ax*bx - ay*by - az*bz,
  ];
}
function qconj(q) { return [-q[0], -q[1], -q[2], q[3]]; }
function qrot(q, v) {
  // v' = v + 2 * cross(q.xyz, cross(q.xyz, v) + w * v)
  const qv = [q[0], q[1], q[2]];
  const c1 = v3cross(qv, v);
  const c2 = v3add(c1, v3scale(v, q[3]));
  const c3 = v3cross(qv, c2);
  return v3add(v, v3scale(c3, 2));
}
function qNormalize(q) {
  const l = Math.sqrt(q[0]*q[0]+q[1]*q[1]+q[2]*q[2]+q[3]*q[3]) || 1;
  return [q[0]/l, q[1]/l, q[2]/l, q[3]/l];
}

// world inverse inertia from body-frame diagonal: Iw^-1 = R * diag(invI) * R^T
function worldInvInertia(q, invI) {
  const [x,y,z,w] = q;
  // rotation matrix columns from quat
  const r00 = 1-2*(y*y+z*z), r01 = 2*(x*y-z*w),   r02 = 2*(x*z+y*w);
  const r10 = 2*(x*y+z*w),   r11 = 1-2*(x*x+z*z), r12 = 2*(y*z-x*w);
  const r20 = 2*(x*z-y*w),   r21 = 2*(y*z+x*w),   r22 = 1-2*(x*x+y*y);
  const R = [r00,r01,r02, r10,r11,r12, r20,r21,r22];
  // M = R D R^T, symmetric: compute upper triangle
  const out = new Array(9).fill(0);
  for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) {
    let s = 0;
    for (let k = 0; k < 3; k++) s += R[i*3+k] * invI[k] * R[j*3+k];
    out[i*3+j] = s;
  }
  return out;
}
function m3v(M, v) {
  return [
    M[0]*v[0]+M[1]*v[1]+M[2]*v[2],
    M[3]*v[0]+M[4]*v[1]+M[5]*v[2],
    M[6]*v[0]+M[7]*v[1]+M[8]*v[2],
  ];
}
function m3invSym(M) {
  // inverse of symmetric 3x3 via adjugate; falls back to scaled identity
  const [a,b,c,d,e,f,g,h,i] = M; // rows: [a b c; b e f; c f i]
  const A = e*i - f*h, B = c*h - b*i, C = b*f - c*e;
  const det = a*A + b*B + c*C;
  if (Math.abs(det) < 1e-12) return [1,0,0, 0,1,0, 0,0,1];
  const s = 1/det;
  return [
    A*s, B*s, C*s,
    B*s, (a*i-c*g)*s, (c*d-a*f)*s,
    C*s, (c*d-a*f)*s, (a*e-b*d)*s,
  ];
}
function skew(v) {
  return [0,-v[2],v[1], v[2],0,-v[0], -v[1],v[0],0];
}

/* ---------------- ChronoBody (ChBody analog) ---------------- */

let _bodySeq = 0;

export class ChronoBody {
  constructor({ mass = 1, inertia = [1,1,1], pos = [0,0,0], quat = [0,0,0,1], kinematic = false, name = '' } = {}) {
    this.id = _bodySeq++;
    this.name = name || ('body'+this.id);
    this.kinematic = kinematic;
    this.invMass = (kinematic || mass <= 0) ? 0 : 1/mass;
    this.invI = (kinematic || mass <= 0) ? [0,0,0]
      : [inertia[0] > 0 ? 1/inertia[0] : 0, inertia[1] > 0 ? 1/inertia[1] : 0, inertia[2] > 0 ? 1/inertia[2] : 0];
    this.p = [...pos];
    this.q = qNormalize([...quat]);
    this.v = [0,0,0];
    this.w = [0,0,0];
    this.force = [0,0,0];
    this.torque = [0,0,0];
  }
  applyForce(f, atWorld = null) {
    this.force = v3add(this.force, f);
    if (atWorld) {
      const r = v3sub(atWorld, this.p);
      this.torque = v3add(this.torque, v3cross(r, f));
    }
  }
  applyTorque(t) { this.torque = v3add(this.torque, t); }
  clearForces() { this.force = [0,0,0]; this.torque = [0,0,0]; }
  integrateForces(dt) {
    if (this.invMass === 0) { this.clearForces(); return; }
    this.v = v3add(this.v, v3scale(this.force, this.invMass * dt));
    const Iw = worldInvInertia(this.q, this.invI);
    this.w = v3add(this.w, m3v(Iw, v3scale(this.torque, dt)));
    this.clearForces();
  }
  integrateVelocities(dt) {
    if (this.invMass === 0) return;
    this.p = v3add(this.p, v3scale(this.v, dt));
    // dq/dt = 0.5 * w_quat * q
    const wq = [this.w[0]*dt*0.5, this.w[1]*dt*0.5, this.w[2]*dt*0.5, 0];
    const dq = qmul(wq, this.q);
    this.q = qNormalize([this.q[0]+dq[0], this.q[1]+dq[1], this.q[2]+dq[2], this.q[3]+dq[3]]);
  }
  snapshot() {
    return { p:[...this.p], q:[...this.q], v:[...this.v], w:[...this.w] };
  }
}

/* ---------------- ChronoLink: joint taxonomy (ChLinkLock* analogs) ---------------- */

export const JOINT = {
  FIXED: 'fixed',           // ChLinkLockLock: welds bodies (0 DOF)
  SPHERICAL: 'spherical',   // ChLinkLockSpherical: ball-and-socket (3 DOF)
  REVOLUTE: 'revolute',     // ChLinkLockRevolute: hinge (1 DOF, about joint Z)
  PRISMATIC: 'prismatic',   // ChLinkLockPrismatic: slider (1 DOF, along joint Z)
  UNIVERSAL: 'universal',   // ChLinkLockUniversal: U-joint (2 DOF)
};

const BAUMGARTE = 0.1; // positional stabilization (Chrono uses stabilization too)

export class ChronoLink {
  constructor(type, bodyA, bodyB, {
    anchorA = [0,0,0], anchorB = [0,0,0],
    frameA = [0,0,0,1], frameB = [0,0,0,1], name = '',
  } = {}) {
    this.type = type;
    this.bodyA = bodyA; this.bodyB = bodyB;
    this.anchorA = [...anchorA]; this.anchorB = [...anchorB];
    this.frameA = qNormalize([...frameA]); this.frameB = qNormalize([...frameB]);
    this.name = name || (type + '_link');
    // reaction accumulators (torque-node readouts, reset each step)
    this._linLambda = [0,0,0];
    this._angLambda = [0,0,0];
    this.reactionForce = [0,0,0];   // N — ChLink::Get_react_force analog
    this.reactionTorque = [0,0,0];  // N·m — ChLink::Get_react_torque analog
    // revolute free-DOF angle state (integrated, no branch cuts)
    this.angle = 0;
  }

  // joint-frame world axes for a body
  _axes(body, frame) {
    const jq = qmul(body.q, frame);
    return {
      X: qrot(jq, [1,0,0]), Y: qrot(jq, [0,1,0]), Z: qrot(jq, [0,0,1]),
    };
  }
  _worldAnchors() {
    const A = this.bodyA, B = this.bodyB;
    const rA = qrot(A.q, this.anchorA);
    const rB = qrot(B.q, this.anchorB);
    return { rA, rB, pA: v3add(A.p, rA), pB: v3add(B.p, rB) };
  }

  _solveAngularRow(u, v, dt) {
    // scalar constraint C = dot(u,v) = 0 ; u fixed on A, v fixed on B
    const A = this.bodyA, B = this.bodyB;
    const J = v3cross(u, v);            // JwA
    const C = v3dot(u, v);
    const IwA = worldInvInertia(A.q, A.invI);
    const IwB = worldInvInertia(B.q, B.invI);
    const JW1 = m3v(IwA, J), JW2 = m3v(IwB, J);
    const K = v3dot(J, JW1) + v3dot(J, JW2);
    if (K < 1e-12) return;
    const bias = (BAUMGARTE / dt) * C;
    const jv = v3dot(J, A.w) - v3dot(J, B.w); // JwB = -J
    const lambda = -(jv + bias) / K;
    A.w = v3add(A.w, v3scale(JW1, lambda));
    B.w = v3add(B.w, v3scale(JW2, -lambda));
    this._angLambda = v3add(this._angLambda, v3scale(J, lambda));
  }

  _solveLinearRows(dt) {
    // point-to-point: C = (pB + rB) - (pA + rA) = 0  (3 rows, block solve)
    const A = this.bodyA, B = this.bodyB;
    const { rA, rB } = this._worldAnchors();
    const C = v3sub(v3add(B.p, rB), v3add(A.p, rA));
    const IwA = worldInvInertia(A.q, A.invI);
    const IwB = worldInvInertia(B.q, B.invI);
    const sA = skew(rA), sB = skew(rB);
    // K = (invMA+invMB) I + sA IwA sA^T + sB IwB sB^T ; sA^T = -sA
    const K = new Array(9).fill(0);
    const mSum = A.invMass + B.invMass;
    for (let i = 0; i < 3; i++) K[i*3+i] = mSum;
    const addTerm = (s, Iw) => {
      // s * Iw * s^T ; s^T = -s so = -(s Iw s)
      const sIw = new Array(9).fill(0);
      for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) {
        let t = 0;
        for (let k = 0; k < 3; k++) t += s[i*3+k] * (Iw[k*3+j]);
        sIw[i*3+j] = t;
      }
      for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) {
        let t = 0;
        // s^T = -s  ⇒  s^T[k,j] = -s[k,j]
        for (let k = 0; k < 3; k++) t += sIw[i*3+k] * (-s[k*3+j]);
        K[i*3+j] += t;
      }
    };
    addTerm(sA, IwA); addTerm(sB, IwB);
    const Kinv = m3invSym(K);
    const jv = v3sub(
      v3add(B.v, v3cross(B.w, rB)),
      v3add(A.v, v3cross(A.w, rA))
    );
    const rhs = v3add(jv, v3scale(C, BAUMGARTE / dt));
    const lambda = v3scale(m3v(Kinv, rhs), -1);
    A.v = v3add(A.v, v3scale(lambda, -A.invMass));
    A.w = v3add(A.w, m3v(IwA, v3scale(v3cross(rA, lambda), -1)));
    B.v = v3add(B.v, v3scale(lambda, B.invMass));
    B.w = v3add(B.w, m3v(IwB, v3cross(rB, lambda)));
    this._linLambda = v3add(this._linLambda, lambda);
  }

  solveVelocity(dt) {
    const axA = this._axes(this.bodyA, this.frameA);
    const axB = this._axes(this.bodyB, this.frameB);
    switch (this.type) {
      case JOINT.FIXED:
        this._solveLinearRows(dt);
        this._solveAngularRow(axA.X, axB.Y, dt);
        this._solveAngularRow(axA.Y, axB.Z, dt);
        this._solveAngularRow(axA.Z, axB.X, dt);
        break;
      case JOINT.SPHERICAL:
        this._solveLinearRows(dt);
        break;
      case JOINT.REVOLUTE:
        this._solveLinearRows(dt);
        this._solveAngularRow(axA.X, axB.Z, dt);
        this._solveAngularRow(axA.Y, axB.Z, dt);
        break;
      case JOINT.PRISMATIC: {
        // 2 linear rows ⟂ to slide axis + 3 angular rows; translation along Z free
        const A = this.bodyA, B = this.bodyB;
        const { rA, rB } = this._worldAnchors();
        // project point-to-point onto X,Y of joint frame (perp to Z slide axis)
        const Z = axA.Z;
        const X = axA.X, Y = axA.Y;
        const Cfull = v3sub(v3add(B.p, rB), v3add(A.p, rA));
        for (const ax of [X, Y]) {
          const C = v3dot(Cfull, ax);
          // scalar row along ax: J = [ax, rA×ax, -ax, -(rB×ax)]
          const IwA = worldInvInertia(A.q, A.invI);
          const IwB = worldInvInertia(B.q, B.invI);
          const tA = v3cross(rA, ax), tB = v3cross(rB, ax);
          const K = (A.invMass + B.invMass)
            + v3dot(tA, m3v(IwA, tA)) + v3dot(tB, m3v(IwB, tB));
          if (K < 1e-12) continue;
          const jv = v3dot(ax, v3sub(v3add(B.v, v3cross(B.w, rB)), v3add(A.v, v3cross(A.w, rA))));
          const lambda = -(jv + (BAUMGARTE/dt) * C) / K;
          A.v = v3add(A.v, v3scale(ax, -A.invMass * lambda));
          A.w = v3add(A.w, m3v(IwA, v3scale(tA, -lambda)));
          B.v = v3add(B.v, v3scale(ax, B.invMass * lambda));
          B.w = v3add(B.w, m3v(IwB, v3scale(tB, lambda)));
          this._linLambda = v3add(this._linLambda, v3scale(ax, lambda));
        }
        void Z;
        this._solveAngularRow(axA.X, axB.Y, dt);
        this._solveAngularRow(axA.Y, axB.Z, dt);
        this._solveAngularRow(axA.Z, axB.X, dt);
        break;
      }
      case JOINT.UNIVERSAL:
        this._solveLinearRows(dt);
        this._solveAngularRow(axA.X, axB.Y, dt);
        break;
      default:
        throw new Error('chrono-grapple: unknown joint type ' + this.type);
    }
  }

  // hinge axis (world) for the revolute free DOF
  hingeAxis() {
    const jq = qmul(this.bodyA.q, this.frameA);
    return qrot(jq, [0,0,1]);
  }
  // relative angular velocity about the hinge axis
  hingeRelVel() {
    const h = this.hingeAxis();
    return v3dot(v3sub(this.bodyB.w, this.bodyA.w), h);
  }
  trackAngle(dt) {
    if (this.type === JOINT.REVOLUTE) this.angle += this.hingeRelVel() * dt;
  }
  beginStep() {
    this._linLambda = [0,0,0];
    this._angLambda = [0,0,0];
  }
  endStep(dt) {
    // torque nodes: reaction force/torque from accumulated impulses
    this.reactionForce = v3scale(this._linLambda, 1/dt);
    // moment of linear reaction about body-B anchor + pure angular part
    const { rB } = this._worldAnchors();
    const momentArm = v3cross(rB, this.reactionForce);
    this.reactionTorque = v3add(v3scale(this._angLambda, 1/dt), momentArm);
  }
}

/* ---------------- ChronoEngine (ChLinkEngine analog) ---------------- */

export const ENG_MODE = {
  TORQUE: 'torque',     // ChLinkEngine::ENG_MODE_TORQUE — constant torque
  SPEED: 'speed',        // ChLinkEngine::ENG_MODE_SPEED — servo to target speed
  POSITION: 'position',  // ChLinkEngine::ENG_MODE_ROTATION — servo to target angle
};

export class ChronoEngine {
  constructor(link, {
    mode = ENG_MODE.TORQUE, torque = 0, targetSpeed = 0,
    targetAngle = 0, maxTorque = 100, kp = 40, kd = 4, name = '',
  } = {}) {
    if (link.type !== JOINT.REVOLUTE) {
      throw new Error('chrono-grapple: ChronoEngine needs a REVOLUTE link, got ' + link.type);
    }
    this.link = link;
    this.mode = mode;
    this.torque = torque;             // TORQUE mode: N·m about hinge axis
    this.targetSpeed = targetSpeed;   // SPEED mode: rad/s
    this.targetAngle = targetAngle;   // POSITION mode: rad
    this.maxTorque = maxTorque;
    this.kp = kp; this.kd = kd;       // servo gains (runtime-tunable)
    this.name = name || 'engine';
    this.lastTorque = 0;              // readout for strain calc
  }
  apply(dt) {
    const link = this.link, A = link.bodyA, B = link.bodyB;
    const h = link.hingeAxis();
    let tau = 0;
    if (this.mode === ENG_MODE.TORQUE) {
      tau = this.torque;
    } else if (this.mode === ENG_MODE.SPEED) {
      const err = this.targetSpeed - link.hingeRelVel();
      tau = Math.max(-this.maxTorque, Math.min(this.maxTorque, this.kp * err));
    } else { // POSITION
      const err = this.targetAngle - link.angle;
      tau = Math.max(-this.maxTorque,
        Math.min(this.maxTorque, this.kp * err - this.kd * link.hingeRelVel()));
    }
    this.lastTorque = tau;
    const t = v3scale(h, tau * dt);
    // τ on B about hinge; equal/opposite on A (torque nodes read this too)
    const IwA = worldInvInertia(A.q, A.invI);
    const IwB = worldInvInertia(B.q, B.invI);
    A.w = v3add(A.w, m3v(IwA, v3scale(t, -1)));
    B.w = v3add(B.w, m3v(IwB, t));
  }
}

/* ---------------- ChronoSpring: the muscle model ----------------
   ChLinkTSDA / ChLinkRSDA analog. stiffness/damping are RUNTIME
   VARIABLES (the Euphoria lesson): the behavior layer + the escape
   minigame modulate them live; PhysicsServo's driveScale blends the
   result with authored animation. */

export class ChronoSpring {
  constructor(bodyA, bodyB, {
    anchorA = [0,0,0], anchorB = [0,0,0],
    restLength = 0, stiffness = 100, damping = 5,
    angular = false, link = null, restAngle = 0, name = '',
  } = {}) {
    this.bodyA = bodyA; this.bodyB = bodyB;
    this.anchorA = [...anchorA]; this.anchorB = [...anchorB];
    this.restLength = restLength;
    this.stiffness = stiffness;   // N/m — variable at runtime
    this.damping = damping;       // N·s/m — variable at runtime
    this.angular = angular;       // true: rotational muscle on link's hinge
    this.link = link;             // required when angular
    this.restAngle = restAngle;
    this.name = name || 'muscle';
    this.lastForce = 0;
  }
  apply(dt) {
    const A = this.bodyA, B = this.bodyB;
    if (this.angular) {
      const link = this.link, h = link.hingeAxis();
      const tau = -this.stiffness * (link.angle - this.restAngle)
                  - this.damping * link.hingeRelVel();
      this.lastForce = tau;
      const IwA = worldInvInertia(A.q, A.invI);
      const IwB = worldInvInertia(B.q, B.invI);
      const t = v3scale(h, tau * dt);
      A.w = v3add(A.w, m3v(IwA, v3scale(t, -1)));
      B.w = v3add(B.w, m3v(IwB, t));
      return;
    }
    const pA = v3add(A.p, qrot(A.q, this.anchorA));
    const pB = v3add(B.p, qrot(B.q, this.anchorB));
    const d = v3sub(pB, pA);
    const len = v3len(d) || 1e-9;
    const dir = v3scale(d, 1/len);
    const rA = v3sub(pA, A.p), rB = v3sub(pB, B.p);
    const relVel = v3dot(v3sub(v3add(B.v, v3cross(B.w, rB)), v3add(A.v, v3cross(A.w, rA))), dir);
    const F = this.stiffness * (len - this.restLength) + this.damping * relVel;
    this.lastForce = F;
    // force on B points back toward A (negative dir) when stretched
    const f = v3scale(dir, -F * dt);
    A.v = v3add(A.v, v3scale(f, -A.invMass));
    A.w = v3add(A.w, m3v(worldInvInertia(A.q, A.invI), v3scale(v3cross(rA, f), -1)));
    B.v = v3add(B.v, v3scale(f, B.invMass));
    B.w = v3add(B.w, m3v(worldInvInertia(B.q, B.invI), v3cross(rB, f)));
  }
}

/* ---------------- ChronoSystem: the solver (ChSystem analog) ---------------- */

export class ChronoSystem {
  constructor({ substeps = 2, iterations = 12, gravity = [0,-9.81,0] } = {}) {
    this.bodies = [];
    this.links = [];
    this.engines = [];
    this.springs = [];
    this.substeps = substeps;       // fixed — determinism contract
    this.iterations = iterations;   // fixed — determinism contract
    this.gravity = [...gravity];
    this.time = 0;
    // external forces re-applied EVERY substep (attacker drives, muscles):
    // [{ body, force:[x,y,z], at:[x,y,z]|null }] — deterministic, no closures
    this.externalForces = [];
  }
  addBody(b) { this.bodies.push(b); return b; }
  addLink(l) { this.links.push(l); return l; }
  addEngine(e) { this.engines.push(e); return e; }
  addSpring(s) { this.springs.push(s); return s; }

  step(dt) {
    const h = dt / this.substeps;
    for (let s = 0; s < this.substeps; s++) {
      for (const b of this.bodies) {
        if (b.invMass !== 0) b.applyForce(v3scale(this.gravity, 1 / b.invMass));
      }
      for (const ef of this.externalForces) {
        ef.body.applyForce(ef.force, ef.at
          ? v3add(ef.body.p, qrot(ef.body.q, ef.at)) : null);
      }
      for (const b of this.bodies) b.integrateForces(h);
      for (const l of this.links) l.beginStep();
      for (const e of this.engines) e.apply(h);
      for (const sp of this.springs) sp.apply(h);
      // sequential-impulse iterations (game-realization of Chrono's DVI solve)
      for (let it = 0; it < this.iterations; it++) {
        for (const l of this.links) l.solveVelocity(h);
      }
      for (const b of this.bodies) b.integrateVelocities(h);
      for (const l of this.links) { l.trackAngle(h); l.endStep(h); }
      this.time += h;
    }
  }
}

/* ---------------- MuscleStrain: real-time muscle-strain force calc ----------------
   Reads a link's TORQUE NODE (reactionTorque) every combat tick and turns
   it into gameplay: strain ratio, submission progress, tap-out, bone-snap.

   JOINT_TOLERANCE — gameplay-tunable torque caps (N·m) per target joint,
   order-of-magnitude from sports-biomechanics literature (elbow
   hyperextension / shoulder rotation / knee varus failure ranges). These
   are GAME BALANCE NUMBERS, not medical claims — tune per fighter with
   the owner's feel law (taps should feel earned, snaps should feel rare).
   Calibrated so a 55 N·m armbar engine taps in ~2–3 s of clean control. */

export const JOINT_TOLERANCE = {
  neck: 55,      // choke/crank compression
  shoulder: 95,  // kimura/americana rotation
  elbow: 75,     // armbar hyperextension
  wrist: 35,     // wrist-lock compression
  hip: 130,      // leg entanglements
  knee: 125,    // kneebar hyperextension
  ankle: 65,     // ankle-lock / heel-hook rotation
};

const STRAIN_RATE = 0.9;    // progress/sec at ratio 1.55 above the danger floor
const DANGER_FLOOR = 0.55;  // below this torque ratio, the joint recovers
const RECOVER_RATE = 0.35;  // progress/sec recovered under the floor
const SNAP_RATIO = 1.5;     // sustained over-torque ⇒ bone-snap ("bone-snapping")
const SNAP_HOLD = 0.25;     // seconds over SNAP_RATIO before the snap

export class MuscleStrain {
  constructor(joint) {
    if (!(joint in JOINT_TOLERANCE)) throw new Error('chrono-grapple: unknown joint ' + joint);
    this.joint = joint;
    this.tauMax = JOINT_TOLERANCE[joint];
    this.progress = 0;      // 0..1 → tap-out
    this.breakTimer = 0;    // sustained over-torque clock
    this.peakRatio = 0;
  }
  /** torqueNm: this tick's |reaction torque| on the joint (from the torque node).
      escapeNm: defender's counter-torque this tick (escape minigame input). */
  update(torqueNm, dt, escapeNm = 0) {
    const eff = Math.max(0, torqueNm - escapeNm);
    const ratio = eff / this.tauMax;
    if (ratio > this.peakRatio) this.peakRatio = ratio;
    if (ratio >= SNAP_RATIO) this.breakTimer += dt;
    else this.breakTimer = 0;
    if (ratio > DANGER_FLOOR) {
      this.progress = Math.min(1.2, this.progress + (ratio - DANGER_FLOOR) * STRAIN_RATE * dt);
    } else {
      this.progress = Math.max(0, this.progress - RECOVER_RATE * dt);
    }
    return {
      ratio, progress: this.progress,
      tap: this.progress >= 1,
      snap: this.breakTimer >= SNAP_HOLD,
    };
  }
  reset() { this.progress = 0; this.breakTimer = 0; this.peakRatio = 0; }
}

/* ---------------- SubmissionChain: multi-step ground-game transitions ----------------
   Data-driven (like the rank ladder — data, not hardcode). Each step names
   the joint lock to build, the torque band the attacker must HOLD, and the
   dwell time to advance. Defender inputs route to escapes. Terminal steps
   end the chain: tap (submission win) or neutral (escape). */

export const CHAINS = {
  armbar: { name: 'Armbar', steps: [
    { id: 'entry', label: 'Clinch entry', dwell: 0.35, lock: null,
      escapes: [{ input: 'sprawl', to: null }] },
    { id: 'isolate', label: 'Isolate the arm', dwell: 0.6, lock: { joint: 'shoulder', type: JOINT.SPHERICAL },
      band: [8, 45], drive: { force: [-70, -40, 0] },
      escapes: [{ input: 'stack', to: null }] },
    { id: 'lock', label: 'Hyperextend the elbow', dwell: 1.1, lock: { joint: 'elbow', type: JOINT.REVOLUTE },
      band: [30, 95], engine: { mode: ENG_MODE.TORQUE, torque: 55, maxTorque: 80 },
      escapes: [{ input: 'hitchhiker', to: null }] },
    { id: 'finish', label: 'Tap out', terminal: 'tap' },
  ]},
  kimura: { name: 'Kimura', steps: [
    { id: 'entry', label: 'Side control', dwell: 0.4, lock: null, escapes: [{ input: 'bridge', to: null }] },
    { id: 'grip', label: 'Figure-four grip', dwell: 0.6, lock: { joint: 'shoulder', type: JOINT.UNIVERSAL },
      band: [10, 50], drive: { force: [-60, -30, 0] },
      escapes: [{ input: 'straighten', to: null }] },
    { id: 'lock', label: 'Rotate the shoulder', dwell: 1.2, lock: { joint: 'shoulder', type: JOINT.REVOLUTE },
      band: [35, 95], engine: { mode: ENG_MODE.TORQUE, torque: 62, maxTorque: 95 },
      escapes: [{ input: 'roll', to: null }] },
    { id: 'finish', label: 'Tap out', terminal: 'tap' },
  ]},
  triangle: { name: 'Triangle choke', steps: [
    { id: 'entry', label: 'Guard pull', dwell: 0.4, lock: null, escapes: [{ input: 'posture', to: null }] },
    { id: 'trap', label: 'Trap arm + head', dwell: 0.7, lock: { joint: 'neck', type: JOINT.PRISMATIC },
      band: [8, 40], drive: { force: [0, -80, 0] },
      escapes: [{ input: 'stack', to: null }] },
    { id: 'lock', label: 'Close the triangle', dwell: 1.3, lock: { joint: 'neck', type: JOINT.PRISMATIC },
      band: [25, 55], drive: { force: [0, -140, 0] },
      escapes: [{ input: 'slam', to: null }] },
    { id: 'finish', label: 'Tap out', terminal: 'tap' },
  ]},
  rear_naked_choke: { name: 'Rear-naked choke', steps: [
    { id: 'entry', label: 'Back take', dwell: 0.4, lock: null, escapes: [{ input: 'handfight', to: null }] },
    { id: 'seatbelt', label: 'Seatbelt control', dwell: 0.6, lock: { joint: 'neck', type: JOINT.SPHERICAL },
      band: [6, 30], drive: { force: [-90, -60, 0] },
      escapes: [{ input: 'shrug', to: null }] },
    { id: 'lock', label: 'Sink the choke', dwell: 1.0, lock: { joint: 'neck', type: JOINT.PRISMATIC },
      band: [20, 55], drive: { force: [0, -120, 0] },
      escapes: [{ input: 'tuck', to: null }] },
    { id: 'finish', label: 'Tap out', terminal: 'tap' },
  ]},
};

export class SubmissionChain {
  constructor(chainId) {
    if (!(chainId in CHAINS)) throw new Error('chrono-grapple: unknown chain ' + chainId);
    this.chainId = chainId;
    this.def = CHAINS[chainId];
    this.stepIndex = 0;
    this.dwell = 0;
    this.done = false;
    this.result = null; // 'tap' | 'escape' | null
  }
  get step() { return this.def.steps[this.stepIndex]; }
  get stepId() { return this.step.id; }

  /** Authoritative combat-tick advance. torqueNm: |reaction torque| on the
      step's lock joint this tick. defenderInput: escape attempt id or null.
      Returns { advanced, event } — event ∈ null | 'escape' | 'tap'. */
  stepCombat(dt, { torqueNm = 0, defenderInput = null } = {}) {
    if (this.done) return { advanced: false, event: null };
    const s = this.step;
    if (s.terminal) {
      this.done = true; this.result = s.terminal;
      return { advanced: false, event: s.terminal };
    }
    if (defenderInput && (s.escapes || []).some(e => e.input === defenderInput)) {
      this.done = true; this.result = 'escape';
      return { advanced: false, event: 'escape' };
    }
    const [lo, hi] = s.band || [0, Infinity];
    if (torqueNm >= lo && torqueNm <= hi) this.dwell += dt;
    else this.dwell = Math.max(0, this.dwell - dt * 2); // torque lost: dwell bleeds
    if (this.dwell >= s.dwell) {
      this.stepIndex++;
      this.dwell = 0;
      return { advanced: true, event: null };
    }
    return { advanced: false, event: null };
  }
  reset() { this.stepIndex = 0; this.dwell = 0; this.done = false; this.result = null; }
}

/* ---------------- GrappleRig: bodies + links + servo contract ----------------
   Minimal two-fighter limb rig for a lock: defender torso (kinematic
   anchor) → defender upper arm → defender forearm, plus attacker torso
   anchor. The active chain step builds its lock link + engine on the fly;
   MuscleStrain reads the lock link's torque node every combat tick. */

function limbSegment(mass, len) {
  // capsule-ish: inertia of a rod about its center, diag approx
  const i = (1/12) * mass * len * len;
  return { mass, inertia: [i, i, i * 0.4] };
}

export class GrappleRig {
  constructor() {
    this.system = new ChronoSystem({ substeps: 2, iterations: 12 });
    this.bodies = {};
    this.activeLink = null;
    this.activeEngine = null;
    this.strain = null;
    this.strains = new Map();   // joint -> MuscleStrain (persists across steps)
    this.chain = null;
    this.muscles = [];
    this._buildBodies();
  }
  _buildBodies() {
    const S = this.system, B = this.bodies;
    // kinematic anchors (the fighters' torsos during the lock)
    B.defTorso = S.addBody(new ChronoBody({ kinematic: true, pos: [0, 1.1, 0], name: 'defTorso' }));
    B.atkTorso = S.addBody(new ChronoBody({ kinematic: true, pos: [0.35, 1.0, 0], name: 'atkTorso' }));
    // defender arm: shoulder → elbow → wrist
    const up = limbSegment(2.2, 0.32), fo = limbSegment(1.4, 0.30);
    B.defUpper = S.addBody(new ChronoBody({ ...up, pos: [0.12, 0.95, 0], name: 'defUpper' }));
    B.defFore = S.addBody(new ChronoBody({ ...fo, pos: [0.12, 0.66, 0], name: 'defFore' }));
    // defender head (neck locks: triangle / rear-naked choke)
    B.defHead = S.addBody(new ChronoBody({ mass: 5, inertia: [0.06, 0.06, 0.06], pos: [0, 1.48, 0], name: 'defHead' }));
    // base posture links (always on during a grapple: limbs attached to body)
    this._shoulderBase = S.addLink(new ChronoLink(JOINT.SPHERICAL, B.defTorso, B.defUpper,
      { anchorA: [0.12, 0.28, 0], anchorB: [0, 0.16, 0], name: 'shoulder_base' }));
    this._neckBase = S.addLink(new ChronoLink(JOINT.SPHERICAL, B.defTorso, B.defHead,
      { anchorA: [0, 0.32, 0], anchorB: [0, -0.12, 0], name: 'neck_base' }));
    this._elbowBase = S.addLink(new ChronoLink(JOINT.REVOLUTE, B.defUpper, B.defFore,
      { anchorA: [0, -0.16, 0], anchorB: [0, 0.15, 0], name: 'elbow_base' }));
  }
  _clearActiveLock() {
    const S = this.system;
    if (this.activeLink) S.links = S.links.filter(l => l !== this.activeLink);
    if (this.activeEngine) S.engines = S.engines.filter(e => e !== this.activeEngine);
    S.externalForces = [];
    this.activeLink = null; this.activeEngine = null;
  }
  _targetBody(joint) {
    const B = this.bodies;
    if (joint === 'elbow' || joint === 'wrist') return B.defFore;
    if (joint === 'neck') return B.defHead;
    return B.defUpper; // shoulder / everything else on the arm
  }
  _buildStepLock(step) {
    this._clearActiveLock();
    if (!step.lock) return;
    const B = this.bodies, S = this.system;
    const { joint, type } = step.lock;
    const target = this._targetBody(joint);
    // attacker grips the limb AWAY from its center of mass so the pull
    // produces a real moment about the joint (the torque the node reads).
    // The grip anchor is placed AT the limb's current position — zero
    // initial constraint error, so the link transmits the attacker's pull
    // instead of yanking (no Baumgarte transient pumping the torque node).
    const gripLocal = joint === 'neck' ? [0, 0.10, 0] : [0, -0.15, 0];
    const gripWorld = v3add(target.p, qrot(target.q, gripLocal));
    const anchorA = v3sub(gripWorld, B.atkTorso.p); // atkTorso: identity rotation
    const link = new ChronoLink(type, B.atkTorso, target, {
      anchorA, anchorB: [...gripLocal], name: joint + '_lock',
    });
    S.addLink(link);
    this.activeLink = link;
    if (step.engine && type === JOINT.REVOLUTE) {
      const eng = new ChronoEngine(link, { ...step.engine, name: joint + '_engine' });
      S.addEngine(eng);
      this.activeEngine = eng;
    }
    if (step.drive) {
      // attacker's constant pull on the limb (the "control" force)
      S.externalForces.push({
        body: target, force: [...step.drive.force], at: [...gripLocal],
      });
    }
    if (!this.strains.has(joint)) this.strains.set(joint, new MuscleStrain(joint));
    this.strain = this.strains.get(joint);
  }

  startChain(chainId) {
    this.chain = new SubmissionChain(chainId);
    this._buildStepLock(this.chain.step);
    return this.chain.stepId;
  }
  /** Authoritative combat tick. Returns chain events + strain state. */
  stepCombat(dt, { defenderInput = null, escapeTorque = 0 } = {}) {
    if (!this.chain || this.chain.done) return { event: null, idle: true };
    // advance the cosmetic solver a matching fixed step so torque nodes are fresh
    this.system.step(dt);
    const link = this.activeLink || this._elbowBase;
    // TORQUE NODE SELECTION (documented in the research doc):
    // - Arm locks (shoulder/elbow): the attacker's grip link IS the lever,
    //   so the joint torque = attacker's applied torque (engine) + the
    //   grip link's constraint reaction.
    // - Chokes (neck): the damage is axial compression of the anatomical
    //   neck joint, so read neck_base: |axial force| × squeeze lever.
    const step = this.chain.step;
    let torqueNm;
    if (step.lock && step.lock.joint === 'neck') {
      const f = this._neckBase.reactionForce;
      const axis = qrot(this.bodies.defTorso.q, [0, 1, 0]); // spine direction
      torqueNm = Math.abs(f[0]*axis[0] + f[1]*axis[1] + f[2]*axis[2]) * 0.18; // NECK_SQUEEZE_LEVER
      torqueNm += v3len(this._neckBase.reactionTorque);
    } else {
      torqueNm = v3len(link.reactionTorque)
        + (this.activeEngine ? Math.abs(this.activeEngine.lastTorque) : 0);
    }
    const sr = this.strain
      ? this.strain.update(torqueNm, dt, escapeTorque)
      : { ratio: 0, progress: 0, tap: false, snap: false };
    if (sr.snap) { this.chain.done = true; this.chain.result = 'snap'; }
    const cev = sr.snap ? { advanced: false, event: 'snap' }
      : sr.tap ? { advanced: false, event: 'tap' }
      : this.chain.stepCombat(dt, { torqueNm, defenderInput });
    if (cev.event === 'tap' || cev.event === 'snap') { this.chain.done = true; this.chain.result = cev.event; }
    if (cev.advanced && !this.chain.done) this._buildStepLock(this.chain.step);
    return {
      event: cev.event, stepId: this.chain.stepId,
      torqueNm, strainRatio: sr.ratio, progress: sr.progress,
    };
  }
  /** Cosmetic per-frame solve for the servo layer. No-op cost while idle. */
  update(dt) {
    if (!this.chain || this.chain.done) return;
    this.system.step(Math.min(dt, 1/30));
  }
  /** PhysicsServo contract: per-limb PD targets. Null while idle. */
  getServoTargets() {
    if (!this.chain || this.chain.done) return null;
    const step = this.chain.step;
    const targets = {};
    // defender limb goes limp-then-tense with strain (Euphoria lesson:
    // stiffness is the control signal)
    const strain = this.strain ? this.strain.progress : 0;
    targets.defFore = {
      joint: 'elbow',
      targetAngle: step.lock && step.lock.joint === 'elbow' ? -2.4 : -0.5,
      stiffness: 30 + 220 * strain,   // muscles fight back as danger rises
      damping: 6,
      driveScale: 0.85,              // mostly servo-driven during the lock
    };
    targets.defUpper = {
      joint: 'shoulder',
      targetAngle: -0.9,
      stiffness: 60 + 120 * strain,
      damping: 8,
      driveScale: 0.7,
    };
    return targets;
  }
  reset() {
    this._clearActiveLock();
    this.chain = null;
    this.strain = null;
    this.strains.clear();
  }
}

/* ---------------- ChronoGrapple facade (integration.js block 8) ---------------- */

export class ChronoGrapple {
  constructor() {
    this.rig = new GrappleRig();
    this.ready = true;
  }
  startChain(chainId) { return this.rig.startChain(chainId); }
  stepCombat(dt, opts) { return this.rig.stepCombat(dt, opts); }
  update(dt) { this.rig.update(dt); }
  getServoTargets() { return this.rig.getServoTargets(); }
  reset() { this.rig.reset(); }
}
