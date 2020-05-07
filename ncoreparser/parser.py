import re
import datetime
from ncoreparser.error import NcoreParserError
from ncoreparser.util import parse_datetime, Size
from ncoreparser.data import SearchParamType, get_detaild_param


class TorrentsPageParser:
    def __init__(self):
        self.type_pattern = re.compile(r'<a href=".*\/torrents\.php\?tipus=(.*?)">'
                                       r'<img src=".*" class="categ_link" alt=".*" title=".*">')
        self.id_name_pattern = re.compile(r'<a href=".*?" onclick="torrent\(([0-9]+)\); return false;" title="(.*?)">')
        self.date_pattern = re.compile(r'<div class="box_feltoltve2">(.*?)<br>(.*?)</div>')
        self.size_pattern = re.compile(r'<div class="box_meret2">(.*?)</div>')
        self.not_found_pattern = re.compile(r'<div class="lista_mini_error">Nincs találat!</div>')

    @staticmethod
    def _get_key(data):
        key_pattern = r'<link rel="alternate" href=".*?\/rss.php\?key=(?P<key>[a-z,0-9]+)" title=".*"'
        find = re.search(key_pattern, data)
        if find:
            return find.group("key")
        else:
            raise NcoreParserError("Error while read user "
                                   "key with pattern: {}".format(key_pattern))

    def get_items(self, data):
        types = self.type_pattern.findall(data)
        ids_names = self.id_name_pattern.findall(data)
        dates_times = self.date_pattern.findall(data)
        sizes = self.size_pattern.findall(data)
        if len(types) != 0 and len(types) == len(ids_names) == len(dates_times) == len(sizes):
            ids, names = zip(*ids_names)
            dates, times = zip(*dates_times)
            key = self._get_key(data)
        else:
            if not self.not_found_pattern.search(data):
                raise NcoreParserError("Error while parse download items in {}.".format(self.__class__.__name__))
        for i in range(0, len(types)):
            yield {"id": ids[i], "title": names[i], "key": key,
                    "date": parse_datetime(dates[i], times[i]), "size": Size(sizes[i]), "type": SearchParamType(types[i])}


class TorrenDetailParser:
    def __init__(self):
        self.type_pattern = re.compile(r'<div class="dd"><a title=".*?" href=".*?torrents.php\?csoport_listazas=(?P<category>.*?)">'
                                       r'.*?</a>.*?<a title=".*?" href=".*?torrents.php\?tipus=(?P<type>.*?)">.*?</a></div>')
        self.date_pattern = re.compile(r'<div class="dd">(?P<date>[0-9]{4}\-[0-9]{2}\-[0-9]{2}\ [0-9]{2}\:[0-9]{2}\:[0-9]{2})</div>')
        self.title_pattern = re.compile(r'<div class="torrent_reszletek_cim">(?P<title>.*?)</div>')
        self.size_pattern = re.compile(r'<div class="dd">(?P<size>[0-9,.]+\ [K,M,G]{1}B)\ \(.*?\)</div>')

    def get_item(self, data):
        try:
            t_type = self.type_pattern.search(data)
            t_type = get_detaild_param(t_type.group("category"), t_type.group("type"))
            date = datetime.datetime.strptime(self.date_pattern.search(data).group("date"), "%Y-%m-%d %H:%M:%S")
            title = self.title_pattern.search(data).group("title")
            key = TorrentsPageParser._get_key(data)
            size = Size(self.size_pattern.search(data).group("size"))
        except AttributeError as e:
            raise NcoreParserError("Error while parsing by detailed page. {}".format(e))
        return {"title": title, "key": key, "date": date, "size": size, "type": t_type}


class RssParser:
    def __init__(self):
        self.id_pattern = re.compile(r'<source url=".*?\/rss_dl.php\/id=(?P<id>[0-9]+)\/key\=.[a-z,0-9]+">')

    def get_ids(self, data):
        return self.id_pattern.findall(data)


class ActivityParser:
    def __init__(self):
        self.action_pattern = re.compile(r'<a href=".*?" onclick="torrent\((.*?)\); return false;'
                                         r'" title=".*?"><nobr>.*?<\/nobr><\/a>')

    def get_ids(self, data):
        return self.action_pattern.findall(data)


class RecommendedParser:
    def __init__(self):
        self.recommended_pattern = re.compile(r'<a href=".*?torrents.php\?action=details\&id=(.*?)" target=".*?">'
                                              r'<img src=".*?" width=".*?" height=".*?" border=".*?" title=".*?"\/><\/a>')

    def get_ids(self, data):
        return self.recommended_pattern.findall(data)
