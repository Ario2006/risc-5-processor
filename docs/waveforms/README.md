<!-- ABOUTME: Reproduction steps and interpretation for issue #2's Surfer captures. -->
<!-- ABOUTME: Documents screenshot provenance and the separate generated overview waveform. -->
# Verification captures

Run `make demo` from the repository root, then open any view:

```sh
surfer build/hazard_demo.vcd -c docs/waveforms/forward.sucl
surfer build/hazard_demo.vcd -c docs/waveforms/load_use.sucl
surfer build/hazard_demo.vcd -c docs/waveforms/branch_flush.sucl
```

The three `figures/waveform_*_annotated.png` files are actual Surfer 0.7.0
captures of this VCD. Named dividers identify the events; the report captions
explain the signals and PCs. The captures retain the full time range so the
recovery after each hazard is visible. `hazard_demo.sucl` opens a combined view.
The `*_valid` signals distinguish bubbles from stale PC fields.

Forwarding selector 2 means EX/MEM, 1 means MEM/WB and 0 means the register
operand. Inspect 45–55 ns for the dependent add, 55–65 ns for stall and
85–95 ns for flush. These times follow the testbench's clock/reset schedule;
they do not measure FPGA timing. See `docs/viva/trishit.md` for the walkthrough.

`make figures` regenerates the existing plotted overview, not these GUI captures.
If the demo or RTL changes, rerun it and recapture these views. Surfer command-file
usage is documented at https://docs.surfer-project.org/book/commands/index.html;
the checked-in commands were exercised with the installed version.
