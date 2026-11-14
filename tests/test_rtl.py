# ABOUTME: Runs every program on all three Verilog CPUs and compares final state with the ISS.
# ABOUTME: Also checks the performance counters: stall counts, CPI of 1 and the cycle identity.
from pathlib import Path

import pytest

from tools.randprog import random_program
from tools.rvasm import assemble
from tools.sim import CONFIGS, check, simulate

ROOT = Path(__file__).resolve().parent.parent
PROGRAMS = sorted((ROOT / "programs").glob("*/*.s"))
RANDOM_SEEDS = range(40)


@pytest.mark.parametrize("config", CONFIGS)
@pytest.mark.parametrize("path", PROGRAMS, ids=lambda p: f"{p.parent.name}/{p.stem}")
def test_program_matches_iss(path, config):
    check(assemble(path.read_text()), config, path.stem)


@pytest.mark.parametrize("config", CONFIGS)
@pytest.mark.parametrize("seed", RANDOM_SEEDS)
def test_random_program_matches_iss(seed, config):
    check(assemble(random_program(seed)), config, f"random{seed}")


def load(name: str):
    return assemble((ROOT / "programs/tests" / f"{name}.s").read_text())


def test_single_cycle_cpi_is_exactly_one():
    res = simulate(assemble((ROOT / "programs/bench/sum_array.s").read_text()), "single", "cpi1")
    assert res.cycles == res.instret


@pytest.mark.parametrize("config", ["pipe_fwd", "pipe_nofwd"])
@pytest.mark.parametrize("path", PROGRAMS, ids=lambda p: p.stem)
def test_pipeline_cycle_identity(path, config):
    """Every lost cycle is a fill cycle, a stall or a branch flush: nothing unexplained."""
    res = simulate(assemble(path.read_text()), config, f"id_{path.stem}")
    assert res.cycles == res.instret + 4 + res.stalls + 2 * res.flushes


def test_forwarding_stalls_once_per_load_use():
    res = simulate(load("load_use"), "pipe_fwd", "lu")
    assert res.stalls == res.load_use == 5


def test_immediate_bits_do_not_cause_false_stalls():
    res = simulate(load("false_hazard"), "pipe_fwd", "fh")
    assert res.stalls == 0


def test_forwarding_removes_alu_stalls():
    res = simulate(load("raw_hazards"), "pipe_fwd", "raw")
    assert res.stalls == 0


def test_taken_branches_flush_two_slots():
    res = simulate(load("branches"), "pipe_fwd", "br")
    assert res.flushes == 5  # jumps to t1 to t5 are taken; the bne to bad is not


@pytest.mark.parametrize("config", CONFIGS)
@pytest.mark.parametrize("name,registers,memory", [
    ("store_load_same_address", {3: 55, 5: 0xfffffff9, 6: 48}, {4: 0xfffffff9, 5: 48}),
    ("consecutive_loads_same_rd", {1: 29, 2: 58, 3: 0xfffffffb, 4: 0xfffffffc,
                                   7: 29, 8: 58}, {3: 58, 4: 0xfffffffc, 5: 58}),
    ("branches", {5: 7, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 42}, {0: 0}),
])
def test_directed_hand_calculated_outcomes(config, name, registers, memory):
    result = check(load(name), config, f"expected_{name}")
    for index, expected in registers.items():
        assert result.regs[index] == expected, f"x{index}"
    for index, expected in memory.items():
        assert result.dmem[index] == expected, f"memory word {index}"
