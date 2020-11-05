import requests
import os
from ncoreparser.data import (
    URLs,
    SearchParamType,
    SearchParamWhere,
    ParamSort,
    ParamSeq
)
from ncoreparser.error import (
    NcoreConnectionError,
    NcoreCredentialError,
    NcoreDownloadError
)
from ncoreparser.parser import (
    TorrentsPageParser,
    TorrenDetailParser,
    RssParser,
    ActivityParser,
    RecommendedParser
)
from ncoreparser.torrent import Torrent
from ncoreparser.constant import TORRENTS_PER_PAGE


class Client:
    def __init__(self, timeout=1):
        self._session = requests.session()
        self._session.cookies.clear()
        self._session.headers.update({'User-Agent': 'python ncoreparser'})
        self.timeout = timeout
        self._page_parser = TorrentsPageParser()
        self._detailed_parser = TorrenDetailParser()
        self._rss_parser = RssParser()
        self._activity_parser = ActivityParser()
        self._recommended_parser = RecommendedParser()

    def open(self, username, password):
        try:
            r = self._session.post(URLs.LOGIN.value,
                                   {"nev": username, "pass": password},
                                   timeout=self.timeout)
        except Exception:
            raise NcoreConnectionError("Error while perform post "
                                       "method to url '{}'.".format(URLs.LOGIN.value))
        if r.url != URLs.INDEX.value:
            self._session.close()
            raise NcoreCredentialError("Error while login, check "
                                       "credentials for user: '{}'".format(username))

    def search(self, pattern, type=SearchParamType.ALL_OWN,  where=SearchParamWhere.NAME,
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
                request = self._session.get(url, timeout=self.timeout)
            except Exception as e:
                raise NcoreConnectionError("Error while searhing torrents. {}".format(e))
            new_torrents = [Torrent(**params) for params in self._page_parser.get_items(request.text)]
            if len(new_torrents) == 0:
                return torrents
            item_count += len(new_torrents)
            torrents.extend(new_torrents)
        return torrents[:number]

    def get_torrent(self, id):
        url = URLs.DETAIL_PATTERN.value.format(id=id)
        try:
            content = self._session.get(url, timeout=self.timeout)
        except Exception as e:
            raise NcoreConnectionError("Error while get detailed page. Url: '{}'. {}".format(url, e))
        params = self._detailed_parser.get_item(content.text)
        params["id"] = id
        return Torrent(**params)

    def get_by_rss(self, url):
        try:
            content = self._session.get(url, timeout=self.timeout)
        except Exception as e:
            raise NcoreConnectionError("Error while get rss. Url: '{}'. {}".format(url, e))

        torrents = []
        for id in self._rss_parser.get_ids(content.text):
            torrents.append(self.get_torrent(id))
        return torrents

    def get_by_activity(self):
        try:
            content = self._session.get(URLs.ACTIVITY.value, timeout=self.timeout)
        except Exception as e:
            raise NcoreConnectionError("Error while get activity. Url: '{}'. {}".format(URLs.ACTIVITY.value, e))

        torrents = []
        for id in self._activity_parser.get_ids(content.text):
            torrents.append(self.get_torrent(id))
        return torrents

    def get_recommended(self, type=None):
        try:
            content = self._session.get(URLs.RECOMMENDED.value, timeout=self.timeout)
        except Exception as e:
            raise NcoreConnectionError("Error while get recommended. Url: '{}'. {}".format(URLs.RECOMMENDED.value, e))

        all_recommended = [self.get_torrent(id) for id in self._recommended_parser.get_ids(content.text)]
        return [torrent for torrent in all_recommended if not type or torrent['type'] == type]

    def download(self, torrent, path, override=False):
        file_path, url = torrent.prepare_download(path)
        try:
            content = self._session.get(url, timeout=self.timeout)
        except Exception as e:
            raise NcoreConnectionError("Error while downloading torrent. Url: '{}'. {}".format(url, e))
        if not override and os.path.exists(file_path):
            raise NcoreDownloadError("Error while downloading file: '{}'. It is already exists.".format(file_path))
        with open(file_path, 'wb') as fh:
            fh.write(content.content)
        return file_path

    def close(self):
        self._session.close()
