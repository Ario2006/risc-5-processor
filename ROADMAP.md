# Roadmap

Submission: **16 November 2026**. Done means: merged to `main`, report section written in
your own words, viva notes written, and you can explain every line you own.

## Done (13 November)

- Single-cycle CPU and 5-stage pipeline (forwarding on and off), all modules from the brief
- Assembler, reference ISS, testbench, 229 automated checks, CI
- ECP5 synthesis and place and route, CPI, IPC, speedup study, all figures
- Full report draft (`report/main.pdf`) with every section

## Remaining, one issue each

| # | Owner | Task | Report section | Due |
|---|---|---|---|---|
| 1 | Sarvesh | Create the GitHub repo, push, open issues 2 to 6, review and merge PRs (Husain takes over review and merging from 14 Nov) | Pipeline (IV) | 14 Nov |
| 2 | Aryan | Check `control.v` and the single-cycle datapath against Table II and the RISC-V spec. Draw a single-cycle datapath diagram (draw.io or similar) to `figures/architecture_single.png` and add it to Section III. Rewrite Section III in your own words. | Single-cycle (III) | 15 Nov |
| 3 | Trishit | Install GTKWave or Surfer, run `make demo`, open `build/hazard_demo.vcd`, save 2 or 3 annotated screenshots (forward, load-use stall, flush) to `figures/`. Add 2 directed tests of your own to `programs/tests/` (ideas: store then load of the same address; two loads in a row into the same register). Rewrite Section V. | Verification (V) | 15 Nov |
| 4 | Husain | Run `make synth perf figures` on your laptop and confirm every number in Section VI matches `results/`. Learn the critical path answers in `docs/viva/question_bank.md` until you can draw them. Rewrite Section VI. | Results (VI) | 15 Nov |
| 5 | Navodit | Review the abstract and Sections I, II and VII, add 2 or 3 related references. Build the slides (10 to 12) from `figures/` following `docs/demo.md`. Export to `slides/`. | Intro, Background, Conclusion | 15 Nov |
| 6 | Everyone | Viva notes in `docs/viva/<name>.md`; rehearse with `docs/viva/question_bank.md` | | 15 Nov |
| 7 | Husain (from Sarvesh) | Final read of `report/main.pdf`, rebuild, tag the submission | | 16 Nov |

Optional, only if the lab has a board: run `synth/fpga_top.v` on a real ECP5 board (ULX3S or
Colorlight). That needs a pin constraint file for that board; ask Sarvesh or Husain first.

## Not in scope

Branch prediction (project 5), caches (projects 6 to 8), byte and halfword loads, `jal` and `jalr`.
The report names branch prediction as future work.
