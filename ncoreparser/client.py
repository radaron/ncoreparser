import requests
import os
from ncoreparser.data import (
    URLs,
    SearchParamType,
    SearchParamWhere,
    ParamSort,
    ParamSeq
)
from ncoreparser.error import (
    NcoreConnectionError,
    NcoreCredentialError,
    NcoreDownloadError
)
from ncoreparser.parser import (
    TorrentsPageParser,
    TorrenDetailParser,
    RssParser,
    ActivityParser,
    RecommendedParser
)
from ncoreparser.torrent import Torrent
from ncoreparser.constant import TORRENTS_PER_PAGE


class Client:
    def __init__(self, timeout=1):
        self._session = requests.session()
        self._session.cookies.clear()
        self._session.headers.update({'User-Agent': 'python ncoreparser'})
        self.timeout = timeout
        self._page_parser = TorrentsPageParser()
        self._detailed_parser = TorrenDetailParser()
        self._rss_parser = RssParser()
        self._activity_parser = ActivityParser()
        self._recommended_parser = RecommendedParser()

    def open(self, username, password):
        try:
            r = self._session.post(URLs.LOGIN.value,
                                   {"nev": username, "pass": password},
                                   timeout=self.timeout)
        except Exception:
            raise NcoreConnectionError("Error while perform post "
                                       "method to url '{}'.".format(URLs.LOGIN.value))
        if r.url != URLs.INDEX.value:
            self._session.close()
            raise NcoreCredentialError("Error while login, check "
                                       "credentials for user: '{}'".format(username))

    def search(self, pattern, type=SearchParamType.ALL_OWN,  where=SearchParamWhere.NAME,
               sort_by=ParamSort.UPLOAD, sort_order=ParamSeq.DECREASING, number=TORRENTS_PER_PAGE):
        page_count = 0
        torrents = []
        while page_count * TORRENTS_PER_PAGE < number:
            url = URLs.DOWNLOAD_PATTERN.value.format(page=page_count+1,
                                                     t_type=type.value,
                                                     sort=sort_by.value,
                                                     seq=sort_order.value,
                                                     pattern=pattern,
                                                     where=where.value)
            try:
                request = self._session.get(url, timeout=self.timeout)
            except Exception as e:
                raise NcoreConnectionError("Error while searhing torrents. {}".format(e))
            new_torrents = [Torrent(**params) for params in self._page_parser.get_items(request.text)]
            if len(new_torrents) == 0:
                return torrents
            torrents.extend(new_torrents)
            page_count += 1
        return torrents[:number]

    def get_torrent(self, id):
        url = URLs.DETAIL_PATTERN.value.format(id=id)
        try:
            content = self._session.get(url, timeout=self.timeout)
        except Exception as e:
            raise NcoreConnectionError("Error while get detailed page. Url: '{}'. {}".format(url, e))
        params = self._detailed_parser.get_item(content.text)
        params["id"] = id
        return Torrent(**params)

    def get_by_rss(self, url):
        try:
            content = self._session.get(url, timeout=self.timeout)
        except Exception as e:
            raise NcoreConnectionError("Error while get rss. Url: '{}'. {}".format(url, e))

        torrents = []
        for id in self._rss_parser.get_ids(content.text):
            torrents.append(self.get_torrent(id))
        return torrents
    
    def get_by_activity2(self):

        content = None
        try:
            content = self._session.get(URLs.ACTIVITY.value, timeout=self.timeout)
        except Exception as e:
            raise NcoreConnectionError("Error while get activity. Url: '{}'. {}".format(URLs.ACTIVITY.value, e))
        torrents = []
        splitedt = []
        for x in content.text.split("""<div class="hnr_torrents">"""):
                if "hnr_tname" in x:
                        splitedt.append("""<div class="hnr_torrents">"""+x)
        splitedt[-1] = splitedt[-1].split("""<div class="lista_lab"></div>""")[0]
        for x in splitedt:
             line = x.split("\n")
             
             for x in range(len(line)):
                 line[x] = line[x].replace("	","")
                 if x in [5,6,8,9]:
                     line[x] = line[x].split(">")[1].split("<")[0]
             line[3] = line[3].split(">")[0]
             line31 = line[3].split(";")[0].split(" onclick=")[0].replace("""torrents.php?action=details&id=""","""""").replace("href=","")[4:].replace('"','')
             line32 = line[3].split(";")[2][2:].replace("title=",'').replace('"','')
             line[3] = line31 + "\n"+ line32
             line[7] = line[7].split("""<div class="hnr_tseed"><span class="stopped">""")[1].split("<")[0]
             line[10] = line[10].split("""<div class="hnr_ttimespent"><span class="stopped">""")[1].split("<")[0]
             line[11] = line[11].split("""<div class="hnr_tratio"><span class="stopped">""")[1].split("<")[0]
             
             item = {}
             item.update({'title':line[3].split("\n")[1]})
             item.update({'id':int(line[3].split("\n")[0])})
             item.update({'start':line[5]})
             item.update({'lastupdate':line[6]})
             item.update({'status':line[7]})
             item.update({'upload':line[8]})
             item.update({'download':line[9]})
             item.update({'elapsedtime': line[10]})
             item.update({'rate': float(line[11])})
             item.update({'torrent':self.get_torrent(int(line[3].split("\n")[0]))})

             torrents.append(item)
        return torrents
    
    def get_by_activity(self):
        try:
            content = self._session.get(URLs.ACTIVITY.value, timeout=self.timeout)
        except Exception as e:
            raise NcoreConnectionError("Error while get activity. Url: '{}'. {}".format(URLs.ACTIVITY.value, e))

        torrents = []
        for id in self._activity_parser.get_ids(content.text):
            torrents.append(self.get_torrent(id))
        return torrents

    def get_recommended(self, type=None):
        try:
            content = self._session.get(URLs.RECOMMENDED.value, timeout=self.timeout)
        except Exception as e:
            raise NcoreConnectionError("Error while get recommended. Url: '{}'. {}".format(URLs.RECOMMENDED.value, e))

        all_recommended = [self.get_torrent(id) for id in self._recommended_parser.get_ids(content.text)]
        return [torrent for torrent in all_recommended if not type or torrent['type'] == type]

    def download(self, torrent, path, override=False):
        file_path, url = torrent.prepare_download(path)
        try:
            content = self._session.get(url, timeout=self.timeout)
        except Exception as e:
            raise NcoreConnectionError("Error while downloading torrent. Url: '{}'. {}".format(url, e))
        if not override and os.path.exists(file_path):
            raise NcoreDownloadError("Error while downloading file: '{}'. It is already exists.".format(file_path))
        with open(file_path, 'wb') as fh:
            fh.write(content.content)
        return file_path

    def close(self):
        self._session.close()
