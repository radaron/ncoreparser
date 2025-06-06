import math
import re
import datetime
from typing_extensions import Generator, Any, Union  # pylint: disable=no-name-in-module
from ncoreparser.error import NcoreParserError
from ncoreparser.util import parse_datetime, Size
from ncoreparser.data import SearchParamType, get_detailed_param


class TorrentsPageParser:
    # pylint: disable=too-many-instance-attributes
    def __init__(self) -> None:
        self.type_pattern = re.compile(
            r'<a href=".*\/torrents\.php\?tipus=(.*?)"><img src=".*" class="categ_link" alt=".*" title=".*">'
        )
        self.id_and_name_pattern = re.compile(
            r'<a href=".*?" onclick="torrent\(([0-9]+)\); return false;" title="(.*?)">'
        )
        self.date_and_time_pattern = re.compile(r'<div class="box_feltoltve2">(.*?)<br>(.*?)</div>')
        self.size_pattern = re.compile(r'<div class="box_meret2">(.*?)</div>')
        self.not_found_pattern = re.compile(r'<div class="lista_mini_error">Nincs találat!</div>')
        self.seeders_pattern = re.compile(r'<div class="box_s2"><a class="torrent" href=".*">([0-9]+)</a></div>')
        self.leechers_pattern = re.compile(r'<div class="box_l2"><a class="torrent" href=".*">([0-9]+)</a></div>')
        self.current_page_pattern = re.compile(r'<span class="active_link"><strong>(\d+).*?</strong></span>')
        self.last_page_pattern = re.compile(r'<a href="/torrents\.php\?oldal=(\d+)[^>]*><strong>Utolsó</strong></a>')

    @staticmethod
    def get_key(data: str) -> Union[str, None]:
        key_pattern = r'<link rel="alternate" href=".*?\/rss.php\?key=(?P<key>[a-z,0-9]+)" title=".*"'
        find = re.search(key_pattern, data)
        if find:
            return find.group("key")
        raise NcoreParserError(f"Error while read user " f"key with pattern: {key_pattern}")

    def get_items(self, data: str) -> Generator[dict, None, None]:
        types = self.type_pattern.findall(data)
        ids_and_names = self.id_and_name_pattern.findall(data)
        dates_and_times = self.date_and_time_pattern.findall(data)
        sizes = self.size_pattern.findall(data)
        seed = self.seeders_pattern.findall(data)
        leech = self.leechers_pattern.findall(data)
        ids: tuple[Any, ...] = ()
        if len(types) != 0 and len(types) == len(ids_and_names) == len(dates_and_times) == len(sizes) == len(
            seed
        ) == len(leech):
            ids, names = zip(*ids_and_names)
            dates, times = zip(*dates_and_times)
            key = self.get_key(data)
        else:
            if not self.not_found_pattern.search(data):
                raise NcoreParserError(f"Error while parse download items in {self.__class__.__name__}.")
        for i, id in enumerate(ids):
            yield {
                "id": id,
                "title": names[i],
                "key": key,
                "date": parse_datetime(dates[i], times[i]),
                "size": Size(sizes[i]),
                "type": SearchParamType(types[i]),
                "seed": seed[i],
                "leech": leech[i],
            }

    def get_num_of_pages(self, data: str) -> int:
        current_num_of_items_found = self.current_page_pattern.search(data)
        last_page_found = self.last_page_pattern.search(data)

        num_of_pages = 0
        if current_num_of_items_found:
            current_num_of_items = int(current_num_of_items_found.group(1))
            num_of_pages = math.ceil(current_num_of_items / 25)
        if last_page_found:
            last_page = int(last_page_found.group(1))
            num_of_pages = max(num_of_pages, last_page)
        return num_of_pages


