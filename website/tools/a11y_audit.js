// Accessibility audit of one Spectrum Atlas page (module 08 scenario S6; website BACKLOG row 9).
//
// Paste into the browser console (or a javascript tool) on a built or published page, then call
// `await a11yAudit()`. It returns one JSON object: axe-core's violations at WCAG 2.2 AA + best practice, and
// a contrast sweep of its own. The sweep exists because axe 4.10 cannot parse the site's oklch() colour
// tokens and reports those nodes as "incomplete" instead of measuring them; here every colour is resolved
// through a canvas to sRGB first. On a large page (the Atlas list has ~44,000 elements) run the two halves
// in separate calls: `a11yAudit({ sweep: false })` and `a11yAudit({ axe: false })`.
//
// S6 passes on a page when `axe.serious_or_critical` is 0 and `contrast.failures` is empty. Run it in the
// light and the dark scheme (prefers-color-scheme), at desktop and phone width.
async function a11yAudit({ axe = true, sweep = true } = {}) {
  const AXE = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js";
  const out = {
    url: location.href,
    scheme: matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light",
    viewport: [document.documentElement.clientWidth, innerHeight],
    horizontal_scroll: document.documentElement.scrollWidth > document.documentElement.clientWidth,
  };

  if (sweep) {
    const cv = document.createElement("canvas");
    cv.width = cv.height = 1;
    const cx = cv.getContext("2d", { willReadFrequently: true });
    const parsed = new Map();
    const rgba = (c) => {
      if (!parsed.has(c)) {
        cx.clearRect(0, 0, 1, 1);
        cx.fillStyle = "rgba(0,0,0,0)";
        cx.fillStyle = c;
        cx.fillRect(0, 0, 1, 1);
        parsed.set(c, Array.from(cx.getImageData(0, 0, 1, 1).data));
      }
      return parsed.get(c);
    };
    const lum = (rgb) => {
      const f = (v) => {
        v /= 255;
        return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
      };
      return 0.2126 * f(rgb[0]) + 0.7152 * f(rgb[1]) + 0.0722 * f(rgb[2]);
    };
    const over = (top, under) => {
      const a = top[3] / 255;
      return [0, 1, 2].map((i) => top[i] * a + under[i] * (1 - a)).concat(255);
    };

    // The backdrop of an element: its own background blended over its parent's backdrop, down to the page.
    // A background image on the way is reported, not guessed. Memoised per element.
    const root = rgba(getComputedStyle(document.documentElement).backgroundColor);
    const pageBg = root[3] === 0 ? [255, 255, 255, 255] : root;
    const memo = new WeakMap();
    const backdrop = (el) => {
      if (!el || el === document.documentElement) return { bg: pageBg, image: null };
      if (memo.has(el)) return memo.get(el);
      const cs = getComputedStyle(el);
      const c = rgba(cs.backgroundColor);
      const below = c[3] === 255 ? null : backdrop(el.parentElement);
      const res = {
        bg: c[3] === 255 ? c : c[3] === 0 ? below.bg : over(c, below.bg),
        image: cs.backgroundImage !== "none" ? cs.backgroundImage.slice(0, 80) : below ? below.image : null,
      };
      memo.set(el, res);
      return res;
    };

    // Text inside an SVG (the charts, a rendered diagram) sits on shapes painted before it, not on its DOM ancestors: sample the paint
    // stack at the text's centre, top to bottom, until an opaque layer. Lines and unfilled paths paint no area and are passed over.
    const areas = new Set(["rect", "circle", "ellipse", "polygon", "path"]);
    const svgText = new Set(["text", "tspan", "textPath"]);
    const painted = (el) => {
      el.scrollIntoView({ block: "center", inline: "center" });
      const r = el.getBoundingClientRect();
      const layers = [];
      let base = null;
      for (const e of document.elementsFromPoint(r.left + r.width / 2, r.top + r.height / 2)) {
        if (e === el || svgText.has(e.localName)) continue;
        const cs = getComputedStyle(e);
        let c = null;
        if (e instanceof SVGElement) {
          if (!areas.has(e.localName) || cs.fill === "none") continue;
          const f = rgba(cs.fill);
          c = [f[0], f[1], f[2], f[3] * +cs.fillOpacity * +cs.opacity];
        } else {
          c = rgba(cs.backgroundColor);
        }
        if (c[3] >= 254.5) {
          base = c;
          break;
        }
        if (c[3] > 0) layers.push(c);
      }
      let bg = base ?? pageBg;
      while (layers.length) bg = over(layers.pop(), bg);
      return { bg, image: null };
    };

    const visible = (el) => {
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) return false;
      if (el.closest("[aria-hidden='true'], [hidden]")) return false;
      if (el.closest("details:not([open]) > :not(summary)")) return false;
      const cs = getComputedStyle(el);
      return cs.visibility !== "hidden" && cs.display !== "none" && +cs.opacity > 0;
    };
    const ownText = (el) =>
      Array.from(el.childNodes)
        .filter((n) => n.nodeType === Node.TEXT_NODE)
        .map((n) => n.textContent)
        .join("")
        .trim();

    // Failures are grouped by element kind and colour pair, so a style repeated on 11,000 cards is one row.
    const groups = new Map();
    let checked = 0;
    let lowest = null;
    for (const el of document.querySelectorAll("body *")) {
      const text = ownText(el);
      if (!text || !/[\p{L}\p{N}]/u.test(text) || !visible(el)) continue;
      const cs = getComputedStyle(el);
      const isSvg = svgText.has(el.localName);
      const fg = rgba(isSvg ? cs.fill : cs.color);
      if (fg[3] === 0) continue;
      // opacity is not inherited but multiplies down the tree; SVG text adds fill-opacity (the µm axis uses 0.7)
      let alpha = (fg[3] / 255) * (isSvg ? +cs.fillOpacity : 1);
      for (let e = el; e; e = e.parentElement) alpha *= +getComputedStyle(e).opacity;
      const { bg, image } = el.closest("svg") ? painted(el) : backdrop(el);
      const fgOn = over([fg[0], fg[1], fg[2], alpha * 255], bg);
      const L1 = lum(fgOn);
      const L2 = lum(bg);
      const ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
      const px = parseFloat(cs.fontSize);
      const large = px >= 24 || (+cs.fontWeight >= 700 && px >= 18.66);
      const need = large ? 3 : 4.5;
      checked += 1;
      const cls = typeof el.className === "string" && el.className.trim()
        ? "." + el.className.trim().split(/\s+/).join(".")
        : "";
      const row = {
        el: el.localName + cls,
        text: text.slice(0, 40),
        ratio: +ratio.toFixed(2),
        need,
        px,
        fg: fgOn.slice(0, 3).map(Math.round),
        bg: bg.slice(0, 3).map(Math.round),
        image,
      };
      if (!lowest || ratio < lowest.ratio) lowest = row;
      if (ratio < need || image) {
        const key = `${row.el}|${row.fg}|${row.bg}|${need}`;
        if (groups.has(key)) groups.get(key).count += 1;
        else groups.set(key, { ...row, count: 1 });
      }
    }
    out.contrast = { checked, lowest, failures: [...groups.values()] };
  }

  if (axe) {
    if (!window.axe) {
      await new Promise((ok, no) => {
        const s = document.createElement("script");
        s.src = AXE;
        s.onload = ok;
        s.onerror = no;
        document.head.appendChild(s);
      });
    }
    const r = await window.axe.run(document, {
      runOnly: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"],
    });
    const violations = r.violations.map((v) => ({
      id: v.id,
      impact: v.impact,
      nodes: v.nodes.length,
      help: v.help,
      first: v.nodes.slice(0, 3).map((n) => n.target.join(" ")),
    }));
    out.axe = {
      version: window.axe.version,
      serious_or_critical: violations.filter((v) => v.impact === "serious" || v.impact === "critical").length,
      violations,
      incomplete: r.incomplete.map((v) => `${v.id}:${v.impact}:${v.nodes.length}`),
      passes: r.passes.length,
    };
  }
  return out;
}
