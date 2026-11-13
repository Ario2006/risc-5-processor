# ABOUTME: Two pass assembler for the RV32I subset this CPU runs, with labels and a data section.
# ABOUTME: Writes $readmemh hex files for instruction and data memory. Run: python -m tools.rvasm f.s
import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ABI = {
    "zero": 0, "ra": 1, "sp": 2, "gp": 3, "tp": 4, "t0": 5, "t1": 6, "t2": 7,
    "s0": 8, "fp": 8, "s1": 9, "a0": 10, "a1": 11, "a2": 12, "a3": 13, "a4": 14,
    "a5": 15, "a6": 16, "a7": 17, "s2": 18, "s3": 19, "s4": 20, "s5": 21, "s6": 22,
    "s7": 23, "s8": 24, "s9": 25, "s10": 26, "s11": 27, "t3": 28, "t4": 29, "t5": 30,
    "t6": 31,
}

# name: (funct7, funct3)
R_TYPE = {
    "add": (0x00, 0), "sub": (0x20, 0), "sll": (0x00, 1), "slt": (0x00, 2),
    "xor": (0x00, 4), "or": (0x00, 6), "and": (0x00, 7),
}
I_TYPE = {"addi": 0, "slti": 2, "xori": 4, "ori": 6, "andi": 7}
B_TYPE = {"beq": 0, "bne": 1}

OP_R, OP_I, OP_LOAD, OP_STORE, OP_BRANCH, OP_SYSTEM = 0x33, 0x13, 0x03, 0x23, 0x63, 0x73

SUPPORTED = sorted([*R_TYPE, *I_TYPE, "slli", "lw", "sw", *B_TYPE, "ecall"])


class AsmError(Exception):
    """Raised for any line the assembler cannot encode."""


@dataclass
class Program:
    """Assembled output: instruction words, data words and label addresses."""

    text: list[int] = field(default_factory=list)
    data: list[int] = field(default_factory=list)
    labels: dict[str, int] = field(default_factory=dict)
    source: list[str] = field(default_factory=list)

    def text_hex(self) -> str:
        """Instruction words, one 8 digit hex word per line."""
        return "".join(f"{w:08x}\n" for w in self.text)

    def data_hex(self) -> str:
        """Data words, one 8 digit hex word per line."""
        return "".join(f"{w & 0xFFFFFFFF:08x}\n" for w in self.data)


def reg(tok: str, line: str) -> int:
    """Register number for x0..x31 or an ABI name."""
    tok = tok.strip().lower()
    if re.fullmatch(r"x([0-9]|[12][0-9]|3[01])", tok):
        return int(tok[1:])
    if tok in ABI:
        return ABI[tok]
    raise AsmError(f"bad register '{tok}' in: {line}")


def num(tok: str, line: str) -> int:
    """Integer literal in decimal or hex."""
    try:
        return int(tok.strip(), 0)
    except ValueError as e:
        raise AsmError(f"bad number '{tok}' in: {line}") from e


def check_range(value: int, bits: int, line: str) -> int:
    """Reject immediates that do not fit a signed field of the given width."""
    lo, hi = -(1 << (bits - 1)), (1 << (bits - 1)) - 1
    if not lo <= value <= hi:
        raise AsmError(f"immediate {value} outside [{lo}, {hi}] in: {line}")
    return value


