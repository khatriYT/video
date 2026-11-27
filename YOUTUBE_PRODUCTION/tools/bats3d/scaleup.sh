#!/bin/bash
# When plate and sprite rendering are finished, add two more character-pass workers (claims prevent duplicates).
cd /home/user/video/YOUTUBE_PRODUCTION
P=01_PROJECTS/what_if_bats_disappeared
while pgrep -f "platequeue.sh" > /dev/null || pgrep -f "spritequeue.sh" > /dev/null; do sleep 60; done
nohup bash tools/bats3d/charqueue.sh $P 2 >> $P/08_Scenes/logs/cq2.log 2>&1 &
sleep 60
nohup bash tools/bats3d/charqueue.sh $P 3 >> $P/08_Scenes/logs/cq3.log 2>&1 &
echo "scaled up" >> $P/08_Scenes/logs/scaleup.log
