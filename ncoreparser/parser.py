import re
from ncoreparser.error import NcoreParserError


class TorrentsPageParser:
    def __init__(self, data):
        self.key_pattern = re.compile(r'<link rel="alternate" href="https:\/\/ncore.cc\/rss.php\?key=(?P<key>[a-z,0-9]+)" title=".*">')
        self.data = data
        self.key = self.get_key()
    
    def get_key(self):
        find = self.key_pattern.search(self.data)
        if find:
            return find.group("key")
        else:
            raise NcoreParserError(f"Error while read user key with pattern: {self.key_pattern}")

with open("/home/aron/Asztal/letoltes.html") as fh:
    p = TorrentsPageParser("asd")
    p.get_key()
