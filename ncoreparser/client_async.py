# pylint: disable=duplicate-code

import os
import httpx
from typing_extensions import Any, AsyncGenerator, Union  # pylint: disable=no-name-in-module
from ncoreparser.data import URLs, SearchParamType, SearchParamWhere, ParamSort, ParamSeq
from ncoreparser.error import NcoreConnectionError, NcoreCredentialError, NcoreDownloadError
from ncoreparser.parser import TorrentsPageParser, TorrenDetailParser, RssParser, ActivityParser, RecommendedParser
from ncoreparser.util import Size, check_login
from ncoreparser.torrent import Torrent
from ncoreparser.types import SearchResult


class AsyncClient:
    def __init__(self, timeout: int = 1) -> None:
        self._client = httpx.AsyncClient(
            headers={"User-Agent": "python ncoreparser"}, timeout=timeout, follow_redirects=True
        )
        self._logged_in = False
        self._page_parser = TorrentsPageParser()
        self._detailed_parser = TorrenDetailParser()
        self._rss_parser = RssParser()
        self._activity_parser = ActivityParser()
        self._recommended_parser = RecommendedParser()

    async def login(self, username: str, password: str) -> None:
        self._client.cookies.clear()
        try:
            r = await self._client.post(URLs.LOGIN.value, data={"nev": username, "pass": password})
        except Exception as e:
            raise NcoreConnectionError(f"Error while perform post " f"method to url '{URLs.LOGIN.value}'.") from e
        if r.url != URLs.INDEX.value:
            await self.logout()
            raise NcoreCredentialError(f"Error while login, check " f"credentials for user: '{username}'")
        self._logged_in = True

    @check_login
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    async def search(
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
            request = await self._client.get(url)
        except Exception as e:
            raise NcoreConnectionError(f"Error while searhing torrents. {e}") from e
        torrents = [Torrent(**params) for params in self._page_parser.get_items(request.text)]
        num_of_pages = self._page_parser.get_num_of_pages(request.text)
        return SearchResult(torrents=torrents, num_of_pages=num_of_pages)

    @check_login
    async def get_torrent(self, id: str, **ext_params: Any) -> Torrent:
        url = URLs.DETAIL_PATTERN.value.format(id=id)
        try:
            content = await self._client.get(url)
        except Exception as e:
            raise NcoreConnectionError(f"Error while get detailed page. Url: '{url}'. {e}") from e
        params = self._detailed_parser.get_item(content.text)
        params["id"] = id
        params.update(ext_params)
        return Torrent(**params)

    @check_login
    async def get_by_rss(self, url: str) -> AsyncGenerator[Torrent, None]:
        try:
            content = await self._client.get(url)
        except Exception as e:
            raise NcoreConnectionError(f"Error while get rss. Url: '{url}'. {e}") from e

        for id in self._rss_parser.get_ids(content.text):
            yield await self.get_torrent(id)

    @check_login
    async def get_by_activity(self) -> list[Torrent]:
        try:
            content = await self._client.get(URLs.ACTIVITY.value)
        except Exception as e:
            raise NcoreConnectionError(f"Error while get activity. Url: '{URLs.ACTIVITY.value}'. {e}") from e

        torrents = []
        for id, start_t, updated_t, status, uploaded, downloaded, remaining_t, rate in self._activity_parser.get_params(
            content.text
        ):
            torrents.append(
                await self.get_torrent(
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
    async def get_recommended(self, type: Union[SearchParamType, None] = None) -> AsyncGenerator[Torrent, None]:
        try:
            content = await self._client.get(URLs.RECOMMENDED.value)
        except Exception as e:
            raise NcoreConnectionError(f"Error while get recommended. Url: '{URLs.RECOMMENDED.value}'. {e}") from e

        for id in self._recommended_parser.get_ids(content.text):
            torrent = await self.get_torrent(id)
            if not type or torrent["type"] == type:
                yield torrent

    @check_login
    async def download(self, torrent: Torrent, path: str, override: bool = False) -> str:
        file_path, url = torrent.prepare_download(path)
        try:
            content = await self._client.get(url)
        except Exception as e:
            raise NcoreConnectionError(f"Error while downloading torrent. Url: '{url}'. {e}") from e
        if not override and os.path.exists(file_path):
            raise NcoreDownloadError(f"Error while downloading file: '{file_path}'. It is already exists.")
        with open(file_path, "wb") as fh:
            fh.write(content.content)
        return file_path

    async def logout(self) -> None:
        self._client.cookies.clear()
        await self._client.aclose()
        self._logged_in = False
