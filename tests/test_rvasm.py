# ABOUTME: Checks the RV32I subset assembler against encodings from the RISC-V spec.
# ABOUTME: Covers every supported instruction, labels, pseudo-instructions and the data section.
import pytest

from tools.rvasm import AsmError, assemble


def words(src: str) -> list[int]:
    """Assemble src and return only the instruction words."""
    return assemble(src).text


@pytest.mark.parametrize(
    "line, expected",
    [
        ("addi x1, x0, 5", 0x00500093),
        ("addi x1, x0, -1", 0xFFF00093),
        ("andi x2, x1, 255", 0x0FF0F113),
        ("ori x2, x1, 1", 0x0010E113),
        ("xori x2, x1, -1", 0xFFF0C113),
        ("slti x2, x1, 3", 0x0030A113),
        ("slli x1, x1, 2", 0x00209093),
        ("add x3, x1, x2", 0x002081B3),
        ("sub x3, x1, x2", 0x402081B3),
        ("and x3, x1, x2", 0x0020F1B3),
        ("or x3, x1, x2", 0x0020E1B3),
        ("xor x3, x1, x2", 0x0020C1B3),
        ("slt x3, x1, x2", 0x0020A1B3),
        ("sll x3, x1, x2", 0x002091B3),
        ("lw x5, 8(x2)", 0x00812283),
        ("lw x5, -4(x2)", 0xFFC12283),
        ("sw x5, 12(x2)", 0x00512623),
        ("sw x5, -4(x2)", 0xFE512E23),
        ("ecall", 0x00000073),
        ("nop", 0x00000013),
        ("add t0, sp, a0", 0x00A102B3),
    ],
)
def test_single_instruction_encoding(line, expected):
    assert words(line) == [expected]


def test_backward_branch_offset():
    src = """
    loop: nop
          nop
          beq x1, x2, loop
    """
    assert words(src)[2] == 0xFE208CE3


def test_forward_branch_offset():
    src = """
          bne x1, x2, done
          nop
    done: ecall
    """
    # offset +8: imm[3]=1 -> bits 11:8 hold imm[4:1] = 0b0100
    assert words(src)[0] == 0x00209463


def test_pseudo_instructions():
    src = """
    start: li x1, 7
           mv x2, x1
           j start
           beqz x1, start
           bnez x1, start
           halt
    """
    w = words(src)
    assert w[0] == 0x00700093
    assert w[1] == 0x00008113
    assert w[2] == 0xFE000CE3  # beq x0, x0, -8
    assert w[3] == 0xFE008AE3  # beq x1, x0, -12
    assert w[4] == 0xFE0098E3  # bne x1, x0, -16
    assert w[5] == 0x00000073


def test_data_section_and_la():
    src = """
    .data
    arr: .word 3, -1, 0x10
    n:   .word 3
    .text
         la x1, n
         lw x2, 0(x1)
    """
    prog = assemble(src)
    assert prog.data == [3, 0xFFFFFFFF, 0x10, 3]
    assert prog.text[0] == 0x00C00093  # addi x1, x0, 12
    assert prog.labels["arr"] == 0


def test_immediate_out_of_range_is_rejected():
    with pytest.raises(AsmError):
        assemble("addi x1, x0, 2048")


def test_unknown_instruction_is_rejected():
    with pytest.raises(AsmError):
        assemble("mul x1, x2, x3")


def test_unknown_label_is_rejected():
    with pytest.raises(AsmError):
        assemble("beq x0, x0, nowhere")


def test_hex_output_has_one_word_per_line():
    prog = assemble("addi x1, x0, 5\necall")
    assert prog.text_hex() == "00500093\n00000073\n"
