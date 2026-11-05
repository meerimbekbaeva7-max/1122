"""Mix voiceover + synthesized cinematic score into build/mix.wav (35 s, 48 kHz stereo)."""
import json
import pathlib

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly

ROOT = pathlib.Path(__file__).parent
B = ROOT / "build"
SR = 48000
DUR = 35.0
N = int(SR * DUR)
rng = np.random.default_rng(3)

TL = [[0, 7.2], [7.2, 11.6], [11.6, 16.6], [16.6, 24.2], [24.2, 28.6], [28.6, 35]]
TURN = TL[2][0] + 1.8

# voice clip -> start time (s), matched to scene.html
span1 = (TL[1][1] - TL[1][0] - .6) / 3
PLACE = {
    0: TL[0][0] + .4,
    1: TL[1][0] + .15, 2: TL[1][0] + .15 + span1, 3: TL[1][0] + .15 + 2 * span1,
    4: TL[2][0] + .25,
    5: TL[3][0] + .4,
    6: TL[4][0] + .08, 7: TL[4][0] + 1.38, 8: TL[4][0] + 2.68,
    9: TL[5][0] + .4,
}

t = np.arange(N) / SR


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)


def env(a, b, fade=0.5):
    e = np.clip((t - a) / fade, 0, 1) * np.clip((b - t) / fade, 0, 1)
    return e


# ---------------- voice ----------------
voice = np.zeros(N)
for i, start in PLACE.items():
    w, sr = sf.read(B / f"vo_{i}.wav")
    w = resample_poly(w, SR, sr)
    s = int(start * SR)
    voice[s:s + len(w)] += w[: N - s]
# gentle broadcast EQ: cut mud, add presence
voice = hp(voice, 90) + 0.35 * bp(voice, 2500, 6000) - 0.15 * bp(voice, 250, 450)
# soft compression
voice = np.tanh(voice * 1.8) / np.tanh(1.8)
voice *= 0.85 / (np.abs(voice).max() + 1e-9)

# ---------------- score ----------------
def note(f):
    return 440 * 2 ** ((f - 69) / 12)


def pad(chord, a, b, bright=0.3, amp=0.12):
    x = np.zeros(N)
    for m in chord:
        for det in (-0.12, 0, 0.11):
            f = note(m + det)
            ph = rng.uniform(0, 6.28)
            x += np.sin(2 * np.pi * f * t + ph) + bright * np.sin(4 * np.pi * f * t + ph) * 0.5
    x = lp(x, 1800 + 3000 * bright)
    return x * env(a, b, 1.2) * amp / len(chord)


music = np.zeros(N)
# problem: dark D minor drones
music += pad([38, 50, 53, 57], 0, TURN + .4, bright=.15, amp=.16)
# tension pulse (heartbeat) in the problem section
for k, bt in enumerate(np.arange(0.6, TURN - .2, 0.75)):
    s = int(bt * SR); L = int(.35 * SR)
    tt = np.arange(L) / SR
    kick = np.sin(2 * np.pi * (55 * np.exp(-tt * 8) + 38) * tt) * np.exp(-tt * 9)
    music[s:s + L] += kick[: N - s] * 0.35
# solution: uplifting progression F - C - Dm - Bb (lifted), brighter
prog_ch = [[53, 57, 60, 65], [48, 55, 60, 64], [50, 57, 62, 65], [46, 53, 58, 62]]
seg = (DUR - TURN) / 4
for i, ch in enumerate(prog_ch * 1):
    a = TURN + i * seg
    music += pad(ch, a - .2, a + seg + .6, bright=.55, amp=.13)
# driving pulse after the turn (8th-note plucks)
bpm = 112; eighth = 60 / bpm / 2
for k, bt in enumerate(np.arange(TURN + .1, DUR - .8, eighth)):
    ch = prog_ch[min(int((bt - TURN) / seg), 3)]
    f = note(ch[k % 4] + 12)
    s = int(bt * SR); L = int(.22 * SR)
    tt = np.arange(L) / SR
    pl = (np.sin(2 * np.pi * f * tt) + .3 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * 18)
    music[s:s + L] += pl[: N - s] * 0.07
    if k % 4 == 0:  # kick on the beat
        L2 = int(.3 * SR); t2 = np.arange(L2) / SR
        kk = np.sin(2 * np.pi * (60 * np.exp(-t2 * 10) + 42) * t2) * np.exp(-t2 * 8)
        music[s:s + L2] += kk[: N - s] * 0.32
# sub bass under the solution
music += 0.10 * np.sin(2 * np.pi * note(29) * t) * env(TURN, DUR, 1.0)


def boom(at, amp=0.9):
    s = int(at * SR); L = int(1.6 * SR); tt = np.arange(L) / SR
    b = np.sin(2 * np.pi * (70 * np.exp(-tt * 4) + 30) * tt) * np.exp(-tt * 2.6)
    noise = lp(rng.standard_normal(L), 900) * np.exp(-tt * 9) * .5
    x = (b + noise) * amp
    music[s:s + L] += x[: N - s]


def whoosh(end, length=0.9, amp=0.35):
    L = int(length * SR); s = int((end - length) * SR)
    n = rng.standard_normal(L)
    sweep = np.linspace(0, 1, L) ** 2
    out = np.zeros(L)
    for j in range(8):  # stepwise rising band
        a, b = j * L // 8, (j + 1) * L // 8
        f = 300 + 5000 * sweep[(a + b) // 2]
        out[a:b] = bp(n, f * .7, min(f * 1.4, 20000))[a:b]
    out *= sweep * amp
    music[max(s, 0):s + L] += out[: N - s]


# stamps
for i in range(3):
    boom(TL[0][0] + 1.6 + i * .8, .55)
# scene transitions
for a, _ in TL[1:]:
    whoosh(a + .05, .8, .22)
# the turn: big riser + impact
whoosh(TURN, 1.4, .45)
boom(TURN, 1.0)
# punches
for i in range(3):
    boom(TL[4][0] + .05 + i * 1.3 + .1, .6)
# CTA tap
boom(TL[5][0] + 3.0, .4)

music *= 0.8 / (np.abs(music).max() + 1e-9)

# sidechain-style ducking under the voice
venv = np.abs(voice)
k = int(.08 * SR)
venv = np.convolve(venv, np.ones(k) / k, mode="same")
duck = 1 - 0.55 * np.clip(venv / (venv.max() * .25 + 1e-9), 0, 1)
music *= duck
music *= np.clip((DUR - t) / 1.2, 0, 1)  # fade out tail
music *= np.clip(t / .3, 0, 1)

# stereo: voice centred, music widened with a short Haas delay
d = int(.012 * SR)
mL = music
mR = np.concatenate([np.zeros(d), music[:-d]])
L_ = voice * 1.0 + mL * .62
R_ = voice * 1.0 + mR * .62
st = np.stack([L_, R_], 1)
st = np.tanh(st * 1.2) / np.tanh(1.2)  # soft limiter
st *= 0.95 / np.abs(st).max()
sf.write(B / "mix.wav", st.astype(np.float32), SR)
print("mix written", st.shape)
