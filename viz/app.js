/* Yachay Tech international collaboration — temporal graph visualization (d3 v7).
 * Data: ../output/json/{red_anual,red_acumulada,metricas}.json (Phases 3–4).
 * Run from the project root:  python -m http.server 8000  → http://localhost:8000/viz/
 */
(() => {
  "use strict";

  // ---------------------------------------------------------------- constants
  const ATLAS_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json";
  const W = 1280, H = 760;
  const DUR = 950;          // transition duration (ms)
  const STEP = 1400;        // time per year while playing (ms)
  const ECU = "ECU";
  const REGIONS = ["Latin America & Caribbean", "Europe", "North America", "Asia", "Africa", "Oceania"];
  // Same hues in both themes, stepped for each surface (dark steps on dark, light steps on light).
  const PALETTES = {
    dark: {
      region: ["#3987e5", "#d95926", "#199e70", "#d55181", "#c98500", "#9085e9"],
      community: ["#3987e5", "#d95926", "#199e70", "#8a93a3", "#9085e9"],
    },
    light: {
      region: ["#2a78d6", "#eb6834", "#1baf7a", "#e87ba4", "#eda100", "#6250d6"],
      community: ["#2a78d6", "#eb6834", "#1baf7a", "#8d8b84", "#6250d6"],
    },
  };
  const REGION_COLOR = {};
  let COMMUNITY_COLOR = [];
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  // Countries without a polygon in world-atlas 110m: [lon, lat]
  const FALLBACK_LONLAT = { "702": [103.82, 1.35] };

  const state = { mode: "cumulative", view: "map", year: 2014, noMega: false, colorBy: "region", playing: false, theme: "dark" };
  try { if (localStorage.getItem("yt-theme") === "light") state.theme = "light"; } catch (e) { /* storage unavailable */ }

  function applyTheme() {
    document.documentElement.dataset.theme = state.theme;
    PALETTES[state.theme].region.forEach((c, i) => { REGION_COLOR[REGIONS[i]] = c; });
    COMMUNITY_COLOR = PALETTES[state.theme].community;
    try { localStorage.setItem("yt-theme", state.theme); } catch (e) { /* storage unavailable */ }
  }
  applyTheme();
  let DATA, METRICS, YEARS, PARTIAL, timer = null;

  const tooltip = d3.select("#tooltip");
  const fmt = d3.format(",");

  // ---------------------------------------------------------------- accessors
  const k = (base) => (state.noMega ? base + "_nm" : base);
  const nDocs = (n) => n[k("docs")];
  const nAuthors = (n) => n[k("authors")];
  const nStrength = (n) => n[k("strength")];
  const nNew = (n) => n[k("is_new")];
  const nFirst = (n) => n[k("first_year")];
  const lW = (l) => l[k("weight")];
  const lFirst = (l) => l[k("first_year")];

  function snapshot(mode = state.mode, year = state.year) {
    const s = DATA[mode].snapshots[year];
    const nodes = s.nodes.filter((n) => nDocs(n) > 0);
    const links = s.links.filter((l) => lW(l) > 0);
    return { nodes, links, byId: new Map(nodes.map((n) => [n.id, n])) };
  }

  function metric(year = state.year, mode = state.mode) {
    const m = METRICS[mode][year];
    return state.noMega ? { ...m, ...m.without_mega } : m;
  }

  function colorOf(n) {
    if (state.colorBy === "community" && state.view === "network") {
      const c = METRICS.final_communities[n.id];
      return COMMUNITY_COLOR[c] ?? css("--link-grey");
    }
    return REGION_COLOR[n.continent] ?? css("--link-grey");
  }

  // ---------------------------------------------------------------- load
  Promise.all([
    d3.json("../output/json/red_anual.json"),
    d3.json("../output/json/red_acumulada.json"),
    d3.json("../output/json/metricas.json"),
    d3.json(ATLAS_URL),
  ]).then(([anual, acum, metricas, world]) => {
    DATA = { annual: anual, cumulative: acum };
    METRICS = metricas;
    YEARS = anual.years.map(String);
    PARTIAL = String(anual.partial_year);
    state.year = YEARS[0];
    d3.select("#loading").remove();
    readHash();
    buildControls();
    Map_.init(world);
    Net.init();
    Panel.init();
    bindZoomButtons();
    render(false);
    window.addEventListener("hashchange", () => { readHash(); render(true); });
  }).catch((err) => {
    d3.select("#loading").html(
      `Could not load data.<br><small>Run <code>python -m http.server 8000</code> from the project root ` +
      `and open <code>http://localhost:8000/viz/</code>.<br>${err}</small>`);
    console.error(err);
  });

  // ---------------------------------------------------------------- hash (#mapa-acumulado-2020)
  function readHash() {
    const parts = decodeURIComponent(location.hash.replace("#", "")).toLowerCase().split("-");
    if (!parts[0]) return;
    // options not present in the hash go back to their defaults
    state.noMega = false;
    state.colorBy = "region";
    for (const p of parts) {
      if (p === "mapa" || p === "map") state.view = "map";
      else if (p === "red" || p === "network") state.view = "network";
      else if (p === "anual" || p === "annual") state.mode = "annual";
      else if (p === "acumulado" || p === "cumulative") state.mode = "cumulative";
      else if (p === "sinmega" || p === "nomega") state.noMega = true;
      else if (p === "conmega" || p === "mega") state.noMega = false;
      else if (p === "comunidad" || p === "community") state.colorBy = "community";
      else if (p === "region") state.colorBy = "region";
      else if (YEARS && YEARS.includes(p)) state.year = p;
    }
  }

  function writeHash() {
    const h = [state.view === "map" ? "mapa" : "red", state.mode === "annual" ? "anual" : "acumulado", state.year];
    if (state.noMega) h.push("sinmega");
    if (state.colorBy === "community") h.push("comunidad");
    history.replaceState(null, "", "#" + h.join("-"));
  }

  // ---------------------------------------------------------------- controls
  function buildControls() {
    d3.selectAll(".seg").each(function () {
      const key = this.dataset.key;
      d3.select(this).selectAll("button").on("click", function () {
        state[key] = this.dataset.value;
        render(true);
      });
    });
    const slider = d3.select("#year-slider")
      .attr("min", YEARS[0]).attr("max", YEARS[YEARS.length - 1])
      .on("input", function () { stop(); state.year = String(this.value); render(true); });
    d3.select("#year-ticks").selectAll("span").data(YEARS).join("span")
      .text((y) => (y === PARTIAL ? y + "*" : y))
      .classed("partial", (y) => y === PARTIAL)
      .on("click", (e, y) => { stop(); state.year = y; render(true); });
    d3.select("#play").on("click", () => (state.playing ? stop() : play()));
    d3.select("#no-mega").on("change", function () { state.noMega = this.checked; render(true); });
    window.addEventListener("keydown", (e) => {
      if (e.target.tagName === "INPUT" && e.target.type !== "checkbox") return;
      const i = YEARS.indexOf(state.year);
      if (e.code === "Space") { e.preventDefault(); state.playing ? stop() : play(); }
      else if (e.key === "ArrowRight" && i < YEARS.length - 1) { stop(); state.year = YEARS[i + 1]; render(true); }
      else if (e.key === "ArrowLeft" && i > 0) { stop(); state.year = YEARS[i - 1]; render(true); }
    });
    slider.node().value = state.year;
  }

  function play() {
    if (state.year === YEARS[YEARS.length - 1]) { state.year = YEARS[0]; render(true); }
    state.playing = true;
    d3.select("#play-icon").attr("d", "M6 4h4v16H6zM14 4h4v16h-4z");
    timer = setInterval(() => {
      const i = YEARS.indexOf(state.year);
      if (i >= YEARS.length - 1) return stop();
      state.year = YEARS[i + 1];
      render(true);
    }, STEP);
  }

  function stop() {
    state.playing = false;
    clearInterval(timer);
    d3.select("#play-icon").attr("d", "M7 4l13 8-13 8z");
  }

  function syncControls() {
    d3.selectAll(".seg").each(function () {
      const key = this.dataset.key;
      d3.select(this).selectAll("button").classed("active", function () { return this.dataset.value === state[key]; });
    });
    d3.selectAll('.seg[data-key="colorBy"] button').property("disabled", function () {
      return state.view === "map" && this.dataset.value === "community";
    });
    if (state.view === "map" && state.colorBy === "community") {
      d3.selectAll('.seg[data-key="colorBy"] button').classed("active", function () { return this.dataset.value === "region"; });
    }
    d3.select("#year-slider").property("value", state.year);
    d3.select("#year-ticks").selectAll("span").classed("active", (y) => y === state.year);
    d3.select("#no-mega").property("checked", state.noMega);
    d3.select("#year-big").text(state.year + (state.year === PARTIAL ? "*" : ""));
    d3.select("#mode-big").text(state.mode === "annual" ? "annual" : "cumulative 2014–" + state.year);
    d3.select("#map").classed("hidden", state.view !== "map");
    d3.select("#network").classed("hidden", state.view !== "network");
  }

  function render(animate) {
    applyTheme();
    syncControls();
    writeHash();
    const snap = snapshot();
    const t = animate ? DUR : 0;
    Map_.update(snap, t);
    Net.update(snap, t);
    Panel.update(t);
    Legend.update();
  }

  // ---------------------------------------------------------------- label placement
  const labelWidth = (txt) => txt.length * 7.3 + 4;
  /** Greedy: keeps labels in priority order and drops any that would overlap a kept one. */
  function placeLabels(items, boxOf) {
    const kept = [], boxes = [];
    for (const d of items) {
      const [x, y, w, h] = boxOf(d);
      if (boxes.some(([bx, by, bw, bh]) => x < bx + bw && x + w > bx && y < by + bh && y + h > by)) continue;
      kept.push(d);
      boxes.push([x, y, w, h]);
    }
    return kept;
  }

  // ---------------------------------------------------------------- tooltip helpers
  function showTip(event, html) {
    tooltip.html(html).attr("hidden", null);
    const { innerWidth: vw, innerHeight: vh } = window;
    const box = tooltip.node().getBoundingClientRect();
    let x = event.clientX + 16, y = event.clientY + 14;
    if (x + box.width > vw - 8) x = event.clientX - box.width - 16;
    if (y + box.height > vh - 8) y = event.clientY - box.height - 14;
    tooltip.style("left", x + "px").style("top", y + "px");
  }
  const hideTip = () => tooltip.attr("hidden", true);
  const row = (label, value) => `<div class="tt-row"><span>${label}</span><b>${value}</b></div>`;
  const dot = (c) => `<span class="swatch" style="background:${c}"></span>`;

  function nodeTip(n) {
    const ecu = n.id === ECU;
    const yearLabel = state.mode === "annual" ? `in ${state.year}` : `2014–${state.year}`;
    return `<div class="tt-title">${dot(ecu ? "var(--ecuador)" : colorOf(n))}${n.name}${ecu ? " (Yachay Tech)" : ""}</div>` +
      row("Region", n.continent) +
      row(ecu ? `Documents ${yearLabel}` : `Co-authored docs ${yearLabel}`, fmt(nDocs(n))) +
      row("Researchers (unique Scopus IDs)", fmt(nAuthors(n))) +
      (ecu ? "" : row("First collaboration", nFirst(n) ?? "–")) +
      row("Partner countries linked", fmt(n[k("degree")])) +
      (nNew(n) && !ecu ? `<div class="tt-row"><span>★ New partner in ${state.year}</span></div>` : "");
  }

  function linkTip(l, byId) {
    const a = byId.get(typeof l.source === "object" ? l.source.id : l.source);
    const b = byId.get(typeof l.target === "object" ? l.target.id : l.target);
    const withEcu = a.id === ECU || b.id === ECU;
    return `<div class="tt-title">${a.name} — ${b.name}</div>` +
      row("Shared documents", fmt(lW(l))) +
      row("First co-authorship", lFirst(l) ?? "–") +
      (withEcu ? "" : `<div class="tt-row"><span>Indirect link: both co-authored with Yachay Tech</span></div>`);
  }

  // ================================================================= MAP VIEW
  // Zoom/pan: the geography (sphere, countries, arcs) is scaled by the zoom transform with
  // non-scaling strokes; circles, Ecuador marker and labels are re-positioned in screen space so
  // they keep their size and simply spread apart when zooming in.
  const Map_ = (() => {
    const svg = d3.select("#map");
    let projection, path, centroid = new Map(), gGeo, gCountries, gArcs, gNodes, gLabels, gPulse, ecuPos;
    let zt = d3.zoomIdentity, current = null;
    const rScale = d3.scaleSqrt();
    const wScale = d3.scaleSqrt();
    const maxByMode = {};
    const P = (iso) => zt.apply(centroid.get(iso));
    const radius = (d) => Math.max(2.5, rScale(nDocs(d)));

    const zoom = d3.zoom().scaleExtent([1, 10]).translateExtent([[0, 0], [W, H]])
      .on("zoom", (e) => { zt = e.transform; zoomed(); })
      .on("end", () => { if (current) drawLabels(0); });

    function init(world) {
      const features = topojson.feature(world, world.objects.countries).features.filter((f) => f.id !== "010");
      projection = d3.geoNaturalEarth1().fitExtent([[20, 70], [W - 20, H - 10]], { type: "FeatureCollection", features });
      path = d3.geoPath(projection);

      // centroid of the largest polygon (avoids overseas territories pulling e.g. France off)
      for (const f of features) {
        let geom = f.geometry;
        if (geom && geom.type === "MultiPolygon") {
          const best = d3.greatest(geom.coordinates, (c) => d3.geoArea({ type: "Polygon", coordinates: c }));
          geom = { type: "Polygon", coordinates: best };
        }
        if (geom) centroid.set(f.id, path.centroid(geom));
      }
      for (const [id, ll] of Object.entries(FALLBACK_LONLAT)) if (!centroid.has(id)) centroid.set(id, projection(ll));

      gGeo = svg.append("g");
      gGeo.append("path").attr("class", "sphere").attr("d", path({ type: "Sphere" }));
      gGeo.append("path").attr("class", "graticule").attr("d", path(d3.geoGraticule10()));
      gCountries = gGeo.append("g");
      gCountries.selectAll("path").data(features, (d) => d.id).join("path")
        .attr("class", "country").attr("d", path).attr("fill", css("--land"));
      gArcs = gGeo.append("g");
      gPulse = svg.append("g");
      gNodes = svg.append("g");
      gLabels = svg.append("g");
      svg.call(zoom);

      const ecuIso = DATA.cumulative.snapshots[YEARS[0]].nodes.find((n) => n.id === ECU).iso_num;
      ecuPos = centroid.get(ecuIso);

      // fixed scales per mode so sizes are comparable across years
      for (const mode of ["annual", "cumulative"]) {
        let maxD = 1, maxW = 1;
        for (const y of YEARS) for (const n of DATA[mode].snapshots[y].nodes) if (n.id !== ECU) maxD = Math.max(maxD, n.docs);
        for (const y of YEARS) for (const l of DATA[mode].snapshots[y].links) if (l.source === ECU) maxW = Math.max(maxW, l.weight);
        maxByMode[mode] = { maxD, maxW };
      }
    }

    function arcPath(p0, p1) {
      const [x0, y0] = p0, [x1, y1] = p1;
      const mx = (x0 + x1) / 2, my = (y0 + y1) / 2;
      const dx = x1 - x0, dy = y1 - y0, dist = Math.hypot(dx, dy);
      let nx = -dy / dist, ny = dx / dist;
      if (ny > 0) { nx = -nx; ny = -ny; }       // always bend upwards
      const bend = Math.min(dist * 0.28, 170);
      return `M${x0},${y0} Q${mx + nx * bend},${my + ny * bend} ${x1},${y1}`;
    }

    function zoomed() {
      gGeo.attr("transform", zt);
      gNodes.selectAll("circle.node-circle").attr("cx", (d) => P(d.iso_num)[0]).attr("cy", (d) => P(d.iso_num)[1]);
      gNodes.selectAll("g.ecu").attr("transform", `translate(${zt.apply(ecuPos)})`);
      gPulse.selectAll("circle").remove();
      positionLabels(gLabels.selectAll("text"));
    }

    function labelBox(d) {
      if (d.id === ECU) { const [x, y] = zt.apply(ecuPos); return [x - 16 - 150, y - 8, 150, 16]; }
      const [x, y] = P(d.iso_num);
      return [x + radius(d) + 4, y - 8, labelWidth(`${d.name} ${nDocs(d)}`), 16];
    }

    function positionLabels(sel) {
      sel.attr("x", (d) => (d.id === ECU ? zt.apply(ecuPos)[0] - 16 : P(d.iso_num)[0] + radius(d) + 4))
        .attr("y", (d) => (d.id === ECU ? zt.apply(ecuPos)[1] + 5 : P(d.iso_num)[1] + 4));
    }

    // Ecuador + top partners; more labels fit as you zoom in. Off-screen labels are skipped.
    function drawLabels(t) {
      const { partners, ecuNode } = current;
      const n = Math.round(12 * Math.sqrt(zt.k)), keep = Math.round(9 * Math.sqrt(zt.k));
      const onScreen = (d) => {
        const [x, y] = d.id === ECU ? zt.apply(ecuPos) : P(d.iso_num);
        return x > 0 && x < W && y > 0 && y < H;
      };
      const cands = partners.filter(onScreen).sort((a, b) => nDocs(b) - nDocs(a)).slice(0, n);
      const labels = placeLabels((ecuNode && onScreen(ecuNode) ? [ecuNode] : []).concat(cands), labelBox).slice(0, keep);
      gLabels.selectAll("text").data(labels, (d) => d.id).join(
        (enter) => enter.append("text").attr("opacity", 0),
        (update) => update,
        (exit) => exit.call((s) => s.transition("o").duration(t * 0.5).attr("opacity", 0).remove()),
      )
        .attr("class", (d) => "map-label" + (d.id === ECU ? " ecuador" : ""))
        .attr("text-anchor", (d) => (d.id === ECU ? "end" : "start"))
        .text((d) => (d.id === ECU ? "Ecuador · Yachay Tech" : `${d.name} ${nDocs(d)}`))
        .call(positionLabels)
        .call((s) => s.transition("o").duration(t).attr("opacity", 1));
    }

    function update(snap, t) {
      const { maxD, maxW } = maxByMode[state.mode];
      rScale.domain([0, maxD]).range([0, state.mode === "annual" ? 24 : 30]);
      wScale.domain([1, maxW]).range([0.9, 11]);
      const partners = snap.nodes.filter((n) => n.id !== ECU && centroid.has(n.iso_num));
      const pById = new Map(partners.map((n) => [n.iso_num, n]));
      const ecuLinks = new Map(snap.links.filter((l) => l.source === ECU || l.target === ECU)
        .map((l) => [l.source === ECU ? l.target : l.source, l]));
      const ecuNode = snap.byId.get(ECU);
      current = { partners, ecuNode };

      // countries
      gCountries.selectAll("path").transition("fill").duration(t)
        .attr("fill", (f) => {
          if (ecuNode && f.id === ecuNode.iso_num) return css("--ecuador-country");
          const n = pById.get(f.id);
          return n ? d3.interpolateRgb(css("--land"), REGION_COLOR[n.continent])(state.theme === "light" ? 0.32 : 0.26) : css("--land");
        });
      gCountries.selectAll("path")
        .on("mousemove", (e, f) => {
          const n = pById.get(f.id) || (ecuNode && f.id === ecuNode.iso_num ? ecuNode : null);
          if (n) showTip(e, nodeTip(n)); else hideTip();
        })
        .on("mouseleave", hideTip);

      // arcs (Ecuador → partner), in map coordinates
      const arcData = partners.filter((n) => ecuLinks.has(n.id)).sort((a, b) => lW(ecuLinks.get(b.id)) - lW(ecuLinks.get(a.id)));
      gArcs.selectAll("path").data(arcData, (d) => d.id).join(
        (enter) => enter.append("path").attr("class", "arc")
          .attr("d", (d) => arcPath(ecuPos, centroid.get(d.iso_num)))
          .attr("stroke", (d) => REGION_COLOR[d.continent])
          .attr("stroke-width", (d) => wScale(lW(ecuLinks.get(d.id))))
          .attr("stroke-opacity", 0.6)
          .each(function () {
            const L = this.getTotalLength();
            d3.select(this).attr("stroke-dasharray", `${L} ${L}`).attr("stroke-dashoffset", L);
          })
          .call((s) => s.transition("draw").duration(t * 1.1).ease(d3.easeCubicOut).attr("stroke-dashoffset", 0)
            .on("end", function () { d3.select(this).attr("stroke-dasharray", null); })),
        (update) => update.call((s) => s.transition("w").duration(t)
          .attr("stroke-width", (d) => wScale(lW(ecuLinks.get(d.id)))).attr("stroke-opacity", 0.6)),
        (exit) => exit.call((s) => s.transition("w").duration(t * 0.6).attr("stroke-opacity", 0).remove()),
      )
        .attr("stroke", (d) => REGION_COLOR[d.continent])
        .on("mousemove", (e, d) => showTip(e, linkTip(ecuLinks.get(d.id), snap.byId)))
        .on("mouseleave", hideTip);

      // partner circles (largest first so small ones stay on top), in screen coordinates
      const nodes = partners.slice().sort((a, b) => nDocs(b) - nDocs(a));
      gNodes.selectAll("circle.node-circle").data(nodes, (d) => d.id).join(
        (enter) => enter.append("circle").attr("class", "node-circle")
          .attr("cx", (d) => P(d.iso_num)[0]).attr("cy", (d) => P(d.iso_num)[1])
          .attr("r", 0).attr("fill", (d) => REGION_COLOR[d.continent])
          .call((s) => s.transition("r").duration(t).attr("r", radius)),
        (update) => update.call((s) => s.transition("r").duration(t).attr("r", radius)),
        (exit) => exit.call((s) => s.transition("r").duration(t * 0.6).attr("r", 0).remove()),
      )
        .classed("is-new", (d) => nNew(d))
        .attr("fill", (d) => REGION_COLOR[d.continent])
        .order()
        .on("mousemove", (e, d) => showTip(e, nodeTip(d)))
        .on("mouseleave", hideTip);

      // Ecuador marker
      gNodes.selectAll("g.ecu").data(ecuNode ? [ecuNode] : []).join((enter) => {
        const g = enter.append("g").attr("class", "ecu");
        g.append("circle").attr("class", "ecuador-ring").attr("r", 13);
        g.append("circle").attr("class", "ecuador-mark").attr("r", 7);
        return g;
      }).attr("transform", `translate(${zt.apply(ecuPos)})`)
        .on("mousemove", (e, d) => showTip(e, nodeTip(d))).on("mouseleave", hideTip).raise();

      // pulse on new partners
      if (t > 0) {
        for (const n of nodes.filter(nNew)) {
          const [x, y] = P(n.iso_num);
          const r0 = Math.max(3, radius(n));
          gPulse.append("circle").attr("class", "pulse").attr("cx", x).attr("cy", y).attr("r", r0)
            .attr("stroke-width", 2.5).attr("opacity", 1)
            .transition().delay(t * 0.5).duration(1300).ease(d3.easeCubicOut)
            .attr("r", r0 + 26).attr("opacity", 0).attr("stroke-width", 0.5).remove();
        }
      }

      drawLabels(t);
    }

    return { init, update, rScale, wScale, svg, zoom };
  })();

  // ============================================================= NETWORK VIEW
  // Zoom/pan: node and link positions are mapped through the zoom transform, so nodes keep their
  // size (links keep their width) and the network spreads out when zooming in.
  const Net = (() => {
    const svg = d3.select("#network");
    const cx = W / 2, cy = H / 2 + 40;
    let gLinks, gNodes, gPulse, gLabels, sim, anchor = new Map(), simNodes = new Map();
    let zt = d3.zoomIdentity, curNodes = [];
    const rScale = d3.scaleSqrt();
    const wScale = d3.scaleSqrt();
    const maxByMode = {};
    const X = (d) => zt.applyX(d.x), Y = (d) => zt.applyY(d.y);

    const zoom = d3.zoom().scaleExtent([0.5, 8])
      .on("zoom", (e) => { zt = e.transform; gPulse.selectAll("circle").remove(); ticked(); })
      .on("end", () => drawLabels(0));

    function init() {
      // transparent background so the whole stage can be dragged
      svg.append("rect").attr("width", W).attr("height", H).attr("fill", "transparent");
      gLinks = svg.append("g");
      gPulse = svg.append("g");
      gNodes = svg.append("g");
      gLabels = svg.append("g");
      svg.call(zoom);

      // Global layout computed ONCE with d3-force on the final cumulative network (all countries).
      // Every snapshot reuses these anchors, so existing nodes never jump between years.
      const fin = DATA.cumulative.snapshots[YEARS[YEARS.length - 1]];
      const maxEcu = d3.max(fin.links.filter((l) => l.source === ECU), (l) => l.weight);
      const nodes = fin.nodes.map((n) => ({ id: n.id, strength: n.strength }));
      const links = fin.links.map((l) => ({ source: l.source, target: l.target, weight: l.weight }));
      const rTmp = d3.scaleSqrt().domain([0, d3.max(fin.nodes, (n) => (n.id === ECU ? 0 : n.strength))]).range([3, 26]);
      const ecu = nodes.find((n) => n.id === ECU);
      ecu.fx = cx; ecu.fy = cy;
      const layout = d3.forceSimulation(nodes)
        .randomSource(d3.randomLcg(42))
        .force("link", d3.forceLink(links).id((d) => d.id)
          .distance((l) => (l.source.id === ECU || l.target.id === ECU) ? 90 + 240 * (1 - Math.sqrt(l.weight / maxEcu)) : 120)
          .strength((l) => (l.source.id === ECU || l.target.id === ECU) ? 0.7 : 0.004))
        .force("charge", d3.forceManyBody().strength(-70))
        .force("collide", d3.forceCollide((d) => (d.id === ECU ? 28 : rTmp(d.strength) + 4)).iterations(2))
        .force("x", d3.forceX(cx).strength(0.02))
        .force("y", d3.forceY(cy).strength(0.03))
        .stop();
      for (let i = 0; i < 500; i++) layout.tick();
      // fit into the viewBox
      const xs = d3.extent(nodes, (d) => d.x), ys = d3.extent(nodes, (d) => d.y);
      const s = Math.min((W - 240) / (xs[1] - xs[0]), (H - 170) / (ys[1] - ys[0]), 1.4);
      for (const n of nodes) anchor.set(n.id, [cx + (n.x - cx) * s, cy + (n.y - cy) * s]);

      for (const mode of ["annual", "cumulative"]) {
        let maxS = 1, maxW = 1;
        for (const y of YEARS) for (const n of DATA[mode].snapshots[y].nodes) if (n.id !== ECU) maxS = Math.max(maxS, n.strength);
        for (const y of YEARS) for (const l of DATA[mode].snapshots[y].links) maxW = Math.max(maxW, l.weight);
        maxByMode[mode] = { maxS, maxW };
      }

      // live simulation: keeps nodes near their anchors and resolves overlaps as sizes change
      sim = d3.forceSimulation().randomSource(d3.randomLcg(7))
        .force("x", d3.forceX((d) => anchor.get(d.id)[0]).strength(0.35))
        .force("y", d3.forceY((d) => anchor.get(d.id)[1]).strength(0.35))
        .force("collide", d3.forceCollide((d) => d.r + 2))
        .alphaDecay(0.05)
        .on("tick", ticked)
        .stop();
    }

    const radius = (n) => (n.id === ECU ? 22 : Math.max(3, rScale(nStrength(n))));

    function positionLabels(sel) {
      sel.attr("x", (d) => X(d) + (d.id === ECU ? 0 : d.r + 4))
        .attr("y", (d) => (d.id === ECU ? Y(d) - d.r - 8 : Y(d) + 4));
    }

    function ticked() {
      gNodes.selectAll("circle.net-node").attr("cx", X).attr("cy", Y);
      gLinks.selectAll("line")
        .attr("x1", (d) => X(d.source)).attr("y1", (d) => Y(d.source))
        .attr("x2", (d) => X(d.target)).attr("y2", (d) => Y(d.target));
      positionLabels(gLabels.selectAll("text"));
    }

    // Ecuador + top partners by weighted degree; more labels fit as you zoom in.
    function drawLabels(t) {
      const onScreen = (d) => X(d) > 0 && X(d) < W && Y(d) > 0 && Y(d) < H;
      const n = Math.round(10 * Math.sqrt(Math.max(1, zt.k)));
      const top = curNodes.filter((d) => d.id !== ECU && onScreen(d)).sort((a, b) => nStrength(b) - nStrength(a)).slice(0, n);
      const labelled = placeLabels(curNodes.filter((d) => d.id === ECU && onScreen(d)).concat(top), (d) => d.id === ECU
        ? [X(d) - 80, Y(d) - d.r - 22, 160, 16]
        : [X(d) + d.r + 4, Y(d) - 8, labelWidth(d.name), 16]);
      gLabels.selectAll("text").data(labelled, (d) => d.id).join(
        (enter) => enter.append("text").attr("opacity", 0),
        (update) => update,
        (exit) => exit.call((s) => s.transition("o").duration(t * 0.5).attr("opacity", 0).remove()),
      )
        .attr("class", (d) => "net-label" + (d.id === ECU ? " ecuador" : ""))
        .attr("text-anchor", (d) => (d.id === ECU ? "middle" : "start"))
        .text((d) => (d.id === ECU ? "Ecuador · Yachay Tech" : d.name))
        .call(positionLabels)
        .call((s) => s.transition("o").duration(t).attr("opacity", 1));
    }

    function update(snap, t) {
      const { maxS, maxW } = maxByMode[state.mode];
      rScale.domain([0, maxS]).range([0, state.mode === "annual" ? 24 : 30]);
      wScale.domain([1, maxW]).range([0.6, 10]);

      // reuse node objects so positions persist between years
      const nodes = snap.nodes.map((n) => {
        let o = simNodes.get(n.id);
        if (!o) {
          const [x, y] = anchor.get(n.id) ?? [cx, cy];
          o = { id: n.id, x, y };
          simNodes.set(n.id, o);
        }
        Object.assign(o, n);
        o.r = radius(n);
        if (n.id === ECU) { o.fx = cx; o.fy = cy; }
        return o;
      });
      curNodes = nodes;
      const byId = new Map(nodes.map((n) => [n.id, n]));
      const links = snap.links.map((l) => ({ ...l, source: byId.get(l.source), target: byId.get(l.target) }))
        .sort((a, b) => (a.source.id === ECU || a.target.id === ECU) - (b.source.id === ECU || b.target.id === ECU) || lW(a) - lW(b));

      const isEcuLink = (l) => l.source.id === ECU || l.target.id === ECU;
      const partner = (l) => (l.source.id === ECU ? l.target : l.source);

      gLinks.selectAll("line").data(links, (d) => d.source.id + "-" + d.target.id).join(
        (enter) => enter.append("line").attr("class", "net-link").attr("stroke-opacity", 0)
          .attr("x1", (d) => X(d.source)).attr("y1", (d) => Y(d.source))
          .attr("x2", (d) => X(d.target)).attr("y2", (d) => Y(d.target)),
        (update) => update,
        (exit) => exit.call((s) => s.transition("o").duration(t * 0.5).attr("stroke-opacity", 0).remove()),
      )
        .attr("stroke", (d) => (isEcuLink(d) ? colorOf(partner(d)) : css("--link-grey")))
        .call((s) => s.transition("o").duration(t)
          .attr("stroke-opacity", (d) => (isEcuLink(d) ? 0.5 : state.theme === "light" ? 0.18 : 0.13))
          .attr("stroke-width", (d) => wScale(lW(d))))
        .on("mousemove", (e, d) => showTip(e, linkTip(d, byId)))
        .on("mouseleave", hideTip);

      gNodes.selectAll("circle.net-node").data(nodes, (d) => d.id).join(
        (enter) => enter.append("circle").attr("class", "net-node").attr("r", 0)
          .attr("cx", X).attr("cy", Y),
        (update) => update,
        (exit) => exit.call((s) => s.transition("r").duration(t * 0.5).attr("r", 0).remove()),
      )
        .classed("is-new", (d) => nNew(d) && d.id !== ECU)
        .call((s) => s.transition("r").duration(t).attr("r", (d) => d.r)
          .attr("fill", (d) => (d.id === ECU ? css("--ecuador") : colorOf(d))))
        .on("mousemove", (e, d) => { showTip(e, nodeTip(d)); highlight(d, links); })
        .on("mouseleave", () => { hideTip(); highlight(null); });

      // pulse for new partners
      if (t > 0 && state.view === "network") {
        for (const n of nodes.filter((d) => nNew(d) && d.id !== ECU)) {
          gPulse.append("circle").attr("class", "pulse").attr("cx", X(n)).attr("cy", Y(n)).attr("r", n.r)
            .attr("stroke-width", 2.5)
            .transition().delay(t * 0.5).duration(1300).ease(d3.easeCubicOut)
            .attr("r", n.r + 24).attr("opacity", 0).remove();
        }
      }

      sim.nodes(nodes);
      if (t > 0) sim.alpha(0.35).restart();
      else { sim.alpha(0.35); for (let i = 0; i < 80; i++) sim.tick(); ticked(); }
      drawLabels(t);
    }

    function highlight(n, links) {
      if (!n) {
        gNodes.selectAll("circle.net-node").classed("dim", false);
        gLinks.selectAll("line").classed("dim", false);
        gLabels.selectAll("text").classed("dim", false);
        return;
      }
      const nb = new Set([n.id]);
      for (const l of links) {
        if (l.source.id === n.id) nb.add(l.target.id);
        if (l.target.id === n.id) nb.add(l.source.id);
      }
      gNodes.selectAll("circle.net-node").classed("dim", (d) => !nb.has(d.id));
      gLinks.selectAll("line").classed("dim", (d) => d.source.id !== n.id && d.target.id !== n.id);
      gLabels.selectAll("text").classed("dim", (d) => !nb.has(d.id));
    }

    return { init, update, rScale, wScale, svg, zoom };
  })();

  // ---------------------------------------------------------------- zoom buttons
  const activeView = () => (state.view === "map" ? Map_ : Net);
  function bindZoomButtons() {
    d3.select("#zoom-in").on("click", () => activeView().svg.transition().duration(450).call(activeView().zoom.scaleBy, 1.6));
    d3.select("#zoom-out").on("click", () => activeView().svg.transition().duration(450).call(activeView().zoom.scaleBy, 1 / 1.6));
    d3.select("#zoom-reset").on("click", () => activeView().svg.transition().duration(600).call(activeView().zoom.transform, d3.zoomIdentity));
  }

  // ============================================================== LEGEND
  const Legend = (() => {
    function update() {
      const el = d3.select("#legend").html("");
      const byCommunity = state.view === "network" && state.colorBy === "community";

      // color
      const c = el.append("div");
      if (byCommunity) {
        c.append("h4").text("Louvain community (cumulative 2026)");
        const n = d3.max(Object.values(METRICS.final_communities)) + 1;
        const items = c.append("div").attr("class", "items");
        const names = {};
        const fin = DATA.cumulative.snapshots[YEARS[YEARS.length - 1]];
        for (const node of fin.nodes.slice().sort((a, b) => b.strength - a.strength)) {
          const cc = METRICS.final_communities[node.id];
          (names[cc] ||= []).length < 3 && node.id !== ECU && names[cc].push(node.name);
        }
        for (let i = 0; i < n; i++) {
          const it = items.append("div").attr("class", "item");
          it.append("span").attr("class", "swatch").style("background", COMMUNITY_COLOR[i]);
          it.append("span").text(`${i + 1}: ${(names[i] || []).join(", ")}…`);
        }
      } else {
        c.append("h4").text("Region of partner country");
        const items = c.append("div").attr("class", "items");
        for (const r of REGIONS) {
          const it = items.append("div").attr("class", "item");
          it.append("span").attr("class", "swatch").style("background", REGION_COLOR[r]);
          it.append("span").text(r);
        }
        const it = items.append("div").attr("class", "item");
        it.append("span").attr("class", "swatch").style("background", "var(--ecuador)");
        it.append("span").text("Ecuador (Yachay Tech)");
      }

      // size
      const s = el.append("div");
      const isMap = state.view === "map";
      s.append("h4").text(isMap ? "Co-authored documents" : "Weighted degree");
      const scale = isMap ? Map_.rScale : Net.rScale;
      const max = scale.domain()[1];
      const vals = [Math.round(max / 10), Math.round(max / 3), Math.round(max)].filter((v, i, a) => v > 0 && a.indexOf(v) === i);
      const rMax = scale(max);
      const svg = s.append("svg").attr("width", rMax * 2 + 70).attr("height", rMax * 2 + 18)
        .append("g").attr("transform", "translate(0,12)");
      for (const v of vals) {
        const r = scale(v);
        svg.append("circle").attr("cx", rMax + 2).attr("cy", rMax * 2 + 2 - r).attr("r", r)
          .attr("fill", "none").style("stroke", "var(--muted)");
        svg.append("line").attr("x1", rMax + 2).attr("x2", rMax * 2 + 12).attr("y1", rMax * 2 + 2 - 2 * r).attr("y2", rMax * 2 + 2 - 2 * r)
          .style("stroke", "var(--line)").attr("stroke-dasharray", "2 2");
        svg.append("text").attr("x", rMax * 2 + 15).attr("y", rMax * 2 + 6 - 2 * r).text(fmt(v));
      }

      // width + new
      const w = el.append("div");
      w.append("h4").text(isMap ? "Arc width = docs with Ecuador" : "Link width = shared docs");
      const ws = isMap ? Map_.wScale : Net.wScale;
      const wmax = ws.domain()[1];
      const wsvg = w.append("svg").attr("width", 150).attr("height", 62);
      [1, Math.round(wmax / 4), Math.round(wmax)].forEach((v, i) => {
        wsvg.append("line").attr("x1", 0).attr("x2", 60).attr("y1", 8 + i * 18).attr("y2", 8 + i * 18)
          .style("stroke", "var(--ink-2)").attr("stroke-width", ws(v)).attr("stroke-linecap", "round");
        wsvg.append("text").attr("x", 70).attr("y", 12 + i * 18).text(fmt(v));
      });
      const nw = w.append("div").attr("class", "item").style("margin-top", "10px");
      nw.append("span").attr("class", "swatch").style("border", "2.5px solid var(--accent)").style("background", "transparent");
      nw.append("span").text("New partner this year (pulse)");
      if (!isMap) {
        w.append("div").attr("class", "note").text("Faint grey links: partner–partner co-authorships (both also co-authored with Yachay Tech).");
      }
    }
    return { update };
  })();

  // =============================================================== PANEL
  const Panel = (() => {
    const SPARKS = [
      { key: "partners", title: "Partner countries", f: d3.format("d"), axisF: d3.format("d"), hint: "" },
      { key: "pct_international", title: "% international documents", f: (v) => v.toFixed(1) + "%", axisF: (v) => Math.round(v) + "%", hint: "" },
      { key: "shannon", title: "Shannon diversity", f: d3.format(".2f"), axisF: d3.format(".1f"), hint: "higher = more diverse" },
      { key: "hhi", title: "HHI concentration", f: d3.format(".3f"), axisF: d3.format(".2f"), hint: "higher = more concentrated" },
    ];
    const SW = 228, SH = 62, M = { l: 34, r: 8, t: 6, b: 16 };

    function init() {
      const box = d3.select("#sparks").selectAll(".spark").data(SPARKS).join("div").attr("class", "spark");
      const head = box.append("div").attr("class", "spark-head");
      head.append("span").attr("class", "spark-title").text((d) => d.title);
      head.append("span").attr("class", "spark-value");
      box.append("div").attr("class", "spark-hint").text((d) => d.hint || " ");
      box.append("svg").attr("viewBox", `0 0 ${SW} ${SH}`);
    }

    function series(key) {
      return YEARS.map((y) => ({ year: +y, value: metric(y)[key] ?? 0 }));
    }

    function update(t) {
      const m = metric();
      const prevYear = YEARS[YEARS.indexOf(state.year) - 1];
      const prev = prevYear ? metric(prevYear) : null;

      d3.select("#panel-year").text(state.year + (state.year === PARTIAL ? "*" : ""));
      d3.select("#panel-sub").text(
        `${state.mode === "annual" ? "Annual snapshot" : "Cumulative since 2014"} · ${fmt(m.documents)} documents` +
        (state.noMega ? " · mega-collaborations excluded" : ""));
      d3.select("#partial-badge").attr("hidden", state.year === PARTIAL ? null : true);

      const delta = prev ? m.partners - prev.partners : null;
      d3.select("#c-partners").text(m.partners);
      d3.select("#c-partners-note").html(delta === null ? "first year"
        : `<span class="${delta >= 0 ? "delta-up" : "delta-down"}">${delta >= 0 ? "▲" : "▼"} ${Math.abs(delta)}</span> vs ${prevYear}`);
      d3.select("#c-continents").text(m.continents);
      d3.select("#c-intl").text(m.pct_international.toFixed(1) + "%");
      d3.select("#c-intl-note").text(`${fmt(m.international_docs)} of ${fmt(m.documents)} documents`);
      const snap = snapshot();
      const newOnes = snap.nodes.filter((n) => n.id !== ECU && nNew(n)).map((n) => n.name).sort();
      d3.select("#c-new").text(newOnes.length);
      d3.select("#c-new-note").text(newOnes.length ? newOnes.join(", ") : "none").attr("title", newOnes.join(", "));

      // sparklines
      d3.selectAll(".spark").each(function (spec) {
        const data = series(spec.key);
        const root = d3.select(this);
        const cur = data.find((d) => String(d.year) === state.year);
        root.select(".spark-value").text(spec.f(cur.value));
        const svg = root.select("svg");
        const x = d3.scaleLinear().domain(d3.extent(data, (d) => d.year)).range([M.l, SW - M.r]);
        const ext = d3.extent(data, (d) => d.value);
        const pad = (ext[1] - ext[0]) * 0.12 || 1;
        const y = d3.scaleLinear().domain([Math.max(0, ext[0] - pad), ext[1] + pad]).range([SH - M.b, M.t]);
        const full = data.filter((d) => String(d.year) !== PARTIAL);
        const part = data.filter((d) => String(d.year) >= String(+PARTIAL - 1));

        svg.selectAll(".axis").data([0]).join("g").attr("class", "axis")
          .attr("transform", `translate(${M.l - 4},0)`)
          .call(d3.axisLeft(y).tickValues(ext).tickSize(0).tickFormat(spec.axisF))
          .call((g) => g.select(".domain").remove());
        svg.selectAll(".xlab").data([data[0], data[data.length - 1]]).join("text").attr("class", "xlab")
          .attr("x", (d) => x(d.year)).attr("y", SH - 2).attr("text-anchor", (d, i) => (i ? "end" : "start"))
          .style("fill", "var(--muted)").attr("font-size", 10).text((d) => d.year);
        const line = d3.line().x((d) => x(d.year)).y((d) => y(d.value));
        svg.selectAll(".line").data([full]).join("path").attr("class", "line").transition().duration(t).attr("d", line);
        svg.selectAll(".line-partial").data([part]).join("path").attr("class", "line-partial").transition().duration(t).attr("d", line);
        svg.selectAll(".pt").data(data).join("circle")
          .attr("class", (d) => "pt" + (String(d.year) === PARTIAL ? " partial" : ""))
          .attr("r", 2.2).transition().duration(t).attr("cx", (d) => x(d.year)).attr("cy", (d) => y(d.value));
        svg.selectAll(".cur-line").data([cur]).join("line").attr("class", "cur-line")
          .transition().duration(t / 2).attr("x1", (d) => x(d.year)).attr("x2", (d) => x(d.year)).attr("y1", M.t).attr("y2", SH - M.b);
        svg.selectAll(".cur-pt").data([cur]).join("circle").attr("class", "cur-pt").attr("r", 4.5)
          .transition().duration(t / 2).attr("cx", (d) => x(d.year)).attr("cy", (d) => y(d.value));

        // hover + click-to-select
        const step = x(data[1].year) - x(data[0].year);
        svg.selectAll(".hit").data(data).join("rect").attr("class", "hit")
          .attr("x", (d) => x(d.year) - step / 2).attr("width", step).attr("y", 0).attr("height", SH)
          .on("mousemove", (e, d) => showTip(e, `<div class="tt-title">${d.year}${String(d.year) === PARTIAL ? " (partial)" : ""}</div>` +
            row(spec.title, spec.f(d.value)) + `<div class="tt-row"><span>Click to jump to this year</span></div>`))
          .on("mouseleave", hideTip)
          .on("click", (e, d) => { stop(); state.year = String(d.year); render(true); });
      });

      // top 5
      const top = (m.top10 || []).slice(0, 5);
      const max = d3.max(top, (d) => d.weight) || 1;
      d3.select("#top-sub").text(state.mode === "annual" ? `co-authored documents with Ecuador in ${state.year}` : `co-authored documents with Ecuador, 2014–${state.year}`);
      const li = d3.select("#top5").selectAll("li").data(top, (d) => d.iso3).join((enter) => {
        const l = enter.append("li");
        l.append("span").attr("class", "rank");
        const nm = l.append("span").attr("class", "name");
        nm.append("span").attr("class", "nm");
        nm.append("small");
        l.append("div").attr("class", "bar-bg").append("div").attr("class", "bar").style("width", "0%");
        l.append("span").attr("class", "val");
        return l;
      });
      li.order();
      li.select(".rank").text((d, i) => i + 1);
      li.select(".nm").text((d) => d.name);
      li.select("small").text((d) => `${d.continent} · ${(d.share * 100).toFixed(1)}%`);
      li.select(".bar").style("background", (d) => REGION_COLOR[d.continent]).style("width", (d) => (100 * d.weight / max) + "%");
      li.select(".val").text((d) => fmt(d.weight));
    }

    return { init, update };
  })();
})();
