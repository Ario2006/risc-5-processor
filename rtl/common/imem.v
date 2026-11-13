// ABOUTME: Instruction memory (ROM), word addressed, asynchronous read.
// ABOUTME: Loaded from INIT_FILE, or in simulation from the +imem=<file> plusarg.
`default_nettype none

module imem #(
    parameter DEPTH = 256,
    parameter INIT_FILE = ""
) (
    input  wire [31:0] addr,     // byte address
    output wire [31:0] rdata
);
    reg [31:0] mem [0:DEPTH-1];

    integer i;
    initial begin
        for (i = 0; i < DEPTH; i = i + 1) mem[i] = 32'h00000013;
        if (INIT_FILE != "") $readmemh(INIT_FILE, mem);
`ifndef SYNTHESIS
        begin : plusarg_load
            reg [1023:0] file;
            if ($value$plusargs("imem=%s", file)) $readmemh(file, mem);
        end
`endif
    end

    assign rdata = mem[addr[$clog2(DEPTH)+1:2]];
endmodule
