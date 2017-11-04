import pytest
import testfilemanager
from shapely.geometry import LineString, Point
from plaza_preprocessing.osm_merger.osm_writer import OSMWriter
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
    osm_writer = OSMWriter()
    edges = [
        LineString([(0,0), (1,1)]),
        LineString([(0,1), (3,4), (1, 1)])
    ]
    entry_points = [Point(0, 0), Point(3, 4)]
    plaza = {
        'graph_edges': edges,
        'entry_points': entry_points,
        'outer_ring_id': 42
        }
    osm_writer.read_plazas([plaza])
    assert len(osm_writer.nodes) == 4
    assert len(osm_writer.ways) == 2
    assert osm_writer.ways[1].nodes[2] == osm_writer.ways[0].nodes[1]
    assert len(osm_writer.entry_node_mappings[42]) == 2


def test_read_real_plaza(process_strategy):
    plaza, processor = prepare_processing('helvetiaplatz', 4533221, process_strategy)
    edges = processor.process_plaza()
    entry_points = processor.entry_points
    assert edges
    assert len(entry_points) > 2
    plaza['graph_edges'] = edges
    plaza['entry_points'] = entry_points

    osm_writer = OSMWriter()
    osm_writer.read_plazas([plaza])
    assert len(osm_writer.ways) == len(edges)
    assert len(osm_writer.nodes) < len(edges) / 2
    ring_id = plaza['outer_ring_id']
    assert ring_id in osm_writer.entry_node_mappings
    assert len(osm_writer.entry_node_mappings[ring_id]) == len(entry_points)


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
