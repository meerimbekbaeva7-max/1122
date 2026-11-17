"""Male, confident ad voice in Russian (Piper) and Kyrgyz (MMS-TTS, pitched down).

usage: python3 voice.py ru|ky "текст" out.wav
"""
import subprocess, sys, wave, pathlib, tempfile
import numpy as np, soundfile as sf

ROOT = pathlib.Path(__file__).parent
lang, text, out = sys.argv[1], sys.argv[2], sys.argv[3]
raw = tempfile.mktemp(suffix=".wav")

if lang == "ru":
    from piper import PiperVoice
    from piper.config import SynthesisConfig
    v = PiperVoice.load(str(ROOT / "models/ru_RU-ruslan-medium.onnx"))
    cfg = SynthesisConfig(length_scale=0.86, noise_scale=0.8, noise_w_scale=0.9)  # brisk, lively intonation
    with wave.open(raw, "wb") as wf:
        v.synthesize_wav(text, wf, syn_config=cfg)
    pitch = 1.0           # ~125 Hz, matches the reference
else:
    import torch
    from transformers import AutoTokenizer, VitsModel
    tok = AutoTokenizer.from_pretrained("facebook/mms-tts-kir")
    m = VitsModel.from_pretrained("facebook/mms-tts-kir")
    m.config.speaking_rate = 1.0; m.config.noise_scale = 0.8; m.config.noise_scale_duration = 0.7
    torch.manual_seed(7)
    with torch.no_grad():
        w = m(**tok(text.replace("«", "").replace("»", ""), return_tensors="pt")).waveform[0].numpy()
    sf.write(raw, w, m.config.sampling_rate)
    pitch = 0.76          # MMS voice is high; bring it to ~125 Hz male

# ad-style chain: pitch (formant-preserving), de-mud, presence, compression, short room, loudness
af = (f"rubberband=pitch={pitch}:formant=preserved,"
      "highpass=f=80,equalizer=f=300:t=q:w=1:g=-3,equalizer=f=140:t=q:w=1:g=1.5,"
      "equalizer=f=3500:t=q:w=1:g=4,highshelf=f=6000:g=4,"  # bright, crisp like the reference
      "acompressor=threshold=-20dB:ratio=4:attack=5:release=80:makeup=4,"
      "aecho=0.8:0.4:25:0.06,"
      "silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_threshold=-45dB:stop_duration=0.25,"
      "loudnorm=I=-14:TP=-1.5:LRA=7")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", af, "-ar", "48000", out], check=True)
print(out)
