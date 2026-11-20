import { AdditiveBlending as e, CustomBlending as t, Euler as n, MultiplyBlending as r, NoBlending as i, NormalBlending as a, SubtractiveBlending as o, Vector3 as s } from "three";
//#region \0rolldown/runtime.js
var c = Object.create, l = Object.defineProperty, u = Object.getOwnPropertyDescriptor, d = Object.getOwnPropertyNames, f = Object.getPrototypeOf, p = Object.prototype.hasOwnProperty, m = (e, t) => () => (t || (e((t = { exports: {} }).exports, t), e = null), t.exports), h = (e, t, n, r) => {
	if (t && typeof t == "object" || typeof t == "function") for (var i = d(t), a = 0, o = i.length, s; a < o; a++) s = i[a], !p.call(e, s) && s !== n && l(e, s, {
		get: ((e) => t[e]).bind(null, s),
		enumerable: !(r = u(t, s)) || r.enumerable
	});
	return e;
}, g = (e, t, n) => (n = e == null ? {} : c(f(e)), h(t || !e || !e.__esModule ? l(n, "default", {
	value: e,
	enumerable: !0
}) : n, e)), ee = "Behaviour", te = "Alpha", _ = "Attraction", ne = "Collision", re = "Color", v = "CrossZone", ie = "Force", y = "Gravity", ae = "RandomDrift", b = "Repulsion", oe = "Rotate", se = "Scale", ce = "Spring", le = "Vortex", ue = "CurlNoise", de = "Initializer", fe = "Body", pe = "BodySprite", me = "Texture", he = "Life", ge = "Mass", _e = "Position", ve = "Rotation", ye = "Radius", be = "VectorVelocity", xe = "PolarVelocity", Se = "RadialVelocity", Ce = "Rate", we = [pe, me], Te = "Zone", Ee = "BoxZone", De = "LineZone", Oe = "MeshZone", ke = "PointZone", Ae = "ScreenZone", je = "SphereZone", Me = "RingZone", Ne = "DiscZone", Pe = "ConeZone", Fe = "CylinderZone", Ie = "BaseRenderer", Le = "CustomRenderer", Re = "SpriteRenderer", ze = "MeshRenderer", Be = "RibbonRenderer", Ve = "GPURenderer", He = "MobileGPURenderer", Ue = "DesktopGPURenderer", x = 3.142, S = x / 180, We = "euler", Ge = () => typeof process > "u" || !process.env ? !1 : process.env.NODE_ENV === "development", C = {
	easeLinear: function(e) {
		return e;
	},
	easeInQuad: function(e) {
		return e ** 2;
	},
	easeOutQuad: function(e) {
		return -((e - 1) ** 2 - 1);
	},
	easeInOutQuad: function(e) {
		return (e /= .5) < 1 ? .5 * e ** 2 : -.5 * ((e -= 2) * e - 2);
	},
	easeInCubic: function(e) {
		return e ** 3;
	},
	easeOutCubic: function(e) {
		return (e - 1) ** 3 + 1;
	},
	easeInOutCubic: function(e) {
		return (e /= .5) < 1 ? .5 * e ** 3 : .5 * ((e - 2) ** 3 + 2);
	},
	easeInQuart: function(e) {
		return e ** 4;
	},
	easeOutQuart: function(e) {
		return -((e - 1) ** 4 - 1);
	},
	easeInOutQuart: function(e) {
		return (e /= .5) < 1 ? .5 * e ** 4 : -.5 * ((e -= 2) * e ** 3 - 2);
	},
	easeInSine: function(e) {
		return -Math.cos(x / 2 * e) + 1;
	},
	easeOutSine: function(e) {
		return Math.sin(x / 2 * e);
	},
	easeInOutSine: function(e) {
		return -.5 * (Math.cos(x * e) - 1);
	},
	easeInExpo: function(e) {
		return e === 0 ? 0 : 2 ** (10 * (e - 1));
	},
	easeOutExpo: function(e) {
		return e === 1 ? 1 : -(2 ** (-10 * e)) + 1;
	},
	easeInOutExpo: function(e) {
		return e === 0 ? 0 : e === 1 ? 1 : (e /= .5) < 1 ? .5 * 2 ** (10 * (e - 1)) : .5 * (-(2 ** (-10 * --e)) + 2);
	},
	easeInCirc: function(e) {
		return -(Math.sqrt(1 - e * e) - 1);
	},
	easeOutCirc: function(e) {
		return Math.sqrt(1 - (e - 1) ** 2);
	},
	easeInOutCirc: function(e) {
		return (e /= .5) < 1 ? -.5 * (Math.sqrt(1 - e * e) - 1) : .5 * (Math.sqrt(1 - (e -= 2) * e) + 1);
	},
	easeInBack: function(e) {
		var t = 1.70158;
		return e * e * ((t + 1) * e - t);
	},
	easeOutBack: function(e) {
		var t = 1.70158;
		return --e * e * ((t + 1) * e + t) + 1;
	},
	easeInOutBack: function(e) {
		var t = 1.70158;
		return (e /= .5) < 1 ? .5 * (e * e * (((t *= 1.525) + 1) * e - t)) : .5 * ((e -= 2) * e * (((t *= 1.525) + 1) * e + t) + 2);
	}
}, { easeLinear: Ke, easeInQuad: qe, easeOutQuad: Je, easeInOutQuad: Ye, easeInCubic: Xe, easeOutCubic: Ze, easeInOutCubic: Qe, easeInQuart: $e, easeOutQuart: et, easeInOutQuart: tt, easeInSine: nt, easeOutSine: rt, easeInOutSine: it, easeInExpo: at, easeOutExpo: ot, easeInOutExpo: st, easeInCirc: ct, easeOutCirc: lt, easeInOutCirc: ut, easeInBack: dt, easeOutBack: ft, easeInOutBack: pt } = C, mt = (e) => C[e], ht = (e) => mt(e) || C.easeLinear, w = (e) => e && mt(e) || C.easeLinear, gt = Infinity, _t = Ke, vt = .0167, yt = 2e3, bt = [
	_e,
	ve,
	he,
	ye,
	ge,
	fe,
	pe,
	me,
	xe,
	Se,
	be
], xt = [
	te,
	_,
	re,
	v,
	ie,
	y,
	ae,
	b,
	oe,
	se,
	ce,
	le,
	ue
], St = [
	Ee,
	De,
	Oe,
	ke,
	je,
	Me,
	Ne,
	Pe,
	Fe
], T = (e, t) => e.includes(t), Ct = { getRGB: function(e) {
	let t = {
		r: 0,
		g: 0,
		b: 0
	};
	if (typeof e == "number") t.r = (e >> 16 & 255) / 255, t.g = (e >> 8 & 255) / 255, t.b = (e & 255) / 255;
	else if (typeof e == "string") {
		var n;
		if (n = /^(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(,\s*([0-9]*\.?[0-9]+)\s*)?$/.exec(e)) t.r = Math.min(255, parseInt(n[1], 10)) / 255, t.g = Math.min(255, parseInt(n[2], 10)) / 255, t.b = Math.min(255, parseInt(n[3], 10)) / 255;
		else if (n = /^\#([A-Fa-f0-9]+)$/.exec(e)) {
			var r = n[1];
			t.r = parseInt(r.charAt(0) + r.charAt(1), 16) / 255, t.g = parseInt(r.charAt(2) + r.charAt(3), 16) / 255, t.b = parseInt(r.charAt(4) + r.charAt(5), 16) / 255;
		}
	} else t.r = e.r, t.g = e.g, t.b = e.b;
	return t;
} }, wt = {
	_id: 0,
	_uids: /* @__PURE__ */ new Map(),
	getNewId: function() {
		return `PUID_${++this._id}`;
	},
	id: function(e) {
		if (this._uids.has(e)) return this._uids.get(e);
		let t = this.getNewId();
		return this._uids.set(e, t), t;
	}
}, E = {
	toScreenPos: (function() {
		var e = new s();
		return function(t, n, r) {
			return e.copy(t), e.project(n), e.x = Math.round((e.x + 1) * r.width / 2), e.y = Math.round((-e.y + 1) * r.height / 2), e.z = 0, e;
		};
	})(),
	toSpacePos: (function() {
		var e = new s(), t = new s(), n;
		return function(r, i, a) {
			return e.set(r.x / a.width * 2 - 1, -(r.y / a.height) * 2 + 1, .5), e.unproject(i), t.copy(e.sub(i.position).normalize()), n = -i.position.z / t.z, e.copy(i.position), e.add(t.multiplyScalar(n)), e;
		};
	})()
}, D = {
	initValue: function(e, t) {
		return e != null && e != null ? e : t;
	},
	isArray: function(e) {
		return Object.prototype.toString.call(e) === "[object Array]";
	},
	destroyArray: function(e) {
		e.length = 0;
	},
	destroyObject: function(e) {
		for (var t in e) delete e[t];
	},
	isUndefined: function(...e) {
		for (var t in e) if (e[t] !== void 0) return !1;
		return !0;
	},
	setVectorByObj: function(e, t) {
		t.x !== void 0 && (e.position.x = t.x), t.y !== void 0 && (e.position.y = t.y), t.z !== void 0 && (e.position.z = t.z), t.vx !== void 0 && (e.velocity.x = t.vx), t.vy !== void 0 && (e.velocity.y = t.vy), t.vz !== void 0 && (e.velocity.z = t.vz), t.ax !== void 0 && (e.acceleration.x = t.ax), t.ay !== void 0 && (e.acceleration.y = t.ay), t.az !== void 0 && (e.acceleration.z = t.az), t.p !== void 0 && e.position.copy(t.p), t.v !== void 0 && e.velocity.copy(t.v), t.a !== void 0 && e.acceleration.copy(t.a), t.position !== void 0 && e.position.copy(t.position), t.velocity !== void 0 && e.velocity.copy(t.velocity), t.accelerate !== void 0 && e.acceleration.copy(t.accelerate);
	},
	setPrototypeByObj: function(e, t, n) {
		for (var r in t) e.hasOwnProperty(r) && (n ? n.indexOf(r) < 0 && (e[r] = this._getValue(t[r])) : e[r] = this._getValue(t[r]));
		return e;
	},
	_getValue: function(e) {
		return e.constructor.type === "Span" ? e.getValue() : e;
	}
}, O = [];
for (let e = 0; e < 256; ++e) O.push((e + 256).toString(16).slice(1));
function Tt(e, t = 0) {
	return (O[e[t + 0]] + O[e[t + 1]] + O[e[t + 2]] + O[e[t + 3]] + "-" + O[e[t + 4]] + O[e[t + 5]] + "-" + O[e[t + 6]] + O[e[t + 7]] + "-" + O[e[t + 8]] + O[e[t + 9]] + "-" + O[e[t + 10]] + O[e[t + 11]] + O[e[t + 12]] + O[e[t + 13]] + O[e[t + 14]] + O[e[t + 15]]).toLowerCase();
}
//#endregion
//#region node_modules/uuid/dist/esm-browser/rng.js
var Et, Dt = /* @__PURE__ */ new Uint8Array(16);
function Ot() {
	if (!Et) {
		if (typeof crypto > "u" || !crypto.getRandomValues) throw Error("crypto.getRandomValues() not supported. See https://github.com/uuidjs/uuid#getrandomvalues-not-supported");
		Et = crypto.getRandomValues.bind(crypto);
	}
	return Et(Dt);
}
//#endregion
//#region node_modules/uuid/dist/esm-browser/v1.js
var k = {};
function kt(e, t, n) {
	let r, i = e?._v6 ?? !1;
	if (e) {
		let t = Object.keys(e);
		t.length === 1 && t[0] === "_v6" && (e = void 0);
	}
	if (e) r = jt(e.random ?? e.rng?.() ?? Ot(), e.msecs, e.nsecs, e.clockseq, e.node, t, n);
	else {
		let e = Date.now(), a = Ot();
		At(k, e, a), r = jt(a, k.msecs, k.nsecs, i ? void 0 : k.clockseq, i ? void 0 : k.node, t, n);
	}
	return t ?? Tt(r);
}
function At(e, t, n) {
	return e.msecs ?? (e.msecs = -Infinity), e.nsecs ?? (e.nsecs = 0), t === e.msecs ? (e.nsecs++, e.nsecs >= 1e4 && (e.node = void 0, e.nsecs = 0)) : t > e.msecs ? e.nsecs = 0 : t < e.msecs && (e.node = void 0), e.node || (e.node = n.slice(10, 16), e.node[0] |= 1, e.clockseq = (n[8] << 8 | n[9]) & 16383), e.msecs = t, e;
}
function jt(e, t, n, r, i, a, o = 0) {
	if (e.length < 16) throw Error("Random bytes length must be >= 16");
	if (!a) a = /* @__PURE__ */ new Uint8Array(16), o = 0;
	else if (o < 0 || o + 16 > a.length) throw RangeError(`UUID byte range ${o}:${o + 15} is out of buffer bounds`);
	t ?? (t = Date.now()), n ?? (n = 0), r ?? (r = (e[8] << 8 | e[9]) & 16383), i ?? (i = e.slice(10, 16)), t += 0xb1d069b5400;
	let s = ((t & 268435455) * 1e4 + n) % 4294967296;
	a[o++] = s >>> 24 & 255, a[o++] = s >>> 16 & 255, a[o++] = s >>> 8 & 255, a[o++] = s & 255;
	let c = t / 4294967296 * 1e4 & 268435455;
	a[o++] = c >>> 8 & 255, a[o++] = c & 255, a[o++] = c >>> 24 & 15 | 16, a[o++] = c >>> 16 & 255, a[o++] = r >>> 8 | 128, a[o++] = r & 255;
	for (let e = 0; e < 6; ++e) a[o++] = i[e];
	return a;
}
//#endregion
//#region src/utils/uid.ts
var A = kt, j = (e, t) => ({
	...e,
	...t
}), M = {
	randomAToB: function(e, t, n, r) {
		let i = r ?? Math.random;
		return n ? (i() * (t - e) >> 0) + e : e + i() * (t - e);
	},
	randomFloating: function(e, t, n, r) {
		return this.randomAToB(e - t, e + t, n, r);
	},
	randomZone: function(e) {},
	degreeTransform: function(e) {
		return e * x / 180;
	},
	toColor16: function(e) {
		return "#" + e.toString(16);
	},
	randomColor: function(e) {
		return "#" + ("00000" + ((e ?? Math.random)() * 16777216 << 0).toString(16)).slice(-6);
	},
	lerp: function(e, t, n) {
		return t + (e - t) * n;
	},
	getNormal: function(e, t) {
		return e.x == 0 && e.y == 0 ? e.z == 0 ? t.set(1, 0, 1) : t.set(1, 1, -e.y / e.z) : e.x == 0 ? t.set(1, 0, 1) : t.set(-e.y / e.x, 1, 1), t.normalize();
	},
	axisRotate: function(e, t, n, r) {
		var i = Math.cos(r), a = Math.sin(r), o = n.dot(t) * (1 - i);
		e.copy(n), e.cross(t).scalar(a), e.addValue(t.x * i, t.y * i, t.z * i), e.addValue(n.x * o, n.y * o, n.z * o);
	}
}, Mt = "ArraySpan", Nt = "ColorSpan", Pt = "Polar3D", Ft = "Span", N = class {
	constructor(e, t, n) {
		this._isArray = !1, this.type = Ft, D.isArray(e) ? (this._isArray = !0, this.a = e) : (this.a = D.initValue(e, 1), this.b = D.initValue(t, this.a), this._center = D.initValue(n, !1));
	}
	getValue(e, t) {
		if (this._isArray) {
			let e = this.a, n = t ?? Math.random;
			return e[e.length * n() >> 0];
		} else {
			let n = this.a;
			return this._center ? M.randomFloating(n, this.b, e, t) : M.randomAToB(n, this.b, e, t);
		}
	}
}, P = (e, t, n) => e instanceof N ? e : t === void 0 ? new N(e) : n === void 0 ? new N(e, t) : new N(e, t, n), It = class extends N {
	constructor(e) {
		super(), this.type = Mt, this.items = Array.isArray(e) ? e : [e];
	}
	getValue(e, t) {
		let n = t ?? Math.random;
		return this.items[n() * this.items.length >> 0];
	}
}, Lt = (e) => e ? e instanceof It ? e : new It(e) : null, Rt = class extends N {
	constructor(e) {
		super(), this.type = Nt, this.shouldRandomize = e === "random", this.colors = Array.isArray(e) ? e : [e];
	}
	getValue(e, t) {
		let n = t ?? Math.random;
		return this.shouldRandomize ? M.randomColor(t) : this.colors[n() * this.colors.length >> 0];
	}
}, zt = (e) => (e || (console.warn(`Invalid colors argument ${e} passed to createColorSpan. Defaulting to 'random'.`), e = "random"), e instanceof Rt ? e : new Rt(e)), Bt = class {
	constructor(e, t, n, r, i, a) {
		this.type = "Box", this.x = e, this.y = t, this.z = n, this.width = r, this.height = i, this.depth = a, this.bottom = this.y + this.height, this.right = this.x + this.width;
	}
	contains(e, t, n) {
		return e <= this.right && e >= this.x && t <= this.bottom && t >= this.y && n <= this.depth && n >= this.z;
	}
}, F = "EULER", Vt = "RUNGE_KUTTA_2", Ht = "RUNGE_KUTTA_4", Ut = "VERLET", Wt = (e, t, n) => {
	e.sleep || (e.old.position.copy(e.position), e.old.velocity.copy(e.velocity), e.acceleration.scalar(1 / e.mass), e.velocity.add(e.acceleration.scalar(t)), e.position.add(e.old.velocity.scalar(t)), n && e.velocity.scalar(n ** (t / .0167)), e.acceleration.clear());
}, Gt = (e, t, n, r = F) => {
	switch (r) {
		case F:
			Wt(e, t, n);
			break;
		default: Wt(e, t, n);
	}
}, I = class extends s {
	clear() {
		return this.x = 0, this.y = 0, this.z = 0, this;
	}
	scalar(e) {
		return this.x *= e, this.y *= e, this.z *= e, this;
	}
	addValue(e, t, n) {
		return this.x += e, this.y += t, this.z += n, this;
	}
	toString() {
		return "x:" + this.x + "y:" + this.y + "z:" + this.z;
	}
	eulerFromDir(e) {
		return new n().setFromVector3(e);
	}
}, Kt = class e {
	constructor(e, t, n) {
		this.type = Pt, this.radius = e || 1, this.phi = n || 0, this.theta = t || 0;
	}
	set(e, t, n) {
		return this.radius = e || 1, this.phi = n || 0, this.theta = t || 0, this;
	}
	setRadius(e) {
		return this.radius = e, this;
	}
	setPhi(e) {
		return this.phi = e, this;
	}
	setTheta(e) {
		return this.theta = e, this;
	}
	copy(e) {
		return this.radius = e.radius, this.phi = e.phi, this.theta = e.theta, this;
	}
	toVector3D() {
		return new I(this.getX(), this.getY(), this.getZ());
	}
	getX() {
		return this.radius * Math.sin(this.theta) * Math.cos(this.phi);
	}
	getY() {
		return -this.radius * Math.sin(this.theta) * Math.sin(this.phi);
	}
	getZ() {
		return this.radius * Math.cos(this.theta);
	}
	normalize() {
		return this.radius = 1, this;
	}
	equals(e) {
		return e.radius === this.radius && e.phi === this.phi && e.theta === this.theta;
	}
	clear() {
		return this.radius = 0, this.phi = 0, this.theta = 0, this;
	}
	clone() {
		return new e(this.radius, this.phi, this.theta);
	}
}, qt = "Particle", Jt = "Pool", Yt = "System", Xt = class {
	constructor(e = {}) {
		this.id = `particle-${A()}`, this.emitterId = null, this.emitterInstanceId = null, this.spawnIndex = 0, this.type = qt, this.life = gt, this.age = 0, this.energy = 1, this.dead = !1, this.sleep = !1, this.body = null, this.parent = null, this.mass = 1, this.radius = 10, this.alpha = 1, this.scale = 1, this.useColor = !1, this.useAlpha = !1, this.easing = _t, this.position = new I(), this.velocity = new I(), this.acceleration = new I(), this.old = {
			position: this.position.clone(),
			velocity: this.velocity.clone(),
			acceleration: this.acceleration.clone()
		}, this.behaviours = [], this.transform = {}, this.color = {
			r: 0,
			g: 0,
			b: 0
		}, this.rotation = new I(), this.rng = Math.random, this.distanceToCamera = 0, D.setPrototypeByObj(this, e);
	}
	getDirection() {
		return Math.atan2(this.velocity.x, -this.velocity.y) * (180 / x);
	}
	reset() {
		return this.life = gt, this.age = 0, this.energy = 1, this.dead = !1, this.sleep = !1, this.body = null, this.parent = null, this.mass = 1, this.radius = 10, this.alpha = 1, this.scale = 1, this.useColor = !1, this.useAlpha = !1, this.easing = _t, this.position.set(0, 0, 0), this.velocity.set(0, 0, 0), this.acceleration.set(0, 0, 0), this.old.position.set(0, 0, 0), this.old.velocity.set(0, 0, 0), this.old.acceleration.set(0, 0, 0), this.color.r = 0, this.color.g = 0, this.color.b = 0, this.rotation.clear(), D.destroyObject(this.transform), this.removeAllBehaviours(), this;
	}
	update(e, t) {
		if (!this.sleep) {
			this.age += e;
			let n = this.behaviours.length;
			for (; n--;) this.behaviours[n].applyBehaviour(this, e, t);
		}
		if (this.age >= this.life) this.destroy();
		else {
			let e = this.easing(this.age / this.life);
			this.energy = Math.max(1 - e, 0);
		}
	}
	addBehaviour(e) {
		this.behaviours.push(e), e.initialize(this);
	}
	addBehaviours(e) {
		let t = e.length;
		for (; t--;) this.addBehaviour(e[t]);
	}
	removeBehaviour(e) {
		let t = this.behaviours.indexOf(e);
		t > -1 && this.behaviours.splice(t, 1);
	}
	removeAllBehaviours() {
		D.destroyArray(this.behaviours);
	}
	destroy() {
		this.removeAllBehaviours(), this.energy = 0, this.dead = !0, this.parent = null;
	}
}, L = class {
	constructor() {
		this.type = Jt, this.cID = 0, this.list = {};
	}
	create(e, ...t) {
		if (!this.canCreateNewObject(e)) throw Error("The pool is unable to create or clone the object supplied");
		if (this.cID++, this.canInstantiateObject(e)) return new e(...t);
		if (this.canCloneObject(e)) return e.clone();
	}
	canInstantiateObject(e) {
		return typeof e == "function";
	}
	canCloneObject(e) {
		let t = e.clone;
		return !!t && typeof t == "function";
	}
	canCreateNewObject(e) {
		return !!(this.canInstantiateObject(e) || this.canCloneObject(e));
	}
	getCount() {
		var e = 0;
		for (var t in this.list) e += this.list[t].length;
		return e++;
	}
	get(e, ...t) {
		var n, r = e.__puid || wt.id(e);
		return n = this.list[r] && this.list[r].length > 0 ? this.list[r].pop() : this.create(e, ...t), n.__puid = e.__puid || r, n;
	}
	expire(e) {
		return this._getList(e.__puid).push(e);
	}
	destroy() {
		for (var e in this.list) this.list[e].length = 0, delete this.list[e];
	}
	_getList(e) {
		return e = e || "default", this.list[e] || (this.list[e] = []), this.list[e];
	}
}, Zt = class {
	constructor() {
		this.listeners = null;
	}
	set listeners(e) {
		this._listeners = e;
	}
	get listeners() {
		return this._listeners;
	}
	addEventListener(e, t) {
		return this.listeners ? this.removeEventListener(e, t) : this.listeners = {}, this.listeners[e] || (this.listeners[e] = []), this.listeners[e].push(t), t;
	}
	removeEventListener(e, t) {
		if (this.listeners && this.listeners[e]) {
			for (var n = this.listeners[e], r = 0, i = n.length; r < i; r++) if (n[r] == t) {
				i == 1 ? delete this.listeners[e] : n.splice(r, 1);
				break;
			}
		}
	}
	removeAllEventListeners(e) {
		e ? this.listeners && delete this.listeners[e] : this.listeners = null;
	}
	dispatchEvent(e, t) {
		var n = !1, r = this.listeners;
		if (e && r) {
			var i = r[e];
			if (!i) return !!n;
			i = i.slice();
			for (var a, o = i.length; o--;) a = i[o], n = n || a(t);
		}
		return !!n;
	}
	hasEventListener(e) {
		var t = this.listeners;
		return !!(t && t[e]);
	}
}, Qt = "SYSTEM_UPDATE", $t = "PARTICLE_CREATED", en = "PARTICLE_UPDATE", tn = "PARTICLE_DEAD", nn = "EMITTER_ADDED", rn = "EMITTER_REMOVED", an = "EMITTER_DEAD", on = "SYSTEM_UPDATE_AFTER", sn = Zt, R = class {
	constructor(e = de, t = !0) {
		this.type = e, this.isEnabled = t;
	}
	init(e, t) {
		this.isEnabled && (t ? (this.initialize(t), t.hasBeenInitialized = !0) : (this.initialize(e), e.hasBeenInitialized = !0));
	}
	reset() {}
	initialize(e) {}
	static requiresWebGlApi() {
		return !1;
	}
	static fromJSON(e, ...t) {}
}, cn = class e extends R {
	constructor(e, t, n, r = !0) {
		super(fe, r), this.body = Lt(e), this.w = t, this.h = n || t;
	}
	initialize(e) {
		let t = this.body.getValue(!1, e.rng);
		this.w ? e.body = {
			width: this.w,
			height: this.h,
			body: t
		} : e.body = t;
	}
	static fromJSON(t) {
		let { body: n, width: r, height: i, isEnabled: a = !0 } = t;
		return new e(n, r, i, a);
	}
}, ln = {
	AdditiveBlending: e,
	CustomBlending: t,
	MultiplyBlending: r,
	NoBlending: i,
	NormalBlending: a,
	SubtractiveBlending: o
}, z = {
	color: 16711680,
	blending: e,
	fog: !0
}, B = {
	...z,
	blending: "AdditiveBlending"
}, un = class e extends R {
	constructor(e, t, n = z, r = !0) {
		super(pe, r);
		let { Sprite: i, SpriteMaterial: a, TextureLoader: o } = e;
		this.materialProperties = j(z, n), new o().load(t, (e) => {
			this.texture = e, this.material = new a({
				map: e,
				...this.materialProperties
			}), this.sprite = new i(this.material);
		}, void 0, (e) => {
			throw Error(e);
		});
	}
	initialize(e) {
		e.body = this.sprite;
	}
	static fromJSON(t, n) {
		let { texture: r, materialProperties: i = B, isEnabled: a = !0 } = t;
		return new e(n, r, j(B, ((e) => {
			let { blending: t } = e;
			return {
				...e,
				blending: t ? ln[t] : ln[B.blending]
			};
		})(i)), a);
	}
}, dn = new n(), fn = {
	particleEuler: null,
	initialize: function(e, t, n) {
		let r = n.length;
		for (; r--;) n[r].init(e, t);
		e.bindEmitter && this.bindEmitter(e, t);
	},
	bindEmitter: function(e, t) {
		let { rotation: { x: n, y: r, z: i } } = e;
		t.position.add(e.position), t.velocity.add(e.velocity), t.acceleration.add(e.acceleration), t.velocity.applyEuler(dn.set(n, r, i));
	}
}, pn = class e extends R {
	constructor(e, t, n, r = !0) {
		super(he, r), this.lifePan = P(e, t, n);
	}
	initialize(e) {
		this.lifePan.a == Infinity || this.lifePan.a == "infi" ? e.life = Infinity : e.life = this.lifePan.getValue(!1, e.rng);
	}
	static fromJSON(t) {
		let { min: n, max: r, center: i = !1, isEnabled: a = !0 } = t;
		return new e(n, r, i, a);
	}
}, mn = class e extends R {
	constructor(e, t, n = !1, r = !0) {
		super(ge, r), this.massPan = P(e, t, n);
	}
	initialize(e) {
		e.mass = this.massPan.getValue(!1, e.rng);
	}
	static fromJSON(t) {
		let { min: n, max: r, center: i = !1, isEnabled: a = !0 } = t;
		return new e(n, r, i, a);
	}
}, V = class {
	constructor(e = Te) {
		this.type = e, this.vector = new I(0, 0, 0), this.random = 0, this.crossType = "dead", this.log = !0, this.supportsCrossing = !0;
	}
	getPosition(e) {
		return null;
	}
	crossing(e) {
		if (!this.supportsCrossing) {
			console.warn(`${this.constructor.name} does not support the crossing method`);
			return;
		}
		switch (this.crossType) {
			case "bound":
				this._bound(e);
				break;
			case "cross":
				this._cross(e);
				break;
			case "dead":
				this._dead(e);
				break;
		}
	}
	isBoxZone() {
		return !1;
	}
	isLineZone() {
		return !1;
	}
	isMeshZone() {
		return !1;
	}
	isPointZone() {
		return !1;
	}
	isScreenZone() {
		return !1;
	}
	isSphereZone() {
		return !1;
	}
	isRingZone() {
		return !1;
	}
	isConeZone() {
		return !1;
	}
	isCylinderZone() {
		return !1;
	}
	_dead(e) {}
	_bound(e) {}
	_cross(e) {}
}, hn = class extends V {
	constructor(e, t, n, r, i, a) {
		super(Ee);
		var o, s, c, l, u;
		D.isUndefined(t, n, r, i, a) ? (o = s = c = 0, l = u = r = e || 100) : D.isUndefined(r, i, a) ? (o = s = c = 0, l = e, u = t, r = n) : (o = e, s = t, c = n, l = r, u = i, r = a), this.x = o, this.y = s, this.z = c, this.width = l, this.height = u, this.depth = r, this.friction = .85, this.max = 6;
	}
	isBoxZone() {
		return !0;
	}
	getPosition(e) {
		return this.vector.x = this.x + M.randomAToB(-.5, .5, void 0, e) * this.width, this.vector.y = this.y + M.randomAToB(-.5, .5, void 0, e) * this.height, this.vector.z = this.z + M.randomAToB(-.5, .5, void 0, e) * this.depth, this.vector;
	}
	_dead(e) {
		(e.position.x + e.radius < this.x - this.width / 2 || e.position.x - e.radius > this.x + this.width / 2) && (e.dead = !0), (e.position.y + e.radius < this.y - this.height / 2 || e.position.y - e.radius > this.y + this.height / 2) && (e.dead = !0), (e.position.z + e.radius < this.z - this.depth / 2 || e.position.z - e.radius > this.z + this.depth / 2) && (e.dead = !0);
	}
	_bound(e) {
		e.position.x - e.radius < this.x - this.width / 2 ? (e.position.x = this.x - this.width / 2 + e.radius, e.velocity.x *= -this.friction, this._static(e, "x")) : e.position.x + e.radius > this.x + this.width / 2 && (e.position.x = this.x + this.width / 2 - e.radius, e.velocity.x *= -this.friction, this._static(e, "x")), e.position.y - e.radius < this.y - this.height / 2 ? (e.position.y = this.y - this.height / 2 + e.radius, e.velocity.y *= -this.friction, this._static(e, "y")) : e.position.y + e.radius > this.y + this.height / 2 && (e.position.y = this.y + this.height / 2 - e.radius, e.velocity.y *= -this.friction, this._static(e, "y")), e.position.z - e.radius < this.z - this.depth / 2 ? (e.position.z = this.z - this.depth / 2 + e.radius, e.velocity.z *= -this.friction, this._static(e, "z")) : e.position.z + e.radius > this.z + this.depth / 2 && (e.position.z = this.z + this.depth / 2 - e.radius, e.velocity.z *= -this.friction, this._static(e, "z"));
	}
	_static(e, t) {
		e.velocity[t] * e.acceleration[t] > 0 || Math.abs(e.velocity[t]) < Math.abs(e.acceleration[t]) * .0167 * this.max && (e.velocity[t] = 0, e.acceleration[t] = 0);
	}
	_cross(e) {
		e.position.x + e.radius < this.x - this.width / 2 && e.velocity.x <= 0 ? e.position.x = this.x + this.width / 2 + e.radius : e.position.x - e.radius > this.x + this.width / 2 && e.velocity.x >= 0 && (e.position.x = this.x - this.width / 2 - e.radius), e.position.y + e.radius < this.y - this.height / 2 && e.velocity.y <= 0 ? e.position.y = this.y + this.height / 2 + e.radius : e.position.y - e.radius > this.y + this.height / 2 && e.velocity.y >= 0 && (e.position.y = this.y - this.height / 2 - e.radius), e.position.z + e.radius < this.z - this.depth / 2 && e.velocity.z <= 0 ? e.position.z = this.z + this.depth / 2 + e.radius : e.position.z - e.radius > this.z + this.depth / 2 && e.velocity.z >= 0 && (e.position.z = this.z - this.depth / 2 - e.radius);
	}
}, gn = class extends V {
	constructor(e, t, n, r, i, a) {
		if (super(De), e instanceof I) {
			let t = r;
			this.x1 = e.x, this.y1 = e.y, this.z1 = e.z, this.x2 = t.x, this.y2 = t.y, this.z2 = t.z;
		} else this.x1 = e, this.y1 = t, this.z1 = n, this.x2 = r, this.y2 = i, this.z2 = a;
		this.supportsCrossing = !1;
	}
	isLineZone() {
		return !0;
	}
	getPosition(e) {
		return this.random = (e ?? Math.random)(), this.vector.x = this.x1 + this.random * (this.x2 - this.x1), this.vector.y = this.y1 + this.random * (this.y2 - this.y1), this.vector.z = this.z1 + this.random * (this.z2 - this.z1), this.vector;
	}
}, _n = class extends V {
	constructor(e, t = 1, n) {
		if (super(Oe), this.geometry = null, this.scale = t, this.supportsCrossing = !1, e.type && e.type === "Geometry" && (this.geometry = e), e.geometry && (this.geometry = e.geometry), !this.geometry) throw Error("MeshZone unable to set geometry from the supplied bounds");
		this.geometry.isBufferGeometry && (this.geometry = new n().fromBufferGeometry(this.geometry));
	}
	isMeshZone() {
		return !0;
	}
	getPosition(e) {
		let t = e ?? Math.random, n = this.geometry.vertices, r = n[n.length * t() >> 0];
		return this.vector.x = r.x * this.scale, this.vector.y = r.y * this.scale, this.vector.z = r.z * this.scale, this.vector;
	}
}, vn = class extends V {
	constructor(e, t, n) {
		super(ke);
		let r = 0;
		D.isUndefined(e, t, n) || (r = e), this.x = r, this.y = r, this.z = r, this.supportsCrossing = !1;
	}
	isPointZone() {
		return !0;
	}
	getPosition() {
		return this.vector.x = this.x, this.vector.y = this.y, this.vector.z = this.z, this.vector;
	}
}, yn = new I(), H = new I(), bn = class extends V {
	constructor(e, t, n, r) {
		super(Ae), this.camera = e, this.renderer = t, this.dis = n || 20, r = r || "1234", this.d1 = r.indexOf("1") >= 0, this.d2 = r.indexOf("2") >= 0, this.d3 = r.indexOf("3") >= 0, this.d4 = r.indexOf("4") >= 0;
	}
	isScreenZone() {
		return !0;
	}
	getPosition(e) {
		let t = e ?? Math.random, n = this.renderer.domElement;
		return yn.x = t() * n.width, yn.y = t() * n.height, this.vector.copy(E.toSpacePos(yn, this.camera, n)), this.vector;
	}
	_dead(e) {
		let t = E.toScreenPos(e.position, this.camera, this.renderer.domElement), n = this.renderer.domElement;
		(t.y + e.radius < -this.dis && this.d1 || t.y - e.radius > n.height + this.dis && this.d3) && (e.dead = !0), (t.x + e.radius < -this.dis && this.d4 || t.x - e.radius > n.width + this.dis && this.d2) && (e.dead = !0);
	}
	_bound(e) {
		let t = E.toScreenPos(e.position, this.camera, this.renderer.domElement), n = this.renderer.domElement;
		(t.y + e.radius < -this.dis || t.y - e.radius > n.height + this.dis) && (e.velocity.y *= -1), (t.x + e.radius < -this.dis || t.x - e.radius > n.width + this.dis) && (e.velocity.y *= -1);
	}
	_cross(e) {
		let t = E.toScreenPos(e.position, this.camera, this.renderer.domElement), n = this.renderer.domElement;
		t.y + e.radius < -this.dis ? (H.x = t.x, H.y = n.height + this.dis + e.radius, e.position.y = E.toSpacePos(H, this.camera, n).y) : t.y - e.radius > n.height + this.dis && (H.x = t.x, H.y = -this.dis - e.radius, e.position.y = E.toSpacePos(H, this.camera, n).y), t.x + e.radius < -this.dis ? (H.y = t.y, H.x = n.width + this.dis + e.radius, e.position.x = E.toSpacePos(H, this.camera, n).x) : t.x - e.radius > n.width + this.dis && (H.y = t.y, H.x = -this.dis - e.radius, e.position.x = E.toSpacePos(H, this.camera, n).x);
	}
}, xn = new I(), Sn = new I(), Cn = class extends V {
	constructor(e, t, n, r) {
		super(je);
		let i = 0, a = 0, o = 0, s = 100;
		D.isUndefined(t, n, r) ? s = e || 100 : (i = e, a = t, o = n, s = r), this.x = i, this.y = a, this.z = o, this.radius = s, this.the = this.phi = 0;
	}
	isSphereZone() {
		return !0;
	}
	getPosition(e) {
		let t = e ?? Math.random;
		this.random = t();
		let n = this.random * this.radius, r = x * t(), i = x * 2 * t();
		return this.vector.x = this.x + n * Math.sin(r) * Math.cos(i), this.vector.y = this.y + n * Math.sin(i) * Math.sin(r), this.vector.z = this.z + n * Math.cos(r), this.vector;
	}
	_dead(e) {
		e.position.distanceTo(this) - e.radius > this.radius && (e.dead = !0);
	}
	_bound(e) {
		if (e.position.distanceTo(this) + e.radius >= this.radius) {
			xn.copy(e.position).sub(this).normalize(), Sn.copy(e.velocity);
			let t = 2 * Sn.dot(xn);
			e.velocity.sub(xn.scalar(t));
		}
	}
	_cross() {
		console.warn(`${this.constructor.name} does not support the _cross method`);
	}
}, wn = Math.PI * 2, Tn = class extends V {
	constructor(e = 0, t = 0, n = 0, r = 0, i = 100) {
		super(Me), this.x = e, this.y = t, this.z = n, this.innerRadius = r, this.outerRadius = i, this.supportsCrossing = !1;
	}
	isRingZone() {
		return !0;
	}
	getPosition(e) {
		let t = e ?? Math.random, n = this.innerRadius * this.innerRadius, r = this.outerRadius * this.outerRadius;
		this.random = t();
		let i = Math.sqrt(n + (r - n) * this.random), a = wn * t();
		return this.vector.x = this.x + i * Math.cos(a), this.vector.y = this.y, this.vector.z = this.z + i * Math.sin(a), this.vector;
	}
}, En = class extends Tn {
	constructor(e = 0, t = 0, n = 0, r = 100) {
		super(e, t, n, 0, r), this.type = Ne;
	}
}, Dn = Math.PI * 2, On = class extends V {
	constructor(e = 0, t = 0, n = 0, r = 100, i = 100) {
		super(Pe), this.x = e, this.y = t, this.z = n, this.radius = r, this.height = i;
	}
	isConeZone() {
		return !0;
	}
	getPosition(e) {
		let t = e ?? Math.random;
		this.random = t();
		let n = Math.cbrt(this.random), r = n * this.radius, i = Math.sqrt(t()) * r, a = Dn * t();
		return this.vector.x = this.x + i * Math.cos(a), this.vector.y = this.y + n * this.height, this.vector.z = this.z + i * Math.sin(a), this.vector;
	}
	_dead(e) {
		let t = e.position.y - this.y;
		if (t < -e.radius || t - e.radius > this.height) {
			e.dead = !0;
			return;
		}
		let n = e.position.x - this.x, r = e.position.z - this.z, i = Math.sqrt(n * n + r * r), a = this.height > 0 ? Math.max(t, 0) / this.height * this.radius : 0;
		i - e.radius > a && (e.dead = !0);
	}
	_bound() {
		console.warn(`${this.constructor.name} does not support the _bound method`);
	}
	_cross() {
		console.warn(`${this.constructor.name} does not support the _cross method`);
	}
}, kn = Math.PI * 2, An = class extends V {
	constructor(e = 0, t = 0, n = 0, r = 100, i = 100) {
		super(Fe), this.x = e, this.y = t, this.z = n, this.radius = r, this.height = i;
	}
	isCylinderZone() {
		return !0;
	}
	getPosition(e) {
		let t = e ?? Math.random;
		this.random = t();
		let n = Math.sqrt(this.random) * this.radius, r = kn * t(), i = (t() - .5) * this.height;
		return this.vector.x = this.x + n * Math.cos(r), this.vector.y = this.y + i, this.vector.z = this.z + n * Math.sin(r), this.vector;
	}
	_dead(e) {
		let t = e.position.x - this.x, n = e.position.y - this.y, r = e.position.z - this.z;
		(Math.sqrt(t * t + r * r) - e.radius > this.radius || Math.abs(n) - e.radius > this.height / 2) && (e.dead = !0);
	}
	_bound(e) {
		let t = e.position.x - this.x, n = e.position.z - this.z, r = Math.sqrt(t * t + n * n) || 1e-6;
		if (r + e.radius >= this.radius) {
			let i = t / r, a = n / r, o = 2 * (e.velocity.x * i + e.velocity.z * a);
			e.velocity.x -= o * i, e.velocity.z -= o * a;
		}
	}
	_cross() {
		console.warn(`${this.constructor.name} does not support the _cross method`);
	}
}, jn = {
	BoxZone: hn,
	LineZone: gn,
	MeshZone: _n,
	PointZone: vn,
	ScreenZone: bn,
	SphereZone: Cn,
	RingZone: Tn,
	DiscZone: En,
	ConeZone: On,
	CylinderZone: An
}, Mn = (e, t) => {
	let n = jn[e];
	return new n(...t);
}, Nn = class e extends R {
	constructor(...e) {
		super(_e), this.reset(...e);
	}
	reset(...e) {
		this.zones ? this.zones.length = 0 : this.zones = [], this.zones = this.zones.concat(e);
	}
	addZone(...e) {
		this.zones = this.zones.concat(e);
	}
	initialize(e) {
		let t = this.zones[e.rng() * this.zones.length >> 0];
		t.getPosition(e.rng), e.position.x = t.vector.x, e.position.y = t.vector.y, e.position.z = t.vector.z;
	}
	static fromJSON(t) {
		let { zoneType: n, ...r } = t;
		if (!n || !T(St, n)) throw Error(`The zone type ${n} is invalid or not yet supported`);
		return new e(Mn(n, Object.values(r)));
	}
}, Pn = class e extends R {
	constructor(e, t, n, r = !0, i = !0) {
		super(ve, i), this.rotation = new s(e, t, n), this.useEmitterRotation = r;
	}
	initialize(e) {
		this.useEmitterRotation ? e.rotation.copy(e.parent.rotation).add(this.rotation) : e.rotation.copy(this.rotation);
	}
	static fromJSON(t) {
		let { x: n, y: r, z: i, useEmitterRotation: a = !0, isEnabled: o = !0 } = t;
		return new e(n, r, i, a, o);
	}
}, Fn = class e extends R {
	constructor(e, t, n = !1, r = !0) {
		super(ye, r), this.radius = P(e, t, n);
	}
	reset(e, t, n = !1) {
		this.radius = P(e, t, n);
	}
	initialize(e) {
		e.radius = this.radius.getValue(!1, e.rng), e.transform.oldRadius = e.radius;
	}
	static fromJSON(t) {
		let { width: n, height: r, center: i = !1, isEnabled: a = !0 } = t;
		return new e(n, r, i, a);
	}
}, U = class e extends R {
	constructor(e = 1, t = 1) {
		super(Ce), this.numPan = P(e), this.timePan = P(t), this.startTime = 0, this.nextTime = 0, this.init();
	}
	init() {
		this.resetInterval();
	}
	resetInterval(e) {
		this.startTime = 0, this.nextTime = this.timePan.getValue(!1, e);
	}
	getValue(e, t) {
		return this.startTime += e, this.startTime >= this.nextTime ? (this.resetInterval(t), this.numPan.b == 1 ? +(this.numPan.getValue(!0, t) > .5) : this.numPan.getValue(!0, t)) : 0;
	}
	static fromJSON(t) {
		let { particlesMin: n, particlesMax: r, perSecondMin: i, perSecondMax: a } = t;
		return new e(new N(n, r), new N(i, a));
	}
}, In = class e extends R {
	constructor(e, t, n = z, r = !0) {
		super(me, r);
		let { Sprite: i, SpriteMaterial: a } = e;
		this.materialProperties = j(z, n), this.texture = t, this.material = new a({
			map: t,
			...this.materialProperties
		}), this.sprite = new i(this.material);
	}
	initialize(e) {
		e.body = this.sprite;
	}
	static fromJSON(t, n) {
		let { loadedTexture: r, materialProperties: i = B, isEnabled: a = !0 } = t;
		return new e(n, r, j(B, ((e) => {
			let { blending: t } = e;
			return {
				...e,
				blending: t ? ln[t] : ln[B.blending]
			};
		})(i)), a);
	}
}, Ln = new I(0, 0, 1), Rn = new I(0, 0, 0), zn = class extends R {
	constructor(e, t = !0) {
		super(e, t), this.dirVec = new I(0, 0, 0);
	}
	normalize(e) {
		return e * 100;
	}
	initialize(e) {
		let t = this.tha * e.rng();
		this._useV && this.dirVec.copy(this.dir).scalar(this.radiusPan.getValue(!1, e.rng)), M.getNormal(this.dirVec, Ln), Rn.copy(this.dirVec).applyAxisAngle(Ln, t), Rn.applyAxisAngle(this.dirVec.normalize(), e.rng() * x * 2), e.velocity.copy(Rn);
	}
}, Bn = class e extends zn {
	constructor(e, t, n = !0) {
		super(xe, n), this.tha = t * S, this.dirVec = e.toVector3D(), this._useV = !1;
	}
	static fromJSON(t) {
		let { polarRadius: n, polarTheta: r, polarPhi: i, velocityTheta: a, isEnabled: o = !0 } = t;
		return new e(new Kt(n, r, i), a, o);
	}
}, Vn = class e extends zn {
	constructor(e, t, n, r = !0) {
		super(Se, r), this.radiusPan = P(e), this.dir = t.clone().normalize(), this.tha = n * S, this._useV = !0;
	}
	static fromJSON(t) {
		let { radius: n, x: r, y: i, z: a, theta: o, isEnabled: s = !0 } = t;
		return new e(n, new I(r, i, a), o, s);
	}
}, Hn = class e extends zn {
	constructor(e, t, n = !0) {
		super(be, n), this.radiusPan = P(1), this.dir = e.clone(), this.tha = t * S, this._useV = !0;
	}
	static fromJSON(t) {
		let { x: n, y: r, z: i, theta: a, isEnabled: o = !0 } = t;
		return new e(new I(n, r, i), a, o);
	}
}, Un = .006, Wn = new U(1, .1), Gn = "always", Kn = "none", qn = "none", Jn = "detach", Yn = "spawn", W = (e) => {
	let t = e >>> 0;
	return () => {
		t |= 0, t = t + 1831565813 | 0;
		let e = Math.imul(t ^ t >>> 15, 1 | t);
		return e = e + Math.imul(e ^ e >>> 7, 61 | e) ^ e, ((e ^ e >>> 14) >>> 0) / 4294967296;
	};
}, Xn = (...e) => {
	let t = 2166136261, n = e.join("\0");
	for (let e = 0; e < n.length; e++) t ^= n.charCodeAt(e), t = Math.imul(t, 16777619);
	return t >>> 0;
}, Zn = () => Math.random() * 4294967296 >>> 0, Qn = /* @__PURE__ */ m(((e, t) => {
	t.exports = typeof global == "object" && global && global.Object === Object && global;
})), $n = /* @__PURE__ */ m(((e, t) => {
	var n = Qn(), r = typeof self == "object" && self && self.Object === Object && self;
	t.exports = n || r || Function("return this")();
})), er = /* @__PURE__ */ m(((e, t) => {
	t.exports = $n().Symbol;
})), tr = /* @__PURE__ */ m(((e, t) => {
	var n = er(), r = Object.prototype, i = r.hasOwnProperty, a = r.toString, o = n ? n.toStringTag : void 0;
	function s(e) {
		var t = i.call(e, o), n = e[o];
		try {
			e[o] = void 0;
			var r = !0;
		} catch {}
		var s = a.call(e);
		return r && (t ? e[o] = n : delete e[o]), s;
	}
	t.exports = s;
})), nr = /* @__PURE__ */ m(((e, t) => {
	var n = Object.prototype.toString;
	function r(e) {
		return n.call(e);
	}
	t.exports = r;
})), rr = /* @__PURE__ */ m(((e, t) => {
	var n = er(), r = tr(), i = nr(), a = "[object Null]", o = "[object Undefined]", s = n ? n.toStringTag : void 0;
	function c(e) {
		return e == null ? e === void 0 ? o : a : s && s in Object(e) ? r(e) : i(e);
	}
	t.exports = c;
})), ir = /* @__PURE__ */ m(((e, t) => {
	function n(e) {
		return typeof e == "object" && !!e;
	}
	t.exports = n;
})), G = /* @__PURE__ */ g((/* @__PURE__ */ m(((e, t) => {
	var n = rr(), r = ir(), i = "[object Number]";
	function a(e) {
		return typeof e == "number" || r(e) && n(e) == i;
	}
	t.exports = a;
})))()), ar = "Emitter", or = "FollowEmitter", sr = (e, t) => e === "always" || t && e === "onCreate", cr = (e, t, n) => {
	let { inherit: r } = e;
	sr(r.position, n) && e.position.copy(t.position), sr(r.rotation, n) && e.rotation.copy(t.rotation), sr(r.scale, n) && (e._inheritedScale = t.scale);
}, lr = class e extends Xt {
	constructor(e) {
		super(e), this.type = ar, this.seed = Zn(), this.rng = W(this.seed), this._spawnCount = 0, this.nodeId = "", this.childNodes = [], this.inherit = {
			position: Gn,
			rotation: Kn,
			scale: qn
		}, this.orphanPolicy = Jn, this.trigger = Yn, this._template = null, this._parentParticle = null, this._inheritedScale = 1, this._freeInstances = [], this.activeChildren = /* @__PURE__ */ new Map(), this.particles = [], this.initializers = [], this.behaviours = [], this.emitterBehaviours = [], this.currentEmitTime = 0, this.totalEmitTimes = -1, this.damping = Un, this.bindEmitter = !0, this.bindEmitterEvent = !1, this.rate = Wn, this.isEmitting = !1, this.id = `emitter-${A()}`, this.cID = 0, this.name = "Emitter", this.index = void 0, this.eventDispatcher = new sn();
	}
	get system() {
		return this.parent;
	}
	reseed(e, t) {
		return this.seed = Xn(e, t), this.rng = W(this.seed), this._spawnCount = 0, this;
	}
	reseedFromParent(e, t) {
		return this.seed = Xn(e, t), this.rng = W(this.seed), this._spawnCount = 0, this;
	}
	_createInstance() {
		let t = new e();
		return t._template = this, t.nodeId = this.nodeId, t.initializers = this.initializers, t.behaviours = this.behaviours, t.emitterBehaviours = this.emitterBehaviours, t.childNodes = this.childNodes, t.inherit = this.inherit, t.orphanPolicy = this.orphanPolicy, t.trigger = this.trigger, t.damping = this.damping, t.rate = new U(this.rate.numPan, this.rate.timePan), t.totalEmitTimes = this.totalEmitTimes, t.life = this.life, t;
	}
	_resetInstanceState() {
		let e = this._template;
		this.age = 0, this.dead = !1, this.energy = 1, this.currentEmitTime = 0, this.totalEmitTimes = e.totalEmitTimes, this.life = e.life, this._spawnCount = 0, this.isEmitting = !1, this.particles.length = 0, this.activeChildren.clear(), this._parentParticle = null, this._inheritedScale = 1, this.position.set(0, 0, 0), this.rotation.clear();
	}
	acquireInstance(e) {
		let t = this._freeInstances.pop() ?? this._createInstance();
		return t._resetInstanceState(), t._parentParticle = e, t.reseedFromParent(this.nodeId, e.id), t.rate.resetInterval(t.rng), t.isEmitting = !0, t;
	}
	releaseInstance(e) {
		e.isEmitting = !1, this._freeInstances.push(e);
	}
	_assignNodeIds(e, t = 0, n = 4) {
		if (t > n) throw Error(`three-nebula: emitter hierarchy exceeds maxDepth (${n}) at "${e}"`);
		this.nodeId = e;
		for (let r = 0; r < this.childNodes.length; r++) this.childNodes[r]._assignNodeIds(`${e}/children/${r}`, t + 1, n);
	}
	addChild(e) {
		return this.childNodes.push(e), this;
	}
	_spawnChildrenFor(e) {
		let t = this.system, n = [];
		for (let r = 0; r < this.childNodes.length; r++) {
			let i = this.childNodes[r];
			if (i.trigger !== "spawn") continue;
			let a = t.spawnEmitterInstance(i, e);
			a && (cr(a, e, !0), n.push(a));
		}
		n.length && this.activeChildren.set(e, n);
	}
	_triggerDeathChildren(e) {
		let t = this.system;
		for (let n = 0; n < this.childNodes.length; n++) {
			let r = this.childNodes[n];
			if (r.trigger !== "death") continue;
			let i = t.spawnEmitterInstance(r, e);
			i && (i.position.copy(e.position), t._detachInstance(i, !1));
		}
	}
	_orphanChildrenOf(e) {
		let t = this.activeChildren.get(e);
		if (!t) return;
		let n = this.system;
		for (let e = 0; e < t.length; e++) {
			let r = t[e];
			r.orphanPolicy === "kill" ? n._killInstance(r) : n._detachInstance(r);
		}
		this.activeChildren.delete(e);
	}
	_updateChildInstances(e) {
		this.activeChildren.size && this.activeChildren.forEach((t, n) => {
			for (let r = 0; r < t.length; r++) {
				let i = t[r];
				cr(i, n, !1), i.update(e);
			}
		});
	}
	dispatch(e, t = this) {
		this.eventDispatcher.dispatchEvent(e, t);
	}
	setRate(e) {
		return this.rate = e, this;
	}
	setPosition(e = {}) {
		let { position: t } = this, { x: n = t.x, y: r = t.y, z: i = t.z } = e;
		return this.position.set(n, r, i), this;
	}
	setRotation(e = {}) {
		let { rotation: t } = this, { x: n = t.x, y: r = t.y, z: i = t.z } = e;
		return this.rotation.set(n, r, i), this;
	}
	emit(e = Infinity, t = Infinity) {
		return this.currentEmitTime = 0, this.totalEmitTimes = (0, G.default)(e) ? e : Infinity, e === 1 ? this.life = e : this.life = (0, G.default)(t) ? t : Infinity, this.rate.resetInterval(this.rng), this.isEmitting = !0, this;
	}
	experimental_emit() {
		let { isEmitting: e, totalEmitTimes: t, life: n } = this;
		return e || (this.currentEmitTime = 0, t || this.setTotalEmitTimes(Infinity), n || this.setLife(Infinity), this.rate.init(), this.isEmitting = !0), this;
	}
	setTotalEmitTimes(e = Infinity) {
		return this.totalEmitTimes = (0, G.default)(e) ? e : Infinity, this;
	}
	setLife(e = Infinity) {
		return this.totalEmitTimes === 1 ? this.life = this.totalEmitTimes : this.life = (0, G.default)(e) ? e : Infinity, this;
	}
	stopEmit() {
		this.totalEmitTimes = -1, this.currentEmitTime = 0, this.isEmitting = !1;
	}
	removeAllParticles() {
		let e = this.particles.length;
		for (; e--;) this.particles[e].dead = !0;
	}
	addInitializer(e) {
		return this.initializers.push(e), this;
	}
	addInitializers(e) {
		let t = e.length;
		for (; t--;) this.addInitializer(e[t]);
		return this;
	}
	setInitializers(e) {
		return this.initializers = e, this;
	}
	removeInitializer(e) {
		let t = this.initializers.indexOf(e);
		return t > -1 && this.initializers.splice(t, 1), this;
	}
	removeAllInitializers() {
		return D.destroyArray(this.initializers), this;
	}
	addBehaviour(e) {
		return this.behaviours.push(e), this;
	}
	addBehaviours(e) {
		let t = e.length;
		for (; t--;) this.addBehaviour(e[t]);
		return this;
	}
	setBehaviours(e) {
		return this.behaviours = e, this;
	}
	removeBehaviour(e) {
		let t = this.behaviours.indexOf(e);
		return t > -1 && this.behaviours.splice(t, 1), this;
	}
	removeAllBehaviours() {
		return D.destroyArray(this.behaviours), this;
	}
	addEmitterBehaviour(e) {
		return this.emitterBehaviours.push(e), e.initialize(this), this;
	}
	addEmitterBehaviours(e) {
		let t = e.length;
		for (; t--;) this.addEmitterBehaviour(e[t]);
		return this;
	}
	setEmitterBehaviours(e) {
		let t = e.length;
		this.emitterBehaviours = e;
		for (let e = 0; e < t; e++) this.emitterBehaviours[e].initialize(this);
		return this;
	}
	removeEmitterBehaviour(e) {
		let t = this.emitterBehaviours.indexOf(e);
		return t > -1 && this.emitterBehaviours.splice(t, 1), this;
	}
	removeAllEmitterBehaviours() {
		return D.destroyArray(this.emitterBehaviours), this;
	}
	addOnEmitterDeadEventListener(e) {
		return this.eventDispatcher.addEventListener(`${this.id}_${an}`, () => e()), this;
	}
	createParticle() {
		let e = this.system.pool.get(Xt), t = this.particles.length;
		return this.setupParticle(e, t), this.system && this.system.dispatch("PARTICLE_CREATED", e), this.bindEmitterEvent && this.dispatch("PARTICLE_CREATED", e), this.childNodes.length && this.system && this._spawnChildrenFor(e), e;
	}
	setupParticle(e, t) {
		let { initializers: n, behaviours: r } = this, i = this._spawnCount++;
		e.id = `particle-${this.seed}-${i}`, e.rng = W(Xn(this.seed, i)), e.emitterId = this.nodeId || null, e.emitterInstanceId = `${this.seed}`, e.spawnIndex = i, fn.initialize(this, e, n), this._inheritedScale !== 1 && (e.radius *= this._inheritedScale), e.addBehaviours(r), e.parent = this, e.index = t, this.particles.push(e);
	}
	update(e) {
		if (!this.isEmitting && this.particles.length === 0) return;
		this.age += e, (this.dead || this.age >= this.life) && this.destroy(), this.isEmitting && this.generate(e), this.integrate(e);
		let t = this.particles.length;
		for (; t--;) {
			let e = this.particles[t];
			e.dead && (this.childNodes.length && this._triggerDeathChildren(e), this.activeChildren.size && this._orphanChildrenOf(e), this.system && this.system.dispatch("PARTICLE_DEAD", e), this.bindEmitterEvent && this.dispatch("PARTICLE_DEAD", e), this.system.pool.expire(e.reset()), this.particles.splice(t, 1), this.particles.length === 0 && this.system && this.system.dispatch("SYSTEM_UPDATE"));
		}
		this.updateEmitterBehaviours(e), this._updateChildInstances(e);
	}
	updateEmitterBehaviours(e) {
		if (this.sleep) return;
		let t = this.emitterBehaviours.length;
		for (let n = 0; n < t; n++) this.emitterBehaviours[n].applyBehaviour(this, e, n);
	}
	integrate(e) {
		let t = this.system ? this.system.integrationType : F, n = 1 - this.damping;
		Gt(this, e, n, t);
		let r = this.particles.length;
		for (; r--;) {
			let i = this.particles[r];
			i.update(e, r), Gt(i, e, n, t), this.system && this.system.dispatch("PARTICLE_UPDATE", i), this.bindEmitterEvent && this.dispatch("PARTICLE_UPDATE", i);
		}
	}
	generate(e) {
		if (this.totalEmitTimes === 1) {
			let e = this.rate.getValue(99999, this.rng);
			for (e > 0 && (this.cID = e); e--;) this.createParticle();
			this.totalEmitTimes = 0;
			return;
		}
		if (this.currentEmitTime += e, this.currentEmitTime < this.totalEmitTimes) {
			let t = this.rate.getValue(e, this.rng);
			for (t > 0 && (this.cID = t); t--;) this.createParticle();
		}
	}
	destroy() {
		this.dead = !0, this.energy = 0, this.totalEmitTimes = -1, this.particles.length == 0 && (this.isEmitting = !1, this.removeAllInitializers(), this.removeAllBehaviours(), this.dispatch(`${this.id}_${an}`), this.system && this.system.removeEmitter(this));
	}
}, K = Infinity, ur = 1e3, q = Ke, dr = .03, fr = .01, pr = .1, mr = "dead", J = class {
	constructor(e = Infinity, t = q, n = ee, r = !0) {
		this.type = n, this.isEnabled = r, this.id = `behaviour-${A()}`, this.life = e, this.easing = t, this.age = 0, this.energy = 1, this.dead = !1;
	}
	reset(e = K, t = q, ...n) {
		this.life = e, this.easing = t || q;
	}
	set life(e) {
		this._life = (0, G.default)(e) ? e : K;
	}
	get life() {
		return this._life;
	}
	normalizeForce(e) {
		return e.scalar(100);
	}
	normalizeValue(e) {
		return e * 100;
	}
	initialize(e) {}
	applyBehaviour(e, t, n) {
		this.isEnabled && this.mutate(e, t, n);
	}
	mutate(e, t, n) {}
	energize(e, t, n) {
		if (this.dead) return;
		if (this.age += t, this.age >= this.life) {
			this.energy = 0, this.dead = !0;
			return;
		}
		let r = this.easing(e.age / e.life);
		this.energy = Math.max(1 - r, 0);
	}
	destroy() {}
	fromJSON(e) {}
}, hr = class e extends J {
	constructor(e = 1, t = null, n, r, i = !0) {
		super(n, r, te, i), this.reset(e, t);
	}
	get same() {
		return this._same;
	}
	set same(e) {
		this._same = e;
	}
	reset(e = 1, t = null, n, r) {
		this.same = t == null, this.alphaA = P(e), this.alphaB = P(t), n && super.reset(n, r);
	}
	initialize(e) {
		e.useAlpha = !0, e.transform.alphaA = this.alphaA.getValue(!1, e.rng), e.transform.alphaB = this.same ? e.transform.alphaA : this.alphaB.getValue(!1, e.rng);
	}
	mutate(e, t, n) {
		this.energize(e, t, n), e.alpha = M.lerp(e.transform.alphaA, e.transform.alphaB, this.energy), e.alpha < .002 && (e.alpha = 0);
	}
	static fromJSON(t) {
		let { alphaA: n, alphaB: r, life: i, easing: a, isEnabled: o = !0 } = t;
		return new e(n, r, i, w(a), o);
	}
}, gr = class e extends J {
	constructor(e = new I(), t = 100, n = ur, r = K, i = q, a = !0) {
		super(r, i, _, a), this.targetPosition = e, this.radius = n, this.force = this.normalizeValue(t), this.radiusSq = this.radius * this.radius, this.attractionForce = new I(), this.lengthSq = 0;
	}
	reset(e = new I(), t = 100, n = ur, r, i) {
		this.targetPosition = e, this.radius = n, this.force = this.normalizeValue(t), this.radiusSq = this.radius * this.radius, this.attractionForce = new I(), this.lengthSq = 0, r && super.reset(r, i);
	}
	mutate(e, t, n) {
		this.energize(e, t, n), this.attractionForce.copy(this.targetPosition), this.attractionForce.sub(e.position), this.lengthSq = this.attractionForce.lengthSq(), this.lengthSq > 4e-6 && this.lengthSq < this.radiusSq && (this.attractionForce.normalize(), this.attractionForce.scalar(1 - this.lengthSq / this.radiusSq), this.attractionForce.scalar(this.force), e.acceleration.add(this.attractionForce));
	}
	static fromJSON(t) {
		let { x: n, y: r, z: i, force: a, radius: o, life: s, easing: c, isEnabled: l = !0 } = t;
		return new e(new I(n, r, i), a, o, s, w(c), l);
	}
}, _r = class extends J {
	constructor(e, t, n, r, i, a = !0) {
		super(r, i, ne, a), this.reset(e, t, n);
	}
	reset(e, t, n, r, i) {
		this.emitter = e, this.useMass = t, this.onCollide = n, this.particles = [], this.delta = new I(), r && super.reset(r, i);
	}
	mutate(e, t, n) {
		let r = this.emitter ? this.emitter.particles.slice(n) : this.particles.slice(n), i, a, o, s, c, l, u = r.length;
		for (; u--;) i = r[u], i != e && (this.delta.copy(i.position).sub(e.position), a = this.delta.lengthSq(), s = e.radius + i.radius, a <= s * s && (o = s - Math.sqrt(a), o += .5, c = this._getAverageMass(e, i), l = this._getAverageMass(i, e), e.position.add(this.delta.clone().normalize().scalar(o * -c)), i.position.add(this.delta.normalize().scalar(o * l)), this.onCollide && this.onCollide(e, i)));
	}
	_getAverageMass(e, t) {
		return this.useMass ? t.mass / (e.mass + t.mass) : .5;
	}
	fromJSON(e) {}
}, vr = class e extends J {
	constructor(e, t, n, r, i = !0) {
		super(n, r, re, i), this.reset(e, t);
	}
	get same() {
		return this._same;
	}
	set same(e) {
		this._same = e;
	}
	reset(e, t, n, r) {
		this.same = t == null, this.colorA = zt(e), this.colorB = zt(t), n && super.reset(n, r);
	}
	initialize(e) {
		e.transform.colorA = Ct.getRGB(this.colorA.getValue(!1, e.rng)), e.useColor = !0, e.transform.colorB = this.same ? e.transform.colorA : Ct.getRGB(this.colorB.getValue(!1, e.rng));
	}
	mutate(e, t, n) {
		this.energize(e, t, n), this._same ? (e.color.r = e.transform.colorA.r, e.color.g = e.transform.colorA.g, e.color.b = e.transform.colorA.b) : (e.color.r = M.lerp(e.transform.colorA.r, e.transform.colorB.r, this.energy), e.color.g = M.lerp(e.transform.colorA.g, e.transform.colorB.g, this.energy), e.color.b = M.lerp(e.transform.colorA.b, e.transform.colorB.b, this.energy));
	}
	static fromJSON(t) {
		let { colorA: n, colorB: r, life: i, easing: a, isEnabled: o = !0 } = t;
		return new e(n, r, i, w(a), o);
	}
}, yr = class e extends J {
	constructor(e, t, n, r, i) {
		super(n, r, v, i), this.reset(e, t);
	}
	reset(e, t = mr, n, r) {
		this.zone = e, this.zone.crossType = t, n && super.reset(n, r);
	}
	mutate(e, t, n) {
		this.energize(e, t, n), this.zone.crossing.call(this.zone, e);
	}
	static fromJSON(t) {
		let { zoneType: n, zoneParams: r, crossType: i, life: a, easing: o, isEnabled: s = !0 } = t, c = Mn(n, Object.values(r));
		return new e(c, i, a, w(o), s);
	}
}, br = class e extends J {
	constructor(e, t, n, r, i, a = !0) {
		super(r, i, ie, a), this.reset(e, t, n);
	}
	reset(e, t, n) {
		this.force = this.normalizeForce(new I(e, t, n)), this.force.id = Math.random();
	}
	mutate(e, t, n) {
		this.energize(e, t, n), e.acceleration.add(this.force);
	}
	static fromJSON(t) {
		let { fx: n, fy: r, fz: i, life: a, easing: o, isEnabled: s = !0 } = t;
		return new e(n, r, i, a, w(o), s);
	}
}, xr = class e extends br {
	constructor(e, t, n, r = !0) {
		super(0, -e, 0, t, n, r), this.type = y;
	}
	static fromJSON(t) {
		let { gravity: n, life: r, easing: i, isEnabled: a = !0 } = t;
		return new e(n, r, w(i), a);
	}
}, Sr = class e extends J {
	constructor(e, t, n, r = dr, i, a, o = !0) {
		super(i, a, ae, o), this.reset(e, t, n, r), this.time = 0;
	}
	reset(e, t, n, r = dr, i, a) {
		this.randomForce = this.normalizeForce(new I(e, t, n)), this.delayPan = P(r), this.time = 0, i && super.reset(i, a);
	}
	mutate(e, t, n) {
		if (this.energize(e, t, n), this.time += t, this.time >= this.delayPan.getValue(!1, e.rng)) {
			let { rng: t } = e, n = M.randomAToB(-this.randomForce.x, this.randomForce.x, void 0, t), r = M.randomAToB(-this.randomForce.y, this.randomForce.y, void 0, t), i = M.randomAToB(-this.randomForce.z, this.randomForce.z, void 0, t);
			e.acceleration.addValue(n, r, i), this.time = 0;
		}
	}
	static fromJSON(t) {
		let { x: n, y: r, z: i, delay: a, life: o, easing: s, isEnabled: c = !0 } = t;
		return new e(n, r, i, a, o, w(s), c);
	}
}, Cr = class e extends gr {
	constructor(e, t, n, r, i, a = !0) {
		super(e, t, n, r, i, a), this.force *= -1, this.type = b;
	}
	reset(e, t, n, r, i) {
		super.reset(e, t, n, r, i), this.force *= -1;
	}
	static fromJSON(t) {
		let { x: n, y: r, z: i, force: a, radius: o, life: s, easing: c, isEnabled: l = !0 } = t;
		return new e(new I(n, r, i), a, o, s, w(c), l);
	}
}, wr = class e extends J {
	constructor(e, t, n, r, i, a = !0) {
		super(r, i, oe, a), this.reset(e, t, n);
	}
	get rotationType() {
		return this._rotationType;
	}
	set rotationType(e) {
		this._rotationType = e;
	}
	reset(e, t, n, r, i) {
		this.x = e || 0, this.y = t || 0, this.z = n || 0, e === void 0 || e == "same" ? this.rotationType = "same" : t == null ? this.rotationType = "set" : n === void 0 ? this.rotationType = "to" : (this.rotationType = "add", this.x = P(this.x * S), this.y = P(this.y * S), this.z = P(this.z * S)), r && super.reset(r, i);
	}
	initialize(e) {
		switch (this.rotationType) {
			case "same": break;
			case "set":
				this._setRotation(e.rotation, this.x, e.rng);
				break;
			case "to":
				e.transform.fR = e.transform.fR || new I(), e.transform.tR = e.transform.tR || new I(), this._setRotation(e.transform.fR, this.x, e.rng), this._setRotation(e.transform.tR, this.y, e.rng);
				break;
			case "add":
				e.transform.addR = new I(this.x.getValue(!1, e.rng), this.y.getValue(!1, e.rng), this.z.getValue(!1, e.rng));
				break;
		}
	}
	_setRotation(e, t, n) {
		if (e = e || new I(), t == "random") {
			var r = M.randomAToB(-x, x, void 0, n), i = M.randomAToB(-x, x, void 0, n), a = M.randomAToB(-x, x, void 0, n);
			e.set(r, i, a);
		} else t instanceof I && e.copy(t);
	}
	mutate(e, t, n) {
		switch (this.energize(e, t, n), this.rotationType) {
			case "same":
				e.rotation || (e.rotation = new I()), e.rotation.copy(e.velocity);
				break;
			case "set": break;
			case "to":
				e.rotation.x = M.lerp(e.transform.fR.x, e.transform.tR.x, this.energy), e.rotation.y = M.lerp(e.transform.fR.y, e.transform.tR.y, this.energy), e.rotation.z = M.lerp(e.transform.fR.z, e.transform.tR.z, this.energy);
				break;
			case "add":
				e.rotation.add(e.transform.addR);
				break;
		}
	}
	static fromJSON(t) {
		let { x: n, y: r, z: i, life: a, easing: o, isEnabled: s = !0 } = t;
		return new e(n, r, i, a, w(o), s);
	}
}, Tr = class e extends J {
	constructor(e, t, n, r, i = !0) {
		super(n, r, se, i), this.reset(e, t);
	}
	get same() {
		return this._same;
	}
	set same(e) {
		this._same = e;
	}
	reset(e, t, n, r) {
		this.same = t == null, this.scaleA = P(e || 1), this.scaleB = P(t), n && super.reset(n, r);
	}
	initialize(e) {
		e.transform.scaleA = this.scaleA.getValue(!1, e.rng), e.transform.oldRadius = e.radius, e.transform.scaleB = this.same ? e.transform.scaleA : this.scaleB.getValue(!1, e.rng);
	}
	mutate(e, t, n) {
		this.energize(e, t, n), e.scale = M.lerp(e.transform.scaleA, e.transform.scaleB, this.energy), e.scale < 5e-4 && (e.scale = 0), e.radius = e.transform.oldRadius * e.scale;
	}
	static fromJSON(t) {
		let { scaleA: n, scaleB: r, life: i, easing: a, isEnabled: o = !0 } = t;
		return new e(n, r, i, w(a), o);
	}
}, Er = class e extends J {
	constructor(e, t, n, r, i, a, o, s = !0) {
		super(a, o, ce, s), this.reset(e, t, n, r, i);
	}
	reset(e, t, n, r, i) {
		this.pos ? this.pos.set(e, t, n) : this.pos = new I(e, t, n), this.spring = r || .1, this.friction = i || .98;
	}
	mutate(e, t, n) {
		this.energize(e, t, n), e.velocity.x += (this.pos.x - e.position.x) * this.spring, e.velocity.y += (this.pos.y - e.position.y) * this.spring, e.velocity.z += (this.pos.z - e.position.z) * this.spring;
	}
	static fromJSON(t) {
		let { x: n, y: r, z: i, spring: a, friction: o, life: s, easing: c, isEnabled: l = !0 } = t;
		return new e(n, r, i, a, o, s, w(c), l);
	}
}, Dr = class e extends J {
	constructor(e = new I(), t = new I(0, 0, 1), n = 400, r = 0, i = 1, a = K, o = q, s = !0) {
		super(a, o, le, s), this.center = e, this.axis = t.clone().normalize(), this.swirl = n, this.pull = r, this.falloff = i, this._radial = new I(), this._tangential = new I(), this._axisProjection = new I();
	}
	reset(e = new I(), t = new I(0, 0, 1), n = 400, r = 0, i = 1, a, o) {
		this.center = e, this.axis = t.clone().normalize(), this.swirl = n, this.pull = r, this.falloff = i, a && super.reset(a, o);
	}
	mutate(e, t, n) {
		this.energize(e, t, n), this._radial.copy(e.position).sub(this.center);
		let r = this._radial.dot(this.axis);
		this._radial.sub(this._axisProjection.copy(this.axis).scalar(r));
		let i = this._radial.length();
		if (i < 1e-4) return;
		let a = 1 / i ** +this.falloff;
		this._tangential.copy(this.axis).cross(this._radial), e.velocity.addScaledVector(this._tangential, this.swirl * a * t).addScaledVector(this._radial, -this.pull * a * t);
	}
	static fromJSON(t) {
		let { x: n = 0, y: r = 0, z: i = 0, axisX: a = 0, axisY: o = 0, axisZ: s = 1, swirl: c, pull: l, falloff: u, life: d, easing: f, isEnabled: p = !0 } = t;
		return new e(new I(n, r, i), new I(a, o, s), c, l, u, d, w(f), p);
	}
}, Or = (e) => e * e * e * (e * (e * 6 - 15) + 10), Y = (e, t, n) => t + e * (n - t), X = (e, t, n, r) => {
	let i = e & 15, a = i < 8 ? t : n, o = i < 4 ? n : i === 12 || i === 14 ? t : r;
	return (i & 1 ? -a : a) + (i & 2 ? -o : o);
}, kr = class {
	constructor(e) {
		let t = W(e), n = /* @__PURE__ */ new Uint8Array(256);
		for (let e = 0; e < 256; e++) n[e] = e;
		for (let e = 255; e > 0; e--) {
			let r = Math.floor(t() * (e + 1)), i = n[e];
			n[e] = n[r], n[r] = i;
		}
		this.perm = /* @__PURE__ */ new Uint8Array(512);
		for (let e = 0; e < 512; e++) this.perm[e] = n[e & 255];
	}
	noise(e, t, n) {
		let r = this.perm, i = Math.floor(e) & 255, a = Math.floor(t) & 255, o = Math.floor(n) & 255;
		e -= Math.floor(e), t -= Math.floor(t), n -= Math.floor(n);
		let s = Or(e), c = Or(t), l = Or(n), u = r[i] + a, d = r[u] + o, f = r[u + 1] + o, p = r[i + 1] + a, m = r[p] + o, h = r[p + 1] + o;
		return Y(l, Y(c, Y(s, X(r[d], e, t, n), X(r[m], e - 1, t, n)), Y(s, X(r[f], e, t - 1, n), X(r[h], e - 1, t - 1, n))), Y(c, Y(s, X(r[d + 1], e, t, n - 1), X(r[m + 1], e - 1, t, n - 1)), Y(s, X(r[f + 1], e, t - 1, n - 1), X(r[h + 1], e - 1, t - 1, n - 1))));
	}
}, Ar = new I(31.416, 47.853, 12.793), jr = new I(71.123, 13.547, 91.371), Mr = class e extends J {
	constructor(e = fr, t = 100, n = 1, r = K, i = q, a = !0) {
		super(r, i, ue, a), this.scale = e, this.strength = t, this.seed = n, this._noise = new kr(n), this._curl = new I(), this._pxp = new I(), this._pxm = new I(), this._pyp = new I(), this._pym = new I(), this._pzp = new I(), this._pzm = new I();
	}
	reset(e = fr, t = 100, n = 1, r, i) {
		this.scale = e, this.strength = t, n !== this.seed && (this.seed = n, this._noise = new kr(n)), r && super.reset(r, i);
	}
	_potential(e, t, n, r) {
		let i = this._noise;
		return r.set(i.noise(e, t, n), i.noise(e + Ar.x, t + Ar.y, n + Ar.z), i.noise(e + jr.x, t + jr.y, n + jr.z)), r;
	}
	mutate(e, t, n) {
		this.energize(e, t, n);
		let r = this.scale, i = pr, a = e.position.x * r, o = e.position.y * r, s = e.position.z * r, c = this._potential(a + i, o, s, this._pxp), l = this._potential(a - i, o, s, this._pxm), u = this._potential(a, o + i, s, this._pyp), d = this._potential(a, o - i, s, this._pym), f = this._potential(a, o, s + i, this._pzp), p = this._potential(a, o, s - i, this._pzm), m = 1 / (2 * i);
		this._curl.set((u.z - d.z - (f.y - p.y)) * m, (f.x - p.x - (c.z - l.z)) * m, (c.y - l.y - (u.x - d.x)) * m), e.velocity.addScaledVector(this._curl, this.strength * t);
	}
	static fromJSON(t) {
		let { scale: n, strength: r, seed: i, life: a, easing: o, isEnabled: s = !0 } = t;
		return new e(n, r, i, a, w(o), s);
	}
}, Nr = {
	Position: Nn,
	Rotation: Pn,
	Life: pn,
	Radius: Fn,
	Mass: mn,
	Body: cn,
	BodySprite: un,
	Texture: In,
	PolarVelocity: Bn,
	RadialVelocity: Vn,
	VectorVelocity: Hn
}, Pr = {
	Alpha: hr,
	Attraction: gr,
	Color: vr,
	CrossZone: yr,
	Force: br,
	Gravity: xr,
	RandomDrift: Sr,
	Repulsion: Cr,
	Rotate: wr,
	Scale: Tr,
	Spring: Er,
	Vortex: Dr,
	CurlNoise: Mr
}, Fr = (e, t, n) => Nr[e].fromJSON(t, n), Ir = (e, t) => Pr[e].fromJSON(t), Lr = (e) => U.fromJSON(e), Rr = (e, t) => {
	let n = [];
	return e.forEach((e) => {
		let { type: r, properties: i } = e;
		if (!T(bt, r)) throw Error(`The initializer type ${r} is invalid or not yet supported`);
		we.includes(r) ? n.push(Fr(r, i, t)) : n.push(Fr(r, i));
	}), n;
}, zr = (e) => {
	let t = [];
	return e.forEach((e) => {
		let { type: n, properties: r } = e;
		if (!T(xt, n)) throw Error(`The behaviour type ${n} is invalid or not yet supported`);
		t.push(Ir(n, r));
	}), t;
}, Br = (e, t, n) => {
	let r = new n(), { rate: i, rotation: a, initializers: o, behaviours: s, emitterBehaviours: c = [], position: l, totalEmitTimes: u = Infinity, life: d = Infinity, damping: f = Un, children: p = [], inherit: m, orphanPolicy: h, trigger: g } = e;
	return r.damping = f, r.setRate(Lr(i)).setRotation(a).setInitializers(Rr(o, t)).setBehaviours(zr(s)).setEmitterBehaviours(zr(c)).setPosition(l).emit(u, d), m && (r.inherit = {
		...r.inherit,
		...m
	}), h && (r.orphanPolicy = h), g && (r.trigger = g), p.forEach((e) => r.addChild(Br(e, t, n))), r;
}, Vr = (e, t, n, r) => {
	let { preParticles: i = 500, integrationType: a = We, emitters: o = [] } = e, s = new n(i, a);
	return o.forEach((e) => s.addEmitter(Br(e, t, r))), s;
}, Hr = { shouldAutoEmit: !0 }, Ur = (e) => U.fromJSON(e), Wr = (e, t) => new Promise((n, r) => {
	if (!e.length) return n([]);
	let i = e.length, a = Array(i), o = 0, s = (e, t) => {
		if (a[e] = t, o += 1, o === i) return n(a);
	};
	e.forEach((e, n) => {
		let { type: i, properties: a } = e;
		if (!T(bt, i)) return r(`The initializer type ${i} is invalid or not yet supported`);
		if (a.texture) {
			new t.TextureLoader().load(a.texture, (e) => s(n, In.fromJSON({
				...a,
				loadedTexture: e
			}, t)), void 0, r);
			return;
		}
		s(n, we.includes(i) ? Fr(i, a, t) : Fr(i, a));
	});
}), Gr = (e) => new Promise((t, n) => {
	if (!e.length) return t([]);
	let r = e.length, i = [];
	e.forEach((e) => {
		let { type: a, properties: o } = e;
		if (!T(xt, a)) return n(`The behaviour type ${a} is invalid or not yet supported`);
		if (i.push(Ir(a, o)), i.length === r) return t(i);
	});
}), Kr = (e, t, n, r) => {
	let i = new t(), { rate: a, rotation: o, initializers: s, behaviours: c, emitterBehaviours: l = [], position: u, totalEmitTimes: d = Infinity, life: f = Infinity, damping: p = Un, children: m = [], inherit: h, orphanPolicy: g, trigger: ee } = e;
	return i.damping = p, i.setRate(Ur(a)).setRotation(o).setPosition(u), h && (i.inherit = {
		...i.inherit,
		...h
	}), g && (i.orphanPolicy = g), ee && (i.trigger = ee), Wr(s, n).then((e) => (i.setInitializers(e), Gr(c))).then((e) => (i.setBehaviours(e), Gr(l))).then((e) => (i.setEmitterBehaviours(e), Promise.all(m.map((e) => Kr(e, t, n, r))))).then((e) => (e.forEach((e) => i.addChild(e)), r ? i.emit(d, f) : i.setTotalEmitTimes(d).setLife(f)));
}, qr = (e, t, n, r) => Promise.all(e.map((e) => Kr(e, t, n, r))), Jr = (e, t, n, r, i = {}) => new Promise((a, o) => {
	let { preParticles: s = 500, integrationType: c = We, emitters: l = [] } = e, u = new n(s, c), { shouldAutoEmit: d } = {
		...Hr,
		...i
	};
	qr(l, r, t, d).then((e) => {
		let t = e.length;
		if (!t) return a(u);
		e.forEach((e) => {
			u.addEmitter(e), u.emitters.length === t && a(u);
		});
	}).catch(o);
}), Yr = class e {
	constructor(e = 500, t = F, n = Zn()) {
		this.type = Yt, this.canUpdate = !0, this.preParticles = e, this.integrationType = t, this.emitters = [], this.renderers = [], this.pool = new L(), this.eventDispatcher = new sn(), this.seed = n, this.fixedTimeStep = vt, this.maxSubSteps = 6, this._accumulator = 0, this.maxEmitterInstances = yt, this._liveEmitterInstances = 0, this._emitterPoolHits = 0, this._emitterPoolMisses = 0, this._warnedInstanceOverflow = !1, this.maxEmitterDepth = 4, this._detached = [];
	}
	spawnEmitterInstance(e, t) {
		if (this._liveEmitterInstances >= this.maxEmitterInstances) return this._warnedInstanceOverflow || (this._warnedInstanceOverflow = !0, console.warn(`three-nebula: maxEmitterInstances (${this.maxEmitterInstances}) reached; dropping newest child emitter instances. Raise System.maxEmitterInstances if intended.`)), null;
		let n = e._freeInstances.length > 0, r = e.acquireInstance(t);
		return r.parent = this, n ? this._emitterPoolHits++ : this._emitterPoolMisses++, this._liveEmitterInstances++, r;
	}
	releaseEmitterInstance(e) {
		e._template.releaseInstance(e), this._liveEmitterInstances--;
	}
	_detachInstance(e, t = !0) {
		t && (e.isEmitting = !1), e._parentParticle = null, this._detached.push(e);
	}
	_killInstance(e) {
		e.isEmitting = !1, e.activeChildren.size && (e.activeChildren.forEach((e) => {
			for (let t = 0; t < e.length; t++) this._killInstance(e[t]);
		}), e.activeChildren.clear());
		let t = e.particles.length;
		for (; t--;) {
			let n = e.particles[t];
			this.dispatch(tn, n), this.pool.expire(n.reset());
		}
		e.particles.length = 0, this.releaseEmitterInstance(e);
	}
	_updateDetached(e) {
		if (!this._detached.length) return;
		let t = !1, n = this._detached.length;
		for (; n--;) {
			let r = this._detached[n];
			r.update(e), r.particles.length && (t = !0), r.particles.length === 0 && r.activeChildren.size === 0 && (this._detached.splice(n, 1), this.releaseEmitterInstance(r));
		}
		t && this.dispatch(Qt);
	}
	setSeed(e) {
		return this.seed = e, this.emitters.forEach((t, n) => t.reseed(e, n)), this;
	}
	static fromJSON(t, n) {
		return Vr(t, n, e, lr);
	}
	static fromJSONAsync(t, n, r) {
		return Jr(t, n, e, lr, r);
	}
	dispatch(e, t = this) {
		this.eventDispatcher.dispatchEvent(e, t);
	}
	addRenderer(e) {
		return this.renderers.push(e), e.init(this), this;
	}
	removeRenderer(e) {
		return this.renderers.splice(this.renderers.indexOf(e), 1), e.remove(this), this;
	}
	addEmitter(e) {
		let t = this.emitters.length;
		return e.parent = this, e.index = t, e.reseed(this.seed, t), e._assignNodeIds(`${t}`, 0, this.maxEmitterDepth), this.emitters.push(e), this.dispatch(nn, e), this;
	}
	removeEmitter(e) {
		return e.parent === this ? (e.parent = null, e.index = void 0, this.emitters.splice(this.emitters.indexOf(e), 1), this.dispatch(rn, e), this) : this;
	}
	emit({ onStart: e, onUpdate: t, onEnd: n }) {
		e && e(), t && this.eventDispatcher.addEventListener(Qt, t);
		let r = this.emitters.map((e) => {
			let { life: t } = e;
			return t === Infinity ? (n && n(), e.experimental_emit(), Promise.resolve()) : new Promise((t) => {
				e.addOnEmitterDeadEventListener(() => {
					n && n(), t();
				}), e.experimental_emit();
			});
		});
		try {
			return Promise.all(r);
		} catch (e) {
			console.warn(e);
		}
	}
	update(e = vt) {
		let t = e || .0167;
		if (this.canUpdate) {
			if (t > 0) {
				let e = this.emitters.length;
				for (; e--;) {
					let n = this.emitters[e];
					n.update(t), n.particles.length && this.dispatch("SYSTEM_UPDATE");
				}
				this._updateDetached(t);
			}
			this.dispatch(on);
		}
		return Promise.resolve();
	}
	tick(e) {
		let { fixedTimeStep: t, maxSubSteps: n } = this, r = [];
		this._accumulator += e;
		let i = 0;
		for (; this._accumulator >= t && i < n;) r.push(this.update(t)), this._accumulator -= t, i++;
		return i === n && this._accumulator >= t && (this._accumulator = 0), Promise.all(r).then(() => void 0);
	}
	getCount() {
		let e = this.emitters.length, t = 0, n;
		for (n = 0; n < e; n++) t += this.emitters[n].particles.length;
		return t;
	}
	destroy() {
		let e = this.emitters.length;
		this.canUpdate = !1;
		for (let t = 0; t < e; t++) this.emitters[t] && this.emitters[t].destroy(), delete this.emitters[t];
		for (let t = 0; t < e; t++) this.renderers[t] && this.renderers[t].destroy && (this.renderers[t].destroy(), delete this.renderers[t]);
		this.emitters.length = 0, this.pool.destroy(), this.canUpdate = !0;
	}
}, Xr = {
	addEventListener: function(e, t) {
		return e.eventDispatcher.addEventListener("SYSTEM_UPDATE", t), this;
	},
	drawZone: function(e, t, n, r = {}) {
		let { width: i = 15, height: a = 15, depth: o = 15, radius: s = 15, x: c = 0, y: l = 0, z: u = 0 } = r, { innerRadius: d = 0, outerRadius: f = s } = r, p;
		r.isPointZone() && (p = new e.SphereGeometry(15)), r.isLineZone(), r.isBoxZone() && (p = new e.BoxGeometry(i, a, o)), r.isSphereZone() && (p = new e.SphereGeometry(s, 15, 15)), r.isRingZone() && (p = new e.RingGeometry(d, f, 32), p.rotateX(Math.PI / 2)), r.isCylinderZone() && (p = new e.CylinderGeometry(s, s, a, 24, 1, !0)), r.isConeZone() && (p = new e.ConeGeometry(s, a, 24, 1, !0)), r.isMeshZone() && (p = r.geometry.geometry ? r.geometry.geometry.clone() : r.geometry.clone()), p || (p = new e.BoxGeometry(i, a, o));
		let m = new e.MeshBasicMaterial({
			color: "#2194ce",
			wireframe: !0
		}), h = new e.Mesh(p.clone(), m);
		n.add(h), this.addEventListener(t, function() {
			h.position.set(c, l, u);
		});
	},
	drawEmitter: function(e, t, n, r, i) {
		let a = new e.OctahedronGeometry(15), o = new e.MeshBasicMaterial({
			color: i || "#aaa",
			wireframe: !0
		}), s = new e.Mesh(a.clone(), o);
		n.add(s), this.addEventListener(t, function() {
			s.position.copy(r.position), s.rotation.set(r.rotation.x, r.rotation.y, r.rotation.z);
		});
	},
	renderInfo: (function() {
		function e(e, t) {
			var n = e == "material" ? "_materialPool" : "_targetPool";
			return t.renderers[0][n].cID;
		}
		function t(e) {
			var t = e.emitters[0];
			return Math.round(t.p.x) + "," + Math.round(t.p.y) + "," + Math.round(t.p.z);
		}
		return function(n, r) {
			this.addInfo(r);
			var i = "";
			switch (this._infoType) {
				case 2:
					i += "emitter:" + n.emitters.length + "<br>", i += "em speed:" + n.emitters[0].cID + "<br>", i += "pos:" + t(n);
					break;
				case 3:
					i += n.renderers[0].name + "<br>", i += "target:" + e("target") + "<br>", i += "material:" + e("material");
					break;
				default: i += "particles:" + n.getCount() + "<br>", i += "pool:" + n.pool.getCount() + "<br>", i += "total:" + (n.getCount() + n.pool.getCount());
			}
			this._infoCon.innerHTML = i;
		};
	})(),
	addInfo: (function() {
		return function(e) {
			var t = this;
			if (!this._infoCon) {
				this._infoCon = document.createElement("div"), this._infoCon.style.cssText = [
					"position:fixed;bottom:0px;left:0;cursor:pointer;",
					"opacity:0.9;z-index:10000;padding:10px;font-size:12px;",
					"width:120px;height:50px;background-color:#002;color:#0ff;"
				].join(""), this._infoType = 1, this._infoCon.addEventListener("click", function() {
					t._infoType++, t._infoType > 3 && (t._infoType = 1);
				}, !1);
				var n, r;
				switch (e) {
					case 2:
						n = "#201", r = "#f08";
						break;
					case 3:
						n = "#020", r = "#0f0";
						break;
					default: n = "#002", r = "#0ff";
				}
				this._infoCon.style.backgroundColor = n, this._infoCon.style.color = r;
			}
			this._infoCon.parentNode || document.body.appendChild(this._infoCon);
		};
	})()
};
//#endregion
//#region src/debug/log.ts
function Zr() {
	let e = 0;
	if (window.console && typeof window.console.trace == "function") {
		var t = Array.prototype.slice.call(arguments);
		if ((arguments[0] + "").indexOf("+") == 0) {
			var n = parseInt(arguments[0]);
			e < n && (t.shift(), console.trace.apply(console, t), e++);
		} else t.unshift("+15"), this.apply(console, t);
	}
}
//#endregion
//#region src/emitter/FollowEmitter.ts
var Qr = class extends lr {
	constructor(e, t, n) {
		super(n), this.type = or, this.mouseTarget = D.initValue(e, window), this.ease = D.initValue(t, .7), this._allowEmitting = !1, this.initEventHandler();
	}
	initEventHandler() {
		var e = this;
		this.mousemoveHandler = function(t) {
			e.mousemove.call(e, t);
		}, this.mouseTarget.addEventListener("mousemove", this.mousemoveHandler, !1);
	}
	emit() {
		return this._allowEmitting = !0, this;
	}
	stopEmit() {
		this._allowEmitting = !1;
	}
	setCameraAndCanvas(e, t) {
		this.camera = e, this.canvas = t;
	}
	mousemove(e) {
		let t = e;
		t.layerX || t.layerX == 0 ? (this.position.x += (t.layerX - this.position.x) * this.ease, this.position.y += (t.layerY - this.position.y) * this.ease) : (e.offsetX || e.offsetX == 0) && (this.position.x += (e.offsetX - this.position.x) * this.ease, this.position.y += (e.offsetY - this.position.y) * this.ease), this.position.copy(E.toSpacePos(this.position, this.camera, this.canvas)), this._allowEmitting && super.emit("once");
	}
	destroy() {
		super.destroy(), this.mouseTarget.removeEventListener("mousemove", this.mousemoveHandler, !1);
	}
}, Z = class {
	constructor(e = Ie) {
		this.type = e;
	}
	init(e) {
		var t = this;
		this.system = e, this.system.eventDispatcher.addEventListener(Qt, function(e) {
			t.onSystemUpdate.call(t, e);
		}), this.system.eventDispatcher.addEventListener($t, function(e) {
			t.onParticleCreated.call(t, e);
		}), this.system.eventDispatcher.addEventListener(en, function(e) {
			t.onParticleUpdate.call(t, e);
		}), this.system.eventDispatcher.addEventListener(tn, function(e) {
			t.onParticleDead.call(t, e);
		});
	}
	remove(e) {
		this.system = null;
	}
	onParticleCreated(e) {}
	onParticleUpdate(e) {}
	onParticleDead(e) {}
	onSystemUpdate(e) {}
}, $r = class extends Z {
	constructor() {
		super(Le), this.targetPool = new L(), this.materialPool = new L();
	}
	onSystemUpdate() {}
	onParticleCreated(e) {}
	onParticleUpdate(e) {}
	onParticleDead(e) {}
}, ei = class extends Z {
	constructor(e, t) {
		super(ze), this.container = e, this._targetPool = new L(), this._materialPool = new L(), this._body = new t.Mesh(new t.BoxGeometry(50, 50, 50), new t.MeshLambertMaterial({ color: "#ff0000" }));
	}
	isThreeSprite(e) {
		return !!e.target.isSprite;
	}
	onSystemUpdate() {}
	onParticleCreated(e) {
		if (!e.target && (e.body || (e.body = this._body), e.target = this._targetPool.get(e.body), e.useAlpha || e.useColor)) {
			let t = e.target;
			t.material.__puid = wt.id(e.body.material), t.material = this._materialPool.get(t.material);
		}
		if (e.target) {
			let t = e.target;
			t.position.copy(e.position), this.container.add(t);
		}
	}
	onParticleUpdate(e) {
		let { useAlpha: t, useColor: n } = e, r = e.target;
		r && (r.position.copy(e.position), this.rotate(e), this.scale(e), t && (r.material.opacity = e.alpha, r.material.transparent = !0), n && r.material.color.copy(e.color));
	}
	rotate(e) {
		e.target.rotation.set(e.rotation.x, e.rotation.y, e.rotation.z);
	}
	scale(e) {
		e.target.scale.set(e.scale, e.scale, e.scale);
	}
	onParticleDead(e) {
		if (e.target) {
			let t = e.target;
			(e.useAlpha || e.useColor) && this._materialPool.expire(t.material), this._targetPool.expire(t), this.container.remove(t), e.target = null;
		}
	}
}, ti = {
	width: 20,
	blending: "AdditiveBlending",
	uv: "stretch",
	softEdge: !0,
	smoothing: 2,
	depthTest: !0,
	depthWrite: !1
}, ni = (e, t) => e.spawnIndex - t.spawnIndex, ri = (e) => {
	let t = [];
	for (let n = 0; n < e - 1; n++) {
		let e = 2 * n, r = 2 * n + 1, i = 2 * n + 2, a = 2 * n + 3;
		t.push(e, i, r, r, i, a);
	}
	return t;
}, ii = class extends Z {
	constructor(e, t, n = {}) {
		super(Be), this.three = t, this.container = e, this.options = {
			...ti,
			...n
		}, this._groups = /* @__PURE__ */ new Map(), this._ribbons = /* @__PURE__ */ new Map(), this._camPos = new t.Vector3(), this._prev = new t.Vector3(), this._next = new t.Vector3(), this._tangent = new t.Vector3(), this._view = new t.Vector3(), this._side = new t.Vector3(), this._lastSide = new t.Vector3(1, 0, 0), this._up = new t.Vector3(0, 1, 0), this._softEdgeMap = this.options.softEdge ? this._makeSoftEdgeMap() : null, this._spine = [];
	}
	_dedupe(e) {
		let t = this._spine;
		t.length = 0;
		for (let n = 0; n < e.length; n++) {
			let r = e[n];
			if (t.length > 0) {
				let e = t[t.length - 1].position, n = r.position.x - e.x, i = r.position.y - e.y, a = r.position.z - e.z;
				if (n * n + i * i + a * a < .0625) continue;
			}
			t.push(r);
		}
		return t;
	}
	_makeSoftEdgeMap() {
		let e = /* @__PURE__ */ new Uint8Array(256);
		for (let t = 0; t < 64; t++) {
			let n = Math.round(Math.sin(t / 63 * Math.PI) * 255);
			e[t * 4] = n, e[t * 4 + 1] = n, e[t * 4 + 2] = n, e[t * 4 + 3] = 255;
		}
		let t = new this.three.DataTexture(e, 1, 64);
		return t.needsUpdate = !0, t;
	}
	_keyOf(e) {
		return e.emitterInstanceId || e.emitterId || "ribbon";
	}
	onParticleCreated(e) {
		let t = this._keyOf(e), n = this._groups.get(t);
		n ? n.push(e) : this._groups.set(t, [e]);
	}
	onParticleUpdate() {}
	onParticleDead(e) {
		let t = this._keyOf(e), n = this._groups.get(t);
		if (!n) return;
		let r = n.indexOf(e);
		r > -1 && n.splice(r, 1), n.length === 0 && (this._groups.delete(t), this._disposeRibbon(t));
	}
	onSystemUpdate() {
		this._groups.forEach((e, t) => this._rebuild(t, e));
	}
	_rebuild(e, t) {
		let n = this._ensureRibbon(e, t.length);
		if (t.length < 2) {
			n.mesh.visible = !1;
			return;
		}
		t.sort(ni);
		let r = this._dedupe(t);
		if (r.length < 2) {
			n.mesh.visible = !1;
			return;
		}
		n.mesh.visible = !0;
		let { width: i, uv: a, camera: o } = this.options, s = r.length, { positions: c, colors: l, uvs: u } = n;
		o && o.getWorldPosition(this._camPos);
		for (let e = 0; e < s; e++) {
			let t = r[e], n = t.position, d = Math.max(1, this.options.smoothing);
			this._prev.copy(r[Math.max(0, e - d)].position), this._next.copy(r[Math.min(s - 1, e + d)].position), this._tangent.subVectors(this._next, this._prev), o ? this._view.subVectors(this._camPos, n).normalize() : this._view.copy(this._up), this._side.crossVectors(this._tangent, this._view), this._side.lengthSq() < 1e-12 ? this._side.copy(this._lastSide) : (this._side.normalize(), e > 0 && this._side.dot(this._lastSide) < 0 && this._side.negate()), this._lastSide.copy(this._side);
			let f = .5 * i * t.scale, p = n.x + this._side.x * f, m = n.y + this._side.y * f, h = n.z + this._side.z * f, g = n.x - this._side.x * f, ee = n.y - this._side.y * f, te = n.z - this._side.z * f, _ = e * 6;
			c[_] = p, c[_ + 1] = m, c[_ + 2] = h, c[_ + 3] = g, c[_ + 4] = ee, c[_ + 5] = te;
			let { r: ne, g: re, b: v } = t.color, ie = t.alpha, y = e * 8;
			l[y] = ne, l[y + 1] = re, l[y + 2] = v, l[y + 3] = ie, l[y + 4] = ne, l[y + 5] = re, l[y + 6] = v, l[y + 7] = ie;
			let ae = a === "tile" ? e : e / (s - 1), b = e * 4;
			u[b] = ae, u[b + 1] = 1, u[b + 2] = ae, u[b + 3] = 0;
		}
		let { geometry: d } = n;
		d.attributes.position.array.set(c.subarray(0, s * 6)), d.attributes.color.array.set(l.subarray(0, s * 8)), d.attributes.uv.array.set(u.subarray(0, s * 4)), d.attributes.position.needsUpdate = !0, d.attributes.color.needsUpdate = !0, d.attributes.uv.needsUpdate = !0, d.setDrawRange(0, (s - 1) * 6);
	}
	_ensureRibbon(e, t) {
		let n = this.three, r = this._ribbons.get(e), i = Math.max(t, 2);
		if (r && r.capacity >= i) return r;
		let a = new Float32Array(i * 6), o = new Float32Array(i * 8), s = new Float32Array(i * 4), c = ri(i), l, u;
		if (r) l = r.geometry, u = r.mesh;
		else {
			l = new n.BufferGeometry();
			let { blending: e, texture: t, depthTest: r, depthWrite: i } = this.options, a = new n.MeshBasicMaterial({
				vertexColors: !0,
				transparent: !0,
				side: n.DoubleSide,
				blending: n[e],
				map: t || null,
				alphaMap: this._softEdgeMap,
				depthTest: r,
				depthWrite: i
			});
			u = new n.Mesh(l, a), u.frustumCulled = !1, this.container.add(u);
		}
		return l.setAttribute("position", new n.BufferAttribute(a, 3)), l.setAttribute("color", new n.BufferAttribute(o, 4)), l.setAttribute("uv", new n.BufferAttribute(s, 2)), l.setIndex(c), r = {
			mesh: u,
			geometry: l,
			positions: a,
			colors: o,
			uvs: s,
			capacity: i
		}, this._ribbons.set(e, r), r;
	}
	_disposeRibbon(e) {
		let t = this._ribbons.get(e);
		t && (this.container.remove(t.mesh), t.geometry.dispose(), t.mesh.material.dispose(), this._ribbons.delete(e));
	}
	onSystemUpdateAfter() {}
	remove(e) {
		this._ribbons.forEach((e, t) => this._disposeRibbon(t)), this._groups.clear(), this._softEdgeMap && (this._softEdgeMap.dispose(), this._softEdgeMap = null);
	}
	destroy() {
		this.remove();
	}
}, ai = class extends ei {
	constructor(e, t) {
		super(e, t), this.type = Re, this._body = new t.Sprite(new t.SpriteMaterial({ color: 16777215 }));
	}
	rotate(e) {
		let t = e.target;
		t.material.rotation = e.rotation.z;
	}
	scale(e) {
		e.target.scale.set(e.scale * e.radius, e.scale * e.radius, 1);
	}
}, oi = class {
	constructor(e) {
		this.position = new e.Vector3(), this.rotation = new e.Vector3(), this.size = 0, this.color = new e.Color(), this.alpha = 0, this.texture = null, this.index = 0;
	}
	reset() {
		this.position.set(0, 0, 0), this.rotation.set(0, 0, 0), this.size = 0, this.color.setRGB(0, 0, 0), this.alpha = 0, this.texture = null;
	}
}, si = class {
	constructor(e = Infinity) {
		this.max = e, this.count = 0, this._items = {}, this._freeSlots = [];
	}
	add(e) {
		this._items[e] === void 0 && (this._items[e] = this._freeSlots.length > 0 ? this._freeSlots.pop() : this.count++);
	}
	find(e) {
		return this._items[e];
	}
	remove(e) {
		let t = this._items[e];
		t !== void 0 && (delete this._items[e], this._freeSlots.push(t));
	}
	destroy() {
		this._items = {}, this._freeSlots = [], this.count = 0;
	}
}, ci = 1e4, li = [
	12,
	4,
	4,
	16
].reduce((e, t) => e + t), ui = {
	position: 3,
	rotation: 1,
	size: 1,
	color: 4,
	alpha: 1,
	texID: 2
};
[
	3,
	1,
	1,
	4,
	1,
	2
].reduce((e, t) => e + t);
//#endregion
//#region src/renderer/GPURenderer/common/ParticleBuffer/index.ts
var di, fi = class {
	constructor(e = ci, t) {
		di = t, this.maxParticles = e, this.createInterleavedBuffer().createBufferGeometry();
	}
	createInterleavedBuffer() {
		let e = new ArrayBuffer(this.maxParticles * li);
		return this.interleavedBuffer = new di.InterleavedBuffer(new Float32Array(e), li), this;
	}
	createBufferGeometry() {
		this.geometry = new di.BufferGeometry();
		let { interleavedBuffer: e, geometry: t } = this;
		return Object.keys(ui).reduce((n, r) => {
			let i = ui[r];
			return t.setAttribute(r, new di.InterleavedBufferAttribute(e, i, n)), n += i;
		}, 0), this;
	}
	get buffer() {
		return this.interleavedBuffer;
	}
	get stride() {
		return li;
	}
};
//#endregion
//#region node_modules/potpack/index.mjs
function pi(e) {
	let t = 0, n = 0;
	for (let r of e) t += r.w * r.h, n = Math.max(n, r.w);
	e.sort((e, t) => t.h - e.h);
	let r = [{
		x: 0,
		y: 0,
		w: Math.max(Math.ceil(Math.sqrt(t / .95)), n),
		h: Infinity
	}], i = 0, a = 0;
	for (let t of e) for (let e = r.length - 1; e >= 0; e--) {
		let n = r[e];
		if (!(t.w > n.w || t.h > n.h)) {
			if (t.x = n.x, t.y = n.y, a = Math.max(a, t.y + t.h), i = Math.max(i, t.x + t.w), t.w === n.w && t.h === n.h) {
				let t = r.pop();
				e < r.length && (r[e] = t);
			} else t.h === n.h ? (n.x += t.w, n.w -= t.w) : t.w === n.w ? (n.y += t.h, n.h -= t.h) : (r.push({
				x: n.x + t.w,
				y: n.y,
				w: n.w - t.w,
				h: t.h
			}), n.y += t.h, n.h -= t.h);
			break;
		}
	}
	return {
		w: i,
		h: a,
		fill: t / (i * a) || 0
	};
}
//#endregion
//#region src/renderer/GPURenderer/common/TextureAtlas/index.ts
var mi = class {
	constructor(e, t) {
		let { three: n, type: r } = e, i = new Float32Array(256 * 4), a = this.ctx = document.createElement("canvas").getContext("2d"), { canvas: o } = a;
		this.shouldDebug = t, this.rendererType = r, this.indexData = i, this.canvas = o, this.entries = [], this.three = n, this.material = e.material, r === "DesktopGPURenderer" && (this.atlasIndex = new n.DataTexture(i, 256, 1, n.RGBAFormat, n.FloatType)), o.width = o.height = 256, t && this.debug(o, a), this.atlasTexture = new n.CanvasTexture(o), this.atlasTexture.flipY = !1, e.material.uniforms.uTexture.value = this.atlasTexture, r === "DesktopGPURenderer" && (e.material.uniforms.atlasIndex.value = this.atlasIndex), e.material.uniformsNeedUpdate = !0;
	}
	log(...e) {
		Ge() && console.log(...e);
	}
	debug(e, t) {
		let { canvas: n, ctx: r } = this, i = n.width;
		r.fillStyle = "purple", r.fillRect(0, 0, i, i), r.fillStyle = "green", r.fillRect(0, i, i, i), r.fillStyle = "blue", r.fillRect(i, 0, i, i), r.fillStyle = "orange", r.fillRect(i, i, i, i), r.fillStyle = "yellow", r.font = n.width + "px Verdana", r.fillText("top row", 100, 500), r.fillStyle = "pink", r.fillText("bottom row", 100, 1500), n.style.position = "absolute", n.style.width = n.style.height = "300px", n.style.left = n.style.top = "0px", n.style.zIndex = "100", document.body.appendChild(n);
	}
	addTexture(e) {
		this.log("Adding texture to atlas:", e.uuid), e.textureIndex = this.entries.length, this.entries.push({ texture: e }), this.needsUpdate = !0;
	}
	update() {
		if (!this.needsUpdate) return;
		let { entries: e, canvas: t, indexData: n, ctx: r, atlasIndex: i, atlasTexture: a, rendererType: o } = this;
		for (let t = 0; t < e.length; t++) if (!e[t].texture.image) return;
		this.needsUpdate = !1;
		for (let t = 0; t < e.length; t++) {
			let n = e[t], { texture: r } = n, { width: i, height: a } = r.image;
			n.w = i, n.h = a;
		}
		let s = pi(e);
		this.log("Rebuilt atlas:", s), (t.width != s.w || t.height != s.h) && (t.width = s.w, t.height = s.h);
		for (let i = 0; i < e.length; i++) {
			let e = this.entries[i], a = e.texture.textureIndex * 4, s = e.x, c = e.y, l = e.w, u = e.h;
			o === "DesktopGPURenderer" && (n[a + 0] = s / t.width, n[a + 1] = c / t.height, n[a + 2] = (s + l) / t.width, n[a + 3] = (c + u) / t.height), o === "MobileGPURenderer" && (n[a + 0] = s / (t.width + 1), n[a + 1] = c / (t.height + 1), n[a + 2] = (s + l) / (t.width + 1), n[a + 3] = (c + u) / (t.height + 1)), r.drawImage(e.texture.image, s, c, l, u);
		}
		o === "DesktopGPURenderer" && (i.needsUpdate = !0), a.dispose();
		let c = new this.three.CanvasTexture(t);
		c.flipY = !1, this.atlasTexture = c, this.material.uniforms.uTexture.value = c, this.material.uniformsNeedUpdate = !0;
	}
	destroy() {
		let { atlasIndex: e, atlasTexture: t, canvas: n } = this;
		t.dispose(), e && e.dispose(), this.shouldDebug && n.remove(), this.entries = [];
	}
}, hi = () => "\n    uniform vec3 baseColor;\n    uniform sampler2D uTexture;\n    uniform sampler2D atlasIndex;\n\n    varying float vRotation;\n    varying vec3 targetColor;\n    varying float targetAlpha;\n    varying vec4 tileRect;\n    varying float tileID;\n\n    void main() {\n      gl_FragColor = vec4(baseColor * targetColor, targetAlpha);\n\n      vec2 uv = gl_PointCoord;\n      uv = mix(tileRect.xy, tileRect.zw, gl_PointCoord);\n\n      float mid = 0.5;\n      uv = vec2(\n        cos(vRotation) * (uv.x - mid) - sin(vRotation) * (uv.y - mid) + mid,\n        cos(vRotation) * (uv.y - mid) + sin(vRotation) * (uv.x - mid) + mid\n      );\n\n      gl_FragColor = gl_FragColor * texture2D(uTexture, uv);\n\n    }\n", gi = "600.0", _i = () => `
    uniform sampler2D uTexture;
    //atlasIndex is a 256x1 float texture of tile rectangles as r=minx g=miny b=maxx a=maxy
    uniform sampler2D atlasIndex;

    attribute float size;
    attribute vec3 color;
    attribute float alpha;
    attribute float texID;
    attribute float rotation;

    varying float vRotation;
    varying vec3 targetColor;
    varying float targetAlpha;
    varying vec4 tileRect;
    varying float tileID;

    void main() {
      vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
      targetColor = color;
      targetAlpha = alpha;
      vRotation = rotation;

      tileID = texID;
      //get the tile rectangle from the atlasIndex texture..
      tileRect = texture2D(atlasIndex, vec2((tileID + 0.5) / 256.0, 0.5));

      gl_PointSize = ((size * ${gi}) / -mvPosition.z);
      gl_Position = projectionMatrix * mvPosition;
    }
`, vi = {
	blending: "AdditiveBlending",
	baseColor: 16777215,
	depthTest: !0,
	depthWrite: !1,
	transparent: !0,
	maxParticles: ci,
	shouldDebugTextureAtlas: !1,
	shouldForceDesktopRenderer: !1,
	shouldForceMobileRenderer: !1
}, Q, yi = class extends Z {
	constructor(e, t, n = {}) {
		super(Ue), Q = this.three = t;
		let { camera: r, maxParticles: i, baseColor: a, blending: o, depthTest: s, depthWrite: c, transparent: l, shouldDebugTextureAtlas: u } = {
			...vi,
			...n
		}, d = new fi(i, Q), f = new Q.ShaderMaterial({
			uniforms: {
				baseColor: { value: new Q.Color(a) },
				uTexture: { value: null },
				atlasIndex: { value: null }
			},
			vertexShader: _i(),
			fragmentShader: hi(),
			blending: Q[o],
			depthTest: s,
			depthWrite: c,
			transparent: l
		});
		this.container = e, this.camera = r, this.targetPool = new L(), this.uniqueList = new si(i), this.particleBuffer = d, this.buffer = d.buffer, this.stride = d.stride, this.geometry = d.geometry, this.material = f, this.points = new Q.Points(this.geometry, this.material), this.points.frustumCulled = !1, this.shouldDebugTextureAtlas = u, this.container.add(this.points);
	}
	onSystemUpdate(e) {
		super.onSystemUpdate(e), this.buffer.needsUpdate = !0, this.textureAtlas && this.textureAtlas.update();
	}
	onParticleCreated(e) {
		e.target || (e.target = this.targetPool.get(oi, Q), this.uniqueList.add(e.id)), this.updateTarget(e).mapParticleTargetPropsToPoint(e);
	}
	onParticleUpdate(e) {
		e.target && this.updateTarget(e).mapParticleTargetPropsToPoint(e);
	}
	onParticleDead(e) {
		e.target && (e.target.reset(), this.mapParticleTargetPropsToPoint(e), this.uniqueList.remove(e.id), e.target = null);
	}
	updateTarget(e) {
		let { position: t, rotation: n, scale: r, radius: i, color: a, alpha: o, body: s, id: c } = e, { r: l, g: u, b: d } = a, f = e.target;
		if (f.position.copy(t), f.rotation.copy(n), f.size = r * i, f.color.setRGB(l, u, d), f.alpha = o, f.index = this.uniqueList.find(c), s && s instanceof Q.Sprite) {
			let { map: e } = s.material;
			f.texture = e, f.textureIndex = this.getTextureID(e, this.shouldDebugTextureAtlas);
		}
		return this;
	}
	mapParticleTargetPropsToPoint(e) {
		return this.updatePointPosition(e).updatePointSize(e).updatePointRotation(e).updatePointColor(e).updatePointAlpha(e).updatePointTextureIndex(e), this;
	}
	updatePointPosition(e) {
		let { geometry: t, stride: n, buffer: r } = this, i = e.target, { offset: a } = t.attributes.position;
		return r.array[i.index * n + a + 0] = i.position.x, r.array[i.index * n + a + 1] = i.position.y, r.array[i.index * n + a + 2] = i.position.z, this;
	}
	updatePointSize(e) {
		let { geometry: t, stride: n, buffer: r } = this, i = e.target, { offset: a } = t.attributes.size;
		return r.array[i.index * n + a + 0] = i.size, this;
	}
	updatePointRotation(e) {
		let { geometry: t, stride: n, buffer: r } = this, i = e.target, { offset: a } = t.attributes.rotation;
		return r.array[i.index * n + a + 0] = i.rotation.z, this;
	}
	updatePointColor(e) {
		let { geometry: t, stride: n, buffer: r } = this, i = e.target, { offset: a } = t.attributes.color;
		return r.array[i.index * n + a + 0] = i.color.r, r.array[i.index * n + a + 1] = i.color.g, r.array[i.index * n + a + 2] = i.color.b, this;
	}
	updatePointAlpha(e) {
		let { geometry: t, stride: n, buffer: r } = this, i = e.target, { offset: a } = t.attributes.alpha;
		return r.array[i.index * n + a + 0] = i.alpha, this;
	}
	updatePointTextureIndex(e) {
		let { geometry: t, stride: n, buffer: r } = this, i = e.target, { offset: a } = t.attributes.texID;
		return r.array[i.index * n + a + 0] = i.textureIndex, this;
	}
	getTextureID(e, t) {
		return e.textureIndex === void 0 && (this.textureAtlas || (this.textureAtlas = new mi(this, t)), this.textureAtlas.addTexture(e)), e.textureIndex;
	}
	destroy() {
		let { container: e, points: t, textureAtlas: n, uniqueList: r } = this;
		e.remove(t), r.destroy(), n && n.destroy();
	}
}, bi = () => "\n    uniform vec3 baseColor;\n    uniform sampler2D uTexture;\n\n    varying float vRotation;\n    varying vec3 targetColor;\n    varying float targetAlpha;\n    varying vec4 tileRect;\n\n    void main() {\n      gl_FragColor = vec4(baseColor * targetColor, targetAlpha);\n\n      vec2 uv = gl_PointCoord;\n      uv = mix(tileRect.xy, tileRect.zw, gl_PointCoord);\n\n      float mid = 0.5;\n      uv = vec2(\n        cos(vRotation) * (uv.x - mid) - sin(vRotation) * (uv.y - mid) + mid,\n        cos(vRotation) * (uv.y - mid) + sin(vRotation) * (uv.x - mid) + mid\n      );\n      \n      gl_FragColor = gl_FragColor * texture2D(uTexture, uv);\n    }\n", xi = () => `
    uniform sampler2D uTexture;
    uniform vec2 atlasDim;

    attribute float size;
    attribute vec3 color;
    attribute float alpha;
    attribute vec2 texID;
    attribute float rotation;

    varying float vRotation;
    varying vec3 targetColor;
    varying float targetAlpha;
    varying vec4 tileRect;

    void main() {
      vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
      targetColor = color;
      targetAlpha = alpha;
      vRotation = rotation;

      vec2 tmin = floor(texID) / atlasDim;
      vec2 tmax = fract(texID);
      tileRect = vec4(tmin,tmax);

      gl_PointSize = ((size * ${gi}) / -mvPosition.z);
      gl_Position = projectionMatrix * mvPosition;
    }
`, $, Si = class extends Z {
	constructor(e, t, n = {}) {
		super(He), $ = this.three = t;
		let { camera: r, maxParticles: i, baseColor: a, blending: o, depthTest: s, depthWrite: c, transparent: l, shouldDebugTextureAtlas: u } = {
			...vi,
			...n
		}, d = new fi(i, $), f = new $.ShaderMaterial({
			uniforms: {
				baseColor: { value: new $.Color(a) },
				uTexture: { value: null },
				FFatlasIndex: { value: null },
				atlasDim: { value: new $.Vector2() }
			},
			vertexShader: xi(),
			fragmentShader: bi(),
			blending: $[o],
			depthTest: s,
			depthWrite: c,
			transparent: l
		});
		this.container = e, this.camera = r, this.targetPool = new L(), this.uniqueList = new si(i), this.particleBuffer = d, this.buffer = d.buffer, this.stride = d.stride, this.geometry = d.geometry, this.material = f, this.points = new $.Points(this.geometry, this.material), this.points.frustumCulled = !1, this.shouldDebugTextureAtlas = u, this.container.add(this.points);
	}
	onSystemUpdate(e) {
		super.onSystemUpdate(e), this.buffer.needsUpdate = !0;
		let { textureAtlas: t } = this;
		t && (t.update(), this.material.uniforms.atlasDim.value.set(t.atlasTexture.image.width, t.atlasTexture.image.height));
	}
	onParticleCreated(e) {
		e.target || (e.target = this.targetPool.get(oi, $), this.uniqueList.add(e.id)), this.updateTarget(e).mapParticleTargetPropsToPoint(e);
	}
	onParticleUpdate(e) {
		e.target && this.updateTarget(e).mapParticleTargetPropsToPoint(e);
	}
	onParticleDead(e) {
		e.target && (e.target.reset(), this.mapParticleTargetPropsToPoint(e), this.uniqueList.remove(e.id), e.target = null);
	}
	updateTarget(e) {
		let { position: t, rotation: n, scale: r, radius: i, color: a, alpha: o, body: s, id: c } = e, { r: l, g: u, b: d } = a, f = e.target;
		if (f.position.copy(t), f.rotation.copy(n), f.size = r * i, f.color.setRGB(l, u, d), f.alpha = o, f.index = this.uniqueList.find(c), s && s instanceof $.Sprite) {
			let { map: e } = s.material;
			f.texture = e, f.textureIndex = this.getTextureID(e, this.shouldDebugTextureAtlas);
		}
		return this;
	}
	mapParticleTargetPropsToPoint(e) {
		return this.updatePointPosition(e).updatePointSize(e).updatePointRotation(e).updatePointColor(e).updatePointAlpha(e).updatePointTextureIndex(e), this;
	}
	updatePointPosition(e) {
		let { geometry: t, stride: n, buffer: r } = this, i = e.target, { offset: a } = t.attributes.position;
		return r.array[i.index * n + a + 0] = i.position.x, r.array[i.index * n + a + 1] = i.position.y, r.array[i.index * n + a + 2] = i.position.z, this;
	}
	updatePointSize(e) {
		let { geometry: t, stride: n, buffer: r } = this, i = e.target, { offset: a } = t.attributes.size;
		return r.array[i.index * n + a + 0] = i.size, this;
	}
	updatePointRotation(e) {
		let { geometry: t, stride: n, buffer: r } = this, i = e.target, { offset: a } = t.attributes.rotation;
		return r.array[i.index * n + a + 0] = i.rotation.z, this;
	}
	updatePointColor(e) {
		let { geometry: t, stride: n, buffer: r } = this, i = e.target, { offset: a } = t.attributes.color;
		return r.array[i.index * n + a + 0] = i.color.r, r.array[i.index * n + a + 1] = i.color.g, r.array[i.index * n + a + 2] = i.color.b, this;
	}
	updatePointAlpha(e) {
		let { geometry: t, stride: n, buffer: r } = this, i = e.target, { offset: a } = t.attributes.alpha;
		return r.array[i.index * n + a + 0] = i.alpha, this;
	}
	updatePointTextureIndex(e) {
		let { geometry: t, stride: n, buffer: r } = this, i = e.target, { offset: a } = t.attributes.texID, o = i.index * n + a + 0;
		{
			let e = i.textureIndex * 4, t = this.textureAtlas, n = t.indexData, a = n[e++], s = n[e++], c = n[e++], l = n[e++];
			r.array[o] = (a * t.atlasTexture.image.width | 0) + c, r.array[o + 1] = (s * t.atlasTexture.image.height | 0) + l;
		}
		return this;
	}
	getTextureID(e, t) {
		return e.textureIndex === void 0 && (this.textureAtlas || (this.textureAtlas = new mi(this, t)), this.textureAtlas.addTexture(e)), e.textureIndex;
	}
	destroy() {
		let { container: e, points: t, textureAtlas: n, uniqueList: r } = this;
		e.remove(t), r.destroy(), n && n.destroy();
	}
}, Ci = class extends Z {
	constructor(e, t, n = {}) {
		super(Ve);
		let { shouldForceDesktopRenderer: r, shouldForceMobileRenderer: i } = n, a = [
			e,
			t,
			n
		];
		return r ? new yi(...a) : i || !wi() ? new Si(...a) : new yi(...a);
	}
}, wi = () => {
	let e = document.createElement("canvas");
	if (window.WebGL2RenderingContext && e.getContext("webgl2")) return !0;
	let t = !!e.getContext("webgl").getExtension("OES_texture_float");
	return e.remove(), t;
}, Ti = Ci, Ei = Yr;
//#endregion
export { hr as Alpha, It as ArraySpan, gr as Attraction, J as Behaviour, cn as Body, un as BodySprite, Bt as Box, hn as BoxZone, _r as Collision, vr as Color, Rt as ColorSpan, Ct as ColorUtil, On as ConeZone, yr as CrossZone, Mr as CurlNoise, $r as CustomRenderer, An as CylinderZone, Xr as Debug, En as DiscZone, lr as Emitter, Qr as FollowEmitter, br as Force, Ti as GPURenderer, xr as Gravity, F as INTEGRATION_TYPE_EULER, Vt as INTEGRATION_TYPE_RK2, Ht as INTEGRATION_TYPE_RK4, Ut as INTEGRATION_TYPE_VERLET, fn as InitializerUtil, pn as Life, gn as LineZone, mn as Mass, M as MathUtils, ei as MeshRenderer, _n as MeshZone, wt as PUID, Xt as Particle, vn as PointZone, Kt as Polar3D, Bn as PolarVelocity, L as Pool, Nn as Position, Vn as RadialVelocity, Fn as Radius, Sr as RandomDrift, U as Rate, Cr as Repulsion, ii as RibbonRenderer, Tn as RingZone, wr as Rotate, Pn as Rotation, Tr as Scale, bn as ScreenZone, N as Span, Cn as SphereZone, Er as Spring, ai as SpriteRenderer, Yr as System, E as THREEUtil, In as Texture, D as Util, I as Vector3D, Hn as VectorVelocity, Dr as Vortex, Lt as createArraySpan, zt as createColorSpan, P as createSpan, Ei as default, C as ease, dt as easeInBack, ct as easeInCirc, Xe as easeInCubic, at as easeInExpo, pt as easeInOutBack, ut as easeInOutCirc, Qe as easeInOutCubic, st as easeInOutExpo, Ye as easeInOutQuad, tt as easeInOutQuart, it as easeInOutSine, qe as easeInQuad, $e as easeInQuart, nt as easeInSine, Ke as easeLinear, ft as easeOutBack, lt as easeOutCirc, Ze as easeOutCubic, ot as easeOutExpo, Je as easeOutQuad, et as easeOutQuart, rt as easeOutSine, w as getEasingByName, Gt as integrate, Zr as log, ht as setEasingByName, A as uid, j as withDefaults };

//# sourceMappingURL=three-nebula.mjs.map