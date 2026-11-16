# ABOUTME: Draws every report figure from results/ and fresh simulation traces into figures/.
# ABOUTME: CPI, speedup, CPI breakdown, Fmax, pipeline diagrams, a waveform and the datapath.
import csv
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

from tools.rvasm import assemble
from tools.sim import BUILD, ROOT, simulate
from tools.vcd import read_vcd, value_at

FIG = ROOT / "figures"
RES = ROOT / "results"

# Validated categorical palette (dataviz reference instance, light mode).
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
CONFIG_COLOR = {"single": "#2a78d6", "pipe_nofwd": "#eb6834", "pipe_fwd": "#1baf7a"}
CONFIG_LABEL = {"single": "Single-cycle", "pipe_nofwd": "Pipeline, no forwarding",
                "pipe_fwd": "Pipeline, forwarding"}
PART_COLOR = {"fill": "#eda100", "stall": "#e87ba4", "flush": "#6250d6"}
STALL_FILL, FLUSH_FILL, CELL_FILL = "#fde7b0", "#f6c9c9", "#e8f0fb"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": INK2, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "font.size": 10, "axes.titlesize": 12,
    "axes.titleweight": "bold", "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "legend.frameon": False, "savefig.dpi": 200, "savefig.bbox": "tight",
})


def read_csv(name: str) -> list[dict]:
    with open(RES / name) as f:
        return list(csv.DictReader(f))


def grouped_bars(ax, groups: list[str], series: dict[str, list[float]], colors: dict[str, str],
                 labels: dict[str, str], fmt: str) -> None:
    """Grouped vertical bars with a 2px surface gap and a value label on every bar."""
    n = len(series)
    width = 0.8 / n
    for i, (key, values) in enumerate(series.items()):
        xs = [g + (i - (n - 1) / 2) * width for g in range(len(groups))]
        bars = ax.bar(xs, values, width, color=colors[key], label=labels[key],
                      edgecolor=SURFACE, linewidth=1.5)
        ax.bar_label(bars, labels=[fmt.format(v) for v in values], padding=2, fontsize=7.5,
                     color=INK2)
    ax.set_xticks(range(len(groups)), [g.replace("_", " ") for g in groups])
    ax.grid(axis="x", visible=False)


def fig_cpi() -> None:
    rows = read_csv("cpi.csv")
    benches = sorted({r["benchmark"] for r in rows})
    series = {c: [float(next(r["cpi"] for r in rows if r["benchmark"] == b and r["config"] == c))
                  for b in benches] for c in CONFIG_COLOR}
    fig, ax = plt.subplots(figsize=(8, 3.8))
    grouped_bars(ax, benches, series, CONFIG_COLOR, CONFIG_LABEL, "{:.2f}")
    ax.set_ylabel("Cycles per instruction (lower is better)")
    ax.set_title("CPI by benchmark", loc="left")
    ax.legend(loc="upper left", ncols=3, bbox_to_anchor=(0, 1.0))
    ax.set_ylim(0, 3.3)
    fig.savefig(FIG / "cpi.png")
    plt.close(fig)


def fig_speedup() -> None:
    rows = read_csv("performance.csv")
    benches = sorted({r["benchmark"] for r in rows})
    configs = ["pipe_nofwd", "pipe_fwd"]
    series = {c: [float(next(r["speedup_vs_single"] for r in rows
                             if r["benchmark"] == b and r["config"] == c)) for b in benches]
              for c in configs}
    fig, ax = plt.subplots(figsize=(8, 3.8))
    grouped_bars(ax, benches, series, CONFIG_COLOR, CONFIG_LABEL, "{:.2f}x")
    ax.axhline(1.0, color=CONFIG_COLOR["single"], linewidth=2)
    ax.text(len(benches) - 0.5, 1.02, "single-cycle = 1.00", ha="right", va="bottom",
            fontsize=8, color=INK2)
    ax.set_ylabel("Speedup in execution time")
    ax.set_title("Execution time speedup over the single-cycle CPU (cycles / Fmax)", loc="left")
    ax.legend(loc="upper left", ncols=2)
    ax.set_ylim(0, 1.6)
    fig.savefig(FIG / "speedup.png")
    plt.close(fig)


