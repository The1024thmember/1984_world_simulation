const $ = (id) => document.getElementById(id);

function mulberry32(seed) {
  let t = seed >>> 0;
  return function () {
    t += 0x6D2B79F5;
    let r = Math.imul(t ^ (t >>> 15), t | 1);
    r ^= r + Math.imul(r ^ (r >>> 7), r | 61);
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}

function randBetween(rng, min, max) {
  return min + (max - min) * rng();
}

function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v));
}

const CAUSES = ["Hunger", "BombAttack", "Execution", "Murder"];
const ROLES = ["InnerParty", "OuterParty", "Proles"];
const MINISTRIES = ["Truth", "Love", "Peace", "Plenty"];

const COLOR_MAP = {
  InnerParty: { Hunger: "#ff8a80", BombAttack: "#ff5252", Execution: "#d50000", Murder: "#ff1744" },
  OuterParty: { Hunger: "#80bfff", BombAttack: "#42a5f5", Execution: "#1565c0", Murder: "#1e88e5" },
  Proles: { Hunger: "#81c784", BombAttack: "#4caf50", Execution: "#2e7d32", Murder: "#43a047" },
};

const ROLE_COLOR = { InnerParty: "#d62728", OuterParty: "#1f77b4", Proles: "#2ca02c" };
const CAUSE_COLOR = { Hunger: "#ffb300", BombAttack: "#ef5350", Execution: "#8e24aa", Murder: "#26c6da" };
const ROLE_PRIORITY = { InnerParty: 2, OuterParty: 1, Proles: 0 };

const MINISTRY_ICON = { Truth: "✝", Love: "♥", Peace: "☮", Plenty: "⚒", Party: "★" };

class Simulation {
  constructor(params) {
    this.params = params;
    this.rng = mulberry32(params.seed);
    this.stepCount = 0;
    this.agents = [];
    this.series = [];
    this.deathSeries = [];
    this.stepDeaths = this.initDeathCounts();
    this.totalDeathsByRole = { InnerParty: 0, OuterParty: 0, Proles: 0 };
    this.totalDeathsByCause = { Hunger: 0, BombAttack: 0, Execution: 0, Murder: 0 };
    this.totalDeathsByRoleMinistry = { InnerParty: {}, OuterParty: {}, Proles: {} };
    this.init();
  }

  init() {
    const p = this.params;
    const total = p.population;
    const nInner = Math.max(1, Math.round(total * p.innerPct));
    const nOuter = Math.max(1, Math.round(total * p.outerPct));
    const nProle = Math.max(1, total - nInner - nOuter);

    const spots = [];
    for (let x = 0; x < p.width; x++) {
      for (let y = 0; y < p.height; y++) spots.push({ x, y });
    }
    for (let i = spots.length - 1; i > 0; i--) {
      const j = Math.floor(this.rng() * (i + 1));
      [spots[i], spots[j]] = [spots[j], spots[i]];
    }

    const outerWeights = { Love: p.lovePct, Truth: p.truthPct, Peace: p.peacePct, Plenty: p.plentyPct };
    const proleWeights = { Peace: p.prolePeacePct, Plenty: 100 - p.prolePeacePct };

    const pickWeighted = (weights) => {
      const keys = Object.keys(weights);
      const vals = keys.map(k => Math.max(0, weights[k]));
      const sum = vals.reduce((a, b) => a + b, 0);
      if (sum <= 0) return keys[Math.floor(this.rng() * keys.length)];
      let r = this.rng() * sum;
      for (let i = 0; i < keys.length; i++) {
        r -= vals[i];
        if (r <= 0) return keys[i];
      }
      return keys[0];
    };

    const makeAgent = (type) => {
      const spot = spots.pop() || { x: 0, y: 0 };
      let ministry = null;
      if (type === "OuterParty") ministry = pickWeighted(outerWeights);
      if (type === "Proles") ministry = pickWeighted(proleWeights);
      if (type === "InnerParty") ministry = "Party";
      return {
        type,
        ministry,
        x: spot.x,
        y: spot.y,
        alive: true,
        rebel: false,
        rebelAction: null,
        loyalty: type === "InnerParty" ? null : 100,
        foodStock: randBetween(this.rng, 1, 3),
        foodCRate: randBetween(this.rng, p.foodCMin, p.foodCMax),
        foodPRate: type === "Proles" ? randBetween(this.rng, p.foodPMin, p.foodPMax) : 0,
        weaponPRate: type === "Proles" ? randBetween(this.rng, p.weaponPMin, p.weaponPMax) : 0,
        stress: 0,
      };
    };

    this.agents = [];
    for (let i = 0; i < nInner; i++) this.agents.push(makeAgent("InnerParty"));
    for (let i = 0; i < nOuter; i++) this.agents.push(makeAgent("OuterParty"));
    for (let i = 0; i < nProle; i++) this.agents.push(makeAgent("Proles"));

    this.series = [];
    this.deathSeries = [];
    this.stepCount = 0;
    this.stepDeaths = this.initDeathCounts();
    this.totalDeathsByRole = { InnerParty: 0, OuterParty: 0, Proles: 0 };
    this.totalDeathsByCause = { Hunger: 0, BombAttack: 0, Execution: 0, Murder: 0 };
    this.totalDeathsByRoleMinistry = { InnerParty: {}, OuterParty: {}, Proles: {} };
  }

