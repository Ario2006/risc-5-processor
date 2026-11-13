# ABOUTME: Writes to x0 must be dropped and must never be forwarded or cause a stall.
# ABOUTME: A forwarding bug would make x2 or x3 nonzero here.
        addi x0, x0, 5
        add  x2, x0, x0
        lw   x0, 0(x0)
        add  x3, x0, x0
        sw   x0, 4(x0)
        ecall
.data
        .word 99, 77
