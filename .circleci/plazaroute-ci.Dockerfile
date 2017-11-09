# Docker image used for circle ci. This has been pushed to https://hub.docker.com/r/excap/plazaroute-ci/
FROM debian:buster

RUN apt-get update

# install requirements for circle ci
RUN apt-get install -y git ssh tar gzip ca-certificates

# install python 3.6 and requirements for osmium
RUN apt-get install -y build-essential libboost-python-dev libexpat1-dev zlib1g-dev libbz2-dev python3.6 python3.6-dev python3-venv wget

# install pip3
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN pip3 install --upgrade wheel setuptools virtualenv

# set locale to UTF-8 (for file encodings)
# from https://stackoverflow.com/questions/28405902/how-to-set-the-locale-inside-a-docker-container
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8
ENV LANG en_US.UTF-8