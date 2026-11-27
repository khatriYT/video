"""Make-style compositing: re-compose every scene whose inputs are complete and newer than its clip.
Inputs: plate (png/json/depth), character or full-render frames, swarm sprite atlas, the compositing code,
storyboard and timing. Run repeatedly while renders finish: python3 compose_sync.py <project> [--once]"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CODE = ["tools/bats3d/compose4.py", "tools/bats3d/cards4.py", "tools/vulture3d/cards.py", "tools/bats3d/shots4.py"]


def newest(path):
    if os.path.isfile(path):
        return os.path.getmtime(path)
    if os.path.isdir(path):
        return max([os.path.getmtime(path)] + [os.path.getmtime(os.path.join(path, f)) for f in os.listdir(path)])
    return 0.0


def shots():
    src = open(os.path.join(ROOT, "tools/bats3d/shots4.py")).read().replace("from mathutils import Vector",
                                                                          "Vector=tuple")
    ns = {}
    exec(src, ns)
    return ns["SHOTS"]


def stale(proj):
    P = os.path.join(ROOT, proj)
    R = os.path.join(P, "08_Scenes", "renders4")
    S = shots()
    sb = json.load(open(os.path.join(P, "06_Storyboard", "storyboard.json")))["scenes"]
    base = max(newest(os.path.join(ROOT, c)) for c in CODE)
    base = max(base, newest(os.path.join(P, "06_Storyboard", "storyboard.json")),
               newest(os.path.join(P, "09_Animation", "scene_timing.json")))
    out = []
    for s in sb:
        clip = os.path.join(P, "09_Animation", f"SC{s['id']:03d}.mp4")
        v = s["visual"]
        need = base
        if v["type"] == "plate":
            sh = S[v["shot"]]
            k = v["shot"]
            if sh["full"]:
                d = os.path.join(R, "full", k)
                if not os.path.exists(os.path.join(d, "meta.json")):
                    continue
                if len([f for f in os.listdir(d) if f.startswith("char_")]) < json.load(open(d + "/meta.json"))["frames"]:
                    continue
                need = max(need, newest(d))
            else:
                if not os.path.exists(os.path.join(R, "plates", k + ".png")):
                    continue
                need = max(need, newest(os.path.join(R, "plates", k + ".png")), newest(os.path.join(R, "plates", k + ".json")))
                if sh["actors"]:
                    d = os.path.join(R, "chars", k)
                    if not os.path.exists(os.path.join(d, "meta.json")):
                        continue
                    if len([f for f in os.listdir(d) if f.startswith("char_")]) < json.load(open(d + "/meta.json"))["frames"]:
                        continue
                    need = max(need, newest(d))
        else:       # cards: backdrop comes from the nearest earlier plate
            for j in range(sb.index(s), -1, -1):
                vv = sb[j]["visual"]
                if vv["type"] == "plate":
                    need = max(need, newest(os.path.join(R, "plates", vv["shot"] + ".png")))
                    break
        if not os.path.exists(clip) or os.path.getmtime(clip) < need:
            out.append(s["id"])
    return out


def main():
    proj = sys.argv[1]
    once = "--once" in sys.argv
    log = os.path.join(ROOT, proj, "08_Scenes", "logs", "compose_sync.log")
    while True:
        todo = stale(proj)
        if todo:
            sid = todo[0]
            t0 = time.time()
            r = subprocess.run(["nice", "-n", "15", sys.executable, os.path.join(ROOT, "tools/bats3d/compose4.py"),
                                proj, "render", str(sid), "--force"], cwd=ROOT, capture_output=True, text=True)
            with open(log, "a") as f:
                f.write(f"{time.strftime('%H:%M')} SC{sid:03d} rc={r.returncode} {time.time() - t0:.0f}s "
                        f"stale={len(todo)}\n" + (r.stderr[-800:] if r.returncode else ""))
            continue
        if once:
            break
        time.sleep(300)


if __name__ == "__main__":
    main()