def fig_cpi_breakdown() -> None:
    """Where the pipeline's extra cycles go: fill, stalls and branch flushes per instruction."""
    rows = read_csv("cpi.csv")
    benches = sorted({r["benchmark"] for r in rows})
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6), sharey=True)
    for ax, config in zip(axes, ["pipe_nofwd", "pipe_fwd"], strict=True):
        base, fill, stall, flush = [], [], [], []
        for b in benches:
            r = next(r for r in rows if r["benchmark"] == b and r["config"] == config)
            n = int(r["instret"])
            base.append(1.0)
            fill.append(4 / n)
            stall.append(int(r["stall_cycles"]) / n)
            flush.append(2 * int(r["taken_branch_flushes"]) / n)
        ys = range(len(benches))
        ax.barh(ys, base, color=GRID, edgecolor=SURFACE, linewidth=1.5, label="1 cycle per instruction")
        left = base[:]
        for name, part in (("fill", fill), ("stall", stall), ("flush", flush)):
            ax.barh(ys, part, left=left, color=PART_COLOR[name], edgecolor=SURFACE, linewidth=1.5,
                    label={"fill": "pipeline fill (4 cycles)", "stall": "data hazard stalls",
                           "flush": "taken branch flushes (2 each)"}[name])
            left = [a + b for a, b in zip(left, part, strict=True)]
        for y, total in zip(ys, left, strict=True):
            ax.text(total + 0.03, y, f"{total:.2f}", va="center", fontsize=8, color=INK2)
        ax.set_yticks(list(ys), [b.replace("_", " ") for b in benches])
        ax.set_title(CONFIG_LABEL[config], loc="left", fontsize=11)
        ax.set_xlim(0, 3.2)
        ax.set_xlabel("CPI")
        ax.grid(axis="y", visible=False)
    axes[0].legend(loc="upper center", bbox_to_anchor=(1.05, -0.2), ncols=4, fontsize=8)
    fig.suptitle("What each pipelined CPI is made of", x=0.07, y=1.06, ha="left", fontweight="bold")
    fig.savefig(FIG / "cpi_breakdown.png")
    plt.close(fig)


def fig_fmax() -> None:
    rows = read_csv("synth.csv")
    styles = ["distributed", "block"]
    series = {c: [float(next(r["fmax_median_mhz"] for r in rows
                             if r["memory"] == m and r["config"] == c)) for m in styles]
              for c in CONFIG_COLOR}
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    grouped_bars(ax, ["LUT (distributed) memories", "block RAM memories"], series, CONFIG_COLOR,
                 CONFIG_LABEL, "{:.1f}")
    ax.set_ylabel("Fmax, MHz (median of 5 seeds)")
    ax.set_title("Maximum clock on a Lattice ECP5 LFE5U-25F", loc="left")
    ax.legend(loc="upper right")
    ax.set_ylim(0, 135)
    fig.savefig(FIG / "fmax.png")
    plt.close(fig)


def read_trace(path: Path) -> list[dict]:
    rows = []
    lines = path.read_text().splitlines()
    for line in lines[1:]:
        p = line.split()
        rows.append({
            "cycle": int(p[0]),
            "IF": int(p[2], 16), "ID": int(p[4], 16) if p[3] == "1" else None,
            "EX": int(p[6], 16) if p[5] == "1" else None,
            "MEM": int(p[8], 16) if p[7] == "1" else None,
            "WB": int(p[10], 16) if p[9] == "1" else None,
            "stall": p[11] == "1", "flush": p[12] == "1",
        })
    return rows