  initDeathCounts() {
    const counts = {};
    for (const role of ROLES) {
      counts[role] = {};
      for (const cause of CAUSES) counts[role][cause] = 0;
    }
    return counts;
  }

  recordDeath(agent, cause) {
    if (!agent || !agent.alive) return;
    agent.alive = false;
    this.stepDeaths[agent.type][cause] += 1;
    this.totalDeathsByRole[agent.type] += 1;
    this.totalDeathsByCause[cause] += 1;
    const minKey = agent.ministry || "Party";
    if (!this.totalDeathsByRoleMinistry[agent.type][minKey]) {
      this.totalDeathsByRoleMinistry[agent.type][minKey] = 0;
    }
    this.totalDeathsByRoleMinistry[agent.type][minKey] += 1;
  }

  getNeighbors(agent, range = 1) {
    const list = [];
    for (const other of this.agents) {
      if (!other.alive || other === agent) continue;
      const dx = agent.x - other.x;
      const dy = agent.y - other.y;
      if (dx * dx + dy * dy <= range * range) list.push(other);
    }
    return list;
  }

  step() {
    const p = this.params;
    this.stepCount += 1;
    this.stepDeaths = this.initDeathCounts();

    for (const a of this.agents) {
      if (!a.alive || a.type === "InnerParty") continue;
      a.rebel = a.loyalty < 50;
    }

    for (const a of this.agents) {
      if (!a.alive || !a.rebel) {
        a.rebelAction = null;
        continue;
      }
      if (a.type === "OuterParty") {
        const r = this.rng();
        a.rebelAction = r < 0.1 ? "KillProle" : r < 0.3 ? "KillOuter" : "Misfunction";
      } else if (a.type === "Proles") {
        const r = this.rng();
        a.rebelAction = r < 0.4 ? "KillProle" : r < 0.5 ? "KillOuter" : "Misfunction";
      }
    }

    let totalFood = 0;
    for (const a of this.agents) {
      if (a.alive && a.type === "Proles") {
        totalFood += a.foodPRate * (a.rebelAction === "Misfunction" ? 0.1 : 1);
      }
    }

    const outerMis = this.agents.filter(a => a.alive && a.type === "OuterParty" && a.rebelAction === "Misfunction").length;
    const efficiency = Math.max(0.2, 1 - outerMis * 0.05);
    totalFood *= efficiency;

    const living = this.agents.filter(a => a.alive);
    const foodAvailable = totalFood * (1 - p.defenseSpend);
    let totalWeight = 0;
    const weights = new Map();
    for (const a of living) {
      const base = 1 + (ROLE_PRIORITY[a.type] * p.rationBias);
      const loyaltyFactor = a.type === "InnerParty" ? 1 : (0.5 + (a.loyalty / 200));
      const rebelPenalty = a.rebel ? 0.7 : 1;
      const weight = Math.max(0.1, base * loyaltyFactor * rebelPenalty);
      weights.set(a, weight);
      totalWeight += weight;
    }
    for (const a of living) {
      const portion = totalWeight > 0 ? (weights.get(a) / totalWeight) : (1 / living.length);
      a.foodStock += foodAvailable * portion;
    }

    let weapons = 0;
    for (const a of this.agents) {
      if (a.alive && a.type === "Proles") {
        weapons += a.weaponPRate * (a.rebelAction === "Misfunction" ? 0.1 : 1);
      }
    }
    weapons += totalFood * p.defenseSpend;

    if (this.rng() < p.bombFreq) {
      const cx = Math.floor(this.rng() * p.width);
      const cy = Math.floor(this.rng() * p.height);
      const radius = Math.max(1, Math.floor(randBetween(this.rng, 1, p.bombSize + 1)));
      const intensity = Math.max(1, Math.floor(randBetween(this.rng, 1, p.bombIntensity + 1)));

      let precision = 0;
      const peaceOuter = this.agents.filter(a => a.alive && a.type === "OuterParty" && a.ministry === "Peace");
      for (const a of peaceOuter) {
        if (a.rebelAction !== "Misfunction") precision += 0.08;
      }
      precision = clamp(precision, 0, 1);
      const predictedRadius = Math.max(1, Math.floor(radius * precision));

      for (const a of living) {
        const dx = a.x - cx;
        const dy = a.y - cy;
        const dist = dx * dx + dy * dy;
        if (dist <= radius * radius) {
          if (weapons >= intensity && this.rng() < 0.6 && dist <= predictedRadius * predictedRadius) {
            weapons -= intensity;
            a.stress += 6;
          } else {
            this.recordDeath(a, "BombAttack");
          }
        }
      }
    }

    for (const a of this.agents) {
      if (!a.alive || a.type === "InnerParty") continue;
      if (a.foodStock < a.foodCRate) {
        this.recordDeath(a, "Hunger");
      } else {
        a.foodStock -= a.foodCRate;
        const hunger = clamp(1 - (a.foodStock / Math.max(1, a.foodCRate)) / 3, 0, 1);
        a.stress += hunger * 10;
      }
    }

    for (const a of this.agents) {
      if (!a.alive || !a.rebel) continue;
      const neighbors = this.getNeighbors(a, 1);
      for (const n of neighbors) {
        if (n.type === "OuterParty" || n.type === "Proles") {
          const loyaltyFactor = (100 - n.loyalty) / 100;
          const alpha = a.type === "OuterParty" ? 5 : 1;
          const spreadProb = 1 - Math.exp(-alpha * loyaltyFactor);
          if (this.rng() < spreadProb) {
            n.loyalty = clamp(n.loyalty - (a.type === "OuterParty" ? 20 : 10), 0, 100);
          }
        }
      }
    }

    for (const a of this.agents) {
      if (a.alive && (a.type === "OuterParty" || a.type === "Proles")) {
        const decay = a.ministry === "Truth" ? p.truthBoost : p.truthBoost * 0.3;
        a.stress = clamp(a.stress - decay, 0, 100);
        const perceived = clamp(100 - a.stress, 0, 100);
        a.loyalty = clamp(a.loyalty * 0.7 + perceived * 0.3, 0, 100);
      }
    }

    const rebels = this.agents.filter(a => a.alive && a.rebel);
    const toProcess = Math.min(Math.floor(rebels.length / 2), 5);
    for (let i = 0; i < toProcess; i++) {
      const target = rebels[Math.floor(this.rng() * rebels.length)];
      if (!target) continue;
      if (target.type === "OuterParty") {
        if (this.rng() < p.loveImpact) this.recordDeath(target, "Execution");
        else target.rebel = false;
      } else if (target.type === "Proles") {
        if (this.rng() < p.loveImpact) this.recordDeath(target, "Execution");
      }
    }

    for (const a of this.agents) {
      if (!a.alive || !a.rebelAction) continue;
      if (a.rebelAction === "KillOuter") {
        const candidates = this.agents.filter(x => x.alive && x.type === "OuterParty" && x !== a);
        const victim = candidates[Math.floor(this.rng() * Math.max(1, candidates.length))];
        if (victim) this.recordDeath(victim, "Murder");
      }
      if (a.rebelAction === "KillProle") {
        const candidates = this.agents.filter(x => x.alive && x.type === "Proles" && x !== a);
        const victim = candidates[Math.floor(this.rng() * Math.max(1, candidates.length))];
        if (victim) this.recordDeath(victim, "Murder");
      }
    }

    this.recordSeries();
  }

