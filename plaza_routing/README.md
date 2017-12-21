# Plaza Routing

This is the backend service for [plazaroute](https://github.com/PlazaRoute/plazaroute), exposing a web API for the [QGIS plugin](https://github.com/PlazaRoute/qgis).

## Requirements

* Python 3.6
* A running [GraphHopper instance](https://github.com/graphhopper/graphhopper) with a processed file from [plaza_preprocessing](https://github.com/PlazaRoute/plazaroute/tree/master/plaza_preprocessing)

## Installation

```
git clone https://github.com/PlazaRoute/plazaroute.git
cd plazaroute
pip install -r plaza_routing/requirements.txt
pip install plaza_routing/
cd plaza_routing
```

To start a local server:

```
python3 plaza_routing/app/application.py
```

The URLs to the services and preferences can be configured in [config.py](https://github.com/PlazaRoute/plazaroute/blob/master/plaza_routing/plaza_routing/config.py)

For deployment, see the [Docker README](https://github.com/PlazaRoute/plazaroute/tree/master/plaza_routing/docker)

## GraphHopper Setup

1. clone the GraphHopper repository
```
git clone https://github.com/graphhopper/graphhopper.git
cd graphhopper
```
2. create `config.properties`
```
cp config-example.properties config.properties
```
3. modify `config.properties`
```
graph.flag_encoders=foot
prepare.ch.weightings=no
prepare.lm.weightings=fastest
```
4. start GraphHopper with the preprocessed file from [plaza_preprocessing](https://github.com/PlazaRoute/plazaroute/tree/master/plaza_preprocessing)
```
./graphhopper.sh web switzerland-visibility-graph.pbf
```
