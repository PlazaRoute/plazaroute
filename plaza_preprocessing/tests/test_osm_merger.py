import pytest
import os.path
import testfilemanager
from shapely.geometry import LineString, Point
from plaza_preprocessing.osm_merger.plazawriter import PlazaWriter
import plaza_preprocessing.osm_merger.osm_merger as osm_merger
from plaza_preprocessing.osm_optimizer import osm_optimizer
from plaza_preprocessing.osm_optimizer.visibilitygraphprocessor import VisibilityGraphProcessor
from plaza_preprocessing.osm_optimizer.spiderwebgraphprocessor import SpiderWebGraphProcessor


@pytest.fixture(params=['visibility', 'spiderweb'])
def process_strategy(request):
    if request.param == 'visibility':
        return VisibilityGraphProcessor()
    elif request.param == 'spiderweb':
        return SpiderWebGraphProcessor(spacing_m=5)


def test_read_plaza():
    plaza_writer = PlazaWriter()
    plaza = create_test_plaza()
    plaza_writer.read_plazas([plaza])
    assert len(plaza_writer.nodes) == 4
    assert len(plaza_writer.ways) == 2
    assert plaza_writer.ways[1].nodes[2] == plaza_writer.ways[0].nodes[1]
    assert len(plaza_writer.entry_node_mappings[99]) == 1


def test_read_real_plaza(process_strategy):
    plaza, processor = prepare_processing(
        'helvetiaplatz', 4533221, process_strategy)
    success = processor.process_plaza()
    assert success
    edges = processor.graph_edges
    entry_points = processor.entry_points
    entry_lines = processor.entry_lines
    assert edges
    assert entry_lines
    assert len(entry_points) > 2
    plaza['graph_edges'] = edges
    plaza['entry_points'] = entry_points
    plaza['entry_lines'] = entry_lines

    plaza_writer = PlazaWriter()
    plaza_writer.read_plazas([plaza])
    assert len(plaza_writer.ways) == len(edges)
    assert len(plaza_writer.nodes) < len(edges) / 2
    way_id = 259200019  # footway with 2 entry points
    assert way_id in plaza_writer.entry_node_mappings
    assert len(plaza_writer.entry_node_mappings[way_id]) == 2


def test_write_to_file():
    plaza_writer = PlazaWriter()
    plaza = create_test_plaza()
    plaza_writer.read_plazas([plaza])
    filename = 'testfile.osm'
    try:
        plaza_writer.write_to_file('testfile.osm')
        assert os.path.exists(filename)
    finally:
        os.remove(filename)


def test_write_to_file_real_plaza(process_strategy):
    plaza, processor = prepare_processing(
        'helvetiaplatz', 4533221, process_strategy)
    success = processor.process_plaza()
    assert success
    edges = processor.graph_edges
    entry_points = processor.entry_points
    entry_lines = processor.entry_lines
    plaza['graph_edges'] = edges
    plaza['entry_points'] = entry_points
    plaza['entry_lines'] = entry_lines

    plaza_writer = PlazaWriter()
    plaza_writer.read_plazas([plaza])
    filename = 'testfile.osm'
    try:
        plaza_writer.write_to_file('testfile.osm')
        assert os.path.exists(filename)
    finally:
        os.remove(filename)


def test_merge_plaza_graphs(process_strategy):
    plaza, processor = prepare_processing(
        'helvetiaplatz', 4533221, process_strategy)
    # plaza, processor = prepare_processing(
    #     'bahnhofplatz_bern', 5117701, process_strategy)
    success = processor.process_plaza()
    assert success
    edges = processor.graph_edges
    entry_points = processor.entry_points
    entry_lines = processor.entry_lines
    plaza['graph_edges'] = edges
    plaza['entry_points'] = entry_points
    plaza['entry_lines'] = entry_lines

    merged_filename = 'testfile-merged.osm'
    try:
        osm_merger.merge_plaza_graphs(
            [plaza], testfilemanager.get_testfile_name('helvetiaplatz'),
            merged_filename)
        assert os.path.exists(merged_filename)

    finally:
        # os.remove(merged_filename)
        pass

