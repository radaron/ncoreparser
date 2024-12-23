import os
from typing_extensions import Any
from ncoreparser.data import URLs
from ncoreparser.util import Size


class Torrent:
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(
        self, id: str, title: str, key: str, size: Size, type: str, date: str, seed: str, leech: str, **params: Any
    ) -> None:
        self._details = {
            "id": id,
            "title": title,
            "key": key,
            "size": size,
            "type": type,
            "date": date,
            "seed": seed,
            "leech": leech,
            "download": URLs.DOWNLOAD_LINK.value.format(id=id, key=key),
            "url": URLs.DETAIL_PATTERN.value.format(id=id),
        }
        self._details.update(params)

    def __getitem__(self, key: str) -> Any:
        return self._details[key]

    def keys(self) -> list[str]:
        return list(self._details.keys())

    def __str__(self) -> str:
        return f"<Torrent {self._details['id']}>"

    def __repr__(self) -> str:
        return f"<Torrent {self._details['id']}>"

    def prepare_download(self, path: str) -> tuple[str, str]:
        filename = str(self._details["title"]).replace(" ", "_") + ".torrent"
        filepath = os.path.join(path, filename)
        url = str(self._details["download"])
        return filepath, url
