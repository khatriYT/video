"""SFX cue sheet for episode 2. Cues are derived automatically from each scene's animated on-screen text,
plus a soft bee buzz on scenes where bees fly. Levels follow the episode-1 fix (SFX well below the voice)."""
import json, os

SFX_MASTER = 0.28
MUSIC_FILE = "music_bed_sunny_84bpm.wav"
_PROJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "01_PROJECTS", "what_if_all_bees_disappeared")
_SB = {s["id"]: s for s in json.load(open(os.path.join(_PROJ, "03_STORYBOARD", "storyboard.json")))["scenes"]}
BUZZ_SCENES = {12, 14, 17, 18, 19, 25, 28, 32, 55, 65, 73, 91, 93, 94, 96, 103, 104}


def cues(i, T):
    sc = _SB.get(i)
    if not sc:
        return []
    c = []
    spec = (sc.get("onscreen") or "").split("|")
    style = spec[0] if spec and spec[0] else ""
    if style == "stamp":
        c.append(("stamp", 0.3 * T, 0.7, None))
    elif style == "count":
        c += [("tick", 0.08 * T + k * 0.09, 0.5, None) for k in range(int(min(1.6, 0.5 * T) / 0.09))]
        c.append(("pop", 0.08 * T, 0.5, None))
    elif style in ("pop", "title"):
        n = len(spec[2].split()) if len(spec) > 2 else 1
        c += [("pop", (0.1 * T if style == "pop" else 0.25 * T) + k * 0.12, 0.45, None) for k in range(min(n, 4))]
    elif style == "list":
        c += [("pop", 0.1 * T + k * 0.45, 0.45, None) for k in range(len([x for x in spec[2:] if x]))]
    elif style == "label":
        c.append(("whoosh", 0.06 * T, 0.4, None))
    elif style == "type":
        c += [("type_key", 0.05 * T + k * 0.07, 0.5, None) for k in range(int(0.75 * T / 0.07))]
    if i in BUZZ_SCENES:
        c.append(("bee_buzz", 0.0, 0.18, T))
    return c
