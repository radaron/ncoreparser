import datetime

class Size:
    unit_size = {
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3,
        "TB": 1024**4
    }

    def __init__(self, size, unit=None):
        self._unit = unit
        self._size = 0 # in bytes
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
        return f"{self.size:.2f} {self.unit}"
    
    def __repr__(self):
        return f"{self.size:.2f} {self.unit}"
    
    def __add__(self, obj):
        if not isinstance(obj, Size):
            raise Exception(f"Error while adding different object type to {self.__class__.__name__}")
        size = self._size + obj._size
        unit = self._unit
        for u, multiplier in self.unit_size.items():
            if len(str(int(size/multiplier))) <= 3:
                unit = u
                break
        return Size(size, unit)
    
    def __iadd__(self, obj):
        if not isinstance(obj, Size):
            raise Exception(f"Error while adding different object type to {self.__class__.__name__}")
        self._size = self._size + obj._size
        for unit, multiplier in self.unit_size.items():
            if len(str(int(self._size/multiplier))) <= 3:
                self._unit = unit
                break
        return self
    
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
    return datetime.datetime.strptime("_".join([date, time]), "%Y-%m-%d_%H:%M:%S")
