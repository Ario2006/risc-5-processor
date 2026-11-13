# ABOUTME: Performance study: runs every benchmark on the three CPUs and joins cycles with Fmax.
# ABOUTME: Writes results/cpi.csv and results/performance.csv (CPI, IPC, execution time, speedup).
import csv
import sys
from pathlib import Path

from tools.rvasm import assemble
from tools.sim import CONFIGS, ROOT, check

BENCHMARKS = sorted((ROOT / "programs/bench").glob("*.s"))


def read_fmax(memory: str = "distributed") -> dict[str, float]:
    """Median Fmax per configuration from results/synth.csv (run tools.synth first).

    Uses the distributed memory build, where every pipeline register is a real flip-flop."""
    path = ROOT / "results/synth.csv"
    if not path.exists():
        raise SystemExit("results/synth.csv missing: run `uv run python -m tools.synth` first")
    with open(path) as f:
        return {row["config"]: float(row["fmax_median_mhz"])
                for row in csv.DictReader(f) if row["memory"] == memory}


def write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    fmax = read_fmax()
    cpi_rows, perf_rows = [], []
    for path in BENCHMARKS:
        prog = assemble(path.read_text())
        times = {}
        for config in CONFIGS:
            res = check(prog, config, f"perf_{path.stem}")
            time_us = res.cycles / fmax[config]
            times[config] = time_us
            cpi_rows.append({
                "benchmark": path.stem, "config": config, "instret": res.instret,
                "cycles": res.cycles, "cpi": round(res.cpi, 3), "ipc": round(res.ipc, 3),
                "stall_cycles": res.stalls, "load_use_stalls": res.load_use,
                "taken_branch_flushes": res.flushes,
            })
            perf_rows.append({
                "benchmark": path.stem, "config": config, "cycles": res.cycles,
                "fmax_mhz": fmax[config], "time_us": round(time_us, 3),
            })
        for row in perf_rows[-len(CONFIGS):]:
            row["speedup_vs_single"] = round(times["single"] / row["time_us"], 3)
    out = ROOT / "results"
    write_csv(out / "cpi.csv", cpi_rows)
    write_csv(out / "performance.csv", perf_rows)
    for row in cpi_rows:
        print(f"{row['benchmark']:12} {row['config']:10} CPI {row['cpi']:.3f}  "
              f"stalls {row['stall_cycles']:4}  flushes {row['taken_branch_flushes']:3}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
