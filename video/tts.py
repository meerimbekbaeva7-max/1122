"""Generate the Kyrgyz voiceover with Meta MMS-TTS (facebook/mms-tts-kir).

Each line is synthesized separately, trimmed of silence, and written to
build/vo_<n>.wav. Timings (seconds) go to build/timings.json so the motion
graphics can be synced to the voice.
"""
import json
import pathlib

import numpy as np
import soundfile as sf
import torch
from transformers import AutoTokenizer, VitsModel

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "build"
OUT.mkdir(exist_ok=True)

lines = json.loads((ROOT / "lines.json").read_text(encoding="utf-8"))

tok = AutoTokenizer.from_pretrained("facebook/mms-tts-kir")
model = VitsModel.from_pretrained("facebook/mms-tts-kir")
model.config.speaking_rate = 1.05   # a touch brisker, keeps the ad snappy
model.config.noise_scale = 0.6      # more natural prosody variation
model.config.noise_scale_duration = 0.7
sr = model.config.sampling_rate


def trim(wav, thresh=0.01, pad=0.04):
    idx = np.where(np.abs(wav) > thresh)[0]
    if len(idx) == 0:
        return wav
    a = max(idx[0] - int(pad * sr), 0)
    b = min(idx[-1] + int(pad * sr), len(wav))
    return wav[a:b]


info = []
for i, text in enumerate(lines):
    clean = text.replace("«", "").replace("»", "")
    inputs = tok(clean, return_tensors="pt")
    torch.manual_seed(7 + i)
    with torch.no_grad():
        wav = model(**inputs).waveform[0].numpy()
    wav = trim(wav)
    wav = wav / (np.abs(wav).max() + 1e-9) * 0.9
    path = OUT / f"vo_{i}.wav"
    sf.write(path, wav, sr)
    info.append({"text": text, "dur": round(len(wav) / sr, 3)})
    print(i, info[-1])

(OUT / "vo_info.json").write_text(json.dumps({"sr": sr, "lines": info}, ensure_ascii=False, indent=1))
