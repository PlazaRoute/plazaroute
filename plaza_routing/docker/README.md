# Run plaza_routing with Docker

The docker-compose file provides a full deploy environment with [plaza_routing](https://github.com/PlazaRoute/PlazaRoute/tree/master/plaza_routing), [Graphhopper](https://github.com/graphhopper/graphhopper) and Nginx as a reverse Proxy.

## Requirements
* [Docker](https://www.docker.com/)
* [Docker Compose](https://docs.docker.com/compose/)
* A processed OSM / PBF file from [plaza_preprocessing](https://github.com/PlazaRoute/PlazaRoute/tree/master/plaza_preprocessing)

## Usage
* Put the processed OSM or PBF file into `gh-data` and adjust the path in the `docker-compose.yml` file, so that graphhopper uses that file
* Start the containers with `docker-compose up`
* After Graphhopper has finished importing the OSM file, [plaza_routing](https://github.com/PlazaRoute/PlazaRoute/tree/master/plaza_routing) should be available under `http://localhost:5000/api`

## Configuration
* The configuration for graphhopper can be adjusted by editing `graphhopper/config.properties`. By default, contraction hierarchies are turned off for faster startup.
* `plaza_routing` can be configured by overwriting `plaza_routing/plaza_routing/config.py` in the [plaza_routing Dockerfile](https://github.com/PlazaRoute/PlazaRoute/blob/PZ-123-docker-deployment/plaza_routing/docker/plaza_routing/Dockerfile)