// ABOUTME: Data memory (RAM), word addressed, asynchronous read and synchronous write.
// ABOUTME: Loaded from INIT_FILE, or in simulation from the +dmem=<file> plusarg.
`default_nettype none

module dmem #(
    parameter DEPTH = 256,
    parameter INIT_FILE = ""
) (
    input  wire        clk,
    input  wire        we,
    input  wire [31:0] addr,     // byte address
    input  wire [31:0] wdata,
    output wire [31:0] rdata
);
    reg [31:0] mem [0:DEPTH-1];
    wire [$clog2(DEPTH)-1:0] word = addr[$clog2(DEPTH)+1:2];

    integer i;
    initial begin
        for (i = 0; i < DEPTH; i = i + 1) mem[i] = 32'b0;
        if (INIT_FILE != "") $readmemh(INIT_FILE, mem);
`ifndef SYNTHESIS
        begin : plusarg_load
            reg [1023:0] file;
            if ($value$plusargs("dmem=%s", file)) $readmemh(file, mem);
        end
`endif
    end

    always @(posedge clk)
        if (we) mem[word] <= wdata;

    assign rdata = mem[word];
endmodule
