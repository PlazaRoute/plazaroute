import logging
import sys
import argparse
from plaza_preprocessing.importer import importer
from plaza_preprocessing.merger import merger
from plaza_preprocessing.optimizer import optimizer, shortest_paths
from plaza_preprocessing.optimizer.graphprocessor.graphprocessor import GraphProcessor
from plaza_preprocessing.optimizer.graphprocessor.visibilitygraph import VisibilityGraphProcessor
from plaza_preprocessing.optimizer.graphprocessor.spiderwebgraph import SpiderWebGraphProcessor
from plaza_preprocessing import configuration

logger = logging.getLogger('plaza_preprocessing')


def plaza_preprocessing():
    """entry point"""
    source, destination, config_file, verbose_log = parse_args(sys.argv[1:])

    setup_logging(verbose=verbose_log)
    config = configuration.load_config(config_file)
    preprocess_osm(source, destination, config)


def preprocess_osm(osm_filename: str, out_file: str, config: dict):
    shortest_path_strategy = _get_shortest_path_strategy(config)
    process_strategy = _get_process_strategy(config)
    logger.info(f"Using {config['graph-strategy']} graph with {config['shortest-path-algorithm']} algorithm")
    osm_holder = importer.import_osm(osm_filename, config['tag-filter'])

    processed_plazas = optimizer.preprocess_plazas(osm_holder, process_strategy, shortest_path_strategy, config)
    merger.merge_plaza_graphs(processed_plazas, osm_filename, out_file, config['footway-tags'])


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


def parse_args(args):
    parser = argparse.ArgumentParser(description='Preprocess an OSM file for pedestrian routing over plazas.')
    parser.add_argument('source', help='input OSM file to process')
    parser.add_argument('destination', help='destination OSM file')
    parser.add_argument('--config', default='plaza_preprocessing_config.yml', metavar="filename",
                        help='specify a config file location. A default config will be created'
                             ' if the path does not exist')
    parser.add_argument('-v', action='store_true', help='verbose log output')

    if len(args) == 0:
        parser.print_help()
        sys.exit(1)

    result = parser.parse_args(args)
    return result.source, result.destination, result.config, result.v


def _get_process_strategy(config: dict) -> GraphProcessor:
    strategy_config = config['graph-strategy']
    if strategy_config == 'visibility':
        return VisibilityGraphProcessor()
    elif strategy_config == 'spiderweb':
        spacing = config['spiderweb-grid-size']
        return SpiderWebGraphProcessor(spacing_m=spacing)
    else:
        raise ValueError("invalid value for process strategy")


def _get_shortest_path_strategy(config: dict):
    strategy_config = config['shortest-path-algorithm']
    if strategy_config == 'astar':
        return shortest_paths.compute_astar_shortest_paths
    elif strategy_config == 'dijkstra':
        return shortest_paths.compute_dijkstra_shortest_paths
    else:
        raise ValueError("invalid value for shortest path algorithm")


if __name__ == "__main__":
    plaza_preprocessing()
