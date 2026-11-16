<!-- ABOUTME: Husain's editing brief: turn the voice takes into the video with make_frames.py and assemble.py. -->
<!-- ABOUTME: The order and frames come from shots.tsv; every shot is a still, with no zoom. -->
# Editing the Phase I video

**For Husain, or the Claude helping with the edit.** Each teammate sends their segment as one
voice take (Navodit sends two, opening and closing), with the lines in order and a pause of about
2 seconds between lines. [`assemble.py`](assemble.py) cuts each take into lines at the pauses and
puts the matching frame full screen under each line.

## What you have

- [`shots.tsv`](shots.tsv): one row per line, in final order: `id`, `image` (the frame),
  `motion`, and the `line` the speaker says. Every row is `still`. The last row is
  `still,end`, which holds the frame for 2 seconds after the last word.
- [`make_frames.py`](make_frames.py): builds every frame at 1920x1080. It exports the 12 slides
  from `slides/phase1-slides.pdf`, spotlights each card on slide 6, renders the Verilog cards
  with the discussed line highlighted, runs `make test` and `make demo` for the real terminal
  output, and lays out the three annotated waveforms. It stops if a test or the demo fails.
- [`assemble.py`](assemble.py): needs `ffmpeg`. It reads the takes from `~/phase1-video/takes`
  and the frames from `~/phase1-video/frames`, and writes `~/phase1-video/phase1-video.mp4`.

## Steps

1. Build the frames, from the repo root:
   ```sh
   uv run --no-project --with pymupdf --with pygments --with pillow python docs/video/make_frames.py ~/phase1-video/frames
   ```
2. Download every take from `Phase1 Video` on the shared Drive into `~/phase1-video/takes`, named
   `navodit_opening`, `aryan`, `sarvesh`, `trishit`, `husain` and `navodit_closing`. Any audio or
   video format works; only the audio is used.
3. Run `python3 docs/video/assemble.py`. Add `--tts-missing` to fill missing takes with a macOS
   `say` voice for a rough cut.
4. If a take has a repeated line or a false start, the script prints the speech segments it found
   and writes `takes/cuts.detected.tsv`. Put the clean attempt of each line in `takes/cuts.tsv`
   as `id`, `start`, `end` in seconds, tab separated, and run it again.

The script shortens the pauses between lines to about half a second and normalizes the whole
video to -16 LUFS.

## Check before you share it

- Under 5:00. The script prints the length.
- Watch it once with sound: every frame matches what is being said, and no false start or
  "retake" is left in.

## Rules

- Do not change any words or numbers. They match `results/`.
- Any text you add on screen has no dashes (`-`, `–`, `—`); use commas or "and".
- No music, no zooms, and no transitions other than cuts.
- If it runs over 5:00, ask the speaker to record again faster. Do not speed up audio.
- Do not commit video or audio files.
