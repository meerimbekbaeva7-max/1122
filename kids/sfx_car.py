"""Horn in the intro + engine rev before the chorus (Beep Beep car)."""
import numpy as np, soundfile as sf, json
from scipy.signal import butter, sosfilt
x,sr=sf.read('build_car/mix.wav');s=json.load(open('build_car/song.json'))
def horn(d=.2):
    t=np.arange(int(d*sr))/sr;y=np.sign(np.sin(2*np.pi*415*t))*.5+np.sign(np.sin(2*np.pi*523*t))*.5
    y=sosfilt(butter(2,2500,'low',fs=sr,output='sos'),y);return y*np.minimum(1,t/.01)*np.minimum(1,(d-t)/.03)*.25
def rev(d=1.1):
    t=np.arange(int(d*sr))/sr;f=70+170*(t/d)**.6;ph=2*np.pi*np.cumsum(f)/sr;y=2*((ph/(2*np.pi))%1)-1
    y=sosfilt(butter(2,900,'low',fs=sr,output='sos'),y);return y*np.sin(np.pi*t/d)**.5*.22
def put(at,y):
    i=int(at*sr);e=min(len(x),i+len(y));x[i:e]+=y[:e-i,None]
put(1.4,horn());put(1.75,horn());put(s['lines'][4]['t0']-.5,rev())
x*=.95/np.abs(x).max();sf.write('build_car/mix.wav',x.astype(np.float32),sr)
