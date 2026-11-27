#!/bin/bash
# Compose each v2 scene as soon as its character pass (meta.json) or full render is complete.
cd "$(dirname "$0")/../.."
P=01_PROJECTS/what_if_vultures_disappeared
R3=$P/08_Scenes/renders3
while true; do
  for m in $R3/chars/SC*/meta.json; do
    [ -f "$m" ] || continue
    d=$(dirname $m); id=$((10#$(basename $d | tr -dc 0-9)))
    pk=$(python3 -c "import json;print(json.load(open('tools/vulture3d/scenes3_data.json'))['scene_plate']['$id'])")
    [ -f "$R3/plates/$pk.png" ] || continue
    [ -f "$P/09_Animation/SC$(printf %03d $id).mp4.v2" ] && continue
    nice -n 15 python3 tools/vulture3d/compose3.py $P $R3 $id >> $R3/logs/compose.log 2>&1
  done
  for id in 71 73; do
    d=$R3/full/SC0$id
    [ -f $R3/logs/full_$id.done ] || continue
    [ -f "$P/09_Animation/SC0$id.mp4.v2" ] && continue
    nice -n 15 python3 tools/vulture3d/compose3.py $P $R3 $id >> $R3/logs/compose.log 2>&1
  done
  sleep 60
done
