// ABOUTME: PC/IF stage: holds the program counter and fetches the instruction at it.
// ABOUTME: The PC holds on a stall and jumps to the branch target when EX redirects it.
`default_nettype none

module if_stage #(
    parameter IMEM_INIT = ""
) (
    input  wire        clk,
    input  wire        rst,
    input  wire        pc_write,      // 0 freezes the PC (stall or halt)
    input  wire        redirect,      // taken branch resolved in EX
    input  wire [31:0] redirect_pc,
    output reg  [31:0] pc,
    output wire [31:0] instr
);
    imem #(.INIT_FILE(IMEM_INIT)) imem_i (.addr(pc), .rdata(instr));

    always @(posedge clk) begin
        if (rst)           pc <= 32'b0;
        else if (redirect) pc <= redirect_pc;
        else if (pc_write) pc <= pc + 32'd4;
    end
endmodule
