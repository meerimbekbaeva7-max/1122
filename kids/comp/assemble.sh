#!/bin/bash
# joins the rendered segments into the final ~10 min compilation
cd "$(dirname "$0")"
ORDER="colors numbers shapes fruits animals car abc vehicles colors planets"
args=(); n=0; for s in $ORDER; do args+=(-i $s.mp4); n=$((n+1)); done
fc=""; for i in $(seq 0 $((n-1))); do fc+="[$i:v][$i:a]"; done
ffmpeg -y -loglevel error "${args[@]}" -filter_complex "${fc}concat=n=$n:v=1:a=1[v][a];[a]loudnorm=I=-14:TP=-1.5:LRA=9[an]" \
  -map "[v]" -map "[an]" -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 48000 -movflags +faststart ../baby_color_10min_compilation.mp4
ffprobe -v error -show_entries format=duration,size -of default=nw=1 ../baby_color_10min_compilation.mp4
