"""Rainbow Tots intro — ENERGETIC backing (variant 2). Same timing as intro.html:
build-up 0-1.67 s, groove 1.67-3.75 s, ta-da at 3.75 s. Writes build_intro/mix_energy.wav."""
import json, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
SR = 48000; DUR = 5.0; N = int(SR * DUR); rng = np.random.default_rng(21)
song = json.load(open('build_intro/song.json')); B = song['beat']; T0 = song['intro']; TD = T0 + 5 * B
t = np.arange(N) / SR
mhz = lambda m: 440 * 2 ** ((m - 69) / 12)
hp = lambda x, f: sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
lp = lambda x, f: sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
bp = lambda x, a, b: sosfilt(butter(2, [a, b], 'band', fs=SR, output='sos'), x)
bus = {k: np.zeros(N) for k in ('drums', 'bass', 'synth', 'fx', 'mel')}
def add(k, at, y, a=1.0):
    i = int(at * SR); e = min(N, i + len(y))
    if 0 <= i < N: bus[k][i:e] += y[:e - i] * a

def kick(a=1.0):
    L = int(.32 * SR); tt = np.arange(L) / SR
    body = np.sin(2 * np.pi * (180 * np.exp(-tt * 30) + 48) * tt) * np.exp(-tt * 9)
    click = hp(rng.standard_normal(L), 3000) * np.exp(-tt * 400) * .3
    return (body + click) * a
def clap(a=.5):
    L = int(.22 * SR); n = bp(rng.standard_normal(L), 1000, 7000); env = np.zeros(L)
    for d in (0, .008, .016, .024): i = int(d * SR); env[i:] += np.exp(-np.arange(L - i) / SR * (70 if d < .024 else 22))
    return n * env * a * .35
def snare(a=.5):
    L = int(.18 * SR); tt = np.arange(L) / SR
    return (bp(rng.standard_normal(L), 1500, 8000) * np.exp(-tt * 28) + np.sin(2 * np.pi * 190 * tt) * np.exp(-tt * 35) * .6) * a
def hat(a=.12, open_=False):
    L = int((.18 if open_ else .04) * SR); return hp(rng.standard_normal(L), 8000) * np.exp(-np.arange(L) / SR * (14 if open_ else 90)) * a
def tom(f, a=.6):
    L = int(.25 * SR); tt = np.arange(L) / SR; return np.sin(2 * np.pi * (f * 1.6 * np.exp(-tt * 12) + f) * tt) * np.exp(-tt * 10) * a
def saw_chord(ms, d, a=.12, cut=5000):
    L = int(d * SR); tt = np.arange(L) / SR; y = np.zeros(L)
    for m in ms:
        for det in (-.12, 0, .12):            # supersaw-ish
            f = mhz(m + det); y += 2 * ((f * tt + rng.random()) % 1) - 1
    y = lp(y / (len(ms) * 3), cut); env = np.minimum(1, tt / .005) * np.exp(-tt * 7)
    return y * env * a
def bass(m, d, a=.35):
    L = int(d * SR); tt = np.arange(L) / SR; f = mhz(m)
    y = np.sin(2 * np.pi * f * tt) + .35 * np.sign(np.sin(2 * np.pi * f * tt)) * .5
    return lp(y, 900) * np.minimum(1, tt / .004) * np.exp(-tt * 5) * a
def xylo(f, d=.6, a=.2):
    tt = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * f * tt) + .5 * np.sin(2 * np.pi * f * 3.98 * tt) * np.exp(-tt * 30) + .25 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * 6) * a

# ---------- 1) build-up 0 -> T0 ----------
L = int(T0 * SR); n = rng.standard_normal(L); sweep = np.zeros(L)        # rising noise sweep
for j in range(12):
    a, b = j * L // 12, (j + 1) * L // 12; f = 300 + 7000 * (j / 12) ** 2; sweep[a:b] = bp(n, f * .7, min(f * 1.5, 20000))[a:b]
add('fx', 0, sweep * np.linspace(0, 1, L) ** 2 * .35)
tt0 = 0.25; step = .2                                                    # accelerating snare roll
while tt0 < T0 - .02:
    add('drums', tt0, snare(.18 + .4 * tt0 / T0)); tt0 += step; step = max(.045, step * .86)
