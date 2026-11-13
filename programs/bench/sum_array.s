# ABOUTME: Benchmark: sum a 16 word array with a counted loop.
# ABOUTME: Loop body has a load-use pair and a taken backward branch per iteration.
.data
arr:    .word 3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3
result: .word 0
.text
        la   x1, arr           # pointer
        addi x2, x0, 16        # count
        addi x3, x0, 0         # sum
loop:   lw   x4, 0(x1)
        add  x3, x3, x4        # uses the load at once
        addi x1, x1, 4
        addi x2, x2, -1
        bnez x2, loop
        la   x5, result
        sw   x3, 0(x5)
        ecall
