<!-- ABOUTME: Husain's voice lines for the Phase I video: synthesis, CPI and speedup. -->
<!-- ABOUTME: Husain also builds the video; the steps for his Claude are in editing.md. -->
# Husain: 6 beats

Read [`README.md`](README.md) first. One audio file per beat, named by its id.
You also build the video: hand [`editing.md`](editing.md) to your Claude once all 36 files are in.

| File | On screen | Say |
|---|---|---|
| `05_01` | Slide 9 | In post-route estimates for a Lattice ECP5, pipelining raises the clock from 58.75 to 113.86 megahertz. |
| `05_02` | Slide 9, slow zoom | Forwarding brings it back to 83.89, because its compare and mux sit in front of the branch decision. |
| `05_03` | Slide 10 | Without forwarding, data stalls are the biggest loss. Forwarding removes them. |
| `05_04` | Slide 10, slow zoom | What is left is load-use stalls and the branch penalty, which adds 0.23 to 0.35 cycles per instruction across the benchmarks. |
| `05_05` | Slide 11 | So the speedup is only 0.71 to 1.29 times, not five. |
| `05_06` | Slide 11, slow zoom | The critical path is still 52 percent of the single-cycle path without forwarding and 70 percent with it, and every loop iteration pays two cycles for its branch. |

## Say it right

"113.86" is "one thirteen point eight six". "83.89" is "eighty three point eight nine".
"0.71 to 1.29 times" is "zero point seven one to one point two nine times". "ECP5" is "E C P five".
