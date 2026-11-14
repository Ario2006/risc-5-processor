# ABOUTME: beq and bne taken and not taken, on freshly computed and freshly loaded operands.
# ABOUTME: Instructions in each taken branch's shadow would corrupt state if not flushed.
        addi x1, x0, 3
        addi x2, x0, 3
        beq  x1, x2, t1        # taken, operands from distance 1 and 2
        addi x10, x0, 1        # shadow: must be flushed
        sw   x1, 0(x0)         # shadow: must be flushed
t1:     bne  x1, x2, bad       # not taken
        addi x3, x1, 1
        bne  x3, x1, t2        # taken, operand from distance 1
        addi x11, x0, 1
        addi x12, x0, 1
t2:     lw   x4, 4(x0)
        beq  x4, x1, t3        # load-use into a branch
        addi x13, x0, 1
t3:     beq  x0, x0, t4        # back-to-back branches
t4:     beq  x0, x0, t5
        addi x14, x0, 1
t5:     addi x5, x0, 7
        beq  x1, x5, bad       # not taken: 3 != 7
        addi x16, x0, 42       # proves the unequal BEQ fell through
        ecall
bad:    addi x15, x0, 1
        ecall
.data
        .word 0, 3
