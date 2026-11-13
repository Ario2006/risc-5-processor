// ABOUTME: Testbench for both CPUs: runs a program to ecall, then dumps state and performance counts.
// ABOUTME: Define PIPELINE to test cpu_pipeline (FORWARDING sets its parameter), else cpu_single.
`timescale 1ns/1ps
`default_nettype none

module tb_cpu;
    reg clk = 1'b0;
    reg rst = 1'b1;
    always #5 clk = ~clk;   // 100 MHz in simulation; real timing comes from synthesis

    wire        halted, retire_valid, retire_we, illegal;
    wire [31:0] retire_pc, retire_data;
    wire [4:0]  retire_rd;

`ifdef PIPELINE
  `ifndef FORWARDING
    `define FORWARDING 1
  `endif
    cpu_pipeline #(.FORWARDING(`FORWARDING)) dut (
`else
    cpu_single dut (
`endif
        .clk(clk), .rst(rst), .halted(halted), .retire_valid(retire_valid),
        .retire_pc(retire_pc), .retire_we(retire_we), .retire_rd(retire_rd),
        .retire_data(retire_data), .illegal(illegal)
    );

`ifdef PIPELINE
    `define RF_REGS  dut.id.rf.regs
    `define DMEM_MEM dut.mem.dmem_i.mem
`else
    `define RF_REGS  dut.rf.regs
    `define DMEM_MEM dut.dmem_i.mem
`endif

    integer cycles = 0, instret = 0, stalls = 0, load_use = 0, flushes = 0;
    integer max_cycles = 200000;
    integer trace_fd = 0, i, fd;
    reg [1023:0] path;
    reg running = 1'b0;

    initial begin
        if ($value$plusargs("vcd=%s", path)) begin
            $dumpfile(path);
            $dumpvars(0, tb_cpu);
        end
        if ($value$plusargs("trace=%s", path)) begin
            trace_fd = $fopen(path, "w");
            $fdisplay(trace_fd, "cycle if_v if id_v id ex_v ex mem_v mem wb_v wb stall flush");
        end
        if ($value$plusargs("max_cycles=%d", max_cycles)) ;
        repeat (2) @(posedge clk);
        #1 rst = 1'b0;
        running = 1'b1;
    end

    // Sample in the middle of each cycle, when every signal has settled.
    always @(negedge clk) if (running) begin
        if (illegal) begin
            $display("FAIL illegal instruction near pc 0x%08x", retire_pc);
            $fatal(1);
        end
        if (retire_valid) instret = instret + 1;
`ifdef PIPELINE
        if (dut.stall)    stalls   = stalls + 1;
        if (dut.load_use) load_use = load_use + 1;
        if (dut.flush)    flushes  = flushes + 1;
        if (trace_fd)
            $fdisplay(trace_fd, "%0d 1 %0x %0d %0x %0d %0x %0d %0x %0d %0x %0d %0d", cycles,
                      dut.if_s.pc, dut.id_valid, dut.id_pc, dut.ex_valid, dut.ex_pc,
                      dut.mem_valid, dut.mem_pc, dut.wb_valid, dut.wb_pc, dut.stall, dut.flush);
`else
        if (trace_fd)
            $fdisplay(trace_fd, "%0d 1 %0x 1 %0x 1 %0x 1 %0x 1 %0x 0 0", cycles,
                      retire_pc, retire_pc, retire_pc, retire_pc, retire_pc);
`endif
        cycles = cycles + 1;
        if (halted) begin
            if ($value$plusargs("dump=%s", path)) begin
                fd = $fopen(path, "w");
                for (i = 0; i < 32; i = i + 1)  $fdisplay(fd, "r %0d %08x", i, `RF_REGS[i]);
                for (i = 0; i < 256; i = i + 1) $fdisplay(fd, "m %0d %08x", i, `DMEM_MEM[i]);
                $fdisplay(fd, "cycles %0d", cycles);
                $fdisplay(fd, "instret %0d", instret);
                $fdisplay(fd, "stalls %0d", stalls);
                $fdisplay(fd, "load_use %0d", load_use);
                $fdisplay(fd, "flushes %0d", flushes);
                $fclose(fd);
            end
            if (trace_fd) $fclose(trace_fd);
            $display("HALT cycles=%0d instret=%0d stalls=%0d load_use=%0d flushes=%0d",
                     cycles, instret, stalls, load_use, flushes);
            $finish;
        end
        if (cycles >= max_cycles) begin
            $display("FAIL no ecall after %0d cycles", cycles);
            $fatal(1);
        end
    end
endmodule
