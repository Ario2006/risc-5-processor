// ABOUTME: ID/EX pipeline register: operands, immediate, register numbers and control for EX onward.
// ABOUTME: flush inserts a bubble by clearing valid and control only; a bubble's data is never used.
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
    // Control: cleared by reset or flush, so a bubble writes nothing and never branches.
    always @(posedge clk) begin
        if (rst || flush) begin
            valid <= 1'b0; reg_write <= 1'b0; mem_read <= 1'b0; mem_write <= 1'b0;
            branch <= 1'b0; halt <= 1'b0;
        end else begin
            valid <= valid_in; reg_write <= reg_write_in; mem_read <= mem_read_in;
            mem_write <= mem_write_in; branch <= branch_in; halt <= halt_in;
        end
    end

    // Data: loads every cycle with no reset. Clearing it on flush would only add a reset
    // to about 140 flip-flops at the end of the branch-flush path, the slowest in the CPU.
    always @(posedge clk) begin
        pc <= pc_in; alu_src <= alu_src_in; branch_ne <= branch_ne_in; alu_op <= alu_op_in;
        rs1_val <= rs1_val_in; rs2_val <= rs2_val_in; imm <= imm_in;
        rs1 <= rs1_in; rs2 <= rs2_in; rd <= rd_in;
    end
endmodule
