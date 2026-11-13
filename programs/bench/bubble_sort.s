# ABOUTME: Benchmark: bubble sort of 12 words in memory, with slt and swaps.
# ABOUTME: Mixes loads, stores, compares and data-dependent branches.
.data
arr:    .word 42, -7, 19, 0, 88, 3, -21, 64, 5, 5, 13, -2
.text
        addi x10, x0, 12       # n
outer:  addi x10, x10, -1
        beqz x10, done
        la   x1, arr
        mv   x11, x10          # inner count
inner:  lw   x2, 0(x1)
        lw   x3, 4(x1)
        slt  x4, x3, x2        # out of order?
        beqz x4, noswap
        sw   x3, 0(x1)
        sw   x2, 4(x1)
noswap: addi x1, x1, 4
        addi x11, x11, -1
        bnez x11, inner
        j    outer
done:   ecall
