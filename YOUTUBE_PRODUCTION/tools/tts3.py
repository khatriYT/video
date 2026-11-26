#!/usr/bin/env python3
"""Narration per scene with Kokoro (local neural TTS), new project layout (episode 3+).

Usage: python3 tools/tts3.py <project_dir> <kokoro_model_dir> [first last]
Reads 06_Storyboard/storyboard.json; writes 10_Audio/narration/SC###.wav + durations.json.
Existing files are skipped (delete one to regenerate it). Pronunciation respellings are applied
to the TTS input only; subtitles keep the real spelling.
"""
import json
import os
import sys

import soundfile as sf
from kokoro_onnx import Kokoro

RESPELL = {
    "Rüppell's": "Rupel's",
    "Gyps": "Jips",
    "Sudarshan": "Soodarshan",
}

proj, model_dir = sys.argv[1], sys.argv[2]
a, b = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (1, 10 ** 6)
sb = json.load(open(os.path.join(proj, "06_Storyboard", "storyboard.json")))
voice = sb.get("voice", "am_michael")
k = Kokoro(os.path.join(model_dir, "kokoro-v1.0.onnx"), os.path.join(model_dir, "voices-v1.0.bin"))
outdir = os.path.join(proj, "10_Audio", "narration")
os.makedirs(outdir, exist_ok=True)
durf = os.path.join(outdir, "durations.json")
durs = json.load(open(durf)) if os.path.exists(durf) else {}
for s in sb["scenes"]:
    if not (a <= s["id"] <= b):
        continue
    out = os.path.join(outdir, s["file"] + ".wav")
    if not os.path.exists(out):
        text = s["narration"]
        for k_, v in RESPELL.items():
            text = text.replace(k_, v)
        audio, sr = k.create(text, voice=voice, speed=1.0, lang="en-us")
        sf.write(out, audio, sr)
    info = sf.info(out)
    durs[s["file"]] = round(info.frames / info.samplerate, 3)
    print(s["file"], durs[s["file"]], flush=True)
    json.dump(durs, open(durf, "w"), indent=1)
print("TOTAL narration s", round(sum(durs.values()), 1))
