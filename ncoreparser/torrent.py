import os
from ncoreparser.data import URLs, URLsV2, SearchParamTypeV2
from ncoreparser.models import TorrentResponse
from ncoreparser.util import Size


class Torrent:
    def __init__(self, id, title, key, size,  # pylint: disable=too-many-arguments
                 type, date, seed, leech, **params):  # pylint: disable=too-many-arguments
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
        self._details.update(params)

    def __getitem__(self, key):
        return self._details[key]

    def keys(self):
        return self._details.keys()

    def __str__(self):
        return f"<Torrent {self._details['id']}>"

    def __repr__(self):
        return f"<Torrent {self._details['id']}>"

    def prepare_download(self, path):
        filename = self._details['title'].replace(' ', '_') + '.torrent'
        filepath = os.path.join(path, filename)
        url = self._details['download']
        return filepath, url


class TorrentV2:
    def __init__(self, torrent_response: TorrentResponse, key: str):
        self._details = torrent_response.model_dump()
        self._details["title"] = torrent_response.release_name
        self._details["type"] = SearchParamTypeV2(torrent_response.category)
        self._details["date"] = torrent_response.created_at
        self._details["seed"] = torrent_response.seeders
        self._details["leech"] = torrent_response.leechers
        self._details["size"] = Size(torrent_response.size)
        self._key = key

    def __getitem__(self, key):
        return self._details[key]

    def keys(self):
        return self._details.keys()

    def __str__(self):
        return f"<Torrent {self._details['id']}>"

    def __repr__(self):
        return f"<Torrent {self._details['id']}>"

    def prepare_download(self, path):
        filename = self._details['release_name'].replace(' ', '_') + '.torrent'
        filepath = os.path.join(path, filename)
        url = URLsV2.DOWNLOAD_LINK.value.format(id=self._details['id'], key=self._key)
        return filepath, url
