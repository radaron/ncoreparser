from enum import Enum


class ParamSort(Enum):
    NAME = "name"
    UPLOAD = "fid"
    SIZE = "size"
    TIMES_COMPLETED = "times_completed"
    SEEDERS = "seeders"
    LEECHERS = "leechers"


class SearchParamType(Enum):
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
    XXX_IMG = 'xxx_imageset'
    ALL_OWN = "all_own"


class ParamSearchWhere(Enum):
    NAME = "name"
    DESCRIPTION = "leiras"
    IMDB = "imdb"
    LABEL = "cimke"


class ParamSeq(Enum):
    INCREASING = "ASC"
    DECREASING = "DESC"


class URLs(Enum):
    INDEX = "https://ncore.cc/index.php"
    LOGIN = "https://ncore.cc/login.php"
    ACTIVITY = "https://ncore.cc/hitnrun.php"
    TORRENTS_BASE = "https://ncore.cc/torrents.php"
    DOWNLOAD_PATTERN = TORRENTS_BASE+"?oldal={page}" \
                                     "&tipus={t_type}" \
                                     "&miszerint={sort}" \
                                     "&hogyan={seq}" \
                                     "&mire={pattern}" \
                                     "&miben={where}"
    DETAIL_PATTERN = TORRENTS_BASE+"?action=details&id={id}"
    DOWNLOAD_LINK = "https://ncore.cc/torrents.php?action=download&id={id}&key={key}"