def test_merge_simple_plaza(process_strategy):
    plaza, processor = prepare_processing(
        'helvetiaplatz', 39429064, process_strategy)
    success = processor.process_plaza()
    assert success
    edges = processor.graph_edges
    entry_points = processor.entry_points
    entry_lines = processor.entry_lines

    plaza['graph_edges'] = edges
    plaza['entry_points'] = entry_points
    plaza['entry_lines'] = entry_lines

    merged_filename = 'testfile-merged.osm'
    try:
        osm_merger.merge_plaza_graphs(
            [plaza], testfilemanager.get_testfile_name('helvetiaplatz'),
            merged_filename)
        assert os.path.exists(merged_filename)
    finally:
        os.remove(merged_filename)

def test_find_exact_insert_position():
    entry_point = Point(2, 2)
    way_nodes = [
        {'id': 1, 'coords': (0, 0)},
        {'id': 2, 'coords': (2, 0)},
        {'id': 3, 'coords': (2, 2)},
        {'id': 4, 'coords': (0, 2)},
    ]
    pos = osm_merger._find_exact_insert_position(entry_point, way_nodes)
    assert pos == 2


def test_find_interpolated_insert_position():
    entry_point = Point(2.5, 1)
    way_nodes = [
        {'id': 1, 'coords': (0, 0)},
        {'id': 2, 'coords': (2, 0)},
        {'id': 3, 'coords': (3, 2)},
        {'id': 4, 'coords': (1, 2)},
    ]
    pos = osm_merger._find_interpolated_insert_position(
        entry_point, way_nodes)
    assert pos == 2


def test_insert_entry_nodes():
    entry_ways = {
        '42': {
            'version': 1,
            'nodes': [
                {'id': 1, 'coords': (0, 0)},
                {'id': 2, 'coords': (2, 0)},
                {'id': 3, 'coords': (3, 2)},
                {'id': 4, 'coords': (1, 2)},
            ]
        }
    }
    entry_node_mappings = {
        '42': [
            {'id': -99, 'coords': (0, 0)},
            {'id': -98, 'coords': (1, 0)},
            {'id': -97, 'coords': (1.5, 2)},
            {'id': -96, 'coords': (1, 2)},
        ]
    }
    entry_ways_expected = {
        '42': {
            'version': 1,
            'nodes': [
                {'id': -99, 'coords': (0, 0)},
                {'id': 1, 'coords': (0, 0)},
                {'id': -98, 'coords': (1, 0)},
                {'id': 2, 'coords': (2, 0)},
                {'id': 3, 'coords': (3, 2)},
                {'id': -97, 'coords': (1.5, 2)},
                {'id': -96, 'coords': (1, 2)},
                {'id': 4, 'coords': (1, 2)}
            ]
        }
    }
    osm_merger.insert_entry_nodes(entry_ways, entry_node_mappings)
    assert entry_ways == entry_ways_expected


def create_test_plaza():
    plaza_writer = PlazaWriter()
    edges = [
        LineString([(0, 0), (1, 1)]),
        LineString([(0, 1), (3, 4), (1, 1)])
    ]
    entry_points = [Point(0, 0), Point(3, 4)]
    plaza = {
        'graph_edges': edges,
        'entry_points': entry_points,
        'entry_lines': [
            {
                'way_id': 99,
                'entry_points': [Point(0, 0)]
            },
            {
                'way_id': 98,
                'entry_points': [Point(3, 4)]
            }
        ]
    }
    return plaza


def prepare_processing(testfile, plaza_id, process_strategy):
    holder = testfilemanager.import_testfile(testfile)
    plaza = get_plaza_by_id(holder.plazas, plaza_id)
    processor = osm_optimizer.PlazaPreprocessor(
        plaza['osm_id'], plaza['geometry'], holder, process_strategy)
    return plaza, processor


def get_plaza_by_id(plazas, osm_id):
    plaza = list(filter(lambda p: p['osm_id'] == osm_id, plazas))
    assert len(plaza) == 1
    return plaza[0]
