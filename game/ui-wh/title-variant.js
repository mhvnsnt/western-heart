// Applies the title variant before first paint: sets <html data-title="vN"> (CSS keys
// the wallpaper and lettering off it) and the Japanese logo line once the DOM exists.
(function () {
  var C = window.WH_TITLE_CONFIG || { default: "v3", variants: {} };
  var alias = { original: "v1", lunge: "v2", folded: "v3" };
  var q = new URLSearchParams(location.search).get("title");
  var stored = null; try { stored = localStorage.getItem("wh_title"); } catch (e) {}
  var pick = function (v) { v = alias[v] || v; return C.variants[v] ? v : null; };
  var v = pick(q) || pick(stored) || C.default;
  document.documentElement.setAttribute("data-title", v);
  window.WH_TITLE = v;
  document.addEventListener("DOMContentLoaded", function () {
    var jp = document.querySelector(".logo-jp");
    if (jp && C.variants[v]) jp.textContent = C.variants[v].jp;
  });
})();
