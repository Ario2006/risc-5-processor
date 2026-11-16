<!-- ABOUTME: Navodit's lines for the Phase I video: the opening and the closing lines. -->
<!-- ABOUTME: Read docs/video/README.md first for how to record and send your take. -->
# Navodit: 8 lines

Read [`README.md`](README.md) first. Record all your lines in one take, face on camera, in order,
with a 2 second pause between lines. The ids are for Aryan's edit, not file names.

## Opening (slides 1 to 3)

| Line | Behind you | Say |
|---|---|---|
| `01_01` | Slide 1 | Hi, we're Processors Assemble: Sarvesh, Aryan, Trishit, Husain, and I'm Navodit. |
| `01_02` | Slide 1, slow zoom | We built a RISC-V processor in Verilog, first single cycle, then as a five stage pipeline, to see how much faster pipelining really makes it. |
| `01_03` | Slide 2 | On paper, five stages means five times faster. So we built three CPUs for the same 18 instructions to test that. |
| `01_04` | Slide 2, slow zoom | Single cycle, a pipeline without forwarding, and one with it. Same tests, same FPGA. |
| `01_05` | Slide 3 | To compare them, we use the iron law: run time is instructions, times cycles per instruction, over the clock. |
| `01_06` | Slide 3, slow zoom | So a pipeline only wins if its cycles per instruction stay below its clock speedup. That bar is 1.94 without forwarding, and 1.43 with it. |

## Closing (slide 12)

| Line | Behind you | Say |
|---|---|---|
| `06_01` | Slide 12 | So a pipeline only wins when the clock it gains beats the cycles it loses. |
| `06_02` | Slide 12, slow zoom, holds 2 s | In Phase II, we go after those two losses, branches and the long critical path, then add instructions and run on a real board. Thanks for watching. |

## Say it right

"RISC-V" is "risk five". "1.94" is "one point nine four". "1.43" is "one point four three".
