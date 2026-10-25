import { ROSTER } from "./roster.js";
// [LANE-I select-redesign] rebuilt select screen (Tekken 8-style, live 3D)
import { initSelect } from "./cards.js";
const $ = (s) => document.querySelector(s);
const EMBED = new URLSearchParams(location.search).has("embed");
if (EMBED) { document.body.classList.add("embed"); document.documentElement.style.background = "transparent"; }
let P1 = ROSTER[0], P2 = ROSTER.find((r) => r.id === "saku_ra");
const post = (m) => EMBED && parent.postMessage({ src: "wh-ui", ...m }, "*");
const go = (h) => { location.hash = h; };

const MENU = [
  ["TRIAL", "トライアル", "Climb the Ladder of Tong-Nou. Nine souls, one vessel."],
  ["VERSUS", "対戦", "Two vessels, one shrine. Local or online."],
  ["PRACTICE", "練習", "Frame data, hitboxes and recordings in the Lab."],
  ["CREATE A VESSEL", "魂の器", "Build a fighter in the creation suite."],
  ["THE LIBRARY", "書庫", "Canon, endings and the soul bestiary."],
  ["OPTIONS", "設定", "Controls, sound, display."],
];
const MODES = [
  ["TRIAL", "The Ladder", "梯子", "1P vs CPU up the nine rooms of Tong-Nou."],
  ["TAG TRIAL", "Twin Souls", "双魂", "Two vessels, one life bar each, tag on the beat."],
  ["SURVIVAL", "The Long Night", "長夜", "How many rooms before the soul gives out."],
  ["TIME ATTACK", "The Hourglass", "砂時計", "SHA's sand runs. Clear the ladder fast."],
  ["STREET", "The Western Heart", "西の心", "Brawl-style free movement, environment hits."],
  ["GAUNTLET", "Wrestling Night", "格闘夜", "Ring, ropes, pins and submissions."],
];
// Settings > Dev Sandbox: the physics / model / animation workbench (mhvnsnt/physics-playground-pwa).
// Its test models (Scarlett, Madelyn) live only in the sandbox and are not roster fighters.
const SANDBOX_URL = "https://physics-playground-pwa.pages.dev/";
// worker 22 (2026-10-22): rollback netplay demo (game/netplay/) — proven
// GGPO-style P2P versus. Opens in a new tab; full combat-sim port is
// tracked in docs/research/OPEN-SOURCE-WAVE-2026-10-22.md §netplay.
const NETPLAY_URL = "netplay/demo/index.html";
const OPTIONS = [
  ["DEV SANDBOX", "開発", "Physics, rigs, jiggle, soft body, face and visemes, movesets, fights and AI tests: the dev workbench."],
  ["NETPLAY (BETA)", "対戦", "Rollback netplay vs a friend — P2P WebRTC, GGPO-style. Opens the netplay demo in a new tab."],
  ["BACK", "戻る", "Return to the main menu."],
];
const nav = (el, items, render) => { el.innerHTML = items.map(render).join(""); };

nav($("#menu-list"), MENU, ([en, jp], i) => `<a class="${i === 0 ? "on" : ""}">${en}<i>${jp}</i></a>`);
$("#menu-blurb").textContent = MENU[0][2];
nav($("#opt-list"), OPTIONS, ([en, jp], i) => `<a class="${i === 0 ? "on" : ""}">${en}<i>${jp}</i></a>`);
$("#opt-blurb").textContent = OPTIONS[0][2];
$("#ds-open").href = SANDBOX_URL;
nav($("#mode-cards"), MODES, ([en, sub, jp, d], i) =>
  `<div class="card ${i === 0 ? "on" : ""}"><b>${en}</b><em>${sub}</em><i>${jp}</i><p>${d}</p></div>`);

// [LANE-I select-redesign] OLD select grid DELETED here (the .sel-side/#sel-grid
// renderer with repeated 2-3 renders, no names, page-level vertical scroll —
// owner-flagged embarrassment). The #select section is now a mount point; the
// rebuilt Tekken 8-style select screen lives in cards.js (initSelect: bisected
// live-3D zone, contained card strip, attire slots, hints bar).
let selectHandle = null;
function mountSelect() {
  const root = document.getElementById("select-root");
  if (!root || selectHandle) return;
  selectHandle = initSelect(root, {
    initial: { p1: P1.id, p2: P2.id },
    onFight: (p1, p2, attire1, attire2) => {
      P1 = byId(p1) || P1; P2 = byId(p2) || P2;
      renderVs();
      startVs(attire1, attire2);
    },
    onBack: () => go("menu"),
  });
}
function syncSelect() { if (selectHandle) selectHandle.setFighters(P1.id, P2.id); }

