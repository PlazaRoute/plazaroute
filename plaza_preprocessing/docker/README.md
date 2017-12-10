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
$ git clone https://github.com/PlazaRoute/PlazaRoute.git
$ cd PlazaRoute/plaza_preprocessing/docker
$ sudo docker build -t plazaroute/plaza_preprocessing .
```

Use the same command as above to execute