class TorrenDetailParser:
    def __init__(self) -> None:
        self.type_pattern = re.compile(
            r'<div class="dd"><a title=".*?" href=".*?torrents.php\?csoport_listazas='
            r'(?P<category>.*?)">.*?</a>.*?<a title=".*?" href=".*?torrents.php\?tipus='
            r'(?P<type>.*?)">.*?</a></div>'
        )
        self.date_pattern = re.compile(
            r'<div class="dd">(?P<date>[0-9]{4}\-[0-9]{2}\-[0-9]{2}\ [0-9]{2}\:[0-9]{2}\:[0-9]{2})</div>'
        )
        self.title_pattern = re.compile(r'<div class="torrent_reszletek_cim">(?P<title>.*?)</div>')
        self.size_pattern = re.compile(r'<div class="dd">(?P<size>[0-9,.]+\ [K,M,G,T]{1}iB)\ \(.*?\)</div>')
        self.peers_pattern = re.compile(
            r'div class="dt">Seederek:</div>.*?<div class="dd"><a onclick=".*?">'
            r'(?P<seed>[0-9]+)</a></div>.*?<div class="dt">Leecherek:</div>.*?<div '
            r'class="dd"><a onclick=".*?">(?P<leech>[0-9]+)</a></div>',
            re.DOTALL,
        )

    def get_item(self, data: str) -> dict:
        try:
            t_type_match = self.type_pattern.search(data)
            if t_type_match:
                t_type = get_detailed_param(t_type_match.group("category"), t_type_match.group("type"))
            else:
                raise NcoreParserError("Type pattern not found in data")
            date_match = self.date_pattern.search(data)
            if date_match:
                date = datetime.datetime.strptime(date_match.group("date"), "%Y-%m-%d %H:%M:%S")
            else:
                raise NcoreParserError("Date pattern not found in data")
            title_match = self.title_pattern.search(data)
            if title_match:
                title = title_match.group("title")
            else:
                raise NcoreParserError("Title pattern not found in data")
            key = TorrentsPageParser.get_key(data)
            size_match = self.size_pattern.search(data)
            if size_match:
                size = Size(size_match.group("size"))
            else:
                raise NcoreParserError("Size pattern not found in data")
            peers_match = self.peers_pattern.search(data)
            if peers_match:
                seed = peers_match.group("seed")
                leech = peers_match.group("leech")
            else:
                raise NcoreParserError("Peers pattern not found in data")
        except AttributeError as e:
            raise NcoreParserError(f"Error while parsing by detailed page. {e}") from e
        return {"title": title, "key": key, "date": date, "size": size, "type": t_type, "seed": seed, "leech": leech}


class RssParser:
    def __init__(self) -> None:
        self.id_pattern = re.compile(r'<source url=".*?\/rss_dl.php\/id=(?P<id>[0-9]+)\/key\=.[a-z,0-9]+">')

    def get_ids(self, data: str) -> list[str]:
        return self.id_pattern.findall(data)


class ActivityParser:
    def __init__(self) -> None:
        self.patterns = [
            re.compile(r'onclick="torrent\((.*?)\);'),
            re.compile(r'<div class="hnr_tstart">(.*?)<\/div>'),
            re.compile(r'<div class="hnr_tlastactive">(.*?)<\/div>'),
            re.compile(r'<div class="hnr_tseed"><span class=".*?">(.*?)<\/span><\/div>'),
            re.compile(r'<div class="hnr_tup">(.*?)<\/div>'),
            re.compile(r'<div class="hnr_tdown">(.*?)<\/div>'),
            re.compile(r'<div class="hnr_ttimespent"><span class=".*?">(.*?)<\/span><\/div>'),
            re.compile(r'<div class="hnr_tratio"><span class=".*?">(.*?)<\/span><\/div>'),
        ]

    def get_params(self, data: str) -> tuple[tuple[Any, ...], ...]:
        out = []
        for parser in self.patterns:
            out.append(parser.findall(data))
        return tuple(zip(*out))


class RecommendedParser:
    def __init__(self) -> None:
        self.recommended_pattern = re.compile(
            r'<a href=".*?torrents.php\?action=details\&id=(.*?)" target=".*?"><img'
            r' src=".*?" width=".*?" height=".*?" border=".*?" title=".*?"\/><\/a>'
        )

    def get_ids(self, data: str) -> list[str]:
        return self.recommended_pattern.findall(data)
