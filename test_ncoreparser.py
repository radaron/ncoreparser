from ncoreparser import Client
import pytest
import json

username = ""
password = ""

@pytest.fixture(scope="session", autouse=True)
def collect_cred():
    global username, password
    credentials = "cred.json"
    with open(credentials) as fh:
        cred = json.load(fh)
    username = cred["username"]
    password = cred["password"]
    yield



def test_credentials():
    a = Client()
    if not a.open(username, password):
        assert 0, f"The login credentials are not correct: {username}, {password}."
"""
d = a.most_seed_movies(1)
for n, l in zip(d.keys(), d.values()):
    print(f"{n:.<80}{l}")
print("Hnr ids:", a.get_hnr_torrent_ids())
a.close()
"""
