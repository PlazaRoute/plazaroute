# overpass

## overpass Abfrage

* [ÖV-Stationen im Umkreis Stadelhofen](http://overpass-turbo.eu/s/soC)

```
/*
This query looks for nodes, ways and relations
with the given key/value combination.
Choose your region and hit the Run button above!
*/
[out:json][timeout:25];
// gather results
(
  // query part for: “public_transport=stop_position”
  node["public_transport"="stop_position"](47.363536675068296,8.544192910194395,47.366799509164736,8.549686074256897);
  way["public_transport"="stop_position"](47.363536675068296,8.544192910194395,47.366799509164736,8.549686074256897);
  relation["public_transport"="stop_position"](47.363536675068296,8.544192910194395,47.366799509164736,8.549686074256897);
);
// print results
out body;
>;
out skel qt;

```

## Python Wrapper

* [overpass-api-python-wrapper](https://github.com/mvexel/overpass-api-python-wrapper)
  * letzter Release: 22.08.2016
  * letzter Commit: 18.09.2017
  * Test-Implementation: overpass_test.py


* [overpy](https://github.com/DinoTools/python-overpy)
  * letzter Release: 08.12.2016
  * letzter Commit: 07.04.2017
  * Test-Implementation: overpy_test.py


* Entscheid: overpy
  * beide haben gleichen Releasezyklus
  * overpass-api-python-wrapper gibt JSON zurück, welches selber geparsed werden muss
  * overpy ist fortgeschrittener, sprich es gibt Klassen für Nodes, Relations, Way, Area, etc. und Hilfsfunktionen, welche das ganze übersichtlich halten
  * overpy hat eine ausgereiftere Doku: https://python-overpy.readthedocs.io/en/latest/


## Links

* [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API)
  * [API Beispiele](https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_API_by_Example)
* https://taginfo.openstreetmap.org/tags
  * https://taginfo.openstreetmap.org/tags/public_transport=stop_position
  * oben rechts kann man direkt eine Overpass Turbo-Abfrage starten
