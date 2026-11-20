// Showcase capture: select screen (default + ?unlock=all), every card, promo strip.
// Serve game/ (python3 -m http.server 8765 -d game) then: node game/ui-wh/tools/capture_cards.mjs <outdir>
import { chromium } from "playwright";
import { ROSTER } from "../roster.js";
const out = process.argv[2] || "proof", base = `http://127.0.0.1:${process.env.WH_PORT || 8765}/ui-wh`;
const b = await chromium.launch(process.env.PW_CHROMIUM ? { executablePath: process.env.PW_CHROMIUM } : {});
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } }); const err = [];
p.on("pageerror", (e) => err.push(String(e))); p.on("response", (r) => r.status() >= 400 && err.push(r.status() + " " + r.url()));
for (const [q, n] of [["", "select_default"], ["?unlock=all", "select_unlock_all"]]) {
  await p.goto(`${base}/index.html${q}#select`); await p.waitForFunction(() => window.__WH_UI_READY); await p.waitForTimeout(600);
  const locked = await p.$$eval(".cell.locked", (e) => e.length); console.log(n, "locked cells:", locked);
  await p.screenshot({ path: `${out}/${n}.png` });
}
for (const r of ROSTER) {
  await p.goto(`${base}/cards.html?unlock=all#${r.id}`); await p.waitForFunction(() => window.__WH_CARDS_READY); await p.waitForTimeout(300);
  await p.screenshot({ path: `${out}/card_${r.id}.png` });
}
await p.goto(`${base}/cards.html?unlock=all#strip`); await p.waitForFunction(() => window.__WH_CARDS_READY); await p.waitForTimeout(300);
await p.screenshot({ path: `${out}/promo_strip.png` });
await b.close(); console.log(err.length ? "CARDS: FAIL\n" + err.join("\n") : `CARDS: PASS (${ROSTER.length} cards + 2 select + strip)`); process.exit(err.length ? 1 : 0);
