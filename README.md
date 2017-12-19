# plazaroute

[![Build Status](https://circleci.com/gh/PlazaRoute/plazaroute.png)](https://circleci.com/gh/PlazaRoute/plazaroute)

API Reference: <https://plazaroute.github.io/plazaroute/>

# Run plaza_routing with Docker

The docker-compose file provides a full deploy environment with [plaza_routing](https://github.com/PlazaRoute/plazaroute/tree/master/plaza_routing), [Graphhopper](https://github.com/graphhopper/graphhopper) and Nginx as a reverse Proxy.

## Requirements
* [Docker](https://www.docker.com/)
* [Docker Compose](https://docs.docker.com/compose/)
* A processed OSM / PBF file from [plaza_preprocessing](https://github.com/PlazaRoute/plazaroute/tree/master/plaza_preprocessing)

## Usage
* Put the processed OSM or PBF file into `gh-data` and adjust the path in the `docker-compose.yml` file, so that graphhopper uses that file
* Start the containers with `docker-compose up`
* After Graphhopper has finished importing the OSM file, [plaza_routing](https://github.com/PlazaRoute/plazaroute/tree/master/plaza_routing) should be available under `http://localhost:5000/api`

## Configuration
* The configuration for graphhopper can be adjusted by editing `graphhopper/config.properties`. By default, contraction hierarchies are turned off for faster startup.
* `plaza_routing` can be configured by overwriting `plaza_routing/plaza_routing/config.py` in the [plaza_routing Dockerfile](https://github.com/PlazaRoute/plazaroute/blob/master/Dockerfile.routing)


# Run Plaza Preprocessing in Docker

## Pre-built image

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

## Build manually

There is a `Dockerfile` in this directory which you can use to build your own image

```
$ git clone https://github.com/PlazaRoute/plazaroute.git
$ cd plazaroute/plaza_preprocessing/docker
$ sudo docker build -t plazaroute/plaza_preprocessing .
```

Use the same command as above to execute


## Fully automated

Have a look in the docker-compose.yml to see how a production setup might
be setup to automatically update the pbf files and restart the graphhopper service
whenever the pbf changes.
