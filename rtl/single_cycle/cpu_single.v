// ABOUTME: Single-cycle RV32I subset CPU: every instruction finishes in one long clock cycle.
// ABOUTME: The baseline the pipelined CPU is compared with (CPI exactly 1, lowest clock).
`default_nettype none
`include "defs.vh"

module cpu_single #(
    parameter IMEM_INIT = "",
    parameter DMEM_INIT = ""
) (
    input  wire        clk,
    input  wire        rst,
    output wire        halted,        // ecall is executing this cycle
    output wire        retire_valid,  // one instruction finishes this cycle
    output wire [31:0] retire_pc,
    output wire        retire_we,
    output wire [4:0]  retire_rd,
    output wire [31:0] retire_data,
    output wire        illegal
);
    reg  [31:0] pc;
    reg         stopped;
    wire [31:0] instr;

    imem #(.INIT_FILE(IMEM_INIT)) imem_i (.addr(pc), .rdata(instr));

    wire reg_write, alu_src, mem_read, mem_write, branch, branch_ne, halt, uses_rs1, uses_rs2;
    wire [2:0] alu_op;
    control ctrl (
        .instr(instr), .reg_write(reg_write), .alu_src(alu_src), .mem_read(mem_read),
        .mem_write(mem_write), .branch(branch), .branch_ne(branch_ne), .halt(halt),
        .uses_rs1(uses_rs1), .uses_rs2(uses_rs2), .alu_op(alu_op), .illegal(illegal)
    );

    wire [31:0] imm;
    imm_gen immg (.instr(instr), .imm(imm));

    wire [31:0] rs1_val, rs2_val, wb_data;
    wire        do_write = reg_write && !stopped;
    regfile #(.WRITE_THROUGH(0)) rf (
        .clk(clk), .we(do_write), .waddr(instr[11:7]), .wdata(wb_data),
        .raddr1(instr[19:15]), .raddr2(instr[24:20]), .rdata1(rs1_val), .rdata2(rs2_val)
    );

    wire [31:0] alu_y;
    alu alu_i (.a(rs1_val), .b(alu_src ? imm : rs2_val), .op(alu_op), .y(alu_y));

    wire [31:0] mem_rdata;
    dmem #(.INIT_FILE(DMEM_INIT)) dmem_i (
        .clk(clk), .we(mem_write && !stopped), .addr(alu_y), .wdata(rs2_val), .rdata(mem_rdata)
    );

    assign wb_data = mem_read ? mem_rdata : alu_y;

    wire taken = branch && ((rs1_val == rs2_val) ^ branch_ne);
    wire [31:0] next_pc = taken ? pc + imm : pc + 32'd4;

    always @(posedge clk) begin
        if (rst) begin
            pc <= 32'b0;
            stopped <= 1'b0;
        end else if (!stopped) begin
            if (halt) stopped <= 1'b1;
            else pc <= next_pc;
        end
    end

    assign halted       = halt && !stopped;
    assign retire_valid = !rst && !stopped;
    assign retire_pc    = pc;
    assign retire_we    = do_write && instr[11:7] != 5'd0;
    assign retire_rd    = instr[11:7];
    assign retire_data  = wb_data;
endmodule
