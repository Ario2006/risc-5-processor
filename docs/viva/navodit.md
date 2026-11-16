<!-- ABOUTME: Navodit's viva preparation for issue #4: abstract, Sections I, II and VII, slides and video. -->
<!-- ABOUTME: Pipelining basics, the iron law, related work and the Phase II plan; numbers from results/. -->
# Viva notes: Navodit

I own the abstract, Section I (Introduction), Section II (Literature Review and Background),
Section VII (Conclusion, Current Progress and Phase II Plan), the slides and the Phase I video.

## The project in 30 seconds

Three CPUs for the same 18-instruction RV32I subset, same tests, same FPGA:
single-cycle, 5-stage pipeline without forwarding, 5-stage pipeline with forwarding.
The question: a 5-stage pipeline is ideally 5x faster, so how much survives in practice?
The answer: 0.71x to 1.29x. Two reasons: the stages are not balanced (EX is the longest),
and every taken branch costs 2 cycles, once per loop iteration.

## Pipelining basics

**What is pipelining?** Like laundry: while one load dries, the next one washes. One
instruction still takes 5 steps (latency does not drop), but one finishes every cycle
(throughput goes up), and the clock only has to cover one stage.

**The five stages.**

| Stage | Does |
|---|---|
| IF | fetch the instruction at PC, PC + 4 |
| ID | decode, read rs1 and rs2, build the immediate |
| EX | ALU, branch compare and branch target |
| MEM | `lw` reads, `sw` writes data memory |
| WB | write the result into rd |

**Why not 5x?** The clock is set by the slowest stage, not by an average one, and hazards
add cycles that a single-cycle CPU never pays.

## Iron law, on the whiteboard

    T = N x CPI / f
    S = (f_pipe / f_single) / CPI_pipe      (single-cycle CPI is exactly 1)

| CPU | Fmax (MHz) | Clock ratio | Wins when CPI < |
|---|---|---|---|
| Single-cycle | 58.75 | 1.00 | |
| Pipe, no fwd | 113.86 | 1.94 | 1.94 |
| Pipe, fwd | 83.89 | 1.43 | 1.43 |

Worked examples (with forwarding), checked against `performance.csv`:
- `dep_chain`: 1.43 / 1.26 = 1.135. Faster.
- `bubble_sort`: 1.43 / 1.45 = 0.985. Slightly slower, because CPI is just above 1.43.

Cycle count: `C = N + 4 + stalls + 2 x taken branches`.
`sum_array` with forwarding: 86 + 4 + 16 + 2 x 15 = 136. That is the `cycles` column in `cpi.csv`.

## The three hazards

| Hazard | Cause | Our fix |
|---|---|---|
| Structural | two stages need one resource | separate instruction and data memories, register file with 2 read and 1 write port |
| Data | an instruction reads a register an older one has not written yet | forwarding, plus one stall for load-use (or stall on every RAW without forwarding) |
| Control | the next PC after a branch is known only in EX | predict not taken, flush 2 instructions if taken |

## Literature review: one line per reference

- **MIPS (Hennessy et al., 1982):** "Microprocessor without Interlocked Pipe Stages". The
  compiler had to avoid hazards. We detect them in hardware with a hazard unit instead.
- **Patterson and Hennessy:** the textbook 5-stage pipeline, forwarding unit and load-use stall.
  Our design follows it.
- **Hennessy and Patterson:** the iron law we use for every result.
- **Asanovic and Patterson (2014):** the case for a free, open ISA. RISC-V came from Berkeley.
- **PicoRV32:** size-optimised, high clock, but about 4 cycles per instruction (CPI about 4.1
  on Dhrystone). Not a classic pipeline.
- **Ibex (lowRISC):** 2-stage pipeline, fetch then combined decode and execute.
- **Rocket (Berkeley):** 5-stage in-order like ours, plus caches and branch prediction; has been
  manufactured and boots Linux.
- **Smith (1981):** studied branch prediction; dynamic prediction (two-bit counters) beats
  fixed rules.

Why these: they place our design on a map. PicoRV32 is smaller and slower, Ibex has fewer
stages, Rocket has the same stages with extras. Ours is the bare 5 stages, so each hazard's
cost shows up on its own.

## Phase II plan, and how to defend it

Every item fixes a loss we measured.

1. **Branches.** Flushes add 0.23 to 0.35 to CPI (bubble sort: 2 x 98 / 591 = 0.33).
   - Resolve branches in ID: penalty 2 -> 1 cycle, but the comparator and its forwarding
     paths move into ID, which can lengthen that stage.
   - Two-bit counter predictor: a loop branch is taken every time except the last, so the
     counter learns "taken" and mispredicts about once per loop. It takes two wrong guesses
     in a row to flip the prediction.
   - Branch target buffer: remembers the target, so IF can jump in the same cycle.
2. **Stage balance.** The critical path, set by EX and the branch decision, is 8.8 ns without
   forwarding and 11.9 ns with it: 52% and 70% of the 17.0 ns single-cycle path, not 20%.
   These are 1 / Fmax, the whole critical path, not a pure EX delay. Split EX or move the
   branch decision out.
3. **Instruction set.** `jal` and `jalr` are needed for function calls, and byte and halfword
   loads for C strings and chars. Then we can run compiled C, not just hand-written assembly.
4. **Hardware.** Run `synth/fpga_top.v` on a real ECP5 board.

## Traps

- **"So is the pipeline faster?"** It depends on the program. With forwarding it wins on
  `dep_chain`, `fibonacci` and `indep_ops` (1.11x to 1.14x) and loses on `bubble_sort` (0.98x)
  and `sum_array` (0.90x).
- **"Why is the forwarding pipeline's clock lower?"** The forwarding compare and mux sit in
  front of the branch comparator, and the branch decides the flush. That path sets the clock.
- **"Why not add branch prediction now?"** Phase I is the baseline: measure the cost first,
  then fix it. Branch prediction is out of scope for Phase I (ROADMAP).
- **"Is single-cycle CPI 1.00 measured?"** It is 1 by construction; `cpi.csv` shows cycles
  equal to instructions for every benchmark.
- **"What is the difference between latency and throughput?"** Latency is how long one
  instruction takes (5 cycles in the pipeline). Throughput is how many finish per second
  (f x IPC). Pipelining improves throughput, not latency.
