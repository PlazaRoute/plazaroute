# GraphHopper

* [Quick-Setup](https://github.com/graphhopper/graphhopper/blob/master/docs/core/quickstart-from-source.md)
* `config.properties`
  * set `graph.flag_encoders=foot`

```
wget http://download.geofabrik.de/europe/switzerland-latest.osm.pbf
./graphhopper.sh web switzerland-latest.osm.pbf
```
* [Demo-Instanz](http://localhost:8989)
* [Demo-Request](http://localhost:8989/route?point=47.366353,8.544976&point=47.365888,8.54709&type=json&locale=de&vehicle=foot&weighting=fastest&elevation=false&points_encoded=false&instructions=false&key=)

## Demo App

```
pip install -r requirements.txt
python3 client.py
```
* make sure that `swagger.json` is locally available
