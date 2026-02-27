import argparse
import json
import os
import random

from Common import CauseOfDeath
from Model import BasicModel


def summarize(model):
    agents = model.spotTaken
    total = len(agents)
    counts = {"InnerParty": 0, "OuterParty": 0, "Proles": 0}
    rebels = {"OuterParty": 0, "Proles": 0}
    loyalty = {"OuterParty": [], "Proles": []}
    food = []

    for agent in agents:
        name = agent.__class__.__name__
        if name in counts:
            counts[name] += 1
        if name in rebels and agent.rebel:
            rebels[name] += 1
        if name in loyalty:
            loyalty[name].append(agent.loyalty)
        if hasattr(agent, "foodStock"):
            food.append(agent.foodStock)

    avg_loyalty = {
        k: (sum(v) / len(v) if v else 0) for k, v in loyalty.items()
    }
    avg_food = sum(food) / len(food) if food else 0

    deaths = {cause.name: model.death_counts[cause] for cause in CauseOfDeath}

    return {
        "total": total,
        "counts": counts,
        "rebels": rebels,
        "avg_loyalty": avg_loyalty,
        "avg_food": avg_food,
        "deaths": deaths,
    }


def run(args):
    random.seed(args.seed)
    model = BasicModel(
        bombAttackFrequency=args.bomb_freq,
        avgBombAttackImpactSize=args.bomb_size,
        avgBombAttackIntensity=args.bomb_intensity,
        width=args.width,
        height=args.height,
        initialPopulation=args.population,
        initialFoodStock=args.initial_food,
    )

    snapshots = []
    series = []

    for step in range(1, args.steps + 1):
        model.step()
        s = summarize(model)
        series.append({"step": step, **s})
        if args.record:
            snapshots.append(model.snapshot(step))
        if step % args.report_every == 0 or step == args.steps:
            print(f"Step {step}")
            print(f"  Population: {s['total']}")
            print(f"  Counts: {s['counts']}")
            print(f"  Rebels: {s['rebels']}")
            print(f"  Avg Loyalty: {s['avg_loyalty']}")
            print(f"  Avg Food: {s['avg_food']:.2f}")
            print(f"  Deaths: {s['deaths']}")

    if args.record:
        os.makedirs(args.out_dir, exist_ok=True)
        data = {
            "meta": {
                "steps": args.steps,
                "width": args.width,
                "height": args.height,
                "population": args.population,
                "seed": args.seed,
            },
            "snapshots": snapshots,
            "series": series,
        }
        data_path = os.path.join(args.out_dir, "sim_data.json")
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        write_viewer(os.path.join(args.out_dir, "view.html"), data)
        print(f"Wrote {data_path}")
        print(f"Wrote {os.path.join(args.out_dir, 'view.html')}")


