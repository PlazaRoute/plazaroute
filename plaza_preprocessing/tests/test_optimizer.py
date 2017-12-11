import pytest
import testfilemanager
import utils
import os
import plaza_preprocessing.optimizer.optimizer as optimizer
from plaza_preprocessing.optimizer import shortest_paths
from plaza_preprocessing import configuration
from plaza_preprocessing.optimizer.graphprocessor.spiderwebgraph import SpiderWebGraphProcessor
from plaza_preprocessing.optimizer.graphprocessor.visibilitygraph import VisibilityGraphProcessor


@pytest.fixture(params=['visibility', 'spiderweb'])
def process_strategy(request):
    if request.param == 'visibility':
        return VisibilityGraphProcessor(visibility_delta_m=0.1)
    elif request.param == 'spiderweb':
        return SpiderWebGraphProcessor(spacing_m=5, visibility_delta_m=0.1)


@pytest.fixture(params=['astar', 'dijkstra'])
def shortest_path_strategy(request):
    if request.param == 'astar':
        return shortest_paths.compute_dijkstra_shortest_paths
    elif request.param == 'dijkstra':
        return shortest_paths.compute_astar_shortest_paths


@pytest.fixture
def config():
    config_path = 'testconfig.yml'
    yield configuration.load_config(config_path)
    os.remove(config_path)


def test_simple_plaza(process_strategy, shortest_path_strategy, config):
    result_plaza = utils.process_plaza('helvetiaplatz', 4533221, process_strategy, shortest_path_strategy, config)
    assert result_plaza
    assert len(result_plaza['graph_edges']) > 10
    assert len(result_plaza['entry_points']) == 7
    assert len(result_plaza['entry_lines']) == 5


def test_complicated_plaza(process_strategy, shortest_path_strategy, config):
    result_plaza = utils.process_plaza('bahnhofplatz_bern', 5117701, process_strategy, shortest_path_strategy, config)
    assert result_plaza
    assert len(result_plaza['graph_edges']) > 20
    assert len(result_plaza['entry_points']) == 49
    assert len(result_plaza['entry_lines']) == 22


def test_multiple_plazas(process_strategy, shortest_path_strategy, config):
    holder = testfilemanager.import_testfile('helvetiaplatz', config)
    processed_plazas = optimizer.preprocess_plazas(
        holder, process_strategy, shortest_path_strategy, config)

    assert len(processed_plazas) == 7
    all_edges = [edge.coords for plaza in processed_plazas for edge in plaza["graph_edges"]]
    assert len(set(all_edges)) == len(all_edges)  # check for duplicates


def test_optimized_lines_inside_plaza(process_strategy, shortest_path_strategy, config):
    holder = testfilemanager.import_testfile('bahnhofplatz_bern', config)
    plaza = utils.get_plaza_by_id(holder.plazas, 5117701)
    plaza_geometry = plaza['geometry']

    processor = optimizer.PlazaPreprocessor(
        holder, process_strategy, shortest_path_strategy, config)
    result_plaza = processor._process_plaza(plaza)

    assert result_plaza
    # all optimized lines should be inside the plaza geometry
    assert all(
        abs(plaza_geometry.intersection(line).length - line.length) <= 0.05 for line in result_plaza['graph_edges'])


def test_obstructed_plaza(process_strategy, shortest_path_strategy, config):
    """ plazas obstructed by buildings should be discarded """
    result_plaza = utils.process_plaza('europaallee', 182055194, process_strategy, shortest_path_strategy, config)
    assert not result_plaza  # plaza should be discarded


def test_almost_obstructed_plaza(process_strategy, shortest_path_strategy, config):
    """ this plaza is almost completely obstructed, but a tiny area remains"""
    result_plaza = utils.process_plaza('zuerich_hb', 6619147, process_strategy, shortest_path_strategy, config)
    assert not result_plaza  # plaza should be discarded


def test_barriers(process_strategy, shortest_path_strategy, config):
    """ test that a line obstacle (a barrier) is cut out"""
    result_plaza = utils.process_plaza('fischmarktplatz', 26261827, process_strategy, shortest_path_strategy, config)
    assert result_plaza['geometry'].area == 3.838230778253772e-07


def test_entry_points(process_strategy, shortest_path_strategy, config):
    """ Entry points on Kreuzplatz don't work with geometry.touches()"""
    result_plaza = utils.process_plaza('kreuzplatz', 5541230, process_strategy, shortest_path_strategy, config)
    assert result_plaza
    assert len(result_plaza['entry_points']) == 16


def test_entry_lines(process_strategy, shortest_path_strategy, config):
    result_plaza = utils.process_plaza('helvetiaplatz', 39429064, process_strategy, shortest_path_strategy, config)
    assert result_plaza
    assert len(result_plaza['entry_lines']) == 3
    assert all(
        len(line['entry_points']) == 1 for line in result_plaza['entry_lines'])


def test_bahnhofstrasse(process_strategy, shortest_path_strategy, config):
    """ one entry point is a couple mm outside the plaza, but should still be considered for the graph edges"""
    result_plaza = utils.process_plaza('bahnhofstrasse', 27405455, process_strategy, shortest_path_strategy, config)
    assert result_plaza
    assert len(result_plaza['graph_edges']) == 253


def test_entry_points_with_cutout_polygon(process_strategy, shortest_path_strategy, config):
    result_plaza = utils.process_plaza('zuerich_hb', 6605179, process_strategy, shortest_path_strategy, config)
    assert result_plaza
    assert len(result_plaza['entry_points']) == 9
