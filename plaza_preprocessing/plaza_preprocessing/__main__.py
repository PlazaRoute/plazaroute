import logging
import sys

from plaza_preprocessing.importer import importer
from plaza_preprocessing.merger import merger
from plaza_preprocessing.optimizer import optimizer, shortest_paths
from plaza_preprocessing.optimizer.graphprocessor.visibilitygraph import VisibilityGraphProcessor
from plaza_preprocessing.optimizer.graphprocessor.spiderwebgraph import SpiderWebGraphProcessor

logger = logging.getLogger('plaza_preprocessing')


def setup_logging(verbose=False, quiet=False):
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
            '[%(levelname)-7s] - %(message)s')
    if verbose and not quiet:
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - [%(levelname)-7s] - %(message)s')
    if quiet:
        logger.setLevel(logging.WARNING)

    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.debug("Setting up logging complete")


def preprocess_osm(osm_filename, out_file):
    # TODO: Make configurable
    shortest_path_strategy = shortest_paths.compute_astar_shortest_paths
    osm_holder = importer.import_osm(osm_filename)
    processed_plazas = optimizer.preprocess_plazas(osm_holder, VisibilityGraphProcessor(), shortest_path_strategy)
    merger.merge_plaza_graphs(processed_plazas, osm_filename, out_file)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('usage: plaza_preprocessing <osm-source-file> <merged-file-dest>')
        exit(1)

    # TODO: make configurable
    setup_logging(verbose=True)
    preprocess_osm(sys.argv[1], sys.argv[2])
