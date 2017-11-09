# Docker image used for circle ci. This has been pushed to https://hub.docker.com/r/excap/plazaroute-ci/
FROM debian:buster

# install python 3.6 and requirements for osmium
RUN apt-get update
RUN apt-get install -y build-essential libboost-python-dev libexpat1-dev zlib1g-dev libbz2-dev python3.6 python3.6-dev python3-venv wget