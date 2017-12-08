FROM openjdk:8-jdk

RUN git clone https://github.com/graphhopper/graphhopper.git
WORKDIR graphhopper

ADD config.properties config.properties

RUN ./graphhopper.sh buildweb