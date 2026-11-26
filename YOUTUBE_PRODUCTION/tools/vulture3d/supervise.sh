#!/bin/bash
# Keep 3 render workers busy: when a worker exits and unclaimed scenes remain, start another queue worker.
cd "$(dirname "$0")/../.."
R3=01_PROJECTS/what_if_vultures_disappeared/08_Scenes/renders3
Q="$1"
while true; do
  left=0
  for id in ${Q//,/ }; do [ -d $R3/claims/SC$(printf %03d $id) ] || left=$((left+1)); done
  [ $left -eq 0 ] && break
  n=$(pgrep -fc "render3.py -- (chars|queue)")
  if [ "$n" -lt 3 ]; then
    nohup blender -b --factory-startup -P tools/vulture3d/render3.py -- queue $Q $R3 >> $R3/logs/queue_extra.log 2>&1 &
    sleep 20
  fi
  sleep 60
done
