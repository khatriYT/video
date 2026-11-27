#!/bin/bash
# Wait for both first-pass plate workers to finish, then run a second pass for released/missing plates.
cd /home/user/video/YOUTUBE_PRODUCTION
L=01_PROJECTS/what_if_bats_disappeared/08_Scenes/logs
until [ $(cat $L/pq1.log $L/pq2.log | grep -c DONE) -ge 2 ]; do sleep 30; done
R=01_PROJECTS/what_if_bats_disappeared/08_Scenes/renders4
nohup bash tools/bats3d/platequeue.sh $R 3 >> $L/pq3.log 2>&1 &
sleep 30
nohup bash tools/bats3d/platequeue.sh $R 4 >> $L/pq4.log 2>&1 &
echo "pass 2 launched" >> $L/pass2.log
