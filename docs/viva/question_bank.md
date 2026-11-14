# Viva question bank

Likely questions with short answers grounded in our design. Learn the reasoning, not the words.
Every number comes from `results/`.

## Pipelining basics

**Why does pipelining speed things up?** Several instructions are in flight at once, one per
stage, so ideally one instruction finishes every cycle (CPI 1) while the clock period only has to
cover the slowest stage, not the whole instruction.

**Define CPI, IPC and throughput.** CPI = cycles / instructions. IPC = 1 / CPI. Throughput =
clock frequency x IPC, in instructions per second.

**What is the iron law?** Time = instructions x CPI / frequency. Our speedup over single-cycle is
(f_pipe / f_single) / CPI_pipe, because single-cycle CPI is exactly 1.

**Why 4 extra cycles at the start?** The first instruction needs 5 cycles to reach WB; after that
one finishes per cycle. Cycles = N + 4 + stalls + 2 x taken branches, and our tests check this on
every program.

## Our design

**What does each pipeline register hold?** Report Table III. Key idea: control is decoded once in
ID and travels with the instruction; each stage uses only what it needs.

**What is a bubble in our design?** An entry with valid = 0 and all control bits 0. It writes
nothing, stores nothing, never branches. Its data fields are garbage, and that is fine.

**Why clear only control bits on a flush?** Clearing data too put a reset on about 140 flip-flops
at the end of the slowest path (branch decision to flush). Clearing control only raised Fmax from
76 to 84 MHz with identical behaviour.

**How does the register file avoid a hazard at distance 3?** Write-through: when WB writes the
register ID is reading in the same cycle, the read returns the new value. It is the hardware form of
"write in the first half, read in the second half".

**Why can't the single-cycle CPU use write-through?** Its write data depends on its read data in the
same cycle, so the bypass mux would form a combinational loop. Yosys found exactly that.

**What are `uses_rs1` and `uses_rs2` for?** In I-type instructions the rs2 field holds immediate
bits. Without these flags the hazard unit would stall on registers the instruction never reads.
Test `false_hazard.s` checks it.

**How do you stop at `ecall`?** When `ecall` leaves ID (and is not being flushed), the hazard unit
freezes the PC and feeds bubbles. The program ends when `ecall` reaches WB. Test `halt_shadow.s`
checks that a store after `ecall` never happens.

## Hazards

**Name the three hazard types and how we handle each.** Structural: separate instruction and data
memories, register file with 2 read and 1 write port. Data: forwarding plus a load-use stall (or
stall on every RAW without forwarding). Control: predict not taken, resolve in EX, flush 2.

**Why does a load still stall with forwarding?** The loaded value exists only at the end of MEM. The
next instruction needs it at the start of EX, one cycle earlier. After one bubble, it is forwarded
from MEM/WB.

**Why does EX/MEM have priority over MEM/WB in forwarding?** If both match, EX/MEM holds the newer
value (the more recent writer). Test: `raw_hazards.s` writes x7 twice in a row.

**Why is the branch penalty 2 cycles?** The branch resolves in EX; by then two younger instructions
(in IF and ID) were fetched on the not-taken path and must be flushed.

**How would you cut it?** Resolve branches in ID (penalty 1, but needs forwarding into ID and a
comparator there, on a longer path) or predict branches (project 5 territory).

## Verification

**How do you know the CPU is correct?** A Python ISS is the reference. After every program we compare
all 32 registers, all 256 data words and the instruction count. 11 directed tests, 5 benchmarks and 40
constrained-random programs run on all three CPUs: 239 checks.

**Why constrained-random?** Hand-written tests only cover cases we thought of. Random programs on six
registers create hazards at every distance with loads, stores and branches mixed in.

**Name a bug your flow caught.** Forwarding written as Verilog functions called from `assign`:
those only re-evaluate when their arguments change, so the forwarding selects went stale. The ISS
comparison failed on the first program.

## Synthesis and performance

**What FPGA and tools?** Lattice ECP5 LFE5U-25F, speed grade 6, Yosys and nextpnr, median of 5
placement seeds.

**Fmax of each design?** Single-cycle 58.75 MHz, pipeline without forwarding 113.86, with forwarding
83.89.

**Why is the forwarding pipeline's clock lower?** Its critical path is: forwarding compare, forwarding
mux, branch comparator, taken signal, flush of the pipeline registers. Without forwarding, the
compare and mux are not on that path.

**Why is the pipeline not 5 times faster?** Unbalanced stages: the longest stage (EX) takes 8.8 ns
without forwarding and 11.9 ns with it, against the single-cycle 17.0 ns, so about half the
single-cycle path, not a fifth. And every loop iteration pays a 2 cycle branch penalty.

**When does the pipeline actually win?** With forwarding, when CPI is below 1.43 (the clock ratio).
dep_chain, fibonacci, indep_ops (CPI about 1.26 to 1.29) win by 1.11 to 1.14x. bubble_sort (1.45) and
sum_array (1.58) lose slightly.

**Why did you not use block RAM?** Yosys folded our pipeline registers into the block RAMs (legal,
saves flip-flops), but then the block RAM's clock-to-output delay starts the ID stage and the
forwarding path. With LUT memories every pipeline register stays a real flip-flop. Block RAM numbers
are in the report for comparison.

**What would you do next?** Branch prediction or ID-stage branches, rebalance EX, and a sixth stage or
registered address to use block RAM for larger memories.
