import os
from ncoreparser.data import URLs


class Torrent:
    def __init__(self, id, title, key, size, type, date, seed, leech):
        self._details = {}
        self._details["id"] = int(id)
        self._details["title"] = title
        self._details["key"] = key
        self._details["size"] = size
        self._details["type"] = type
        self._details["date"] = date
        self._details["seed"] = seed
        self._details["leech"] = leech
        self._details["download"] = URLs.DOWNLOAD_LINK.value.format(id=id, key=key)

    def __getitem__(self, key):
        return self._details[key]

    def keys(self):
        return self._details.keys()

    def __str__(self):
        return "<Torrent {}>".format(self._details['id'])

    def __repr__(self):
        return "<Torrent {}>".format(self._details['id'])

    def prepare_download(self, path):
        filename = self._details['title'].replace(' ', '_') + '.torrent'
        filepath = os.path.join(path, filename)
        url = self._details['download']
        return filepath, url
