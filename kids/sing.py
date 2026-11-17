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
OUT = ROOT / "build"; OUT.mkdir(exist_ok=True)
SR = 48000
BPM = 112; BEAT = 60 / BPM
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
INTRO_BEATS = 8
TOTAL = INTRO_BEATS + 8 * len(SONG)

voice = PiperVoice.load(str(ROOT.parent / "voice/models/en_US-amy-medium.onnx"))
cfg = SynthesisConfig(length_scale=1.0, noise_scale=0.5, noise_w_scale=0.6)


def speak(word):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        voice.synthesize_wav(word.strip(",!").lower(), wf, syn_config=cfg)
    buf.seek(0); x, sr = sf.read(buf)
    idx = np.where(np.abs(x) > 0.02)[0]
    x = x[max(idx[0] - 200, 0): idx[-1] + 200]
    return x.astype(np.float64), sr


def sing(word, notes, formant=1.10, vib=0.35):
    x, sr = speak(word)
    f0, t = pw.harvest(x, sr, f0_floor=70, f0_ceil=600, frame_period=5.0)
    sp = pw.cheaptrick(x, f0, t, sr); ap = pw.d4c(x, f0, t, sr)
    n = len(f0); voiced = np.where(f0 > 0)[0]
    dur = sum(b for _, b in notes) * BEAT * 0.92          # small gap before next note
    m = max(int(dur / 0.005), 10)
    if len(voiced) == 0:
        v0, v1 = 0, n - 1
    else:
        v0, v1 = voiced[0], voiced[-1]
    head, tail = v0, n - 1 - v1
    body_m = max(m - head - tail, 4)
    # time map: consonant head/tail at natural speed, voiced body stretched
    src = np.concatenate([np.arange(head), np.linspace(v0, v1, body_m), np.arange(v1 + 1, n)]).astype(float)
    m = len(src)
    i0 = np.floor(src).astype(int); fr = (src - i0)[:, None]; i1 = np.minimum(i0 + 1, n - 1)
    sp2 = sp[i0] * (1 - fr) + sp[i1] * fr; ap2 = ap[i0] * (1 - fr) + ap[i1] * fr
    vmask = np.concatenate([np.zeros(head, bool), np.ones(body_m, bool), np.zeros(n - 1 - v1, bool)])
    # pitch: lock voiced frames to the note(s), smooth glide, delayed vibrato
    tot = sum(b for _, b in notes); f = np.zeros(m); acc = 0
    bounds = []
    for name, b in notes:
        bounds.append((acc / tot, hz(name))); acc += b
    pos = np.clip((np.arange(m) - head) / max(body_m, 1), 0, 1)
    target = np.array([[h for s, h in bounds if s <= p][-1] for p in pos])
    k = 8; target = np.convolve(np.pad(target, k, mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), "valid")
    tt = np.arange(m) * 0.005
    vib_env = np.clip((tt - 0.15) / 0.2, 0, 1)
    f = target * 2 ** (vib / 12 * np.sin(2 * np.pi * 5.5 * tt) * vib_env / 1)
    f[~vmask] = 0
    # cartoon formant lift: stretch spectral envelope upward
    bins = sp2.shape[1]; src_bins = np.arange(bins) / formant
    sp3 = np.array([np.interp(src_bins, np.arange(bins), row) for row in sp2])
    y = pw.synthesize(f, np.ascontiguousarray(sp3), np.ascontiguousarray(ap2), sr, 5.0)
    y = resample_poly(y, SR, sr)
    L = len(y); fade = int(0.012 * SR)
    y[:fade] *= np.linspace(0, 1, fade); y[-fade * 3:] *= np.linspace(1, 0, fade * 3)
    return y


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
        s = int(beat * BEAT * SR); vox[s:s + len(y)] += y
        if tag in ("chorus", "all"):         # light "kids choir" double on the chorus
            y2 = sing(word, notes, formant=1.22, vib=0.25)
            dbl[s + 400:s + 400 + len(y2)] += y2
        b = sum(n for _, n in notes)
        wl.append({"w": word, "t0": round(beat * BEAT, 3), "t1": round((beat + b) * BEAT, 3)})
        beat += b
        print(f"{li} {word:9s} ok")
    lines.append({"tag": tag, "t0": round((INTRO_BEATS + 8 * li) * BEAT, 3),
                  "t1": round((INTRO_BEATS + 8 * li + 8) * BEAT, 3), "words": wl})

vox = vox / (np.abs(vox).max() + 1e-9) * 0.9
mix = vox + 0.45 * dbl / (np.abs(dbl).max() + 1e-9)
mix = mix[: int(TOTAL * BEAT * SR)]
sf.write(OUT / "vocals.wav", (mix / np.abs(mix).max() * 0.9).astype(np.float32), SR)
json.dump({"bpm": BPM, "beat": BEAT, "duration": TOTAL * BEAT, "intro": INTRO_BEATS * BEAT, "lines": lines,
           "song": [[t, [None if w is None else [w[0], w[1]] for w in ws]] for t, ws in SONG]},
          open(OUT / "song.json", "w"), indent=1)
print("duration", TOTAL * BEAT)