const vs = (r) => `<img src="${r.full}" class="${r.model ? "" : "sil"}"><div class="vs-name"><span class="k">${r.kanji}</span>${r.name}<em>${r.soul}</em><small>${r.origin}</small>${r.model ? "" : "<small class='pend'> · MODEL PENDING</small>"}</div>`;
function renderVs() { $("#vs-l").innerHTML = vs(P1); $("#vs-r").innerHTML = vs(P2); }
renderVs();

$("#hud-n1").innerHTML = `${P1.name}<i>${P1.kanji}</i>`; $("#hud-n2").innerHTML = `<i>${P2.kanji}</i>${P2.name}`;
const souls = (n) => Array.from({ length: 9 }, (_, i) => `<em class="${i < n ? "on" : ""}"></em>`).join("");
$("#hud-s1").innerHTML = souls(6); $("#hud-s2").innerHTML = souls(3);

nav($("#pause-list"), [["RESUME", "再開"], ["COMMAND LIST", "技表"], ["CONTROLS", "操作"], ["RESTART", "やり直し"], ["CHARACTER SELECT", "魂を選べ"], ["MAIN MENU", "メニュー"]],
  ([en, jp], i) => `<a class="${i === 0 ? "on" : ""}">${en}<i>${jp}</i></a>`);

const QUOTES = { pantera: "“The soul IS the hold.”" };   // CANON.md lines only
function renderResults(w, stats) {
  $("#res-hero").innerHTML = `<img src="${w.full}" class="${w.model ? "" : "sil"}">`;
  $("#res-name").innerHTML = `<span class="k">${w.kanji}</span>${w.name}<em>${w.soul}</em>`;
  $("#res-quote").textContent = QUOTES[w.id] || "";
  $("#res-stats").innerHTML = stats.map(([k, v]) => `<tr><td>${k}</td><td>${v}</td></tr>`).join("");
}
renderResults(P1, [["ROUNDS", "2 – 1"], ["TIME", "1:47"], ["MAX COMBO", "7 HITS"], ["SOUL SURGE", "1"], ["PERFECT", "—"]]);
nav($("#res-list"), [["REMATCH", "再戦"], ["CHARACTER SELECT", "魂を選べ"], ["MAIN MENU", "メニュー"]],
  ([en, jp], i) => `<a class="${i === 0 ? "on" : ""}">${en}<i>${jp}</i></a>`);

function route() {
  const s = (location.hash || "#title").slice(1);
  document.querySelectorAll("section[data-screen]").forEach((e) => e.classList.toggle("active", e.dataset.screen === s));
  document.body.dataset.screen = s;
  const fr = $("#ds-frame");   // load the sandbox only while its page is open
  if (s === "devsandbox" && !fr.src) fr.src = SANDBOX_URL;
  if (s === "select") mountSelect(); // [LANE-I select-redesign] mount rebuilt screen
}
addEventListener("hashchange", route); route();
// Keyboard flow: Enter advances title→menu→modes→select→vs→hud, Esc pauses/backs.
// [LANE-I select-redesign] the rebuilt select screen owns Enter/Esc on #select
// (P1/P2 confirm flow, punch/kick attire rule) — the old skip-to-VS is gone.
const FLOW = ["title", "menu", "modes", "select", "vs", "hud", "results"];
addEventListener("keydown", (e) => {
  const s = document.body.dataset.screen, i = FLOW.indexOf(s);
  if (s === "options" || s === "devsandbox") { if (e.key === "Escape") go(s === "devsandbox" ? "options" : "menu"); return; }
  if (EMBED && (s === "vs" || s === "hud" || s === "results")) { if (e.key === "Escape" && s === "hud") post({ type: "pause" }); return; }
  if (e.key === "Enter" && s !== "select" && i >= 0 && i < FLOW.length - 1) location.hash = FLOW[i + 1];
  if (e.key === "Escape" && s !== "select") location.hash = s === "hud" ? "pause" : s === "pause" ? "hud" : FLOW[Math.max(i - 1, 0)];
});

