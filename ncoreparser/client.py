import requests
from ncoreparser.data import URLs
from ncoreparser.error import NcoreConnectionError, NcoreCredentialError
from ncoreparser.torrent import Torrent


class Client:
    def __init__(self, username, password):
        self._session = requests.session()
        self._session.cookies.clear()
        try:
            r = self._session.post(URLs.LOGIN.value,
                                   {"nev": username, "pass": password})
        except Exception:
            raise NcoreConnectionError(f"Error while perform post "
                                       f"method to url '{URLs.LOGIN.value}'.")
        if r.url != URLs.INDEX.value:
            self._session.close()
            raise NcoreCredentialError(f"Error while login, check "
                                       f"credentials for user: '{username}'")

    def query(self, pattern, type, sort_by, sort_order, number):
        item_count = 0
        # TODO Slice number to max 25 length groups
        """
        def group(lst, n):
            for i in range(0, len(lst), n):
            val = lst[i:i+n]
        """
        while item_count < number:
            url = URLs.DOWNLOAD_PATTERN.value.format(page="",
                                                     t_type=type,
                                                     sort=sort_by,
                                                     seq=sort_order,
                                                     pattern=pattern,
                                                     miben="name")
            r = self._session.get(url)

    def close(self):
        self._session.close()
