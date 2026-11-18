#!/bin/bash
cd "$(dirname "$0")"
C=($(python3 -c "import json;print(' '.join(str(x) for x in json.load(open('parts/cuts.json'))))"))
for i in 0 1 2; do node render_range.js ep1.html parts/p$i.mp4 ${C[$i]} ${C[$((i+1))]} > parts/p$i.log 2>&1 & done; wait
grep -h done parts/p*.log
