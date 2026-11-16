<!-- ABOUTME: Sarvesh's recording script for the Phase I video: pipeline and hazard slides, then the Verilog walk. -->
<!-- ABOUTME: Read docs/video/README.md first for setup and how to send clips. -->
# Sarvesh: `03_sarvesh_pipeline.mp4`, about 55 seconds

Read [`README.md`](README.md) for setup first.

## Before you record

Open the repo in VS Code (or any editor) and prepare two tabs:
`rtl/pipeline/hazard_unit.v` and `rtl/pipeline/forwarding_unit.v`.

- Zoom in until about 25 lines fill the screen (`Cmd +` or `Ctrl +`).
- Hide the sidebar (`Cmd + B` or `Ctrl + B`) and close the terminal panel.
- In `hazard_unit.v`, scroll so lines 35 to 46 sit in the middle of the screen.

## Script

Start on slide 5, in full screen. Two seconds of silence, then:

> We cut the same datapath into five stages with a pipeline register between each pair,
> one Verilog module each. Green lines are forwarding paths; red is the branch flush.

`[NEXT]` to slide 6.

> Structural hazards cost nothing. With forwarding, only a load used at once stalls,
> for one cycle. A taken branch flushes two instructions. Here is how that looks in the Verilog.

Leave the slideshow and switch to the editor, on `hazard_unit.v`.
Select each line as you name it, so the viewer sees where you are.

> In the hazard unit, line 39: load use is a load in EX writing a register the
> instruction in ID reads. Line 43: flush is just a taken branch in EX. Line 44: with
> forwarding we stall only on load use; without it, on any result still in EX or MEM.

Switch to the `forwarding_unit.v` tab and select lines 25 to 28.

> In the forwarding unit, lines 25 to 28: EX/MEM is checked before MEM/WB,
> so the newest value wins.

Two seconds of silence, stop.

## Say it right

- "EX/MEM" is "E X to MEM". "MEM/WB" is "MEM to W B".
- "ID" is "I D", "EX" is "E X".
