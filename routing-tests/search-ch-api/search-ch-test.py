import requests
import sys

this = sys.modules[__name__]
this.search_ch_url = 'https://timetable.search.ch/api/route.json'


def get_timetable(start, destination):
    payload = {'from': start, 'to': destination}
    req = requests.get(this.search_ch_url, params=payload)

    print(req.url)
    print(req.json())


if __name__ == '__main__':
    start = 'Sternen Oerlikon'
    destination = 'Hallenband Oerlikon'
    get_timetable(start, destination)
