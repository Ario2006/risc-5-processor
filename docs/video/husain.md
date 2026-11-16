<!-- ABOUTME: Husain's lines for the Phase I video: synthesis, CPI and speedup. -->
<!-- ABOUTME: Read docs/video/README.md first for how to record and send your take. -->
# Husain: one take

Read [`README.md`](README.md) first. Record your whole segment as **one take**, face on camera,
saying the lines below in order, with a short pause between them. Upload it as `husain.mov`.

| Behind you | Say |
|---|---|
| Slide 9 | So, is it faster? After place and route on a Lattice ECP5, pipelining nearly doubles the clock, from 58.75 to 113.86 megahertz. |
| Slide 9, slow zoom | Forwarding pulls it back to 83.89, because its extra logic sits right before the branch decision. |
| Slide 10 | Without forwarding, the biggest loss is waiting on data. Forwarding removes that. |
| Slide 10, slow zoom | What's left is the load stall and branches, adding 0.23 to 0.35 cycles per instruction. |
| Slide 11 | So the pipeline is only 0.71 to 1.29 times as fast. Nowhere near five. |
| Slide 11, slow zoom | The slowest path is still 52 percent of the single cycle one without forwarding, 70 percent with it. And every loop pays two cycles for its branch. |

## Say it right

"113.86" is "one thirteen point eight six". "83.89" is "eighty three point eight nine".
"0.71 to 1.29 times" is "zero point seven one to one point two nine times". "0.23 to 0.35" is "zero point two three to zero point three five". "ECP5" is "E C P five".
