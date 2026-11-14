// ABOUTME: Shared constants: RV32I opcodes used by this CPU and the ALU operation codes.
// ABOUTME: Included by the control unit, ALU and both CPU tops.
// Author: Sarvesh Srinath
`ifndef RV_DEFS_VH
`define RV_DEFS_VH

`define OP_R      7'b0110011
`define OP_I      7'b0010011
`define OP_LOAD   7'b0000011
`define OP_STORE  7'b0100011
`define OP_BRANCH 7'b1100011
`define OP_SYSTEM 7'b1110011

`define ALU_ADD 3'd0
`define ALU_SUB 3'd1
`define ALU_AND 3'd2
`define ALU_OR  3'd3
`define ALU_XOR 3'd4
`define ALU_SLT 3'd5
`define ALU_SLL 3'd6

`define NOP 32'h00000013

`endif
