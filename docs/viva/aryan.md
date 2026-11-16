<!-- ABOUTME: Viva preparation notes for Section III (Single-Cycle Design) by Aryan Kumar. -->
<!-- ABOUTME: Covers datapath flow, control logic, timing analysis, and viva defense questions. -->

# Viva notes: Aryan

I own Section III, Instruction Set and Single-Cycle Design (`report/sections/single_cycle.tex`),
and the underlying modules: `rtl/single_cycle/cpu_single.v` and shared common blocks
`rtl/common/control.v`, `alu.v`, `imm_gen.v`, and `regfile.v`.

---

## 1. The Single-Cycle Datapath, on the whiteboard

In the single-cycle design, every instruction finishes in exactly **one long clock cycle** ($\text{CPI} = 1.00$).
The entire datapath is combinational except for state updates (PC, register file, and data memory writes)
which latch synchronously on the rising clock edge.

```
       +----------------------- taken: PC + imm --------------------------+
       |                                                                  |
       v                                                                  |
   [PC Mux] ---> [ PC ] ---> [ Instruction Mem ] ---> [ Control Unit ]    |
       ^            |               |                 (RegWr, ALUSrc,     |
       |            |               |                  MemWr, etc.)       |
    [ +4 ] <--------+               |                                     |
                                    +---------------> [ Imm Gen ]         |
                                    |                      |              |
                                    v                      v              |
                             [ Reg File ] ----------> [ALU Src Mux]       |
                              (rs1, rs2)                   |              |
                                |       |                  v              |
                                |       +-----------> [ 32-bit ALU ]      |
                                |       |               |        |        |
                                v       v               |        | (alu_y)|
                             [ Branch == ]              v        |        |
                                    |            [ Data Memory ] |        |
                                    v                   |        |        |
                                  taken                 v        v        |
                                    |            [      WB Mux     ]      |
                                    |                   |                 |
                                    |                   v (wb_data)       |
                                    |            [ Regfile wdata ]        |
                                    |                                     |
                                    +-------------------------------------+
```

### Step-by-Step Flow:
1. **Fetch (IF):** PC addresses the 256-word instruction memory (`imem.v`), yielding a 32-bit instruction word.
2. **Decode (ID):**
   - Opcode bits `[6:0]`, `funct3`, and `funct7` feed `control.v`.
   - `imm_gen.v` sign-extends immediates: 12-bit for I and S formats, and 13-bit (with bit 0 hardwired to 0) for B-format branches.
   - `regfile.v` reads source operands `rs1_val = regs[instr[19:15]]` and `rs2_val = regs[instr[24:20]]` asynchronously.
3. **Execute (EX):**
   - The ALU operand B multiplexer picks `rs2_val` (`alu_src = 0`, R-type/branch) or `imm` (`alu_src = 1`, I-type/load/store).
   - 32-bit `alu.v` computes the result (`alu_y`) based on `alu_op`.
   - In parallel, dedicated branch comparator checks `(rs1_val == rs2_val) ^ branch_ne`. If true and `branch` is asserted, `taken` selects $\text{PC} + \text{imm}$; otherwise $\text{PC} + 4$.
4. **Memory (MEM):**
   - `dmem.v` uses `alu_y` as effective address. If `mem_write` is high and CPU not stopped, writes `rs2_val`.
   - On loads (`lw`), reads word `mem_rdata`.
5. **Write-Back (WB):**
   - WB multiplexer selects between `alu_y` and `mem_rdata` using `mem_read`.
   - `regfile` latches `wb_data` into register `instr[11:7]` on the rising clock edge (suppressed if `rd == x0` or `stopped`).

---

## 2. Control Unit Truth Table (`control.v`)

| Instruction Class | `RegWr` | `ALUSrc` | `MemRd` | `MemWr` | `Branch` | `BranchNE` | `ALUOp` | `uses_rs1` | `uses_rs2` |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **R-type** (`add`, `sub`, etc.) | 1 | 0 (reg) | 0 | 0 | 0 | 0 | funct-based | 1 | 1 |
| **I-type** (`addi`, `andi`, etc.) | 1 | 1 (imm) | 0 | 0 | 0 | 0 | funct3-based | 1 | 0 |
| **Load** (`lw`) | 1 | 1 (imm) | 1 | 0 | 0 | 0 | `ALU_ADD` | 1 | 0 |
| **Store** (`sw`) | 0 | 1 (imm) | 0 | 1 | 0 | 0 | `ALU_ADD` | 1 | 1 |
| **Branch** (`beq`) | 0 | 0 (reg) | 0 | 0 | 1 | 0 | `ALU_ADD` | 1 | 1 |
| **Branch** (`bne`) | 0 | 0 (reg) | 0 | 0 | 1 | 1 | `ALU_ADD` | 1 | 1 |
| **System** (`ecall`) | 0 | 0 | 0 | 0 | 0 | 0 | `ALU_ADD` | 0 | 0 |

*Note on Branches:* Because branch conditions are evaluated by a dedicated equality comparator, `alu_op` is not needed for branches and stays at its default value (`ALU_ADD`).

---

## 3. Critical Path Analysis, on the whiteboard

From `results/synth.csv` and `results/synth_runs.csv`:
- **Single-cycle $F_{\max}$:** **58.75 MHz** (median of 5 seeds, range 57.68 to 60.15 MHz).
- **Clock Period:** $T = \frac{1}{58.75\text{ MHz}} = \mathbf{17.0\text{ ns}}$.
- **Worst-case Path:** Load word (`lw`).
  `synth_runs.csv` pinpoints the start and end registers:
  - Start: `cpu.core.immg.instr_TRELLIS_FF_Q` (PC moved to ROM output during synthesis).
  - End: `cpu.core.rf.regs.*$DPRAM_COMB*` (register file RAM write port).

