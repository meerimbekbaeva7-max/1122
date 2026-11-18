"""Guide tracks for a real singer: 4-click count-in (2 bars at song tempo... 4 beats), instrumental, melody on piano, click.
usage: python3 make_guide.py <build_dir> <name> <chords.json> [music env...]"""
import sys, json, shutil, subprocess, os, pathlib, numpy as np, soundfile as sf
bd, name, chords = sys.argv[1], sys.argv[2], sys.argv[3]
SR=48000
tmp=pathlib.Path('/tmp/claude-0/-home-user-1122/baafca0a-3286-5745-8381-c2f1cff59929/scratchpad/guide_'+name); shutil.rmtree(tmp,ignore_errors=True); tmp.mkdir(parents=True)
shutil.copy(f'{bd}/song.json',tmp/'song.json'); v,sr=sf.read(f'{bd}/vocals.wav'); sf.write(tmp/'vocals.wav',np.zeros_like(v),sr)
subprocess.run(['python3','music.py',str(tmp),chords],check=True,stdout=subprocess.DEVNULL)
inst,_=sf.read(tmp/'mix.wav'); inst=inst.mean(1) if inst.ndim>1 else inst
song=json.load(open(f'{bd}/song.json')); B=song['beat']; IB=round(song['intro']/B)
NOTE={n:i for i,n in enumerate("C C# D D# E F F# G G# A A# B".split())}
hz=lambda s:440*2**((NOTE[s[:-1]]+12*(int(s[-1])+1)-69)/12)
mel=np.zeros(len(inst))
def piano(f,d):
    t=np.arange(int(d*SR))/SR;return (np.sin(2*np.pi*f*t)+.4*np.sin(4*np.pi*f*t)+.15*np.sin(6*np.pi*f*t))*np.exp(-t*2.5)*np.minimum(1,(d-t)/.03)
for li,(tag,ws) in enumerate(song['song']):
    b=IB+8*li
    for w in ws:
        if w is None: continue
        for n,d in w[1]:
            y=piano(hz(n),d*B*.95);i=int(b*B*SR);mel[i:i+len(y)]+=y[:len(mel)-i];b+=d
def click(hi):
    t=np.arange(int(.05*SR))/SR;return np.sin(2*np.pi*(1500 if hi else 1000)*t)*np.exp(-t*80)*.5
cl=np.zeros(len(inst))
for k in range(int(song['duration']/B)):
    y=click(k%4==0);i=int(k*B*SR);cl[i:i+len(y)]+=y[:len(cl)-i]
pre=np.zeros(int(4*B*SR))
for k in range(4):
    y=click(True)*1.2;i=int(k*B*SR);pre[i:i+len(y)]+=y
def out(fn,parts):
    x=np.concatenate([pre,sum(parts)]);x*=.9/np.abs(x).max();sf.write(fn,np.stack([x,x],1).astype(np.float32),SR)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',fn,'-b:a','192k',fn.replace('.wav','.mp3')],check=True);os.remove(fn)
out(f'voice_kit/{name}_GUIDE_with_melody.wav',[inst*.6,mel*.5,cl*.25])
out(f'voice_kit/{name}_MINUS_instrumental.wav',[inst*.8,cl*.15])
print(name,'ok',round(song['duration'],2),'s + count-in',round(4*B,2),'s')