  recordSeries() {
    const alive = this.agents.filter(a => a.alive);
    const rebels = alive.filter(a => a.rebel && a.type !== "InnerParty");
    const outer = alive.filter(a => a.type === "OuterParty");
    const proles = alive.filter(a => a.type === "Proles");
    const avgLoyalty = (list) => list.length ? list.reduce((s, a) => s + a.loyalty, 0) / list.length : 0;
    this.series.push({
      step: this.stepCount,
      population: alive.length,
      rebels: rebels.length,
      outer: outer.length,
      proles: proles.length,
      inner: alive.filter(a => a.type === "InnerParty").length,
      outerLoyalty: avgLoyalty(outer),
      proleLoyalty: avgLoyalty(proles),
    });
    const snapshot = this.stepDeaths ? JSON.parse(JSON.stringify(this.stepDeaths)) : this.initDeathCounts();
    this.deathSeries.push({ step: this.stepCount, counts: snapshot });
  }
}

const grid = $("grid");
const line = $("line");
const pieRole = $("pieRole");
const pieCause = $("pieCause");
const gctx = grid.getContext("2d");
const lctx = line.getContext("2d");
const prctx = pieRole.getContext("2d");
const pcctx = pieCause.getContext("2d");
const deathLegend = $("deathLegend");
const roleLegend = $("roleLegend");
const causeLegend = $("causeLegend");

