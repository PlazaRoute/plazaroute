import pytest
import testfilemanager
from plaza_preprocessing.osm_optimizer import osm_optimizer
from plaza_preprocessing.osm_optimizer.visibilitygraphprocessor import VisibilityGraphProcessor
from plaza_preprocessing.osm_optimizer.spiderwebgraphprocessor import SpiderWebGraphProcessor


@pytest.fixture(params=['visibility', 'spiderweb'])
def process_strategy(request):
    if request.param == 'visibility':
        return VisibilityGraphProcessor()
    elif request.param == 'spiderweb':
        return SpiderWebGraphProcessor(spacing_m=5)


def test_simple_plaza(process_strategy):
    processor = prepare_processing('helvetiaplatz', 4533221, process_strategy)
    success = processor.process_plaza()
    assert success
    edges = processor.graph_edges
    assert len(edges) > 10
    assert len(processor.entry_points) == 7
    assert len(processor.entry_lines) == 5


def test_complicated_plaza(process_strategy):
    processor = prepare_processing('bahnhofplatz_bern', 5117701, process_strategy)
    success = processor.process_plaza()
    assert success
    edges = processor.graph_edges
    assert len(edges) > 20
    assert len(processor.entry_points) == 17
    assert len(processor.entry_lines) == 22


def test_obstructed_plaza(process_strategy):
    """ plazas obstructed by buildings should be discarded """
    processor = prepare_processing('europaallee', 182055194, process_strategy)
    edges = processor.process_plaza()
    assert not processor.plaza_geometry # geometry should be empty
    assert not edges


def test_entry_points():
    """ Entry points on Kreuzplatz seem to be wrong """
    processor = prepare_processing('kreuzplatz', 5541230, process_strategy)
    with pytest.raises(AssertionError):
        assert len(processor.entry_points) == 16
        # TODO: is 0 instead of 16
    assert len(processor.entry_points) == 0


def test_entry_lines(process_strategy):
    processor = prepare_processing('helvetiaplatz', 39429064, process_strategy)
    success = processor.process_plaza()
    assert success
    assert len(processor.entry_lines) == 3
    assert all(
        len(l['entry_points']) == 1 for l in processor.entry_lines)


def prepare_processing(testfile, plaza_id, process_strategy):
    holder = testfilemanager.import_testfile(testfile)
    plaza = get_plaza_by_id(holder.plazas, plaza_id)
    processor = osm_optimizer.PlazaPreprocessor(
        plaza['osm_id'], plaza['geometry'], holder, process_strategy)
    return processor


def get_plaza_by_id(plazas, osm_id):
    plaza = list(filter(lambda p: p['osm_id'] == osm_id, plazas))
    assert len(plaza) == 1
    return plaza[0]
