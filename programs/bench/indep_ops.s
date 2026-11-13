# ABOUTME: Microbenchmark: the same work as dep_chain.s but spread over independent registers.
# ABOUTME: Close to the ideal CPI of 1; only the loop branch costs cycles.
        addi x9, x0, 20
loop:   addi x1, x1, 1
        addi x2, x2, 2
        addi x3, x3, 3
        addi x4, x4, 4
        addi x5, x5, 5
        addi x6, x6, 6
        addi x9, x9, -1
        bnez x9, loop
        ecall