let sim = null;
let timer = null;
let pieRenderInterval = 10;

function getParams() {
  const innerPct = parseFloat($("innerPct").value) / 100;
  const outerPct = parseFloat($("outerPct").value) / 100;
  const prolePct = parseFloat($("prolePct").value) / 100;
  return {
    steps: parseInt($("steps").value, 10),
    seed: parseInt($("seed").value, 10),
    width: parseInt($("width").value, 10),
    height: parseInt($("height").value, 10),
    population: parseInt($("population").value, 10),
    innerPct,
    outerPct,
    prolePct,
    bombFreq: parseFloat($("bombFreq").value),
    bombSize: parseInt($("bombSize").value, 10),
    bombIntensity: parseInt($("bombIntensity").value, 10),
    foodCMin: parseFloat($("foodCMin").value),
    foodCMax: parseFloat($("foodCMax").value),
    foodPMin: parseFloat($("foodPMin").value),
    foodPMax: parseFloat($("foodPMax").value),
    weaponPMin: parseFloat($("weaponPMin").value),
    weaponPMax: parseFloat($("weaponPMax").value),
    lovePct: parseFloat($("lovePct").value),
    truthPct: parseFloat($("truthPct").value),
    peacePct: parseFloat($("peacePct").value),
    plentyPct: parseFloat($("plentyPct").value),
    prolePeacePct: parseFloat($("prolePeacePct").value),
    truthBoost: parseFloat($("truthBoost").value),
    loveImpact: parseFloat($("loveImpact").value),
    rationBias: parseFloat($("rationBias").value),
    defenseSpend: parseFloat($("defenseSpend").value),
  };
}

function setStatus(msg) {
  $("status").textContent = msg;
}

function buildLegend() {
  deathLegend.innerHTML = "";
  for (const role of ROLES) {
    for (const cause of CAUSES) {
      const item = document.createElement("span");
      item.className = "legend-item";
      const swatch = document.createElement("span");
      swatch.className = "swatch";
      swatch.style.background = COLOR_MAP[role][cause];
      const label = document.createElement("span");
      label.textContent = `${role} - ${cause}`;
      item.appendChild(swatch);
      item.appendChild(label);
      deathLegend.appendChild(item);
    }
  }
}

function initSim() {
  const params = getParams();
  const sum = params.innerPct + params.outerPct + params.prolePct;
  if (Math.abs(sum - 1) > 0.01) {
    setStatus("Percentages must sum to 100% (±1%).");
    return;
  }
  const outerSum = params.lovePct + params.truthPct + params.peacePct + params.plentyPct;
  if (outerSum <= 0) {
    setStatus("Outer ministry percentages must sum to > 0.");
    return;
  }
  pieRenderInterval = Math.max(1, Math.floor(params.steps * 0.1));
  sim = new Simulation(params);
  sim.recordSeries();
  buildLegend();
  draw();
  drawPies(true);
  setStatus("Initialized.");
}

