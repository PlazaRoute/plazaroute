""" Configuration properties for Plaza Routing"""

geocoding = dict(
    geocoding_api="http://nominatim.openstreetmap.org/search",
    viewbox="5.9559,45.818,10.4921,47.8084",  # Viewbox to geocode, default Switzerland
)

overpass = dict(
    overpass_api="http://overpass.osm.ch/api/interpreter",
    public_transport_search_radius=1000  # max distance from start point where public transport stops will be searched
)

search_ch = dict(
    search_ch_api="https://timetable.search.ch/api/route.json"
)

graphhopper = dict(
    swagger_file="graphhopper_swagger.json"  # location of swagger file that specifies the graphhopper api
)
