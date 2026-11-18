"""'Transparent' finish for any vocal wav: rumble off, de-mud, presence, air, de-ess, dry. usage: clear_eq.py in.wav out.wav"""
import sys, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
v, sr = sf.read(sys.argv[1]); v = v.mean(1) if v.ndim > 1 else v
bp = lambda x, a, b: sosfilt(butter(2, [a, b], 'band', fs=sr, output='sos'), x)
v = sosfilt(butter(2, 120, 'high', fs=sr, output='sos'), v)
v = v - 0.5 * bp(v, 160, 500)                      # boxiness / mud
v = v + 0.6 * bp(v, 2200, 5500)                    # diction
v = v + 0.5 * sosfilt(butter(2, 8000, 'high', fs=sr, output='sos'), v)   # air
ex = np.tanh(bp(v, 3000, 6500) * 6) ; ex = sosfilt(butter(4, 7000, 'high', fs=sr, output='sos'), ex)   # exciter: synth has no content >11 kHz
v = v + 0.35 * ex * (np.std(v) / (np.std(ex) + 1e-9)) * 0.25
hi = sosfilt(butter(2, 6000, 'high', fs=sr, output='sos'), v)
he = np.sqrt(np.convolve(hi ** 2, np.ones(240) / 240, 'same')); thr = np.percentile(he, 95)
v = v - hi * np.clip(1 - thr / (he + 1e-9), 0, .5)  # de-esser
v = np.tanh(v / (np.abs(v).max() + 1e-9) * 1.2) / np.tanh(1.2) * .9
sf.write(sys.argv[2], v.astype(np.float32), sr); print('clear ok')
