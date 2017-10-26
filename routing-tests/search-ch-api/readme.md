# search.ch API

* [Map API](https://map.search.ch/api/help)
* [Timetable API](https://fahrplan.search.ch/api/help)
* maximal 1000 Requests pro Tag


## Routensuche

* [API](https://fahrplan.search.ch/api/help#route)
* https://timetable.search.ch/api/route.json?from=Sternen+Oerlikon&to=Hallenbad+Oerlikon

## Vorgehen

1. Verbindungen über search.ch-API laden
  1. https://timetable.search.ch/api/route.json?from=Sternen+Oerlikon&to=Hallenbad+Oerlikon
  2. legs[0] liefert Ausgangspunkt der ÖV-Strecke
```
"legs": [
        {
          "departure": "2017-10-24 13:19:00",
          "tripid": "T2017_20528_000849_001_600ae97_0",
          "number": "BUS 20528",
          "stopid": "8591382",
          "x": 683594,
          "y": 251618,
          "name": "Zürich, Sternen Oerlikon",
          "sbb_name": "Zürich, Sternen Oerlikon",
          "type": "bus",
          "line": "62",
          "terminal": "Zürich, Schwamendingerplatz",
          "fgcolor": "000",
          "bgcolor": "d0c2af",
          "*G": "BUS",
          "*L": "62",
          "operator": "VBZ""
...
```
  3. wichtig sind die Attribute `stopid` und `terminal`
    1. `stopid` entspricht dem OSM-Tag: `uic_ref`
    2. `terminal`kann für das Bestimmen der Richtung verwendet werden um so zur richtigen Station zu routen, da die `uic_ref`mehrere Stationen referenzieren kann, z.B. für beide Fahrtrichtungen.
2. mit Overpass die Ausgangsstation bestimmen
  1. ÖV-Linie laden
```
# lässt sich mit der gleichen Bounding Box erreichen, wie das Finden der erreichbaren Stationen
relation["type"="route"]["route"="bus"]["ref"="62"]({{bbox}});
```
  2. zum letzten Node in der Relation navigieren --> dieser entspricht der Endstation (Terminal)
  3. Node mit Overpass laden über `ref`
  4. entspricht die Endstation dem `terminal` von search.ch kann man nun die Ausgangsstation laden, welcher Teil dieser Relation ist mit der `uic_ref`
  5. entspricht sie nicht, nimmt man nächste Linie, welche man im Schritt 2.1. geladen hat
