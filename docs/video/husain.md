<!-- ABOUTME: Husain's recording script for the Phase I video: the synthesis, CPI and speedup slides. -->
<!-- ABOUTME: Husain also edits the video; the editing steps for his Claude are in editing.md. -->
# Husain: `05_husain_results.mp4`, about 50 seconds

Read [`README.md`](README.md) for setup first. You also edit the final video:
hand [`editing.md`](editing.md) to your Claude once all six clips are in.

## Script

Start on slide 9, in full screen. Two seconds of silence, then:

> Post-route on a Lattice ECP5, pipelining raises the clock from 58.75 to 113.86 MHz.
> Forwarding brings it back to 83.89, because its compare and mux sit in front of the
> branch decision.

`[NEXT]` to slide 10.

> Without forwarding, data stalls dominate. Forwarding removes them, leaving load-use
> stalls and the branch penalty, which adds a quarter to a third of a cycle per
> instruction in every benchmark.

`[NEXT]` to slide 11.

> So the speedup is only 0.71 to 1.29 times, not five. The critical path is still half
> to two-thirds of the single-cycle path, and every loop iteration pays two cycles for its branch.

Two seconds of silence, stop.

## Say it right

- "113.86" is "one thirteen point eight six". "83.89" is "eighty three point eight nine".
- "0.71 to 1.29 times" is "zero point seven one to one point two nine times".
- "ECP5" is "E C P five".
