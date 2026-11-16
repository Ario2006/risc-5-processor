<!-- ABOUTME: Navodit's recording script for the Phase I video: the opening clip and the closing clip. -->
<!-- ABOUTME: Read docs/video/README.md first for setup and how to send clips. -->
# Navodit: two clips

Read [`README.md`](README.md) for setup first.

## Clip 1: `01_navodit_intro.mp4`, about 50 seconds

Start on slide 1, in full screen. Two seconds of silence, then:

> Hi, we're team Processors Assemble: Sarvesh, Aryan, Trishit, Husain and me, Navodit.
> We built a RISC-V processor in Verilog, first single-cycle, then a five-stage pipeline,
> and measured what pipelining really buys on an FPGA.

`[NEXT]` to slide 2.

> A five-stage pipeline is ideally five times faster. To test that, we built three CPUs
> for the same 18-instruction subset: single-cycle, a pipeline without forwarding, and
> one with forwarding. Same tests, same FPGA target.

`[NEXT]` to slide 3.

> Every result follows the iron law: time is instructions times CPI over clock.
> Single-cycle CPI is one, so a pipeline wins only while its CPI stays below its clock gain:
> 1.94 without forwarding, 1.43 with it.

Two seconds of silence, stop.

## Clip 2: `06_navodit_conclusion.mp4`, about 25 seconds

Start on slide 12. Two seconds of silence, then:

> A pipeline wins only when the clock it gains beats the CPI it loses.
> Phase II attacks the two losses we measured, branches and the long critical path,
> then extends the instruction set and runs on a real board. Thank you.

Stay on slide 12 and keep quiet for **three** seconds before you stop. That is the ending.

## Say it right

- "1.94" is "one point nine four". "CPI" is "C P I".
- "RISC-V" is "risk five".
