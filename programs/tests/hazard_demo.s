# ABOUTME: Short program that shows each pipeline event once, for the pipeline diagram and waveform.
# ABOUTME: Forwarding, a load-use stall, a taken branch with two flushed instructions, then ecall.
        addi x1, x0, 5
        add  x2, x1, x1        # needs x1 from the instruction just before: forwarding
        lw   x3, 0(x0)
        add  x4, x3, x1        # needs the load at once: one load-use stall
        beq  x4, x4, skip      # always taken: two wrong-path instructions are flushed
        addi x5, x0, 1
        addi x6, x0, 1
skip:   sw   x4, 4(x0)
        ecall
.data
        .word 7
