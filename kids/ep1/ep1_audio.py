"""Episode 1 sound: playful bed (ducked under speech), footsteps, tick-tock while kids answer,
spike dings, sparkles, rainbow riser, energetic song groove, outro. -> mix.wav"""
import json, pathlib, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
ROOT = pathlib.Path(__file__).parent; SR = 48000; rng = np.random.default_rng(5)
T = json.load(open(ROOT / 'timeline.json')); S = T['segments']; DUR = T['duration']; N = int(DUR * SR)
t = np.arange(N) / SR
mhz = lambda m: 440 * 2 ** ((m - 69) / 12)
bp = lambda x, a, b: sosfilt(butter(2, [a, b], 'band', fs=SR, output='sos'), x)
hp = lambda x, f: sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
lp = lambda x, f: sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
bus = {k: np.zeros(N) for k in ('bed', 'song', 'sfx')}
def add(k, at, y, a=1.0):
    i = int(at * SR); e = min(N, i + len(y))
    if 0 <= i < N: bus[k][i:e] += y[:e - i] * a
def xylo(f, d=.5, a=.2):
    tt = np.arange(int(d * SR)) / SR; return (np.sin(2*np.pi*f*tt) + .5*np.sin(2*np.pi*f*3.98*tt)*np.exp(-tt*30) + .25*np.sin(4*np.pi*f*tt)) * np.exp(-tt*6) * a
def uke(fs, d, a=.06):
    L = int(d * SR); tt = np.arange(L) / SR; y = np.zeros(L)
    for j, f in enumerate(fs):
        o = int(j * .012 * SR); tl = tt[:L - o]; y[o:] += (np.sin(2*np.pi*f*tl) + .5*np.sin(4*np.pi*f*tl) + .3*np.sin(6*np.pi*f*tl)) * np.exp(-tl*5)
    return y * a
def kick(a=.6):
    tt = np.arange(int(.3*SR))/SR; return np.sin(2*np.pi*(160*np.exp(-tt*28)+48)*tt)*np.exp(-tt*9)*a
def clap(a=.3):
    L = int(.2*SR); return bp(rng.standard_normal(L), 1000, 7000) * np.exp(-np.arange(L)/SR*30) * a
def hat(a=.06):
    L = int(.04*SR); return hp(rng.standard_normal(L), 8000) * np.exp(-np.arange(L)/SR*90) * a
def tick(f=1800, a=.12):
    tt = np.arange(int(.05*SR))/SR; return np.sin(2*np.pi*f*tt) * np.exp(-tt*120) * a
def step(a=.18):
    L = int(.09*SR); return lp(rng.standard_normal(L), 700) * np.exp(-np.arange(L)/SR*45) * a
def chime(fs, a=.08):
    y = np.zeros(int(1.0*SR))
    for k, f in enumerate(fs):
        tt = np.arange(int(.6*SR))/SR; i = int(k*.06*SR); y[i:i+len(tt)] += np.sin(2*np.pi*f*tt)*np.exp(-tt*7)*a
    return y
def whoosh(d=.8, a=.2):
    L = int(d*SR); n = rng.standard_normal(L); out = np.zeros(L)
    for j in range(8):
        s0, s1 = j*L//8, (j+1)*L//8; f = 400 + 5000*(j/8)**2; out[s0:s1] = bp(n, f*.7, min(f*1.4, 20000))[s0:s1]
    return out * np.sin(np.linspace(0, np.pi, L))**2 * a
