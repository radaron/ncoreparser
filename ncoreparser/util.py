import datetime


class Size:
    unit_size = {
        "B": 1,
        "KiB": 1024,
        "MiB": 1024**2,
        "GiB": 1024**3,
        "TiB": 1024**4
    }

    def __init__(self, size, unit=None):
        self._unit = unit
        self._size = 0  # in bytes
        if isinstance(size, str):
            self._parse_str(size)
        elif isinstance(size, (int, float)):
            self._size = size

    def _parse_str(self, size):
        size, unit = size.split(" ")
        self._size = float(size) * self.unit_size[unit]
        self._unit = unit

    def __str__(self):
        return f"{self.size:.2f} {self.unit}"

    def __repr__(self):
        return f"{self.size:.2f} {self.unit}"

    def _check_obj(self, obj):
        if not isinstance(obj, Size):
            raise ValueError(f"Error while perform operaton with Size and {type(obj)}")

    def __add__(self, obj):
        self._check_obj(obj)
        size = self._size + obj._size
        unit = self._unit
        for u, multiplier in self.unit_size.items():
            if 0 < int(self._size / multiplier) <= 1000:
                unit = u
                break
        return Size(size, unit)

    def __iadd__(self, obj):
        self._check_obj(obj)
        self._size = self._size + obj._size
        for unit, multiplier in self.unit_size.items():
            if 0 < int(self._size / multiplier) <= 1000:
                self._unit = unit
                break
        return self

    def __eq__(self, obj):
        self._check_obj(obj)
        return self._size == obj._size

    def __ne__(self, obj):
        self._check_obj(obj)
        return self._size != obj._size

    def __gt__(self, obj):
        self._check_obj(obj)
        return self._size > obj._size

    def __ge__(self, obj):
        self._check_obj(obj)
        return self._size >= obj._size

    @property
    def unit(self):
        return self._unit

    @property
    def size(self):
        return self._size / self.unit_size[self._unit]

    @property
    def bytes(self):
        return self._size


def parse_datetime(date, time):
    return datetime.datetime.strptime(f"{date}_{time}", "%Y-%m-%d_%H:%M:%S")
