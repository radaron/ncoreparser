import os
import functools
from typing import List
import httpx
from ncoreparser.models import AuthResponse, UserResponse, TorrentSearchResult
from ncoreparser.data import (
    URLs,
    URLsV2,
    SearchParamType,
    SearchParamTypeV2,
    SearchParamWhere,
    ParamSort,
    ParamSortV2,
    ParamSeq,
    ParamSeqV2
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
from ncoreparser.torrent import Torrent, TorrentV2


def _check_login(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self._logged_in:  # pylint: disable=protected-access
            raise NcoreConnectionError("Cannot login to tracker. "
                                       f"Please use {Client.login.__name__} function first.")
        return func(self, *args, **kwargs)
    return wrapper


class Client:
    def __init__(self, timeout=1):
        self._client = httpx.Client(headers={'User-Agent': 'python ncoreparser'},
                                    timeout=timeout,
                                    follow_redirects=True)
        self._logged_in = False
        self._page_parser = TorrentsPageParser()
        self._detailed_parser = TorrenDetailParser()
        self._rss_parser = RssParser()
        self._activity_parser = ActivityParser()
        self._recommended_parser = RecommendedParser()

    def login(self, username, password):
        self._client.cookies.clear()
        try:
            r = self._client.post(URLs.LOGIN.value,
                                  data={"nev": username, "pass": password})
        except Exception as e:
            raise NcoreConnectionError(f"Error while perform post "
                                       f"method to url '{URLs.LOGIN.value}'.") from e
        if r.url != URLs.INDEX.value:
            self.logout()
            raise NcoreCredentialError(f"Error while login, check "
                                       f"credentials for user: '{username}'")
        self._logged_in = True

    @_check_login
    # pylint: disable=too-many-arguments
    def search(self, pattern, type=SearchParamType.ALL_OWN, where=SearchParamWhere.NAME,
               sort_by=ParamSort.UPLOAD, sort_order=ParamSeq.DECREASING, number=None):
        page_count = 1
        torrents = []
        while number is None or len(torrents) < number:
            url = URLs.DOWNLOAD_PATTERN.value.format(page=page_count,
                                                     t_type=type.value,
                                                     sort=sort_by.value,
                                                     seq=sort_order.value,
                                                     pattern=pattern,
                                                     where=where.value)
            try:
                request = self._client.get(url)
            except Exception as e:
                raise NcoreConnectionError(f"Error while searhing torrents. {e}") from e
            new_torrents = [Torrent(**params) for params in self._page_parser.get_items(request.text)]
            if number is None or len(new_torrents) == 0:
                return torrents
            torrents.extend(new_torrents)
            page_count += 1
        return torrents[:number]

    @_check_login
    def get_torrent(self, id, **ext_params):
        url = URLs.DETAIL_PATTERN.value.format(id=id)
        try:
            content = self._client.get(url)
        except Exception as e:
            raise NcoreConnectionError(f"Error while get detailed page. Url: '{url}'. {e}") from e
        params = self._detailed_parser.get_item(content.text)
        params["id"] = id
        params.update(ext_params)
        return Torrent(**params)

    @_check_login
    def get_by_rss(self, url):
        try:
            content = self._client.get(url)
        except Exception as e:
            raise NcoreConnectionError(f"Error while get rss. Url: '{url}'. {e}") from e

        torrents = []
        for id in self._rss_parser.get_ids(content.text):
            torrents.append(self.get_torrent(id))
        return torrents

    @_check_login
    def get_by_activity(self):
        try:
            content = self._client.get(URLs.ACTIVITY.value)
        except Exception as e:
            raise NcoreConnectionError(f"Error while get activity. Url: '{URLs.ACTIVITY.value}'. {e}") from e

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
            content = self._client.get(URLs.RECOMMENDED.value)
        except Exception as e:
            raise NcoreConnectionError(f"Error while get recommended. Url: '{URLs.RECOMMENDED.value}'. {e}") from e

        all_recommended = [self.get_torrent(id) for id in self._recommended_parser.get_ids(content.text)]
        return [torrent for torrent in all_recommended if not type or torrent['type'] == type]

    @_check_login
    def download(self, torrent, path, override=False):
        file_path, url = torrent.prepare_download(path)
        try:
            content = self._client.get(url)
        except Exception as e:
            raise NcoreConnectionError(f"Error while downloading torrent. Url: '{url}'. {e}") from e
        if not override and os.path.exists(file_path):
            raise NcoreDownloadError(f"Error while downloading file: '{file_path}'. It is already exists.")
        with open(file_path, 'wb') as fh:
            fh.write(content.content)
        return file_path

    def logout(self):
        self._client.cookies.clear()
        self._client.close()
        self._logged_in = False


class ClientV2:
    def __init__(self, timeout=1):
        self._client = httpx.Client(headers={'User-Agent': 'python ncoreparser'},
                                    timeout=timeout,
                                    follow_redirects=True)
        self._logged_in = False
        self._user_info: UserResponse = None

    def login(self, username, password):
        self._client.cookies.clear()
        try:
            response = self._client.post(URLsV2.LOGIN.value,
                                         data={"nev": username, "pass": password})
        except Exception as e:
            raise NcoreConnectionError(f"Error while perform post "
                                       f"method to url '{URLsV2.LOGIN.value}'.") from e
        if response.url != URLs.INDEX.value:
            self.logout()
            raise NcoreCredentialError(f"Error while login, check "
                                       f"credentials for user: '{username}'")
        self._logged_in = True
        self._fetch_user_info()
        self._client.headers['Authorization'] = f'Bearer {self._user_info.token}'

    def _fetch_user_info(self):
        try:
            response = self._client.get(URLsV2.AUTH.value)
        except Exception as e:
            raise NcoreConnectionError(f"Error while get auth token. {e}") from e
        self._user_info = AuthResponse(**response.json()).user

    @_check_login
    # pylint: disable=too-many-arguments
    def search(self, pattern, types=SearchParamTypeV2.all, sort_by=ParamSortV2.UPLOAD,
               sort_order=ParamSeqV2.DECREASING, number=None) -> List[TorrentV2]:
        page_count = 0
        torrents = []
        while number is None or len(torrents) < number:
            query_params = {
                'pi': page_count,
                'oby': sort_by.value,
                'odir': sort_order.value,
                'q': pattern,
                'categories': [type.value for type in types] if isinstance(types, list) else [types.value]
            }

            try:
                request = self._client.get(URLsV2.TORRENTS_BASE.value, params=query_params)
                request.raise_for_status()
            except Exception as e:
                raise NcoreConnectionError(f"Error while searhing torrents. {e}") from e
            new_torrents = [TorrentV2(torrent_response=torrent_response, key=self._user_info.tracker_key)
                            for torrent_response in TorrentSearchResult(**request.json()).torrents]
            if number is None or len(new_torrents) == 0:
                return torrents
            torrents.extend(new_torrents)
            page_count += 1
        return torrents[:number]

    @_check_login
    def download(self, torrent: TorrentV2, path: str, override: bool = False) -> str:
        file_path, url = torrent.prepare_download(path)
        try:
            content = self._client.get(url)
        except Exception as e:
            raise NcoreConnectionError(f"Error while downloading torrent. Url: '{url}'. {e}") from e
        if not override and os.path.exists(file_path):
            raise NcoreDownloadError(f"Error while downloading file: '{file_path}'. It is already exists.")
        with open(file_path, 'wb') as fh:
            fh.write(content.content)
        return file_path

    def logout(self):
        self._client.cookies.clear()
        self._client.close()
        self._logged_in = False
