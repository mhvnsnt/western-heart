// Playwright end-to-end: ui-wh wired into game/ — title → menu → modes → select → VS
// → real fight (live HUD) → pause → resume → results → main menu, then classic fallback.
// Serve game/ (python3 -m http.server 8765 -d game), then: node game/ui-wh/tools/flow.mjs <outdir>
import { chromium } from "playwright";
const out = process.argv[2] || "proof";
const base = `http://127.0.0.1:${process.env.WH_PORT || 8765}`;
const browser = await chromium.launch({ ...(process.env.PW_CHROMIUM ? { executablePath: process.env.PW_CHROMIUM } : {}),
  args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--autoplay-policy=no-user-gesture-required"] });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
const errors = [], log = [];
page.on("pageerror", (e) => errors.push("pageerror " + e));
page.on("response", (r) => { if (r.status() >= 400) log.push("WARN " + r.status() + " " + r.url()); });
let n = 0;
const shot = async (name) => { const p = `${out}/${String(++n).padStart(2, "0")}_${name}.png`; await page.screenshot({ path: p }); log.push(p); };
const ui = () => page.frameLocator("#wh-ui");
const uiScreen = () => page.evaluate(() => document.getElementById("wh-ui").contentDocument.body.dataset.screen);
const g = (fn) => page.evaluate(fn);
const expect = (ok, msg) => { if (!ok) errors.push("EXPECT " + msg); log.push((ok ? "ok   " : "FAIL ") + msg); };

await page.goto(`${base}/index.html?ui=wh&demo=1`);
await page.waitForFunction(() => document.getElementById("wh-ui")?.contentWindow?.__WH_UI_READY);
expect(await g(() => !document.querySelector("#screen-menu.active")), "classic menu hidden when ui=wh");
await page.waitForTimeout(500); await shot("title");
await ui().locator('section[data-screen="title"]').click(); await page.waitForTimeout(300);
expect((await uiScreen()) === "menu", "title → menu"); await shot("menu");
await ui().locator("#menu-list a").first().click(); await page.waitForTimeout(300);
expect((await uiScreen()) === "modes", "menu → modes"); await shot("modes");
await ui().locator("#mode-cards .card").first().click(); await page.waitForTimeout(300);
expect((await uiScreen()) === "select", "modes → select"); await shot("select");
await ui().locator("#sel-grid .cell").nth(13).click(); await page.waitForTimeout(200);   // pick SCIMITAR as P1
await ui().locator("#sel-grid .cell").nth(0).click(); await page.waitForTimeout(200);    // PANTERA as P1
await ui().locator("#sel-grid .cell").nth(0).click(); await page.waitForTimeout(500);    // confirm → VS
expect((await uiScreen()) === "vs", "select → VS"); await shot("vs");
await page.waitForFunction(() => window.__game.running && window.__game.roundState === "fight", null, { timeout: 90000 });
expect((await uiScreen()) === "hud", "VS → fight with ui-wh HUD");
expect(await g(() => window.__game.p1 && window.__game.p2 && document.getElementById("wh-ui").style.pointerEvents === "none"), "real Game running, overlay passes input through");
await page.waitForTimeout(4000); await shot("fight_hud");
// live-state check: knock P2 HP down in the real Game and the ui-wh bar must follow
await g(() => { window.__game.p2.hp = Math.round(window.__game.p2.maxHp * 0.4); });
await page.waitForTimeout(500);
const bar = await page.evaluate(() => document.getElementById("wh-ui").contentDocument.querySelector(".plate.r .bar i").style.width);
const clock = await page.evaluate(() => document.getElementById("wh-ui").contentDocument.querySelector(".clock b").textContent);
log.push(`p2 bar ${bar}, HUD clock ${clock}, game timer ${await g(() => window.__game.timer.toFixed(2))}`);
expect(bar === "40%", "HUD bar driven by live game state");
await page.keyboard.press("Escape"); await page.waitForTimeout(400);
expect((await uiScreen()) === "pause" && (await g(() => window.__game.paused)), "Esc → ui-wh pause, game paused"); await shot("pause");
await ui().locator("#pause-list a").first().click(); await page.waitForTimeout(600);
expect((await uiScreen()) === "hud" && !(await g(() => window.__game.paused)), "RESUME → fight continues");
await page.waitForTimeout(6000); await shot("fight_resumed");
// Software WebGL on the box runs the game ~10x slow, so the harness shortens each round's
// clock; rounds and the match still end through the Game's own time-out/round/match logic.
const fast = setInterval(() => page.evaluate(() => { const g = window.__game; if (g.running && g.roundState === "fight" && g.timer > 2) g.timer = 1.5; }).catch(() => {}), 1000);
await page.waitForFunction(() => document.getElementById("wh-ui").contentDocument.body.dataset.screen === "results", null, { timeout: 420000, polling: 1000 });
clearInterval(fast);
expect(true, "match ended → ui-wh results"); await page.waitForTimeout(500); await shot("results");
log.push("results: " + await page.evaluate(() => document.getElementById("wh-ui").contentDocument.querySelector("#res-stats").innerText.replace(/\s+/g, " ")));
await ui().locator("#res-list a").nth(2).click(); await page.waitForTimeout(400);
expect((await uiScreen()) === "menu" && !(await g(() => window.__game.running)), "MAIN MENU → back to menu, fight torn down"); await shot("back_to_menu");
await page.goto(`${base}/index.html`); await page.waitForTimeout(800);
expect(await g(() => !document.getElementById("wh-ui") && !!document.querySelector("#screen-menu.active")), "fallback: classic menu without toggle"); await shot("classic_fallback");
await browser.close();
console.log(log.join("\n"));
console.log(errors.length ? "UI FLOW: FAIL\n" + errors.join("\n") : "UI FLOW: PASS");
process.exit(errors.length ? 1 : 0);
