import { ROSTER } from "./roster.js";
const $ = (s) => document.querySelector(s);
const P1 = ROSTER[0], P2 = ROSTER.find((r) => r.id === "saku_ra");

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
const nav = (el, items, render) => { el.innerHTML = items.map(render).join(""); };

nav($("#menu-list"), MENU, ([en, jp], i) => `<a class="${i === 0 ? "on" : ""}">${en}<i>${jp}</i></a>`);
$("#menu-blurb").textContent = MENU[0][2];
nav($("#mode-cards"), MODES, ([en, sub, jp, d], i) =>
  `<div class="card ${i === 0 ? "on" : ""}"><b>${en}</b><em>${sub}</em><i>${jp}</i><p>${d}</p></div>`);

const side = (r, who) => `<img src="${r.full}" class="${r.model ? "" : "sil"}"><div class="tag ${who}">
  <span class="k">${r.kanji}</span><b>${r.name}</b><em>${r.soul}</em>
  <small>ORIGIN · ${r.origin}</small>${r.model ? "" : "<small class='pend'>MODEL PENDING</small>"}</div>`;
$("#sel-p1").innerHTML = side(P1, "p1"); $("#sel-p2").innerHTML = side(P2, "p2");
nav($("#sel-grid"), ROSTER, (r) => `<div class="cell ${r.id === P1.id ? "c1" : ""} ${r.id === P2.id ? "c2" : ""}">
  <img src="${r.bust}" class="${r.model ? "" : "sil"}"><span class="k">${r.kanji}</span><b>${r.name}</b></div>`);

const vs = (r) => `<img src="${r.full}" class="${r.model ? "" : "sil"}"><div class="vs-name"><span class="k">${r.kanji}</span>${r.name}<em>${r.soul}</em><small>${r.origin}</small>${r.model ? "" : "<small class='pend'> · MODEL PENDING</small>"}</div>`;
$("#vs-l").innerHTML = vs(P1); $("#vs-r").innerHTML = vs(P2);

$("#hud-n1").innerHTML = `${P1.name}<i>${P1.kanji}</i>`; $("#hud-n2").innerHTML = `<i>${P2.kanji}</i>${P2.name}`;
const souls = (n) => Array.from({ length: 9 }, (_, i) => `<em class="${i < n ? "on" : ""}"></em>`).join("");
$("#hud-s1").innerHTML = souls(6); $("#hud-s2").innerHTML = souls(3);

nav($("#pause-list"), [["RESUME", "再開"], ["COMMAND LIST", "技表"], ["CONTROLS", "操作"], ["RESTART", "やり直し"], ["CHARACTER SELECT", "魂を選べ"], ["MAIN MENU", "メニュー"]],
  ([en, jp], i) => `<a class="${i === 0 ? "on" : ""}">${en}<i>${jp}</i></a>`);

$("#res-hero").innerHTML = `<img src="${P1.full}">`;
$("#res-name").innerHTML = `<span class="k">${P1.kanji}</span>${P1.name}<em>${P1.soul}</em>`;
$("#res-quote").textContent = "“The soul IS the hold.”";   // CANON.md, Pantera body/mind/soul
$("#res-stats").innerHTML = [["ROUNDS", "2 – 1"], ["TIME", "1:47"], ["MAX COMBO", "7 HITS"], ["SOUL SURGE", "1"], ["PERFECT", "—"]]
  .map(([k, v]) => `<tr><td>${k}</td><td>${v}</td></tr>`).join("");
nav($("#res-list"), [["REMATCH", "再戦"], ["CHARACTER SELECT", "魂を選べ"], ["MAIN MENU", "メニュー"]],
  ([en, jp], i) => `<a class="${i === 0 ? "on" : ""}">${en}<i>${jp}</i></a>`);

function route() {
  const s = (location.hash || "#title").slice(1);
  document.querySelectorAll("[data-screen]").forEach((e) => e.classList.toggle("active", e.dataset.screen === s));
  document.body.dataset.screen = s;
}
addEventListener("hashchange", route); route();
// Keyboard flow: Enter advances title→menu→modes→select→vs→hud, Esc pauses/backs.
const FLOW = ["title", "menu", "modes", "select", "vs", "hud", "results"];
addEventListener("keydown", (e) => {
  const s = document.body.dataset.screen, i = FLOW.indexOf(s);
  if (e.key === "Enter" && i >= 0 && i < FLOW.length - 1) location.hash = FLOW[i + 1];
  if (e.key === "Escape") location.hash = s === "hud" ? "pause" : s === "pause" ? "hud" : FLOW[Math.max(i - 1, 0)];
});
window.__WH_UI_READY = true;
