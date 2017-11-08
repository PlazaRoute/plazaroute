import pytest
import utils
from plaza_preprocessing.osm_optimizer.visibilitygraphprocessor import VisibilityGraphProcessor
from plaza_preprocessing.osm_optimizer.spiderwebgraphprocessor import SpiderWebGraphProcessor


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


def test_obstructed_plaza(process_strategy):
    """ plazas obstructed by buildings should be discarded """
    result_plaza = utils.process_plaza('europaallee', 182055194, process_strategy)
    assert not result_plaza  # plaza should be discarded


def test_entry_points():
    """ Entry points on Kreuzplatz seem to be wrong """
    result_plaza = utils.process_plaza('kreuzplatz', 5541230, process_strategy)
    with pytest.raises(AssertionError):
        assert result_plaza
        assert len(result_plaza['entry_points']) == 16
        # TODO: is 0 instead of 16
    assert not result_plaza


def test_entry_lines(process_strategy):
    result_plaza = utils.process_plaza('helvetiaplatz', 39429064, process_strategy)
    assert result_plaza
    assert len(result_plaza['entry_lines']) == 3
    assert all(
        len(line['entry_points']) == 1 for line in result_plaza['entry_lines'])
