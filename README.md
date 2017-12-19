# PlazaRoute

[![Build Status](https://circleci.com/gh/PlazaRoute/plazaroute.png)](https://circleci.com/gh/PlazaRoute/plazaroute)

<<<<<<< HEAD
API Reference: <https://plazaroute.github.io/plazaroute/>

=======
>>>>>>> master
PlazaRoute is a Python Webservice to provide public transport and pedestrian routing. Its main purpose is to show pedestrian routing through open areas. To achieve that, an OSM file for a region is first processed with [plaza_preprocessing](https://github.com/PlazaRoute/plazaroute/tree/master/plaza_preprocessing) to add new ways for the router. The processed file can than be used with [plaza_routing](https://github.com/PlazaRoute/plazaroute/tree/master/plaza_routing) to provide an API.

A QGIS plugin as a frontend is available here: <https://github.com/PlazaRoute/qgis>


Python Packages Reference: <https://plazaroute.github.io/plazaroute/>

## Research

This project was created as a part of a student research project at the University of Applied Sciences Rapperswil (HSR). The full text can be found [here](https://github.com/PlazaRoute/doc).

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

### Fully automated

Have a look in [deploy directory](deploy/) to see how a production setup might be setup to automatically update the pbf files and restart the graphhopper service whenever the pbf changes.
