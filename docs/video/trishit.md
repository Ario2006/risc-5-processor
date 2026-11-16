<!-- ABOUTME: Trishit's voice lines for the Phase I video: the demo, waveforms, diagrams and verification. -->
<!-- ABOUTME: Read docs/video/README.md first for how to record and send files. -->
# Trishit: 10 beats

Read [`README.md`](README.md) first. One audio file per beat, named by its id.
You do not need to record your screen. The build runs `make test` and `make demo`
itself and shows their real output, then your annotated Surfer captures from `figures/`.

| File | On screen | Say |
|---|---|---|
| `04_01` | Terminal card: `make test` | Now the demo. make test runs every program on all three CPUs, and checks each one against our Python reference simulator. |
| `04_02` | Same card, slow zoom | 248 passed, in under three seconds. |
| `04_03` | Terminal card: `make demo` | make demo runs the hazard demo on the forwarding pipeline: seven instructions, 14 cycles, one stall, one flush. It also writes a waveform. |
| `04_04` | `waveform_forward_annotated.png` | At EX PC hex four, forward A and forward B both switch to 2. The add takes x1 straight from EX MEM. |
| `04_05` | `waveform_load_use_annotated.png` | Next, stall goes high for one cycle. The add right after the load waits for its value. |
| `04_06` | `waveform_branch_flush_annotated.png` | Then flush goes high. The branch is taken in EX, so the two instructions behind it become bubbles. |
| `04_07` | Slide 7 | The same demo as pipeline diagrams from the simulation trace: 14 cycles with forwarding, 19 without. |
| `04_08` | Slide 7, slow zoom | Without forwarding, a result still in EX or MEM cannot be used yet. |
| `04_09` | Slide 8 | Every program runs on all three CPUs and must match our Python reference simulator: every register, every data word, the instruction count. |
| `04_10` | Slide 8, slow zoom | 248 automated checks, all passing. |

## Say it right

"make test" is said as two words. "x1" is "x one". "EX MEM" is "E X MEM".
