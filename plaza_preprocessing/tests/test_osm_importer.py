import pytest
from plaza_preprocessing import osm_importer
from plaza_preprocessing.osm_merger import geojson_writer
import testfilemanager

def test_empty_file():
    with pytest.raises(RuntimeError):
        holder = testfilemanager.import_testfile('empty_file')

def test_simple_plaza():
    holder = testfilemanager.import_testfile('helvetiaplatz')
    assert len(holder.plazas) == 9
    assert len(holder.buildings) > 1000
    assert len(holder.lines) > 800
    assert len(holder.points) > 550

    helvetiaplatz = get_plazas_by_id(holder.plazas, 4533221)
    assert len(helvetiaplatz) == 1
    helvetiaplatz = helvetiaplatz[0]
    assert helvetiaplatz['geometry']
    assert helvetiaplatz['geometry'].area > 0
    assert not helvetiaplatz['is_relation']
    assert helvetiaplatz['outer_ring_id'] == helvetiaplatz['osm_id']

def test_relation_plaza_with_single_polygon():
    """ test a relation with 1 polygon with inner rings """
    holder = testfilemanager.import_testfile('bahnhofplatz_bern')
    bahnhofplatz = get_plazas_by_id(holder.plazas, 5117701)
    assert len(bahnhofplatz) ==  1
    bahnhofplatz = bahnhofplatz[0]
    assert bahnhofplatz['is_relation']
    assert bahnhofplatz['outer_ring_id'] == 306097074
    assert bahnhofplatz['geometry']
    assert len(bahnhofplatz['geometry'].interiors) == 5


def test_multipolygon_plaza():
    """ test a relation with 2 independent plazas """
    holder = testfilemanager.import_testfile('zentrum_witikon')
    assert len(holder.plazas) == 2
    assert all([p['osm_id'] == 4105514 for p in holder.plazas])
    assert all([p['is_relation'] for p in holder.plazas])

    smaller_plaza = list(filter(lambda p: p['outer_ring_id'] == 307416675, holder.plazas))
    bigger_plaza = list(filter(lambda p: p['outer_ring_id'] == 385832858, holder.plazas))
    assert len(smaller_plaza) == 1
    assert len(bigger_plaza) == 1
    smaller_plaza = smaller_plaza[0]
    bigger_plaza = bigger_plaza[0]
    assert bigger_plaza['geometry'].area > smaller_plaza['geometry'].area


def test_relation_with_unclosed_ways():
    """ test a relation with unclosed ways """
    holder = testfilemanager.import_testfile('unclosed_ways')
    # plaza should be discarded
    assert len(holder.plazas) == 0


def get_plazas_by_id(plazas, osm_id):
    return list(filter(lambda p: p['osm_id'] == osm_id, plazas))