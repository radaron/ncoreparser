import datetime
import functools
import sys
from typing import Any, Callable, Dict, Union

from ncoreparser.data import URLs
from ncoreparser.error import NcoreConnectionError

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


class Size:
    unit_size = {"B": 1, "KiB": 1024, "MiB": 1024**2, "GiB": 1024**3, "TiB": 1024**4}

    def __init__(self, size: Union[str, int, float], unit: Union[str, None] = None) -> None:
        self._unit: Union[str, None] = unit
        self._size: Union[int, float] = 0  # in bytes
        if isinstance(size, str):
            self._parse_str(size)
        elif isinstance(size, (int, float)):
            self._size = size

    def _parse_str(self, size: str) -> None:
        size, unit = size.split(" ")
        self._size = float(size) * self.unit_size[unit]
        self._unit = unit

    def __str__(self) -> str:
        return f"{self.size:.2f} {self.unit}"

    def __repr__(self) -> str:
        return f"{self.size:.2f} {self.unit}"

    def _check_obj(self, obj: object) -> None:
        if not isinstance(obj, Size):
            raise ValueError(f"Error while perform operaton with Size and {type(obj)}")

    def __add__(self, obj: Self) -> object:
        self._check_obj(obj)
        size = self._size + obj._size
        unit = self._unit
        for u, multiplier in self.unit_size.items():
            if 0 < int(self._size / multiplier) <= 1000:
                unit = u
                break
        return Size(size, unit)

    def __iadd__(self, obj: Self) -> object:
        self._check_obj(obj)
        self._size = self._size + obj._size
        for unit, multiplier in self.unit_size.items():
            if 0 < int(self._size / multiplier) <= 1000:
                self._unit = unit
                break
        return self

    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, Size):
            return NotImplemented
        return self._size == obj._size

    def __ne__(self, obj: object) -> bool:
        if not isinstance(obj, Size):
            return NotImplemented
        return self._size != obj._size

    def __gt__(self, obj: Self) -> bool:
        self._check_obj(obj)
        return self._size > obj._size

    def __ge__(self, obj: Self) -> bool:
        self._check_obj(obj)
        return self._size >= obj._size

    @property
    def unit(self) -> Union[str, None]:
        return self._unit

    @property
    def size(self) -> float:
        return self._size / float(self.unit_size[str(self._unit)])

    @property
    def bytes(self) -> int:
        return int(self._size)


def parse_datetime(date: str, time: str) -> datetime.datetime:
    return datetime.datetime.strptime(f"{date}_{time}", "%Y-%m-%d_%H:%M:%S")


def extract_cookies_from_client(client: Any, allowed_cookies: list[str]) -> Dict[str, str]:
    cookies_dict = {}
    for cookie in client.cookies.jar:
        if cookie.name in allowed_cookies:
            cookies_dict[cookie.name] = cookie.value
    return cookies_dict


def set_cookies_to_client(
    client: Any, cookies: Dict[str, str], allowed_cookies: list[str], domain: str = URLs.COOKIE_DOMAIN.value
) -> None:
    for name, value in cookies.items():
        if name in allowed_cookies:
            client.cookies.set(name, value, domain=domain)


def check_login(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Callable:
        if not self._logged_in:
            raise NcoreConnectionError(f"Cannot login to tracker. Please use {self.login.__name__} function first.")
        return func(self, *args, **kwargs)

    return wrapper
