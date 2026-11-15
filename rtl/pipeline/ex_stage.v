// ABOUTME: ALU/EX stage: forwarding muxes, the ALU, the branch comparator and the branch target.
// ABOUTME: Branches resolve here, so a taken branch costs two flushed instructions.
// Author: Sarvesh Srinath
`default_nettype none

module ex_stage (
    input  wire [31:0] pc,
    input  wire [31:0] rs1_val,
    input  wire [31:0] rs2_val,
    input  wire [31:0] imm,
    input  wire        alu_src,
    input  wire [2:0]  alu_op,
    input  wire        branch,
    input  wire        branch_ne,
    input  wire [1:0]  fwd_a,          // 00 register file, 10 EX/MEM, 01 MEM/WB
    input  wire [1:0]  fwd_b,
    input  wire [31:0] ex_mem_value,
    input  wire [31:0] mem_wb_value,
    output wire [31:0] alu_y,
    output wire [31:0] store_data,
    output wire        taken,
    output wire [31:0] target
);
    wire [31:0] a = fwd_a == 2'b10 ? ex_mem_value : fwd_a == 2'b01 ? mem_wb_value : rs1_val;
    wire [31:0] b = fwd_b == 2'b10 ? ex_mem_value : fwd_b == 2'b01 ? mem_wb_value : rs2_val;

    alu alu_i (.a(a), .b(alu_src ? imm : b), .op(alu_op), .y(alu_y));

    assign store_data = b;
    assign taken      = branch && ((a == b) ^ branch_ne);
    assign target     = pc + imm;
endmodule
