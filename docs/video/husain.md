<!-- ABOUTME: Husain's voice lines for the Phase I video: synthesis, CPI and speedup. -->
<!-- ABOUTME: Husain also builds the video; the steps for his Claude are in editing.md. -->
# Husain: 6 beats

Read [`README.md`](README.md) first. One audio file per beat, named by its id.
You also build the video: hand [`editing.md`](editing.md) to your Claude once all 36 files are in.

| File | On screen | Say |
|---|---|---|
| `05_01` | Slide 9 | So, is it faster? After place and route on a Lattice ECP5, pipelining nearly doubles the clock, from 58.75 to 113.86 megahertz. |
| `05_02` | Slide 9, slow zoom | Forwarding pulls it back to 83.89, because its extra logic sits right before the branch decision. |
| `05_03` | Slide 10 | Without forwarding, the biggest loss is waiting on data. Forwarding removes them. |
| `05_04` | Slide 10, slow zoom | What's left is the load stall and branches, adding 0.23 to 0.35 cycles per instruction. |
| `05_05` | Slide 11 | So the pipeline is only 0.71 to 1.29 times as fast. Nowhere near five. |
| `05_06` | Slide 11, slow zoom | The slowest path is still 52 percent of the single cycle one without forwarding, 70 percent with it. And every loop pays two cycles for its branch. |

## Say it right

"113.86" is "one thirteen point eight six". "83.89" is "eighty three point eight nine".
"0.71 to 1.29 times" is "zero point seven one to one point two nine times". "0.23 to 0.35" is "zero point two three to zero point three five". "ECP5" is "E C P five".
