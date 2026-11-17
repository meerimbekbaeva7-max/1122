"""Shell cracks, pop and twinkle at every reveal (Surprise Eggs)."""
import numpy as np, soundfile as sf, json
from scipy.signal import butter, sosfilt
x,sr=sf.read('build_eggs/mix.wav');s=json.load(open('build_eggs/song.json'));rng=np.random.default_rng(4)
def put(at,y):
    i=int(at*sr);e=min(len(x),i+len(y));x[i:e]+=y[:e-i,None]
def crack():
    L=int(.08*sr);n=sosfilt(butter(2,[1500,7000],'band',fs=sr,output='sos'),rng.standard_normal(L));return n*np.exp(-np.arange(L)/sr*60)*.5
def pop():
    t=np.arange(int(.25*sr))/sr;return np.sin(2*np.pi*(1200*np.exp(-t*18)+250)*t)*np.exp(-t*14)*.55
def twinkle():
    y=np.zeros(int(.8*sr))
    for k,f in enumerate([1568,2093,2637,3136]):
        t=np.arange(int(.5*sr))/sr;i=int(k*.07*sr);y[i:i+len(t)]+=np.sin(2*np.pi*f*t)*np.exp(-t*8)*.12
    return y
for li in range(1,5):
    t0=s['lines'][li]['t0'];put(t0+.55,crack());put(t0+.8,crack());put(t0+1.05,crack());put(t0+1.5,pop());put(t0+1.52,twinkle())
x*=.95/np.abs(x).max();sf.write('build_eggs/mix.wav',x.astype(np.float32),sr)
