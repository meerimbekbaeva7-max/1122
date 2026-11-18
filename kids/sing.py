"""Make the TTS voice *sing* an original kids' "Colors Song".

Each word is spoken by Piper (en_US-amy), analysed with the WORLD vocoder, then
re-synthesised with its pitch locked to the melody notes (plus gentle vibrato),
its vowel stretched to the note length and its formants lifted a little for a
friendly cartoon timbre. Outputs:
  build/vocals.wav  - lead vocal, 48 kHz
  build/song.json   - bpm, lines, word timings (for lyrics + mouth sync)
"""
import json, pathlib, wave, io
import numpy as np, soundfile as sf, pyworld as pw
from scipy.signal import resample_poly
from piper import PiperVoice
from piper.config import SynthesisConfig

ROOT = pathlib.Path(__file__).parent
import sys
OUT = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "build"; OUT.mkdir(exist_ok=True)
SR = 48000
import os
BPM = float(os.environ.get('BPM', 112)); BEAT = 60 / BPM
NOTE = {n: i for i, n in enumerate("C C# D D# E F F# G G# A A# B".split())}
def hz(name):
    n, o = name[:-1], int(name[-1]); return 440 * 2 ** ((NOTE[n] + 12 * (o + 1) - 69) / 12)

# (word, [(note, beats), ...]) ; None = rest. 8 beats per line, intro = 8 beats.
SONG = [
    ("red",   [("Red", [("G4", 1)]), ("red", [("G4", 1)]), ("apple", [("E4", .5), ("F4", .5)]), ("is", [("G4", 1)]), ("red!", [("C5", 2)]), None]),
    ("blue",  [("Blue", [("A4", 1)]), ("blue,", [("A4", 1)]), ("the", [("F4", .5)]), ("sky", [("F4", .5)]), ("is", [("G4", 1)]), ("blue!", [("A4", 2)]), None]),
    ("yellow",[("Yellow,", [("G4", .5), ("E4", .5)]), ("yellow,", [("G4", .5), ("E4", .5)]), ("sunny", [("C5", 1), ("B4", 1)]), ("yellow!", [("A4", 1), ("G4", 1)]), None]),
    ("green", [("Green,", [("F4", 1)]), ("green,", [("F4", 1)]), ("the", [("D4", .5)]), ("frog", [("D4", .5)]), ("is", [("E4", 1)]), ("green!", [("C4", 2)]), None]),
    ("chorus",[("Colors,", [("E4", .5), ("G4", .5)]), ("colors,", [("E4", .5), ("G4", .5)]), ("sing", [("C5", 1)]), ("with", [("B4", 1)]), ("me!", [("C5", 2)]), None]),
    ("all",   [("Red,", [("C5", 1)]), ("blue,", [("A4", 1)]), ("yellow,", [("G4", .5), ("E4", .5)]), ("green!", [("C5", 3)]), None]),
]
if len(sys.argv) > 1:
    SONG = [(t, [None if w is None else (w[0], [tuple(n) for n in w[1]]) for w in ws]) for t, ws in json.load(open(sys.argv[1]))]
INTRO_BEATS = int(os.environ.get("INTRO_BEATS", 8))
TOTAL = INTRO_BEATS + 8 * len(SONG)

VOICE = os.environ.get("VOICE", "en_US-lessac-high")
voice = PiperVoice.load(str(ROOT.parent / f"voice/models/{VOICE}.onnx"))
cfg = SynthesisConfig(length_scale=1.0, noise_scale=0.4, noise_w_scale=0.5)
FP = 5.0  # WORLD frame period, ms
CLEAN = os.environ.get('CLEAN') == '1'
HUMAN = os.environ.get('HUMAN') == '1'   # tiny timing/level/pitch imperfections like a real singer
HRNG = np.random.default_rng(11)   # studio-clean lead: no double, tight room, gate, cleaner excitation


from functools import lru_cache

@lru_cache(maxsize=None)
def speak(word):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        voice.synthesize_wav(word, wf, syn_config=cfg)
    buf.seek(0); x, sr = sf.read(buf)
    idx = np.where(np.abs(x) > 0.015)[0]
    x = x[max(idx[0] - 160, 0): idx[-1] + 160]
    return x.astype(np.float64), sr


def fill_dropouts(f0, max_gap):
    """Harvest sometimes reports a few unvoiced frames in the middle of a vowel -> rasp/glitch.
    Bridge short gaps by interpolation; keep long gaps (real consonants)."""
    f = f0.copy(); v = np.where(f > 0)[0]
    if len(v) < 2: return f
    for a, b in zip(v[:-1], v[1:]):
        if 1 < b - a <= max_gap:
            f[a:b + 1] = np.interp(np.arange(a, b + 1), [a, b], [f[a], f[b]])
    return f


