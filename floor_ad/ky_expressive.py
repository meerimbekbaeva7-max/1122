"""Make the Kyrgyz TTS lines livelier: wider intonation, rising questions, energetic exclamations,
natural micro-variation, then a clean 'radio ad' finish. vo_flat/N.wav -> vo/N.wav"""
import json, numpy as np, soundfile as sf, pyworld as pw, subprocess
from scipy.signal import resample_poly
L = json.load(open('lines.json')); rng = np.random.default_rng(4)
for i, text in enumerate(L):
    x, sr = sf.read(f'vo_flat/{i}.wav'); x = x.mean(1) if x.ndim > 1 else x
    y = resample_poly(x, 1, 2).astype(np.float64); fs = sr // 2          # WORLD at 24 kHz
    f0, t = pw.harvest(y, fs, f0_floor=70, f0_ceil=400, frame_period=5.0)
    sp = pw.cheaptrick(y, f0, t, fs); ap = pw.d4c(y, f0, t, fs); v = f0 > 0
    if v.sum() > 10:
        med = np.median(f0[v]); semi = np.zeros_like(f0); semi[v] = 12 * np.log2(f0[v] / med)
        semi[v] *= 1.7                                                   # wider melody
        pos = np.zeros(len(f0)); idx = np.where(v)[0]; pos[idx] = np.linspace(0, 1, len(idx))
        if '?' in text: semi[v] += 3.5 * np.clip((pos[v] - .72) / .28, 0, 1) ** 1.5
        if '!' in text:
            semi[v] += .8 + 1.6 * np.exp(-((pos[v] - .1) / .1) ** 2)       # bright, punchy start
        drift = np.convolve(rng.standard_normal(len(f0) + 60), np.ones(60) / 60, 'valid')[:len(f0)]
        semi[v] += drift[v] / (np.abs(drift).max() + 1e-9) * .35          # human micro-variation
        f2 = np.where(v, med * 2 ** (semi / 12), 0)
        ap = np.where(v[:, None], np.minimum(ap, ap * .6 + .01), ap)       # less buzz
        y = pw.synthesize(f2, sp, ap, fs, 5.0)
    sf.write('_tmp.wav', y, fs)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', '_tmp.wav', '-af',
        'atempo=1.06,highpass=f=90,equalizer=f=250:t=q:w=1.2:g=-4,equalizer=f=120:t=q:w=1:g=2,equalizer=f=3200:t=q:w=1:g=4,'
        'highshelf=f=7000:g=3,acompressor=threshold=-20dB:ratio=3.5:attack=4:release=70:makeup=3,'
        'aecho=0.8:0.4:18:0.05,loudnorm=I=-16:TP=-1.5:LRA=6', '-ar', '48000', '-ac', '1', f'vo/{i}.wav'], check=True)
    print(i, 'ok', round(len(sf.read(f'vo/{i}.wav')[0]) / 48000, 2))
import os; os.remove('_tmp.wav')
