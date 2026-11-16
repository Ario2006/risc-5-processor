<!-- ABOUTME: Navodit's voice lines for the Phase I video: the opening and the closing beats. -->
<!-- ABOUTME: Read docs/video/README.md first for how to record and send files. -->
# Navodit: 8 beats

Read [`README.md`](README.md) first. One audio file per beat, named by its id.

## Opening (slides 1 to 3)

| File | On screen | Say |
|---|---|---|
| `01_01` | Slide 1 | Hi, we're team Processors Assemble: Sarvesh, Aryan, Trishit, Husain and me, Navodit. |
| `01_02` | Slide 1, slow zoom | We built a RISC-V processor in Verilog, first single-cycle, then a five-stage pipeline, and measured what pipelining really buys in post-route FPGA timing. |
| `01_03` | Slide 2 | A five-stage pipeline is ideally five times faster. To test that, we built three CPUs for the same 18-instruction subset. |
| `01_04` | Slide 2, slow zoom | Single-cycle, a pipeline without forwarding, and one with forwarding. Same tests, same FPGA target. |
| `01_05` | Slide 3 | Every result follows the iron law: time is instructions times CPI over clock. |
| `01_06` | Slide 3, slow zoom | Single-cycle CPI is one, so a pipeline wins only while its CPI stays below its clock gain: 1.94 without forwarding, 1.43 with it. |

## Closing (slide 12)

| File | On screen | Say |
|---|---|---|
| `06_01` | Slide 12 | A pipeline wins only when the clock it gains beats the CPI it loses. |
| `06_02` | Slide 12, slow zoom, holds 2 s | Phase II attacks the two losses we measured, branches and the long critical path, then extends the instruction set and runs on a real board. Thank you. |

## Say it right

"RISC-V" is "risk five". "1.94" is "one point nine four". "CPI" is "C P I".
