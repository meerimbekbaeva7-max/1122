"""timeline.json + lines -> data.js (timeline and per-character mouth envelopes at 30 fps)"""
import json,numpy as np,soundfile as sf
T=json.load(open('timeline.json'));SR=48000;FPS=30;N=int(T['duration']*FPS)+1
env={'tiko':np.zeros(N),'lulu':np.zeros(N)}
for s in T['segments']:
    items=[(s['who'],s,0)] if 'file' in s else [('both',l,.25) for l in s.get('lines',[])]
    for who,it,off in items:
        y,_=sf.read('lines/'+it['file']);hop=SR//FPS
        e=np.array([np.sqrt(np.mean(y[i:i+hop]**2)) for i in range(0,len(y),hop)]);e=np.clip(e/(np.percentile(e,95)+1e-9),0,1)
        f0=int((it['t0']+off)*FPS)
        for spk in (['tiko','lulu'] if who=='both' else [who]):
            seg=env[spk][f0:f0+len(e)];env[spk][f0:f0+len(e)]=np.maximum(seg,e[:len(seg)])
open('data.js','w').write('window.TL='+json.dumps(T)+';window.ENV='+json.dumps({k:[round(float(v),2) for v in a] for k,a in env.items()})+';')
print('data ok',N,'frames')
