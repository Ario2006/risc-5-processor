# ABOUTME: Benchmark: first 30 Fibonacci numbers written to memory, each from the two before it.
# ABOUTME: Long dependent chains through registers, the worst case for a CPU without forwarding.
.data
fib:    .word 0
.text
        la   x1, fib
        addi x2, x0, 0         # f(n-2)
        addi x3, x0, 1         # f(n-1)
        addi x4, x0, 30
loop:   sw   x2, 0(x1)
        add  x5, x2, x3
        mv   x2, x3
        mv   x3, x5
        addi x1, x1, 4
        addi x4, x4, -1
        bnez x4, loop
        ecall