// ---- interactivity (standalone + embedded in game/) ----
// [LANE-I select-redesign] attire slots now ride along (T8: slot chosen on select)
function startVs(attire1, attire2) { go("vs"); if (EMBED) setTimeout(() => post({ type: "fight", p1: P1.id, p2: P2.id, attire1, attire2 }), 1800); }
const bind = (sel, fn) => document.querySelectorAll(sel).forEach((el, i) => el.addEventListener("click", () => fn(i)));
document.querySelector('section[data-screen="title"]').addEventListener("click", () => go("menu"));
bind("#menu-list a", (i) => { if (i === 0 || i === 1) go("modes"); else if (i === 2) { P2 = P1; go("select"); } else if (i === 5) go("options"); });
bind("#opt-list a", (i) => {
  if (i === 0) go("devsandbox");
  else if (i === 1) (window.top || window).open(NETPLAY_URL, "_blank", "noopener");
  else go("menu");
});
document.querySelectorAll("#opt-list a").forEach((a, i) => a.addEventListener("mouseenter", () => { $("#opt-blurb").textContent = OPTIONS[i][2]; }));
$("#ds-back").addEventListener("click", () => go("options"));
bind("#mode-cards .card", () => go("select"));
bind("#pause-list a", (i) => post({ type: ["resume", "commands", "controls", "restart", "select", "menu"][i] }) || (!EMBED && go(i === 0 ? "hud" : i === 4 ? "select" : i === 5 ? "menu" : "pause")));
bind("#res-list a", (i) => post({ type: ["rematch", "select", "menu"][i] }) || (!EMBED && go(["vs", "select", "menu"][i])));
const byId = (id) => ROSTER.find((r) => r.id.replace(/[^a-z0-9]/g, "") === String(id).replace(/[^a-z0-9]/g, ""));
function hud(d) {
  const set = (side, f) => {
    const pct = Math.max(0, (f.hp / f.maxHp) * 100);
    // COMBAT-SYSTEMS 2026-10-24: white recoverable bar (<b>) extends
    // past the hp fill by the pool; the red trail (<u>) keeps its old
    // delayed-shrink behaviour underneath it.
    const greyPct = Math.max(pct, Math.min(100, ((f.hp + (f.recoverable || 0)) / f.maxHp) * 100));
    const bar = document.querySelector(`.plate.${side} .bar`);
    const gb = bar.querySelector("b"); if (gb) gb.style.width = greyPct + "%";
    bar.querySelector("i").style.width = pct + "%";
    const u = bar.querySelector("u"); if (parseFloat(u.style.width) < pct || !u.dataset.t) u.style.width = pct + "%";
    clearTimeout(u._t); u._t = setTimeout(() => { u.style.width = pct + "%"; }, 600); u.dataset.t = 1;
    document.getElementById(side === "l" ? "hud-s1" : "hud-s2").innerHTML = souls(Math.floor((f.meter / f.maxMeter) * 9 + 1e-3));
  };
  set("l", d.p1); set("r", d.p2);
  document.querySelector(".clock b").textContent = String(d.timer).padStart(2, "0");
  const pip = (w) => `<em class="${w >= 1 ? "won" : ""}"></em><em class="${w >= 2 ? "won" : ""}"></em>`;
  document.querySelector(".clock span").innerHTML = `${pip(d.wins.p1)} ROUND ${d.round} ${pip(d.wins.p2)}`;
}
addEventListener("message", (e) => {
  const m = e.data || {}; if (m.src !== "wh-game") return;
  if (m.type === "show") go(m.screen);
  if (m.type === "fighters") { P1 = byId(m.p1) || P1; P2 = byId(m.p2) || P2; syncSelect(); renderVs(); // [LANE-I select-redesign] old renderSelect() deleted
    $("#hud-n1").innerHTML = `${P1.name}<i>${P1.kanji}</i>`; $("#hud-n2").innerHTML = `<i>${P2.kanji}</i>${P2.name}`; }
  if (m.type === "hud") hud(m);
  if (m.type === "combo") { const fx = document.querySelector(".hud-fx"); fx.querySelector("b").textContent = m.n; fx.classList.remove("pop"); void fx.offsetWidth; fx.classList.add("pop"); }
  if (m.type === "results") { renderResults(byId(m.winner) || P1, m.stats); go("results"); }
});
if (EMBED) document.querySelector(".hud-fx").classList.add("idle");
window.__WH_UI_READY = true;