_cache = {}
def sing(word, notes, formant=1.0, vib=0.18, detune=0.0):
    spoken = word.split('|')[-1].strip(',!?').lower().replace('_', ' ')
    key = (spoken, tuple(map(tuple, notes)), formant, vib, detune)
    if key in _cache and not HUMAN: return _cache[key].copy()
    x, sr = speak(spoken)
    f0, t = pw.harvest(x, sr, f0_floor=90, f0_ceil=650, frame_period=FP)
    f0 = fill_dropouts(f0, max_gap=int(35 / FP))
    sp = pw.cheaptrick(x, f0, t, sr); ap = pw.d4c(x, f0, t, sr)
    n = len(f0); voiced = np.where(f0 > 0)[0]
    dur = sum(b for _, b in notes) * BEAT * 0.985            # legato: almost no gap between notes
    m = max(int(dur / (FP / 1000)), 10)
    v0, v1 = (voiced[0], voiced[-1]) if len(voiced) else (0, n - 1)
    head, tail = v0, n - 1 - v1
    body_m = max(m - head - tail, 4)
    # time map: consonants at natural speed, vowel body stretched (ease the stretch so it doesn't "freeze")
    u = np.linspace(0, 1, body_m); u = 0.5 - 0.5 * np.cos(np.pi * u) * 0.0 + (u - 0.5)  # linear, kept explicit
    src = np.concatenate([np.arange(head), v0 + u * (v1 - v0), np.arange(v1 + 1, n)]).astype(float)
    m = len(src)
    i0 = np.floor(src).astype(int); fr = (src - i0)[:, None]; i1 = np.minimum(i0 + 1, n - 1)
    sp2 = sp[i0] * (1 - fr) + sp[i1] * fr; ap2 = ap[i0] * (1 - fr) + ap[i1] * fr
    srcf0 = f0[np.round(src).astype(int)]
    vmask = srcf0 > 0
    # a voiced body that is mostly voiced: bridge tiny holes created by the stretch
    vmask[head:head + body_m] |= np.convolve(vmask[head:head + body_m].astype(float), np.ones(9) / 9, "same") > 0.5
    # pitch line: notes -> scoop into each note, glide between notes, gentle late vibrato on long notes
    tot = sum(b for _, b in notes); acc = 0; bounds = []
    for name, b in notes:
        bounds.append((acc / tot, hz(name) * 2 ** (detune / 1200), b)); acc += b
    pos = np.clip((np.arange(m) - head) / max(body_m, 1), 0, 1)
    idx = np.array([max(i for i, (s0, _, _) in enumerate(bounds) if s0 <= p) for p in pos])
    target = np.array([bounds[i][1] for i in idx])
    tt = np.arange(m) * FP / 1000
    # note-local time (for scoop + vibrato)
    start_t = np.array([bounds[i][0] for i in idx]) * (body_m * FP / 1000) + head * FP / 1000
    lt = np.maximum(tt - start_t, 0)
    scoop = 2 ** (-0.35 / 12 * np.exp(-lt / 0.05))            # start ~35 cents flat, settle in ~50 ms
    k = 6; target = np.exp(np.convolve(np.pad(np.log(target), k, mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), "valid"))
    long_note = np.array([bounds[i][2] * BEAT >= 0.45 for i in idx])
    vib_env = np.clip((lt - 0.22) / 0.25, 0, 1) * long_note
    vrate = 5.2 * (1 + (HRNG.uniform(-.06, .06) if HUMAN else 0))
    f = target * scoop * 2 ** (vib / 12 * np.sin(2 * np.pi * vrate * tt) * vib_env)
    if HUMAN:  # slow natural pitch drift, +-6 cents
        drift = np.convolve(HRNG.standard_normal(m + 80), np.ones(80) / 80, 'valid')[:m]
        f = f * 2 ** (drift / (np.abs(drift).max() + 1e-9) * 6 / 1200)
    f[~vmask] = 0
    # cleaner, less buzzy voiced frames
    ap2 = np.where(vmask[:, None], np.minimum(ap2, 0.35 + 0.65 * ap2 ** 2), ap2)
    if CLEAN:  # less breath noise inside sung vowels (keeps consonants intact)
        fq = np.linspace(0, sr / 2, ap2.shape[1])
        clean = np.where(fq < 5000, 0.12, 0.5)[None, :]          # nearly pure harmonics below 5 kHz, a little air above
        ap2 = np.where(vmask[:, None], np.minimum(ap2, ap2 * clean + 0.002), ap2)
    if formant != 1.0:
        bins = sp2.shape[1]; src_bins = np.arange(bins) / formant
        sp2 = np.array([np.interp(src_bins, np.arange(bins), row) for row in sp2])
    y = pw.synthesize(f, np.ascontiguousarray(sp2), np.ascontiguousarray(ap2), sr, FP)
    y = resample_poly(y, SR, sr)
    fi, fo = int(0.006 * SR), int(0.03 * SR)
    y[:fi] *= np.linspace(0, 1, fi) ** 0.5; y[-fo:] *= np.cos(np.linspace(0, np.pi / 2, fo))
    _cache[key] = y
    return y.copy()


