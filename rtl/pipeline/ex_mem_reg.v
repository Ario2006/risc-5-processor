// ABOUTME: EX/MEM pipeline register: ALU result, store data, destination and memory/WB control.
// ABOUTME: Never stalls or flushes; anything that reaches EX/MEM will complete.
// Author: Sarvesh Srinath
`default_nettype none

module ex_mem_reg (
    input  wire        clk,
    input  wire        rst,
    input  wire        valid_in,
    input  wire [31:0] pc_in,
    input  wire [31:0] alu_y_in,
    input  wire [31:0] store_data_in,
    input  wire [4:0]  rd_in,
    input  wire        reg_write_in, mem_read_in, mem_write_in, halt_in,
    output reg         valid,
    output reg  [31:0] pc,
    output reg  [31:0] alu_y,
    output reg  [31:0] store_data,
    output reg  [4:0]  rd,
    output reg         reg_write, mem_read, mem_write, halt
);
    always @(posedge clk) begin
        if (rst) begin
            valid <= 1'b0; pc <= 32'b0; alu_y <= 32'b0; store_data <= 32'b0; rd <= 5'd0;
            reg_write <= 1'b0; mem_read <= 1'b0; mem_write <= 1'b0; halt <= 1'b0;
        end else begin
            valid <= valid_in; pc <= pc_in; alu_y <= alu_y_in; store_data <= store_data_in;
            rd <= rd_in; reg_write <= reg_write_in; mem_read <= mem_read_in;
            mem_write <= mem_write_in; halt <= halt_in;
        end
    end
endmodule