song = next(s for s in S if s['type'] == 'song'); BEAT = song['beat']
CH = {"C": [60, 64, 67, 72], "F": [60, 65, 69, 72], "G": [59, 62, 67, 71], "Am": [57, 60, 64, 69]}
# ---- 1) playful bed (C F G C, 2 beats per chord), off during the song ----
prog = ["C", "C", "F", "F", "G", "G", "C", "C"]; MEL = [72, 76, 79, 76, 77, 74, 72, 74]
b = 0.3; k = 0
while b < DUR - 2:
    if not (song['t0'] - .3 <= b < song['t1']):
        c = CH[prog[k % 8]]
        if k % 2 == 0: add('bed', b, uke([mhz(m) for m in c], 2*BEAT, .05))
        add('bed', b, np.sin(2*np.pi*mhz(c[0]-24)*np.arange(int(BEAT*SR))/SR)*np.exp(-np.arange(int(BEAT*SR))/SR*4)*.12)
        if k % 2 == 1: add('bed', b, xylo(mhz(MEL[(k//2) % 8]), .5, .05))
        add('bed', b, hat(.025))
    b += BEAT; k += 1
# ---- 2) footsteps while walking ----
for s in S:
    if s['type'] == 'walk':
        n = 0; st = s['t0'] + .15
        while st < s['t1'] - .1:
            add('sfx', st, step(.16 + .04 * (n % 2))); st += 1 / 2.4; n += 1
    if s['type'] == 'arrive':
        add('sfx', s['t0'], whoosh(1.2, .18)); add('sfx', s['t1'] - .2, chime([1568, 2093, 2637], .06))
# ---- 3) kids' pause: pop + gentle tick-tock; answer: ding + sparkle ----
notes = [1047, 1175, 1319, 1397, 1568, 1760]
for s in S:
    if s['type'] == 'pause':
        tt0 = np.arange(int(.2*SR))/SR; add('sfx', s['t0'], np.sin(2*np.pi*(700*np.exp(-tt0*10)+300)*tt0)*np.exp(-tt0*14)*.25)
        x = s['t0'] + .3; i = 0
        while x < s['t1'] - .1: add('sfx', x, tick(1600 if i % 2 else 1200, .1)); x += .5; i += 1
    if s['type'] == 'answer':
        L = s['light']; add('sfx', L, xylo(notes[s['spike']], .8, .22)); add('sfx', L, xylo(notes[s['spike']]*2, .6, .08))
        add('sfx', L + .05, chime([2093, 2637, 3136, 4186], .05))
    if s['type'] == 'say' and s.get('act') == 'turn':
        tt0 = np.arange(int(.5*SR))/SR; add('sfx', s['t0'] + .1, np.sin(2*np.pi*(500-300*tt0)*tt0)*np.exp(-tt0*4)*.15)   # "uh-oh" slide
    if s['type'] == 'say' and s.get('act') == 'rainbow':
        add('sfx', s['t0'] + .1, whoosh(1.0, .25)); [add('sfx', s['t0'] + 1 + k*.0, chime([1568, 2093, 2637, 3136, 4186], .07)) for k in range(1)]
        add('sfx', s['t0'] + 1, kick(.6))
# ---- 4) song groove (8 bars at 100 bpm) ----
sp = ["C", "C", "F", "F", "G", "G", "C", "C"]
for bar in range(len(song['lines'])):
    b0 = song['t0'] + bar * 4 * BEAT
    for bt in range(4):
        at = b0 + bt * BEAT; c = CH[sp[(bar*2 + bt//2) % 8]]
        add('song', at, kick(.7)); add('song', at + BEAT/2, hat(.07))
        if bt % 2 == 1: add('song', at, clap(.35))
        for s2 in range(2): add('song', at + s2*BEAT/2, np.sin(2*np.pi*mhz(c[0]-24+(12 if s2 else 0))*np.arange(int(BEAT/2*SR*.9))/SR)*np.exp(-np.arange(int(BEAT/2*SR*.9))/SR*5)*.3)
        if bt % 2 == 0: add('song', at, uke([mhz(m) for m in c], 2*BEAT, .08))
    # melody hint on xylophone: one note per sung word-ish (C E G E)
    for j, m in enumerate([72, 76, 79, 76]): add('song', b0 + .25 + j*BEAT, xylo(mhz(m), .5, .07))
end = song['t1']; add('song', end, chime([1047, 1319, 1568, 2093], .08)); add('song', end, kick(.8))
# ---- 5) outro: subscribe pop/click/chime ----
outro = next(s for s in S if s['type'] == 'outro')
sub, _ = sf.read(ROOT.parent / 'brand/subscribe_sfx.wav'); add('sfx', outro['t0'], sub.mean(1) * .9)
# ---- mix with ducking under dialogue ----
vox, _ = sf.read(ROOT / 'dialogue.wav'); vox = np.pad(vox, (0, max(0, N - len(vox))))[:N]
ve = np.convolve(np.abs(vox), np.ones(2400)/2400, 'same'); g = np.clip(ve / (np.percentile(ve[ve > 1e-4], 95) + 1e-9), 0, 1)
bed = bus['bed'] * (1 - .55*g); songb = bus['song'] * (1 - .35*g); songb = songb - bp(songb, 1500, 5000) * .4 * g
mus = bed*.9 + songb*.85 + bus['sfx']*.9
mus *= np.clip(t / .5, 0, 1) * np.clip((DUR - t) / .6, 0, 1)
mix = vox * 1.0 + mus
st = np.stack([mix, mix], 1); st = np.tanh(st*1.1)/np.tanh(1.1); st *= .95 / np.abs(st).max()
sf.write(ROOT / 'mix.wav', st.astype(np.float32), SR); print('ep1 audio ok', DUR)
