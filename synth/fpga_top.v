// ABOUTME: FPGA wrapper: runs one CPU configuration with a program baked into instruction memory.
// ABOUTME: LEDs show the low bits of the last value written back, plus a halted light.
`default_nettype none

module fpga_top #(
    parameter CONFIG = 2,          // 0 single-cycle, 1 pipeline without forwarding, 2 with
    parameter IMEM_INIT = "",
    parameter DMEM_INIT = ""
) (
    input  wire       clk,
    input  wire       btn_rst,      // active high reset button
    output reg  [7:0] led
);
    // Two flip-flop synchroniser so the button does not cause metastability.
    reg [1:0] rst_sync = 2'b11;
    always @(posedge clk) rst_sync <= {rst_sync[0], btn_rst};
    wire rst = rst_sync[1];

    wire        halted, retire_valid, retire_we, illegal;
    wire [31:0] retire_pc, retire_data;
    wire [4:0]  retire_rd;

    generate
        if (CONFIG == 0) begin : cpu
            cpu_single #(.IMEM_INIT(IMEM_INIT), .DMEM_INIT(DMEM_INIT)) core (
                .clk(clk), .rst(rst), .halted(halted), .retire_valid(retire_valid),
                .retire_pc(retire_pc), .retire_we(retire_we), .retire_rd(retire_rd),
                .retire_data(retire_data), .illegal(illegal));
        end else begin : cpu
            cpu_pipeline #(.FORWARDING(CONFIG == 2), .IMEM_INIT(IMEM_INIT), .DMEM_INIT(DMEM_INIT)) core (
                .clk(clk), .rst(rst), .halted(halted), .retire_valid(retire_valid),
                .retire_pc(retire_pc), .retire_we(retire_we), .retire_rd(retire_rd),
                .retire_data(retire_data), .illegal(illegal));
        end
    endgenerate

    reg done;
    always @(posedge clk) begin
        if (rst) begin
            led  <= 8'b0;
            done <= 1'b0;
        end else begin
            if (halted) done <= 1'b1;
            if (retire_we && !done) led[6:0] <= retire_data[6:0];
            led[7] <= done;
        end
    end
endmodule