vox = np.zeros(int(TOTAL * BEAT * SR) + SR)
dbl = np.zeros_like(vox)
lines = []
for li, (tag, words) in enumerate(SONG):
    beat = INTRO_BEATS + 8 * li
    wl = []
    for w in words:
        if w is None:
            continue
        word, notes = w
        y = sing(word, notes)
        s = int(beat * BEAT * SR)
        if HUMAN:
            s = max(0, s + int(HRNG.uniform(-.012, .012) * SR)); y = y * 10 ** (HRNG.uniform(-1.2, 1.2) / 20)
        vox[s:s + len(y)] += y
        if not CLEAN and (tag in ("chorus", "all", "vroom", "bye") or tag.startswith("ch")):   # subtle double-track on choruses
            y2 = sing(word, notes, vib=0.12, detune=9)
            d = int(0.022 * SR); dbl[s + d:s + d + len(y2)] += y2
        b = sum(n for _, n in notes)
        wl.append({"w": word.split("|")[0], "t0": round(beat * BEAT, 3), "t1": round((beat + b) * BEAT, 3)})
        beat += b
        print(f"{li} {word:9s} ok")
    lines.append({"tag": tag, "t0": round((INTRO_BEATS + 8 * li) * BEAT, 3),
                  "t1": round((INTRO_BEATS + 8 * li + 8) * BEAT, 3), "words": wl})

# ---- vocal polish: de-ess, presence, gentle compression, small room reverb ----
from scipy.signal import butter, sosfilt, fftconvolve
def polish(v):
    v = sosfilt(butter(2, 90, "high", fs=SR, output="sos"), v)
    hi = sosfilt(butter(2, 6500, "high", fs=SR, output="sos"), v)
    env = np.sqrt(np.convolve(hi ** 2, np.ones(240) / 240, "same")); thr = np.percentile(env, 97)
    v = v - hi * np.clip(1 - thr / (env + 1e-9), 0, 0.6)                # de-esser
    v = v + 0.25 * sosfilt(butter(2, [2500, 5000], "band", fs=SR, output="sos"), v)   # presence
    e = np.sqrt(np.convolve(v ** 2, np.ones(480) / 480, "same")) + 1e-6
    g = np.clip((e / np.percentile(e[e > 1e-4], 90)) ** -0.35, 0.5, 2.0)   # ~3:1 soft compression
    g = np.convolve(g, np.ones(480) / 480, "same"); v = v * g
    rng = np.random.default_rng(0); L = int(0.9 * SR); tt = np.arange(L) / SR
    ir = rng.standard_normal(L) * np.exp(-tt * 6.5); ir = sosfilt(butter(1, 5000, "low", fs=SR, output="sos"), ir); ir[:int(.012 * SR)] = 0
    wet = fftconvolve(v, ir)[:len(v)]; wet *= np.std(v) / (np.std(wet) + 1e-9)
    if CLEAN:
        return v + float(os.environ.get('ROOM', 0.05)) * sosfilt(butter(2, [300, 6000], 'band', fs=SR, output='sos'), fftconvolve(v, ir[:int(.35 * SR)])[:len(v)] * np.std(v) / (np.std(wet) + 1e-9))
    return v + 0.16 * wet
vox = polish(vox)
if CLEAN:
    # broadcast EQ: cut mud, add clarity and air
    vox = vox - 0.25 * sosfilt(butter(2, [220, 450], "band", fs=SR, output="sos"), vox)
    vox = vox + 0.22 * sosfilt(butter(2, [2800, 4500], "band", fs=SR, output="sos"), vox)
    vox = vox + 0.15 * sosfilt(butter(2, 9000, "high", fs=SR, output="sos"), vox)
    # downward expander/gate: silence between words, smooth attack/release
    env = np.sqrt(np.convolve(vox ** 2, np.ones(480) / 480, "same")); thr = np.percentile(env[env > 1e-5], 35) * 0.5
    g = np.clip(env / thr, 0, 1) ** 2
    k = int(0.04 * SR); g = np.maximum.accumulate(np.r_[g, np.zeros(k)][::-1])[::-1][:len(g)] if False else g
    rel = np.exp(-1 / (0.08 * SR)); gs = np.empty_like(g); a = 0.0
    for i in range(len(g)):
        a = g[i] if g[i] > a else a * rel + g[i] * (1 - rel)
        gs[i] = a
    vox = vox * (0.03 + 0.97 * gs)
    # peak limiter
    vox = np.tanh(vox / (np.percentile(np.abs(vox), 99.9) + 1e-9) * 1.2) * 0.9
if np.abs(dbl).max() > 0: dbl = polish(dbl)
vox = vox / (np.abs(vox).max() + 1e-9) * 0.9
mix = vox + 0.28 * dbl / (np.abs(dbl).max() + 1e-9) * (np.abs(vox).max())
mix = mix[: int(TOTAL * BEAT * SR)]
sf.write(OUT / "vocals.wav", (mix / np.abs(mix).max() * 0.9).astype(np.float32), SR)
json.dump({"bpm": BPM, "beat": BEAT, "duration": TOTAL * BEAT, "intro": INTRO_BEATS * BEAT, "lines": lines,
           "song": [[t, [None if w is None else [w[0], w[1]] for w in ws]] for t, ws in SONG]},
          open(OUT / "song.json", "w"), indent=1)
print("duration", TOTAL * BEAT)
