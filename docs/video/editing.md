<!-- ABOUTME: Editing brief for Husain's Claude: turn the six recorded clips into the final Phase I video with ffmpeg. -->
<!-- ABOUTME: Written as agent instructions; every ffmpeg command here was tested on macOS with Homebrew ffmpeg. -->
# Editing the Phase I video

**For Claude, running on Husain's laptop.** Husain gives you six clips recorded
by five people. Turn them into one video under 5:00. Work only with `ffmpeg` and
`ffprobe`. Ask Husain when a judgment needs ears (a cough, a bad take), because you cannot hear audio.

## Inputs

- Clips in `~/phase1-video/raw/`, outside the repo. Never commit video files to git.
- Expected files, in final order (extension may be `.mov` or `.mp4`):

| # | File | Speaker | Target | Script |
|---|---|---|---|---|
| 1 | `01_navodit_intro` | Navodit | 0:50 | `docs/video/navodit.md`, clip 1 |
| 2 | `02_aryan_single_cycle` | Aryan | 0:15 | `docs/video/aryan.md` |
| 3 | `03_sarvesh_pipeline` | Sarvesh | 0:55 | `docs/video/sarvesh.md` |
| 4 | `04_trishit_demo` | Trishit | 1:20 | `docs/video/trishit.md` |
| 5 | `05_husain_results` | Husain | 0:50 | `docs/video/husain.md` |
| 6 | `06_navodit_conclusion` | Navodit | 0:25 | `docs/video/navodit.md`, clip 2 |

Each script file holds the exact words, and recording rules are in `docs/video/README.md`.
Speakers leave 2 seconds of silence at both ends. After a mistake they stay silent
about 3 seconds and repeat the whole sentence, so **the last take of a sentence is the good one**.

## Step 1: check every clip

```sh
cd ~/phase1-video
mkdir -p work frames
for f in raw/*; do
  echo "== $f"
  ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,r_frame_rate,sample_rate -of compact "$f"
done
```

Stop and tell Husain if a clip is missing, has no audio stream, or is more than 20 seconds
off its target. For each clip, grab a frame near the start and near the end and **look at them**:

```sh
ffmpeg -loglevel error -y -ss 3 -i raw/01_navodit_intro.mov -frames:v 1 frames/01_start.png
ffmpeg -loglevel error -y -sseof -3 -i raw/01_navodit_intro.mov -frames:v 1 frames/01_end.png
```

Check: the right slide (slide numbers sit bottom right, "01 / 12"), text readable,
no notifications, no private windows or chats on screen. Report anything wrong to Husain.

## Step 2: find the cuts

Find pauses. Gaps of 2.5 seconds or more mark the start and end of a clip, or a retake:

```sh
ffmpeg -hide_banner -i raw/01_navodit_intro.mov -af silencedetect=n=-35dB:d=2.5 -f null - 2>&1 | grep silence_
```

To see where each sentence starts, transcribe with word timestamps if whisper is available
(this step was not tested; it needs `brew install whisper-cpp` and a model download):

```sh
ffmpeg -loglevel error -y -i raw/01_navodit_intro.mov -ar 16000 -ac 1 work/01.wav
whisper-cli -m <path to ggml-base.en.bin> -f work/01.wav -ojf -of work/01   # writes work/01.json
```

Compare the transcript to the script file. When a sentence appears twice, cut from the
start of the first try to the start of the last try. If whisper is not available,
show Husain the silence list and ask him to name the bad takes by time.

Write the result to `cuts.csv`, one row per piece to keep, in final order. Keep about
0.3 s of room before the first word and 0.5 s after the last word of each piece:

```csv
file,start,end
raw/01_navodit_intro.mov,1.7,52.4
raw/02_aryan_single_cycle.mp4,1.9,17.2
raw/03_sarvesh_pipeline.mov,1.8,24.0
raw/03_sarvesh_pipeline.mov,29.6,60.1
```

Exception: in clip 4, Trishit may wait in silence while Surfer opens. Cut the wait
but keep the moment the window appears.

Show Husain `cuts.csv` and the total kept length before you render.

## Step 3: render each piece

Every piece goes to the same format: 1920x1080, 30 fps, H.264, AAC 48 kHz stereo,
loudness normalized to -16 LUFS, with a 0.15 s audio fade at both ends so cuts do not click.
Screens that are not 16:9 get letterboxed, never stretched.

```sh
render() { # input output start end
  ffmpeg -nostdin -loglevel error -y -ss "$3" -to "$4" -i "$1" \
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,fps=30,format=yuv420p,setsar=1" \
    -af "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,afade=t=in:d=0.15,areverse,afade=t=in:d=0.15,areverse" -ac 2 \
    -c:v libx264 -preset medium -crf 18 -c:a aac -b:a 192k "$2"
}
i=0
tail -n +2 cuts.csv | while IFS=, read -r f s e; do
  i=$((i+1)); render "$f" "$(printf 'work/piece_%02d.mp4' $i)" "$s" "$e"
done
```

## Step 4: join

All pieces share one format, so they join without re-encoding:

```sh
for p in work/piece_*.mp4; do echo "file '$PWD/$p'"; done > work/list.txt
ffmpeg -loglevel error -y -f concat -safe 0 -i work/list.txt -c copy -movflags +faststart phase1-video.mp4
```

## Step 5: verify before you say done

Run all of these and show Husain the output:

```sh
ffprobe -v error -show_entries format=duration -of compact phase1-video.mp4     # must be under 300 s
ffmpeg -hide_banner -i phase1-video.mp4 -af ebur128 -f null - 2>&1 | grep -A1 "Integrated loudness"   # about -16 LUFS
ffmpeg -hide_banner -i phase1-video.mp4 -vf blackdetect=d=0.5 -an -f null - 2>&1 | grep black_start      # should print nothing
```

Then extract one frame 1 s after each join and look at every one: the slide or screen
must match the speaker in the table. Last, ask Husain to watch the whole video once with
sound, at normal speed, because you cannot check lip timing, mouse pointing or audio quality.

## If it runs over 5:00

In this order: trim long pauses between sentences (keep at least 0.3 s), then shorten
the Surfer wait in clip 4. Do not speed up audio above 1.05x
(`-af atempo=1.05` with `-vf setpts=PTS/1.05`), and never cut scripted sentences without Husain's OK.

## Rules

- No music, no transitions other than hard cuts, no intro or outro cards. The slides already
  name each presenter.
- Any text you add on screen must have no dashes (`-`, `–`, `—`); use commas or "and".
- If one clip is bad (wrong slide, unreadable, noisy), do not patch it. Tell Husain which clip,
  what is wrong, and ask him to request a reshoot from that person.
- Deliver `phase1-video.mp4` to Husain. It is not committed to the repo.
