<!-- ABOUTME: Trishit's verification viva preparation for issue #2 and report Section V. -->
<!-- ABOUTME: Explains the ISS comparison, new directed tests and captured pipeline hazards. -->
# Viva notes: Trishit

I own Section V, Verification. These are preparation notes; rehearse the answers and
trace the signals personally before the viva.

## Explain the verification flow

Assembly -> assembler -> instruction/data images -> shared RTL testbench.
The same assembled program runs on the Python ISS. `tools.sim.check` compares
all registers, all data-memory words and retired instruction count at termination.
The testbench stops when ecall reaches retirement, and rejects illegal instructions
or a timeout. The assembler and ISS also have tests with independent expected values.

The suite checks single-cycle, pipeline without forwarding and pipeline with
forwarding. Directed programs isolate cases; constrained-random programs combine
loads, stores, arithmetic and forward branches using a small register set so
register dependencies are common. Benchmarks check longer executions.

**What does passing prove?** Agreement on these programs and final architectural
states. It is not a proof for all instruction sequences. A transient wrong write
that is later overwritten may escape final-state comparison. More coverage could
come from comparing each retirement with the reference, plus assertions on pipeline
valid bits and side effects.

## My two directed tests

`store_load_same_address.s`: x1 is the byte address 16. Store 55 and immediately
reload into x3; overwrite with -7 and reload into x5. x3 must be 55, x5 must be
0xfffffff9, and x6 must be 48, also stored at address 20. This catches a stale
memory read or incorrect forwarding of store data. The immediate consumer of x5
also creates a load-use dependency.

`consecutive_loads_same_rd.s`: initial words are 11, 29 and -5. Two loads write
x1 consecutively, then add x1 to itself. x1 must end as 29 and x2 as 58, also
stored at address 12. A second pair writes x3, followed by addi; x3 must be
0xfffffffb and x4 0xfffffffc, also stored at address 16. Forwarding an older load
rather than the latest writer gives a different final state. Distinct source
values are essential: equal values would hide the bug.

The suite finds both files automatically and compares each on all CPUs. It also
checks the cycle identity for both pipeline modes. On this machine the complete
suite passed with 239 tests; `make lint` passed too.

## Walk through the captured hazard demo

Reproduce with `make demo`, then open the command views in `docs/waveforms/`.
PC values in the screenshots are hexadecimal byte addresses; selectors are numeric.
Read every PC with its stage valid signal: an invalid stage's stale PC is not an
instruction that will execute.

- **Forwarding:** at 45–55 ns, EX PC is 0x04 (add x2,x1,x1), MEM PC is 0x00
  (addi x1,x0,5). fwd_a and fwd_b are both 2, selecting EX/MEM. Waiting for
  register writeback is unnecessary. Result: x2 = 10.
- **Load-use:** stall is high at 55–65 ns with the load in EX and its consumer
  held at ID PC 0x0c. IF PC 0x10 also holds. At the next edge EX valid is
  cleared, creating a bubble. At 75–85 ns the add executes and fwd_a = 1
  takes the load's value from MEM/WB. x3 = 7, so x4 = 12.
- **Branch flush:** at 85–95 ns, EX PC 0x10 is beq x4,x4 and flush is high.
  After the edge IF redirects to 0x1c, ID and EX are invalid. Instructions at
  PCs 0x14 and 0x18 must not write x5 or x6. The target stores x4 at address 4.

The simulation uses an artificial clock for functional checking. Its period is
not the measured FPGA maximum frequency; performance numbers come from results/.

## Answers to practise aloud

**Why does a load need a stall even with forwarding?** Its data is available after
MEM, but the immediate consumer needs it in EX. One bubble moves the consumer
far enough back to use MEM/WB.

**Why EX/MEM before MEM/WB?** It is the more recent writer when both match. A load
must still wait for actual memory data rather than forwarding its address.

**Why two flushed slots?** A branch resolves in EX with younger instructions in
IF and ID. Both must be invalidated when the branch is taken.

**How do I check the cycle count?** For these five-stage pipelines:
cycles = retired instructions + 4 fill cycles + stalls + 2 * taken branches.
`test_pipeline_cycle_identity` checks this on each program in both pipeline modes.

**Name a bug the project caught.** A forwarding function called from assign read
module signals not passed as arguments. Changes to those signals did not trigger
reevaluation, leaving stale selectors. The ISS comparison exposed wrong outcomes;
the project changed that combinational logic to always @(*).

**Why not just inspect a waveform?** Waveforms explain the timing of a chosen run.
The ISS comparisons automate architectural checks across many runs. We need both
a repeatable check and a way to diagnose why it failed.
