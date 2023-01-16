#!/bin/bash
#

MUSIC_DIR="/home/nealla/Music/royaltyfree-cc/epic"
# Pick a random .mp3 from MUSIC_DIR
MUSIC_FILENAME="${MUSIC_DIR}/$(ls $MUSIC_DIR/*.mp3 | shuf -n 1)"

ffmpeg -f concat -i video_list.txt -i $MUSIC_FILENAME \
    -filter_complex "[0:a]volume=1.0[voiceover];[1:a]volume=0.15[music];[voiceover][music]amix=inputs=2" \
    -ac 1 \
    -movflags +faststart -shortest \
    output.mp4
