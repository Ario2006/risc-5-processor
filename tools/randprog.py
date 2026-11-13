# ABOUTME: Constrained-random program generator for verifying the pipeline against the ISS.
# ABOUTME: Uses few registers and short distances so hazards, loads and branches collide often.
import random

REGS = [f"x{i}" for i in range(1, 7)]
R_OPS = ["add", "sub", "and", "or", "xor", "slt", "sll"]
I_OPS = ["addi", "andi", "ori", "xori", "slti"]


def random_program(seed: int, length: int = 40) -> str:
    """Return assembly source for one random program that always reaches ecall."""
    rng = random.Random(seed)
    lines = [f"addi {r}, x0, {rng.randint(-50, 50)}" for r in REGS]
    body: list[str] = []
    branch_targets: dict[int, str] = {}
    for i in range(length):
        kind = rng.choices(["r", "i", "shift", "lw", "sw", "branch"], [5, 4, 1, 3, 2, 2])[0]
        rd, rs1, rs2 = rng.choice(REGS + ["x0"]), rng.choice(REGS + ["x0"]), rng.choice(REGS)
        if kind == "r":
            body.append(f"{rng.choice(R_OPS)} {rd}, {rs1}, {rs2}")
        elif kind == "i":
            body.append(f"{rng.choice(I_OPS)} {rd}, {rs1}, {rng.randint(-2048, 2047)}")
        elif kind == "shift":
            body.append(f"slli {rd}, {rs1}, {rng.randint(0, 31)}")
        elif kind == "lw":
            body.append(f"lw {rd}, {4 * rng.randint(0, 7)}(x0)")
        elif kind == "sw":
            body.append(f"sw {rs2}, {4 * rng.randint(0, 7)}(x0)")
        else:
            # Forward only, so every program terminates.
            target = min(i + 1 + rng.randint(1, 3), length)
            label = branch_targets.setdefault(target, f"L{target}")
            body.append(f"{rng.choice(['beq', 'bne'])} {rs1}, {rs2}, {label}")
    for i, inst in enumerate(body):
        prefix = f"{branch_targets[i]}: " if i in branch_targets else ""
        lines.append(prefix + inst)
    end_label = f"{branch_targets[length]}: " if length in branch_targets else ""
    lines.append(end_label + "ecall")
    data = ", ".join(str(rng.randint(-100, 100)) for _ in range(8))
    return "\n".join(lines) + f"\n.data\n.word {data}\n"
