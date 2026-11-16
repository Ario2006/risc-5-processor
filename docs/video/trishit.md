<!-- ABOUTME: Trishit's lines for the Phase I video: the demo, waveforms, diagrams and verification. -->
<!-- ABOUTME: Read docs/video/README.md first for how to record and send your take. -->
# Trishit: one take

Read [`README.md`](README.md) first. Record your whole segment as **one take**, face on camera,
saying the lines below in order, with a short pause between them. Upload it as `trishit.mov`.
You do not need to record your screen. `make_frames.py` renders the real `make test` and
`make demo` output, and Aryan puts it behind you, then your annotated Surfer captures from `figures/`.

| Behind you | Say |
|---|---|
| Terminal card: `make test` | Now let's see it run. make test runs every program on all three CPUs, and checks each against our Python reference simulator. |
| Same card, slow zoom | All 248 pass, in under three seconds. |
| Terminal card: `make demo` | make demo runs a program built to hit every hazard: seven instructions, 14 cycles, one stall, one flush. It also saves a waveform. |
| `waveform_forward_annotated.png` | Here's forwarding. Both forward signals switch to 2, so the add gets x1 straight from the instruction ahead. |
| `waveform_load_use_annotated.png` | Here's the stall. The add right after the load waits one cycle for its value. |
| `waveform_branch_flush_annotated.png` | And the flush. The branch is taken, so the two instructions behind it are thrown away. |
| Slide 7 | The same program as a pipeline diagram from the simulation: 14 cycles with forwarding, 19 without. |
| Slide 7, slow zoom | Without forwarding, an instruction waits until the result it needs is written back. |
| Slide 8 | Every program must match the reference on all three CPUs: every register, every memory word, and the instruction count. |
| Slide 8, slow zoom | That's 248 automated checks, all passing. |

## Say it right

"make test" and "make demo" are said as two words each. "x1" is "x one".
