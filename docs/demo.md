# Demo and slides script

About 8 minutes of slides, then a 3 minute live demo. Every figure is in `figures/`.

## Slides (Navodit builds, each person presents their part)

1. Title, team, objective from the brief (Navodit)
2. Why pipeline: the iron law, T = N x CPI / f (Navodit)
3. Instruction subset and single-cycle datapath, `figures/architecture_single.png` (Aryan)
4. Five-stage datapath, `figures/architecture_pipeline.png` (Sarvesh or Husain)
5. Hazards and how we handle them: forwarding, load-use stall, branch flush (Sarvesh or Husain)
6. Pipeline diagram, `figures/pipeline_diagram_pipe_fwd.png`, next to `pipeline_diagram_pipe_nofwd.png` (Trishit)
7. Verification: ISS comparison, directed and random tests, 229 checks, bugs we caught (Trishit)
8. Synthesis: `figures/fmax.png` and Table V (Husain)
9. CPI: `figures/cpi_breakdown.png` (Husain)
10. Speedup and why it is not 5x: `figures/speedup.png` (Husain)
11. Conclusion and future work (Navodit)

## Live demo

```sh
make test       # 229 passed in about 3 s: every program, every CPU, checked against the ISS
make demo       # hazard demo: cycles, CPI, stalls, flushes; writes build/hazard_demo.vcd
uv run python -m tools.sim programs/tests/hazard_demo.s --config pipe_nofwd   # 19 cycles instead of 14
surfer build/hazard_demo.vcd    # or gtkwave; add tb_cpu.dut.stall, flush, fwd_a, id_pc, ex_pc
```

Point at: the stall in cycle 5, the two flushed instructions in cycle 9, `fwd_a` switching to EX/MEM.
