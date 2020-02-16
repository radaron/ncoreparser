import os


class Torrent:
    def __init__(self, details, session):
        self._details = details
        self._session = session

    def __getattribute__(self, name):
        return self._details[name]

    def __str__(self):
        return f"<Torrent {self._details['name']}>"

    def download(self, path):
        os.path.join(path, self._details['name']+'.torrent')
        content = self._session.get(self._details['download_link'])
        with open(path, 'wb') as fh:
            fh.write(content.content)
