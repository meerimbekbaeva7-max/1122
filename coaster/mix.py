"""Voice + music + SFX for the 30 s roller-coaster video -> build/mix.wav"""
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly
SR=48000; DUR=30.0; N=int(SR*DUR); t=np.arange(N)/SR; rng=np.random.default_rng(1)
TL=[[0,4],[4,8.5],[8.5,12.5],[12.5,17],[17,21.5],[21.5,25.5],[25.5,30]]
DROP=TL[3][0]+1.35
lp=lambda x,f:sosfilt(butter(2,f,'low',fs=SR,output='sos'),x)
hp=lambda x,f:sosfilt(butter(2,f,'high',fs=SR,output='sos'),x)
bp=lambda x,a,b:sosfilt(butter(2,[a,b],'band',fs=SR,output='sos'),x)
note=lambda m:440*2**((m-69)/12)
def add(buf,at,x):
    s=int(at*SR); e=min(N,s+len(x)); buf[s:e]+=x[:e-s]

voice=np.zeros(N)
starts=[a+.35 for a,_ in TL]; starts[3]=TL[3][0]+.1
for i,st in enumerate(starts):
    w,sr=sf.read(f'build/vo_{i}.wav'); w=w.mean(1) if w.ndim>1 else w
    add(voice,st,resample_poly(w,SR,sr))
voice*=0.9/np.abs(voice).max()

music=np.zeros(N)
bpm=124; beat=60/bpm
chords=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]  # Am F C G
def kick(a=.5):
    L=int(.35*SR);tt=np.arange(L)/SR;return np.sin(2*np.pi*(55*np.exp(-tt*9)+45)*tt)*np.exp(-tt*8)*a
def hat(a=.08):
    L=int(.05*SR);return hp(rng.standard_normal(L),7000)*np.exp(-np.arange(L)/SR*80)*a
def pluck(f,a=.06,d=.25):
    L=int(d*SR);tt=np.arange(L)/SR;return (np.sin(2*np.pi*f*tt)+.4*np.sin(4*np.pi*f*tt)+.2*np.sin(6*np.pi*f*tt))*np.exp(-tt*14)*a
# light intro groove (scene 0-1), lift tension (2), silence, full drop (3-5), outro (6)
for k,b in enumerate(np.arange(0,DUR,beat/2)):
    ch=chords[int(b/(beat*8))%4]
    if b<TL[2][0]:          # intro: soft plucks only
        add(music,b,pluck(note(ch[k%3]+12),.05))
        if k%4==0: add(music,b,kick(.25))
    elif b<DROP-1.3:        # lift: pulse builds
        add(music,b,pluck(note(ch[k%3]+12),.04))
        if k%2==0: add(music,b,kick(.18+.25*(b-TL[2][0])/(DROP-TL[2][0])))
    elif b<DROP:            # the silent second
        pass
    elif b<TL[6][1]-.6:     # full energy
        add(music,b,pluck(note(ch[k%3]+12),.07)); add(music,b,pluck(note(ch[(k+1)%3]+24),.03))
        if k%2==0: add(music,b,kick(.55))
        add(music,b+beat/4,hat(.07 if k%2 else .04))
        if k%8==4:
            L=int(.2*SR);add(music,b,bp(rng.standard_normal(L),900,5000)*np.exp(-np.arange(L)/SR*20)*.25)  # snare
# bass pad under everything except the silent second
for i,ch in enumerate(chords*4):
    a=i*beat*8; 
    if a>=DUR: break
    env=np.clip((t-a)/.3,0,1)*np.clip((a+beat*8+.3-t)/.3,0,1)
    music+=.05*np.sin(2*np.pi*note(ch[0]-12)*t)*env
music*=np.where((t>DROP-1.3)&(t<DROP),0.1,1.0)
# lift chain clicks
for c in np.arange(TL[1][0]+.3,DROP-1.3,0.13):
    L=int(.02*SR);add(music,c,bp(rng.standard_normal(L),1500,6000)*np.exp(-np.arange(L)/SR*300)*.35)
# riser into drop, then impact + wind
L=int(2.5*SR);ri=np.zeros(L);n=rng.standard_normal(L)
for j in range(10):
    a,b=j*L//10,(j+1)*L//10;f=400+6000*(j/10)**2;ri[a:b]=bp(n,f*.7,min(f*1.4,20000))[a:b]
add(music,DROP-2.6,ri*np.linspace(0,1,L)**2*.25)
Lb=int(1.6*SR);tb=np.arange(Lb)/SR
add(music,DROP,(np.sin(2*np.pi*(65*np.exp(-tb*4)+32)*tb)*np.exp(-tb*2.5)+lp(rng.standard_normal(Lb),900)*np.exp(-tb*8)*.5)*.9)
Lw=int(8*SR);wind=bp(rng.standard_normal(Lw),300,3000)*.12;wind*=np.minimum(1,np.arange(Lw)/(.3*SR))*np.minimum(1,(Lw-np.arange(Lw))/(2*SR))
add(music,DROP,wind)
# loop whoosh
for w in (TL[4][0]+.4,TL[4][0]+1.6):
    L=int(.8*SR);add(music,w,bp(rng.standard_normal(L),500,4000)*np.sin(np.linspace(0,np.pi,L))*.25)
music*=0.8/np.abs(music).max()
# duck under voice
k=int(.08*SR);ve=np.convolve(np.abs(voice),np.ones(k)/k,'same');music*=1-.55*np.clip(ve/(ve.max()*.25),0,1)
music*=np.clip((DUR-t)/1.0,0,1)
d=int(.012*SR);L_=voice+music*.6;R_=voice+np.concatenate([np.zeros(d),music[:-d]])*.6
st=np.tanh(np.stack([L_,R_],1)*1.2)/np.tanh(1.2);st*=.95/np.abs(st).max()
sf.write('build/mix.wav',st.astype(np.float32),SR);print('mix ok')
