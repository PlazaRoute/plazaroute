import testfilemanager
from plaza_preprocessing.optimizer import optimizer


def process_plaza(testfile, plaza_id, process_strategy, shortest_path_strategy):
    holder = testfilemanager.import_testfile(testfile)
    plaza = get_plaza_by_id(holder.plazas, plaza_id)

    processor = optimizer.PlazaPreprocessor(holder, process_strategy, shortest_path_strategy)
    return processor._process_plaza(plaza)


def get_plaza_by_id(plazas, osm_id):
    plaza = list(filter(lambda p: p['osm_id'] == osm_id, plazas))
    assert len(plaza) == 1
    return plaza[0]
