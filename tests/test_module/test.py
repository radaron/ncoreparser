import os
import pytest
from ncoreparser import Client, SearchParamType
from ncoreparser.torrent import Torrent


class TestNcoreParser:

    @pytest.fixture(scope="class")
    def client(self):
        username = os.environ["NCORE_USERNAME"]
        password = os.environ["NCORE_PASSWORD"]
        c = Client(timeout=5)  # sometimes got read timeout error.
        c.login(username, password)
        return c

    def test_search(self, client):
        result = client.search(pattern="forrest gump", type=SearchParamType.HD)

        assert isinstance(result.torrents[0], Torrent)

    def test_rss(self, client):
        rss_url = os.environ["RSS_URL"]
        torrents = client.get_by_rss(rss_url)

        torrents_list = list(torrents)
        assert len(torrents_list) == 1
        torrent = torrents_list[0]

        assert isinstance(torrent, Torrent)
        assert "FORREST" in torrent["title"].upper()

    def test_recommended(self, client):
        torrents = client.get_recommended(SearchParamType.HDSER_HUN)

        assert len(list(torrents)) > 0
        for torrent in torrents:
            assert isinstance(torrent, Torrent)
            assert torrent["type"] == SearchParamType.HDSER_HUN

    def test_download(self, client):
        result = client.search(pattern="forrest gump", type=SearchParamType.HD_HUN)

        client.download(result.torrents[0], ".", override=True)

        for root, _, files in os.walk("."):
            for file in files:
                if file.endswith(".torrent"):
                    path = os.path.join(root, file)
                    file_content = open(path, "rb").read()
                    assert len(file_content) > 0
