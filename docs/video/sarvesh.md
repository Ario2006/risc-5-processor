<!-- ABOUTME: Sarvesh's lines for the Phase I video: pipeline, hazards and the Verilog walk. -->
<!-- ABOUTME: Read docs/video/README.md first for how to record and send your take. -->
# Sarvesh: one take

Read [`README.md`](README.md) first. Record your whole segment as **one take**, voice
only, no camera, saying the lines below in order, with a short pause between them. Upload it
named `sarvesh`, in any audio or video format.

| On screen | Say |
|---|---|
| Slide 5 | To pipeline it, we cut that datapath into five stages, with registers in between, so five instructions are in flight at once. |
| Slide 5, the datapath diagram | The catch is they depend on each other. The green wires pass results back early. The red one throws away wrong work after a branch. |
| Slide 6, Structural card lit | Structural hazards, two instructions fighting over hardware, we designed out completely. |
| Slide 6, Data card lit | Forwarding fixes almost every data hazard. The exception is a load whose result is used straight away. That costs one cycle. |
| Slide 6, Control card lit | And by the time a branch is taken, two wrong instructions have started, so we flush them. |
| `hazard_unit.v`, lines 35 to 45 | All of this lives in one small module, the hazard unit. |
| Line 39 highlighted | This line spots the load case: a load, and the next instruction needs its result. |
| Line 43 highlighted | This one is the flush. Just a taken branch. |
| Line 44 highlighted | And this is the stall. With forwarding, only the load case. Without it, any result still on its way. |
| `forwarding_unit.v`, lines 25 to 28 highlighted | Forwarding checks the newest result first, so you always get the latest value. |

## Say it right

Speak it like you are explaining it to a friend. The highlight on screen shows which line you mean, so you never read out line numbers.
