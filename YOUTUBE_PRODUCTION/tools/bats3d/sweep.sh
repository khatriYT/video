#!/bin/bash
# After the character workers finish, re-run the queues once to pick up any released/missing jobs.
cd /home/user/video/YOUTUBE_PRODUCTION
P=01_PROJECTS/what_if_bats_disappeared
R=$P/08_Scenes/renders4
L=$P/08_Scenes/logs
while [ $(pgrep -fc "charqueue.sh") -ge 2 ]; do sleep 60; done    # wait until at most one worker is left
bash tools/bats3d/platequeue.sh $R 7 >> $L/pq7.log 2>&1
nohup bash tools/bats3d/charqueue.sh $P 4 >> $L/cq4.log 2>&1 &
sleep 60
nohup bash tools/bats3d/charqueue.sh $P 5 >> $L/cq5.log 2>&1 &
echo "sweep launched" >> $L/sweep.log
