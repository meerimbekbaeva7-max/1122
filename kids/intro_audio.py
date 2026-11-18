"""Rainbow Tots 5-second intro: xylophone glissando, pops, jingle backing, ta-da. -> build_intro/mix.wav"""
import json, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
SR=48000; DUR=5.0; N=int(SR*DUR); rng=np.random.default_rng(7)
song=json.load(open('build_intro/song.json')); B=song['beat']; T0=song['intro']   # 1.667 s
NOTE={n:i for i,n in enumerate("C C# D D# E F F# G G# A A# B".split())}
hz=lambda s:440*2**((NOTE[s[:-1]]+12*(int(s[-1])+1)-69)/12); mhz=lambda m:440*2**((m-69)/12)
mus=np.zeros((N,)); 
def add(at,y,a=1.0):
    i=int(at*SR);e=min(N,i+len(y))
    if i<N: mus[i:e]+=y[:e-i]*a
def xylo(f,d=.6,a=.2):
    t=np.arange(int(d*SR))/SR;return (np.sin(2*np.pi*f*t)+.5*np.sin(2*np.pi*f*3.98*t)*np.exp(-t*30)+.25*np.sin(4*np.pi*f*t))*np.exp(-t*6)*a
def uke(fs,d,a=.07):
    L=int(d*SR);t=np.arange(L)/SR;y=np.zeros(L)
    for j,f in enumerate(fs):
        o=int(j*.012*SR);tl=t[:L-o];y[o:]+=(np.sin(2*np.pi*f*tl)+.5*np.sin(4*np.pi*f*tl)+.3*np.sin(6*np.pi*f*tl))*np.exp(-tl*5)
    return y*a
def kick(a=.5):
    t=np.arange(int(.3*SR))/SR;return np.sin(2*np.pi*(150*np.exp(-t*25)+50)*t)*np.exp(-t*10)*a
def clap(a=.2):
    L=int(.18*SR);n=sosfilt(butter(2,[900,6000],'band',fs=SR,output='sos'),rng.standard_normal(L));return n*np.exp(-np.arange(L)/SR*25)*a
def pop(f0=900,a=.35):
    t=np.arange(int(.18*SR))/SR;return np.sin(2*np.pi*(f0*np.exp(-t*18)+250)*t)*np.exp(-t*16)*a
def boing(a=.3):
    t=np.arange(int(.45*SR))/SR;f=180+520*(1-np.exp(-t*9));ph=2*np.pi*np.cumsum(f)/SR;return np.sin(ph+3*np.sin(2*np.pi*14*t)*np.exp(-t*4))*np.exp(-t*5)*a
# 1) glissando while the rainbow draws
for k,n in enumerate(["C5","D5","E5","G5","A5","C6","D6","E6","G6"]): add(k*.07,xylo(hz(n),.7,.15))
# 2) character entrances
add(.5,pop(1100));add(.62,pop(1400,.2));add(.9,boing())
# 3) jingle backing from T0: C - F - G - (ta-da) C
CH={"C":[60,64,67,72],"F":[60,65,69,72],"G":[59,62,67,71]}
for k,c in enumerate(["C","F","G"]):
    at=T0+k*2*B;add(at,uke([mhz(m) for m in CH[c]],2*B));add(at,np.sin(2*np.pi*mhz(CH[c][0]-24)*np.arange(int(2*B*SR))/SR)*np.exp(-np.arange(int(2*B*SR))/SR*3)*.3)
for b in range(5): add(T0+b*B,kick() if b%2==0 else clap())
for b in range(10): add(T0+b*B/2,sosfilt(butter(2,6000,'high',fs=SR,output='sos'),rng.standard_normal(int(.05*SR)))*np.exp(-np.arange(int(.05*SR))/SR*60)*.04)
# 4) ta-da at the end of "Tots!"
TD=T0+5*B
for m in [48,60,64,67,72,76,79,84]: add(TD,xylo(mhz(m),1.25,.07))
add(TD,uke([mhz(m) for m in [60,64,67,72]],1.25,.1));add(TD,kick(.7))
crash=sosfilt(butter(2,4000,'high',fs=SR,output='sos'),rng.standard_normal(int(1.2*SR)))*np.exp(-np.arange(int(1.2*SR))/SR*3.5)*.12;add(TD,crash)
for k,f in enumerate([1568,2093,2637,3136,4186]): add(TD+.1+k*.06,xylo(f,.6,.06))
mus/=np.abs(mus).max()
vox,_=sf.read('build_intro/vocals.wav');vox=np.pad(vox,(0,max(0,N-len(vox))))[:N]
ve=np.convolve(np.abs(vox),np.ones(2400)/2400,'same');mus*=1-.4*np.clip(ve/(np.percentile(ve,99)+1e-9),0,1)
t=np.arange(N)/SR;mix=vox*1.0+mus*.55;mix*=np.clip((DUR-t)/.25,0,1)
d=int(.01*SR);st=np.stack([mix,vox+np.concatenate([np.zeros(d),mus[:-d]])*.55*np.clip((DUR-t)/.25,0,1)],1)
st=np.tanh(st*1.2)/np.tanh(1.2);st*=.95/np.abs(st).max();sf.write('build_intro/mix.wav',st.astype(np.float32),SR);print('intro audio ok')
