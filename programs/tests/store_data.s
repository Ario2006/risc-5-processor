# ABOUTME: Stores whose data or address was produced by the instruction just before.
# ABOUTME: Store data travels on rs2, so this checks forwarding on the B operand path.
        addi x1, x0, 8
        addi x2, x0, 55
        sw   x2, 0(x1)         # data and base both distance 1-2
        addi x3, x2, 1
        sw   x3, 4(x1)
        lw   x4, 4(x1)
        sw   x4, 8(x1)         # load then store of the same value
        ecall
