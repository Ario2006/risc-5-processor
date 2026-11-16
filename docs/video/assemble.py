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
found and writes takes/cuts.detected.tsv. Put all of that speaker's lines in cuts.tsv
with the right times, and run it again. A take that splits into the right count can
override single lines. A line whose length doesn't fit its word count gets a warning.

--noise=-45 sets the silence threshold in dB (default: 30 dB below the take's peak).
--tts-missing fills any missing take with a macOS `say` placeholder in ~/phase1-video/tts,
for a rough cut.
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HOME = Path.home() / "phase1-video"
TAKES, FRAMES, TTS, OUT = HOME / "takes", HOME / "frames", HOME / "tts", HOME / "phase1-video.mp4"
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
BELOW_PEAK, GAP, BLIP, NEAR = 30, 1.2, 0.35, 0.6  # silence = BELOW_PEAK dB under the peak;
# a line break is a silence >= GAP s; a sound < BLIP s is dropped unless speech is within NEAR s
WORDS_PER_S = (
    2.5  # rough rate, counting digits as words; the 0.6x to 1.6x tolerance covers the rest
)


def run(*cmd):
    try:
        return subprocess.run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        sys.exit(f"{cmd[0]} not found")
    except subprocess.CalledProcessError as e:
        sys.exit(f"{cmd[0]} failed:\n{e.stderr[-2000:]}")


def duration(f):
    return float(
        run(
            "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)
        ).stdout
    )


def speech_segments(f, noise=None):
    """Return [(start, end)] of speech, split at silences >= GAP, ignoring isolated blips."""
    if noise is None:
        vol = run("ffmpeg", "-i", str(f), "-vn", "-af", "volumedetect", "-f", "null", "-").stderr
        noise = float(re.search(r"max_volume: ([-\d.]+) dB", vol).group(1)) - BELOW_PEAK
    err = run(
        "ffmpeg",
        "-i",
        str(f),
        "-vn",
        "-af",
        f"silencedetect=noise={noise}dB:d=0.25",
        "-f",
        "null",
        "-",
    ).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    total = duration(f)
    edges = [0.0] + [v for pair in zip(starts, ends + [total]) for v in pair] + [total]
    raw = [(a, b) for a, b in zip(edges[::2], edges[1::2]) if b - a > 0.02]

    def near(i):  # a short word like "So," just before or after other speech
        return (i > 0 and raw[i][0] - raw[i - 1][1] < NEAR) or (
            i + 1 < len(raw) and raw[i + 1][0] - raw[i][1] < NEAR
        )

    segs = [s for i, s in enumerate(raw) if s[1] - s[0] >= BLIP or near(i)]
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
    noise = next((float(a.split("=", 1)[1]) for a in sys.argv if a.startswith("--noise=")), None)
    rows = [
        dict(zip(["id", "image", "motion", "line"], l.split("\t")))
        for l in SHOTS.read_text().splitlines()[1:]
        if l.strip()
    ]
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        sys.exit("needs ffmpeg and ffprobe on PATH")
    missing = sorted({r["image"] for r in rows if not (FRAMES / r["image"]).exists()})
    if missing:
        sys.exit(f"missing frames in {FRAMES}: {', '.join(missing)}. Run make_frames.py first.")
    TAKES.mkdir(parents=True, exist_ok=True)
    overrides = {}
    if (TAKES / "cuts.tsv").exists():
        for l in (TAKES / "cuts.tsv").read_text().splitlines():
            f = l.split()
            if len(f) < 3 or f[0] == "id" or f[0].startswith("#"):
                continue
            try:
                a, b = float(f[1]), float(f[2])
            except ValueError:
                sys.exit(f"cuts.tsv: bad line {l!r}; expected: id start end, in seconds")
            if b <= a:
                sys.exit(f"cuts.tsv: end is not after start in {l!r}")
            overrides[f[0]] = (a, b)
    unknown = sorted(set(overrides) - {r["id"] for r in rows})
    if unknown:
        sys.exit(f"cuts.tsv: no such line id in shots.tsv: {', '.join(unknown)}")

    cuts, detected, bad = [], [], False
    for name, seg in ORDER:
        lines = [r for r in rows if r["id"].startswith(seg + "_")]
        found = [p for p in TAKES.iterdir() if p.stem.lower() == name and p.suffix != ".tsv"]
        if len(found) > 1:
            sys.exit(f"more than one take for {name}: {', '.join(p.name for p in found)}")
        if found:
            take = found[0]
        elif tts:
            TTS.mkdir(parents=True, exist_ok=True)
            take = TTS / f"{name}.wav"
            tts_take(lines, take)
            print(f"{name}: using say placeholder")
        else:
            sys.exit(f"missing take: {TAKES}/{name}.*  (or pass --tts-missing)")
        has_audio = run(
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=index",
            "-of",
            "csv=p=0",
            str(take),
        ).stdout.strip()
        if not has_audio:
            sys.exit(f"no audio in {take}; was the mic picked?")
        segs = speech_segments(take, noise)
        for i, (a, b) in enumerate(segs):
            detected.append(
                f"{lines[i]['id'] if i < len(lines) else '??'}\t{a:.2f}\t{b:.2f}\t{name}"
            )
        todo = [r["id"] for r in lines if r["id"] not in overrides]
        if len(segs) != len(lines) and todo:
            bad = True
            print(f"{name}: expected {len(lines)} lines, found {len(segs)} speech segments.")
            print(f"    Put {', '.join(todo)} in cuts.tsv. Segments found:")
            for a, b in segs:
                print(f"    {a:7.2f} - {b:7.2f}  ({b - a:.1f} s)")
            continue
        for i, r in enumerate(lines):
            a, b = overrides.get(r["id"]) or segs[i]
            expect = len(re.findall(r"[A-Za-z']+|\d", r["line"])) / WORDS_PER_S
            if not 0.6 * expect <= b - a <= 1.6 * expect:
                print(f"check {r['id']}: {b - a:.1f} s of speech, expected about {expect:.1f} s")
            cuts.append((r, take, (a, b)))
    (TAKES / "cuts.detected.tsv").write_text("\n".join(detected) + "\n")
    if bad:
        sys.exit(f"\nFix with {TAKES}/cuts.tsv (see cuts.detected.tsv), then rerun.")

    with tempfile.TemporaryDirectory() as tmp:
        vlist, alist = [], []
        for k, (r, take, (a, b)) in enumerate(cuts):
            start = max(0.0, a - LEAD)
            speech = (b + TAIL) - start
            dur = speech + (END_HOLD if r["motion"].endswith(",end") else 0)
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
                f"atrim=0:{speech:.4f},apad,atrim=0:{dur:.4f}",
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
    t = round(total)
    print(f"\nwrote {OUT}  {t // 60}:{t % 60:02d}")
    if total > 300:
        print(
            "OVER 5:00: ask the longest speaker to record again a bit faster. Don't speed up audio."
        )
    if any(take.parent == TTS for _, take, _ in cuts):
        print("contains say placeholders: rough cut only")


if __name__ == "__main__":
    main()
