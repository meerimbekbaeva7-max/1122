"""Turn a real sung take into a clean, in-time, in-tune lead vocal.
usage: python3 make_vocal.py <take.wav> <song.json> <out.wav> <seg_spec>
seg_spec: comma list of start-end (s) in the take for each NOTE of the song, e.g. "0.70-1.80,1.85-2.55,2.65-3.80"
Keeps the singer's timbre (WORLD spectral envelope) and natural pitch movement (30 %), snaps the note centre to the melody."""
import sys, json, numpy as np, soundfile as sf, pyworld as pw
from scipy.signal import butter, sosfilt, stft, istft, fftconvolve
take, songf, outf, spec = sys.argv[1:5]
x, sr = sf.read(take); x = x.mean(1) if x.ndim > 1 else x
song = json.load(open(songf)); B = song['beat']; IB = round(song['intro'] / B)
NOTE = {n: i for i, n in enumerate("C C# D D# E F F# G G# A A# B".split())}
hz = lambda s: 440 * 2 ** ((NOTE[s[:-1]] + 12 * (int(s[-1]) + 1) - 69) / 12)
# ---- 1) denoise: spectral gating with a noise profile from the quietest 0.3 s ----
x = sosfilt(butter(4, 75, 'high', fs=sr, output='sos'), x)
win = int(.02 * sr); e = np.array([np.sqrt(np.mean(x[i:i + win] ** 2)) for i in range(0, len(x) - win, win)])
q = np.argsort(e)[:max(3, int(.3 / .02))]; noise = np.concatenate([x[i * win:(i + 1) * win] for i in sorted(q)])
f, t, Z = stft(x, sr, nperseg=2048); _, _, N = stft(noise, sr, nperseg=2048)
prof = np.mean(np.abs(N), axis=1, keepdims=True)
mag = np.abs(Z); g = np.clip((mag - 1.8 * prof) / (mag + 1e-9), 0.08, 1)
g = np.apply_along_axis(lambda r: np.convolve(r, np.ones(5) / 5, 'same'), 1, g)   # smooth over time -> no musical noise
_, x = istft(Z * g, sr, nperseg=2048); x = x[:len(x)]
# ---- 2) melody notes from the song ----
notes = []
for li, (tag, ws) in enumerate(song['song']):
    b = IB + 8 * li
    for w in ws:
        if w is None: continue
        for n, d in w[1]: notes.append((b * B, d * B, n)); b += d
segs = [tuple(map(float, s.split('-'))) for s in spec.split(',')]
assert len(segs) == len(notes), (len(segs), len(notes))
# singer register: transpose the melody by whole octaves to sit near the singer's median pitch
y64 = np.ascontiguousarray(x.astype(np.float64))
f0all, _ = pw.harvest(y64, sr, f0_floor=70, f0_ceil=600, frame_period=5)
med = np.median(f0all[f0all > 0]); mel_med = np.median([hz(n) for _, _, n in notes])
octs = int(np.round(np.log2(med / mel_med))); print('singer median %.0f Hz, melody shifted %+d octave(s)' % (med, octs))
FP = 5.0
out = np.zeros(int(song['duration'] * sr) + sr)
for (a, b), (t0, dur, n) in zip(segs, notes):
    seg = np.ascontiguousarray(x[int(a * sr):int(b * sr)].astype(np.float64))
    f0, tt = pw.harvest(seg, sr, f0_floor=70, f0_ceil=600, frame_period=FP)
    sp = pw.cheaptrick(seg, f0, tt, sr); ap = pw.d4c(seg, f0, tt, sr)
    m = max(int(dur * .97 / (FP / 1000)), 8); src = np.linspace(0, len(f0) - 1, m)
    i0 = np.floor(src).astype(int); fr = (src - i0)[:, None]; i1 = np.minimum(i0 + 1, len(f0) - 1)
    sp2 = sp[i0] * (1 - fr) + sp[i1] * fr; ap2 = ap[i0] * (1 - fr) + ap[i1] * fr
    f0s = f0[np.round(src).astype(int)]; v = f0s > 0
    target = hz(n) * 2 ** octs
    if v.any():
        cents = 1200 * np.log2(np.where(v, f0s, 1) / np.median(f0s[v]))
        cents = np.clip(cents, -150, 150) * 0.3                    # keep 30 % of natural movement
        k = np.arange(m) * FP / 1000; scoop = -30 * np.exp(-k / .05)  # slight natural scoop into the note
        f2 = np.where(v, target * 2 ** ((cents + scoop) / 1200), 0)
    else:
        f2 = np.zeros(m)
    ap2 = np.where(v[:, None], np.minimum(ap2, ap2 * 0.5 + 0.01), ap2)   # a touch cleaner, still human
    yv = pw.synthesize(f2, np.ascontiguousarray(sp2), np.ascontiguousarray(ap2), sr, FP)
    fi, fo = int(.008 * sr), int(.03 * sr); yv[:fi] *= np.linspace(0, 1, fi); yv[-fo:] *= np.cos(np.linspace(0, np.pi / 2, fo))
    i = int(t0 * sr); out[i:i + len(yv)] += yv
    print(f'{n}: take {a:.2f}-{b:.2f}s -> {t0:.2f}s ({dur:.2f}s) at {target:.0f} Hz')
# ---- 3) studio polish ----
v = out
v = v - 0.2 * sosfilt(butter(2, [200, 400], 'band', fs=sr, output='sos'), v)
v = v + 0.3 * sosfilt(butter(2, [2500, 5000], 'band', fs=sr, output='sos'), v)
v = v + 0.15 * sosfilt(butter(2, 9000, 'high', fs=sr, output='sos'), v)
env = np.sqrt(np.convolve(v ** 2, np.ones(480) / 480, 'same')) + 1e-6
gc = np.clip((env / np.percentile(env[env > 1e-4], 90)) ** -0.4, .5, 2.2); v = v * np.convolve(gc, np.ones(480) / 480, 'same')
rng = np.random.default_rng(0); L = int(.5 * sr); ir = rng.standard_normal(L) * np.exp(-np.arange(L) / sr * 9); ir[:int(.01 * sr)] = 0
wet = fftconvolve(v, ir)[:len(v)]; v = v + .07 * wet * np.std(v) / (np.std(wet) + 1e-9)
v = v[:int(song['duration'] * sr)]; v = np.tanh(v / (np.abs(v).max() + 1e-9) * 1.3) / np.tanh(1.3) * .9
sf.write(outf, v.astype(np.float32), sr); print('vocal ok', outf)
