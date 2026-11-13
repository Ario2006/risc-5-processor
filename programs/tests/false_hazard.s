# ABOUTME: An I-type whose immediate bits look like rs2 = the load's rd must not stall.
# ABOUTME: addi x2, x0, 1 has 00001 in the rs2 field; only real source registers count.
        lw   x1, 0(x0)
        addi x2, x0, 1
        lw   x3, 0(x0)
        addi x4, x0, 3
        ecall
.data
        .word 5
