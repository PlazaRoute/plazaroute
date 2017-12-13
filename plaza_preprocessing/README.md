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

### Download an OSM file

plaza_preprocessing takes an existing OSM file as an input. Data for Switzerland can be found on https://planet.osm.ch.

#### Updating OSM file

In order to keep the OSM data up to date without redownloading it every time, you can use [pyosmium-up-to-date](http://docs.osmcode.org/pyosmium/latest/tools_uptodate.html) provided by pyosmium. Example to bring [switzerland-padded.osm.pbf](https://planet.osm.ch) up to date:

```
pyosmium-up-to-date -v --server https://planet.osm.ch/replication/hour/ switzerland-padded.osm.pbf
```

You can also do this with Docker without having to install pyosmium. See the [the Docker readme](docker/) for reference.

## Preprocessing

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

Example:

```
plaza_preprocessing switzerland-padded.osm.pbf switzerland-processed.osm.pbf
```
