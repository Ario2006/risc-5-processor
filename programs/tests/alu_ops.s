# ABOUTME: Every ALU instruction once, including negative compares, shift by 31 and xori -1.
# ABOUTME: Checks the datapath and control unit, not hazards (independent setup values).
        addi x1, x0, 12
        addi x2, x0, -10
        addi x3, x0, 31
        nop
        nop
        nop
        add  x4, x1, x2
        sub  x5, x1, x2
        and  x6, x1, x2
        or   x7, x1, x2
        xor  x8, x1, x2
        slt  x9, x2, x1
        slt  x10, x1, x2
        sll  x11, x1, x3
        addi x12, x2, 2047
        slti x13, x2, -9
        xori x14, x1, -1
        ori  x15, x2, 255
        andi x16, x2, -256
        slli x17, x1, 31
        slli x18, x2, 0
        ecall
