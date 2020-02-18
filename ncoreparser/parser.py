import re
from html.parser import HTMLParser
from ncoreparser.data import ParamType, URLs


class TorrentsPageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data = []
        self.dict = {}
        self.new_element = ""
        self.is_data = False
        self.key = ""
        self.id_patern = re.compile(r"(.*)\((?P<id>.*)\)(.*)")
        self.type_pattern = re.compile(r"(.*)\?tipus=(?P<type>.*)")
        self.key_pattern = re.compile(r"(.*)\?key=(?P<key>.*)")

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if tag == 'link' and name == 'href' and self.key_pattern.search(value):
                self.key = self.key_pattern.search(value).group('key')
            if name == 'class' and value == 'torrent_txt' or value == 'torrent_txt2':
                self.new_element = "id"
                break
            if self.new_element and tag == 'a' and name == 'onclick':
                self.dict[self.new_element] = self.id_patern.search(value).group('id')
                self.new_element = "title"
            if self.new_element and tag == 'a' and name == 'title':
                self.dict[self.new_element] = value
                self.new_element = ""
                break
            if tag == 'div' and value == 'box_feltoltve2':
                self.new_element = "uploaded"
                self.is_data = True
                break
            if tag == 'div' and value == 'box_meret2':
                self.new_element = "size"
                self.is_data = True
                break
            if tag == 'div' and value == 'box_alap_img':
                self.new_element = "type"
                break
            if self.new_element and tag == 'a' and self.type_pattern.search(value):
                print(self.type_pattern.search(value).group(0))
                self.dict[self.new_element] = ParamType(self.type_pattern.search(value).group("type"))
                self.new_element = ""
                break
            # close the dict
            if tag == 'div' and value == 'box_feltolto2':
                self.dict['download'] = URLs.DOWNLOAD_LINK.value.format(id=self.dict['id'], key=self.key)
                self.data.append(dict(self.dict))
                self.dict = {}
                break

    def handle_data(self, data):
        if self.is_data and self.new_element:
            self.dict[self.new_element] = data
            self.is_data = False
            self.new_element = ""