def fig_pipeline_diagram(config: str) -> None:
    """Classic instruction by cycle chart, built from the RTL's own per cycle trace."""
    path = ROOT / "programs/tests/hazard_demo.s"
    prog = assemble(path.read_text())
    trace = BUILD / f"diagram_{config}.trace"
    simulate(prog, config, "diagram", trace=trace)
    rows = read_trace(trace)
    n = len(prog.text)
    cells: dict[tuple[int, int], str] = {}
    for r in rows:
        for stage in ("IF", "ID", "EX", "MEM", "WB"):
            pc = r[stage]
            if pc is not None and pc // 4 < n:
                cells.setdefault((pc // 4, r["cycle"]), stage)
                if stage == "ID" and r["stall"]:
                    cells[(pc // 4, r["cycle"])] = "ID stall"
    retired = {r["WB"] // 4 for r in rows if r["WB"] is not None}
    # A row that never retires was flushed; mark the cycle after its last stage.
    for i in range(n):
        if i not in retired:
            last = max((c for (row, c) in cells if row == i), default=None)
            if last is not None:
                cells[(i, last + 1)] = "flushed"
    ncyc = max(r["cycle"] for r in rows) + 1
    fig, ax = plt.subplots(figsize=(1.0 + 0.62 * ncyc, 0.42 * n + 1.3))
    for (i, c), label in cells.items():
        color = STALL_FILL if "stall" in label else FLUSH_FILL if label == "flushed" else CELL_FILL
        ax.add_patch(Rectangle((c + 0.04, i + 0.06), 0.92, 0.88, color=color, linewidth=0))
        ax.text(c + 0.5, i + 0.5, label.replace(" ", "\n"), ha="center", va="center",
                fontsize=7 if "\n" in label.replace(" ", "\n") else 8,
                color=INK if i in retired else INK2)
    ax.set_xlim(0, ncyc)
    ax.set_ylim(n, 0)
    ax.set_xticks([c + 0.5 for c in range(ncyc)], [str(c + 1) for c in range(ncyc)])
    ax.set_yticks([i + 0.5 for i in range(n)],
                  [prog.source[i].split("#")[0].strip() for i in range(n)], fontfamily="monospace",
                  fontsize=8)
    ax.tick_params(length=0)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xlabel("Clock cycle")
    res = simulate(prog, config, "diagram")
    ax.set_title(f"{CONFIG_LABEL[config]}: {res.instret} instructions in {res.cycles} cycles "
                 f"(CPI {res.cpi:.2f})", loc="left")
    fig.savefig(FIG / f"pipeline_diagram_{config}.png")
    plt.close(fig)


def fig_waveform() -> None:
    """Waveform of the hazard demo with forwarding: stage PCs, hazard signals, write-back."""
    prog = assemble((ROOT / "programs/tests/hazard_demo.s").read_text())
    vcd = BUILD / "demo_fwd.vcd"
    simulate(prog, "pipe_fwd", "wave", vcd=vcd)
    d = "tb_cpu.dut."
    signals = [
        ("IF pc", d + "if_pc", None), ("ID pc", d + "id_pc", d + "id_valid"),
        ("EX pc", d + "ex_pc", d + "ex_valid"), ("MEM pc", d + "mem_pc", d + "mem_valid"),
        ("WB pc", d + "wb_pc", d + "wb_valid"), ("stall", d + "stall", None),
        ("flush", d + "flush", None), ("fwd_a", d + "fwd_a", None), ("fwd_b", d + "fwd_b", None),
        ("WB rd", d + "wb_rd", d + "wb_we"), ("WB data", d + "wb_data", d + "wb_we"),
    ]
    names = sorted({s for _, a, b in signals for s in (a, b) if s})
    ch = read_vcd(vcd, names)
    ncyc = simulate(prog, "pipe_fwd", "wave").cycles
    first, period = 20_000, 10_000   # first mid-cycle sample and clock period, in ps
    fig, ax = plt.subplots(figsize=(1.2 + 0.7 * ncyc, 0.45 * len(signals) + 1.0))
    for row, (label, sig, valid) in enumerate(signals):
        y = len(signals) - row
        values = []
        for c in range(ncyc):
            t = first + c * period
            v = value_at(ch[sig], t)
            ok = value_at(ch[valid], t) if valid else 1
            values.append(v if ok else None)
        one_bit = label in ("stall", "flush")
        for c, v in enumerate(values):
            if one_bit:
                level = 0.3 if v else -0.3
                ax.plot([c, c + 1], [y + level] * 2, color=INK, linewidth=1.5)
                if c and values[c - 1] != v:
                    ax.plot([c, c], [y - 0.3, y + 0.3], color=INK, linewidth=1.5)
            else:
                same_as_prev = c and values[c - 1] == v
                ax.plot([c, c + 1], [y + 0.3] * 2, color=INK2, linewidth=1)
                ax.plot([c, c + 1], [y - 0.3] * 2, color=INK2, linewidth=1)
                if not same_as_prev:
                    ax.plot([c, c], [y - 0.3, y + 0.3], color=INK2, linewidth=1)
                    text = "-" if v is None else (f"{v:x}" if "pc" in label else str(v))
                    if label == "fwd_a" or label == "fwd_b":
                        text = {0: "reg", 2: "EX/MEM", 1: "MEM/WB"}.get(v, text)
                    ax.text(c + 0.08, y, text, va="center", fontsize=7.5, fontfamily="monospace")
        ax.text(-0.2, y, label, ha="right", va="center", fontsize=9)
    ax.set_xlim(-0.05, ncyc)
    ax.set_ylim(0.3, len(signals) + 0.7)
    ax.set_yticks([])
    ax.set_xticks(range(ncyc), [str(c + 1) for c in range(ncyc)], fontsize=8)
    ax.grid(axis="x", color=GRID)
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Clock cycle (values sampled mid-cycle)")
    ax.set_title("Hazard demo on the forwarding pipeline (from the simulation VCD)", loc="left")
    fig.savefig(FIG / "waveform_hazard_demo.png")
    plt.close(fig)


def box(ax, x, y, w, h, text, fill=CELL_FILL, size=8.5, weight="normal"):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=INK2, linewidth=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size,
            fontweight=weight)


def arrow(ax, a, b, color=INK, style="-|>", ls="-", rad=0.0, lw=1.2):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=9, color=color,
                                 linestyle=ls, linewidth=lw, connectionstyle=f"arc3,rad={rad}"))


def fig_architecture() -> None:
    """Block diagram of the 5-stage datapath, its pipeline registers and control units."""
    fig, ax = plt.subplots(figsize=(13, 6.2))
    ax.set_xlim(0, 26)
    ax.set_ylim(0, 12.4)
    ax.axis("off")
    stages = [("IF", 0.3, 4.4), ("ID", 5.2, 5.4), ("EX", 11.1, 5.2), ("MEM", 16.8, 4.0),
              ("WB", 21.3, 4.4)]
    for name, x, w in stages:
        ax.add_patch(Rectangle((x, 1.2), w, 9.0, facecolor="#f3f2ee", edgecolor="none"))
        ax.text(x + w / 2, 9.75, name, ha="center", fontsize=12, fontweight="bold", color=INK2)
    regs = [(4.75, "IF/ID"), (10.65, "ID/EX"), (16.35, "EX/MEM"), (20.85, "MEM/WB")]
    for x, name in regs:
        ax.add_patch(Rectangle((x, 1.6), 0.38, 7.6, facecolor="#cfd8e6", edgecolor=INK2))
        ax.text(x + 0.19, 1.25, name, ha="center", va="top", fontsize=8, fontweight="bold")
    # IF
    box(ax, 0.6, 5.0, 1.2, 1.2, "PC", weight="bold")
    box(ax, 2.4, 4.6, 2.0, 2.0, "Instruction\nmemory\n(256 words)")
    box(ax, 0.6, 7.2, 1.2, 0.8, "+4", size=8)
    arrow(ax, (1.8, 5.6), (2.4, 5.6))
    arrow(ax, (4.4, 5.6), (4.75, 5.6))
    arrow(ax, (1.2, 6.2), (1.2, 7.2))
    # ID
    box(ax, 5.6, 6.9, 2.1, 1.3, "Control\nunit", fill="#eef3e8")
    box(ax, 7.9, 4.2, 2.4, 2.4, "Register\nfile\n32 x 32\n(write-through)", size=7.5)
    box(ax, 5.6, 2.4, 2.1, 1.1, "Immediate\ngenerator")
    arrow(ax, (5.13, 5.6), (7.9, 5.6))
    arrow(ax, (5.13, 7.5), (5.6, 7.5))
    arrow(ax, (5.13, 3.0), (5.6, 3.0))
    arrow(ax, (10.3, 5.0), (10.65, 5.0))
    arrow(ax, (7.7, 7.5), (10.65, 7.5))
    arrow(ax, (7.7, 3.0), (10.65, 3.0))
    # EX
    box(ax, 11.5, 5.6, 1.1, 1.2, "fwd\nmux A", size=7.5)
    box(ax, 11.5, 3.6, 1.1, 1.2, "fwd\nmux B", size=7.5)
    box(ax, 13.3, 4.0, 1.6, 2.6, "ALU", weight="bold")
    box(ax, 13.1, 7.2, 2.9, 1.0, "branch compare\n+ target", size=7.5)
    arrow(ax, (11.03, 6.2), (11.5, 6.2))
    arrow(ax, (11.03, 4.2), (11.5, 4.2))
    arrow(ax, (12.6, 6.2), (13.3, 6.2))
    arrow(ax, (12.6, 4.2), (13.3, 4.2))
    arrow(ax, (14.9, 5.3), (16.35, 5.3))
    # MEM
    box(ax, 17.3, 4.4, 2.6, 2.2, "Data\nmemory\n(256 words)")
    arrow(ax, (16.73, 5.3), (17.3, 5.3))
    arrow(ax, (19.9, 5.5), (20.85, 5.5))
    # WB
    box(ax, 21.8, 4.6, 1.3, 1.8, "WB\nmux", size=8)
    arrow(ax, (21.23, 5.5), (21.8, 5.5))
    # write back loop to the register file
    ax.plot([23.1, 25.3, 25.3, 9.1, 9.1], [5.5, 5.5, 0.55, 0.55, 4.2], color=INK, linewidth=1.2)
    arrow(ax, (9.1, 0.9), (9.1, 4.2))
    ax.text(17.0, 0.15, "write back: rd, data", fontsize=8, color=INK2)
    # forwarding paths
    fwd = "#1baf7a"
    ax.plot([16.55, 16.55, 12.05], [3.0, 2.2, 2.2], color=fwd, linewidth=1.6)
    arrow(ax, (12.05, 2.2), (12.05, 3.6), color=fwd, lw=1.6)
    ax.plot([24.0, 24.0, 11.2], [5.5, 1.75, 1.75], color=fwd, linewidth=1.6, linestyle="--")
    arrow(ax, (11.2, 1.75), (11.6, 3.6), color=fwd, lw=1.6, ls="--")
    ax.text(12.5, 2.32, "forward from EX/MEM", fontsize=7.5, color=INK2)
    ax.text(17.3, 1.87, "forward from MEM/WB", fontsize=7.5, color=INK2)
    # branch redirect
    red = "#d03b3b"
    ax.plot([15.9, 15.9, 0.35, 0.35], [8.2, 10.5, 10.5, 5.6], color=red, linewidth=1.4)
    arrow(ax, (0.35, 5.6), (0.6, 5.6), color=red)
    ax.text(8.4, 10.62, "taken branch: new PC, flush IF/ID and ID/EX (2 cycle penalty)",
            fontsize=8, color=INK2)
    # hazard and forwarding units
    box(ax, 0.8, 11.0, 6.9, 0.85, "Hazard unit: load-use stall, flush, stop at ecall",
        fill="#fbeedd", size=8)
    box(ax, 16.4, 11.0, 8.2, 0.85, "Forwarding unit: compares rs1/rs2 with rd in MEM, WB",
        fill="#e3f4ec", size=8)
    arrow(ax, (4.3, 11.0), (6.6, 8.25), color=INK2, ls=":")
    arrow(ax, (18.0, 11.0), (12.05, 6.85), color=INK2, ls=":")
    ax.text(0.3, 12.2, "5-stage pipelined RV32I subset CPU", fontsize=13, fontweight="bold")
    fig.savefig(FIG / "architecture_pipeline.png")
    plt.close(fig)


def fig_architecture_single() -> None:
    """Block diagram of the single-cycle datapath, control unit and critical path."""
    rows = read_csv("synth.csv")
    row = next(r for r in rows if r["config"] == "single" and r["memory"] == "distributed")
    fmax = float(row["fmax_median_mhz"])
    period_ns = 1000.0 / fmax

    fig, ax = plt.subplots(figsize=(13, 6.4))
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 11.5)
    ax.axis("off")

    crit_color = "#c93b2b"
    ctrl_color = "#2e7d32"
    branch_color = "#6250d6"

    # Header and Banner
    ax.text(0.5, 10.8, f"Single-cycle RV32I subset CPU (clock period {period_ns:.1f} ns, {fmax:.2f} MHz)",
            fontsize=12, fontweight="bold")
    ax.text(0.5, 10.2, f"Critical path in distributed RAM: instr (retimed PC) → regfile read → ALU addr → dmem read → WB mux → regfile setup ({fmax:.2f} MHz)",
            fontsize=8.5, color=crit_color, fontweight="bold")

    # Legend at top right (away from all wires and labels)
    ax.plot([18.2, 19.2], [10.8, 10.8], color=crit_color, linewidth=2.2)
    ax.text(19.4, 10.8, "worst-case critical path (lw)", va="center", fontsize=8, color=crit_color, fontweight="bold")

    # 1. PC Mux & PC
    box(ax, 0.5, 4.4, 1.0, 1.8, "PC\nMux", size=8)
    box(ax, 1.9, 4.7, 1.1, 1.2, "PC", weight="bold")
    arrow(ax, (1.5, 5.3), (1.9, 5.3))

    # PC Adders: +4 and Branch target
    box(ax, 1.9, 7.3, 1.1, 0.8, "+4", size=8)
    # PC to +4 adder
    arrow(ax, (2.45, 5.9), (2.45, 7.3))
    # PC+4 to PC Mux input 0 (enters from top-left of PC Mux at x=0.75)
    ax.plot([1.9, 0.75, 0.75], [7.7, 7.7, 6.2], color=INK, linewidth=1.1)
    arrow(ax, (0.75, 6.6), (0.75, 6.2))
    ax.text(0.75, 6.35, "0", fontsize=7, color=INK2, ha="right")

    # Branch Target adder (PC + imm) placed at x=3.5, y=8.3, h=1.0
    box(ax, 3.5, 8.3, 1.6, 1.0, "Branch\nTarget (+)", size=7.5)
    # PC to Branch Target adder
    ax.plot([2.45, 2.45, 3.5], [5.9, 8.8, 8.8], color=INK, linewidth=1.0)
    arrow(ax, (3.1, 8.8), (3.5, 8.8))
    # imm to Branch Target adder
    ax.plot([8.3, 8.5, 8.5, 4.3, 4.3], [2.6, 2.6, 1.4, 1.4, 8.3], color=INK, linewidth=1.0)
    arrow(ax, (4.3, 7.9), (4.3, 8.3))
    # Branch target output to PC Mux input 1 (enters from top-right of PC Mux at x=1.25)
    ax.plot([3.5, 1.25, 1.25], [8.6, 8.6, 6.2], color=branch_color, linewidth=1.1)
    arrow(ax, (1.25, 6.6), (1.25, 6.2), color=branch_color)
    ax.text(1.25, 6.35, "1", fontsize=7, color=branch_color, ha="left")

    # 2. Instruction memory
    box(ax, 3.5, 4.2, 2.1, 2.2, "Instruction\nmemory\n(256 words)")
    arrow(ax, (3.0, 5.3), (3.5, 5.3))

    # Instruction bus split out of IMEM (Critical path starts at retimed instr)
    ax.plot([5.6, 6.0], [5.3, 5.3], color=crit_color, linewidth=2.0)

    # 3. Control unit (placed at x=6.2, y=7.4, w=2.1, h=1.4)
    box(ax, 6.2, 7.4, 2.1, 1.4, "Control\nunit", fill="#eef3e8", size=8.5)
    ax.plot([5.8, 5.8, 6.2], [5.3, 8.1, 8.1], color=INK, linewidth=1.1)
    arrow(ax, (5.8, 8.1), (6.2, 8.1))

    # 4. Immediate generator
    box(ax, 6.2, 2.0, 2.1, 1.2, "Immediate\ngenerator", size=8)
    ax.plot([5.8, 5.8, 6.2], [5.3, 2.6, 2.6], color=INK, linewidth=1.1)
    arrow(ax, (5.8, 2.6), (6.2, 2.6))

    # 5. Register file (Critical path passes through rs1 read)
    ax.add_patch(Rectangle((8.7, 3.7), 2.5, 3.0, facecolor=CELL_FILL, edgecolor=crit_color, linewidth=1.5, zorder=3))
    ax.text(8.7 + 1.25, 3.7 + 1.5, "Register\nfile\n32 x 32\n(x0 = 0)", ha="center", va="center", fontsize=8, zorder=4)
    ax.plot([5.8, 8.7], [5.7, 5.7], color=crit_color, linewidth=2.0)
    arrow(ax, (8.3, 5.7), (8.7, 5.7), color=crit_color, lw=2.0)
    ax.text(7.35, 5.88, "rs1, rs2, rd", fontsize=7.5, color=INK2)
    ax.plot([5.8, 8.7], [4.5, 4.5], color=INK, linewidth=1.1)
    arrow(ax, (8.3, 4.5), (8.7, 4.5))

    # 6. ALU Src Mux
    box(ax, 12.0, 3.3, 0.9, 1.5, "ALU\nSrc\nMux", size=7.5)
    arrow(ax, (11.2, 4.3), (12.0, 4.3))
    ax.plot([8.3, 11.6, 11.6, 12.0], [2.6, 2.6, 3.7, 3.7], color=crit_color, linewidth=1.8)
    arrow(ax, (11.6, 3.7), (12.0, 3.7), color=crit_color, lw=1.8)

    # 7. ALU (Critical path computes memory address a + imm)
    ax.add_patch(Rectangle((13.5, 3.6), 1.8, 2.8, facecolor=CELL_FILL, edgecolor=crit_color, linewidth=1.5, zorder=3))
    ax.text(13.5 + 0.9, 3.6 + 1.4, "ALU", ha="center", va="center", fontsize=8.5, fontweight="bold", zorder=4)
    arrow(ax, (11.2, 5.7), (13.5, 5.7), color=crit_color, lw=2.0)
    arrow(ax, (12.9, 4.05), (13.5, 4.05), color=crit_color, lw=1.8)

    # 8. Branch comparator (placed at x=11.6, y=6.2, w=2.8, h=1.0)
    box(ax, 11.6, 6.2, 2.8, 1.0, "Branch compare\n(rs1 == rs2) ^ bne", fill="#fbeedd", size=7.5)
    ax.plot([11.4, 11.4, 11.6], [5.7, 6.8, 6.8], color=INK, linewidth=1.0)
    arrow(ax, (11.5, 6.8), (11.6, 6.8))
    ax.plot([11.5, 11.5, 11.6], [4.3, 6.4, 6.4], color=INK, linewidth=1.0)
    arrow(ax, (11.55, 6.4), (11.6, 6.4))

    # Taken redirect wire (in branch_color):
    # Runs from Branch compare (14.4, 6.7) up to y=9.7 (completely above Branch Target box),
    # then left all the way to x=0.2, then down to y=5.3, entering left side of PC Mux!
    ax.plot([14.4, 14.8, 14.8, 0.2, 0.2, 0.5], [6.7, 6.7, 9.7, 9.7, 5.3, 5.3], color=branch_color, linewidth=1.2)
    arrow(ax, (0.2, 5.3), (0.5, 5.3), color=branch_color)
    ax.text(7.5, 9.85, "taken = branch && condition (selects branch target at PC Mux)",
            fontsize=8, color=branch_color, fontweight="bold")

    # 9. Data Memory (Critical path reads data memory)
    ax.add_patch(Rectangle((16.7, 3.8), 2.5, 2.4, facecolor=CELL_FILL, edgecolor=crit_color, linewidth=1.5, zorder=3))
    ax.text(16.7 + 1.25, 3.8 + 1.2, "Data\nmemory\n(256 words)", ha="center", va="center", fontsize=8.5, zorder=4)
    arrow(ax, (15.3, 5.0), (16.7, 5.0), color=crit_color, lw=2.0)
    # store data (rs2) to dmem
    ax.plot([11.3, 11.3, 16.2, 16.2, 16.7], [4.3, 2.9, 2.9, 4.2, 4.2], color=INK, linewidth=1.0)
    arrow(ax, (16.2, 4.2), (16.7, 4.2))
    ax.text(13.6, 2.65, "store data (rs2_val)", fontsize=7.5, color=INK2)

    # 10. WB Mux (Critical path selects load data)
    ax.add_patch(Rectangle((20.2, 4.2), 1.0, 1.8, facecolor=CELL_FILL, edgecolor=crit_color, linewidth=1.5, zorder=3))
    ax.text(20.2 + 0.5, 4.2 + 0.9, "WB\nMux", ha="center", va="center", fontsize=8, zorder=4)
    arrow(ax, (19.2, 5.0), (20.2, 5.0), color=crit_color, lw=2.0)
    # alu_y bypass dmem to WB mux
    ax.plot([15.6, 15.6, 19.8, 19.8, 20.2], [5.0, 6.4, 6.4, 4.5, 4.5], color=INK, linewidth=1.1)
    arrow(ax, (19.8, 4.5), (20.2, 4.5))

    # 11. Write-back bus back to Register File (Critical path completes write-back)
    ax.plot([21.2, 22.5, 22.5, 9.8, 9.8], [5.1, 5.1, 0.7, 0.7, 3.7], color=crit_color, linewidth=2.0)
    arrow(ax, (9.8, 1.5), (9.8, 3.7), color=crit_color, lw=2.0)
    ax.text(14.5, 0.45, "write-back: wb_data (ALU result or load data) to rd",
            fontsize=8, color=crit_color, fontweight="bold")

    # 12. Control lines (dashed, completely avoiding all text and boxes)
    # RegWr
    ax.plot([8.3, 9.2, 9.2], [7.9, 7.9, 6.7], color=ctrl_color, lw=1.1, ls="--")
    arrow(ax, (9.2, 7.0), (9.2, 6.7), color=ctrl_color, ls="--")
    ax.text(8.5, 8.02, "RegWr", fontsize=7.5, color=ctrl_color)

    # ALUSrc
    ax.plot([8.3, 12.4, 12.4], [7.7, 7.7, 4.8], color=ctrl_color, lw=1.1, ls="--")
    arrow(ax, (12.4, 5.1), (12.4, 4.8), color=ctrl_color, ls="--")
    ax.text(10.2, 7.82, "ALUSrc", fontsize=7.5, color=ctrl_color)

    # Branch control to branch compare box
    ax.plot([8.3, 11.2, 11.2, 11.6], [7.6, 7.6, 6.9, 6.9], color=ctrl_color, lw=1.1, ls="--")
    arrow(ax, (11.2, 6.9), (11.6, 6.9), color=ctrl_color, ls="--")
    ax.text(9.2, 7.72, "Branch/NE", fontsize=7.5, color=ctrl_color)

    # ALUOp - routes to x=15.0 (right side of ALU, above at y=7.3, drops down to 6.4)
    # Does NOT pass through Branch compare (which is at x=11.6 to 14.4, y=6.2 to 7.2)
    ax.plot([8.3, 15.0, 15.0], [7.3, 7.3, 6.4], color=ctrl_color, lw=1.1, ls="--")
    arrow(ax, (15.0, 6.7), (15.0, 6.4), color=ctrl_color, ls="--")
    ax.text(10.2, 7.42, "ALUOp", fontsize=7.5, color=ctrl_color)

    # MemWr - routes at y=8.8 to x=17.5, drops down to 6.2
    # Text placed at (16.3, 8.95), above the dashed line
    ax.plot([8.3, 17.5, 17.5], [8.8, 8.8, 6.2], color=ctrl_color, lw=1.1, ls="--")
    arrow(ax, (17.5, 6.5), (17.5, 6.2), color=ctrl_color, ls="--")
    ax.text(16.3, 8.95, "MemWr", fontsize=7.5, color=ctrl_color)

    # MemRd - routes at y=9.3 to x=20.7, drops down to 6.0
    # Text placed at (19.4, 9.45), above the dashed line
    ax.plot([8.3, 20.7, 20.7], [9.3, 9.3, 6.0], color=ctrl_color, lw=1.1, ls="--")
    arrow(ax, (20.7, 6.3), (20.7, 6.0), color=ctrl_color, ls="--")
    ax.text(19.4, 9.45, "MemRd", fontsize=7.5, color=ctrl_color)

    fig.savefig(FIG / "architecture_single.png")
    plt.close(fig)


def main() -> int:
    FIG.mkdir(exist_ok=True)
    fig_cpi()
    fig_speedup()
    fig_cpi_breakdown()
    fig_fmax()
    for config in ("pipe_fwd", "pipe_nofwd"):
        fig_pipeline_diagram(config)
    fig_waveform()
    fig_architecture()
    fig_architecture_single()
    for f in sorted(FIG.glob("*.png")):
        print(f.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
