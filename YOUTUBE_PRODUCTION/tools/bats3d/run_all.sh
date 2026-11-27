#!/bin/bash
# Resumable launcher for all Episode 4 render queues (safe to re-run after a reboot).
cd "$(dirname "$0")/../.."
P=01_PROJECTS/what_if_bats_disappeared
R=$P/08_Scenes/renders4
L=$P/08_Scenes/logs
mkdir -p $L
nohup bash tools/bats3d/platequeue.sh $R 1 >> $L/pq1.log 2>&1 &
sleep 20
nohup bash tools/bats3d/platequeue.sh $R 2 >> $L/pq2.log 2>&1 &
sleep 20
nohup bash tools/bats3d/charqueue.sh $P 1 >> $L/cq1.log 2>&1 &
echo launched
