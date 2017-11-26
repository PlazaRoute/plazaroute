
def transform_ch_to_wgs(x, y):
    return _transform_ch_to_wgs_lng(x, y), _transform_ch_to_wgs_lat(x, y)


def _transform_ch_to_wgs_lat(y, x):
    """
    Convert CH y/x to WGS lat.

    Credit:
    https://github.com/ValentinMinder/Swisstopo-WGS84-LV03/blob/f1a7e0129d93647c1c11e151b95a208a53e57ce6/scripts/py/wgs84_ch1903.py#L51
    """
    # auxiliary values (% Bern)
    y_aux = (y - 600000) / 1000000
    x_aux = (x - 200000) / 1000000
    lat = (16.9023892 + (3.238272 * x_aux)) - (0.270978 * pow(y_aux, 2)) - (0.002528 * pow(x_aux, 2)) - \
          (0.0447 * pow(y_aux, 2) * x_aux) - (0.0140 * pow(x_aux, 3))
    # unit 10000" to 1" and convert seconds to degrees (dec)
    lat = (lat * 100) / 36
    return lat


def _transform_ch_to_wgs_lng(y, x):
    """
    Convert CH y/x to WGS long.

    Credit:
    https://github.com/ValentinMinder/Swisstopo-WGS84-LV03/blob/f1a7e0129d93647c1c11e151b95a208a53e57ce6/scripts/py/wgs84_ch1903.py#L65
    """
    # auxiliary values (% Bern)
    y_aux = (y - 600000) / 1000000
    x_aux = (x - 200000) / 1000000
    lng = (2.6779094 + (4.728982 * y_aux) + (0.791484 * y_aux * x_aux) + (0.1306 * y_aux * pow(x_aux, 2))) - \
          (0.0436 * pow(y_aux, 3))
    # unit 10000" to 1" and convert seconds to degrees (dec)
    lng = (lng * 100) / 36
    return lng
