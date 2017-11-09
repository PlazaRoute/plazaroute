import pytest
import testfilemanager
from os import path, remove
from plaza_preprocessing import __main__


def test_main():
    testfile = testfilemanager.get_testfile_name('helvetiaplatz')
    out_file = 'helvetiaplatz-merged.osm'
    try:
        __main__.preprocess_osm(testfile, out_file)
        assert path.exists(out_file)
    finally:
        remove(out_file)
