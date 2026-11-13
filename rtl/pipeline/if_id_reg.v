// ABOUTME: IF/ID pipeline register: the fetched instruction and its PC.
// ABOUTME: en=0 holds it (stall); flush turns it into a bubble (wrong path or halt).
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
    always @(posedge clk) begin
        if (rst || flush) begin
            valid <= 1'b0; pc <= 32'b0; instr <= `NOP;
        end else if (en) begin
            valid <= 1'b1; pc <= pc_in; instr <= instr_in;
        end
    end
endmodule
