<!-- ABOUTME: How the team records the Phase I video: voice only, one short audio file per beat. -->
<!-- ABOUTME: Each person reads this page plus their own script; Husain's Claude reads editing.md. -->
# Recording the Phase I video

The video is a **show and tell**: nobody records their screen. Each of us records
**only our voice**, one short audio file per beat (a beat is one or two sentences).
Husain builds every frame from the real sources (slides, Verilog, terminal output,
waveforms) and times each frame to its beat's audio. Final length is about 4:40.

## Who records what

| Beats | Who | What the viewer sees |
|---|---|---|
| `01_01` to `01_06` | Navodit | Slides 1 to 3 |
| `02_01` to `02_02` | Aryan | Slide 4 |
| `03_01` to `03_10` | Sarvesh | Slide 5 with a zoom, slide 6 one card at a time, then the Verilog with each line highlighted |
| `04_01` to `04_10` | Trishit | Terminal output, three waveforms, slides 7 and 8 |
| `05_01` to `05_06` | Husain | Slides 9 to 11 |
| `06_01` to `06_02` | Navodit | Slide 12 |

Your lines: [Navodit](navodit.md), [Aryan](aryan.md), [Sarvesh](sarvesh.md),
[Trishit](trishit.md), [Husain](husain.md). Every line is also in [`shots.tsv`](shots.tsv),
which is what the build reads.

## How to record

1. **App:** your phone's voice recorder (iPhone Voice Memos, Android Recorder) is enough.
2. **Room:** quiet, soft furnishings help, fan off. Hold the phone about a hand's width from your mouth, a little to the side.
3. **One file per beat.** Read the beat, stop, listen back. Not clean? Delete and record it again.
   Short files make retakes cheap, so aim for clean, not perfect.
4. **Name each file by its beat id**, for example `03_07.m4a`. Keep the app's extension.
5. **Read the line as written.** The numbers are checked against `results/`. Do not round them or add new ones.
6. **Tone:** like explaining to a friend in the lab. Steady pace, small smile, end each beat with a falling tone, as if it is the end of a sentence.
7. Silence at the start or end of a file is fine. The build trims it.

## Sending

Put all your files in one folder named after you, zip it, and send it to Husain as a
**file** (WhatsApp: attach as Document; Google Drive works too). Say "sent" in the group.
