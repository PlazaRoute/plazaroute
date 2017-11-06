from sys import argv
from plaza_preprocessing.osm_optimizer import osm_optimizer
from plaza_preprocessing import osm_importer
from plaza_preprocessing.osm_merger import osm_merger

def preprocess_osm(osm_filename, out_file):
    osm_holder = osm_importer.import_osm(osm_filename)
    processed_plazas = osm_optimizer.preprocess_plazas(osm_holder)

    osm_merger.merge_plaza_graphs(processed_plazas, osm_filename, out_file)

if len(argv) != 3:
    print('usage: plaza_preprocessing <osm-source-file> <merged-file-dest>')
    exit(1)
preprocess_osm(argv[1], argv[2])
