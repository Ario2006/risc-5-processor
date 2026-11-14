# Viva notes: Husain

I own Section VI, Results. Every number here comes from `results/`, and I reran
`make synth perf figures` on 14 Nov: all four CSVs came out byte-identical.

## Iron law, on the whiteboard

    T = N x CPI / f

Single-cycle CPI is exactly 1, so the speedup of a pipeline is just

    S = (f_pipe / f_single) / CPI_pipe

So the pipeline only wins when its CPI is below its clock ratio.

| CPU | Fmax (MHz) | Period (ns) | Clock ratio | Wins when CPI < |
|---|---|---|---|---|
| Single-cycle | 58.75 | 17.0 | 1.00 | |
| Pipe, no fwd | 113.86 | 8.8 | 1.94 | 1.94 |
| Pipe, fwd | 83.89 | 11.9 | 1.43 | 1.43 |

Worked example, `dep_chain` with forwarding: 1.43 / 1.26 = 1.14x. CSV says 1.135. Same answer.

Cycle count: `C = N + 4 + stalls + 2 x taken branches`. Check with bubble sort, forwarding:
591 + 4 + 66 + 2 x 98 = 857. That's the `cycles` column in `cpi.csv`.

## Critical paths, on the whiteboard

These come from `results/synth_runs.csv` (start and end register of nextpnr's worst path).

**Single-cycle (17.0 ns).** Starts at the fetched instruction (`immg.instr` in the netlist),
ends at the register file write. So it's the whole datapath in one cycle: decode, regfile
read, ALU, data memory, write back.

    instr -> imm gen / regfile read -> ALU -> dmem -> wb mux -> regfile

**Pipeline, no forwarding (8.8 ns).** Starts at ID/EX (`imm`, `rs2_val`), ends at EX/MEM
(`ex_mem_value`). That's EX on its own: operand mux into the ALU into EX/MEM.

    ID/EX -> ALU src mux -> ALU -> EX/MEM

**Pipeline, forwarding (11.9 ns).** Starts at the MEM/WB destination register (`wb_rd`) or
ID/EX `rs1`/`rs2`, ends at the flush or stall of IF/ID and ID/EX (`valid`, `mem_read`, `pc`).

    rd compare -> fwd mux -> branch compare -> taken -> flush IF/ID, ID/EX

The forwarding compare and mux sit in front of the branch comparator, and the branch decides
whether to flush. Without forwarding they aren't on that path, so that clock is 1.94x not 1.43x.

## Why not 5x faster

1. Stages aren't balanced. The longest stage is 8.8 ns of a 17.0 ns path, about half, not a
   fifth. It's EX in both pipelines.
2. Branches cost 2 cycles each, and every loop iteration ends in one. That adds 0.23 to 0.35
   to CPI on its own (bubble sort: 196 flush cycles / 591 instructions = 0.33).

Fixes: resolve branches in ID (1-cycle penalty) or predict them, and split EX.

## Block RAM vs LUT RAM

With block RAM, Yosys folds the pipeline register into the RAM. Legal, saves flip-flops, but
now the RAM's clock-to-output delay starts the ID stage and the forwarding path. Fmax drops to
42.2 / 72.2 / 59.1 MHz. So we use LUT RAM for both 256-word memories.

I took the 5.6 ns figure out of the report because nothing in `results/` produces it. If asked
for the exact delay, say it's in the ECP5 datasheet timing tables, not something we measured.

## Traps

- **"So forwarding is always better?"** No. Without forwarding wins on `indep_ops` (1.29x vs
  1.13x) and `fibonacci` (1.14x vs 1.11x), because the clock is faster and there's little to
  forward. Forwarding wins on worst case: 0.90x against 0.71x.
- **"Why does bubble sort lose with forwarding?"** CPI 1.45 > 1.43. The 66 load-use stalls
  (one per inner iteration) plus 98 flushes push it just over.
- **"Why median of 5 seeds?"** nextpnr placement is random. The single-cycle range is 57.7 to
  60.2 MHz, so one seed could swing the ratio.
- **"Is CPI 1.00 for single-cycle measured?"** It's by construction, one instruction per cycle.
  `cpi.csv` shows cycles = instret for every benchmark.
