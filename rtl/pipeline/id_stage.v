// ABOUTME: Decode/Register File stage: control unit, immediate generator and register file.
// ABOUTME: WB writes the register file here; write-through lets ID read a value written this cycle.
`default_nettype none

module id_stage (
    input  wire        clk,
    input  wire        valid,
    input  wire [31:0] instr,
    // write port, driven by WB
    input  wire        wb_we,
    input  wire [4:0]  wb_rd,
    input  wire [31:0] wb_data,
    // decoded outputs; control is zero for a bubble
    output wire        reg_write,
    output wire        alu_src,
    output wire        mem_read,
    output wire        mem_write,
    output wire        branch,
    output wire        branch_ne,
    output wire        halt,
    output wire        uses_rs1,
    output wire        uses_rs2,
    output wire [2:0]  alu_op,
    output wire        illegal,
    output wire [31:0] rs1_val,
    output wire [31:0] rs2_val,
    output wire [31:0] imm,
    output wire [4:0]  rs1,
    output wire [4:0]  rs2,
    output wire [4:0]  rd
);
    wire c_reg_write, c_alu_src, c_mem_read, c_mem_write, c_branch, c_branch_ne, c_halt;
    wire c_uses_rs1, c_uses_rs2, c_illegal;
    control ctrl (
        .instr(instr), .reg_write(c_reg_write), .alu_src(c_alu_src), .mem_read(c_mem_read),
        .mem_write(c_mem_write), .branch(c_branch), .branch_ne(c_branch_ne), .halt(c_halt),
        .uses_rs1(c_uses_rs1), .uses_rs2(c_uses_rs2), .alu_op(alu_op), .illegal(c_illegal)
    );

    assign reg_write = valid && c_reg_write && rd != 5'd0;
    assign alu_src   = c_alu_src;
    assign mem_read  = valid && c_mem_read;
    assign mem_write = valid && c_mem_write;
    assign branch    = valid && c_branch;
    assign branch_ne = c_branch_ne;
    assign halt      = valid && c_halt;
    assign uses_rs1  = valid && c_uses_rs1;
    assign uses_rs2  = valid && c_uses_rs2;
    assign illegal   = valid && c_illegal;

    imm_gen immg (.instr(instr), .imm(imm));

    assign rs1 = instr[19:15];
    assign rs2 = instr[24:20];
    assign rd  = instr[11:7];

    regfile #(.WRITE_THROUGH(1)) rf (
        .clk(clk), .we(wb_we), .waddr(wb_rd), .wdata(wb_data),
        .raddr1(rs1), .raddr2(rs2), .rdata1(rs1_val), .rdata2(rs2_val)
    );
endmodule
