import requests
from ncoreparser.data import URLs
from ncoreparser.errors import NcoreConnectionError, NcoreCredentialError

class Client:
    def __init__(self, username, password):
        self.session = requests.session()
        self.session.cookies.clear()
        try:
            r = self.session.post(URLs.LOGIN.value, {"nev": username, "pass": password})
        except:
            raise NcoreConnectionError(f"Error while perform post method to url '{URLs.LOGIN.value}'.")
        if r.url != URLs.INDEX.value:
            self.session.close()
            raise NcoreCredentialError(f"Error while login, check credentials for user: '{username}'")
        
        #TODO self.torrents_url_pattern = self.url+"torrents.php?oldal={page}&tipus={t_type}&miszerint={sort}&hogyan={seq}"
        #TODO self.torrent_detail_pattern = self.url+"torrents.php?action=details&id={id}"
        #TODO param =  {"mire": "Pirates", "miben": "name", "tipus": "xvid_hun", "submit.x": "17", "submit.y": "16", "tags": ""} 
    
    def close(self):
        self.session.close()
