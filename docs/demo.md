# Demo and slides script

About 4 minutes of slides, then a 1 minute live demo (5 minutes in all, for the Phase I video). Every figure is in `figures/`.

## Slides (Navodit builds, each person presents their part)

1. Title, team and project idea (Navodit)
2. The question: how much of the ideal 5x survives in post-route FPGA timing (Navodit)
3. Why pipeline: the iron law, T = N x CPI / f, and the clock ratios (Navodit)
4. Instruction subset and single-cycle datapath, `figures/architecture_single.png` (Aryan)
5. Five-stage datapath, `figures/architecture_pipeline.png` (Sarvesh)
6. Hazards and how we handle them: forwarding, load-use stall, branch flush (Sarvesh)
7. Pipeline diagrams, `figures/pipeline_diagram_pipe_fwd.png` next to `pipeline_diagram_pipe_nofwd.png` (Trishit)
8. Verification: ISS comparison, directed and random tests, 248 checks, an EX/MEM forward in Surfer (Trishit)
9. Synthesis: `figures/fmax.png`, Fmax, ratios and resources (Husain)
10. CPI: `figures/cpi_breakdown.png` (Husain)
11. Speedup and why it is not 5x: `figures/speedup.png` (Husain)
12. Conclusion and Phase II plan (Navodit)

The exported deck is `slides/phase1-slides.pdf`.

## Live demo

```sh
make test       # 248 passed in about 3 s: every program, every CPU, checked against the ISS
make demo       # hazard demo: cycles, CPI, stalls, flushes; writes build/hazard_demo.vcd
uv run python -m tools.sim programs/tests/hazard_demo.s --config pipe_nofwd   # 19 cycles instead of 14
surfer build/hazard_demo.vcd    # or gtkwave; add tb_cpu.dut.stall, flush, fwd_a, id_pc, ex_pc
```

Point at: the stall in cycle 5, the two flushed instructions in cycle 9, `fwd_a` switching to EX/MEM.
