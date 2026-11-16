#!/usr/bin/env python3
# ABOUTME: Cuts the voice takes into lines at the pauses and lays each line over its still frame from shots.tsv.
# ABOUTME: Run from anywhere: python3 docs/video/assemble.py; reads ~/phase1-video/takes and frames.
"""Assemble the Phase I video from voice-only takes and the shots.tsv frames.

Usage (from anywhere):
    python3 docs/video/assemble.py [--tts-missing]

Inputs:
    ~/phase1-video/takes/<name>.<any audio/video ext>   one take per speaker
    ~/phase1-video/frames/*.png                         from docs/video/make_frames.py
    docs/video/shots.tsv                                line order, frame, still or still,end
    ~/phase1-video/takes/cuts.tsv (optional)            manual id<TAB>start<TAB>end overrides

Each take is split into lines at pauses. If a take doesn't split into the expected
number of lines (a repeated line, a long mid-line pause), the script prints what it
found and writes takes/cuts.detected.tsv. Copy the rows you need into cuts.tsv, fix
the times, and run it again.

--tts-missing fills any missing take with a macOS `say` placeholder, for a rough cut.
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

HOME = Path.home() / "phase1-video"
TAKES, FRAMES, OUT = HOME / "takes", HOME / "frames", HOME / "phase1-video.mp4"
SHOTS = Path(__file__).with_name("shots.tsv")
ORDER = [
    ("navodit_opening", "01"),
    ("aryan", "02"),
    ("sarvesh", "03"),
    ("trishit", "04"),
    ("husain", "05"),
    ("navodit_closing", "06"),
]
FPS, SR = 30, 48000
LEAD, TAIL, END_HOLD = 0.15, 0.35, 2.0  # ~0.5 s between lines; 2 s hold on the ,end row
GAP, BLIP = 0.9, 0.35  # line break = silence >= GAP; drop sounds < BLIP


def run(*cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def duration(f):
    return float(
        run(
            "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)
        ).stdout
    )


def speech_segments(f):
    """Return [(start, end)] of speech, split at silences >= GAP, ignoring short blips."""
    err = subprocess.run(
        ["ffmpeg", "-i", str(f), "-af", "silencedetect=noise=-38dB:d=0.25", "-f", "null", "-"],
        check=False,
        capture_output=True,
        text=True,
    ).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    total = duration(f)
    edges = [0.0] + [v for pair in zip(starts, ends + [total]) for v in pair] + [total]
    segs = [(a, b) for a, b in zip(edges[::2], edges[1::2]) if b - a >= BLIP]
    merged = []
    for a, b in segs:
        if merged and a - merged[-1][1] < GAP:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    return merged


def tts_take(rows, dest):
    with tempfile.TemporaryDirectory() as tmp:
        parts = []
        for i, r in enumerate(rows):
            w = Path(tmp, f"{i}.wav")
            run("say", "-o", str(w), f"--data-format=LEI16@{SR}", r["line"])
            parts.append(w)
        lst = Path(tmp, "list.txt")
        sil = Path(tmp, "sil.wav")
        run("ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", "2", str(sil))
        lst.write_text("".join(f"file '{p}'\nfile '{sil}'\n" for p in parts))
        run("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), str(dest))


def main():
    tts = "--tts-missing" in sys.argv
    rows = [
        dict(zip(["id", "image", "motion", "line"], l.split("\t")))
        for l in SHOTS.read_text().splitlines()[1:]
        if l.strip()
    ]
    overrides = {}
    if (TAKES / "cuts.tsv").exists():
        for l in (TAKES / "cuts.tsv").read_text().splitlines():
            i, a, b = l.split("\t")[:3]
            overrides[i] = (float(a), float(b))
    TAKES.mkdir(parents=True, exist_ok=True)

    cuts, detected, bad = [], [], False
    for name, seg in ORDER:
        lines = [r for r in rows if r["id"].startswith(seg + "_")]
        found = sorted(p for p in TAKES.glob(name + ".*") if p.suffix != ".tsv")
        if not found:
            if not tts:
                sys.exit(f"missing take: {TAKES}/{name}.*  (or pass --tts-missing)")
            found = [TAKES / f"{name}.tts.wav"]
            tts_take(lines, found[0])
            print(f"{name}: using say placeholder")
        take = found[0]
        segs = speech_segments(take)
        for i, (a, b) in enumerate(segs):
            detected.append(
                f"{lines[i]['id'] if i < len(lines) else '??'}\t{a:.2f}\t{b:.2f}\t{name}"
            )
        if len(segs) != len(lines) and not all(r["id"] in overrides for r in lines):
            bad = True
            print(f"{name}: expected {len(lines)} lines, found {len(segs)} speech segments:")
            for a, b in segs:
                print(f"    {a:7.2f} - {b:7.2f}  ({b - a:.1f} s)")
            continue
        for r, s in zip(lines, segs):
            cuts.append((r, take, overrides.get(r["id"], s)))
    (TAKES / "cuts.detected.tsv").write_text("\n".join(detected) + "\n")
    if bad:
        sys.exit(f"\nFix with {TAKES}/cuts.tsv (see cuts.detected.tsv), then rerun.")

    with tempfile.TemporaryDirectory() as tmp:
        vlist, alist = [], []
        for k, (r, take, (a, b)) in enumerate(cuts):
            start = max(0.0, a - LEAD)
            dur = (b + TAIL) - start + (END_HOLD if r["motion"].endswith(",end") else 0)
            n = round(dur * FPS)
            dur = n / FPS
            v, au = Path(tmp, f"{k:02}.mp4"), Path(tmp, f"{k:02}.wav")
            run(
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-framerate",
                str(FPS),
                "-i",
                str(FRAMES / r["image"]),
                "-vf",
                "scale=1920:1080,setsar=1",
                "-frames:v",
                str(n),
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "18",
                "-pix_fmt",
                "yuv420p",
                "-r",
                str(FPS),
                str(v),
            )
            run(
                "ffmpeg",
                "-y",
                "-ss",
                f"{start:.3f}",
                "-i",
                str(take),
                "-vn",
                "-ac",
                "1",
                "-ar",
                str(SR),
                "-af",
                f"apad,atrim=0:{dur:.4f}",
                "-c:a",
                "pcm_s16le",
                str(au),
            )
            vlist.append(f"file '{v}'")
            alist.append(f"file '{au}'")
            print(f"{r['id']}  {r['image']:<22} {r['motion']:<24} {a:7.2f}-{b:7.2f}  {take.name}")
        Path(tmp, "v.txt").write_text("\n".join(vlist) + "\n")
        Path(tmp, "a.txt").write_text("\n".join(alist) + "\n")
        run(
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            f"{tmp}/v.txt",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            f"{tmp}/a.txt",
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-ar",
            str(SR),
            "-ac",
            "2",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            "-shortest",
            str(OUT),
        )

    total = duration(OUT)
    print(f"\nwrote {OUT}  {int(total // 60)}:{total % 60:04.1f}")
    if total > 300:
        print(
            "OVER 5:00: ask the longest speaker to record again a bit faster. Don't speed up audio."
        )
    if any(t.name.endswith(".tts.wav") for _, t, _ in cuts):
        print("contains say placeholders: rough cut only")


if __name__ == "__main__":
    main()
