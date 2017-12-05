import os
import pytest
import testfilemanager
from plaza_preprocessing import configuration


@pytest.fixture
def config():
    config_path = 'testconfig.yml'
    yield configuration.load_config(config_path)
    os.remove(config_path)


def test_empty_file(config):
    with pytest.raises(RuntimeError):
        testfilemanager.import_testfile('empty_file', config)


def test_simple_plaza(config):
    holder = testfilemanager.import_testfile('helvetiaplatz', config)
    assert len(holder.plazas) == 9
    assert len(holder.buildings) > 1000
    assert len(holder.lines) > 800
    assert len(holder.points) > 550

    helvetiaplatz = get_plazas_by_id(holder.plazas, 4533221)
    assert len(helvetiaplatz) == 1
    helvetiaplatz = helvetiaplatz[0]
    assert helvetiaplatz['geometry']
    assert helvetiaplatz['geometry'].area > 0


def test_relation_plaza_with_single_polygon(config):
    """ test a relation with 1 polygon with inner rings """
    holder = testfilemanager.import_testfile('bahnhofplatz_bern', config)
    bahnhofplatz = get_plazas_by_id(holder.plazas, 5117701)
    assert len(bahnhofplatz) == 1
    bahnhofplatz = bahnhofplatz[0]
    assert bahnhofplatz['geometry']
    assert len(bahnhofplatz['geometry'].interiors) == 5


def test_multipolygon_plaza(config):
    """ test a relation with 2 independent plazas """
    holder = testfilemanager.import_testfile('zentrum_witikon', config)
    assert len(holder.plazas) == 2
    assert all([p['osm_id'] == 4105514 for p in holder.plazas])


def test_relation_with_unclosed_ways(config):
    """ test a relation with unclosed ways """
    holder = testfilemanager.import_testfile('unclosed_ways', config)
    # plaza should not be discarded
    assert len(holder.plazas) == 1


def get_plazas_by_id(plazas, osm_id):
    return list(filter(lambda p: p['osm_id'] == osm_id, plazas))
