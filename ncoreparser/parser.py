import re
from ncoreparser.error import NcoreParserError
from ncoreparser.util import parse_datetime, Size
from ncoreparser.data import SearchParamType

class TorrentsPageParser:
    def __init__(self):
        self.key_pattern = re.compile(r'<link rel="alternate" href=".*?\/rss.php\?key=(?P<key>[a-z,0-9]+)" title=".*"')
        self.type_pattern = re.compile(r'<a href=".*\/torrents\.php\?tipus=(.*?)"><img src=".*" class="categ_link" alt=".*" title=".*">')
        self.id_name_pattern = re.compile(r'<a href=".*?" onclick="torrent\(([0-9]+)\); return false;" title="(.*?)">')
        self.date_pattern = re.compile(r'<div class="box_feltoltve2">(.*?)<br>(.*?)</div>')
        self.size_pattern = re.compile(r'<div class="box_meret2">(.*?)</div>')
    
    def _get_key(self, data):
        find = self.key_pattern.search(data)
        if find:
            return find.group("key")
        else:
            raise NcoreParserError(f"Error while read user "
                                   f"key with pattern: {self.key_pattern}")

    def get_items(self, data):
        types = self.type_pattern.findall(data)
        ids_names = self.id_name_pattern.findall(data)
        dates_times = self.date_pattern.findall(data)
        sizes = self.size_pattern.findall(data) 
        if len(types) == 0 or not len(types) == len(ids_names) == len(dates_times) == len(sizes):
            raise NcoreParserError(f"Error while read download items "
                                   f"with pattern: {self.download_pattern}")
        ids, names = zip(*ids_names)
        dates, times = zip(*dates_times)
        key = self._get_key(data)
        for i in range(0, len(types)):
            yield {"id": ids[i], "title": names[i], "key": key, "date": parse_datetime(dates[i], times[i]), "size": Size(sizes[i]), "type": SearchParamType(types[i])}

