# ABOUTME: Runs assembly programs on the Verilog CPUs with Icarus and checks them against the ISS.
# ABOUTME: Three configurations: single-cycle, pipeline without forwarding, pipeline with forwarding.
import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from tools.iss import DMEM_WORDS, run
from tools.rvasm import Program, assemble

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
IMEM_WORDS = 256

CONFIGS = {
    "single": {"dir": "single_cycle", "defines": []},
    "pipe_nofwd": {"dir": "pipeline", "defines": ["-DPIPELINE", "-DFORWARDING=0"]},
    "pipe_fwd": {"dir": "pipeline", "defines": ["-DPIPELINE", "-DFORWARDING=1"]},
}


class SimError(Exception):
    """Raised when simulation fails or disagrees with the reference model."""


@dataclass
class SimResult:
    """Final state and performance counts from one RTL run."""

    regs: list[int]
    dmem: list[int]
    cycles: int
    instret: int
    stalls: int
    load_use: int
    flushes: int

    @property
    def cpi(self) -> float:
        return self.cycles / self.instret

    @property
    def ipc(self) -> float:
        return self.instret / self.cycles


def require_iverilog() -> None:
    """Fail with install help if Icarus Verilog is missing."""
    if not shutil.which("iverilog") or not shutil.which("vvp"):
        raise SimError("Icarus Verilog not found. See README, section Setup.")


def compile_config(config: str) -> Path:
    """Compile the testbench for one configuration, rebuilding only if a source changed."""
    require_iverilog()
    spec = CONFIGS[config]
    sources = [ROOT / "tb/tb_cpu.v", *sorted((ROOT / "rtl/common").glob("*.v")),
               *sorted((ROOT / "rtl" / spec["dir"]).glob("*.v"))]
    headers = sorted((ROOT / "rtl/common").glob("*.vh"))
    out = BUILD / f"{config}.vvp"
    newest = max(p.stat().st_mtime for p in [*sources, *headers])
    if out.exists() and out.stat().st_mtime >= newest:
        return out
    BUILD.mkdir(exist_ok=True)
    cmd = ["iverilog", "-g2012", "-I", str(ROOT / "rtl/common"), *spec["defines"],
           "-o", str(out), *map(str, sources)]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode:
        raise SimError(f"iverilog failed for {config}:\n{proc.stderr}")
    return out


def write_images(prog: Program, stem: str) -> tuple[Path, Path]:
    """Write padded imem and dmem hex files so $readmemh fills every word."""
    if len(prog.text) > IMEM_WORDS or len(prog.data) > DMEM_WORDS:
        raise SimError(f"{stem}: program does not fit the 256 word memories")
    BUILD.mkdir(exist_ok=True)
    imem = BUILD / f"{stem}.imem.hex"
    dmem = BUILD / f"{stem}.dmem.hex"
    imem.write_text("".join(f"{w:08x}\n" for w in prog.text + [0x13] * (IMEM_WORDS - len(prog.text))))
    data = prog.data + [0] * (DMEM_WORDS - len(prog.data))
    dmem.write_text("".join(f"{w & 0xFFFFFFFF:08x}\n" for w in data))
    return imem, dmem


def parse_dump(text: str) -> SimResult:
    """Read the testbench's dump file."""
    regs, dmem, stats = [0] * 32, [0] * DMEM_WORDS, {}
    for line in text.splitlines():
        parts = line.split()
        if parts[0] == "r":
            regs[int(parts[1])] = int(parts[2], 16)
        elif parts[0] == "m":
            dmem[int(parts[1])] = int(parts[2], 16)
        else:
            stats[parts[0]] = int(parts[1])
    return SimResult(regs=regs, dmem=dmem, **stats)


def simulate(prog: Program, config: str, stem: str = "prog", trace: Path | None = None,
             vcd: Path | None = None, max_cycles: int = 200_000) -> SimResult:
    """Run prog on one RTL configuration and return its final state and counts."""
    vvp = compile_config(config)
    imem, dmem = write_images(prog, f"{stem}.{config}")
    dump = BUILD / f"{stem}.{config}.dump"
    dump.unlink(missing_ok=True)
    cmd = ["vvp", "-n", str(vvp), f"+imem={imem}", f"+dmem={dmem}", f"+dump={dump}",
           f"+max_cycles={max_cycles}"]
    if trace:
        cmd.append(f"+trace={trace}")
    if vcd:
        cmd.append(f"+vcd={vcd}")
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, check=False)
    if proc.returncode or "FAIL" in proc.stdout or not dump.exists():
        raise SimError(f"{stem} on {config} failed:\n{proc.stdout}\n{proc.stderr}")
    return parse_dump(dump.read_text())


def check(prog: Program, config: str, stem: str = "prog") -> SimResult:
    """Simulate and compare every register and data word with the ISS; raise on mismatch."""
    ref = run(prog)
    got = simulate(prog, config, stem)
    errors = [f"x{i}: rtl 0x{got.regs[i]:08x} iss 0x{ref.regs[i]:08x}"
              for i in range(32) if got.regs[i] != ref.regs[i]]
    errors += [f"mem[{i}]: rtl 0x{got.dmem[i]:08x} iss 0x{ref.dmem[i]:08x}"
               for i in range(DMEM_WORDS) if got.dmem[i] != ref.dmem[i]]
    if got.instret != ref.instret:
        errors.append(f"instret: rtl {got.instret} iss {ref.instret}")
    if errors:
        raise SimError(f"{stem} on {config} disagrees with the ISS:\n  " + "\n  ".join(errors))
    return got


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run a program on the RTL and check it against the ISS")
    ap.add_argument("source", type=Path)
    ap.add_argument("--config", choices=CONFIGS, default="pipe_fwd")
    ap.add_argument("--trace", type=Path, help="write a per cycle pipeline trace")
    ap.add_argument("--vcd", type=Path, help="write a waveform file for GTKWave or Surfer")
    args = ap.parse_args(argv)
    prog = assemble(args.source.read_text())
    stem = args.source.stem
    try:
        res = check(prog, args.config, stem)
        if args.trace or args.vcd:
            simulate(prog, args.config, stem, trace=args.trace, vcd=args.vcd)
    except SimError as e:
        print(e, file=sys.stderr)
        return 1
    print(f"PASS {stem} on {args.config}: cycles={res.cycles} instret={res.instret} "
          f"CPI={res.cpi:.3f} stalls={res.stalls} flushes={res.flushes}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
