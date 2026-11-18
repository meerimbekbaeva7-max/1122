"""Star drop whoosh, catch 'pop', count chimes, YAY sparkle, subscribe SFX (Count with Tiko)."""
import numpy as np, soundfile as sf, json
from scipy.signal import butter, sosfilt
x,sr=sf.read('build_count/mix.wav');s=json.load(open('build_count/song.json'));L=s['lines'];rng=np.random.default_rng(3)
def put(at,y):
    i=int(at*sr);e=min(len(x),i+len(y));x[i:e]+=(y[:e-i,None] if y.ndim==1 else y[:e-i])
def tone(f,d=.3,a=.12,dec=9):
    t=np.arange(int(d*sr))/sr;return (np.sin(2*np.pi*f*t)+.3*np.sin(4*np.pi*f*t))*np.exp(-t*dec)*a
def whoosh(d=.5):
    n=sosfilt(butter(2,[1500,6000],'band',fs=sr,output='sos'),rng.standard_normal(int(d*sr)));return n*np.sin(np.linspace(0,np.pi,len(n)))**2*.06
catch=[L[1]['words'][i]['t0'] for i in range(3)]+[L[2]['words'][i]['t0'] for i in range(2)]
notes=[1047,1175,1319,1397,1568]
for i,c in enumerate(catch): put(c-.55,whoosh());put(c,tone(notes[i],.35,.13))
for i,w in enumerate(L[3]['words'][:5]): put(w['t0'],tone(notes[i]*2,.2,.06,14))
for k,f in enumerate([1568,2093,2637,3136]): put(L[3]['words'][5]['t0']+k*.06,tone(f,.5,.08,7))
sfx,_=sf.read('brand/subscribe_sfx.wav');put(16.0,sfx*.8)
x=np.tanh(x*1.1)/np.tanh(1.1);x*=.95/np.abs(x).max();sf.write('build_count/mix.wav',x.astype(np.float32),sr);print('sfx ok')
