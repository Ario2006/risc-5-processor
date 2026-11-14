# ABOUTME: Loads distinct values into the same destination in consecutive instructions.
# ABOUTME: Catches forwarding of the older load when the consumer needs the latest value.
        lw   x1, 0(x0)         # older x1 = 11
        lw   x1, 4(x0)         # latest x1 = 29
        add  x2, x1, x1        # both operands must use 29: x2 = 58
        sw   x2, 12(x0)
        lw   x3, 4(x0)         # older x3 = 29
        lw   x3, 8(x0)         # latest x3 = -5
        addi x4, x3, 1         # x4 = -4
        sw   x4, 16(x0)
        ecall
.data
        .word 11, 29, -5
