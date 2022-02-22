import requests
import os
import functools
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
from ncoreparser.util import Size
from ncoreparser.torrent import Torrent
from ncoreparser.constant import TORRENTS_PER_PAGE


def _check_login(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self._logged_in:
            raise NcoreConnectionError("Cannot login to tracker. "
                                       f"Please use {Client.open.__name__} function first.")
        return func(self, *args, **kwargs)
    return wrapper


class Client:
    def __init__(self, timeout=1):
        self._session = requests.session()
        self._session.headers.update({'User-Agent': 'python ncoreparser'})
        self._logged_in = False
        self._page_parser = TorrentsPageParser()
        self._detailed_parser = TorrenDetailParser()
        self._rss_parser = RssParser()
        self._activity_parser = ActivityParser()
        self._recommended_parser = RecommendedParser()
        self.timeout = timeout

    def open(self, *args, **kwargs):
        print("Deprecation warning! Use login instead!")
        self.login(*args, **kwargs)

    def close(self, *args, **kwargs):
        print("Deprecation warning! Use logout instead!")
        self.logout(*args, **kwargs)

    def login(self, username, password):
        self._session.cookies.clear()
        try:
            r = self._session.post(URLs.LOGIN.value,
                                   {"nev": username, "pass": password},
                                   timeout=self.timeout)
        except Exception:
            raise NcoreConnectionError("Error while perform post "
                                       "method to url '{}'.".format(URLs.LOGIN.value))
        if r.url != URLs.INDEX.value:
            self.logout()
            raise NcoreCredentialError("Error while login, check "
                                       "credentials for user: '{}'".format(username))
        self._logged_in = True

    @_check_login
    def search(self, pattern, type=SearchParamType.ALL_OWN, where=SearchParamWhere.NAME,
               sort_by=ParamSort.UPLOAD, sort_order=ParamSeq.DECREASING, number=TORRENTS_PER_PAGE):
        page_count = 0
        torrents = []
        while page_count * TORRENTS_PER_PAGE < number:
            url = URLs.DOWNLOAD_PATTERN.value.format(page=page_count + 1,
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
            torrents.extend(new_torrents)
            page_count += 1
        return torrents[:number]

    @_check_login
    def get_torrent(self, id, **ext_params):
        url = URLs.DETAIL_PATTERN.value.format(id=id)
        try:
            content = self._session.get(url, timeout=self.timeout)
        except Exception as e:
            raise NcoreConnectionError("Error while get detailed page. Url: '{}'. {}".format(url, e))
        params = self._detailed_parser.get_item(content.text)
        params["id"] = id
        params.update(ext_params)
        return Torrent(**params)

    @_check_login
    def get_by_rss(self, url):
        try:
            content = self._session.get(url, timeout=self.timeout)
        except Exception as e:
            raise NcoreConnectionError("Error while get rss. Url: '{}'. {}".format(url, e))

        torrents = []
        for id in self._rss_parser.get_ids(content.text):
            torrents.append(self.get_torrent(id))
        return torrents

    @_check_login
    def get_by_activity(self):
        try:
            content = self._session.get(URLs.ACTIVITY.value, timeout=self.timeout)
        except Exception as e:
            raise NcoreConnectionError("Error while get activity. Url: '{}'. {}".format(URLs.ACTIVITY.value, e))

        torrents = []
        for id, start_t, updated_t, status, uploaded, downloaded, remaining_t, rate in \
                self._activity_parser.get_params(content.text):
            torrents.append(self.get_torrent(id,
                                             start=start_t,
                                             updated=updated_t,
                                             status=status,
                                             uploaded=Size(uploaded),
                                             downloaded=Size(downloaded),
                                             remaining=remaining_t,
                                             rate=float(rate)))
        return torrents

    @_check_login
    def get_recommended(self, type=None):
        try:
            content = self._session.get(URLs.RECOMMENDED.value, timeout=self.timeout)
        except Exception as e:
            raise NcoreConnectionError("Error while get recommended. Url: '{}'. {}".format(URLs.RECOMMENDED.value, e))

        all_recommended = [self.get_torrent(id) for id in self._recommended_parser.get_ids(content.text)]
        return [torrent for torrent in all_recommended if not type or torrent['type'] == type]

    @_check_login
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

    def logout(self):
        self._session.cookies.clear()
        self._session.close()
        self._logged_in = False
