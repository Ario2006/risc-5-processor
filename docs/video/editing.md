<!-- ABOUTME: Aryan's editing brief: cut five face takes together with the right frame behind each line. -->
<!-- ABOUTME: Frames come from make_frames.py; the order and backgrounds come from shots.tsv. -->
# Editing the Phase I video

**For Aryan, or the Claude helping with the edit.** Each teammate sends their segment as one face take
(Navodit sends two, opening and closing), lines in order and a pause of about 2 seconds between lines. You cut the takes
into one video and put the matching frame in the background behind each line.

## What you have

- [`shots.tsv`](shots.tsv): one row per line, in final order: `id`, `image` (the
  background frame), `motion`, and the `line` the speaker says.
  - `still`: the frame holds.
  - `push`: a slow 6% zoom into the centre.
  - `crop:x:y:w:h`: start on that region of the 1920x1080 frame, then zoom in 4%.
  - `,end` on the last row: hold 2 seconds after the last word.
- [`make_frames.py`](make_frames.py): builds every background frame at 1920x1080. It exports
  the 12 slides from `slides/phase1-slides.pdf`, spotlights each card on slide 6,
  renders the Verilog cards with the discussed line highlighted, runs `make test` and
  `make demo` for the real terminal output, and lays out the three annotated waveforms.
  It stops if a test or the demo fails. From the repo root:
  ```sh
  uv run --no-project --with pymupdf --with pygments --with pillow python docs/video/make_frames.py ~/phase1-video/frames
  ```
- The six takes, in `Phase1 Video` on the shared Drive: `navodit_opening`, `aryan`, `sarvesh`,
  `trishit`, `husain`, `navodit_closing`. The `id` in `shots.tsv` is only a row number for you;
  the speakers never see it.

## Steps

1. Download every take and build the frames.
2. In each take, find where each line starts and ends. The 2 second pauses mark the
   boundaries. Where a speaker repeated a line, use the last clean attempt.
3. Put the takes in order: Navodit opening, Aryan, Sarvesh, Trishit, Husain, Navodit closing.
4. For each line, place its `image` behind the speaker for exactly that line, with its `motion`.
   The background changes on the first word of the next line.
5. Shorten the pauses between lines to about half a second.
6. Match loudness across speakers, about -16 LUFS for the whole video.

## Check before you share it

- Under 5:00.
- Watch it once with sound: every background matches what is being said, and no
  speaker's face covers the text on a slide or the highlighted line of code.

## Rules

- Do not change any words or numbers. They match `results/`.
- Any text you add on screen has no dashes (`-`, `–`, `—`); use commas or "and".
- No music, and no transitions other than cuts and the zooms in `shots.tsv`.
- If it runs over 5:00, ask the speaker to record again faster. Do not speed up audio.
- Do not commit video or audio files.
