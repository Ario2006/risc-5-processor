// ABOUTME: Forwarding unit: sends a result still in EX/MEM or MEM/WB straight to the EX operands.
// ABOUTME: The newest producer (EX/MEM) wins. ENABLE=0 turns forwarding off for the comparison.
`default_nettype none

module forwarding_unit #(
    parameter ENABLE = 1
) (
    input  wire [4:0] ex_rs1,
    input  wire [4:0] ex_rs2,
    input  wire       ex_mem_reg_write,
    input  wire [4:0] ex_mem_rd,
    input  wire       mem_wb_reg_write,
    input  wire [4:0] mem_wb_rd,
    output wire [1:0] fwd_a,
    output wire [1:0] fwd_b
);
    // reg_write is already 0 when rd is x0 (see id_stage), so x0 is never forwarded.
    // always @(*) and not a function: a function called from assign only re-evaluates when
    // its arguments change, so it would miss changes to ex_mem_rd and the other signals.
    reg [1:0] a_sel, b_sel;
    always @(*) begin
        a_sel = 2'b00;
        b_sel = 2'b00;
        if (ex_mem_reg_write && ex_mem_rd == ex_rs1)      a_sel = 2'b10;
        else if (mem_wb_reg_write && mem_wb_rd == ex_rs1) a_sel = 2'b01;
        if (ex_mem_reg_write && ex_mem_rd == ex_rs2)      b_sel = 2'b10;
        else if (mem_wb_reg_write && mem_wb_rd == ex_rs2) b_sel = 2'b01;
    end

    assign fwd_a = ENABLE ? a_sel : 2'b00;
    assign fwd_b = ENABLE ? b_sel : 2'b00;
endmodule
