"""Bright kids' backing track for the Colors Song + final mix -> build/mix.wav"""
import json, sys, os
BD = sys.argv[1] if len(sys.argv) > 1 else "build"
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt

SR = 48000
song = json.load(open(f"{BD}/song.json"))
B = song["beat"]; DUR = song["duration"]; N = int(DUR * SR); rng = np.random.default_rng(5)
t = np.arange(N) / SR
NOTE = {n: i for i, n in enumerate("C C# D D# E F F# G G# A A# B".split())}
def hz(name): n, o = name[:-1], int(name[-1]); return 440 * 2 ** ((NOTE[n] + 12 * (o + 1) - 69) / 12)
def mhz(m): return 440 * 2 ** ((m - 69) / 12)
hp = lambda x, f: sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)
bp = lambda x, a, b: sosfilt(butter(2, [a, b], "band", fs=SR, output="sos"), x)
out = {k: np.zeros(N) for k in ("mel", "uke", "bass", "drum")}
def add(k, at, x):
    s = int(at * SR); e = min(N, s + len(x))
    if s < N: out[k][s:e] += x[:e - s]

def xylo(f, d=.5, a=.25):
    L = int(d * SR); tt = np.arange(L) / SR
    return (np.sin(2*np.pi*f*tt) + .5*np.sin(2*np.pi*f*3.98*tt)*np.exp(-tt*30) + .25*np.sin(2*np.pi*f*2*tt)) * np.exp(-tt*7) * a
def uke(freqs, d, a=.07):
    L = int(d * SR); tt = np.arange(L) / SR; y = np.zeros(L)
    for j, f in enumerate(freqs):            # strum: 12 ms between strings, plucked tone
        o = int(j * .012 * SR); tl = tt[:L - o]
        y[o:] += (np.sin(2*np.pi*f*tl) + .5*np.sin(4*np.pi*f*tl) + .3*np.sin(6*np.pi*f*tl)) * np.exp(-tl*6)
    return y * a
def kick(a=.6):
    L = int(.3*SR); tt = np.arange(L)/SR; return np.sin(2*np.pi*(150*np.exp(-tt*25)+50)*tt)*np.exp(-tt*10)*a
def clap(a=.25):
    L = int(.18*SR); n = bp(rng.standard_normal(L), 900, 6000); env = np.exp(-np.arange(L)/SR*25)
    for d in (0, .01, .02): env[int(d*SR):] += np.exp(-np.arange(L-int(d*SR))/SR*60)*.5
    return n*env*a
def shaker(a=.05):
    L = int(.06*SR); return hp(rng.standard_normal(L), 6000)*np.exp(-np.arange(L)/SR*60)*a

# chords: per line, 4 chords x 2 beats ; intro first
CH = {"C": [60, 64, 67, 72], "F": [60, 65, 69, 72], "G": [59, 62, 67, 71], "Am": [60, 64, 69, 72]}
prog = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else [["C", "F", "G", "C"], ["C", "C", "F", "C"], ["F", "F", "C", "F"], ["C", "C", "G", "C"],
        ["F", "G", "C", "C"], ["C", "C", "G", "C"], ["C", "F", "C", "C"]]
for li, p in enumerate(prog):
    for k, c in enumerate(p):
        at = (li * 8 + k * 2) * B
        add("uke", at, uke([mhz(m) for m in CH[c]], 2 * B))
        add("uke", at + B, uke([mhz(m) for m in CH[c]][::-1], B, .05))
        add("bass", at, np.sin(2*np.pi*mhz(CH[c][0]-24)*np.arange(int(1.8*B*SR))/SR)*np.exp(-np.arange(int(1.8*B*SR))/SR*2.5)*.35)
# drums: from bar 2 of intro, kick on 1&3, clap on 2&4, shaker 8ths
for b in np.arange(4, DUR / B, 1):
    at = b * B
    if int(b) % 2 == 0: add("drum", at, kick())
    else: add("drum", at, clap())
    add("drum", at, shaker()); add("drum", at + B/2, shaker(.03))
# intro xylophone fanfare (C E G C')
for k, n in enumerate(["C5", "E5", "G5", "C6", "G5", "C6"]):
    add("mel", k * .5 * B, xylo(hz(n), .6, .22))
# xylophone doubles the sung melody an octave up (helps kids follow the tune)
for li, (tag, words) in enumerate(song["song"]):
    beat = 8 + 8 * li
    for w in words:
        if w is None: continue
        for n, b in w[1]:
            add("mel", beat * B, xylo(hz(n) * 2, min(b * B, .6), .12)); beat += b
# "ta-da" sparkle at the end
for k, n in enumerate(["C6", "E6", "G6", "C7"]):
    add("mel", DUR - 1.6 + k * .06, xylo(hz(n), 1.2, .1))

music = out["mel"] + out["uke"] + out["bass"] + out["drum"]
music /= np.abs(music).max()
vox, _ = sf.read(f"{BD}/vocals.wav")
vox = np.pad(vox, (0, max(0, N - len(vox))))[:N]
mix = vox * 1.0 + music * 0.55
d = int(.01 * SR)
st = np.stack([mix, np.concatenate([np.zeros(d), music[:-d]]) * .55 + vox], 1)
st = np.tanh(st * 1.3) / np.tanh(1.3); st *= .95 / np.abs(st).max()
st *= np.clip((DUR - t) / .4, 0, 1)[:, None]
sf.write(f"{BD}/mix.wav", st.astype(np.float32), SR)
# per-frame vocal envelope (30 fps) for mouth sync
fps = 30; hop = SR // fps
env = np.array([np.sqrt(np.mean(vox[i:i + hop] ** 2)) for i in range(0, N, hop)])
env = np.clip(env / (np.percentile(env, 98) + 1e-9), 0, 1)
json.dump([round(float(v), 3) for v in env], open(f"{BD}/env.json", "w"))
print("mix ok", DUR)
