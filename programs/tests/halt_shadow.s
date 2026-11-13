# ABOUTME: Instructions fetched after ecall must never change registers or memory.
# ABOUTME: The pipeline fetches them before ecall reaches WB, so it has to stop and squash them.
        addi x1, x0, 1
        ecall
        addi x2, x0, 2
        sw   x1, 0(x0)
        addi x3, x0, 3
