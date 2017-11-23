import plaza_preprocessing.osm_optimizer.osm_optimizer as osm_optimizer
import pytest
import testfilemanager
import utils
from plaza_preprocessing.osm_optimizer.graphprocessor.spiderwebgraphprocessor import SpiderWebGraphProcessor
from plaza_preprocessing.osm_optimizer.graphprocessor.visibilitygraphprocessor import VisibilityGraphProcessor


@pytest.fixture(params=['visibility', 'spiderweb'])
def process_strategy(request):
    if request.param == 'visibility':
        return VisibilityGraphProcessor()
    elif request.param == 'spiderweb':
        return SpiderWebGraphProcessor(spacing_m=5)


def test_simple_plaza(process_strategy):
    result_plaza = utils.process_plaza('helvetiaplatz', 4533221, process_strategy)
    assert result_plaza
    assert len(result_plaza['graph_edges']) > 10
    assert len(result_plaza['entry_points']) == 7
    assert len(result_plaza['entry_lines']) == 5


def test_complicated_plaza(process_strategy):
    result_plaza = utils.process_plaza('bahnhofplatz_bern', 5117701, process_strategy)
    assert result_plaza
    assert len(result_plaza['graph_edges']) > 20
    assert len(result_plaza['entry_points']) == 17
    assert len(result_plaza['entry_lines']) == 22


def test_multiple_plazas(process_strategy):
    holder = testfilemanager.import_testfile('helvetiaplatz')
    processed_plazas = osm_optimizer.preprocess_plazas(holder, process_strategy)

    assert len(processed_plazas) == 6
    all_edges = [edge.coords for plaza in processed_plazas for edge in plaza["graph_edges"]]
    assert len(set(all_edges)) == len(all_edges)  # check for duplicates


def test_optimized_lines_inside_plaza(process_strategy):
    holder = testfilemanager.import_testfile('bahnhofplatz_bern')
    plaza = utils.get_plaza_by_id(holder.plazas, 5117701)
    plaza_geometry = plaza['geometry']
    processor = osm_optimizer.PlazaPreprocessor(holder, process_strategy)
    result_plaza = processor._process_plaza(plaza)

    assert result_plaza
    # all optimized lines should be inside the plaza geometry
    assert all(line.equals(plaza_geometry.intersection(line)) for line in result_plaza['graph_edges'])


def test_obstructed_plaza(process_strategy):
    """ plazas obstructed by buildings should be discarded """
    result_plaza = utils.process_plaza('europaallee', 182055194, process_strategy)
    assert not result_plaza  # plaza should be discarded


def test_almost_obstructed_plaza(process_strategy):
    """ this plaza is almost completely obstructed, but a tiny area remains"""
    result_plaza = utils.process_plaza('zuerich_hb', 6619147, process_strategy)
    assert not result_plaza  # plaza should be discarded


def test_entry_points():
    """ Entry points on Kreuzplatz seem to be wrong """
    result_plaza = utils.process_plaza('kreuzplatz', 5541230, process_strategy)
    with pytest.raises(AssertionError):
        assert result_plaza
        assert len(result_plaza['entry_points']) == 16
        # TODO: is 0 instead of 16


def test_entry_lines(process_strategy):
    result_plaza = utils.process_plaza('helvetiaplatz', 39429064, process_strategy)
    assert result_plaza
    assert len(result_plaza['entry_lines']) == 3
    assert all(
        len(line['entry_points']) == 1 for line in result_plaza['entry_lines'])


def test_bahnhofstrasse(process_strategy):
    result_plaza = utils.process_plaza('bahnhofstrasse', 27405455, process_strategy)
    # TODO: one entry point is inaccurate
    assert result_plaza
    with pytest.raises(AssertionError):
        assert all(e.touches(result_plaza['geometry']) for e in result_plaza['entry_points'])


def test_entry_points_with_cutout_polygon(process_strategy):
    result_plaza = utils.process_plaza('zuerich_hb', 6605179, process_strategy)
    assert result_plaza
    # TODO: entry points should still be valid after the geometry has been cutout
    with pytest.raises(AssertionError):
        assert all(e.touches(result_plaza['geometry']) for e in result_plaza['entry_points'])
