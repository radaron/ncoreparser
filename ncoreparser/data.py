from enum import Enum
from ncoreparser.error import NcoreParserError


class ParamSort(Enum):
    NAME = "name"
    UPLOAD = "fid"
    SIZE = "size"
    TIMES_COMPLETED = "times_completed"
    SEEDERS = "seeders"
    LEECHERS = "leechers"


class SearchParamType(Enum):
    SD_HUN = 'xvid_hun'
    SD = 'xvid'
    DVD_HUN = 'dvd_hun'
    DVD = 'dvd'
    DVD9_HUN = 'dvd9_hun'
    DVD9 = 'dvd9'
    HD_HUN = 'hd_hun'
    HD = 'hd'
    SDSER_HUN = 'xvidser_hun'
    SDSER = 'xvidser'
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
    XXX_SD = 'xxx_xvid'
    XXX_DVD = 'xxx_dvd'
    XXX_HD = 'xxx_hd'
    ALL_OWN = "all_own"


def get_detailed_param(category, type):
    detailed = {
            "osszes_film_xvid_hun": SearchParamType.SD_HUN,
            "osszes_film_xvid": SearchParamType.SD,
            "osszes_film_dvd_hun": SearchParamType.DVD_HUN,
            "osszes_film_dvd": SearchParamType.DVD,
            "osszes_film_dvd9_hun": SearchParamType.DVD9_HUN,
            "osszes_film_dvd9": SearchParamType.DVD9,
            "osszes_film_hd_hun": SearchParamType.HD_HUN,
            "osszes_film_hd": SearchParamType.HD,
            "osszes_sorozat_xvidser_hun": SearchParamType.SDSER_HUN,
            "osszes_sorozat_xvidser": SearchParamType.SDSER,
            "osszes_sorozat_dvdser_hun": SearchParamType.DVDSER_HUN,
            "osszes_sorozat_dvdser": SearchParamType.DVDSER,
            "osszes_sorozat_hdser_hun": SearchParamType.HDSER_HUN,
            "osszes_sorozat_hdser": SearchParamType.HDSER,
            "osszes_zene_mp3_hun": SearchParamType.MP3_HUN,
            "osszes_zene_mp3": SearchParamType.MP3,
            "osszes_zene_lossless_hun": SearchParamType.LOSSLESS_HUN,
            "osszes_zene_lossless": SearchParamType.LOSSLESS,
            "osszes_zene_clip": SearchParamType.CLIP,
            "osszes_jatek_game_iso": SearchParamType.GAME_ISO,
            "osszes_jatek_game_rip": SearchParamType.GAME_RIP,
            "osszes_jatek_console": SearchParamType.CONSOLE,
            "osszes_konyv_ebook_hun": SearchParamType.EBOOK_HUN,
            "osszes_konyv_ebook": SearchParamType.EBOOK,
            "osszes_program_iso": SearchParamType.ISO,
            "osszes_program_misc": SearchParamType.MISC,
            "osszes_program_mobil": SearchParamType.MOBIL,
            "osszes_xxx_xxx_imageset": SearchParamType.XXX_IMG,
            "osszes_xxx_xxx_xvid": SearchParamType.XXX_SD,
            "osszes_xxx_xxx_dvd": SearchParamType.XXX_DVD,
            "osszes_xxx_xxx_hd": SearchParamType.XXX_HD,
    }.get("{}_{}".format(category, type), None)

    if detailed is None:
        raise NcoreParserError("Error while get type by detailed page.")
    return detailed


class SearchParamWhere(Enum):
    NAME = "name"
    DESCRIPTION = "leiras"
    IMDB = "imdb"
    LABEL = "cimke"


class ParamSeq(Enum):
    INCREASING = "ASC"
    DECREASING = "DESC"


class URLs(Enum):
    INDEX = "https://ncore.pro/index.php"
    LOGIN = "https://ncore.pro/login.php"
    ACTIVITY = "https://ncore.pro/hitnrun.php"
    RECOMMENDED = "https://ncore.pro/recommended.php"
    TORRENTS_BASE = "https://ncore.pro/torrents.php"
    DOWNLOAD_PATTERN = TORRENTS_BASE+"?oldal={page}" \
                                     "&tipus={t_type}" \
                                     "&miszerint={sort}" \
                                     "&hogyan={seq}" \
                                     "&mire={pattern}" \
                                     "&miben={where}"
    DETAIL_PATTERN = TORRENTS_BASE+"?action=details&id={id}"
    DOWNLOAD_LINK = "https://ncore.pro/torrents.php?action=download&id={id}&key={key}"
