// ABOUTME: Write-Back stage: picks the loaded data or the ALU result for the register file.
// ABOUTME: The register file itself sits in ID; this stage only drives its write port.
// Author: Sarvesh Srinath
`default_nettype none

module wb_stage (
    input  wire        mem_read,
    input  wire [31:0] alu_y,
    input  wire [31:0] load_data,
    output wire [31:0] wb_data
);
    assign wb_data = mem_read ? load_data : alu_y;
endmodule
