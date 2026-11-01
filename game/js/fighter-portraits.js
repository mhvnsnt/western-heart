/**
 * fighter-portraits.js — deterministic SVG street-art portraits for the
 * Western Heart character select screen.
 *
 * Ported (vanilla JS, no React) from the owner's AshLane-prototype
 * `src/game3d/fighter-portraits.tsx` — the owner's own procedural portrait
 * generator. Same fighter id ALWAYS generates the same portrait.
 * Style: bold geometric street-art / wheatpaste poster look.
 *
 * Provenance: mhvnsnt/AshLane-prototype, owner's own code (2026).
 * Wired per the INTEGRATION LAW as the select screen's procedural portrait
 * layer — placeholder/personality portraits until the portrait-pose pipeline
 * produces real renders. Not a parallel system: it feeds the existing
 * select-screen portrait slots.
 *
 * A portrait the player took in the Creation Suite (POSE & PICTURE) lives
 * on-device in game/js/user-portraits.js and wins over this procedural
 * layer in renderPortrait — the suite picture is the real card.
 */
import { getPortrait } from './user-portraits.js';

var SKIN_TONES = ["#f5d0b0", "#e8b88a", "#c98e5e", "#a06a3c", "#7a4e28", "#5a3820", "#3e2616"];
var HAIR_COLORS = ["#1a1a1a", "#2e2018", "#4a3220", "#6e4a28", "#8a6a3a", "#b8b8b8", "#e8e8e8", "#a83215", "#1f2a44"];
var ACCENT = ["#e4572e", "#f0b429", "#cc3300", "#7fb3d5", "#b04df0", "#4d9de0"];

var BG_COLORS = {
    ashes: "#2a1a12",
    combine: "#141e30",
    hollows: "#1a1214",
    unaffiliated: "#1e1c14",
    painted: "#1e1226",
    authority: "#101c2c"
};

