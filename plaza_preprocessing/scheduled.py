import json
import os
import shlex
from datetime import datetime, timedelta

import schedule
import subprocess
import time

PBF_DOWNLOAD_URL = os.environ.get('PBF_DOWNLOAD_URL', 'https://planet.osm.ch/switzerland-padded.osm.pbf')
UPDATE_SERVER_URL = os.environ.get('UPDATE_SERVER_URL', 'https://planet.osm.ch/replication/hour/')
PBF_PATH = os.environ.get('PBF_PATH', '/pbf/switzerland-padded.osm.pbf')
PBF_PROCESSED_PATH = os.environ.get('PBF_PROCESSED_PATH', '/pbf/switzerland-processed.osm.pbf')
RUN_EVERY_X_MINUTES = int(os.environ.get('RUN_EVERY_X_MINUTES', 60 * 24 * 7))  # default: every week

_LAST_RUN_FILE_PATH = '/pbf/last_run.txt'

def _run_command(command):
    with subprocess.Popen(
        shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1,
    ) as p:
        for line in p.stdout:
            print(line, end='')


def _get_last_run():
    if os.path.exists(_LAST_RUN_FILE_PATH) and os.path.isfile(_LAST_RUN_FILE_PATH):
        with open(_LAST_RUN_FILE_PATH, 'r') as last_run:
            last_run_timestamp = json.loads(last_run.readlines()[0])
            return datetime.fromtimestamp(last_run_timestamp)
    return datetime.min


def job():
    last_run = _get_last_run()
    if datetime.now() < (last_run + timedelta(minutes=RUN_EVERY_X_MINUTES)):
        print("Last update not old enough, skipping.")
        return
    if os.path.exists(PBF_PATH):
        print(30 * '#')
        print("PBF exists. Starting Update Process.")
        _run_command(f"pyosmium-up-to-date -v --server {UPDATE_SERVER_URL} {PBF_PATH}")
        print("Update Finished")
        print(30 * '#')
    else:
        print(30 * '#')
        print("PBF does not exist. Starting Download.")
        _run_command(f"wget -O {PBF_PATH} {PBF_DOWNLOAD_URL}")
        print("Download Done")
        print(30 * '#')

    print(30 * '#')
    print("Preprocessing...")
    _run_command(f"/usr/local/bin/plaza_preprocessing {PBF_PATH} {PBF_PROCESSED_PATH}")
    with open(_LAST_RUN_FILE_PATH, 'w') as last_run:
        last_run.write(json.dumps(datetime.timestamp(datetime.now())))
    print("Preprocessing Done")
    print(30 * '#')


def run():
    job()  # init
    schedule.every(RUN_EVERY_X_MINUTES).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == '__main__':
    run()
