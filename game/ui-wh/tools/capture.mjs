// Playwright capture of every Western Heart menu screen.
// Serve game/ (python3 -m http.server 8765 -d game), then: node game/ui-wh/tools/capture.mjs <outdir>
import { chromium } from "playwright";
const out = process.argv[2] || "proof";
const SCREENS = ["title", "menu", "modes", "select", "vs", "hud", "pause", "results"];
const browser = await chromium.launch(process.env.PW_CHROMIUM ? { executablePath: process.env.PW_CHROMIUM } : {});
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
const errors = [];
page.on("pageerror", (e) => errors.push(String(e)));
page.on("requestfailed", (r) => errors.push("404 " + r.url()));
page.on("response", (r) => { if (r.status() >= 400) errors.push(r.status() + " " + r.url()); });
await page.goto(`http://127.0.0.1:${process.env.WH_PORT || 8765}/ui-wh/index.html#title`);
await page.waitForFunction(() => window.__WH_UI_READY);
for (const s of SCREENS) {
  await page.evaluate((h) => (location.hash = h), s);
  await page.waitForTimeout(400);
  const active = await page.evaluate(() => document.querySelector("[data-screen].active")?.dataset.screen);
  if (active !== s) errors.push(`screen ${s} not active (got ${active})`);
  await page.screenshot({ path: `${out}/${SCREENS.indexOf(s) + 1}_${s}.png` });
}
// keyboard flow: Enter from title reaches menu, Esc in hud opens pause
await page.evaluate(() => (location.hash = "title")); await page.keyboard.press("Enter"); await page.waitForTimeout(100);
const k1 = await page.evaluate(() => document.body.dataset.screen);
await page.evaluate(() => (location.hash = "hud")); await page.keyboard.press("Escape"); await page.waitForTimeout(100);
const k2 = await page.evaluate(() => document.body.dataset.screen);
if (k1 !== "menu" || k2 !== "pause") errors.push(`keyboard flow failed: ${k1} ${k2}`);
await browser.close();
console.log(errors.length ? "UI CAPTURE: FAIL\n" + errors.join("\n") : `UI CAPTURE: PASS (${SCREENS.length} screens, keyboard flow ok)`);
process.exit(errors.length ? 1 : 0);
