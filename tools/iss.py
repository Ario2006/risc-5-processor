# ABOUTME: Instruction set simulator for the RV32I subset: the golden reference for the RTL.
# ABOUTME: Runs a Program one instruction at a time and returns registers, data memory, count.
from dataclasses import dataclass

from tools.rvasm import Program

MASK = 0xFFFFFFFF
DMEM_WORDS = 256


class IssError(Exception):
    """Raised when the program does something the CPU does not support."""


@dataclass
class Result:
    """Final architectural state after ecall."""

    regs: list[int]
    dmem: list[int]
    instret: int


def sext(value: int, bits: int) -> int:
    """Sign extend a bits wide field to a Python int."""
    sign = 1 << (bits - 1)
    return (value & (sign - 1)) - (value & sign)


def signed(x: int) -> int:
    return sext(x, 32)


def run(prog: Program, max_steps: int = 100_000) -> Result:
    """Execute until ecall; raise IssError on anything unsupported."""
    regs = [0] * 32
    dmem = (prog.data + [0] * DMEM_WORDS)[:DMEM_WORDS]
    pc = 0
    for count in range(1, max_steps + 1):
        if pc % 4 or pc // 4 >= len(prog.text):
            raise IssError(f"pc 0x{pc:x} outside the program")
        inst = prog.text[pc // 4]
        op, rd, f3 = inst & 0x7F, (inst >> 7) & 0x1F, (inst >> 12) & 7
        rs1, rs2, f7 = (inst >> 15) & 0x1F, (inst >> 20) & 0x1F, inst >> 25
        a, b = regs[rs1], regs[rs2]
        imm_i = sext(inst >> 20, 12)
        next_pc = pc + 4
        result = None
        if op == 0x33:
            result = {
                (0, 0x00): a + b, (0, 0x20): a - b, (1, 0x00): a << (b & 31),
                (2, 0x00): int(signed(a) < signed(b)), (4, 0x00): a ^ b,
                (6, 0x00): a | b, (7, 0x00): a & b,
            }.get((f3, f7))
            if result is None:
                raise IssError(f"unsupported R-type 0x{inst:08x}")
        elif op == 0x13:
            if f3 == 1:
                result = a << (imm_i & 31)
            else:
                result = {
                    0: a + imm_i, 2: int(signed(a) < imm_i), 4: a ^ (imm_i & MASK),
                    6: a | (imm_i & MASK), 7: a & (imm_i & MASK),
                }.get(f3)
            if result is None:
                raise IssError(f"unsupported I-type 0x{inst:08x}")
        elif op == 0x03 and f3 == 2:
            addr = (a + imm_i) & MASK
            if addr % 4 or addr // 4 >= DMEM_WORDS:
                raise IssError(f"bad load address 0x{addr:x}")
            result = dmem[addr // 4]
        elif op == 0x23 and f3 == 2:
            imm_s = sext(((inst >> 25) << 5) | ((inst >> 7) & 0x1F), 12)
            addr = (a + imm_s) & MASK
            if addr % 4 or addr // 4 >= DMEM_WORDS:
                raise IssError(f"bad store address 0x{addr:x}")
            dmem[addr // 4] = b
        elif op == 0x63 and f3 in (0, 1):
            imm_b = sext(
                (((inst >> 31) & 1) << 12) | (((inst >> 7) & 1) << 11)
                | (((inst >> 25) & 0x3F) << 5) | (((inst >> 8) & 0xF) << 1), 13)
            if (a == b) == (f3 == 0):
                next_pc = pc + imm_b
        elif inst == 0x73:
            return Result(regs=regs, dmem=dmem, instret=count)
        else:
            raise IssError(f"unsupported instruction 0x{inst:08x} at pc 0x{pc:x}")
        if result is not None and rd:
            regs[rd] = result & MASK
        pc = next_pc
    raise IssError(f"no ecall within {max_steps} instructions")
