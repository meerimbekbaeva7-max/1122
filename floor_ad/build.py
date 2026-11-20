"""Timeline from the voice lines -> data.js, and the music/SFX/voice mix -> mix.wav"""
import json, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly
SR = 48000; rng = np.random.default_rng(3)
L = json.load(open('lines.json'))
IMG = json.load(open('images.json'))   # scene -> image file(s)
GAP = 0.45
scenes = []; t = 0.3
for i, text in enumerate(L):
    v, sr = sf.read(f'vo/{i}.wav'); v = v.mean(1) if v.ndim > 1 else v
    d = len(v) / sr; dur = max(d + GAP, 2.3) + (1.6 if i == 10 else 0) + (0.3 if i == 0 else 0)
    scenes.append({'i': i, 't0': round(t, 3), 't1': round(t + dur, 3), 'vo': round(t + .12, 3), 'vd': round(d, 3), 'text': text, 'img': IMG[str(i)]})
    t += dur
DUR = round(t + .2, 3)
json.dump({'duration': DUR, 'scenes': scenes}, open('timeline.json', 'w'), ensure_ascii=False, indent=1)
open('data.js', 'w').write('window.TL=' + json.dumps({'duration': DUR, 'scenes': scenes}, ensure_ascii=False) + ';')
N = int(DUR * SR); tt = np.arange(N) / SR
vox = np.zeros(N)
for s in scenes:
    v, sr = sf.read(f'vo/{s["i"]}.wav'); v = v.mean(1) if v.ndim > 1 else v; v = resample_poly(v, SR, sr) if sr != SR else v
    i0 = int(s['vo'] * SR); vox[i0:i0 + len(v)] += v[:N - i0]
vox *= .95 / np.abs(vox).max()
mus = np.zeros(N); sfx = np.zeros(N)
def add(buf, at, y, a=1.):
    i = int(at * SR); e = min(N, i + len(y))
    if 0 <= i < N: buf[i:e] += y[:e - i] * a
hp = lambda x, f: sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
lp = lambda x, f: sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
bp = lambda x, a, b: sosfilt(butter(2, [a, b], 'band', fs=SR, output='sos'), x)
mhz = lambda m: 440 * 2 ** ((m - 69) / 12)
def kick(a=.8):
    x = np.arange(int(.3 * SR)) / SR; return np.sin(2 * np.pi * (170 * np.exp(-x * 30) + 48) * x) * np.exp(-x * 9) * a
def clap(a=.35):
    n = int(.2 * SR); return bp(rng.standard_normal(n), 1000, 7000) * np.exp(-np.arange(n) / SR * 28) * a
def hat(a=.06):
    n = int(.04 * SR); return hp(rng.standard_normal(n), 8000) * np.exp(-np.arange(n) / SR * 90) * a
def pluck(f, d, a=.08):
    x = np.arange(int(d * SR)) / SR; y = sum(np.sin(2 * np.pi * f * k * x) / k for k in (1, 2, 3)); return lp(y, 2500) * np.exp(-x * 7) * a
def whoosh(d=.5, a=.18):
    n = int(d * SR); w = rng.standard_normal(n); o = np.zeros(n)
    for j in range(8):
        s0, s1 = j * n // 8, (j + 1) * n // 8; f = 400 + 6000 * (j / 8) ** 2; o[s0:s1] = bp(w, f * .7, min(f * 1.4, 20000))[s0:s1]
    return o * np.sin(np.linspace(0, np.pi, n)) ** 2 * a
BPM = 122; B = 60 / BPM
prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]   # Am F C G
b = 0; k = 0
while b < DUR - .5:
    c = prog[(k // 8) % 4]
    if k % 2 == 0: add(mus, b, kick(.75 if k % 4 == 0 else .55))
    if k % 4 == 2: add(mus, b, clap())
    add(mus, b + B / 4, hat(.05)); add(mus, b, hat(.03))
    add(mus, b, np.sin(2 * np.pi * mhz(c[0] - 24) * np.arange(int(B / 2 * SR * .9)) / SR) * np.exp(-np.arange(int(B / 2 * SR * .9)) / SR * 6) * .35)
    if k % 2 == 1: add(mus, b, pluck(mhz(c[(k // 2) % 3] + 12), .3))
    b += B / 2; k += 1
for s in scenes[1:]: add(sfx, s['t0'] - .25, whoosh())
for s in scenes:
    if 4 <= s['i'] <= 7: add(sfx, s['t0'] + .05, pluck(mhz(84), .6, .18))      # step "ding"
x = np.arange(int(1.2 * SR)) / SR
add(sfx, scenes[3]['t0'], np.sin(2 * np.pi * (60 * np.exp(-x * 4) + 32) * x) * np.exp(-x * 2.5) * .9)   # solution impact
add(sfx, .05, np.sin(2 * np.pi * (60 * np.exp(-x * 4) + 32) * x) * np.exp(-x * 2.5) * .8)               # hook impact
sub, _ = sf.read('../kids/brand/subscribe_sfx.wav'); add(sfx, scenes[10]['t0'] + .3, sub.mean(1))
mus /= np.abs(mus).max()
ve = np.convolve(np.abs(vox), np.ones(2400) / 2400, 'same'); gdk = np.clip(ve / (np.percentile(ve[ve > 1e-4], 95) + 1e-9), 0, 1)
mus = mus * (1 - .5 * gdk); mus = mus - bp(mus, 1500, 5000) * .4 * gdk
mix = vox * 1.0 + mus * .45 + sfx * .8
mix *= np.clip(tt / .05, 0, 1) * np.clip((DUR - tt) / .5, 0, 1)
st = np.stack([mix, mix], 1); st = np.tanh(st * 1.1) / np.tanh(1.1); st *= .95 / np.abs(st).max()
sf.write('mix.wav', st.astype(np.float32), SR); print('duration', DUR)
