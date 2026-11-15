// ABOUTME: Instruction memory (ROM), word addressed, asynchronous read.
// ABOUTME: Loaded from INIT_FILE, or in simulation from the +imem=<file> plusarg.
// Author: Sarvesh Srinath
`default_nettype none

module imem #(
    parameter DEPTH = 256,
    parameter INIT_FILE = ""
) (
    input  wire [31:0] addr,     // byte address
    output wire [31:0] rdata
);
    // Synthesis with MEM_DISTRIBUTED builds this ROM from LUTs, so it cannot absorb the
    // pipeline register that follows it into a slow block RAM (see the report, Synthesis).
`ifdef MEM_DISTRIBUTED
    (* ram_style = "logic" *)
`endif
    reg [31:0] mem [0:DEPTH-1];

    integer i;
    initial begin
        if (INIT_FILE != "") $readmemh(INIT_FILE, mem);
`ifndef SYNTHESIS
        // Simulation only: in synthesis Yosys can let this fill override the file contents,
        // so the tools always pass files padded to DEPTH words instead.
        for (i = 0; i < DEPTH; i = i + 1) mem[i] = 32'h00000013;
        if (INIT_FILE != "") $readmemh(INIT_FILE, mem);
        begin : plusarg_load
            reg [8*1024-1:0] file;
            if ($value$plusargs("imem=%s", file)) $readmemh(file, mem);
        end
`endif
    end

    assign rdata = mem[addr[$clog2(DEPTH)+1:2]];
endmodule
