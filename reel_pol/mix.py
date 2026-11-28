import json, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly
SR=48000; rng=np.random.default_rng(5); D='/home/user/1122/reel_pol/'
tl=json.load(open(D+'timeline.json')); TOTAL=tl['total']; TALK=tl['talk']; cuts=tl['cuts']; N=int(TOTAL*SR)
v,sr=sf.read(D+'a_voice.wav'); v=v.mean(1) if v.ndim>1 else v; v=v[int(.45*sr):int(.45*sr)+int(TALK*sr)]
vox=np.zeros(N); vox[:len(v)]=v; fade=int(.08*SR); vox[len(v)-fade:len(v)]*=np.linspace(1,0,fade)
def add(buf,at,y,a=1.):
    i=int(at*SR);e=min(N,i+len(y))
    if 0<=i<N: buf[i:e]+=y[:e-i]*a
hp=lambda x,f:sosfilt(butter(2,f,'high',fs=SR,output='sos'),x); lp=lambda x,f:sosfilt(butter(2,f,'low',fs=SR,output='sos'),x)
bp=lambda x,a,b:sosfilt(butter(2,[a,b],'band',fs=SR,output='sos'),x); mhz=lambda m:440*2**((m-69)/12)
def kick(a=.8):x=np.arange(int(.3*SR))/SR;return np.sin(2*np.pi*(160*np.exp(-x*30)+46)*x)*np.exp(-x*9)*a
def clap(a=.3):n=int(.2*SR);return bp(rng.standard_normal(n),1000,7000)*np.exp(-np.arange(n)/SR*28)*a
def hat(a=.05):n=int(.04*SR);return hp(rng.standard_normal(n),8000)*np.exp(-np.arange(n)/SR*90)*a
def pluck(f,d,a=.08):x=np.arange(int(d*SR))/SR;y=sum(np.sin(2*np.pi*f*k*x)/k for k in(1,2,3));return lp(y,2600)*np.exp(-x*6)*a
def pad(fs,d,a=.05):x=np.arange(int(d*SR))/SR;y=sum(np.sin(2*np.pi*f*x+np.sin(2*np.pi*.3*x)*.4) for f in fs);env=np.minimum(1,np.minimum(x/.3,(d-x)/.4));return lp(y,1800)*env*a
def whoosh(d=.45,a=.16):
    n=int(d*SR);w=rng.standard_normal(n);o=np.zeros(n)
    for j in range(8):s0,s1=j*n//8,(j+1)*n//8;f=400+6000*(j/8)**2;o[s0:s1]=bp(w,f*.7,min(f*1.4,20000))[s0:s1]
    return o*np.sin(np.linspace(0,np.pi,n))**2*a
BPM=118;B=60/BPM;prog=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]
mus=np.zeros(N);b=0;k=0
while b<TOTAL-.3:
    c=prog[(k//8)%4]
    if k%8==0:add(mus,b,pad([mhz(n) for n in c],B*4))
    if k%2==0:add(mus,b,kick(.7 if k%4==0 else .5))
    if k%4==2:add(mus,b,clap())
    add(mus,b+B/4,hat(.045));add(mus,b,hat(.025))
    nb=int(B/2*SR*.9);xb=np.arange(nb)/SR;add(mus,b,np.sin(2*np.pi*mhz(c[0]-24)*xb)*np.exp(-xb*6)*.32)
    if k%2==1:add(mus,b,pluck(mhz(c[(k//2)%3]+12),.3))
    b+=B/2;k+=1
mus/=np.abs(mus).max()
sfx=np.zeros(N)
for c in cuts[:-1]:add(sfx,c-.22,whoosh())
x=np.arange(int(1.1*SR))/SR;imp=np.sin(2*np.pi*(60*np.exp(-x*4)+32)*x)*np.exp(-x*2.6)
add(sfx,0,imp,.6);add(sfx,TALK,imp,.7)
sub,ssr=sf.read('/home/user/1122/kids/brand/subscribe_sfx.wav');sub=sub.mean(1) if sub.ndim>1 else sub
if ssr!=SR:sub=resample_poly(sub,SR,ssr)
add(sfx,cuts[-2]+.6,sub,.7)
t=np.arange(N)/SR
# music level: low under the speaker, quiet bed in the voice-over slot, up on the end card
lev=np.where(t<TALK,.16,np.where(t<cuts[-2],.22,.5))
lev=np.convolve(lev,np.ones(4800)/4800,'same')
def master(m):
    m=m*np.clip(t/.04,0,1)*np.clip((TOTAL-t)/.6,0,1);st=np.stack([m,m],1);st=np.tanh(st*1.05)/np.tanh(1.05);return st*.95/np.abs(st).max()
vn=vox/np.abs(vox).max()*.9
sf.write(D+'mix_music.wav',master(vn+mus*lev+sfx*.6).astype(np.float32),SR)
sf.write(D+'mix_nomusic_slot.wav',master(vn+mus*np.where(t<TALK,lev,np.where(t<cuts[-2],0,lev))+sfx*.6).astype(np.float32),SR)
sf.write(D+'music_only.wav',master(mus*.6).astype(np.float32),SR)
print('ok',TOTAL)
