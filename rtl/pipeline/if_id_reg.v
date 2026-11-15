// ABOUTME: IF/ID pipeline register: the fetched instruction and its PC.
// ABOUTME: en=0 holds it (stall); flush clears valid, which turns it into a bubble.
// Author: Sarvesh Srinath
`default_nettype none
`include "defs.vh"

module if_id_reg (
    input  wire        clk,
    input  wire        rst,
    input  wire        en,
    input  wire        flush,
    input  wire [31:0] pc_in,
    input  wire [31:0] instr_in,
    output reg         valid,
    output reg  [31:0] pc,
    output reg  [31:0] instr
);
    // Only valid needs clearing: id_stage gates every control signal with it.
    always @(posedge clk) begin
        if (rst || flush) valid <= 1'b0;
        else if (en)      valid <= 1'b1;
    end

    always @(posedge clk) begin
        if (rst)     begin pc <= 32'b0; instr <= `NOP; end
        else if (en) begin pc <= pc_in; instr <= instr_in; end
    end
endmodule
