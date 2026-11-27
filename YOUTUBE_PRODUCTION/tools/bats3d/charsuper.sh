#!/bin/bash
# Keep up to N character-queue workers alive while unclaimed character jobs remain.
# (Workers build their job list once; jobs released later are only picked up by a fresh worker.)
cd "$(dirname "$0")/../.."
P="$1"; N="${2:-3}"; R="$P/08_Scenes/renders4"; L="$P/08_Scenes/logs"
id=10
while true; do
  pending=$(python3 - "$P" <<'PY'
import json, os, sys
sys.path.insert(0, 'tools/bats3d')
src = open('tools/bats3d/shots4.py').read().replace('from mathutils import Vector', 'Vector=tuple')
ns = {}; exec(src, ns); S = ns['SHOTS']
P = sys.argv[1]; R = P + '/08_Scenes/renders4'
sb = json.load(open(P + '/06_Storyboard/storyboard.json'))['scenes']
n = 0
for s in sb:
    v = s['visual']
    if v['type'] == 'plate' and S[v['shot']]['actors'] and not os.path.isdir(f"{R}/claims/char_{v['shot']}"):
        n += 1
print(n)
PY
)
  running=$(pgrep -fc "charqueue2?\.sh")
  if [ "$pending" -eq 0 ]; then echo "[super] no unclaimed jobs; exiting" >> $L/super.log; exit 0; fi
  if [ "$running" -lt "$N" ]; then
    id=$((id+1)); echo "[super] $(date +%H:%M) pending=$pending running=$running -> worker $id" >> $L/super.log
    nohup bash tools/bats3d/charqueue2.sh "$P" $id >> $L/cq$id.log 2>&1 &
  fi
  sleep 90
done
