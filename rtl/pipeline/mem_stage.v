// ABOUTME: Memory/MEM stage: the data memory, read by loads and written by stores.
// ABOUTME: The ALU result is the byte address; only aligned word access is supported.
// Author: Sarvesh Srinath
`default_nettype none

module mem_stage #(
    parameter DMEM_INIT = ""
) (
    input  wire        clk,
    input  wire        mem_write,
    input  wire [31:0] addr,
    input  wire [31:0] store_data,
    output wire [31:0] load_data
);
    dmem #(.INIT_FILE(DMEM_INIT)) dmem_i (
        .clk(clk), .we(mem_write), .addr(addr), .wdata(store_data), .rdata(load_data)
    );
endmodule
