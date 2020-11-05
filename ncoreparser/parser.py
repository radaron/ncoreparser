import re
import datetime
from bs4 import BeautifulSoup as Soup
from ncoreparser.error import NcoreParserError
from ncoreparser.util import parse_datetime, Size
from ncoreparser.data import SearchParamType, get_detailed_param


class TorrentsPageParser:
    def __init__(self):
        self.types_re = re.compile(r'tipus=(.*?)"')
        self.ids_re = re.compile(r'torrent\((.*?)\)')
        self.name_re = re.compile(r'title="(.*?)"')

    @staticmethod
    def _get_key(data):
        key_re = re.compile(r'key=(.*?)"')
        try:
            key = key_re.search(str(data.find('link', rel="alternate"))).group(1)
        except Exception as e:
            raise NcoreParserError("Error while read user key. {}".format(e))
        return key

    def get_items(self, data):
        bs = Soup(data, "html.parser")
        # get types
        lines = bs.findAll(class_="box_alap_img")
        types = [SearchParamType(self.types_re.search(str(i)).group(1)) for i in lines if self.types_re.search(str(i))]

        # get ids and names
        lines = bs.findAll('a', attrs={'onclick': re.compile("torrent")})
        names = [self.name_re.search(str(i)).group(1) for i in lines if self.name_re.search(str(i))]
        ids = [self.ids_re.search(str(i)).group(1) for i in lines if self.ids_re.search(str(i))]

        # get dates
        dates = [parse_datetime(date.text) for date in bs.findAll('div', class_="box_feltoltve2")]
        # get sizes
        sizes = [Size(size.string) for size in bs.findAll('div', class_="box_meret2")]

        if len(types) != 0 and len(types) == len(ids) == len(names) == len(sizes) == len(dates):
            key = self._get_key(bs)
        else:
            if data.find(string="Nincs találat!"):
                raise NcoreParserError("Error while parse download items in {}.".format(self.__class__.__name__))
        for i in range(0, len(types)):
            yield {"id": ids[i], "title": names[i], "key": key, "date": dates[i], "size": sizes[i], "type": types[i]}


class TorrenDetailParser:
    def __init__(self):
        group_re = re.compile(r'csoport_listazas=(.*?)"')
        type_re = re.compile(r'tipus=(.*?)"')
        date_re = re.compile(r'([0-9]{4}\-[0-9]{2}\-[0-9]{2} [0-9]{2}\:[0-9]{2}\:[0-9]{2})')
        size_re = re.compile(r'([0-9,.]+\ [K,M,G]{1}B\ )')

    def get_item(self, data):
        try:
            # get type
            group = self.group_re.search(str(data)).group(1)
            type = self.type_re.search(str(data)).group(1)
            type = get_detailed_param(group, type)

            bs = Soup(data, "html.parser")

            # get date
            date = datetime.datetime.strptime(self.date_re.search(str(data)).group(1), "%Y-%m-%d %H:%M:%S")

            # get title
            title = data.find('div', class_="torrent_reszletek_cim").string

            # get size
            size = Size(self.size_re.search(str(data)).group(1))

            # get key
            key = TorrentsPageParser._get_key(data)
        except Exception as e:
            raise NcoreParserError("Error while parsing by detailed page. {}".format(e))
        return {"title": title, "key": key, "date": date, "size": size, "type": type}


class RssParser:
    def __init__(self):
        self.id_pattern = re.compile(r'<source url=".*?\/rss_dl.php\/id=(?P<id>[0-9]+)\/key\=.[a-z,0-9]+">')

    def get_ids(self, data):
        return self.id_pattern.findall(data)


class ActivityParser:
    def __init__(self):
        self.action_pattern = re.compile(r'action=details\&id=(.*?)"')

    def get_ids(self, data):
        return self.action_pattern.findall(data)


class RecommendedParser:
    def __init__(self):
        self.id_re = re.compile('id=(.*?)"')

    def get_ids(self, data):
        bs = Soup(data)
        # Find all tags with exactly two attributes
        ids = bs.findAll('a', href=re.compile("action=details"), attrs={'target': '_blank'})
        ids = [id for id in ids if len(id.attrs)==2]

        # get id from found html tags
        ids = [self.id_re.search(str(id)).group(1) for id in ids if self.id_re.search(str(id))]

        return ids
