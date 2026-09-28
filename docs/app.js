// Charts and tables for the results site. All numbers come from data.json (built by build_site_data.py).
(function () {
  "use strict";

  const SERIES = [
    { key: "B", name: "Jev", color: "var(--s1)" },
    { key: "C", name: "Sonnet 5", color: "var(--s2)" },
    { key: "D", name: "Haiku 4.5", color: "var(--s3)" },
  ];
  const NS = "http://www.w3.org/2000/svg";
  const tip = document.getElementById("tip");
  const fmt = (v, d = 1) => (v == null ? "–" : Number(v).toFixed(d));

  // ---------- small helpers ----------
  function el(tag, attrs, parent) {
    const node = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (k === "style") node.setAttribute("style", v);
      else if (k === "text") node.textContent = v;
      else node.setAttribute(k, v);
    }
    if (parent) parent.appendChild(node);
    return node;
  }
  function svgFor(container, width, height) {
    container.innerHTML = "";
    return el("svg", { viewBox: `0 0 ${width} ${height}`, width, height, role: "img" }, container);
  }
  function scale(d0, d1, r0, r1) {
    return (v) => r0 + ((v - d0) / (d1 - d0)) * (r1 - r0);
  }
  function showTip(html, container, x, y) {
    tip.innerHTML = html;
    const box = container.getBoundingClientRect();
    tip.classList.add("on");
    const tw = tip.offsetWidth, th = tip.offsetHeight;
    let left = box.left + window.scrollX + x + 14;
    if (left + tw > window.scrollX + document.documentElement.clientWidth - 8) left = box.left + window.scrollX + x - tw - 14;
    tip.style.left = left + "px";
    tip.style.top = box.top + window.scrollY + y - th / 2 + "px";
  }
  function hideTip() { tip.classList.remove("on"); }
  function row(label, value, color) {
    const key = color ? `<i class="key" style="background:${color}"></i>` : "";
    return `<div class="tr"><span>${key}${label}</span><span>${value}</span></div>`;
  }
  function table(id, head, rows, highlight) {
    const t = document.getElementById(id);
    if (!t) return;
    t.innerHTML = "<thead><tr>" + head.map((h) => `<th>${h}</th>`).join("") + "</tr></thead><tbody>" +
      rows.map((r, i) => `<tr${highlight && highlight(r, i) ? ' class="hl"' : ""}>` + r.map((c) => `<td>${c}</td>`).join("") + "</tr>").join("") +
      "</tbody>";
  }
  function yAxis(svg, y, ticks, x0, x1, suffix) {
    for (const t of ticks) {
      el("line", { x1: x0, x2: x1, y1: y(t), y2: y(t), style: "stroke:var(--grid);stroke-width:1" }, svg);
      el("text", { x: x0 - 8, y: y(t) + 4, "text-anchor": "end", "font-size": 11.5, style: "fill:var(--muted);font-variant-numeric:tabular-nums", text: t + suffix }, svg);
    }
  }

  // ---------- Hero: accuracy vs cost ----------
  function hero(data) {
    const box = document.getElementById("hero");
    if (!box) return;
    const W = Math.max(300, box.clientWidth), H = W < 480 ? 250 : 290;
    const m = { l: 44, r: 18, t: 18, b: 40 };
    const svg = svgFor(box, W, H);
    const lx = (v) => Math.log10(v);
    const x = scale(lx(0.05), lx(12), m.l, W - m.r), y = scale(82, 94, H - m.b, m.t);
    yAxis(svg, y, [82, 86, 90, 94], m.l, W - m.r, "%");
    for (const t of [0.1, 1, 10]) {
      el("line", { x1: x(lx(t)), x2: x(lx(t)), y1: m.t, y2: H - m.b, style: "stroke:var(--grid)" }, svg);
      el("text", { x: x(lx(t)), y: H - m.b + 18, "text-anchor": "middle", "font-size": 11.5, style: "fill:var(--muted)", text: "$" + t }, svg);
    }
    el("text", { x: (m.l + W - m.r) / 2, y: H - 4, "text-anchor": "middle", "font-size": 12, style: "fill:var(--ink-2)", text: "Cost per 1,000 decisions (log scale) →" }, svg);
    el("text", { x: m.l + 6, y: H - m.b - 8, "font-size": 11.5, style: "fill:var(--muted)", text: "Accuracy ↑" }, svg);
    const pts = SERIES.map((s) => {
      const c = data.contenders[s.key], r = c.rows.find((q) => q.target === 70);
      return { ...s, cx: x(lx(c.cost_per_1000)), cy: y(r.accuracy), acc: r.accuracy, cost: c.cost_per_1000 };
    });
    // Bracket showing the cost gap between Jev and Sonnet.
    const [j, so] = pts;
    const by = Math.min(j.cy, so.cy) - 26;
    el("path", { d: `M${j.cx},${by + 6} V${by} H${so.cx} V${by + 6}`, fill: "none", style: "stroke:var(--ink-2);stroke-width:1" }, svg);
    el("text", { x: (j.cx + so.cx) / 2, y: by - 6, "text-anchor": "middle", "font-size": 12.5, style: "fill:var(--ink);font-weight:600", text: `${Math.floor(data.cost_ratio_sonnet_jev)}× the cost, same accuracy` }, svg);
    for (const p of pts) {
      el("circle", { cx: p.cx, cy: p.cy, r: 16, style: `fill:${p.color};opacity:0.12` }, svg);
      el("circle", { cx: p.cx, cy: p.cy, r: 7, style: `fill:${p.color};stroke:var(--surface);stroke-width:2.5` }, svg);
      const right = p.key !== "C";
      el("text", { x: p.cx + (right ? 14 : -14), y: p.cy + (p.key === "D" ? 18 : 18), "text-anchor": right ? "start" : "end", "font-size": 12.5, style: "fill:var(--ink);font-weight:600", text: p.name }, svg);
      if (W < 480) { const h0 = el("circle", { cx: p.cx, cy: p.cy, r: 18, fill: "transparent" }, svg); h0.addEventListener("mouseenter", () => showTip(`<div class="tt">${p.name}</div>` + row("Accuracy, auto-accepted", fmt(p.acc) + "%") + row("Cost per 1,000", "$" + fmt(p.cost, 2)), box, (p.cx / W) * box.clientWidth, (p.cy / H) * box.clientHeight)); h0.addEventListener("mouseleave", hideTip); continue; }
      el("text", { x: p.cx + (right ? 14 : -14), y: p.cy + 33, "text-anchor": right ? "start" : "end", "font-size": 11.5, style: "fill:var(--ink-2);font-variant-numeric:tabular-nums", text: `${fmt(p.acc)}% · $${fmt(p.cost, 2)}` }, svg);
      const h = el("circle", { cx: p.cx, cy: p.cy, r: 18, fill: "transparent" }, svg);
      h.addEventListener("mouseenter", () => showTip(`<div class="tt">${p.name}</div>` + row("Accuracy, auto-accepted", fmt(p.acc) + "%") + row("Cost per 1,000", "$" + fmt(p.cost, 2)), box, (p.cx / W) * box.clientWidth, (p.cy / H) * box.clientHeight));
      h.addEventListener("mouseleave", hideTip);
    }
  }

  // ---------- Finding 1: accuracy vs automation ----------
  function tradeoff(data) {
    const box = document.getElementById("tradeoff");
    if (!box) return;
    const W = Math.max(320, box.clientWidth), H = W < 560 ? 300 : 360;
    const m = { l: 46, r: 16, t: 16, b: 44 };
    const svg = svgFor(box, W, H);
    const x = scale(30, 100, m.l, W - m.r), y = scale(75, 100, H - m.b, m.t);
    yAxis(svg, y, [75, 80, 85, 90, 95, 100], m.l, W - m.r, "%");
    for (const t of [30, 40, 50, 60, 70, 80, 90, 100]) {
      el("text", { x: x(t), y: H - m.b + 20, "text-anchor": "middle", "font-size": 11.5, style: "fill:var(--muted)", text: t + "%" }, svg);
    }
    el("line", { x1: m.l, x2: W - m.r, y1: H - m.b, y2: H - m.b, style: "stroke:var(--axis)" }, svg);
    el("text", { x: (m.l + W - m.r) / 2, y: H - 6, "text-anchor": "middle", "font-size": 12, style: "fill:var(--ink-2)", text: "Share of messages auto-accepted →" }, svg);
    el("text", { x: m.l, y: m.t - 4, "font-size": 12, style: "fill:var(--ink-2)", text: "Accuracy on auto-accepted ↑" }, svg);

    const curves = {};
    for (const s of SERIES) {
      const pts = data.curves[s.key].filter((p) => p.share >= 30);
      curves[s.key] = data.curves[s.key];
      const d = pts.map((p, i) => `${i ? "L" : "M"}${x(p.share).toFixed(1)},${y(Math.max(75, p.accuracy)).toFixed(1)}`).join("");
      const path = el("path", { d, fill: "none", class: "draw", style: `stroke:${s.color};stroke-width:2;stroke-linejoin:round;stroke-linecap:round` }, svg);
      const len = path.getTotalLength ? path.getTotalLength() : 0;
      path.style.strokeDasharray = len; path.style.strokeDashoffset = len;
      requestAnimationFrame(() => { path.style.transition = "stroke-dashoffset 1.6s cubic-bezier(.3,.7,.2,1)"; path.style.strokeDashoffset = 0; });
    }
    // Pre-registered 70% operating points (thresholds chosen on tuning, applied to test).
    for (const s of SERIES) {
      const r = data.contenders[s.key].rows.find((q) => q.target === 70);
      el("circle", { cx: x(r.realized), cy: y(r.accuracy), r: 6.5, style: `fill:var(--surface);stroke:${s.color};stroke-width:2.5` }, svg);
    }
    const labelB = data.contenders.B.rows.find((q) => q.target === 70), labelC = data.contenders.C.rows.find((q) => q.target === 70);
    const narrow = W < 560;
    el("text", { x: narrow ? x(labelB.realized) - 10 : x(labelC.realized) + 10, y: y(Math.max(labelB.accuracy, labelC.accuracy)) - 14, "text-anchor": narrow ? "end" : "start", "font-size": 12, style: "fill:var(--ink);paint-order:stroke;stroke:var(--surface);stroke-width:4px", text: `Jev ${fmt(labelB.accuracy)}% · Sonnet ${fmt(labelC.accuracy)}%` }, svg);

    // Hover: vertical guide + each model's best achievable point at or below that share.
    const guide = el("line", { y1: m.t, y2: H - m.b, style: "stroke:var(--axis);stroke-width:1;opacity:0" }, svg);
    const dots = SERIES.map((s) => el("circle", { r: 4.5, style: `fill:${s.color};stroke:var(--surface);stroke-width:2;opacity:0` }, svg));
    const hit = el("rect", { x: m.l, y: m.t, width: W - m.l - m.r, height: H - m.t - m.b, fill: "transparent" }, svg);
    function move(evt) {
      const rect = svg.getBoundingClientRect();
      const px = ((evt.touches ? evt.touches[0].clientX : evt.clientX) - rect.left) * (W / rect.width);
      const share = Math.min(100, Math.max(30, 30 + ((px - m.l) / (W - m.l - m.r)) * 70));
      guide.setAttribute("x1", x(share)); guide.setAttribute("x2", x(share)); guide.style.opacity = 1;
      let html = `<div class="tt">Automating up to ${fmt(share, 0)}% of messages</div>`;
      SERIES.forEach((s, i) => {
        const pts = curves[s.key].filter((p) => p.share <= share);
        const p = pts[pts.length - 1];
        if (!p) { dots[i].style.opacity = 0; html += row(s.name, "–", s.color); return; }
        dots[i].setAttribute("cx", x(Math.max(30, p.share))); dots[i].setAttribute("cy", y(Math.max(75, p.accuracy))); dots[i].style.opacity = p.share >= 30 ? 1 : 0;
        html += row(s.name, `${fmt(p.accuracy)}% right · ${fmt(p.share)}% auto`, s.color);
      });
      showTip(html, box, (x(share) / W) * rect.width, (m.t + 60) * (rect.height / H));
    }
    hit.addEventListener("mousemove", move);
    hit.addEventListener("touchmove", move, { passive: true });
    hit.addEventListener("mouseleave", () => { guide.style.opacity = 0; dots.forEach((d) => (d.style.opacity = 0)); hideTip(); });

    table("t-headline", ["Model", "Setting", "Cutoff", "Actually auto-accepted", "Accuracy on auto-accepted", "Accuracy, all answers"],
      SERIES.flatMap((s) => data.contenders[s.key].rows.map((r) => [
        `<i class="key" style="background:${s.color}"></i>${s.name}`, r.target + "%", fmt(r.threshold, 0), fmt(r.realized) + "%", fmt(r.accuracy) + "%", fmt(data.contenders[s.key].accuracy_all) + "%",
      ])), (r) => r[1] === "70%");
  }

  // ---------- Finding 2: cost ----------
  function costBars(data) {
    const box = document.getElementById("costbars");
    if (!box) return;
    const items = [
      { name: "Jev", v: data.contenders.B.cost_per_million, color: "var(--s1)" },
      { name: "Cascade", v: data.cascade.find((c) => c.target === 70).cost_per_million, color: "var(--muted)" },
      { name: "Haiku 4.5", v: data.contenders.D.cost_per_million, color: "var(--s3)" },
      { name: "Sonnet 5", v: data.contenders.C.cost_per_million, color: "var(--s2)" },
    ];
    const max = Math.max(...items.map((i) => i.v));
    box.innerHTML = items.map((i) => `
      <div class="bar-row"><div>${i.name}</div>
        <div class="bar-track"><div class="bar" style="width:${(i.v / max) * 82}%;background:${i.color}"></div>
        <div class="bar-value num" style="left:${(i.v / max) * 82}%">$${Math.round(i.v).toLocaleString()}</div></div></div>`).join("");
    table("t-cost", ["Setup", "Cost per 1,000", "Per 1 million", "Median time per message"], [
      ["Jev", "$" + fmt(data.contenders.B.cost_per_1000, 2), "$" + data.contenders.B.cost_per_million.toLocaleString(), data.contenders.B.median_ms + " ms"],
      ["Cascade (Jev → Sonnet)", "$" + fmt(data.cascade[1].cost_per_1000, 2), "$" + data.cascade[1].cost_per_million.toLocaleString(), "–"],
      ["Haiku 4.5", "$" + fmt(data.contenders.D.cost_per_1000, 2), "$" + data.contenders.D.cost_per_million.toLocaleString(), data.contenders.D.median_ms + " ms"],
      ["Sonnet 5", "$" + fmt(data.contenders.C.cost_per_1000, 2), "$" + data.contenders.C.cost_per_million.toLocaleString(), data.contenders.C.median_ms + " ms"],
    ]);
  }

  // ---------- Finding 3: cascade ----------
  function cascade(data) {
    const box = document.getElementById("cascade");
    if (!box) return;
    const c = data.cascade.find((q) => q.target === 70);
    const s = data.contenders.C;
    box.innerHTML = `
      <div class="split">
        <div class="a" style="flex:${c.jev_share}"><b>${fmt(c.jev_share)}%</b>Jev auto-accepts · ${fmt(c.jev_accuracy)}% right</div>
        <div class="b" style="flex:${100 - c.jev_share}"><b>${fmt(100 - c.jev_share)}%</b>Sonnet 5 handles</div>
      </div>
      <div class="compare">
        <div class="win"><div class="lbl">Cascade: Jev first, Sonnet for the rest</div><div class="v num">${fmt(c.overall)}%</div><div class="c num">accuracy · $${fmt(c.cost_per_1000, 2)} per 1,000</div></div>
        <div><div class="lbl">Sonnet 5 on every message</div><div class="v num">${fmt(s.accuracy_all)}%</div><div class="c num">accuracy · $${fmt(s.cost_per_1000, 2)} per 1,000</div></div>
      </div>`;
    table("t-cascade", ["Jev setting", "Jev handles", "Accuracy, Jev's share", "Accuracy, Sonnet's share", "Overall", "Cost per 1,000"],
      data.cascade.map((q) => [q.target + "%", fmt(q.jev_share) + "%", fmt(q.jev_accuracy) + "%", fmt(q.sonnet_accuracy) + "%", fmt(q.overall) + "%", "$" + fmt(q.cost_per_1000, 2)]),
      (r) => r[0] === "70%");
  }

  // ---------- Finding 4: achievable settings (strip) + calibration ----------
  function strip(data) {
    const box = document.getElementById("strip");
    if (!box) return;
    const W = Math.max(320, box.clientWidth), rowH = 66, H = SERIES.length * rowH + 50;
    const m = { l: W < 560 ? 76 : 96, r: 16 };
    const svg = svgFor(box, W, H);
    const x = scale(0, 100, m.l, W - m.r);
    for (const t of [0, 25, 50, 75, 100]) {
      el("line", { x1: x(t), x2: x(t), y1: 8, y2: H - 30, style: "stroke:var(--grid)" }, svg);
      el("text", { x: x(t), y: H - 12, "text-anchor": "middle", "font-size": 11.5, style: "fill:var(--muted)", text: t + "%" }, svg);
    }
    el("line", { x1: x(70), x2: x(70), y1: 8, y2: H - 30, style: "stroke:var(--ink-2);stroke-width:1;stroke-dasharray:3 3" }, svg);
    el("text", { x: x(70), y: H - 12, "text-anchor": "middle", "font-size": 11.5, style: "fill:var(--ink);font-weight:600;paint-order:stroke;stroke:var(--surface);stroke-width:4px", text: "70% target" }, svg);
    SERIES.forEach((s, i) => {
      const cy = 24 + i * rowH;
      const pts = data.curves[s.key];
      el("text", { x: 0, y: cy + 4, "font-size": 13, style: "fill:var(--ink);font-weight:600", text: s.name }, svg);
      el("text", { x: 0, y: cy + 20, "font-size": 11.5, style: "fill:var(--muted)", text: `${pts.length} settings` }, svg);
      el("line", { x1: x(0), x2: x(100), y1: cy, y2: cy, style: "stroke:var(--hair)" }, svg);
      const r70 = data.contenders[s.key].rows.find((q) => q.target === 70);
      for (const p of pts) {
        const c = el("circle", { cx: x(p.share), cy, r: 4.5, style: `fill:${s.color};stroke:var(--surface);stroke-width:1.5` }, svg);
        const hitc = el("circle", { cx: x(p.share), cy, r: 10, fill: "transparent" }, svg);
        hitc.addEventListener("mouseenter", () => {
          c.setAttribute("r", 6.5);
          showTip(`<div class="tt">${s.name}: cutoff ${fmt(p.threshold, 0)}</div>` + row("Auto-accepted", fmt(p.share) + "%") + row("Accuracy on those", fmt(p.accuracy) + "%"),
            box, (x(p.share) / W) * box.clientWidth, cy * (box.clientWidth / W));
        });
        hitc.addEventListener("mouseleave", () => { c.setAttribute("r", 4.5); hideTip(); });
      }
      el("circle", { cx: x(r70.realized), cy, r: 8.5, style: `fill:none;stroke:var(--ink);stroke-width:1.5` }, svg);
      el("text", { x: x(r70.realized), y: cy + 24, "text-anchor": "middle", "font-size": 11.5, style: "fill:var(--ink);font-weight:600", text: `actually ${fmt(r70.realized)}%` }, svg);
    });
  }

  function calibration(data) {
    const box = document.getElementById("calib");
    if (!box) return;
    const W = Math.max(320, box.clientWidth), H = 300, m = { l: 46, r: 12, t: 16, b: 44 };
    const bands = data.calibration.B.map((b) => b.band);
    const mids = [25, 55, 65, 75, 85, 95];
    const svg = svgFor(box, W, H);
    const step = (W - m.l - m.r) / bands.length;
    const x = (i, dodge = 0) => m.l + step * (i + 0.5) + dodge;
    const y = scale(0, 100, H - m.b, m.t);
    yAxis(svg, y, [0, 25, 50, 75, 100], m.l, W - m.r, "%");
    bands.forEach((b, i) => el("text", { x: x(i), y: H - m.b + 20, "text-anchor": "middle", "font-size": 11.5, style: "fill:var(--muted)", text: b.replace("-", "–") }, svg));
    el("text", { x: (m.l + W - m.r) / 2, y: H - 6, "text-anchor": "middle", "font-size": 12, style: "fill:var(--ink-2)", text: "Confidence the model reported" }, svg);
    el("polyline", { points: mids.map((v, i) => `${x(i)},${y(v)}`).join(" "), fill: "none", style: "stroke:var(--muted);stroke-width:1" }, svg);
    SERIES.forEach((s, k) => {
      const dodge = (k - 1) * 7;
      const pts = data.calibration[s.key];
      let run = [];
      const flush = () => { if (run.length > 1) el("polyline", { points: run.join(" "), fill: "none", style: `stroke:${s.color};stroke-width:2;stroke-linejoin:round` }, svg); run = []; };
      pts.forEach((p, i) => { if (p.accuracy == null || p.n < 20) flush(); else run.push(`${x(i, dodge)},${y(p.accuracy)}`); });
      flush();
      pts.forEach((p, i) => {
        if (p.accuracy == null) return;
        const hollow = p.n < 20;
        const c = el("circle", { cx: x(i, dodge), cy: y(p.accuracy), r: 4, style: hollow ? `fill:var(--surface);stroke:${s.color};stroke-width:2` : `fill:${s.color};stroke:var(--surface);stroke-width:2` }, svg);
        const h = el("circle", { cx: x(i, dodge), cy: y(p.accuracy), r: 11, fill: "transparent" }, svg);
        h.addEventListener("mouseenter", () => showTip(`<div class="tt">${s.name}, said ${p.band.replace("-", "–")}</div>` + row("Actually right", fmt(p.accuracy) + "%") + row("Answers in band", p.n), box, (x(i, dodge) / W) * box.clientWidth, y(p.accuracy) * (box.clientWidth / W)));
        h.addEventListener("mouseleave", hideTip);
        void c;
      });
    });
    const head = ["Said", ...SERIES.flatMap((s) => [`${s.name}: answers`, `${s.name}: right`])];
    table("t-calib", head, bands.map((b, i) => [b.replace("-", "–"), ...SERIES.flatMap((s) => {
      const p = data.calibration[s.key][i];
      return [p.n, p.accuracy == null ? "–" : fmt(p.accuracy) + "%"];
    })]));
  }

  // ---------- Finding 5: gate ----------
  function gate(data) {
    const set = (k, v) => document.querySelectorAll(`[data-k="${k}"]`).forEach((n) => (n.textContent = v));
    set("kw-wrong", fmt(data.gate.B.keyword_flags_wrong) + "%");
    set("kw-right", fmt(data.gate.B.keyword_flags_correct) + "%");
    set("mv-B", fmt(data.matched_volume_730.B));
    set("mv-C", fmt(data.matched_volume_730.C));
    table("t-invalid", ["Invented or unreadable categories (1,000 answers)", "Count", "Auto-accepted"],
      SERIES.map((s) => [`<i class="key" style="background:${s.color}"></i>${s.name}`, data.contenders[s.key].hard_hallucinations, "0"]));
    table("t-keyword", ["Model", "Right answers flagged", "Wrong answers flagged"],
      SERIES.map((s) => [s.name, fmt(data.gate[s.key].keyword_flags_correct) + "%", fmt(data.gate[s.key].keyword_flags_wrong) + "%"]));
  }

  // ---------- Finding 6: tuning, before/after ----------
  function tuning(data) {
    const box = document.getElementById("tuning");
    if (!box) return;
    const at70 = (k) => data.contenders[k].rows.find((q) => q.target === 70).accuracy;
    const items = [
      { name: "Jev", before: at70("A"), after: at70("B"), color: "var(--s1)" },
      { name: "Sonnet 5", before: at70("F"), after: at70("C"), color: "var(--s2)" },
    ];
    const W = Math.max(320, box.clientWidth), H = 230, m = { l: 46, r: 24, t: 24, b: 40 };
    const svg = svgFor(box, W, H);
    const y = scale(88, 93, H - m.b, m.t);
    const xs = [m.l + (W - m.l - m.r) * 0.18, m.l + (W - m.l - m.r) * (W < 480 ? 0.55 : 0.66)];
    yAxis(svg, y, [88, 89, 90, 91, 92, 93], m.l, W - m.r, "%");
    ["Before (names only)", "After (rewritten)"].forEach((t, i) => el("text", { x: xs[i], y: H - m.b + 22, "text-anchor": "middle", "font-size": 12, style: "fill:var(--ink-2)", text: t }, svg));
    items.forEach((it, k) => {
      el("line", { x1: xs[0], x2: xs[1], y1: y(it.before), y2: y(it.after), style: `stroke:${it.color};stroke-width:2` }, svg);
      [[0, it.before], [1, it.after]].forEach(([i, v]) => {
        el("circle", { cx: xs[i], cy: y(v), r: 5, style: `fill:${it.color};stroke:var(--surface);stroke-width:2` }, svg);
        const label = i ? `${fmt(v)}%  ${it.name} +${fmt(it.after - it.before)}` : `${fmt(v)}%`;
        el("text", { x: xs[i] + (i ? 12 : -12), y: y(v) + 4 + (k ? 7 : -5), "text-anchor": i ? "start" : "end", "font-size": 12, style: "fill:var(--ink);font-variant-numeric:tabular-nums", text: label }, svg);
      });
    });
    table("t-tuning", ["Model", "Before", "After", "Change", "All answers: before → after"], [
      ["Jev", fmt(items[0].before) + "%", fmt(items[0].after) + "%", "+" + fmt(items[0].after - items[0].before), `${fmt(data.contenders.A.accuracy_all)}% → ${fmt(data.contenders.B.accuracy_all)}%`],
      ["Sonnet 5", fmt(items[1].before) + "%", fmt(items[1].after) + "%", "+" + fmt(items[1].after - items[1].before), `${fmt(data.contenders.F.accuracy_all)}% → ${fmt(data.contenders.C.accuracy_all)}%`],
    ]);
  }

  // ---------- Report page tables ----------
  function reportTables(data) {
    const names = { A: "A · Jev, v1", B: "B · Jev, v2 (final)", C: "C · Sonnet 5, v2", D: "D · Haiku 4.5, v2", F: "F · Sonnet 5, v1" };
    table("r-results", ["Contender", "Target", "Cutoff", "Realized", "Acc. on auto-accepted", "Soft halluc.", "Hard halluc.", "Acc. all", "$ / 1k"],
      Object.keys(names).flatMap((k) => data.contenders[k].rows.map((r) => [
        names[k], r.target + "%", fmt(r.threshold, 0), fmt(r.realized) + "%", fmt(r.accuracy) + "%", fmt(100 - r.accuracy) + "%",
        fmt(data.contenders[k].hard_hallucinations / 10) + "%", fmt(data.contenders[k].accuracy_all) + "%", "$" + fmt(data.contenders[k].cost_per_1000, 2),
      ])), (r) => r[1] === "70%" && (r[0].startsWith("B") || r[0].startsWith("C")));
    table("r-cascade", ["Jev target", "Jev handles", "Jev share acc.", "Sonnet share acc.", "Overall", "$ / 1k"],
      data.cascade.map((q) => [q.target + "%", fmt(q.jev_share) + "%", fmt(q.jev_accuracy) + "%", fmt(q.sonnet_accuracy) + "%", fmt(q.overall) + "%", "$" + fmt(q.cost_per_1000, 2)]));
    const bands = data.calibration.B.map((b) => b.band);
    table("r-calib", ["Band", ...["A", "B", "C", "D", "F"].map((k) => k + " n / acc.")],
      bands.map((b, i) => [b, ...["A", "B", "C", "D", "F"].map((k) => { const p = data.calibration[k][i]; return `${p.n} / ${p.accuracy == null ? "–" : fmt(p.accuracy) + "%"}`; })]));
    table("r-keyword", ["Contender", "Keyword check: right flagged", "Wrong flagged"],
      Object.keys(names).map((k) => [names[k], fmt(data.gate[k].keyword_flags_correct) + "%", fmt(data.gate[k].keyword_flags_wrong) + "%"]));
  }

  // ---------- boot ----------
  function renderAll(data) {
    hero(data); tradeoff(data); costBars(data); cascade(data); strip(data); calibration(data); gate(data); tuning(data); reportTables(data);
  }
  fetch("data.json").then((r) => r.json()).then((data) => {
    renderAll(data);
    let t;
    let lastW = window.innerWidth;
    window.addEventListener("resize", () => {
      if (window.innerWidth === lastW) return;
      lastW = window.innerWidth;
      clearTimeout(t); t = setTimeout(() => { hero(data); tradeoff(data); strip(data); calibration(data); tuning(data); }, 150);
    });
    document.querySelectorAll("details.more").forEach((d) => d.addEventListener("toggle", () => { if (d.open) { calibration(data); } }));
    const bars = document.getElementById("costbars");
    if (bars) {
      const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { bars.classList.remove("pre"); io.disconnect(); } }), { threshold: 0.3 });
      io.observe(bars);
    }
  });

  // Section reveal on scroll.
  const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), { threshold: 0.08 });
  document.querySelectorAll(".reveal").forEach((n) => io.observe(n));

  // Report page: highlight the current section in the table of contents.
  const tocLinks = [...document.querySelectorAll(".toc a")];
  if (tocLinks.length) {
    const heads = [...document.querySelectorAll(".doc h2[id]")];
    const update = () => {
      const line = window.innerHeight * 0.3;
      let current = heads[0];
      for (const h of heads) if (h.getBoundingClientRect().top <= line) current = h;
      tocLinks.forEach((a) => a.classList.toggle("active", a.getAttribute("href") === "#" + current.id));
    };
    window.addEventListener("scroll", update, { passive: true });
    update();
  }
})();
