// ABOUTME: Hazard unit: stalls on data hazards, flushes on taken branches, stops fetch at ecall.
// ABOUTME: With forwarding only a load-use stalls; without it every RAW on EX or MEM stalls.
// Author: Sarvesh Srinath
`default_nettype none

module hazard_unit #(
    parameter FORWARDING = 1
) (
    input  wire       clk,
    input  wire       rst,
    // instruction in ID
    input  wire [4:0] id_rs1,
    input  wire [4:0] id_rs2,
    input  wire       id_uses_rs1,
    input  wire       id_uses_rs2,
    input  wire       id_halt,
    // instruction in EX
    input  wire       ex_reg_write,
    input  wire       ex_mem_read,
    input  wire [4:0] ex_rd,
    input  wire       ex_taken,
    // instruction in MEM
    input  wire       mem_reg_write,
    input  wire [4:0] mem_rd,
    output wire       pc_write,
    output wire       if_id_en,
    output wire       if_id_flush,
    output wire       id_ex_flush,
    output wire       stall,
    output wire       load_use,
    output wire       flush
);
    // Does the instruction in ID read register r? (Written out per producer, not as a function,
    // because a function called from assign only re-evaluates when its arguments change.)
    wire reads_ex  = (id_uses_rs1 && id_rs1 == ex_rd)  || (id_uses_rs2 && id_rs2 == ex_rd);
    wire reads_mem = (id_uses_rs1 && id_rs1 == mem_rd) || (id_uses_rs2 && id_rs2 == mem_rd);

    // ex_reg_write and mem_reg_write are 0 for x0 destinations.
    assign load_use = ex_mem_read && ex_reg_write && reads_ex;
    wire raw_ex     = ex_reg_write && reads_ex;
    wire raw_mem    = mem_reg_write && reads_mem;

    assign flush = ex_taken;
    assign stall = !flush && (FORWARDING ? load_use : (raw_ex || raw_mem));

    // After ecall leaves ID nothing younger may enter the pipeline.
    reg  fetch_stopped;
    wire stop_now = !flush && (id_halt || fetch_stopped);
    always @(posedge clk) begin
        if (rst)                    fetch_stopped <= 1'b0;
        else if (id_halt && !flush) fetch_stopped <= 1'b1;
    end

    assign pc_write    = !stall && !stop_now;
    assign if_id_en    = !stall;
    assign if_id_flush = flush || stop_now;
    assign id_ex_flush = flush || stall;
endmodule
