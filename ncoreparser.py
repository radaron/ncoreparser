import requests
import re
from enum import Enum

class Pattern:
    torrent_id_list = '<div class="torrent_txt">(.*?)<a href="(.*?)id=(.[0-9]+)(.*?)"(.*?)>(.*?)</div>'
    details_download_link = '(.*)<div class="torrent_reszletek_cim">(?P<name>.*?)</div>(.*)<div class="download">(.*?)href="(?P<link>.*?)"(.*?)</div>'
    hnr_id = '<div class="hnr_tname">(.*?)onclick="torrent\((.*?)\);(.*?)</div>'


class ParamSort(Enum):
    NAME = "name"
    UPLOAD = "fid"
    SIZE = "size"
    TIMES_COMPLETED = "times_completed"
    SEEDERS = "seeders"
    LEECHERS = "leechers"


class ParamType(Enum):
    XVID_HUN = 'xvid_hun'
    XVID = 'xvid'
    DVD_HUN = 'dvd_hun'
    DVD = 'dvd'
    DVD9_HUN = 'dvd9_hun'
    DVD9 = 'dvd9'
    HD_HUN = 'hd_hun'
    HD = 'hd'
    XVIDSER_HUN = 'xvidser_hun'
    XVIDSER = 'xvidser'
    DVDSER_HUN = 'dvdser_hun'
    DVDSER = 'dvdser'
    HDSER_HUN = 'hdser_hun'
    HDSER = 'hdser'
    MP3_HUN = 'mp3_hun'
    MP3 = 'mp3'
    LOSSLESS_HUN = 'lossless_hun'
    LOSSLESS = 'lossless'
    CLIP = 'clip'
    GAME_ISO = 'game_iso'
    GAME_RIP = 'game_rip'
    CONSOLE = 'console'
    EBOOK_HUN = 'ebook_hun'
    EBOOK = 'ebook'
    ISO = 'iso'
    MISC = 'misc'
    MOBIL = 'mobil'


class ParamSeq(Enum):
    INCREASING = "ASC"
    DECREASING = "DESC"


class Client:
    def __init__(self):
        self.session = None
        self.url = "https://ncore.cc/"
        self.login_url = self.url + "login.php"
        self.index_url = self.url + "index.php"
        self.hnr_url = self.url + "hitnrun.php"
        self.torrents_url_pattern = self.url+"torrents.php?oldal={page}&tipus={t_type}&miszerint={sort}&hogyan={seq}"
        self.torrent_detail_pattern = self.url+"torrents.php?action=details&id={id}"
    
    def open(self, username, password):
        self.session = requests.session()
        self.session.cookies.clear()
        r = self.session.post(self.login_url, {"nev": username, "pass": password})
        if r.url != self.index_url:
            self.session.close()
            return False
        else:
            return True

    def close(self):
        self.session.close()

    def get_details_list(self, page, t_type, sort_by, seq):
        if type(page) is not int:
            return
        if t_type not in ParamType:
            return
        if sort_by not in ParamSort:
            return
        if seq not in ParamSeq:
            return
        url = self.torrents_url_pattern.format(page=page, t_type=t_type.value, sort=sort_by.value, seq=seq.value)
        text = ""
        try:
            text = self.session.get(url).text
        except Exception:
            return
        else:
            tmp_list = re.findall(Pattern.torrent_id_list, text, re.DOTALL | re.MULTILINE)
            if tmp_list is None:
                return
            link_list = list(map(lambda l: l[2], tmp_list))
            return link_list

    def get_download_dict(self, id_list):
        down_links = {}
        for id in id_list:
            raw_html = self.session.get(self.torrent_detail_pattern.format(id=id)).text
            find = re.search(Pattern.details_download_link, raw_html, re.MULTILINE | re.DOTALL)
            if find:
                down_name = find.group("name")
                down_link = self.url + find.group("link")
                down_links[down_name] = down_link
            else:
                return
        return down_links

    def most_seed_movies(self, page=1):
        links = self.get_details_list(page, ParamType.XVID_HUN, ParamSort.SEEDERS, ParamSeq.DECREASING)
        return self.get_download_dict(links)
    
    def get_hnr_torrent_ids(self):
        text = ""
        try:
            text = self.session.get(self.hnr_url).text
        except Exception:
            return False
        tmp_list = re.findall(Pattern.hnr_id, text, re.DOTALL | re.MULTILINE)
        if tmp_list is None:
            return
        else:
            return list(map(lambda l: l[1], tmp_list))
