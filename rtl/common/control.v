// ABOUTME: Control unit: decodes opcode, funct3 and funct7 into datapath control signals.
// ABOUTME: Also reports which source registers an instruction really reads, for hazard checks.
// Author: Sarvesh Srinath
`default_nettype none
`include "defs.vh"

module control (
    input  wire [31:0] instr,
    output reg         reg_write,   // write rd in WB
    output reg         alu_src,     // ALU operand B is the immediate
    output reg         mem_read,    // load: WB takes memory data
    output reg         mem_write,   // store
    output reg         branch,      // beq or bne
    output reg         branch_ne,   // 1 for bne, 0 for beq
    output reg         halt,        // ecall ends the program
    output reg         uses_rs1,
    output reg         uses_rs2,
    output reg  [2:0]  alu_op,
    output reg         illegal
);
    wire [6:0] opcode = instr[6:0];
    wire [2:0] funct3 = instr[14:12];
    wire [6:0] funct7 = instr[31:25];

    always @(*) begin
        reg_write = 1'b0; alu_src = 1'b0; mem_read = 1'b0; mem_write = 1'b0;
        branch = 1'b0; branch_ne = 1'b0; halt = 1'b0;
        uses_rs1 = 1'b0; uses_rs2 = 1'b0; alu_op = `ALU_ADD; illegal = 1'b0;
        case (opcode)
            `OP_R: begin
                reg_write = 1'b1; uses_rs1 = 1'b1; uses_rs2 = 1'b1;
                case ({funct7, funct3})
                    {7'h00, 3'd0}: alu_op = `ALU_ADD;
                    {7'h20, 3'd0}: alu_op = `ALU_SUB;
                    {7'h00, 3'd1}: alu_op = `ALU_SLL;
                    {7'h00, 3'd2}: alu_op = `ALU_SLT;
                    {7'h00, 3'd4}: alu_op = `ALU_XOR;
                    {7'h00, 3'd6}: alu_op = `ALU_OR;
                    {7'h00, 3'd7}: alu_op = `ALU_AND;
                    default: begin illegal = 1'b1; reg_write = 1'b0; end
                endcase
            end
            `OP_I: begin
                reg_write = 1'b1; alu_src = 1'b1; uses_rs1 = 1'b1;
                case (funct3)
                    3'd0: alu_op = `ALU_ADD;
                    3'd1: if (funct7 == 7'h00) alu_op = `ALU_SLL;
                          else begin illegal = 1'b1; reg_write = 1'b0; end
                    3'd2: alu_op = `ALU_SLT;
                    3'd4: alu_op = `ALU_XOR;
                    3'd6: alu_op = `ALU_OR;
                    3'd7: alu_op = `ALU_AND;
                    default: begin illegal = 1'b1; reg_write = 1'b0; end
                endcase
            end
            `OP_LOAD: begin
                if (funct3 == 3'd2) begin
                    reg_write = 1'b1; alu_src = 1'b1; mem_read = 1'b1; uses_rs1 = 1'b1;
                end else illegal = 1'b1;
            end
            `OP_STORE: begin
                if (funct3 == 3'd2) begin
                    alu_src = 1'b1; mem_write = 1'b1; uses_rs1 = 1'b1; uses_rs2 = 1'b1;
                end else illegal = 1'b1;
            end
            `OP_BRANCH: begin
                if (funct3 == 3'd0 || funct3 == 3'd1) begin
                    branch = 1'b1; branch_ne = funct3[0]; uses_rs1 = 1'b1; uses_rs2 = 1'b1;
                end else illegal = 1'b1;
            end
            `OP_SYSTEM: begin
                if (instr == 32'h00000073) halt = 1'b1;
                else illegal = 1'b1;
            end
            default: illegal = 1'b1;
        endcase
    end
endmodule