def enc_r(f7: int, rs2: int, rs1: int, f3: int, rd: int, op: int) -> int:
    return (f7 << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | op


def enc_i(imm: int, rs1: int, f3: int, rd: int, op: int) -> int:
    return ((imm & 0xFFF) << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | op


def enc_s(imm: int, rs2: int, rs1: int, f3: int) -> int:
    imm &= 0xFFF
    return ((imm >> 5) << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | ((imm & 0x1F) << 7) | OP_STORE


def enc_b(off: int, rs2: int, rs1: int, f3: int) -> int:
    off &= 0x1FFF
    return (
        (((off >> 12) & 1) << 31) | (((off >> 5) & 0x3F) << 25) | (rs2 << 20) | (rs1 << 15)
        | (f3 << 12) | (((off >> 1) & 0xF) << 8) | (((off >> 11) & 1) << 7) | OP_BRANCH
    )


def split_line(raw: str) -> tuple[list[str], str]:
    """Strip comments, pull off leading labels; return (labels, rest)."""
    line = raw.split("#", 1)[0].strip()
    labels = []
    while True:
        m = re.match(r"^([A-Za-z_.][\w.]*)\s*:\s*(.*)$", line)
        if not m:
            break
        labels.append(m.group(1))
        line = m.group(2).strip()
    return labels, line


def expand(mnemonic: str, args: list[str]) -> list[tuple[str, list[str]]]:
    """Turn pseudo-instructions into real ones."""
    if mnemonic == "nop":
        return [("addi", ["x0", "x0", "0"])]
    if mnemonic in ("li", "la"):
        return [("addi", [args[0], "x0", args[1]])]
    if mnemonic == "mv":
        return [("addi", [args[0], args[1], "0"])]
    if mnemonic == "j":
        return [("beq", ["x0", "x0", args[0]])]
    if mnemonic == "beqz":
        return [("beq", [args[0], "x0", args[1]])]
    if mnemonic == "bnez":
        return [("bne", [args[0], "x0", args[1]])]
    if mnemonic == "halt":
        return [("ecall", [])]
    return [(mnemonic, args)]


def parse(src: str) -> tuple[list[tuple[int, str, list[str], str]], list[int], dict[str, int]]:
    """First pass: collect instructions with addresses, data words and labels."""
    section = "text"
    insts: list[tuple[int, str, list[str], str]] = []
    data: list[int] = []
    labels: dict[str, int] = {}
    for raw in src.splitlines():
        names, line = split_line(raw)
        for name in names:
            if name in labels:
                raise AsmError(f"label '{name}' defined twice")
            labels[name] = 4 * len(insts) if section == "text" else 4 * len(data)
        if not line:
            continue
        mnemonic, _, rest = line.partition(" ")
        mnemonic = mnemonic.lower()
        args = [a.strip() for a in rest.split(",")] if rest.strip() else []
        if mnemonic in (".text", ".data"):
            section = mnemonic[1:]
        elif mnemonic == ".word":
            if section != "data":
                raise AsmError(f".word only allowed in .data: {raw.strip()}")
            data.extend(num(a, raw) & 0xFFFFFFFF for a in args)
        elif section == "data":
            raise AsmError(f"instruction in .data section: {raw.strip()}")
        else:
            for m, a in expand(mnemonic, args):
                insts.append((4 * len(insts), m, a, raw.strip()))
    return insts, data, labels


def encode(addr: int, m: str, a: list[str], line: str, labels: dict[str, int]) -> int:
    """Second pass: encode one real instruction."""

    def want(n: int) -> None:
        if len(a) != n:
            raise AsmError(f"'{m}' takes {n} operands: {line}")

    def imm_or_label(tok: str) -> int:
        return labels[tok] if tok in labels else num(tok, line)

    if m in R_TYPE:
        want(3)
        f7, f3 = R_TYPE[m]
        return enc_r(f7, reg(a[2], line), reg(a[1], line), f3, reg(a[0], line), OP_R)
    if m in I_TYPE:
        want(3)
        imm = check_range(imm_or_label(a[2]), 12, line)
        return enc_i(imm, reg(a[1], line), I_TYPE[m], reg(a[0], line), OP_I)
    if m == "slli":
        want(3)
        sh = num(a[2], line)
        if not 0 <= sh <= 31:
            raise AsmError(f"shift amount {sh} outside [0, 31]: {line}")
        return enc_i(sh, reg(a[1], line), 1, reg(a[0], line), OP_I)
    if m in ("lw", "sw"):
        want(2)
        mm = re.fullmatch(r"(.*)\((.+)\)", a[1].replace(" ", ""))
        if not mm:
            raise AsmError(f"expected offset(reg): {line}")
        off = check_range(imm_or_label(mm.group(1) or "0"), 12, line)
        base = reg(mm.group(2), line)
        if m == "lw":
            return enc_i(off, base, 2, reg(a[0], line), OP_LOAD)
        return enc_s(off, reg(a[0], line), base, 2)
    if m in B_TYPE:
        want(3)
        if a[2] not in labels:
            raise AsmError(f"unknown label '{a[2]}': {line}")
        off = check_range(labels[a[2]] - addr, 13, line)
        return enc_b(off, reg(a[1], line), reg(a[0], line), B_TYPE[m])
    if m == "ecall":
        want(0)
        return OP_SYSTEM
    raise AsmError(f"unsupported instruction '{m}' (supported: {', '.join(SUPPORTED)}): {line}")


def assemble(src: str) -> Program:
    """Assemble source text into a Program."""
    insts, data, labels = parse(src)
    text = [encode(addr, m, a, line, labels) for addr, m, a, line in insts]
    return Program(text=text, data=data, labels=labels, source=[line for *_, line in insts])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path)
    ap.add_argument("-o", "--out-dir", type=Path, default=Path("build"))
    args = ap.parse_args(argv)
    try:
        prog = assemble(args.source.read_text())
    except AsmError as e:
        print(f"{args.source}: {e}", file=sys.stderr)
        return 1
    args.out_dir.mkdir(parents=True, exist_ok=True)
    stem = args.source.stem
    (args.out_dir / f"{stem}.imem.hex").write_text(prog.text_hex())
    (args.out_dir / f"{stem}.dmem.hex").write_text(prog.data_hex())
    print(f"{stem}: {len(prog.text)} instructions, {len(prog.data)} data words")
    return 0


if __name__ == "__main__":
    sys.exit(main())
