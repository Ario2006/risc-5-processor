// ABOUTME: 32 x 32 register file with two read ports and one write port; x0 always reads 0.
// ABOUTME: WRITE_THROUGH=1 returns the value being written this cycle (pipeline WB to ID bypass).
// Author: Sarvesh Srinath
`default_nettype none

module regfile #(
    parameter WRITE_THROUGH = 0
) (
    input  wire        clk,
    input  wire        we,
    input  wire [4:0]  waddr,
    input  wire [31:0] wdata,
    input  wire [4:0]  raddr1,
    input  wire [4:0]  raddr2,
    output wire [31:0] rdata1,
    output wire [31:0] rdata2
);
    reg [31:0] regs [0:31];

    integer i;
    initial for (i = 0; i < 32; i = i + 1) regs[i] = 32'b0;

    always @(posedge clk)
        if (we && waddr != 5'd0) regs[waddr] <= wdata;

    wire [31:0] stored1 = (raddr1 == 5'd0) ? 32'b0 : regs[raddr1];
    wire [31:0] stored2 = (raddr2 == 5'd0) ? 32'b0 : regs[raddr2];

    // Write-through models the textbook "write in the first half, read in the second half".
    // It only exists when asked for: in the single-cycle CPU wdata depends on rdata, so the
    // bypass mux would form a combinational loop even though it is never selected.
    generate
        if (WRITE_THROUGH) begin : bypass
            assign rdata1 = (we && waddr != 5'd0 && waddr == raddr1) ? wdata : stored1;
            assign rdata2 = (we && waddr != 5'd0 && waddr == raddr2) ? wdata : stored2;
        end else begin : no_bypass
            assign rdata1 = stored1;
            assign rdata2 = stored2;
        end
    endgenerate
endmodule
