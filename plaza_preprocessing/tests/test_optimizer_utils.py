import pytest
from plaza_preprocessing.osm_optimizer import utils


def test_bounding_boxes_overlap():
    assert utils.bounding_boxes_overlap(0, 0, 1, 1, 0, 0, 1, 1)
    assert utils.bounding_boxes_overlap(0, 0, 2, 2, 0, 1, 4, 5)
    assert utils.bounding_boxes_overlap(0, 0, 2, 2, -1, -1, 1, 1)
    assert not utils.bounding_boxes_overlap(0, 0, 1, 1, 0, 1, 1, 2)
    assert not utils.bounding_boxes_overlap(0, 0, -1, -1, -1, 0, -2, -1)
    assert not utils.bounding_boxes_overlap(0, 0, 1, 1, -1, -1, 0, 0)
    assert not utils.bounding_boxes_overlap(-1, -1, 0, 0, 0, 0, 1, -1)
