FROM python:3.6.3

#CHANGE BEFORE MERGING
RUN git clone -b PZ-123-docker-deployment https://github.com/PlazaRoute/PlazaRoute.git /plazaroute
WORKDIR /plazaroute

RUN pip install -r plaza_routing/requirements.txt

# set the graphhopper host name to "graphhopper"
RUN sed -i "s/localhost/graphhopper/g" plaza_routing/plaza_routing/integration/routing_strategy/graphhopper_swagger.json

RUN pip install plaza_routing/
RUN pip install uwsgi

RUN useradd -d /plazaroute -s /bin/bash plazarouting

USER plazarouting

EXPOSE 8080

CMD ["uwsgi", "--socket", "0.0.0.0:8080", "--manage-script-name", "--mount", "/=plaza_routing.app.application:app"]