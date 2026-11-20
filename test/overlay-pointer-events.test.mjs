// Fight-start overlays must never eat touches (owner 2026-10-25 stuck-drag bug):
// #wh-loading and #wh-vs are display-only full-screen overlays. With default
// pointer-events they intercept every touch while up; a drag that starts on
// one stays dead after it hides (nipplejs only creates a nipple on touchstart)
// until lift + re-touch. #wh-pause MUST keep intercepting (it has buttons).
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';

const menus = readFileSync(new URL('../game/menus.css', import.meta.url), 'utf8');
const styles = readFileSync(new URL('../game/styles.css', import.meta.url), 'utf8');

function blocks(css, selector) {
  // All rule blocks for exactly this selector (not .show/.hide/.hidden
  // variants: those have a class suffix between selector and brace).
  const re = new RegExp(selector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\s*\\{[^}]*\\}', 'g');
  const out = css.match(re) || [];
  assert.ok(out.length >= 1, `missing rule ${selector}`);
  return out;
}
const hasNone = (b) => /pointer-events\s*:\s*none/.test(b);
const anyNone = (arr) => arr.some(hasNone);

assert.ok(anyNone(blocks(menus, '#wh-loading')), '#wh-loading must be pointer-events:none (display-only overlay must not eat touches)');
assert.ok(anyNone(blocks(menus, '#wh-vs')), '#wh-vs must be pointer-events:none (display-only overlay must not eat touches)');
assert.ok(!anyNone(blocks(menus, '#wh-pause')), '#wh-pause must KEEP intercepting touches (RESUME/OPTIONS/QUIT buttons)');
assert.ok(anyNone(blocks(styles, '.loading')), 'boot .loading overlay keeps its t122u pointer-events:none precedent');
console.log('overlay-pointer-events: ok (#wh-loading + #wh-vs pass-through, #wh-pause intercepts, boot .loading intact)');
