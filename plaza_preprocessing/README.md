# Plaza Preprocessing

This is the plaza preprocessing package for [PlazaRoute](https://github.com/PlazaRoute/PlazaRoute), responsible for preparing OSM files for optimized pedestrian routing with support for routing through plazas.

## Install

See [the Docker readme](docker/) for quickly getting up and running without an installation.

```
$ git clone https://github.com/PlazaRoute/PlazaRoute.git
$ cd PlazaRoute
$ pip install plaza_preprocessing/
```

## Usage

```
usage: plaza_preprocessing [-h] [--config filename] [-v] source destination

Preprocess an OSM file for pedestrian routing over plazas.

positional arguments:
  source             input OSM file to process
  destination        destination OSM file

optional arguments:
  -h, --help         show this help message and exit
  --config filename  specify a config file location. A default config will be
                     created if the path does not exist
  -v                 verbose log output
```