// ABOUTME: 32 bit ALU for the supported subset: add, sub, and, or, xor, set less than, shift left.
// ABOUTME: Purely combinational, shared by the single-cycle and pipelined CPUs.
`default_nettype none
`include "defs.vh"

module alu (
    input  wire [31:0] a,
    input  wire [31:0] b,
    input  wire [2:0]  op,
    output reg  [31:0] y
);
    always @(*) begin
        case (op)
            `ALU_ADD: y = a + b;
            `ALU_SUB: y = a - b;
            `ALU_AND: y = a & b;
            `ALU_OR:  y = a | b;
            `ALU_XOR: y = a ^ b;
            `ALU_SLT: y = {31'b0, $signed(a) < $signed(b)};
            `ALU_SLL: y = a << b[4:0];
            default:  y = 32'b0;
        endcase
    end
endmodule