/* FNV-1a string hash — deterministic per fighter id */
function hashStr(s) {
    var h = 2166136261;
    for (var i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
}

/* Seeded PRNG */
function mulberry32(seed) {
    var a = seed >>> 0;
    return function () {
      a |= 0;
      a = (a + 0x6d2b79f5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
}

function pick(rng, arr) {
    return arr[Math.floor(rng() * arr.length)];
}

/**
   * Build the portrait SVG markup for a fighter.
   * @param {string} fighterId  stable id — same id = same portrait, always
   * @param {string} name       accessible label
   * @param {string} [faction] faction key for background tint
   * @param {number} [size]     pixel size (default 96)
   * @returns {string} SVG markup
   */
function fighterPortraitSVG(fighterId, name, faction, size) {
    size = size || 96;
    var rng = mulberry32(hashStr(String(fighterId)));
    var skin = pick(rng, SKIN_TONES);
    var hair = pick(rng, HAIR_COLORS);
    var accent = pick(rng, ACCENT);
    var bg = (faction && BG_COLORS[faction]) || "#1a1512";

    var faceW = 34 + rng() * 8;
    var faceH = 40 + rng() * 8;
    var jawSharp = rng() > 0.5;
    var hairStyle = Math.floor(rng() * 5); // 0=short, 1=long, 2=mohawk/fade, 3=bald, 4=dreads-ish
    var beard = rng() > 0.65;
    var mark = rng() > 0.7;
    var markSide = rng() > 0.5 ? 1 : -1;
    var angryBrows = rng() > 0.4;
    var accessory = rng() > 0.75;
    var mouthSmirk = rng() > 0.5;

    var cx = 50;
    var faceTop = 50 - faceH / 2;
    var uid = 'fp-' + String(fighterId).replace(/[^a-z0-9]/gi, '');
    var slashY = 60 + rng() * 20;
    var dreads = '';
    var i, x;

    if (hairStyle === 4) {
      for (i = 0; i < 7; i++) {
        x = cx - 18 + i * 6;
        dreads += '<rect x="' + x.toFixed(1) + '" y="' + (faceTop - 8).toFixed(1) +
          '" width="4.5" height="' + (26 + rng() * 10).toFixed(1) + '" rx="2"/>';
      }
    }

    var face = jawSharp
      ? '<polygon points="' + (cx - faceW / 2).toFixed(1) + ',' + faceTop.toFixed(1) + ' ' +
        (cx + faceW / 2).toFixed(1) + ',' + faceTop.toFixed(1) + ' ' +
        (cx + faceW / 2).toFixed(1) + ',' + (faceTop + faceH * 0.6).toFixed(1) + ' ' +
        cx + ',' + (faceTop + faceH).toFixed(1) + ' ' +
        (cx - faceW / 2).toFixed(1) + ',' + (faceTop + faceH * 0.6).toFixed(1) +
        '" fill="' + skin + '"/>'
      : '<ellipse cx="' + cx + '" cy="' + (faceTop + faceH / 2).toFixed(1) +
        '" rx="' + (faceW / 2).toFixed(1) + '" ry="' + (faceH / 2).toFixed(1) +
        '" fill="' + skin + '"/>';

    var hairSvg = '';
    if (hairStyle === 0) {
      hairSvg = '<path d="M' + (cx - faceW / 2 - 2).toFixed(1) + ' ' + (faceTop + 12).toFixed(1) +
        ' Q' + cx + ' ' + (faceTop - 14).toFixed(1) + ' ' + (cx + faceW / 2 + 2).toFixed(1) + ' ' + (faceTop + 12).toFixed(1) +
        ' L' + (cx + faceW / 2 - 2).toFixed(1) + ' ' + (faceTop + 4).toFixed(1) +
        ' Q' + cx + ' ' + (faceTop - 4).toFixed(1) + ' ' + (cx - faceW / 2 + 2).toFixed(1) + ' ' + (faceTop + 4).toFixed(1) +
        ' Z" fill="' + hair + '"/>';
    } else if (hairStyle === 1) {
      hairSvg = '<g fill="' + hair + '">' +
        '<path d="M' + (cx - faceW / 2 - 4).toFixed(1) + ' ' + (faceTop + 40).toFixed(1) +
        ' Q' + (cx - faceW / 2 - 6).toFixed(1) + ' ' + (faceTop - 10).toFixed(1) + ' ' + cx + ' ' + (faceTop - 12).toFixed(1) +
        ' Q' + (cx + faceW / 2 + 6).toFixed(1) + ' ' + (faceTop - 10).toFixed(1) + ' ' + (cx + faceW / 2 + 4).toFixed(1) + ' ' + (faceTop + 40).toFixed(1) +
        ' L' + (cx + faceW / 2 - 2).toFixed(1) + ' ' + (faceTop + 38).toFixed(1) +
        ' Q' + cx + ' ' + (faceTop + 2).toFixed(1) + ' ' + (cx - faceW / 2 + 2).toFixed(1) + ' ' + (faceTop + 38).toFixed(1) + ' Z"/>' +
        '<ellipse cx="' + (cx - faceW / 2 - 2).toFixed(1) + '" cy="' + (faceTop + 42).toFixed(1) + '" rx="5" ry="12"/>' +
        '<ellipse cx="' + (cx + faceW / 2 + 2).toFixed(1) + '" cy="' + (faceTop + 42).toFixed(1) + '" rx="5" ry="12"/>' +
        '</g>';
    } else if (hairStyle === 2) {
      hairSvg = '<g fill="' + hair + '">' +
        '<rect x="' + (cx - 6) + '" y="' + (faceTop - 16).toFixed(1) + '" width="12" height="22" rx="3"/>' +
        '<rect x="' + (cx - faceW / 2).toFixed(1) + '" y="' + faceTop.toFixed(1) + '" width="' + faceW.toFixed(1) + '" height="6" opacity="0.6"/>' +
        '</g>';
    } else if (hairStyle === 3) {
      hairSvg = '<ellipse cx="' + cx + '" cy="' + (faceTop + 2).toFixed(1) + '" rx="' + (faceW / 2).toFixed(1) + '" ry="6" fill="' + skin + '" opacity="0.7"/>';
    } else {
      hairSvg = '<g fill="' + hair + '">' + dreads + '</g>';
    }

    var brows = angryBrows
      ? '<g stroke="#1a1a1a" stroke-width="2.5" stroke-linecap="round">' +
        '<path d="M' + (cx - 14) + ' ' + (faceTop + 22).toFixed(1) + ' L' + (cx - 4) + ' ' + (faceTop + 26).toFixed(1) + '"/>' +
        '<path d="M' + (cx + 14) + ' ' + (faceTop + 22).toFixed(1) + ' L' + (cx + 4) + ' ' + (faceTop + 26).toFixed(1) + '"/></g>'
      : '<g stroke="#1a1a1a" stroke-width="2" stroke-linecap="round">' +
        '<path d="M' + (cx - 14) + ' ' + (faceTop + 23).toFixed(1) + ' Q' + (cx - 9) + ' ' + (faceTop + 21).toFixed(1) + ' ' + (cx - 4) + ' ' + (faceTop + 23).toFixed(1) + '"/>' +
        '<path d="M' + (cx + 4) + ' ' + (faceTop + 23).toFixed(1) + ' Q' + (cx + 9) + ' ' + (faceTop + 21).toFixed(1) + ' ' + (cx + 14) + ' ' + (faceTop + 23).toFixed(1) + '"/></g>';

    var mouth = mouthSmirk
      ? '<path d="M' + (cx - 7) + ' ' + (faceTop + 46).toFixed(1) + ' Q' + cx + ' ' + (faceTop + 49).toFixed(1) + ' ' + (cx + 7) + ' ' + (faceTop + 46).toFixed(1) + '" stroke="#1a1a1a" stroke-width="2" fill="none" stroke-linecap="round"/>'
      : '<rect x="' + (cx - 6) + '" y="' + (faceTop + 44).toFixed(1) + '" width="12" height="3" rx="1.5" fill="#1a1a1a" opacity="0.8"/>';

    var beardSvg = beard
      ? '<path d="M' + (cx - faceW / 2 + 4).toFixed(1) + ' ' + (faceTop + faceH * 0.62).toFixed(1) +
        ' Q' + cx + ' ' + (faceTop + faceH + 6).toFixed(1) + ' ' + (cx + faceW / 2 - 4).toFixed(1) + ' ' + (faceTop + faceH * 0.62).toFixed(1) +
        ' Q' + cx + ' ' + (faceTop + faceH - 4).toFixed(1) + ' ' + (cx - faceW / 2 + 4).toFixed(1) + ' ' + (faceTop + faceH * 0.62).toFixed(1) +
        ' Z" fill="' + hair + '" opacity="0.85"/>'
      : '';

    var markSvg = mark
      ? '<g stroke="' + accent + '" stroke-width="2" opacity="0.85" stroke-linecap="round">' +
        '<path d="M' + (cx + markSide * 12) + ' ' + (faceTop + 18).toFixed(1) + ' L' + (cx + markSide * 8) + ' ' + (faceTop + 34).toFixed(1) + '"/>' +
        '<path d="M' + (cx + markSide * 14) + ' ' + (faceTop + 24).toFixed(1) + ' L' + (cx + markSide * 6) + ' ' + (faceTop + 28).toFixed(1) + '"/></g>'
      : '';

    var accessorySvg = accessory
      ? '<rect x="' + (cx - faceW / 2 - 2).toFixed(1) + '" y="' + (faceTop + 6).toFixed(1) +
        '" width="' + (faceW + 4).toFixed(1) + '" height="7" fill="' + accent + '" opacity="0.9" transform="rotate(-3 ' + cx + ' ' + (faceTop + 9).toFixed(1) + ')"/>'
      : '';

    var escName = String(name).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');

    return '<svg width="' + size + '" height="' + size + '" viewBox="0 0 100 100" role="img" aria-label="' + escName + '">' +
      '<defs>' +
      '<clipPath id="' + uid + '-clip"><rect x="0" y="0" width="100" height="100" rx="8"/></clipPath>' +
      '<pattern id="' + uid + '-dots" width="8" height="8" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#ffffff" opacity="0.06"/></pattern>' +
      '</defs>' +
      '<g clip-path="url(#' + uid + '-clip)">' +
      '<rect width="100" height="100" fill="' + bg + '"/>' +
      '<rect width="100" height="100" fill="url(#' + uid + '-dots)"/>' +
      '<polygon points="0,100 100,' + slashY.toFixed(1) + ' 100,100" fill="' + accent + '" opacity="0.25"/>' +
      '<rect x="' + (cx - 9) + '" y="' + (50 + faceH / 2 - 8).toFixed(1) + '" width="18" height="20" fill="' + skin + '" opacity="0.85"/>' +
      '<path d="M' + (cx - 28) + ' 100 Q' + (cx - 24) + ' 78 ' + (cx - 10) + ' 72 L' + (cx + 10) + ' 72 Q' + (cx + 24) + ' 78 ' + (cx + 28) + ' 100 Z" fill="#241d17"/>' +
      '<path d="M' + (cx - 28) + ' 100 Q' + (cx - 24) + ' 78 ' + (cx - 10) + ' 72 L' + (cx + 10) + ' 72 Q' + (cx + 24) + ' 78 ' + (cx + 28) + ' 100 Z" fill="' + accent + '" opacity="0.3"/>' +
      face + hairSvg + brows +
      '<g fill="#1a1a1a">' +
      '<ellipse cx="' + (cx - 9) + '" cy="' + (faceTop + 30).toFixed(1) + '" rx="3.2" ry="2.4"/>' +
      '<ellipse cx="' + (cx + 9) + '" cy="' + (faceTop + 30).toFixed(1) + '" rx="3.2" ry="2.4"/>' +
      '</g>' +
      '<circle cx="' + (cx - 8.2) + '" cy="' + (faceTop + 29.2).toFixed(1) + '" r="0.9" fill="#fff"/>' +
      '<circle cx="' + (cx + 9.8) + '" cy="' + (faceTop + 29.2).toFixed(1) + '" r="0.9" fill="#fff"/>' +
      '<path d="M' + cx + ' ' + (faceTop + 32).toFixed(1) + ' L' + (cx - 2.5) + ' ' + (faceTop + 40).toFixed(1) + ' L' + (cx + 2.5) + ' ' + (faceTop + 40).toFixed(1) + ' Z" fill="#000" opacity="0.18"/>' +
      mouth + beardSvg + markSvg + accessorySvg +
      '<polygon points="0,0 26,0 0,26" fill="' + accent + '" opacity="0.5"/>' +
      '</g>' +
      '<rect x="1" y="1" width="98" height="98" rx="8" fill="none" stroke="' + accent + '" stroke-width="2" opacity="0.6"/>' +
      '</svg>';
}

/**
   * Render a portrait into a container element (select-screen portrait slot).
   * @param {HTMLElement} el container
   * @param {string} fighterId
   * @param {string} name
   * @param {string} [faction]
   * @param {number} [size]
   */
function renderPortrait(el, fighterId, name, faction, size) {
    if (!el) return;
    var user = getPortrait(fighterId);
    if (user) {
      var escName = String(name == null ? '' : name).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
      el.innerHTML = '<img src="' + user + '" alt="' + escName + '" style="width:100%;height:100%;object-fit:cover;border-radius:8px">';
      return;
    }
    el.innerHTML = fighterPortraitSVG(fighterId, name, faction, size);
}

export { fighterPortraitSVG, renderPortrait };
export default { svg: fighterPortraitSVG, render: renderPortrait };
