"""Narration per scene with Kokoro (local neural TTS).

Usage: python3 tts.py <project_dir> <model_dir> [first_id last_id] [voice]
Writes 06_AUDIO/narration/scene_###.wav and durations.json. Skips files that already exist.
"""
import json, os, sys
import soundfile as sf
from kokoro_onnx import Kokoro

proj, model_dir = sys.argv[1], sys.argv[2]
a, b = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (1, 10**6)
voice = sys.argv[5] if len(sys.argv) > 5 else "am_michael"
k = Kokoro(os.path.join(model_dir, "kokoro-v1.0.onnx"), os.path.join(model_dir, "voices-v1.0.bin"))
sb = json.load(open(os.path.join(proj, "03_STORYBOARD", "storyboard.json")))
outdir = os.path.join(proj, "06_AUDIO", "narration")
durf = os.path.join(outdir, "durations.json")
durs = json.load(open(durf)) if os.path.exists(durf) else {}
for s in sb["scenes"]:
    if not (a <= s["id"] <= b):
        continue
    out = os.path.join(outdir, s["file"] + ".wav")
    if not os.path.exists(out):
        audio, sr = k.create(s["narration"], voice=voice, speed=1.0, lang="en-us")
        sf.write(out, audio, sr)
    info = sf.info(out)
    durs[s["file"]] = round(info.frames / info.samplerate, 3)
    print(s["file"], durs[s["file"]], flush=True)
json.dump(durs, open(durf, "w"), indent=1)
