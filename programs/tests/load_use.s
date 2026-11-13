# ABOUTME: Loads followed at once by a use on rs1, on rs2, as a base address and as store data.
# ABOUTME: Each pair needs exactly one load-use stall with forwarding on.
        lw   x1, 0(x0)
        add  x2, x1, x0        # rs1 use
        lw   x3, 4(x0)
        add  x4, x0, x3        # rs2 use
        lw   x5, 8(x0)
        lw   x6, 0(x5)         # loaded value is the next address
        lw   x7, 12(x0)
        sw   x7, 16(x0)        # loaded value is store data
        lw   x8, 16(x0)
        addi x8, x8, 1
        ecall
.data
        .word 10, 20, 4, 30, 0
