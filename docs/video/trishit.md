<!-- ABOUTME: Trishit's lines for the Phase I video: the demo, waveforms, diagrams and verification. -->
<!-- ABOUTME: Read docs/video/README.md first for how to record and send your take. -->
# Trishit: 10 lines

Read [`README.md`](README.md) first. Record all your lines in one take, face on camera, in order,
with a 2 second pause between lines. The ids are for Aryan's edit, not file names.
You do not need to record your screen. `make_frames.py` renders the real `make test` and
`make demo` output, and Aryan puts it behind you, then your annotated Surfer captures from `figures/`.

| Line | Behind you | Say |
|---|---|---|
| `04_01` | Terminal card: `make test` | Now let's see it run. make test runs every program on all three CPUs, and checks each against our Python reference simulator. |
| `04_02` | Same card, slow zoom | All 248 pass, in under three seconds. |
| `04_03` | Terminal card: `make demo` | make demo runs a program built to hit every hazard: seven instructions, 14 cycles, one stall, one flush. It also saves a waveform. |
| `04_04` | `waveform_forward_annotated.png` | Here's forwarding. Both forward signals switch to 2, so the add gets x1 straight from the instruction ahead. |
| `04_05` | `waveform_load_use_annotated.png` | Here's the stall. The add right after the load waits one cycle for its value. |
| `04_06` | `waveform_branch_flush_annotated.png` | And the flush. The branch is taken, so the two instructions behind it are thrown away. |
| `04_07` | Slide 7 | The same program as a pipeline diagram from the simulation: 14 cycles with forwarding, 19 without. |
| `04_08` | Slide 7, slow zoom | Without forwarding, an instruction waits until the result it needs is written back. |
| `04_09` | Slide 8 | Every program must match the reference on all three CPUs: every register, every memory word, and the instruction count. |
| `04_10` | Slide 8, slow zoom | That's 248 automated checks, all passing. |

## Say it right

"make test" and "make demo" are said as two words each. "x1" is "x one".
