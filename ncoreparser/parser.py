import re
import datetime
from ncoreparser.error import NcoreParserError
from ncoreparser.util import parse_datetime, Size
from ncoreparser.data import SearchParamType, get_detailed_param


class TorrentsPageParser:
    def __init__(self):
        self.type_pattern = re.compile(r'<a href=".*\/torrents\.php\?tipus=(.*?)">'
                                       r'<img src=".*" class="categ_link" alt=".*" title=".*">')
        self.id_name_poster_pattern = re.compile(
             r'<a href=".*?" onclick="torrent\((\d+)\);.*?" title="(.*?)">.*?(?:onmouseover="mutat\(\'(https:\/\/.*?)\',.*?)',
             re.DOTALL
        )
        self.id_name_patter = re.compile(r'<a href=".*?" onclick="torrent\(([0-9]+)\); return false;" title="(.*?)">')
        self.date_pattern = re.compile(r'<div class="box_feltoltve2">(.*?)<br>(.*?)</div>')
        self.size_pattern = re.compile(r'<div class="box_meret2">(.*?)</div>')
        self.not_found_pattern = re.compile(r'<div class="lista_mini_error">Nincs találat!</div>')
        self.seeders_pattern = re.compile(r'<div class="box_s2"><a class="torrent" href=".*">([0-9]+)</a></div>')
        self.leechers_pattern = re.compile(r'<div class="box_l2"><a class="torrent" href=".*">([0-9]+)</a></div>')


    @staticmethod
    def get_key(data):
        key_pattern = r'<link rel="alternate" href=".*?\/rss.php\?key=(?P<key>[a-z,0-9]+)" title=".*"'
        find = re.search(key_pattern, data)
        if find:
            return find.group("key")
        raise NcoreParserError(f"Error while read user "
                               f"key with pattern: {key_pattern}")


    def id_exists(self, data, search_id):
        for i, id in enumerate(data):
            if search_id in data[i]:
                return True

        return False


    def get_items(self, data):
        types = self.type_pattern.findall(data)
        ids_names_posters = self.id_name_poster_pattern.findall(data)
        ids_names = self.id_name_patter.findall(data)
        dates_times = self.date_pattern.findall(data)
        sizes = self.size_pattern.findall(data)
        seed = self.seeders_pattern.findall(data)
        leech = self.leechers_pattern.findall(data)

        # Not all torrents has poster img
        if (len(ids_names) != len(ids_names_posters)):
            for i, id in enumerate(ids_names):
                if not self.id_exists(ids_names_posters, ids_names[i][0]):
                    missing_torrent_data = (ids_names[i][0], ids_names[i][1], 'no cover')
                    ids_names_posters.append(missing_torrent_data)

        if len(types) != 0 and len(types) == len(ids_names_posters) == \
            len(dates_times) == len(sizes) == len(seed) == len(leech):
            ids, names, poster_image = zip(*ids_names_posters)
            dates, times = zip(*dates_times)
            key = self.get_key(data)
        else:
            if not self.not_found_pattern.search(data):
                raise NcoreParserError(f"Error while parse download items in {self.__class__.__name__}.")
            return
        for i, id in enumerate(ids):
            yield {"id": id, "title": names[i], "key": key, "date": parse_datetime(dates[i], times[i]),
                   "size": Size(sizes[i]), "type": SearchParamType(types[i]), "seed": seed[i], "leech": leech[i], "poster_image": poster_image[i]}


class TorrenDetailParser:
    def __init__(self):
        self.type_pattern = re.compile(r'<div class="dd"><a title=".*?" href=".*?torrents.php\?csoport_listazas='
                                       r'(?P<category>.*?)">.*?</a>.*?<a title=".*?" href=".*?torrents.php\?tipus='
                                       r'(?P<type>.*?)">.*?</a></div>')
        self.date_pattern = re.compile(r'<div class="dd">(?P<date>[0-9]{4}\-[0-9]{2}\-[0-9]{2}\ '
                                       r'[0-9]{2}\:[0-9]{2}\:[0-9]{2})</div>')
        self.title_pattern = re.compile(r'<div class="torrent_reszletek_cim">(?P<title>.*?)</div>')
        self.size_pattern = re.compile(r'<div class="dd">(?P<size>[0-9,.]+\ [K,M,G,T]{1}iB)\ \(.*?\)</div>')
        self.peers_pattern = re.compile(r'div class="dt">Seederek:</div>.*?<div class="dd"><a onclick=".*?">'
                                        r'(?P<seed>[0-9]+)</a></div>.*?<div class="dt">Leecherek:</div>.*?<div '
                                        r'class="dd"><a onclick=".*?">(?P<leech>[0-9]+)</a></div>', re.DOTALL)
        self.poster_image_pattern = re.compile(r'<td class="inforbar_img" align="center"><img\s+[^>]*src="(https://[^\"]+)', re.DOTALL)

    def get_item(self, data):
        try:
            t_type = self.type_pattern.search(data)
            t_type = get_detailed_param(t_type.group("category"), t_type.group("type"))
            date = datetime.datetime.strptime(self.date_pattern.search(data).group("date"), "%Y-%m-%d %H:%M:%S")
            title = self.title_pattern.search(data).group("title")
            key = TorrentsPageParser.get_key(data)
            size = Size(self.size_pattern.search(data).group("size"))
            peers = self.peers_pattern.search(data)
            seed = peers.group('seed')
            leech = peers.group('leech')
            poster_image_match = self.poster_image_pattern.search(data)
            poster_image = poster_image_match.group(1) if poster_image_match else "No cover"

        except AttributeError as e:
            raise NcoreParserError(f"Error while parsing by detailed page. {e}") from e
        return {"title": title, "key": key, "date": date, "size": size, "type": t_type, 'seed': seed, 'leech': leech, 'poster_image': poster_image}


class RssParser:
    def __init__(self):
        self.id_pattern = re.compile(r'<source url=".*?\/rss_dl.php\/id=(?P<id>[0-9]+)\/key\=.[a-z,0-9]+">')

    def get_ids(self, data):
        return self.id_pattern.findall(data)


class ActivityParser:
    def __init__(self):
        self.patterns = [
            re.compile(r'onclick="torrent\((.*?)\);'),
            re.compile(r'<div class="hnr_tstart">(.*?)<\/div>'),
            re.compile(r'<div class="hnr_tlastactive">(.*?)<\/div>'),
            re.compile(r'<div class="hnr_tseed"><span class=".*?">(.*?)<\/span><\/div>'),
            re.compile(r'<div class="hnr_tup">(.*?)<\/div>'),
            re.compile(r'<div class="hnr_tdown">(.*?)<\/div>'),
            re.compile(r'<div class="hnr_ttimespent"><span class=".*?">(.*?)<\/span><\/div>'),
            re.compile(r'<div class="hnr_tratio"><span class=".*?">(.*?)<\/span><\/div>')
        ]

    def get_params(self, data):
        out = []
        for parser in self.patterns:
            out.append(parser.findall(data))
        return tuple(zip(*out))


class RecommendedParser:
    def __init__(self):
        self.recommended_pattern = re.compile(r'<a href=".*?torrents.php\?action=details\&id=(.*?)" target=".*?"><img'
                                              r' src=".*?" width=".*?" height=".*?" border=".*?" title=".*?"\/><\/a>')

    def get_ids(self, data):
        return self.recommended_pattern.findall(data)
