import datetime


class Size:
    unit_size = {
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
        elif isinstance(size, int) or isinstance(size, float):
            self._size = size

    def _parse_str(self, size):
        size, unit = size.split(" ")
        for i in self.unit_size:
            if unit == i:
                self._size = float(size)*self.unit_size[i]
                self._unit = i
                break

    def __str__(self):
        return "{:.2f} {}".format(self.size, self.unit)

    def __repr__(self):
        return "{:.2f} {}".format(self.size, self.unit)

    def _check_obj(self, obj):
        if not isinstance(obj, Size):
            raise Exception("Error while perform operaton with Size and {}".format(type(obj)))

    def __add__(self, obj):
        self._check_obj(obj)
        size = self._size + obj._size
        unit = self._unit
        for u, multiplier in self.unit_size.items():
            if 0 < int(self._size/multiplier) <= 1000:
                unit = u
                break
        return Size(size, unit)

    def __iadd__(self, obj):
        self._check_obj(obj)
        self._size = self._size + obj._size
        for unit, multiplier in self.unit_size.items():
            if 0 < int(self._size/multiplier) <= 1000:
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
    return datetime.datetime.strptime("{}_{}".format(date, time), "%Y-%m-%d_%H:%M:%S")
