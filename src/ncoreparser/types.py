from dataclasses import dataclass
from ncoreparser.torrent import Torrent


@dataclass
class SearchResult:
    torrents: list[Torrent]
    num_of_pages: int
