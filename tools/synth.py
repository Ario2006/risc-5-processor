# ABOUTME: Synthesises and places each CPU for a Lattice ECP5 FPGA; records Fmax and resource use.
# ABOUTME: Yosys maps the design, nextpnr places and routes it over several seeds. Writes results/.
import csv
import json
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

from tools.rvasm import assemble
from tools.sim import BUILD, ROOT, write_images

DEVICE = ["--25k", "--package", "CABGA381", "--speed", "6"]
SEEDS = [1, 2, 3, 4, 5]
PROGRAM = ROOT / "programs/bench/bubble_sort.s"
CONFIGS = {"single": 0, "pipe_nofwd": 1, "pipe_fwd": 2}
# block: Yosys may put memories in block RAM (and fold pipeline registers into it).
# distributed: memories stay in LUT RAM, so every pipeline register is a real flip-flop.
MEMORY_STYLES = {"distributed": "-DMEM_DISTRIBUTED", "block": ""}


def tool(native: str, wasm: str) -> list[str]:
    """Prefer a native binary for speed; fall back to the pip-installed YoWASP build."""
    return [native] if shutil.which(native) else ["uv", "run", wasm]


def rel(path: Path) -> str:
    """Path relative to the repo root: the folder name may contain spaces, and YoWASP tools
    only see files under their working directory."""
    return str(Path(path).resolve().relative_to(ROOT))


def sources() -> list[str]:
    files = [*sorted((ROOT / "rtl/common").glob("*.v")),
             *sorted((ROOT / "rtl/single_cycle").glob("*.v")),
             *sorted((ROOT / "rtl/pipeline").glob("*.v")), ROOT / "synth/fpga_top.v"]
    return [rel(f) for f in files]


def synthesise(config: str, memory: str, imem: Path, dmem: Path) -> tuple[Path, dict]:
    """Run Yosys synth_ecp5 for one configuration; return the netlist and cell counts."""
    out = BUILD / f"synth_{config}_{memory}.json"
    stat = BUILD / f"synth_{config}_{memory}.stat.json"
    script = "\n".join([
        f"read_verilog -DSYNTHESIS {MEMORY_STYLES[memory]} -I rtl/common {' '.join(sources())}",
        (f'chparam -set CONFIG {CONFIGS[config]} -set IMEM_INIT "{rel(imem)}" '
         f'-set DMEM_INIT "{rel(dmem)}" fpga_top'),
        f"synth_ecp5 -top fpga_top -json {rel(out)}",
        f"tee -q -o {rel(stat)} stat -json",
    ])
    ys = BUILD / f"synth_{config}_{memory}.ys"
    ys.write_text(script + "\n")
    subprocess.run([*tool("yosys", "yowasp-yosys"), "-q", "-s", rel(ys)], check=True, cwd=ROOT)
    cells = json.loads(stat.read_text())["design"]["num_cells_by_type"]
    return out, cells


def place_and_route(name: str, netlist: Path, seed: int) -> dict:
    """Run nextpnr-ecp5 once; return achieved Fmax, utilisation and the critical path ends."""
    report = BUILD / f"pnr_{name}_{seed}.json"
    subprocess.run([*tool("nextpnr-ecp5", "yowasp-nextpnr-ecp5"), *DEVICE,
                    "--json", rel(netlist), "--freq", "50", "--lpf-allow-unconstrained", "--timing-allow-fail",
                    "--seed", str(seed), "--report", rel(report), "--quiet"],
                   check=True, capture_output=True, cwd=ROOT)
    r = json.loads(report.read_text())
    fmax = next(iter(r["fmax"].values()))["achieved"]
    path = r.get("critical_paths", [{}])[0].get("path", [])
    ends = f"{path[0]['from']['cell']} -> {path[-1]['to']['cell']}" if path else ""
    util = {k: v["used"] for k, v in r["utilization"].items()}
    return {"fmax": fmax, "util": util, "critical": ends}


def main() -> int:
    prog = assemble(PROGRAM.read_text())
    imem, dmem = write_images(prog, "synth")
    rows, runs = [], []
    for memory in MEMORY_STYLES:
        for config in CONFIGS:
            netlist, cells = synthesise(config, memory, imem, dmem)
            results = [place_and_route(f"{config}_{memory}", netlist, s) for s in SEEDS]
            fmaxes = [r["fmax"] for r in results]
            for seed, r in zip(SEEDS, results, strict=True):
                runs.append({"memory": memory, "config": config, "seed": seed,
                             "fmax_mhz": round(r["fmax"], 2), "critical_path": r["critical"]})
            util = results[0]["util"]
            rows.append({
                "memory": memory,
                "config": config,
                "lut4": cells.get("LUT4", 0),
                "ff": cells.get("TRELLIS_FF", 0),
                "logic_cells": util.get("TRELLIS_COMB", 0),
                "lutram_cells": util.get("TRELLIS_RAMW", 0),
                "bram_dp16kd": util.get("DP16KD", 0),
                "fmax_median_mhz": round(statistics.median(fmaxes), 2),
                "fmax_min_mhz": round(min(fmaxes), 2),
                "fmax_max_mhz": round(max(fmaxes), 2),
            })
            print(f"{memory:11} {config:10}: median Fmax {rows[-1]['fmax_median_mhz']} MHz, "
                  f"{rows[-1]['logic_cells']} logic cells, {rows[-1]['ff']} FFs")
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    for name, data in (("synth.csv", rows), ("synth_runs.csv", runs)):
        with open(out / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
