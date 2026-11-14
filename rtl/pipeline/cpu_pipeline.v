// ABOUTME: 5-stage pipelined RV32I subset CPU (IF, ID, EX, MEM, WB) built from the stage modules.
// ABOUTME: FORWARDING=1 forwards results and stalls only on load-use; 0 stalls on every RAW hazard.
// Author: Sarvesh Srinath
`default_nettype none
`include "defs.vh"

module cpu_pipeline #(
    parameter FORWARDING = 1,
    parameter IMEM_INIT = "",
    parameter DMEM_INIT = ""
) (
    input  wire        clk,
    input  wire        rst,
    output wire        halted,        // ecall is in WB this cycle
    output wire        retire_valid,  // one instruction finishes (leaves WB) this cycle
    output wire [31:0] retire_pc,
    output wire        retire_we,
    output wire [4:0]  retire_rd,
    output wire [31:0] retire_data,
    output wire        illegal
);
    // ---------------- hazard control ----------------
    wire pc_write, if_id_en, if_id_flush, id_ex_flush, stall, load_use, flush;

    // ---------------- IF ----------------
    wire [31:0] if_pc, if_instr, ex_target;
    wire        ex_taken;
    if_stage #(.IMEM_INIT(IMEM_INIT)) if_s (
        .clk(clk), .rst(rst), .pc_write(pc_write), .redirect(ex_taken), .redirect_pc(ex_target),
        .pc(if_pc), .instr(if_instr)
    );

    // ---------------- IF/ID ----------------
    wire        id_valid;
    wire [31:0] id_pc, id_instr;
    if_id_reg if_id (
        .clk(clk), .rst(rst), .en(if_id_en), .flush(if_id_flush),
        .pc_in(if_pc), .instr_in(if_instr), .valid(id_valid), .pc(id_pc), .instr(id_instr)
    );

    // ---------------- ID ----------------
    wire        wb_we;
    wire [4:0]  wb_rd;
    wire [31:0] wb_data;
    wire id_reg_write, id_alu_src, id_mem_read, id_mem_write, id_branch, id_branch_ne, id_halt;
    wire id_uses_rs1, id_uses_rs2, id_illegal;
    wire [2:0]  id_alu_op;
    wire [31:0] id_rs1_val, id_rs2_val, id_imm;
    wire [4:0]  id_rs1, id_rs2, id_rd;
    id_stage id (
        .clk(clk), .valid(id_valid), .instr(id_instr),
        .wb_we(wb_we), .wb_rd(wb_rd), .wb_data(wb_data),
        .reg_write(id_reg_write), .alu_src(id_alu_src), .mem_read(id_mem_read),
        .mem_write(id_mem_write), .branch(id_branch), .branch_ne(id_branch_ne), .halt(id_halt),
        .uses_rs1(id_uses_rs1), .uses_rs2(id_uses_rs2), .alu_op(id_alu_op), .illegal(id_illegal),
        .rs1_val(id_rs1_val), .rs2_val(id_rs2_val), .imm(id_imm),
        .rs1(id_rs1), .rs2(id_rs2), .rd(id_rd)
    );

    // ---------------- ID/EX ----------------
    wire        ex_valid, ex_reg_write, ex_alu_src, ex_mem_read, ex_mem_write;
    wire        ex_branch, ex_branch_ne, ex_halt;
    wire [2:0]  ex_alu_op;
    wire [31:0] ex_pc, ex_rs1_val, ex_rs2_val, ex_imm;
    wire [4:0]  ex_rs1, ex_rs2, ex_rd;
    id_ex_reg id_ex (
        .clk(clk), .rst(rst), .flush(id_ex_flush),
        .valid_in(id_valid), .pc_in(id_pc),
        .reg_write_in(id_reg_write), .alu_src_in(id_alu_src), .mem_read_in(id_mem_read),
        .mem_write_in(id_mem_write), .branch_in(id_branch), .branch_ne_in(id_branch_ne),
        .halt_in(id_halt), .alu_op_in(id_alu_op),
        .rs1_val_in(id_rs1_val), .rs2_val_in(id_rs2_val), .imm_in(id_imm),
        .rs1_in(id_rs1), .rs2_in(id_rs2), .rd_in(id_rd),
        .valid(ex_valid), .pc(ex_pc),
        .reg_write(ex_reg_write), .alu_src(ex_alu_src), .mem_read(ex_mem_read),
        .mem_write(ex_mem_write), .branch(ex_branch), .branch_ne(ex_branch_ne), .halt(ex_halt),
        .alu_op(ex_alu_op), .rs1_val(ex_rs1_val), .rs2_val(ex_rs2_val), .imm(ex_imm),
        .rs1(ex_rs1), .rs2(ex_rs2), .rd(ex_rd)
    );

    // ---------------- EX ----------------
    wire        mem_valid, mem_reg_write, mem_mem_read, mem_mem_write, mem_halt;
    wire [31:0] mem_pc, mem_alu_y, mem_store_data;
    wire [4:0]  mem_rd;
    wire [1:0]  fwd_a, fwd_b;
    wire [31:0] ex_alu_y, ex_store_data;

    forwarding_unit #(.ENABLE(FORWARDING)) fwd (
        .ex_rs1(ex_rs1), .ex_rs2(ex_rs2),
        .ex_mem_reg_write(mem_reg_write), .ex_mem_rd(mem_rd),
        .mem_wb_reg_write(wb_we), .mem_wb_rd(wb_rd),
        .fwd_a(fwd_a), .fwd_b(fwd_b)
    );

    ex_stage ex (
        .pc(ex_pc), .rs1_val(ex_rs1_val), .rs2_val(ex_rs2_val), .imm(ex_imm),
        .alu_src(ex_alu_src), .alu_op(ex_alu_op), .branch(ex_branch), .branch_ne(ex_branch_ne),
        .fwd_a(fwd_a), .fwd_b(fwd_b), .ex_mem_value(mem_alu_y), .mem_wb_value(wb_data),
        .alu_y(ex_alu_y), .store_data(ex_store_data), .taken(ex_taken), .target(ex_target)
    );

    hazard_unit #(.FORWARDING(FORWARDING)) hz (
        .clk(clk), .rst(rst),
        .id_rs1(id_rs1), .id_rs2(id_rs2), .id_uses_rs1(id_uses_rs1), .id_uses_rs2(id_uses_rs2),
        .id_halt(id_halt),
        .ex_reg_write(ex_reg_write), .ex_mem_read(ex_mem_read), .ex_rd(ex_rd), .ex_taken(ex_taken),
        .mem_reg_write(mem_reg_write), .mem_rd(mem_rd),
        .pc_write(pc_write), .if_id_en(if_id_en), .if_id_flush(if_id_flush),
        .id_ex_flush(id_ex_flush), .stall(stall), .load_use(load_use), .flush(flush)
    );

    // ---------------- EX/MEM ----------------
    ex_mem_reg ex_mem (
        .clk(clk), .rst(rst), .valid_in(ex_valid), .pc_in(ex_pc),
        .alu_y_in(ex_alu_y), .store_data_in(ex_store_data), .rd_in(ex_rd),
        .reg_write_in(ex_reg_write), .mem_read_in(ex_mem_read), .mem_write_in(ex_mem_write),
        .halt_in(ex_halt),
        .valid(mem_valid), .pc(mem_pc), .alu_y(mem_alu_y), .store_data(mem_store_data),
        .rd(mem_rd), .reg_write(mem_reg_write), .mem_read(mem_mem_read),
        .mem_write(mem_mem_write), .halt(mem_halt)
    );

    // ---------------- MEM ----------------
    wire [31:0] mem_load_data;
    mem_stage #(.DMEM_INIT(DMEM_INIT)) mem (
        .clk(clk), .mem_write(mem_mem_write), .addr(mem_alu_y), .store_data(mem_store_data),
        .load_data(mem_load_data)
    );

    // ---------------- MEM/WB ----------------
    wire        wb_valid, wb_reg_write, wb_mem_read, wb_halt;
    wire [31:0] wb_pc, wb_alu_y, wb_load_data;
    mem_wb_reg mem_wb (
        .clk(clk), .rst(rst), .valid_in(mem_valid), .pc_in(mem_pc),
        .alu_y_in(mem_alu_y), .load_data_in(mem_load_data), .rd_in(mem_rd),
        .reg_write_in(mem_reg_write), .mem_read_in(mem_mem_read), .halt_in(mem_halt),
        .valid(wb_valid), .pc(wb_pc), .alu_y(wb_alu_y), .load_data(wb_load_data),
        .rd(wb_rd), .reg_write(wb_reg_write), .mem_read(wb_mem_read), .halt(wb_halt)
    );

    // ---------------- WB ----------------
    wb_stage wb (.mem_read(wb_mem_read), .alu_y(wb_alu_y), .load_data(wb_load_data),
                 .wb_data(wb_data));
    assign wb_we = wb_reg_write;

    assign halted       = wb_valid && wb_halt;
    assign retire_valid = wb_valid;
    assign retire_pc    = wb_pc;
    assign retire_we    = wb_we;
    assign retire_rd    = wb_rd;
    assign retire_data  = wb_data;
    assign illegal      = id_illegal;
endmodule
