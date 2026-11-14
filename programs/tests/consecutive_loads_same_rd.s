# ABOUTME: Loads distinct values into the same destination in consecutive instructions.
# ABOUTME: Checks load-use recovery, then EX/MEM priority over an older MEM/WB load.
        lw   x1, 0(x0)         # older x1 = 11
        lw   x1, 4(x0)         # latest x1 = 29
        add  x2, x1, x1        # both operands must use 29: x2 = 58
        sw   x2, 12(x0)
        lw   x3, 4(x0)         # older x3 = 29
        lw   x3, 8(x0)         # latest x3 = -5
        addi x4, x3, 1         # x4 = -4
        sw   x4, 16(x0)
        lw   x7, 0(x0)         # older writer: 11, reaches MEM/WB
        addi x7, x0, 29        # newer writer: 29, reaches EX/MEM
        add  x8, x7, x7        # both sources match: EX/MEM must win, x8 = 58
        sw   x8, 20(x0)
        ecall
.data
        .word 11, 29, -5
