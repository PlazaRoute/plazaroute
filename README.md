# PlazaRoute

[![Build Status](https://circleci.com/gh/PlazaRoute/plazaroute.png)](https://circleci.com/gh/PlazaRoute/plazaroute)

API Reference: <https://plazaroute.github.io/plazaroute/>

PlazaRoute is a Python Webservice to provide public transport and pedestrian routing. Its main purpose is to show pedestrian routing through open areas. To achieve that, an OSM file for a region is first processed with [plaza_preprocessing](https://github.com/PlazaRoute/plazaroute/tree/master/plaza_preprocessing) to add new ways for the router. The processed file can than be used with [plaza_routing](https://github.com/PlazaRoute/plazaroute/tree/master/plaza_routing) to provide an API.

A QGIS plugin as a frontend is available here: <https://github.com/PlazaRoute/qgis>


Python Packages Reference: <https://plazaroute.github.io/plazaroute/>

## Acknowledgments

* [Search.ch](https://www.search.ch/) for public transport routing
* [Graphhopper](https://github.com/graphhopper/graphhopper) for pedestrian routing
* [Nominatim](https://nominatim.openstreetmap.org/) for geocoding
* [Swiss Overpass API](http://overpass.osm.ch/)
* Visibility Graph algorithm based on the [paper by A. Graser](https://www.researchgate.net/publication/305272744_Integrating_Open_Spaces_into_OpenStreetMap_Routing_Graphs_for_Realistic_Crossing_Behaviour_in_Pedestrian_Navigation)
* SpiderWeb Graph algorithm based on [Routing über Flächen mit SpiderWebGraph](https://gispoint.de/gisopen-paper/1613-routing-ueber-flaechen-mit-spiderwebgraph.html)

## plaza_preprocessing

Python package to prepare OSM data for pedestrian routing through open spaces. With two available algorithms - Visibility Graph and SpiderWeb Graph - new ways over open spaces (plazas) will be generated.

See the [plaza_preprocessing README](https://github.com/PlazaRoute/plazaroute/tree/master/plaza_preprocessing) for more information

## plaza_routing

Python webservice that exposes an API which can be used for public transport and pedestrian routing.

* The API specification can be found under <https://plazaroute.github.io/api/>
* There is a QGIS Plugin to use the API under [PlazaRoute/qgis](https://github.com/PlazaRoute/qgis)

See the [plaza_routing README](https://github.com/PlazaRoute/plazaroute/tree/master/plaza_routing) for more information


---



## Run Plaza Preprocessing in Docker

### Pre-built image

A pre-built docker image for this package is published on [Docker Hub](https://hub.docker.com/r/plazaroute/plaza_preprocessing)

### Usage
For this example, we assume that you have the file you want to process under `/tmp/osm/my_osm.pbf`. The processed file will be saved under `/tmp/osm/my_osm_processed.pbf`.

``` bash
sudo docker run -v /tmp/osm:/osm plazaroute/plaza_preprocessing plaza_preprocessing /osm/my_osm.pbf /osm/my_osm_processed.pbf --config /osm/preprocessing_config.yml
```

Notice that `/osm` in the command refers to the filesystem inside the docker container, which is mounted to `/tmp/osm`

With the `--config` option we create a new configuration file in `/tmp/osm`, which we can modify for further calls with the same command.

### Updating OSM files

You can also use the docker image to update the downloaded OSM data. Example for Switzerland, our file to update is `/tmp/osm/switzerland-padded.osm.pbf`:

```
sudo docker run -v /tmp/osm:/osm plazaroute/plaza_preprocessing pyosmium-up-to-date --server https://planet.osm.ch/replication/hour/ /osm/switzerland-padded.osm.pbf
```

### Build manually

There is a `Dockerfile` in this directory which you can use to build your own image

```
$ git clone https://github.com/PlazaRoute/plazaroute.git
$ cd plazaroute/plaza_preprocessing/docker
$ sudo docker build -t plazaroute/plaza_preprocessing .
```

Use the same command as above to execute

---

## Run plaza_routing with Docker

The docker-compose file provides a full deploy environment with [plaza_routing](https://github.com/PlazaRoute/plazaroute/tree/master/plaza_routing), [Graphhopper](https://github.com/graphhopper/graphhopper) and Nginx as a reverse Proxy.

### Requirements
* [Docker](https://www.docker.com/)
* [Docker Compose](https://docs.docker.com/compose/)
* A processed OSM / PBF file from [plaza_preprocessing](https://github.com/PlazaRoute/plazaroute/tree/master/plaza_preprocessing)

### Usage
* Put the processed OSM or PBF file into `gh-data` and adjust the path in the `docker-compose.yml` file, so that graphhopper uses that file
* Start the containers with `docker-compose up`
* After Graphhopper has finished importing the OSM file, [plaza_routing](https://github.com/PlazaRoute/plazaroute/tree/master/plaza_routing) should be available under `http://localhost:5000/api`

### Configuration
* The configuration for graphhopper can be adjusted by editing `graphhopper/config.properties`. By default, contraction hierarchies are turned off for faster startup.
* `plaza_routing` can be configured by overwriting `plaza_routing/plaza_routing/config.py` in the [plaza_routing Dockerfile](https://github.com/PlazaRoute/plazaroute/blob/master/Dockerfile.routing)

---

## Fully automated

Have a look in the docker-compose.yml to see how a production setup might
be setup to automatically update the pbf files and restart the graphhopper service
whenever the pbf changes.
