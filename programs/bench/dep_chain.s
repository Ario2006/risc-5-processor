# ABOUTME: Microbenchmark: each instruction needs the one right before it (worst case for hazards).
# ABOUTME: Shows how much forwarding saves; compare with indep_ops.s.
        addi x1, x0, 0
        addi x9, x0, 20
loop:   addi x1, x1, 1
        add  x1, x1, x1
        sub  x1, x1, x9
        xor  x1, x1, x9
        addi x1, x1, 3
        slli x1, x1, 1
        addi x9, x9, -1
        bnez x9, loop
        ecall
