# ABOUTME: Builds every still frame the Phase I video uses: slide PNGs, spotlights, code, terminal and figure cards.
# ABOUTME: Run from the repo root: uv run --no-project --with pymupdf --with pygments --with pillow python docs/video/make_frames.py OUT
import subprocess
import sys
import textwrap
from io import BytesIO
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont
from pygments import highlight
from pygments.formatters import ImageFormatter
from pygments.formatters.img import FontNotFound
from pygments.lexers import VerilogLexer

W, H = 1920, 1080
BG = (247, 246, 242)
INK = (22, 34, 64)
RUST = (176, 74, 20)
MUTED = (95, 104, 120)
TERM_BG = (28, 32, 40)
TERM_FG = (226, 230, 236)
TERM_OK = (120, 200, 140)
SANS = ["/System/Library/Fonts/Supplemental/Arial.ttf", "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
MONO = ["/System/Library/Fonts/Menlo.ttc", "C:/Windows/Fonts/consola.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
MONO_NAMES = ["Menlo", "Consolas", "DejaVu Sans Mono"]


def font(paths, size):
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)


def slides(pdf, out):
    doc = fitz.open(pdf)
    for i, page in enumerate(doc, start=1):
        z = W / page.rect.width
        page.get_pixmap(matrix=fitz.Matrix(z, z)).save(out / f"slide_{i:02d}.png")


def spotlight(src, rect, dst):
    im = Image.open(src).convert("RGBA")
    veiled = Image.alpha_composite(im, Image.new("RGBA", im.size, BG + (200,)))
    mask = Image.new("L", im.size, 255)
    ImageDraw.Draw(mask).rectangle(rect, fill=0)
    im.paste(veiled, (0, 0), mask)
    im.convert("RGB").save(dst)


def frame(eyebrow, title, presenter, title_mono=False):
    canvas = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(canvas)
    d.text((128, 110), eyebrow, font=font(SANS, 30), fill=RUST)
    d.text((128, 160), title, font=font(MONO if title_mono else SANS, 46), fill=INK)
    d.text((128, 990), f"Presenter: {presenter}", font=font(SANS, 28), fill=MUTED)
    return canvas


def paste_fit(canvas, img, box):
    x, y, w, h = box
    s = min(w / img.width, h / img.height, 1.0)
    img = img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)
    canvas.paste(img, (x, y))


def code_card(repo, path, first, last, hl, presenter, dst):
    lines = (repo / path).read_text().splitlines()[first - 1:last]
    for name in MONO_NAMES:
        try:
            fmt = ImageFormatter(font_name=name, font_size=34, line_numbers=True, line_number_start=first,
                                 line_number_bg="#F7F6F2", line_number_fg="#9AA0AA", line_pad=14,
                                 style="friendly", hl_lines=[h - first + 1 for h in hl],
                                 hl_color="#FBE3C8", image_pad=24)
            code = Image.open(BytesIO(highlight("\n".join(lines), VerilogLexer(), fmt))).convert("RGB")
            break
        except FontNotFound:
            continue
    else:
        sys.exit(f"No monospace font found for the code cards; tried {MONO_NAMES}")
    canvas = frame("THE VERILOG", path, presenter, title_mono=True)
    paste_fit(canvas, code, (128, 250, 1664, 700))
    canvas.save(dst)


def terminal_card(command, output, presenter, dst):
    canvas = frame("THE DEMO", "Run in the repository root", presenter)
    d = ImageDraw.Draw(canvas)
    mono = font(MONO, 48)
    wrapped = [c for l in output for c in (textwrap.wrap(l, 52) or [""])]
    rows = len(wrapped)
    top = 380
    d.rounded_rectangle((128, top, 1792, top + 200 + 70 * rows), radius=18, fill=TERM_BG)
    d.text((176, top + 56), f"$ {command}", font=mono, fill=TERM_FG)
    y = top + 140
    ok = any("passed" in l or l.startswith("PASS") for l in output)
    for chunk in wrapped:
        d.text((176, y), chunk, font=mono, fill=TERM_OK if ok else TERM_FG)
        y += 70
    canvas.save(dst)


def figure_card(src, eyebrow, title, presenter, dst):
    canvas = frame(eyebrow, title, presenter)
    paste_fit(canvas, Image.open(src).convert("RGB"), (128, 260, 1664, 700))
    canvas.save(dst)


def run(cmd, repo):
    done = subprocess.run(cmd, check=False, cwd=repo, capture_output=True, text=True)
    lines = [l for l in (done.stdout + done.stderr).splitlines() if l.strip()]
    return lines


def main():
    repo = Path.cwd()
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    slides(repo / "slides/phase1-slides.pdf", out)

    s6 = out / "slide_06.png"
    spotlight(s6, (128, 280, 664, 778), out / "s06_structural.png")
    spotlight(s6, (692, 280, 1228, 778), out / "s06_data.png")
    spotlight(s6, (1256, 280, 1792, 778), out / "s06_control.png")

    hz, fw = "rtl/pipeline/hazard_unit.v", "rtl/pipeline/forwarding_unit.v"
    code_card(repo, hz, 35, 45, [], "Sarvesh Srinath", out / "code_hazard.png")
    for line in (39, 43, 44):
        code_card(repo, hz, 35, 45, [line], "Sarvesh Srinath", out / f"code_hazard_{line}.png")
    code_card(repo, fw, 22, 29, [25, 26, 27, 28], "Sarvesh Srinath", out / "code_fwd_25_28.png")

    test_out = [l for l in run(["make", "test"], repo) if "passed" in l or "failed" in l]
    demo_out = [l for l in run(["make", "demo"], repo) if l.startswith(("PASS", "FAIL"))]
    if not test_out or "failed" in test_out[-1] or not demo_out or not demo_out[-1].startswith("PASS"):
        sys.exit(f"make test or make demo did not pass: {test_out} {demo_out}")
    terminal_card("make test", test_out[-1:], "Trishit Swarnakar", out / "term_test.png")
    terminal_card("make demo", demo_out[-1:], "Trishit Swarnakar", out / "term_demo.png")

    wf = [("forward", "Forwarding: fwd_a and fwd_b switch to 2 at EX PC 0x04"),
          ("load_use", "Load use: stall is high for one cycle"),
          ("branch_flush", "Taken branch: flush, then two bubbles")]
    for name, title in wf:
        figure_card(repo / f"figures/waveform_{name}_annotated.png", "THE WAVEFORM", title,
                    "Trishit Swarnakar", out / f"wave_{name}.png")
    print(f"frames written to {out}")


if __name__ == "__main__":
    main()
