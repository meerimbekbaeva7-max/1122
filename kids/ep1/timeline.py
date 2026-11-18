"""Turn script.json + lines.json into timeline.json (what happens when) and the dialogue track."""
import json, pathlib, numpy as np, soundfile as sf
ROOT = pathlib.Path(__file__).parent; SR = 48000
sc = json.load(open(ROOT / 'script.json')); lines = json.load(open(ROOT / 'lines.json'))
by_ev = {}
for l in lines: by_ev.setdefault(l['event'], []).append(l)
SONG_BEAT = 0.6; SONG_SLOT = 4 * SONG_BEAT          # 100 bpm, one sung line per bar
GAP = 0.35
t = 0.5; x = -9.0; segs = []; lulu_in = None
for i, ev in enumerate(sc['events']):
    ty = ev['type']
    if ty == 'walk':
        x0 = ev.get('from', x); segs.append({'type': 'walk', 't0': t, 't1': t + ev['dur'], 'x0': x0, 'x1': ev['to'], 'who': ev.get('who', 'both')})
        t += ev['dur']; x = ev['to']
    elif ty == 'arrive':
        segs.append({'type': 'arrive', 't0': t, 't1': t + ev['dur'], 'x': x}); lulu_in = t; t += ev['dur']
    elif ty in ('say', 'ask', 'answer'):
        l = by_ev[i][0]; seg = {'type': ty, 't0': t, 't1': t + l['dur'], 'who': ev['who'], 'text': ev['text'], 'file': l['file'], 'x': x, 'act': ev.get('act')}
        if ty == 'answer':
            seg.update(spike=ev['spike'], word=ev['word'], light=round(t + l['dur'] * 0.72, 3))
        segs.append(seg); t += l['dur'] + GAP
        if ty == 'ask':
            segs[-1]['target'] = ev['target']
            segs.append({'type': 'pause', 't0': t, 't1': t + ev['pause'], 'target': ev['target'], 'x': x}); t += ev['pause'] + 0.15
    elif ty == 'song':
        song = {'type': 'song', 't0': t, 'beat': SONG_BEAT, 'lines': []}
        for rep in range(ev['repeat']):
            for k, l in enumerate(by_ev[i]):
                song['lines'].append({'t0': t, 't1': t + SONG_SLOT, 'text': l['text'], 'file': l['file']}); t += SONG_SLOT
        song['t1'] = t; segs.append(song); t += 0.3
    elif ty == 'outro':
        segs.append({'type': 'outro', 't0': t, 't1': t + ev['dur'], 'x': x}); t += ev['dur']
DUR = round(t + 0.3, 3)
json.dump({'duration': DUR, 'lulu_in': lulu_in, 'segments': segs}, open(ROOT / 'timeline.json', 'w'), indent=1)
# dialogue track
vox = np.zeros(int(DUR * SR) + SR)
for s in segs:
    for item in ([s] if 'file' in s else s.get('lines', [])):
        y, _ = sf.read(ROOT / 'lines' / item['file']); i0 = int(item['t0'] * SR) + (int(0.25 * SR) if s['type'] == 'song' else 0)
        vox[i0:i0 + len(y)] += y
sf.write(ROOT / 'dialogue.wav', vox[:int(DUR * SR)].astype(np.float32), SR)
print('duration %.1f s, %d segments' % (DUR, len(segs)))