for k, m in enumerate([72, 74, 76, 79, 81, 84, 86, 88, 91]): add('mel', k * .07, xylo(mhz(m), .6, .13))   # glissando
add('fx', .5, np.sin(2 * np.pi * (1100 * np.exp(-np.arange(int(.18 * SR)) / SR * 18) + 250) * np.arange(int(.18 * SR)) / SR) * np.exp(-np.arange(int(.18 * SR)) / SR * 16) * .3)  # Lulu pop
tb = np.arange(int(.45 * SR)) / SR; add('fx', .9, np.sin(2 * np.pi * np.cumsum(180 + 520 * (1 - np.exp(-tb * 9))) / SR) * np.exp(-tb * 5) * .28)  # Tiko boing
add('drums', T0 - .02, kick(1.0)); add('fx', T0 - .02, hp(rng.standard_normal(int(1.0 * SR)), 5000) * np.exp(-np.arange(int(1.0 * SR)) / SR * 4) * .18)  # drop crash

# ---------- 2) groove T0 -> TD ----------
CH = {"C": [60, 64, 67, 72], "F": [60, 65, 69, 72], "G": [59, 62, 67, 71]}
prog = ["C", "C", "F", "F", "G"]                                      # one chord per beat (5 beats)
for k in range(5):
    at = T0 + k * B; c = CH[prog[k]]
    if k < 4: add('drums', at, kick(.95))
    if k % 2 == 1: add('drums', at, clap(.7))
    for s in range(4):                                                 # 16th hats, accented offbeats
        add('drums', at + s * B / 4, hat(.10 if s % 2 else .06, open_=(s == 2)))
    for s in range(2):                                                 # octave-bouncing bass 8ths
        add('bass', at + s * B / 2, bass(c[0] - 24 + (12 if s else 0), B / 2 * .9))
    add('synth', at + B / 2, saw_chord(c, B * .45, .16))               # offbeat stabs (pump)
# drum fill into the ta-da
for i, (o, f) in enumerate([(-.40, 220), (-.30, 180), (-.20, 150), (-.10, 120)]): add('drums', TD + o, tom(f, .55))
add('drums', TD - .1, snare(.5))

# ---------- 3) ta-da ----------
add('drums', TD, kick(1.2)); add('drums', TD, clap(.8))
add('fx', TD, hp(rng.standard_normal(int(1.3 * SR)), 4000) * np.exp(-np.arange(int(1.3 * SR)) / SR * 3) * .22)   # crash
add('synth', TD, saw_chord([48, 60, 64, 67, 72, 76], 1.25, .22, 7000))
add('bass', TD, bass(36, 1.2, .45))
for k, f in enumerate([1568, 2093, 2637, 3136, 4186]): add('mel', TD + .08 + k * .05, xylo(f, .6, .06))
for at, n, d in [(1.667, 72, .35), (1.92, 76, .35), (2.14, 79, 1.4)]:  # jingle melody under the voice
    add('mel', at, xylo(mhz(n), d + .3, .22)); add('mel', at, xylo(mhz(n + 12), d + .2, .08))

# ---------- mix ----------
mus = bus['drums'] * 1.0 + bus['bass'] * .9 + bus['synth'] * .8 + bus['fx'] * .8 + bus['mel'] * .9
mus = np.tanh(mus * 1.4) / np.tanh(1.4); mus /= np.abs(mus).max()                    # glue / punch
vox, _ = sf.read('build_intro/vocals.wav'); vox = vox.mean(1) if vox.ndim > 1 else vox; vox = np.pad(vox, (0, max(0, N - len(vox))))[:N]
ve = np.convolve(np.abs(vox), np.ones(2400) / 2400, 'same'); g = np.clip(ve / (np.percentile(ve, 99) + 1e-9), 0, 1)
mus = mus * (1 - .5 * g); mus = mus - bp(mus, 1500, 5000) * .45 * g                   # make room for the words
mix = vox * 1.05 + mus * .5; mix *= np.clip((DUR - t) / .2, 0, 1)
d = int(.008 * SR); R = vox * 1.05 + np.concatenate([np.zeros(d), mus[:-d]]) * .5 * np.clip((DUR - t) / .2, 0, 1)
st = np.stack([mix, R], 1); st = np.tanh(st * 1.15) / np.tanh(1.15); st *= .95 / np.abs(st).max()
sf.write('build_intro/mix_energy.wav', st.astype(np.float32), SR); print('energetic intro audio ok')
