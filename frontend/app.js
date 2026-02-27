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

const COLOR_MAP = {
  InnerParty: {
    Hunger: "#ff8a80",
    BombAttack: "#ff5252",
    Execution: "#d50000",
    Murder: "#ff1744",
  },
  OuterParty: {
    Hunger: "#80bfff",
    BombAttack: "#42a5f5",
    Execution: "#1565c0",
    Murder: "#1e88e5",
  },
  Proles: {
    Hunger: "#81c784",
    BombAttack: "#4caf50",
    Execution: "#2e7d32",
    Murder: "#43a047",
  },
};

class Simulation {
  constructor(params) {
    this.params = params;
    this.rng = mulberry32(params.seed);
    this.stepCount = 0;
    this.agents = [];
    this.series = [];
    this.deathSeries = [];
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
      for (let y = 0; y < p.height; y++) {
        spots.push({ x, y });
      }
    }
    for (let i = spots.length - 1; i > 0; i--) {
      const j = Math.floor(this.rng() * (i + 1));
      [spots[i], spots[j]] = [spots[j], spots[i]];
    }

    const makeAgent = (type) => {
      const spot = spots.pop() || { x: 0, y: 0 };
      return {
        type,
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
      };
    };

    this.agents = [];
    for (let i = 0; i < nInner; i++) this.agents.push(makeAgent("InnerParty"));
    for (let i = 0; i < nOuter; i++) this.agents.push(makeAgent("OuterParty"));
    for (let i = 0; i < nProle; i++) this.agents.push(makeAgent("Proles"));

    this.series = [];
    this.deathSeries = [];
    this.stepCount = 0;
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
    const perAgent = totalFood / Math.max(1, living.length);
    for (const a of living) {
      a.foodStock += perAgent;
    }

    let weapons = 0;
    for (const a of this.agents) {
      if (a.alive && a.type === "Proles") {
        weapons += a.weaponPRate * (a.rebelAction === "Misfunction" ? 0.1 : 1);
      }
    }

    if (this.rng() < p.bombFreq) {
      const cx = Math.floor(this.rng() * p.width);
      const cy = Math.floor(this.rng() * p.height);
      const radius = Math.max(1, Math.floor(randBetween(this.rng, 1, p.bombSize + 1)));
      const intensity = Math.max(1, Math.floor(randBetween(this.rng, 1, p.bombIntensity + 1)));

      let precision = 0;
      const peaceOuter = this.agents.filter(a => a.alive && a.type === "OuterParty");
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
        a.loyalty = clamp(a.loyalty - hunger * 5, 0, 100);
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
        a.loyalty = clamp(a.loyalty + randBetween(this.rng, 2, 6), 0, 100);
      }
    }

    const rebels = this.agents.filter(a => a.alive && a.rebel);
    const toProcess = Math.min(Math.floor(rebels.length / 2), 5);
    for (let i = 0; i < toProcess; i++) {
      const target = rebels[Math.floor(this.rng() * rebels.length)];
      if (!target) continue;
      if (target.type === "OuterParty") {
        if (this.rng() < 0.5) this.recordDeath(target, "Execution");
        else target.rebel = false;
      } else if (target.type === "Proles") {
        this.recordDeath(target, "Execution");
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
    this.deathSeries.push({ step: this.stepCount, counts: this.stepDeaths });
  }
}

const grid = $("grid");
const plot = $("plot");
const gctx = grid.getContext("2d");
const pctx = plot.getContext("2d");
const deathLegend = $("deathLegend");

let sim = null;
let timer = null;

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
  sim = new Simulation(params);
  sim.recordSeries();
  buildLegend();
  draw();
  setStatus("Initialized.");
}

function draw() {
  if (!sim) return;
  drawGrid();
  drawPlot();
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
  }
}

function drawPlot() {
  const series = sim.series;
  const deaths = sim.deathSeries;
  if (!series.length) return;
  const w = plot.width;
  const h = plot.height;
  pctx.clearRect(0, 0, w, h);
  pctx.fillStyle = "#0a1016";
  pctx.fillRect(0, 0, w, h);

  const padding = 40;
  const maxStep = Math.max(...series.map(s => s.step));
  let maxVal = Math.max(...series.map(s => s.population), 1);

  for (const entry of deaths) {
    for (const role of ROLES) {
      for (const cause of CAUSES) {
        maxVal = Math.max(maxVal, entry.counts[role][cause]);
      }
    }
  }

  const xScale = (step) => padding + (step / maxStep) * (w - padding * 2);
  const yScale = (val) => h - padding - (val / maxVal) * (h - padding * 2);

  pctx.strokeStyle = "#233040";
  pctx.beginPath();
  pctx.moveTo(padding, padding);
  pctx.lineTo(padding, h - padding);
  pctx.lineTo(w - padding, h - padding);
  pctx.stroke();

  function drawLine(values, color, width = 1.5) {
    pctx.strokeStyle = color;
    pctx.lineWidth = width;
    pctx.beginPath();
    values.forEach((v, i) => {
      const x = xScale(series[i].step);
      const y = yScale(v);
      if (i === 0) pctx.moveTo(x, y);
      else pctx.lineTo(x, y);
    });
    pctx.stroke();
    pctx.lineWidth = 1;
  }

  drawLine(series.map(s => s.population), "#1f77b4", 2);
  drawLine(series.map(s => s.rebels), "#ff7f0e", 2);

  for (const role of ROLES) {
    for (const cause of CAUSES) {
      const values = deaths.map(d => d.counts[role][cause]);
      drawLine(values, COLOR_MAP[role][cause], 1);
    }
  }

  pctx.fillStyle = "#1f77b4";
  pctx.fillText("Population", padding + 10, padding - 10);
  pctx.fillStyle = "#ff7f0e";
  pctx.fillText("Rebels", padding + 120, padding - 10);
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
  exportCanvas.width = grid.width + plot.width;
  exportCanvas.height = Math.max(grid.height, plot.height);
  const ctx = exportCanvas.getContext("2d");
  ctx.fillStyle = "#0a1016";
  ctx.fillRect(0, 0, exportCanvas.width, exportCanvas.height);
  ctx.drawImage(grid, 0, 0);
  ctx.drawImage(plot, grid.width, 0);

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
