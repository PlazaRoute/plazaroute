import pytest
import testfilemanager


def test_empty_file():
    with pytest.raises(RuntimeError):
        testfilemanager.import_testfile('empty_file')


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


def test_relation_plaza_with_single_polygon():
    """ test a relation with 1 polygon with inner rings """
    holder = testfilemanager.import_testfile('bahnhofplatz_bern')
    bahnhofplatz = get_plazas_by_id(holder.plazas, 5117701)
    assert len(bahnhofplatz) == 1
    bahnhofplatz = bahnhofplatz[0]
    assert bahnhofplatz['geometry']
    assert len(bahnhofplatz['geometry'].interiors) == 5


def test_multipolygon_plaza():
    """ test a relation with 2 independent plazas """
    holder = testfilemanager.import_testfile('zentrum_witikon')
    assert len(holder.plazas) == 2
    assert all([p['osm_id'] == 4105514 for p in holder.plazas])


def test_relation_with_unclosed_ways():
    """ test a relation with unclosed ways """
    holder = testfilemanager.import_testfile('unclosed_ways')
    # plaza should not be discarded
    assert len(holder.plazas) == 1


def get_plazas_by_id(plazas, osm_id):
    return list(filter(lambda p: p['osm_id'] == osm_id, plazas))
