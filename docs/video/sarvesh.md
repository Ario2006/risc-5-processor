<!-- ABOUTME: Sarvesh's voice lines for the Phase I video: pipeline, hazards and the Verilog walk. -->
<!-- ABOUTME: Read docs/video/README.md first for how to record and send files. -->
# Sarvesh: 10 beats

Read [`README.md`](README.md) first. One audio file per beat, named by its id.

| File | On screen | Say |
|---|---|---|
| `03_01` | Slide 5, slow push in | We cut the same datapath into five stages, with a pipeline register between each pair, and one Verilog module each. |
| `03_02` | Zoomed on the datapath diagram | Green lines are the forwarding paths. Red is the branch flush. |
| `03_03` | Slide 6, Structural card lit | Structural hazards cost nothing. |
| `03_04` | Slide 6, Data card lit | With forwarding, only a load that is used at once stalls, and only for one cycle. |
| `03_05` | Slide 6, Control card lit | A taken branch flushes two instructions. |
| `03_06` | `hazard_unit.v`, lines 35 to 45 | Here is how that looks in the Verilog, in the hazard unit. |
| `03_07` | Line 39 highlighted | Line 39. Load use is a load in EX, writing a register that the instruction in ID reads. |
| `03_08` | Line 43 highlighted | Line 43. Flush is just a taken branch in EX. |
| `03_09` | Line 44 highlighted | Line 44. With forwarding, we stall only on load use. Without it, whenever a result it needs is still in EX or MEM. |
| `03_10` | `forwarding_unit.v`, lines 25 to 28 highlighted | In the forwarding unit, lines 25 to 28 check EX MEM before MEM WB, so the newest value wins. |

## Say it right

"EX" is "E X", "ID" is "I D", "MEM WB" is "MEM W B".
