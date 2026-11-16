<!-- ABOUTME: Sarvesh's lines for the Phase I video: pipeline, hazards and the Verilog walk. -->
<!-- ABOUTME: Read docs/video/README.md first for how to record and send your take. -->
# Sarvesh: 10 lines

Read [`README.md`](README.md) first. Record all your lines in one take, face on camera, in order,
with a 2 second pause between lines. The ids are for Aryan's edit, not file names.

| Line | Behind you | Say |
|---|---|---|
| `03_01` | Slide 5, slow push in | To pipeline it, we cut that datapath into five stages, with registers in between, so five instructions are in flight at once. |
| `03_02` | Zoomed on the datapath diagram | The catch is they depend on each other. The green wires pass results back early. The red one throws away wrong work after a branch. |
| `03_03` | Slide 6, Structural card lit | Structural hazards, two instructions fighting over hardware, we designed out completely. |
| `03_04` | Slide 6, Data card lit | Forwarding fixes almost every data hazard. The exception is a load whose result is used straight away. That costs one cycle. |
| `03_05` | Slide 6, Control card lit | And by the time a branch is taken, two wrong instructions have started, so we flush them. |
| `03_06` | `hazard_unit.v`, lines 35 to 45 | All of this lives in one small module, the hazard unit. |
| `03_07` | Line 39 highlighted | This line spots the load case: a load, and the next instruction needs its result. |
| `03_08` | Line 43 highlighted | This one is the flush. Just a taken branch. |
| `03_09` | Line 44 highlighted | And this is the stall. With forwarding, only the load case. Without it, any result still on its way. |
| `03_10` | `forwarding_unit.v`, lines 25 to 28 highlighted | Forwarding checks the newest result first, so you always get the latest value. |

## Say it right

Speak it like you are explaining it to a friend. The highlight on screen shows which line you mean, so you never read out line numbers.
