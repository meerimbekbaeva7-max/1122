#!/bin/bash
# renders every segment (3 in parallel), muxes its audio
cd "$(dirname "$0")/.."
job(){ IFS='|' read id page audio <<< "$1"
  [ -f comp/$id.mp4 ] && { echo "skip $id"; return; }
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $audio)
  node render_seg.js "$page" comp/${id}_v.mp4 $dur 30 > comp/$id.log 2>&1 &&
  ffmpeg -y -loglevel error -i comp/${id}_v.mp4 -i $audio -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest comp/$id.mp4 && echo "done $id" || echo "FAIL $id"; }
export -f job
cat comp/segments.txt | xargs -P 3 -I{} bash -c 'job "{}"'
