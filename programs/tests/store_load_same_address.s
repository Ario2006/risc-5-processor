# ABOUTME: Stores and immediately reloads the same address, including an overwrite.
# ABOUTME: Catches stale memory reads and store-data forwarding failures on all CPUs.
        addi x1, x0, 16
        addi x2, x0, 55
        sw   x2, 0(x1)
        lw   x3, 0(x1)         # x3 must see 55, not the initial zero
        addi x4, x0, -7
        sw   x4, 0(x1)
        lw   x5, 0(x1)         # x5 must see -7, not the old 55
        add  x6, x3, x5        # x6 = 48; also exercises load-use
        sw   x6, 4(x1)
        ecall
