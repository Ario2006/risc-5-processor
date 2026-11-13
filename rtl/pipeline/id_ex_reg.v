// ABOUTME: ID/EX pipeline register: operands, immediate, register numbers and control for EX onward.
// ABOUTME: flush inserts a bubble (load-use stall, RAW stall without forwarding, or taken branch).
`default_nettype none

module id_ex_reg (
    input  wire        clk,
    input  wire        rst,
    input  wire        flush,
    input  wire        valid_in,
    input  wire [31:0] pc_in,
    input  wire        reg_write_in, alu_src_in, mem_read_in, mem_write_in,
    input  wire        branch_in, branch_ne_in, halt_in,
    input  wire [2:0]  alu_op_in,
    input  wire [31:0] rs1_val_in, rs2_val_in, imm_in,
    input  wire [4:0]  rs1_in, rs2_in, rd_in,
    output reg         valid,
    output reg  [31:0] pc,
    output reg         reg_write, alu_src, mem_read, mem_write, branch, branch_ne, halt,
    output reg  [2:0]  alu_op,
    output reg  [31:0] rs1_val, rs2_val, imm,
    output reg  [4:0]  rs1, rs2, rd
);
    always @(posedge clk) begin
        if (rst || flush) begin
            valid <= 1'b0; pc <= 32'b0;
            reg_write <= 1'b0; alu_src <= 1'b0; mem_read <= 1'b0; mem_write <= 1'b0;
            branch <= 1'b0; branch_ne <= 1'b0; halt <= 1'b0; alu_op <= 3'd0;
            rs1_val <= 32'b0; rs2_val <= 32'b0; imm <= 32'b0;
            rs1 <= 5'd0; rs2 <= 5'd0; rd <= 5'd0;
        end else begin
            valid <= valid_in; pc <= pc_in;
            reg_write <= reg_write_in; alu_src <= alu_src_in; mem_read <= mem_read_in;
            mem_write <= mem_write_in; branch <= branch_in; branch_ne <= branch_ne_in;
            halt <= halt_in; alu_op <= alu_op_in;
            rs1_val <= rs1_val_in; rs2_val <= rs2_val_in; imm <= imm_in;
            rs1 <= rs1_in; rs2 <= rs2_in; rd <= rd_in;
        end
    end
endmodule
