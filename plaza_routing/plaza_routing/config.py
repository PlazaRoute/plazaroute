""" Configuration properties for Plaza Routing """

import logging

app = dict(
    server_url="localhost:5000",  # only used when deployed locally (without uWSGI)
    debug=True,  # only used when deployed locally (without uWSGI)
    log_level=logging.DEBUG,
    restplus=dict(
        swagger_ui_doc_expansion="list",
        validate=True,
        mask_swagger=False,
        error_404_help=False
    )
)

plaza_route_finder = dict(
    max_walking_duration=300  # in seconds
)

geocoding = dict(
    geocoding_api="https://nominatim.openstreetmap.org/search",
    viewbox="5.9559,45.818,10.4921,47.8084",  # Viewbox to geocode, default Switzerland
)

overpass = dict(
    overpass_api="https://overpass.osm.ch/api/interpreter",
    public_transport_search_radius=1000  # max distance from start point where public transport stops will be searched
)

search_ch = dict(
    search_ch_api="https://timetable.search.ch/api/route.json"
)

graphhopper = dict(
    swagger_file="graphhopper_swagger.json"  # location of swagger file that specifies the graphhopper api
)
