<!-- ABOUTME: Reproduce the annotated Surfer 0.7 verification captures. -->
<!-- ABOUTME: Saved states specify exact time windows, markers and readable text. -->
# Verification captures

Run `make demo` from the repository root, then:

```sh
surfer build/hazard_demo.vcd -s docs/waveforms/forward.ron -c docs/waveforms/light.sucl
surfer build/hazard_demo.vcd -s docs/waveforms/load_use.ron -c docs/waveforms/light.sucl
surfer build/hazard_demo.vcd -s docs/waveforms/branch_flush.ron -c docs/waveforms/light.sucl
```

The captures use Surfer 0.7.0, its light+ theme and 2x UI text. Saved states select
33–67 ns, 43–92 ns and 73–112 ns respectively, including a small margin
around each event window to keep tick labels readable. Labeled markers identify forwarding,
stall/bubble/recovery, and flush/redirect boundaries. Screenshots contain the real
viewer output with window chrome excluded; the report displays them at full width.
The `.sucl` signal scripts remain useful for rebuilding views; use `.ron` states
for exact capture framing and nanosecond units. `make figures` does not overwrite
these GUI captures. Regenerate them if the RTL or hazard demo changes.

Selector 2 is EX/MEM, 1 is MEM/WB, and 0 is the register operand. Interpret selectors
only alongside stage validity. Simulation time is functional timing, not FPGA Fmax.
