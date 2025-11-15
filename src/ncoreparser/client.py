import os
import sys
from typing import Dict, Optional

import httpx

from ncoreparser.data import URLs, SearchParamType, SearchParamWhere, ParamSort, ParamSeq
from ncoreparser.error import NcoreConnectionError, NcoreCredentialError, NcoreDownloadError
from ncoreparser.parser import TorrentsPageParser, TorrenDetailParser, RssParser, ActivityParser, RecommendedParser
from ncoreparser.util import Size, check_login, extract_cookies_from_client, set_cookies_to_client
from ncoreparser.torrent import Torrent
from ncoreparser.types import SearchResult
if sys.version_info >= (3, 10):
    from typing import Any, Generator, Union
else:
    from typing_extensions import Any, Generator, Union  # pylint: disable=no-name-in-module


class Client:
    # pylint: disable=too-many-instance-attributes
    def __init__(self, timeout: int = 1, cookies: Optional[Dict[str, str]] = None) -> None:
        self._client = httpx.Client(
            headers={"User-Agent": "python ncoreparser"}, timeout=timeout, follow_redirects=True
        )
        self._logged_in = False
        self._page_parser = TorrentsPageParser()
        self._detailed_parser = TorrenDetailParser()
        self._rss_parser = RssParser()
        self._activity_parser = ActivityParser()
        self._recommended_parser = RecommendedParser()
        self._allowed_cookies = ["nick", "pass", "stilus", "nyelv", "PHPSESSID"]
        if cookies:
            set_cookies_to_client(self._client, cookies, self._allowed_cookies, URLs.COOKIE_DOMAIN.value)
            if self._check_logged_in():
                self._logged_in = True

    def _check_logged_in(self) -> bool:
        try:
            r = self._client.get(URLs.INDEX.value)
            if "login.php" in str(r.url) or "<title>nCore</title>" in r.text:
                return False
            return True
        except Exception:  # pylint: disable=broad-except
            return False

    def login(self, username: str, password: str, twofactorcode: str = "") -> Dict[str, str]:
        if self._logged_in and self._check_logged_in():
            return extract_cookies_from_client(self._client, self._allowed_cookies)

        self._client.cookies.clear()
        self._logged_in = False

        try:
            login_data = {"nev": username, "pass": password, "set_lang": "hu", "submitted": "1", "ne_leptessen_ki": "1"}

            if twofactorcode:
                login_data["2factor"] = twofactorcode

            r = self._client.post(URLs.LOGIN.value, data=login_data)
        except Exception as e:
            raise NcoreConnectionError(f"Error while performing post method to url '{URLs.LOGIN.value}'.") from e

        if r.url != URLs.INDEX.value or "<title>nCore</title>" in r.text:
            self.logout()
            error_msg = f"Error while login, check credentials for user: '{username}'"
            if twofactorcode:
                error_msg += ". Invalid 2FA code or wait 5 minutes between login attempts."
            raise NcoreCredentialError(error_msg)

        self._logged_in = True
        return extract_cookies_from_client(self._client, self._allowed_cookies)

    @check_login
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def search(
        self,
        pattern: str,
        type: SearchParamType = SearchParamType.ALL_OWN,
        where: SearchParamWhere = SearchParamWhere.NAME,
        sort_by: ParamSort = ParamSort.UPLOAD,
        sort_order: ParamSeq = ParamSeq.DECREASING,
        page: int = 1,
    ) -> SearchResult:
        url = URLs.DOWNLOAD_PATTERN.value.format(
            page=page,
            t_type=type.value,
            sort=sort_by.value,
            seq=sort_order.value,
            pattern=pattern,
            where=where.value,
        )
        try:
            request = self._client.get(url)
        except Exception as e:
            raise NcoreConnectionError(f"Error while searching torrents. {e}") from e
        torrents = [Torrent(**params) for params in self._page_parser.get_items(request.text)]
        num_of_pages = self._page_parser.get_num_of_pages(request.text)
        return SearchResult(torrents=torrents, num_of_pages=num_of_pages)

    @check_login
    def get_torrent(self, id: str, **ext_params: Any) -> Torrent:
        url = URLs.DETAIL_PATTERN.value.format(id=id)
        try:
            content = self._client.get(url)
        except Exception as e:
            raise NcoreConnectionError(f"Error while get detailed page. Url: '{url}'. {e}") from e
        params = self._detailed_parser.get_item(content.text)
        params["id"] = id
        params.update(ext_params)
        return Torrent(**params)

    @check_login
    def get_by_rss(self, url: str) -> Generator[Torrent, None, None]:
        try:
            content = self._client.get(url)
        except Exception as e:
            raise NcoreConnectionError(f"Error while get rss. Url: '{url}'. {e}") from e

        for id in self._rss_parser.get_ids(content.text):
            yield self.get_torrent(id)

    @check_login
    def get_by_activity(self) -> list[Torrent]:
        try:
            content = self._client.get(URLs.ACTIVITY.value)
        except Exception as e:
            raise NcoreConnectionError(f"Error while get activity. Url: '{URLs.ACTIVITY.value}'. {e}") from e

        torrents = []
        for id, start_t, updated_t, status, uploaded, downloaded, remaining_t, rate in self._activity_parser.get_params(
            content.text
        ):
            torrents.append(
                self.get_torrent(
                    id,
                    start=start_t,
                    updated=updated_t,
                    status=status,
                    uploaded=Size(uploaded),
                    downloaded=Size(downloaded),
                    remaining=remaining_t,
                    rate=float(rate),
                )
            )
        return torrents

    @check_login
    def get_recommended(self, type: Union[SearchParamType, None] = None) -> Generator[Torrent, None, None]:
        try:
            content = self._client.get(URLs.RECOMMENDED.value)
        except Exception as e:
            raise NcoreConnectionError(f"Error while get recommended. Url: '{URLs.RECOMMENDED.value}'. {e}") from e

        for id in self._recommended_parser.get_ids(content.text):
            torrent = self.get_torrent(id)
            if not type or torrent["type"] == type:
                yield torrent

    @check_login
    def download(self, torrent: Torrent, path: str, override: bool = False) -> str:
        file_path, url = torrent.prepare_download(path)
        try:
            content = self._client.get(url)
        except Exception as e:
            raise NcoreConnectionError(f"Error while downloading torrent. Url: '{url}'. {e}") from e
        if not override and os.path.exists(file_path):
            raise NcoreDownloadError(f"Error while downloading file: '{file_path}'. It is already exists.")
        with open(file_path, "wb") as fh:
            fh.write(content.content)
        return file_path

    def logout(self) -> None:
        self._client.cookies.clear()
        self._client.close()
        self._logged_in = False
