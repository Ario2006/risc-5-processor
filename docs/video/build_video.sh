#!/usr/bin/env bash
# ABOUTME: Builds the Phase I video from shots.tsv: one still or slow zoom per beat, timed to that beat's voice file.
# ABOUTME: Usage: bash docs/video/build_video.sh FRAMES_DIR AUDIO_DIR OUT.mp4 [SHOTS_TSV]
set -euo pipefail
FR=$1; AUD=$2; OUT=$3; SHOTS=${4:-docs/video/shots.tsv}
WORK=$(dirname "$OUT")/work
mkdir -p "$WORK"; rm -f "$WORK"/*.mp4 "$WORK"/*.wav
LEAD=0.25; LEAD_MS=250; TAIL=0.35

while IFS=$'\t' read -r id image motion line; do
  [[ $id == id || -z $id ]] && continue
  src=$(ls "$AUD/$id".* 2>/dev/null | head -1 || true)
  [[ -z $src ]] && { echo "missing audio for $id" >&2; exit 1; }
  # Trim silence at both ends, cut rumble, light denoise, then normalize loudness.
  ffmpeg -nostdin -loglevel error -y -i "$src" -af \
    "highpass=f=80,afftdn=nf=-25,silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-16:TP=-1.5:LRA=11" \
    -ar 48000 -ac 2 "$WORK/$id.wav"
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$WORK/$id.wav")
  tail=$TAIL; [[ $motion == *end* ]] && tail=2.0
  T=$(python3 -c "print(round($d+$LEAD+$tail,2))"); F=$(python3 -c "print(int(round($T*30)))")
  case $motion in
    push*)  VF="scale=3840:2160,zoompan=z='1+0.06*on/${F}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=${F}:s=1920x1080:fps=30";;
    crop:*) IFS=: read -r _ cx cy cw ch _rest <<< "$motion"
            VF="crop=${cw}:${ch}:${cx}:${cy},scale=3840:2160,zoompan=z='1+0.04*on/${F}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=${F}:s=1920x1080:fps=30";;
    *)      VF="scale=1920:1080,fps=30";;
  esac
  ffmpeg -nostdin -loglevel error -y -loop 1 -framerate 30 -i "$FR/$image" -i "$WORK/$id.wav" \
    -filter_complex "[0:v]${VF},format=yuv420p,setsar=1,trim=duration=${T}[v];[1:a]adelay=${LEAD_MS}:all=1,apad,atrim=duration=${T}[a]" \
    -map "[v]" -map "[a]" -c:v libx264 -crf 18 -preset medium -c:a aac -b:a 192k "$WORK/$id.mp4"
  printf '%s\t%5.2fs\t%s\n' "$id" "$T" "$image"
done < "$SHOTS"

WORK_ABS=$(cd "$WORK" && pwd)
for f in "$WORK_ABS"/*.mp4; do echo "file '$f'"; done > "$WORK/list.txt"
ffmpeg -nostdin -loglevel error -y -f concat -safe 0 -i "$WORK/list.txt" -c copy -movflags +faststart "$OUT"
echo "built $OUT: $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT") s"
