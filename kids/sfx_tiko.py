"""Spike dings, riser into RAINBOW, subscribe pop/click/chime (Tiko's Rainbow Spikes)."""
import numpy as np, soundfile as sf, json
from scipy.signal import butter, sosfilt
x,sr=sf.read('build_tiko/mix.wav');s=json.load(open('build_tiko/song.json'))
def put(at,y,ch=None):
    i=int(at*sr);e=min(len(x),i+len(y));x[i:e]+=(y[:e-i,None] if y.ndim==1 else y[:e-i])
def ding(f):
    t=np.arange(int(.35*sr))/sr;return (np.sin(2*np.pi*f*t)+.3*np.sin(4*np.pi*f*t))*np.exp(-t*9)*.12
L=s['lines'];lt=[L[1]['words'][i]['t0'] for i in range(4)]+[L[2]['words'][0]['t0'],L[2]['words'][2]['t0']]
for i,t in enumerate(lt): put(t,ding([1047,1175,1319,1397,1568,1760][i]))
t=np.arange(int(1.0*sr))/sr;ri=sosfilt(butter(2,[800,6000],'band',fs=sr,output='sos'),np.random.default_rng(1).standard_normal(len(t)))*np.linspace(0,1,len(t))**2*.16
put(L[2]['words'][3]['t0']-.9,ri)
sfx,_=sf.read('brand/subscribe_sfx.wav');put(16.0,sfx*.8)
x=np.tanh(x*1.1)/np.tanh(1.1);x*=.95/np.abs(x).max();sf.write('build_tiko/mix.wav',x.astype(np.float32),sr);print('sfx ok')
