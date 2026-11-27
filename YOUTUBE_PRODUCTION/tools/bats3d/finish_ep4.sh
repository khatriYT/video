#!/bin/bash
# Autonomous finish for Episode 4 (runs without the assistant): wait for every character / full-3D pass,
# final composites, audio mix + assembly, QC, 720p copy, then commit + push the review video and reports.
cd "$(dirname "$0")/../.."
P=01_PROJECTS/what_if_bats_disappeared; L=$P/08_Scenes/logs/finish.log; BR=ccr-82bff6bd-fiyrgo
BASE=what_if_all_bats_disappeared
log() { echo "$(date '+%d %H:%M') $*" >> "$L"; }
remaining() {
python3 - <<'PY'
import json, os, math
src = open('tools/bats3d/shots4.py').read().replace('from mathutils import Vector', 'Vector=tuple')
ns = {}; exec(src, ns); S = ns['SHOTS']
P = '01_PROJECTS/what_if_bats_disappeared'; R = P + '/08_Scenes/renders4'
sb = json.load(open(P + '/06_Storyboard/storyboard.json'))['scenes']
tm = json.load(open(P + '/09_Animation/scene_timing.json'))
left = 0
for s in sb:
    v = s['visual']
    if v['type'] != 'plate' or not S[v['shot']]['actors']:
        continue
    k = v['shot']; sh = S[k]
    n = 1 if sh.get('hold') else math.ceil(tm[s['file']]['duration'] * sh.get('fps', 8 if sh['full'] else 12)) + 1
    d = f"{R}/{'full' if sh['full'] else 'chars'}/{k}"
    have = len([f for f in os.listdir(d) if f.startswith('char_')]) if os.path.isdir(d) else 0
    left += max(0, n - have)
print(left)
PY
}
log "finish script started"
last=$(remaining); still=0
while true; do
  r=$(remaining)
  [ "$r" = "0" ] && break
  pgrep -f charsuper.sh > /dev/null || { nohup bash tools/bats3d/charsuper.sh "$P" 4 > /dev/null 2>&1 & log "supervisor restarted"; }
  if [ "$r" = "$last" ]; then still=$((still + 1)); else still=0; last=$r; fi
  if [ $still -ge 12 ]; then log "no render progress for 2 h ($r frames left): finishing with what exists"; break; fi
  log "frames left: $r"
  sleep 600
done
log "renders done (left=$(remaining))"
pkill -f compose_sync.py; sleep 5
python3 tools/bats3d/compose_sync.py "$P" --once
# scenes whose passes never completed still get a clip (last rendered frame is held)
python3 - "$P" <<'PY' | while read sid; do nice python3 tools/bats3d/compose4.py "$P" render "$sid" --force >> "$L" 2>&1; done
import json, os, sys
P = sys.argv[1]
for s in json.load(open(P + '/06_Storyboard/storyboard.json'))['scenes']:
    if not os.path.exists(f"{P}/09_Animation/SC{s['id']:03d}.mp4"):
        print(s['id'])
PY
log "composites done"
python3 tools/bats3d/audio4.py "$P" assemble "$BASE" >> "$L" 2>&1 || { log "ASSEMBLE FAILED"; exit 1; }
F=$P/12_Exports/${BASE}_REVIEW.mp4
python3 tools/vulture3d/qc.py "$P" "$F" >> "$L" 2>&1; log "qc rc=$?"
ffmpeg -y -loglevel error -i "$F" -vf scale=1280:-2 -c:v libx264 -crf 24 -preset medium -c:a aac -b:a 128k \
  "$P/12_Exports/${BASE}_REVIEW_720p.mp4" && log "720p done"
git add "$P/12_Exports" "$P/11_Edit" "$P/09_Animation/scene_timing.json" 2>> "$L"
git commit -q -m "Ep4: review cut (autonomous finish): final composites, audio mix, QC, 720p copy

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TihUFgZp2d2FxV6iVgmJbD" >> "$L" 2>&1
for i in 1 2 3 4 5; do git push -u origin "$BR" >> "$L" 2>&1 && { log "PUSHED"; break; }; sleep $((2 ** i * 5)); done
log "finish script done"