function draw() {
  if (!sim) return;
  drawGrid();
  drawLine();
}

function drawGrid() {
  const p = sim.params;
  const cell = Math.floor(Math.min(grid.width / p.width, grid.height / p.height));
  gctx.clearRect(0, 0, grid.width, grid.height);
  gctx.fillStyle = "#0a1016";
  gctx.fillRect(0, 0, grid.width, grid.height);

  for (let i = 0; i <= p.width; i++) {
    gctx.strokeStyle = "#131b25";
    gctx.beginPath();
    gctx.moveTo(i * cell, 0);
    gctx.lineTo(i * cell, p.height * cell);
    gctx.stroke();
  }
  for (let j = 0; j <= p.height; j++) {
    gctx.strokeStyle = "#131b25";
    gctx.beginPath();
    gctx.moveTo(0, j * cell);
    gctx.lineTo(p.width * cell, j * cell);
    gctx.stroke();
  }

  gctx.textAlign = "center";
  gctx.textBaseline = "middle";
  gctx.font = `${Math.max(8, cell * 0.4)}px serif`;

  for (const a of sim.agents) {
    if (!a.alive) continue;
    const x = a.x * cell + cell / 2;
    const y = a.y * cell + cell / 2;
    gctx.beginPath();
    gctx.fillStyle = a.type === "InnerParty" ? "#d62728" : a.type === "OuterParty" ? "#1f77b4" : "#2ca02c";
    gctx.arc(x, y, cell * 0.35, 0, Math.PI * 2);
    gctx.fill();
    if (a.rebel) {
      gctx.strokeStyle = "#ffcc00";
      gctx.lineWidth = 2;
      gctx.stroke();
    }
    if (a.ministry) {
      gctx.fillStyle = "#f1f1f1";
      gctx.fillText(MINISTRY_ICON[a.ministry], x, y);
    }
  }
}

function drawLine() {
  const series = sim.series;
  if (!series.length) return;
  const w = line.width;
  const h = line.height;
  lctx.clearRect(0, 0, w, h);
  lctx.fillStyle = "#0a1016";
  lctx.fillRect(0, 0, w, h);

  const padding = 32;
  const maxStep = Math.max(...series.map(s => s.step));
  const maxVal = Math.max(...series.map(s => s.population), 1);

  const xScale = (step) => padding + (step / maxStep) * (w - padding * 2);
  const yScale = (val) => h - padding - (val / maxVal) * (h - padding * 2);

  lctx.strokeStyle = "#233040";
  lctx.beginPath();
  lctx.moveTo(padding, padding);
  lctx.lineTo(padding, h - padding);
  lctx.lineTo(w - padding, h - padding);
  lctx.stroke();

  function drawLineSeries(values, color, width = 2) {
    lctx.strokeStyle = color;
    lctx.lineWidth = width;
    lctx.beginPath();
    values.forEach((v, i) => {
      const x = xScale(series[i].step);
      const y = yScale(v);
      if (i === 0) lctx.moveTo(x, y);
      else lctx.lineTo(x, y);
    });
    lctx.stroke();
    lctx.lineWidth = 1;
  }

  drawLineSeries(series.map(s => s.population), "#1f77b4");
  drawLineSeries(series.map(s => s.rebels), "#ff7f0e");

  lctx.fillStyle = "#1f77b4";
  lctx.fillText("Population", padding + 10, padding - 8);
  lctx.fillStyle = "#ff7f0e";
  lctx.fillText("Rebels", padding + 100, padding - 8);
}

function drawPies(force = false) {
  if (!sim) return;
  if (!force && sim.stepCount % pieRenderInterval !== 0 && sim.stepCount !== sim.params.steps) return;
  drawRolePie();
  drawCausePie();
}

