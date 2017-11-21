import os.path
from plaza_preprocessing import osm_importer

TESTFILEPATH = os.path.join(os.path.dirname(__file__), 'testfiles')

TEST_PLAZAS = {
    'empty_file': 'empty_file.osm',
    'unclosed_ways': 'unclosed_ways.osm',
    'helvetiaplatz': 'helvetiaplatz.osm',
    'bahnhofplatz_bern': 'bahnhofplatz-bern.osm',
    'bundeshaus_bern': 'bundeshaus-bern.osm',
    'zurich-city': 'stadt-zuerich.pbf',
    'zentrum_witikon': 'zentrum_witikon.osm',
    'europaallee': 'europaallee.osm',
    'kreuzplatz': 'kreuzplatz.osm',
    'bahnhofstrasse': 'bahnhofstrasse.osm'
}


def get_testfile_name(name):
    return os.path.join(TESTFILEPATH, TEST_PLAZAS[name])


def import_testfile(name):
    filename = get_testfile_name(name)
    return osm_importer.import_osm(filename)
