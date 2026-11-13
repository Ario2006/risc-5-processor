# ABOUTME: Minimal reader for the VCD waveform files Icarus writes, enough to plot named signals.
# ABOUTME: Returns each signal as a list of (time, value) changes, values as ints or None for x/z.
from pathlib import Path


def read_vcd(path: Path, wanted: list[str]) -> dict[str, list[tuple[int, int | None]]]:
    """Read value changes for signals whose full dotted name is in wanted."""
    ids: dict[str, list[str]] = {}
    scope: list[str] = []
    changes: dict[str, list[tuple[int, int | None]]] = {name: [] for name in wanted}
    time = 0
    in_header = True
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line:
            continue
        if in_header:
            parts = line.split()
            if parts[0] == "$scope":
                scope.append(parts[2])
            elif parts[0] == "$upscope":
                scope.pop()
            elif parts[0] == "$var":
                name = ".".join([*scope, parts[4]])
                if name in changes:
                    ids.setdefault(parts[3], []).append(name)
            elif parts[0] == "$enddefinitions":
                in_header = False
            continue
        if line[0] == "#":
            time = int(line[1:])
        elif line[0] in "01xzXZ":
            for name in ids.get(line[1:], []):
                changes[name].append((time, int(line[0]) if line[0] in "01" else None))
        elif line[0] in "bB":
            bits, code = line[1:].split()
            value = None if any(c in "xzXZ" for c in bits) else int(bits, 2)
            for name in ids.get(code, []):
                changes[name].append((time, value))
    return changes


def value_at(changes: list[tuple[int, int | None]], t: int) -> int | None:
    """Value of a signal at time t, from its change list."""
    value = None
    for time, v in changes:
        if time > t:
            break
        value = v
    return value