def write_viewer(path, data):
    data_json = json.dumps(data)
    html = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>1984 World Simulation Viewer</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 20px; }
      .row { display: flex; gap: 20px; flex-wrap: wrap; }
      canvas { border: 1px solid #ccc; }
      .controls { margin: 10px 0; }
      .legend span { display: inline-block; margin-right: 12px; }
      .dot { display: inline-block; width: 10px; height: 10px; margin-right: 6px; border-radius: 50%; }
      .inner { background: #d62728; }
      .outer { background: #1f77b4; }
      .prole { background: #2ca02c; }
      .rebel { border: 2px solid #ffcc00; }
    </style>
  </head>
  <body>
    <h2>1984 World Simulation</h2>
    <div class="controls">
      <button id="play">Play</button>
      <button id="pause">Pause</button>
      <input id="step" type="range" min="1" max="1" value="1" />
      <span id="stepLabel">Step 1</span>
    </div>
    <div class="legend">
      <span><span class="dot inner"></span>Inner Party</span>
      <span><span class="dot outer"></span>Outer Party</span>
      <span><span class="dot prole"></span>Proles</span>
      <span><span class="dot rebel"></span>Rebel (outline)</span>
    </div>
    <div class="row">
      <canvas id="grid" width="340" height="340"></canvas>
      <canvas id="plot" width="520" height="340"></canvas>
    </div>
    <script>
      const data = {{DATA}};
      const snapshotData = data.snapshots;
      const series = data.series;
      const gridCanvas = document.getElementById("grid");
      const plotCanvas = document.getElementById("plot");
      const ctx = gridCanvas.getContext("2d");
      const pctx = plotCanvas.getContext("2d");
      const stepInput = document.getElementById("step");
      const stepLabel = document.getElementById("stepLabel");
      const playBtn = document.getElementById("play");
      const pauseBtn = document.getElementById("pause");

      stepInput.max = snapshotData.length;

      function colorFor(type) {
        if (type === "InnerParty") return "#d62728";
        if (type === "OuterParty") return "#1f77b4";
        return "#2ca02c";
      }

      function drawGrid(step) {
        const snap = snapshotData[step - 1];
        const cell = Math.floor(Math.min(gridCanvas.width / snap.width, gridCanvas.height / snap.height));
        ctx.clearRect(0, 0, gridCanvas.width, gridCanvas.height);
        ctx.fillStyle = "#f7f7f7";
        ctx.fillRect(0, 0, gridCanvas.width, gridCanvas.height);
        for (let i = 0; i <= snap.width; i++) {
          ctx.strokeStyle = "#e6e6e6";
          ctx.beginPath();
          ctx.moveTo(i * cell, 0);
          ctx.lineTo(i * cell, snap.height * cell);
          ctx.stroke();
        }
        for (let j = 0; j <= snap.height; j++) {
          ctx.strokeStyle = "#e6e6e6";
          ctx.beginPath();
          ctx.moveTo(0, j * cell);
          ctx.lineTo(snap.width * cell, j * cell);
          ctx.stroke();
        }
        for (const agent of snap.agents) {
          const x = agent.x * cell + cell / 2;
          const y = agent.y * cell + cell / 2;
          ctx.beginPath();
          ctx.fillStyle = colorFor(agent.type);
          ctx.arc(x, y, cell * 0.35, 0, Math.PI * 2);
          ctx.fill();
          if (agent.rebel) {
            ctx.strokeStyle = "#ffcc00";
            ctx.lineWidth = 2;
            ctx.stroke();
          }
        }
      }

      function drawPlot() {
        const w = plotCanvas.width;
        const h = plotCanvas.height;
        pctx.clearRect(0, 0, w, h);
        pctx.fillStyle = "#ffffff";
        pctx.fillRect(0, 0, w, h);

        const padding = 40;
        const steps = series.map(s => s.step);
        const totals = series.map(s => s.total);
        const rebels = series.map(s => s.rebels.OuterParty + s.rebels.Proles);

        const maxStep = Math.max(...steps);
        const maxVal = Math.max(...totals, ...rebels, 1);

        function xScale(step) {
          return padding + (step / maxStep) * (w - padding * 2);
        }
        function yScale(val) {
          return h - padding - (val / maxVal) * (h - padding * 2);
        }

        pctx.strokeStyle = "#333";
        pctx.beginPath();
        pctx.moveTo(padding, padding);
        pctx.lineTo(padding, h - padding);
        pctx.lineTo(w - padding, h - padding);
        pctx.stroke();

        function drawLine(values, color) {
          pctx.strokeStyle = color;
          pctx.beginPath();
          values.forEach((v, i) => {
            const x = xScale(steps[i]);
            const y = yScale(v);
            if (i === 0) pctx.moveTo(x, y);
            else pctx.lineTo(x, y);
          });
          pctx.stroke();
        }

        drawLine(totals, "#1f77b4");
        drawLine(rebels, "#ff7f0e");

        pctx.fillStyle = "#1f77b4";
        pctx.fillText("Population", padding + 10, padding - 10);
        pctx.fillStyle = "#ff7f0e";
        pctx.fillText("Rebels", padding + 120, padding - 10);
      }

      let timer = null;
      function setStep(step) {
        stepInput.value = step;
        stepLabel.textContent = `Step ${step}`;
        drawGrid(step);
      }

      playBtn.onclick = () => {
        if (timer) return;
        timer = setInterval(() => {
          let step = parseInt(stepInput.value, 10) + 1;
          if (step > snapshotData.length) step = 1;
          setStep(step);
        }, 200);
      };
      pauseBtn.onclick = () => {
        if (timer) {
          clearInterval(timer);
          timer = null;
        }
      };
      stepInput.oninput = () => setStep(parseInt(stepInput.value, 10));

      drawPlot();
      setStep(1);
    </script>
  </body>
</html>
"""
    html = html.replace("{{DATA}}", data_json)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    parser = argparse.ArgumentParser(description="Run 1984 world simulation.")
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--report-every", type=int, default=10)
    parser.add_argument("--population", type=int, default=200)
    parser.add_argument("--width", type=int, default=17)
    parser.add_argument("--height", type=int, default=17)
    parser.add_argument("--initial-food", type=float, default=3)
    parser.add_argument("--bomb-freq", type=float, default=0.2)
    parser.add_argument("--bomb-size", type=int, default=3)
    parser.add_argument("--bomb-intensity", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--record", action="store_true", help="Record snapshots and write viewer HTML")
    parser.add_argument("--out-dir", type=str, default="output")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
