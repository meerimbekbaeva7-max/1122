#!/bin/bash
# usage: make_audio.sh <song_id>  -> vocals, backing, mix, env, data.js in build_<id>
set -e
d=build_$1
BPM=$(cat $d/bpm) python3 sing.py $d/song_in.json $d > $d/sing.log 2>&1
python3 music.py $d $d/chords.json > /dev/null
python3 -c "
import json;d='$d';s=json.load(open(d+'/song.json'));e=json.load(open(d+'/env.json'));v=json.load(open(d+'/vis.json'))
open(d+'/data.js','w').write('window.SONG='+json.dumps(s)+';window.ENV='+json.dumps(e)+';window.VIS='+json.dumps(v)+';')"
echo "$1 audio ok $(python3 -c "import json;print(round(json.load(open('$d/song.json'))['duration'],1))")s"