function drawRolePie() {
  const ctx = prctx;
  const w = pieRole.width;
  const h = pieRole.height;
  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = "#0a1016";
  ctx.fillRect(0, 0, w, h);

  const total = Object.values(sim.totalDeathsByRole).reduce((a, b) => a + b, 0) || 1;
  let start = -Math.PI / 2;

  for (const role of ROLES) {
    const val = sim.totalDeathsByRole[role];
    const angle = (val / total) * Math.PI * 2;
    ctx.beginPath();
    ctx.moveTo(w / 2, h / 2);
    ctx.fillStyle = ROLE_COLOR[role];
    ctx.arc(w / 2, h / 2, Math.min(w, h) / 2 - 6, start, start + angle);
    ctx.fill();
    start += angle;
  }

  roleLegend.innerHTML = "";
  for (const role of ROLES) {
    const val = sim.totalDeathsByRole[role];
    const pct = ((val / total) * 100).toFixed(1);
    const item = document.createElement("span");
    item.className = "legend-item";
    const swatch = document.createElement("span");
    swatch.className = "swatch";
    swatch.style.background = ROLE_COLOR[role];
    const minIcons = Object.keys(sim.totalDeathsByRoleMinistry[role] || {});
    const iconText = minIcons.length ? minIcons.map(m => MINISTRY_ICON[m] || "?").join(" ") : "";
    item.appendChild(swatch);
    item.appendChild(document.createTextNode(`${role} ${iconText} (${pct}%)`));
    roleLegend.appendChild(item);
  }
}

function drawCausePie() {
  const ctx = pcctx;
  const w = pieCause.width;
  const h = pieCause.height;
  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = "#0a1016";
  ctx.fillRect(0, 0, w, h);

  const total = Object.values(sim.totalDeathsByCause).reduce((a, b) => a + b, 0) || 1;
  let start = -Math.PI / 2;

  for (const cause of CAUSES) {
    const val = sim.totalDeathsByCause[cause];
    const angle = (val / total) * Math.PI * 2;
    ctx.beginPath();
    ctx.moveTo(w / 2, h / 2);
    ctx.fillStyle = CAUSE_COLOR[cause];
    ctx.arc(w / 2, h / 2, Math.min(w, h) / 2 - 6, start, start + angle);
    ctx.fill();
    start += angle;
  }

  causeLegend.innerHTML = "";
  for (const cause of CAUSES) {
    const val = sim.totalDeathsByCause[cause];
    const pct = ((val / total) * 100).toFixed(1);
    const item = document.createElement("span");
    item.className = "legend-item";
    const swatch = document.createElement("span");
    swatch.className = "swatch";
    swatch.style.background = CAUSE_COLOR[cause];
    item.appendChild(swatch);
    item.appendChild(document.createTextNode(`${cause} (${pct}%)`));
    causeLegend.appendChild(item);
  }
}

function stepSim() {
  if (!sim) return;
  if (sim.stepCount >= sim.params.steps) {
    pause();
    setStatus("Finished.");
    return;
  }
  sim.step();
  draw();
  drawPies();
  setStatus(`Step ${sim.stepCount} / ${sim.params.steps}`);
}

function play() {
  if (timer) return;
  timer = setInterval(stepSim, 120);
}

function pause() {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
}

function reset() {
  pause();
  initSim();
}

function exportImage() {
  if (!sim) return;
  const exportCanvas = document.createElement("canvas");
  exportCanvas.width = grid.width + line.width;
  exportCanvas.height = Math.max(grid.height, line.height + pieRole.height + 40);
  const ctx = exportCanvas.getContext("2d");
  ctx.fillStyle = "#0a1016";
  ctx.fillRect(0, 0, exportCanvas.width, exportCanvas.height);
  ctx.drawImage(grid, 0, 0);
  ctx.drawImage(line, grid.width, 0);
  ctx.drawImage(pieRole, grid.width, line.height + 10);
  ctx.drawImage(pieCause, grid.width + pieRole.width + 10, line.height + 10);

  const p = sim.params;
  const name = `sim_w${p.width}_h${p.height}_pop${p.population}_bomb${p.bombFreq}_seed${p.seed}.png`;
  const link = document.createElement("a");
  link.download = name;
  link.href = exportCanvas.toDataURL("image/png");
  link.click();
}

$("init").onclick = initSim;
$("play").onclick = play;
$("pause").onclick = pause;
$("step").onclick = stepSim;
$("reset").onclick = reset;
$("export").onclick = exportImage;

initSim();
