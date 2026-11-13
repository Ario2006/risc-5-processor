# ABOUTME: Checks the Python reference model (instruction set simulator) on small programs.
# ABOUTME: The RTL is later compared against this model, so it must be right first.
from tools.iss import run
from tools.rvasm import assemble


def regs_after(src: str) -> list[int]:
    """Assemble and run src, return the 32 final registers."""
    return run(assemble(src)).regs


def test_arithmetic_and_x0_stays_zero():
    r = regs_after("""
        addi x1, x0, 5
        addi x2, x0, -3
        add  x3, x1, x2
        sub  x4, x1, x2
        addi x0, x0, 9
        ecall
    """)
    assert r[3] == 2
    assert r[4] == 8
    assert r[2] == 0xFFFFFFFD
    assert r[0] == 0


def test_logic_shift_and_compare():
    r = regs_after("""
        addi x1, x0, 12
        addi x2, x0, 10
        and  x3, x1, x2
        or   x4, x1, x2
        xor  x5, x1, x2
        slt  x6, x2, x1
        slt  x7, x1, x2
        addi x8, x0, -1
        slti x9, x8, 0
        slli x10, x1, 4
        addi x11, x0, 3
        sll  x12, x1, x11
        andi x13, x1, 4
        ori  x14, x1, 1
        xori x15, x1, -1
        ecall
    """)
    assert r[3:8] == [8, 14, 6, 1, 0]
    assert r[9] == 1
    assert r[10] == 192
    assert r[12] == 96
    assert r[13:16] == [4, 13, 0xFFFFFFF3]


def test_load_store_and_data_section():
    result = run(assemble("""
        .data
        a: .word 41
        b: .word 0
        .text
        la  x1, a
        lw  x2, 0(x1)
        addi x2, x2, 1
        sw  x2, 4(x1)
        ecall
    """))
    assert result.dmem[1] == 42
    assert result.regs[2] == 42


def test_loop_counts_instructions():
    result = run(assemble("""
        addi x1, x0, 0
        addi x2, x0, 5
    loop:
        addi x1, x1, 1
        bne  x1, x2, loop
        ecall
    """))
    assert result.regs[1] == 5
    # 2 setup + 5 iterations x 2 + ecall
    assert result.instret == 13


def test_beq_taken_and_not_taken():
    r = regs_after("""
        addi x1, x0, 1
        beq  x1, x0, skip
        addi x2, x0, 7
    skip:
        beq  x0, x0, end
        addi x3, x0, 9
    end:
        ecall
    """)
    assert r[2] == 7
    assert r[3] == 0
