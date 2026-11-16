<!-- ABOUTME: Navodit's lines for the Phase I video: the opening and the closing lines. -->
<!-- ABOUTME: Read docs/video/README.md first for how to record and send your take. -->
# Navodit: two takes

Read [`README.md`](README.md) first. You record **two takes**, voice only, no camera:
the opening as `navodit_opening` and the closing as `navodit_closing`. Say the lines in order,
with a short pause between them.

## Take 1: opening (slides 1 to 3)

| On screen | Say |
|---|---|
| Slide 1 | Hi, we're Processors Assemble: Sarvesh, Aryan, Trishit, Husain, and I'm Navodit. |
| Slide 1 | We built a RISC-V processor in Verilog, first single cycle, then as a five stage pipeline, to see how much faster pipelining really makes it. |
| Slide 2 | On paper, five stages means five times faster. So we built three CPUs for the same 18 instructions to test that. |
| Slide 2 | Single cycle, a pipeline without forwarding, and one with it. Same tests, same FPGA. |
| Slide 3 | To compare them, we use the iron law: run time is instructions, times cycles per instruction, over the clock. |
| Slide 3 | So a pipeline only wins if its cycles per instruction stay below its clock speedup. That bar is 1.94 without forwarding, and 1.43 with it. |

## Take 2: closing (slide 12)

| On screen | Say |
|---|---|
| Slide 12 | So a pipeline only wins when the clock it gains beats the cycles it loses. |
| Slide 12, holds 2 s | In Phase II, we go after those two losses, branches and the long critical path, then add instructions and run on a real board. Thanks for watching. |

## Say it right

"RISC-V" is "risk five". "1.94" is "one point nine four". "1.43" is "one point four three".
