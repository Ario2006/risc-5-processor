<!-- ABOUTME: Trishit's recording script for the Phase I video: the live demo, then the diagram and verification slides. -->
<!-- ABOUTME: Read docs/video/README.md first for setup and how to send clips. -->
# Trishit: `04_trishit_demo.mp4`, about 80 seconds

Read [`README.md`](README.md) for setup first.

## Before you record

1. In the repo root, run `uv sync` and `make test` once, so nothing downloads on camera.
2. Terminal: font size 20 or bigger, light theme if you have one, short prompt, then `clear`.
3. Have `slides/phase1-slides.pdf` open on slide 7, ready to switch to.
4. Do one dry run of the Surfer part so you know where the `fwd_a`, `stall` and `flush` rows are.

## Script

Start on the cleared terminal. Two seconds of silence, then type `make test` and press Enter.

> Now the live demo. make test runs every program on all three CPUs and checks each
> one against our Python reference simulator.

When the result shows:

> 248 passed, in under three seconds.

Type `make demo` and press Enter.

> make demo runs the hazard demo on the forwarding pipeline: seven instructions,
> 14 cycles, one stall, one flush. It also writes a waveform.

Type `surfer build/hazard_demo.vcd -c docs/waveforms/hazard_demo.sucl` and press Enter.
Point the mouse at each event as you name it.

> At EX PC 0x04, fwd_a and fwd_b both switch to 2: the add takes x1 straight from EX/MEM.
> Next, stall goes high for one cycle: the add right after the load waits for its value.
> Then flush goes high: the branch is taken in EX, so the two instructions behind it
> become bubbles.

Switch to the slides, full screen, on slide 7.

> The same demo as pipeline diagrams from the hardware trace: 14 cycles with forwarding,
> 19 without, because without forwarding a result still in EX or MEM cannot be used yet.

`[NEXT]` to slide 8.

> Every program runs on all three CPUs and must match our Python reference simulator:
> every register, every data word, the instruction count. 248 automated checks, all passing.

Two seconds of silence, stop.

## Say it right

- "0x04" is "hex four". "fwd_a" is "forward A".
- "EX/MEM" is "E X to MEM".

If Surfer is slow to open, keep quiet until it is up. Husain will cut the wait.
