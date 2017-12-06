import pytest
import os
import testfilemanager
from os import path, remove
from plaza_preprocessing import __main__, configuration


@pytest.fixture
def config():
    config_path = 'testconfig.yml'
    yield configuration.load_config(config_path)
    os.remove(config_path)


def test_main(config):
    testfile = testfilemanager.get_testfile_name('helvetiaplatz')
    out_file = 'helvetiaplatz-merged.osm'
    try:
        __main__.preprocess_osm(testfile, out_file, config)
        assert path.exists(out_file)
    finally:
        remove(out_file)
