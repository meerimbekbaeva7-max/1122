#!/bin/bash
# intro (energetic) + episode (3 parts) + audio + subscribe reminder in the outro
cd "$(dirname "$0")"
OT=$(python3 -c "import json;print(next(s['t0'] for s in json.load(open('timeline.json'))['segments'] if s['type']=='outro'))")
printf "file 'p0.mp4'\nfile 'p1.mp4'\nfile 'p2.mp4'\n" > parts/list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i parts/list.txt -c copy parts/video.mp4
ffmpeg -y -loglevel error -i parts/video.mp4 -itsoffset $OT -i ../brand/subscribe_overlay.mov -i mix_norm.wav \
  -filter_complex "[0:v][1:v]overlay=1250:640:enable='between(t,$OT,$OT+4)':eof_action=pass[v]" -map "[v]" -map 2:a \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest parts/episode.mp4
ffmpeg -y -loglevel error -i ../rainbow_tots_intro_v2_energetic.mp4 -i parts/episode.mp4 \
  -filter_complex "[0:v]fps=30,format=yuv420p[v0];[0:a]aresample=48000,aformat=channel_layouts=stereo[a0];[1:v]fps=30,format=yuv420p[v1];[1:a]aresample=48000,aformat=channel_layouts=stereo[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart ../tiko_lulu_ep1_lost_colors.mp4
ffprobe -v error -show_entries format=duration,size -of default=nw=1 ../tiko_lulu_ep1_lost_colors.mp4