```
[ instr (retimed PC) ] ---> [ Regfile Read ] ---> [ ALU Addr ] ---> [ DMem Read ] ---> [ WB Mux ] ---> [ Regfile Setup ]
       (Start)                                                                                                (End)
```

### Why does this limit performance?
In a single-cycle CPU, the clock cycle must accommodate this worst-case **17.0 ns** path.
Simple instructions like `addi` or `add` do not access data memory, but must still wait for the full 17.0 ns cycle.
Slicing this into a 5-stage pipeline isolates the stages with registers, raising $F_{\max}$ to 113.86 MHz (no fwd) and 83.89 MHz (fwd).

---

## 4. Key Design Decisions & Nuances

### A. Dedicated Branch Comparator vs ALU
- We do not use the ALU to subtract and check zero for branches in single-cycle.
- `cpu_single.v` uses a direct comparator: `(rs1_val == rs2_val) ^ branch_ne`.
- Dedicated branch target adder: $\text{PC} + \text{imm}$ runs in parallel with ALU execution.
- Keeps branch evaluation completely separate and avoids complicating ALU control.

### B. Purpose of `uses_rs1` and `uses_rs2`
- In I-type instructions, bits `instr[24:20]` hold immediate bits (`imm[4:0]`), not a register index.
- If the control unit didn't signal that `rs2` is unused (`uses_rs2 = 0`), the pipelined CPU's hazard unit would see a RAW hazard whenever an earlier instruction wrote to register number matching `imm[4:0]`, causing false stalls!
- Verified by our directed test: `programs/tests/false_hazard.s`.

### C. Register File Write-Through (`WRITE_THROUGH = 0` vs `1`)
- In `rtl/common/regfile.v`, write-through is disabled (`WRITE_THROUGH = 0`) for `cpu_single.v`.
- **Why?** In single-cycle, write data (`wb_data`) combinationally depends on read data (`rs1_val`, `rs2_val`). If write-through bypass mux were active, it would create an illegal combinational loop:
  `rdata -> ALU -> dmem -> wb_data -> bypass_mux -> rdata`.
- In the pipelined CPU (`cpu_pipeline.v`), write-through is enabled (`WRITE_THROUGH = 1`) to naturally handle distance-3 data hazards between WB and ID stages ("write in first half, read in second half of the cycle").

### D. Zero Register (`x0`) Guarantee
- In RISC-V, register `x0` is hardwired to zero.
- In `regfile.v`:
  - Asynchronous read: `(raddr1 == 5'd0) ? 32'b0 : regs[raddr1]`
  - Synchronous write: `if (we && waddr != 5'd0) regs[waddr] <= wdata;`
- Tested by `programs/tests/x0_reg.s`.

### E. Halting with `ecall`
- `ecall` opcode `7'b1110011` with `instr == 32'h00000073`.
- `control.v` asserts `halt = 1`.
- `cpu_single.v` sets `stopped <= 1'b1`, stopping PC advancement and disabling `do_write` and memory writes (`mem_write && !stopped`), preventing any instruction shadow from altering machine state.

---

## 5. Likely Viva Traps & Sharp Answers

- **Q: "Is single-cycle always slower than pipelining?"**
  - **A:** No! Execution time depends on the Iron Law: $\text{Time} = \frac{N \times \text{CPI}}{f}$.
    Single-cycle has $\text{CPI} = 1.00$ by construction. Pipelining increases clock frequency, but also increases CPI due to branch flushes (2 cycles each) and hazard stalls.
    From `results/performance.csv`:
    - Single-cycle **beats both pipelined designs** on `bubble_sort` (speedups 0.94x for no-fwd, 0.98x for fwd) and `sum_array` (0.90x and 0.90x), because tight loops suffer heavy 2-cycle branch flush penalties and load-use stalls that outweigh the clock frequency gain.
    - Single-cycle also **beats the pipeline without forwarding** on `dep_chain` (0.71x), where back-to-back RAW stalls balloon CPI to 2.74.
    - The pipeline only wins when its CPI is lower than its clock ratio: $\text{CPI} < 1.43$ for forwarding, or $\text{CPI} < 1.94$ without forwarding.

- **Q: "What are the CPI ranges for the two pipelined designs?"**
  - **A:**
    - Pipeline with forwarding: **1.26 to 1.58** (stalls only on load-use hazards and 2-cycle branch flushes).
    - Pipeline without forwarding: **1.51 to 2.74** (stalls on every RAW data hazard plus 2-cycle branch flushes).

- **Q: "Why does `imm_gen` not need a control signal from the control unit?"**
  - **A:** RISC-V instruction formats place immediate bits in fixed locations uniquely identified by opcode bits `instr[6:0]`. Store instructions (`0100011`) are S-type, branch instructions (`1100011`) are B-type, and all other supported immediate instructions (loads, ALU immediates) use the standard I-type format. Decoding directly from `instr[6:0]` eliminates extra control muxes.

- **Q: "Why are instruction and data memories separate (Harvard)?"**
  - **A:** To prevent structural hazards. In a single-cycle CPU, an instruction must be fetched from instruction memory in the very same cycle that a `lw` or `sw` reads or writes data memory. A unified single-port memory would cause a structural conflict.
