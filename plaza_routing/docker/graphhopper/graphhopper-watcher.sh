#!/bin/bash
set -e

GH_PID=''

start_graphhopper() {
    if [ -d ${PBF_PATH}-sh ]; then
        rm -rf ${PBF_PATH}-sh;
    fi
    ./graphhopper.sh web ${PBF_PATH} &
    GH_PID=$!
}


kill_and_restart() {
    echo "file change discovered, restarting service"
    if [ ! -f ${PBF_PATH} ]; then
        sleep 10
    else
        echo "killing " ${GH_PID}
        sleep 10
        kill -1 ${GH_PID}
        if [ -d ${PBF_PATH}-sh ]; then
            rm -rf ${PBF_PATH}-sh
        fi
        ./graphhopper.sh web ${PBF_PATH} &
        GH_PID=$!
        echo "graphhopper started, PID: " ${GH_PID}
    fi
    sleep 30
}

start_graphhopper
echo "graphhopper started, PID: " ${GH_PID}

WATCH_DIR=$(dirname ${PBF_PATH})
echo "watching $WATCH_DIR"

inotifywait -e modify,create -m ${WATCH_DIR} |
while read -r directory events filename; do
  if [ "$filename" = "$(basename ${PBF_PATH})" ]; then
    kill_and_restart
  fi
done
