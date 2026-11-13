# ABOUTME: Read-after-write chains at distance 1, 2 and 3 on both ALU operands.
# ABOUTME: Distance 1 needs EX/MEM forwarding, 2 needs MEM/WB, 3 needs the register file bypass.
        addi x1, x0, 1
        add  x2, x1, x1        # distance 1 on rs1 and rs2
        add  x3, x2, x1        # distance 1 rs1, distance 2 rs2
        addi x9, x0, 100
        add  x4, x1, x3        # distance 2 on rs2... and 4 on rs1
        nop
        add  x5, x4, x4        # distance 2
        nop
        nop
        add  x6, x5, x5        # distance 3: WB writes while ID reads
        sub  x7, x6, x5
        sub  x7, x7, x1        # same rd twice in a row
        add  x8, x7, x7        # must see the newest x7
        ecall
