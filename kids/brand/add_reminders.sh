#!/bin/bash
# overlays the subscribe/like reminder 5 times on the compilation
cd "$(dirname "$0")"
IN=../baby_color_10min_compilation.mp4; OUT=../baby_color_10min_final.mp4
T=(18 135 280 390 545); X=1260; Y=600
args=(-i $IN); for t in "${T[@]}"; do args+=(-itsoffset $t -i subscribe_overlay.mov); done; args+=(-i subscribe_sfx.wav)
fc="[0:v]null[v0];"; for i in 0 1 2 3 4; do t=${T[$i]}; fc+="[v$i][$((i+1)):v]overlay=$X:$Y:enable='between(t,$t,$((t+4)))':eof_action=pass[v$((i+1))];"; done
fc+="[6:a]asplit=5[s0][s1][s2][s3][s4];"; for i in 0 1 2 3 4; do d=$((T[$i]*1000)); fc+="[s$i]adelay=${d}|${d}[d$i];"; done
fc+="[0:a][d0][d1][d2][d3][d4]amix=inputs=6:normalize=0:duration=first[a]"
ffmpeg -y -loglevel error "${args[@]}" -filter_complex "$fc" -map "[v5]" -map "[a]" -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart $OUT
ffprobe -v error -show_entries format=duration,size -of default=nw=1 $OUT
