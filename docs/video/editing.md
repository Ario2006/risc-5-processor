<!-- ABOUTME: Build brief for Husain's Claude: turn 36 voice files into the final Phase I video, frame by frame. -->
<!-- ABOUTME: Uses make_frames.py and build_video.sh in this folder; both were run end to end on macOS. -->
# Building the Phase I video

**For Claude, running on Husain's laptop.** The video is a show and tell. Every frame
is built from real project sources and held for exactly as long as its voice beat lasts.
Nobody recorded their screen. You get 36 short voice files and build the video
with two tested tools in this folder. You cannot hear audio, so ask Husain whenever
a judgment needs ears.

## What you have

- [`shots.tsv`](shots.tsv): the shot list, one row per beat, in final order:
  `id`, `image` (a frame file), `motion`, and the `line` the speaker reads.
  - `still`: the frame holds.
  - `push`: a slow 6% zoom into the centre.
  - `crop:x:y:w:h`: starts on that region of the 1920x1080 frame, then zooms 4%.
  - `,end` on the last row adds a 2 second hold at the end.
- [`make_frames.py`](make_frames.py): builds every frame into a folder. It exports the 12
  slides from `slides/phase1-slides.pdf` and spotlights each card on slide 6. It renders
  the Verilog cards with the discussed line highlighted, runs `make test` and `make demo`
  for the real terminal output, and lays out the three annotated waveforms. It stops if
  a test or the demo fails.
- [`build_video.sh`](build_video.sh): for each row, it cleans the voice file (trims
  silence at both ends, high pass, light denoise, -16 LUFS), holds the frame for the
  voice length plus 0.6 s, and joins all the beats.

Needs: `ffmpeg`, `uv`, `python3`, `bash`, and on macOS the system fonts Arial and Menlo.
On Windows the scripts fall back to Arial and Consolas, but bash is needed for `build_video.sh` (Git Bash works).

## Steps

1. **Pull `main`** and work from the repo root.
2. **Collect audio.** Unzip every teammate's folder into one flat folder, `~/phase1-video/audio/`.
   Check that all 36 ids from `shots.tsv` are there:
   ```sh
   tail -n +2 docs/video/shots.tsv | cut -f1 | while read id; do ls ~/phase1-video/audio/$id.* >/dev/null 2>&1 || echo "missing $id"; done
   ```
   Tell Husain who is missing what. Do not build with gaps.
3. **Build the frames:**
   ```sh
   uv run --no-project --with pymupdf --with pygments --with pillow python docs/video/make_frames.py ~/phase1-video/frames
   ```
   Open and look at every frame the shot list uses. Text must be readable and nothing clipped.
4. **Build the video:**
   ```sh
   bash docs/video/build_video.sh ~/phase1-video/frames ~/phase1-video/audio ~/phase1-video/phase1-video.mp4
   ```
   It prints each beat's length. Each beat should be within a few seconds of the others
   in that speaker's set. A beat far longer than its line suggests the speaker paused or
   restarted inside the file, so ask Husain to listen to it.

## Verify before you say done

```sh
V=~/phase1-video/phase1-video.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 $V                   # under 300 s
ffmpeg -hide_banner -i $V -af ebur128 -f null - 2>&1 | grep -A1 "Integrated loudness"   # about -16 LUFS
```

Then extract one frame from the middle of every beat (`~/phase1-video/work/<id>.mp4`)
and check it is the frame `shots.tsv` names. Last, Husain watches the whole video once
with sound. You cannot judge voice quality, so ask him to name any beat to re-record.
For a re-record, replace that one audio file and run step 4 again.

## Rules

- Do not change the words in `shots.tsv` or the numbers in any frame. They match `results/`.
- Any text you add on screen has no dashes (`-`, `–`, `—`); use commas or "and".
- No music, no transitions other than the cuts and zooms the shot list defines.
- If it runs over 5:00, ask Husain which beats to re-record faster. Do not speed up audio.
- Do not commit video or audio files. Deliver `phase1-video.mp4` to Husain.
