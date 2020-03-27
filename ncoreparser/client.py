import requests
import os
from ncoreparser.data import (
    URLs, 
    SearchParamType, 
    ParamSort, 
    ParamSeq, 
    ParamSearchWhere
)
from ncoreparser.error import (
    NcoreConnectionError,
    NcoreCredentialError, 
    NcoreDownloadError
)
from ncoreparser.constant import TORRENTS_PER_PAGE
from ncoreparser.parser import TorrentsPageParser
from ncoreparser.torrent import Torrent


class Client:
    def __init__(self):
        self._session = requests.session()
        self._session.cookies.clear()
        self._parser = TorrentsPageParser()

    def open(self, username, password):
        try:
            r = self._session.post(URLs.LOGIN.value,
                                   {"nev": username, "pass": password})
        except Exception:
            raise NcoreConnectionError(f"Error while perform post "
                                       f"method to url '{URLs.LOGIN.value}'.")
        if r.url != URLs.INDEX.value:
            self._session.close()
            raise NcoreCredentialError(f"Error while login, check "
                                       f"credentials for user: '{username}'")

    def search(self, pattern, type=SearchParamType.ALL_OWN,  where=ParamSearchWhere.NAME,
               sort_by=ParamSort.UPLOAD, sort_order=ParamSeq.DECREASING, number=TORRENTS_PER_PAGE):
        item_count = 0
        torrents = []
        while item_count < number:
            url = URLs.DOWNLOAD_PATTERN.value.format(page="",
                                                     t_type=type.value,
                                                     sort=sort_by.value,
                                                     seq=sort_order.value,
                                                     pattern=pattern,
                                                     where=where.value)
            try:
                request = self._session.get(url)
            except ConnectionError as e:
                raise NcoreConnectionError(f"Error while searhing torrents. {e}")
            new_torrents = [Torrent(**params) for params in self._parser.get_items(request.text)]
            item_count += len(new_torrents)
            torrents.extend(new_torrents)
        return torrents[:number]
    
    def get_torrent(self, id):
        pass

    def get_by_rss(self, url):
        pass

    def download(self, torrent, path):
        file_path, url = torrent.prepare_download(path)
        try:
            content = self._session.get(url)
        except ConnectionError as e:
            raise NcoreConnectionError(f"Error while downloading torrent. Url: '{url}'. {e}")
        if os.path.exists(file_path):
            raise NcoreDownloadError(f"Error while downloading file: '{file_path}'. It is already exists.")
        with open(file_path, 'wb') as fh:
            fh.write(content.content)
        return file_path

    def close(self):
        self._session.close()
