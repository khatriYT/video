"""Generate SCRIPT.md, SCRIPT_FINAL.txt, STORYBOARD.md and storyboard.json from storyboard_data.py.

Usage: python3 build_docs.py <project_dir>
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from storyboard_data import TITLE, STYLE, PIP, MOSQ, SCI_A, SCI_B, SECTIONS

proj = sys.argv[1]
WPM = 150
SHOTS = {"ECU": "extreme close-up", "MCU": "medium close-up (head and vest)", "MS": "medium shot (full figure)", "WS": "wide shot"}


def expand_chars(chars):
    out = []
    for c in chars:
        lc = c.lower()
        if lc.startswith("pip"):
            out.append(PIP + ("" if c == "Pip" else f" (show only: {c[4:].strip('() ')})"))
        elif "mosquito" in lc:
            out.append(MOSQ + ("" if lc == "mosquito" else f" ({c})"))
        elif c == "Scientist A":
            out.append(SCI_A)
        elif c == "Scientist B":
            out.append(SCI_B)
        else:
            out.append(f"{c}, drawn in the same stick-figure / simplified cartoon style with dot eyes and thick dark-brown outlines")
    return out


scenes, n = [], 0
for section, items in SECTIONS:
    for (narr, shot, visual, chars, bg, action, camera, anim) in items:
        n += 1
        words = len(narr.split())
        dur = round(words / WPM * 60 + 0.6, 1)
        cdesc = expand_chars(chars)
        img_prompt = (f"{visual} "
                      + (f"Characters: {'; '.join(cdesc)}. " if cdesc else "")
                      + f"Background: {bg}. Pose/action at key moment: {action}. "
                      f"Framing: {SHOTS.get(shot, shot)}, eye-level camera, subject on a rule-of-thirds line, important action inside the central 80%. "
                      f"Style: {STYLE}.")
        anim_prompt = (f"Animate the still image for {dur} s at 24 fps. Main motion: {action}. Secondary motion: {anim}. "
                       f"Camera: {camera}, eased in-out. Add subtle hand-drawn line boil (outline wobble refreshed 8 times per second). "
                       f"Characters blink once if a face is visible. Start composition = the still image; end composition = same framing after the camera move. "
                       f"Motion intensity: low to medium. Keep the illustration style, colours and character design exactly as in the image; no new objects.")
        scenes.append(dict(id=n, file=f"scene_{n:03d}", section=section, narration=narr, words=words, est_duration_s=dur,
                           shot=shot, visual=visual, characters=chars, background=bg, action=action,
                           camera=camera, animation=anim, image_prompt=img_prompt, animation_prompt=anim_prompt))

d = lambda *p: os.path.join(proj, *p)
json.dump(dict(title=TITLE, scenes=scenes), open(d("03_STORYBOARD", "storyboard.json"), "w"), indent=1)

# SCRIPT_FINAL.txt: narration only, one paragraph per section
with open(d("02_SCRIPT", "SCRIPT_FINAL.txt"), "w") as f:
    for section, _ in SECTIONS:
        f.write(" ".join(s["narration"] for s in scenes if s["section"] == section) + "\n\n")

total_words = sum(s["words"] for s in scenes)
with open(d("02_SCRIPT", "SCRIPT.md"), "w") as f:
    f.write(f"# {TITLE}\n\n")
    f.write(f"- Words: **{total_words}**; estimated runtime at {WPM} wpm: **{total_words / WPM:.1f} min**\n")
    f.write("- Narration-only version: `SCRIPT_FINAL.txt`. Every line maps to a scene in `../03_STORYBOARD/STORYBOARD.md`.\n")
    f.write("- Facts and sources: `../01_RESEARCH/TOPIC_SCIENTIFIC_RESEARCH.md`\n\n")
    for section, _ in SECTIONS:
        f.write(f"## {section}\n\n")
        for s in scenes:
            if s["section"] == section:
                f.write(f"{s['narration']}  \n*[VISUAL, scene {s['id']:03d}: {s['visual']}]*\n\n")

with open(d("03_STORYBOARD", "STORYBOARD.md"), "w") as f:
    f.write(f"# Storyboard: {TITLE}\n\n")
    f.write(f"- **{len(scenes)} scenes**; estimated total {sum(s['est_duration_s'] for s in scenes) / 60:.1f} min. Machine-readable copy: `storyboard.json`.\n")
    f.write("- Scene durations here are estimates. Produced scenes take their real length from the narration audio (see `../05_ANIMATIONS/ANIMATION_REPORT.md`).\n")
    f.write("- Every image prompt is self-contained and repeats the full style and character descriptions on purpose.\n\n")
    f.write("| # | Section | Shot | Narration | Est. s |\n|---|---|---|---|---|\n")
    for s in scenes:
        f.write(f"| {s['id']:03d} | {s['section']} | {s['shot']} | {s['narration']} | {s['est_duration_s']} |\n")
    f.write("\n---\n\n")
    for s in scenes:
        f.write(f"## Scene {s['id']:03d} ({s['section']})\n\n")
        f.write(f"- **Narration:** \"{s['narration']}\"\n- **Estimated duration:** {s['est_duration_s']} s\n")
        f.write(f"- **Visual:** {s['visual']}\n- **Characters:** {', '.join(s['characters']) or 'none'}\n")
        f.write(f"- **Background:** {s['background']}\n- **Action:** {s['action']}\n- **Camera:** {s['shot']}, {s['camera']}\n\n")
        f.write(f"**Image prompt**\n\n> {s['image_prompt']}\n\n**Animation prompt**\n\n> {s['animation_prompt']}\n\n")
print(len(scenes), "scenes,", total_words, "words")
