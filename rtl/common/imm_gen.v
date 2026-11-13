// ABOUTME: Immediate generator: builds the sign extended I, S or B immediate from an instruction.
// ABOUTME: The format is chosen from the opcode, so no extra control signal is needed.
`default_nettype none
`include "defs.vh"

module imm_gen (
    input  wire [31:0] instr,
    output reg  [31:0] imm
);
    always @(*) begin
        case (instr[6:0])
            `OP_STORE:  imm = {{20{instr[31]}}, instr[31:25], instr[11:7]};
            `OP_BRANCH: imm = {{19{instr[31]}}, instr[31], instr[7], instr[30:25], instr[11:8], 1'b0};
            default:    imm = {{20{instr[31]}}, instr[31:20]};
        endcase
    end
endmodule
