import re

COORDINATE_RX = re.compile(r'^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$')
TIME_RX = re.compile(r'^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$')


def is_address(address: str) -> bool:
    return bool(re.search('[a-zA-Z]', address))


def is_valid_coordinate(coordinate: str) -> bool:
    return bool(COORDINATE_RX.match(coordinate))


def is_valid_departure(departure: str) -> bool:
    return bool(TIME_RX.match(departure))
