import os
import requests


class Torrent:
    def __init__(self, details):
        self._details = details

    def __getattribute__(self, name):
        return self._details[name]

    def __str__(self):
        return f"<Torrent {self._details['id']}>"

    def download(self, path):
        filename = self._details['title'].replace(' ', '_') + '.torrent'
        filepath = os.path.join(path, filename)
        content = requests.get(self._details['download'])
        with open(filepath, 'wb') as fh:
            fh.write(content.content)
