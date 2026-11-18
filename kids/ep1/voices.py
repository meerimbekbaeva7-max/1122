"""Speak every line of script.json with the character's voice -> lines/NN_M.wav.
Each line is re-synthesised (different prosody noise) until Whisper understands it."""
import json, io, wave, subprocess, pathlib, numpy as np, soundfile as sf
from scipy.signal import resample_poly
from piper import PiperVoice
from piper.config import SynthesisConfig
from faster_whisper import WhisperModel
ROOT = pathlib.Path(__file__).parent; OUT = ROOT / 'lines'; OUT.mkdir(exist_ok=True)
M = ROOT.parent.parent / 'voice/models'
VOICES = {'tiko': ('en_US-amy-medium', 1.22, 0.95), 'lulu': ('en_US-hfc_female-medium', 1.10, 1.0)}
pv = {k: PiperVoice.load(str(M / f'{m}.onnx')) for k, (m, _, _) in VOICES.items()}
wm = WhisperModel('small', device='cpu', compute_type='int8')
import re
ALIAS = {'tico': 'tiko', 'teeko': 'tiko', 'rar': 'rawr', 'rour': 'rawr', 'raur': 'rawr', 'rower': 'rawr', 'roar': 'rawr', "i'm": 'i am', 'im': 'i am'}
norm = lambda s: ' '.join(ALIAS.get(w, w) for w in re.sub(r"[^a-z' ]", ' ', s.lower()).split()).replace("'", '').split()

def speak(spk, text, ns, fast):
    model, pitch, ls = VOICES[spk]; buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        pv[spk].synthesize_wav(text, wf, syn_config=SynthesisConfig(length_scale=ls * (0.92 if fast else 1.0), noise_scale=ns, noise_w_scale=0.6))
    buf.seek(0); x, sr = sf.read(buf); raw = OUT / '_raw.wav'; fx = OUT / '_fx.wav'; sf.write(raw, x, sr)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(raw), '-af',
                    f'rubberband=pitch={pitch}:formant=preserved,highpass=f=110,equalizer=f=300:t=q:w=1:g=-4,equalizer=f=3500:t=q:w=1:g=4,'
                    'acompressor=threshold=-18dB:ratio=3:attack=5:release=60:makeup=2,'
                    'silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_threshold=-45dB:stop_duration=0.15',
                    '-ar', '48000', '-ac', '1', str(fx)], check=True)
    y, _ = sf.read(fx); return y

def score(y, text):
    heard = ' '.join(s.text for s in wm.transcribe(resample_poly(y, 1, 3).astype(np.float32), beam_size=5, language='en')[0])
    a, b = norm(text), norm(heard); return sum(1 for w in a if w in b) / max(len(a), 1), heard.strip()

sc = json.load(open(ROOT / 'script.json')); lines = []; bad = 0
for i, ev in enumerate(sc['events']):
    if ev['type'] in ('say', 'ask', 'answer'): items = [(ev['who'], ev.get('speak', ev['text']), ev['text'])]
    elif ev['type'] == 'song': items = [('both', l, l) for l in ev['lines']]
    else: continue
    for j, (who, spoken, shown) in enumerate(items):
        best = None
        for ns in (0.5, 0.35, 0.65, 0.25, 0.8):
            outs = [speak(s, spoken, ns, who == 'both') for s in (['tiko', 'lulu'] if who == 'both' else [who])]
            L = max(len(o) for o in outs); y = sum(np.pad(o, (0, L - len(o))) for o in outs) / len(outs); y = y / (np.abs(y).max() + 1e-9) * .9
            sc_, heard = score(y, spoken)
            if best is None or sc_ > best[0]: best = (sc_, heard, y)
            if sc_ >= .99: break
        s_, heard, y = best; bad += s_ < .8
        name = f'{i:02d}_{j}.wav'; sf.write(OUT / name, y.astype(np.float32), 48000)
        lines.append({'event': i, 'part': j, 'who': who, 'text': shown, 'file': name, 'dur': round(len(y) / 48000, 3), 'clarity': round(s_, 2)})
        print(f"{'OK ' if s_ >= .8 else 'BAD'} {who:4s} {len(y)/48000:4.1f}s | {shown!r} -> {heard!r}")
for f in OUT.glob('_*'): f.unlink()
json.dump(lines, open(ROOT / 'lines.json', 'w'), indent=1)
print('lines needing attention:', bad)
