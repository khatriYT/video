#!/usr/bin/env python3
"""Final QC for an episode export.

Usage: python3 tools/vulture3d/qc.py <project_dir> <export.mp4>
Checks: every storyboard scene has a clip; export resolution/fps/codec/duration; audio present;
black segments (blackdetect); integrated loudness (ebur128); writes a one-frame-per-scene contact sheet
and 12_Exports/QC_REPORT.md.
"""
import json
import os
import re
import subprocess
import sys

proj, mp4 = sys.argv[1], sys.argv[2]
P = lambda *x: os.path.join(proj, *x)
sb = json.load(open(P("06_Storyboard", "storyboard.json")))["scenes"]
timing = json.load(open(P("09_Animation", "scene_timing.json")))
rep = ["# QC Report", "", f"File: `{os.path.relpath(mp4, proj)}`", ""]
ok = True

missing = [s["file"] for s in sb if not os.path.exists(P("09_Animation", s["file"] + ".mp4"))]
rep.append(f"- Scenes in storyboard: {len(sb)}; missing clips: {missing or 'none'}")
ok &= not missing

pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", mp4],
                               capture_output=True, text=True).stdout)
v = next(s for s in pr["streams"] if s["codec_type"] == "video")
a = [s for s in pr["streams"] if s["codec_type"] == "audio"]
dur = float(pr["format"]["duration"])
exp = sum(timing[s["file"]]["duration"] for s in sb)
rep.append(f"- Video: {v['codec_name']} {v['width']}x{v['height']} @ {v['r_frame_rate']} fps, pix_fmt {v.get('pix_fmt')}")
rep.append(f"- Audio: {', '.join(x['codec_name'] + ' ' + x.get('sample_rate', '') + ' Hz ' + str(x.get('channels')) + 'ch' for x in a) or 'NONE'}")
rep.append(f"- Duration: {dur:.2f} s ({int(dur // 60)}:{dur % 60:05.2f}); sum of scene clips {exp:.2f} s")
ok &= (v["width"], v["height"]) == (1920, 1080) and bool(a) and abs(dur - exp) < 1.0

bd = subprocess.run(["ffmpeg", "-hide_banner", "-i", mp4, "-vf", "blackdetect=d=0.4:pix_th=0.06", "-an", "-f", "null", "-"],
                    capture_output=True, text=True).stderr
blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", bd)
rep.append(f"- Black segments ≥0.4 s: {[(round(float(x), 2), round(float(y), 2)) for x, y in blacks] or 'none'}")
ok &= not blacks

lo = subprocess.run(["ffmpeg", "-hide_banner", "-i", mp4, "-af", "ebur128=peak=true", "-vn", "-f", "null", "-"],
                    capture_output=True, text=True).stderr
I = re.findall(r"I:\s+(-?[\d.]+) LUFS", lo)
tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", lo)
rep.append(f"- Integrated loudness: {I[-1] if I else '?'} LUFS (target -14); true peak {tp[-1] if tp else '?'} dBFS")

# one frame per scene contact sheet
tmp = P("12_Exports", "_qc_frames")
os.makedirs(tmp, exist_ok=True)
t0 = 0.0
frames = []
for s in sb:
    d = timing[s["file"]]["duration"]
    out = os.path.join(tmp, s["file"] + ".jpg")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t0 + d * 0.7:.2f}", "-i", mp4, "-frames:v", "1",
                    "-vf", "scale=384:216", out])
    frames.append(out)
    t0 += d
sheet = P("12_Exports", "QC_contact_sheet.jpg")
subprocess.run(["montage", *frames, "-geometry", "384x216+2+2", "-tile", "8x", "-background", "#111", sheet])
for f in frames:
    os.remove(f)
os.rmdir(tmp)
rep.append(f"- Contact sheet (one frame per scene, 70% through): `12_Exports/{os.path.basename(sheet)}`")
rep += ["", f"**Automated result: {'PASS' if ok else 'CHECK FAILURES ABOVE'}**", ""]
open(P("12_Exports", "QC_REPORT.md"), "w").write("\n".join(rep) + "\n")
print("\n".join(rep))
